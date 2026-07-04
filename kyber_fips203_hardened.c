/*
  kyber_fips203_hardened.c   CRYSTALS-Kyber / ML-KEM (FIPS 203).

  Derived from kyber_fips203_update.c (the educational reference). This variant
  adds two hardening items from future_update.md, leaving the rest of that file's
  educational core (plain `% q`, no zeroization, no CSPRNG) unchanged:

    #1  Constant-time implicit-rejection select in Decaps. The K'/Kbar choice no
        longer branches on whether the ciphertext was valid, closing the
        decryption-failure side channel that the FO transform exists to remove.
    #2  FIPS 203 input validation:
          - Encaps: encapsulation-key length check + the "modulus check" (every
            12-bit coefficient of t-hat must be < q; non-canonical ek is rejected
            instead of silently reduced).
          - Decaps: ciphertext-length and decapsulation-key-length type checks.

  Because of #2 the public Encaps/Decaps entry points now take input lengths and
  return an int status (0 = success, negative = rejected; see MLKEM_ERR_* below).

  This build also adds the remaining future_update.md items:
    #3  Secret zeroization (secure_zero, a volatile wipe the optimizer cannot
        elide) on seeds, noise polynomials, and the (K,r) buffers.
    #4  CSPRNG path: randombytes() over getrandom(2) with a /dev/urandom
        fallback, plus mlkem_keygen_rand / mlkem_encaps_rand wrappers that pull
        their own randomness instead of taking caller seeds.
    #5  Static asserts pinning the PRF / SampleNTT buffer-size invariants, and a
        simpler CBD reduction.
    #6  A deterministic regression KAT (self-generated, locks behavior across
        edits). NOTE: this is NOT the official NIST ACVP vector set; running
        those still requires the NIST response files, fed through the same
        deterministic mlkem_keygen / mlkem_encaps entry points.

  Remaining caveat: the modular reduction is still plain `% q`, so the
  arithmetic is not guaranteed constant-time on every target; production needs
  Barrett/Montgomery. Item #1 removes the Decaps *branch* oracle specifically.

  Read this file top to bottom: it is layered, and each layer only uses the one
  below it.

    1. Primitives   Keccak sponge -> SHAKE128/256, SHA3-256/512; the NTT and
                    its inverse; centered-binomial noise; compress/encode.
    2. K-PKE        The IND-CPA public-key encryption (KeyGen/Encrypt/Decrypt).
                    This is the lattice maths, but it is only CPA-secure.
    3. ML-KEM       The IND-CCA2 KEM. It wraps K-PKE with the Fujisaki-Okamoto
                    transform so a tampered ciphertext cannot leak the secret.

  The big idea: a polynomial is multiplied fast by moving it to the "NTT domain"
  (a frequency-like representation) where multiplication becomes cheap
  pointwise products, then moving back with the inverse NTT.

  Build:  gcc -O2 -Wall -o kyber_fips203_hardened kyber_fips203_hardened.c
  Run:    ./kyber_fips203_hardened   (self-tests incl. input-validation, then demo)
*/

#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>        /* #4: errno (EINTR) for the getrandom retry loop   */
#include <unistd.h>       /* #4: ssize_t                                      */
#include <sys/random.h>   /* #4: getrandom(2)                                 */

/* Parameters. Switch KYBER_K to pick the security level; everything else is
   derived from it exactly as in the FIPS 203 parameter table. */

#define KYBER_N 256        /* polynomials have 256 coefficients            */
#define KYBER_Q 3329       /* the prime modulus for every coefficient      */
#define KYBER_K 2          /* module rank: 2=ML-KEM-512, 3=768, 4=1024     */

#if   KYBER_K == 2
  #define KYBER_ETA1 3     /* ML-KEM-512 widens the keygen noise to eta=3  */
  #define KYBER_DU   10    /* bits kept per coeff when compressing u       */
  #define KYBER_DV   4     /* bits kept per coeff when compressing v       */
  #define KYBER_NAME 512
#elif KYBER_K == 3
  #define KYBER_ETA1 2
  #define KYBER_DU   10
  #define KYBER_DV   4
  #define KYBER_NAME 768
#else
  #define KYBER_ETA1 2
  #define KYBER_DU   11
  #define KYBER_DV   5
  #define KYBER_NAME 1024
#endif
#define KYBER_ETA2 2       /* encryption noise width is 2 for every set    */

#define N_INV       3303   /* 128^{-1} mod 3329; final scaling in the INTT */
#define SEED_BYTES  32
#define POLY_BYTES  384    /* a 256-coeff polynomial at 12 bits each = 384 B */

/* Serialized object sizes (these are what gets sent on the wire). */
#define PKE_PK_BYTES  (KYBER_K*POLY_BYTES + SEED_BYTES)   /* t || rho        */
#define PKE_SK_BYTES  (KYBER_K*POLY_BYTES)                /* s               */
#define CT_C1_BYTES   (KYBER_K*32*KYBER_DU)               /* compressed u    */
#define CT_C2_BYTES   (32*KYBER_DV)                       /* compressed v    */
#define CT_BYTES      (CT_C1_BYTES + CT_C2_BYTES)
#define DK_BYTES      (2*KYBER_K*POLY_BYTES + 2*SEED_BYTES + SEED_BYTES) /* dkPKE+ek+H(ek)+z */
#define SS_BYTES      32                                  /* shared secret   */

typedef int16_t poly[KYBER_N];   /* one ring element = 256 coefficients */

/* Status codes for the public Encaps/Decaps (see hardening item #2). */
#define MLKEM_OK            0
#define MLKEM_ERR_EK_LEN  (-1)   /* encapsulation key has the wrong length      */
#define MLKEM_ERR_EK_RANGE (-2)  /* ek failed the modulus check (coeff >= q)    */
#define MLKEM_ERR_DK_LEN  (-3)   /* decapsulation key has the wrong length      */
#define MLKEM_ERR_CT_LEN  (-4)   /* ciphertext has the wrong length             */
#define MLKEM_ERR_RNG     (-5)   /* the CSPRNG failed (see #4 wrappers)         */

/* Constant-time helpers (hardening item #1). These avoid secret-dependent
   branches; they do NOT make the surrounding `% q` arithmetic constant-time. */

/* Return 0xFF if x == 0, else 0x00, with no branch. x is treated as 32-bit. */
static inline uint8_t ct_eq0_mask(uint32_t x){
    uint32_t nz = (x | (0u - x)) >> 31;   /* 1 if x != 0, 0 if x == 0 */
    return (uint8_t)(nz - 1u);            /* 0xFF if equal, 0x00 otherwise */
}

/* out[i] = (a[i] if mask==0xFF) else b[i], byte-wise, branch-free. */
static inline void ct_select(uint8_t *out,const uint8_t *a,const uint8_t *b,
                             size_t n,uint8_t mask){
    for(size_t i=0;i<n;i++) out[i]=(uint8_t)((a[i]&mask)|(b[i]&(uint8_t)~mask));
}

/* Hardening #3: wipe a secret buffer so it does not linger on the stack. The
   volatile pointer stops the optimizer from eliding the stores -- a plain
   memset() on a soon-dead buffer is legally removed at -O2. */
static void secure_zero(void *p,size_t n){
    volatile uint8_t *v=(volatile uint8_t*)p;
    while(n--) *v++=0;
}

/* Hardening #4: fill `out` with cryptographically secure random bytes from the
   kernel CSPRNG via getrandom(2), falling back to /dev/urandom. Returns 0 on
   success, -1 on failure. This is the only randomness source for real keys;
   the xorshift `rng` further down is for self-tests only and must never be
   used for key material. */
static int randombytes(uint8_t *out,size_t n){
    size_t got=0;
    while(got<n){
        ssize_t r=getrandom(out+got,n-got,0);
        if(r<0){ if(errno==EINTR) continue; break; }
        got+=(size_t)r;
    }
    if(got==n) return 0;
    FILE *f=fopen("/dev/urandom","rb");          /* fallback if getrandom unavailable */
    if(!f) return -1;
    size_t rd=fread(out+got,1,n-got,f); fclose(f);
    return (got+rd==n)?0:-1;
}

/* Keccak-f[1600] sponge. This single permutation underlies all of Kyber's
   hashing: SHAKE128 (expand the matrix A), SHAKE256 (sample noise, and J),
   SHA3-256 (H), SHA3-512 (G). They differ only in rate and the domain byte. */

#define KECCAK_ROUNDS 24
static const uint64_t RC[24] = {       /* round constants for the iota step */
    0x0000000000000001ULL,0x0000000000008082ULL,0x800000000000808AULL,
    0x8000000080008000ULL,0x000000000000808BULL,0x0000000080000001ULL,
    0x8000000080008081ULL,0x8000000000008009ULL,0x000000000000008AULL,
    0x0000000000000088ULL,0x0000000080008009ULL,0x000000008000000AULL,
    0x000000008000808BULL,0x800000000000008BULL,0x8000000000008089ULL,
    0x8000000000008003ULL,0x8000000000008002ULL,0x8000000000000080ULL,
    0x000000000000800AULL,0x800000008000000AULL,0x8000000080008081ULL,
    0x8000000000008080ULL,0x0000000080000001ULL,0x8000000080008008ULL,
};
static const int RHO[24]={1,3,6,10,15,21,28,36,45,55,2,14,27,41,56,8,25,43,62,18,39,61,20,44}; /* rotation offsets */
static const int PI[24] ={10,7,11,17,18,3,5,16,8,21,24,4,15,23,19,13,12,2,20,14,22,9,6,1};      /* lane permutation */

static inline uint64_t rol64(uint64_t x,int s){return (x<<s)|(x>>(64-s));}

/* The permutation: 24 rounds of theta (mix columns), rho+pi (rotate and move
   lanes along the Keccak walk), chi (non-linear mix), iota (add a constant).
   The rho/pi step threads the source lane through a chain (t = A[1], then the
   previous destination) -- doing it any other way silently breaks SHA-3. */
static void keccakf(uint64_t A[25]){
    uint64_t bc[5], t;
    for(int r=0;r<KECCAK_ROUNDS;r++){
        for(int i=0;i<5;i++) bc[i]=A[i]^A[i+5]^A[i+10]^A[i+15]^A[i+20];      /* theta */
        for(int i=0;i<5;i++){ t=bc[(i+4)%5]^rol64(bc[(i+1)%5],1);
            for(int j=0;j<25;j+=5) A[j+i]^=t; }
        t=A[1];                                                             /* rho & pi */
        for(int i=0;i<24;i++){ int j=PI[i]; uint64_t tt=A[j]; A[j]=rol64(t,RHO[i]); t=tt; }
        for(int j=0;j<25;j+=5){                                             /* chi */
            for(int i=0;i<5;i++) bc[i]=A[j+i];
            for(int i=0;i<5;i++) A[j+i]^=(~bc[(i+1)%5])&bc[(i+2)%5]; }
        A[0]^=RC[r];                                                        /* iota */
    }
}

/* Incremental sponge state: absorb input, then squeeze output, `rate` bytes at
   a time. rate is what distinguishes the functions (SHAKE128=168, SHAKE256 and
   SHA3-256=136, SHA3-512=72). */
typedef struct{ uint64_t A[25]; uint8_t buf[200]; int rate,pos; } Keccak;

static void xof_init(Keccak*c,int rate){ memset(c,0,sizeof(*c)); c->rate=rate; }
static void absorb_block(Keccak*c){      /* XOR one full rate block into the state */
    for(int j=0;j<c->rate/8;j++){ uint64_t l=0;
        for(int b=0;b<8;b++){ l|=(uint64_t)c->buf[j*8+b]<<(b*8); } c->A[j]^=l; }
    int rem=c->rate%8; if(rem){ uint64_t l=0; int base=(c->rate/8)*8;
        for(int b=0;b<rem;b++){ l|=(uint64_t)c->buf[base+b]<<(b*8); } c->A[c->rate/8]^=l; }
}
static void extract_block(Keccak*c){     /* read one rate block of output back out */
    for(int j=0;j<c->rate/8;j++){ uint64_t l=c->A[j];
        for(int b=0;b<8;b++) c->buf[j*8+b]=(l>>(b*8))&0xFF; }
    int rem=c->rate%8; if(rem){ uint64_t l=c->A[c->rate/8]; int base=(c->rate/8)*8;
        for(int b=0;b<rem;b++) c->buf[base+b]=(l>>(b*8))&0xFF; }
}
static void xof_absorb(Keccak*c,const uint8_t*in,size_t len){  /* feed input, permuting each full block */
    for(size_t i=0;i<len;i++){ c->buf[c->pos++]^=in[i];
        if(c->pos==c->rate){ absorb_block(c); keccakf(c->A); memset(c->buf,0,c->rate); c->pos=0; } }
}
/* Pad and switch from absorbing to squeezing. domain = 0x1F for SHAKE,
   0x06 for SHA3 -- this single byte is the only difference between them. */
static void xof_finalize(Keccak*c,uint8_t domain){
    c->buf[c->pos]^=domain; c->buf[c->rate-1]^=0x80;
    absorb_block(c); keccakf(c->A); extract_block(c); c->pos=0;
}
static void xof_squeeze(Keccak*c,uint8_t*out,size_t len){     /* pull output, re-permuting when a block runs out */
    for(size_t i=0;i<len;i++){
        if(c->pos==c->rate){ keccakf(c->A); extract_block(c); c->pos=0; }
        out[i]=c->buf[c->pos++];
    }
}

/* The five named hash roles, each just a (rate, domain, length) choice. */
static void shake256(const uint8_t*in,size_t inl,uint8_t*out,size_t outl){ /* PRF (noise) and J (reject key) */
    Keccak c; xof_init(&c,136); xof_absorb(&c,in,inl); xof_finalize(&c,0x1F); xof_squeeze(&c,out,outl);
}
static void shake128(const uint8_t*in,size_t inl,uint8_t*out,size_t outl){ /* XOF, used to expand matrix A */
    Keccak c; xof_init(&c,168); xof_absorb(&c,in,inl); xof_finalize(&c,0x1F); xof_squeeze(&c,out,outl);
}
static void sha3_256(const uint8_t*in,size_t inl,uint8_t out[32]){         /* H: binds ek into the transform */
    Keccak c; xof_init(&c,136); xof_absorb(&c,in,inl); xof_finalize(&c,0x06); xof_squeeze(&c,out,32);
}
static void sha3_512(const uint8_t*in,size_t inl,uint8_t out[64]){         /* G: derives (rho,sigma) and (K,r) */
    Keccak c; xof_init(&c,72); xof_absorb(&c,in,inl); xof_finalize(&c,0x06); xof_squeeze(&c,out,64);
}

/* NTT and pointwise multiplication.
   zetas[k] = zeta^BitRev7(k) mod q with zeta=17, in the plain (non-Montgomery)
   domain, matching the plain `% q` arithmetic used below. */
static const int16_t zetas[128]={
      1,1729,2580,3289,2642, 630,1897, 848,1062,1919, 193, 797,2786,3260, 569,1746,
    296,2447,1339,1476,3046,  56,2240,1333,1426,2094, 535,2882,2393,2879,1974, 821,
    289, 331,3253,1756,1197,2304,2277,2055, 650,1977,2513, 632,2865,  33,1320,1915,
   2319,1435, 807, 452,1438,2868,1534,2402,2647,2617,1481, 648,2474,3110,1227, 910,
     17,2761, 583,2649,1637, 723,2288,1100,1409,2662,3281, 233, 756,2156,3015,3050,
   1703,1651,2789,1789,1847, 952,1461,2687, 939,2308,2437,2388, 733,2337, 268, 641,
   1584,2298,2037,3220, 375,2549,2090,1645,1063, 319,2773, 757,2099, 561,2466,2594,
   2804,1092, 403,1026,1143,2150,2775, 886,1722,1212,1874,1029,2110,2935, 885,2154,
};

/* Forward NTT: 7 layers of Cooley-Tukey butterflies. It does NOT reach single
   points -- 3329 has no primitive 512th root, so X^256+1 only factors into 128
   quadratics. The transform therefore stops at 128 degree-1 pairs. */
static void poly_ntt(poly f){
    int k=1;
    for(int len=128;len>=2;len>>=1)
        for(int start=0;start<KYBER_N;start+=2*len){
            int z=zetas[k++];
            for(int j=start;j<start+len;j++){
                int t=(int)z*f[j+len]%KYBER_Q;
                f[j+len]=(int16_t)((f[j]-t+KYBER_Q)%KYBER_Q);
                f[j]=(int16_t)((f[j]+t)%KYBER_Q);
            }
        }
}

/* Inverse NTT: the same butterflies run backwards (Gentleman-Sande), then every
   coefficient is scaled by 128^{-1} to undo the transform. */
static void poly_intt(poly f){
    int k=127;
    for(int len=2;len<=128;len<<=1)
        for(int start=0;start<KYBER_N;start+=2*len){
            int z=zetas[k--];
            for(int j=start;j<start+len;j++){
                int t=f[j];
                f[j]=(int16_t)((t+f[j+len])%KYBER_Q);
                f[j+len]=(int16_t)((int)z*((f[j+len]-t+KYBER_Q)%KYBER_Q)%KYBER_Q);
            }
        }
    for(int i=0;i<KYBER_N;i++) f[i]=(int16_t)((int)f[i]*N_INV%KYBER_Q);
}

/* Multiply in the NTT domain. Because the transform stops at quadratics, this
   is 128 little degree-1 products (a0+a1X)(b0+b1X) mod (X^2 - gamma), not plain
   pointwise products. gamma alternates +zetas[64+g] / -zetas[64+g].
   The casts to `long` matter: gamma*a*b can reach q^3 ~ 3.7e10 and would
   overflow a 32-bit int. */
static void poly_basemul(poly r,const poly a,const poly b){
    for(int g=0;g<64;g++){
        long gp=zetas[64+g], gn=KYBER_Q-gp; int i=4*g;
        r[i]  =(int16_t)(((long)a[i]*b[i]+gp*a[i+1]%KYBER_Q*b[i+1])%KYBER_Q);
        r[i+1]=(int16_t)(((long)a[i]*b[i+1]+(long)a[i+1]*b[i])%KYBER_Q);
        i=4*g+2;
        r[i]  =(int16_t)(((long)a[i]*b[i]+gn*a[i+1]%KYBER_Q*b[i+1])%KYBER_Q);
        r[i+1]=(int16_t)(((long)a[i]*b[i+1]+(long)a[i+1]*b[i])%KYBER_Q);
    }
}
static void poly_add(poly r,const poly a,const poly b){ /* coefficient-wise add mod q */
    for(int i=0;i<KYBER_N;i++) r[i]=(int16_t)((a[i]+b[i])%KYBER_Q);
}
static void poly_sub(poly r,const poly a,const poly b){ /* coefficient-wise subtract mod q */
    for(int i=0;i<KYBER_N;i++) r[i]=(int16_t)((a[i]-b[i]+KYBER_Q)%KYBER_Q);
}

/* Generate one entry of the public matrix A on demand (it is never stored
   whole). A[R][C] = SampleNTT(SHAKE128(rho || C || R)): stream bytes from the
   XOF and rejection-sample 12-bit values that land in [0, q). The result is
   already in the NTT domain. */
static void gen_a_entry(poly out,const uint8_t rho[SEED_BYTES],int R,int C){
    uint8_t seed[SEED_BYTES+2];
    memcpy(seed,rho,SEED_BYTES); seed[SEED_BYTES]=(uint8_t)C; seed[SEED_BYTES+1]=(uint8_t)R;
    Keccak c; xof_init(&c,168); xof_absorb(&c,seed,SEED_BYTES+2); xof_finalize(&c,0x1F);
    int count=0,bp=0,bl=0; uint8_t buf[168*4];
    /* #5: the 3-byte reader must never straddle a refill, so the buffer length
       has to be a multiple of 3; otherwise bytes would be dropped and the
       sampled matrix A would desync from the reference. */
    _Static_assert(sizeof(buf)%3==0,"SampleNTT buffer must be a multiple of 3");
    while(count<KYBER_N){
        if(bp+3>bl){ xof_squeeze(&c,buf,sizeof(buf)); bl=sizeof(buf); bp=0; }
        uint8_t b0=buf[bp],b1=buf[bp+1],b2=buf[bp+2]; bp+=3;   /* 3 bytes -> two 12-bit candidates */
        int d1=b0|((b1&0x0F)<<8), d2=(b1>>4)|((int)b2<<4);
        if(d1<KYBER_Q&&count<KYBER_N) out[count++]=(int16_t)d1; /* reject anything >= q */
        if(d2<KYBER_Q&&count<KYBER_N) out[count++]=(int16_t)d2;
    }
}

/* Centered Binomial Distribution: the noise source. For each coefficient, take
   2*eta random bits, subtract the popcount of the second half from the first,
   giving a small value in [-eta, +eta] centered on 0. */
static inline int getbit(const uint8_t*b,int t){ return (b[t>>3]>>(t&7))&1; }
static void cbd(poly f,const uint8_t*buf,int eta){
    for(int i=0;i<KYBER_N;i++){
        int base=2*eta*i,a=0,b=0;
        for(int j=0;j<eta;j++) a+=getbit(buf,base+j);
        for(int j=0;j<eta;j++) b+=getbit(buf,base+eta+j);
        /* #5: v is in [-eta, eta] (eta <= 3), so a single conditional add is
           enough to store the positive representative -- no `% q` needed. */
        int v=a-b; f[i]=(int16_t)(v<0 ? v+KYBER_Q : v);
    }
}
/* Sample one noise polynomial: PRF = SHAKE256(seed || nonce) gives 64*eta fresh
   bytes, which CBD turns into coefficients. The nonce keeps each polynomial
   independent. */
static void sample_poly(poly f,const uint8_t seed[SEED_BYTES],uint8_t nonce,int eta){
    uint8_t in[SEED_BYTES+1]; memcpy(in,seed,SEED_BYTES); in[SEED_BYTES]=nonce;
    uint8_t buf[64*3];
    /* #5: PRF emits 64*eta bytes; the buffer must hold the widest case (eta1). */
    _Static_assert(64*KYBER_ETA1<=sizeof(buf),"PRF buffer too small for eta1");
    _Static_assert(64*KYBER_ETA2<=sizeof(buf),"PRF buffer too small for eta2");
    shake256(in,SEED_BYTES+1,buf,(size_t)64*eta); cbd(f,buf,eta);
    secure_zero(in,sizeof in); secure_zero(buf,sizeof buf);  /* #3: seed+PRF stream are secret */
}

/* Compression throws away low bits to shrink ciphertexts; it is lossy but the
   error stays small enough to decrypt. Decompress is the inverse rounding.
   ByteEncode/Decode just pack/unpack d-bit values into a byte string. */
static inline int compress_c(int x,int d){ return (int)(((((long)x)<<d)+KYBER_Q/2)/KYBER_Q)&((1<<d)-1); }
static inline int decompress_c(int y,int d){ return (int)(((long)KYBER_Q*y+(1<<(d-1)))>>d); }

static void byte_encode(uint8_t*out,const poly f,int d){   /* pack 256 d-bit coeffs, LSB first */
    memset(out,0,(size_t)32*d);
    for(int i=0;i<KYBER_N;i++){ int v=f[i]&((1<<d)-1);
        for(int b=0;b<d;b++) if((v>>b)&1) out[(i*d+b)>>3]|=1<<((i*d+b)&7); }
}
static void byte_decode(poly f,const uint8_t*in,int d){     /* unpack; d=12 also reduces mod q */
    for(int i=0;i<KYBER_N;i++){ int v=0;
        for(int b=0;b<d;b++) v|=getbit(in,i*d+b)<<b;
        if(d==12){ v%=KYBER_Q; } f[i]=(int16_t)v; }
}
/* Hardening #2: the FIPS 203 "modulus check". Unpack 256 12-bit coefficients
   and REJECT (return -1) if any is >= q, instead of silently reducing it. This
   is how Encaps validates an externally supplied encapsulation key so that a
   non-canonical ek cannot be accepted. */
static int byte_decode12_validate(poly f,const uint8_t*in){
    for(int i=0;i<KYBER_N;i++){ int v=0;
        for(int b=0;b<12;b++) v|=getbit(in,i*12+b)<<b;
        if(v>=KYBER_Q) return -1;
        f[i]=(int16_t)v; }
    return 0;
}
static void poly_compress(uint8_t*out,const poly f,int d){  /* compress then pack */
    poly t; for(int i=0;i<KYBER_N;i++) t[i]=(int16_t)compress_c(f[i],d); byte_encode(out,t,d);
}
static void poly_decompress(poly f,const uint8_t*in,int d){ /* unpack then decompress */
    byte_decode(f,in,d); for(int i=0;i<KYBER_N;i++) f[i]=(int16_t)decompress_c(f[i],d);
}

/* K-PKE: the IND-CPA encryption underneath the KEM. */

/* KeyGen: derive seeds from d, sample secret s and error e, publish t = A*s + e.
   Everything is done in the NTT domain so the matrix product is cheap. The hard
   problem (MLWE) is that e hides s: t looks random. */
static void kpke_keygen(const uint8_t d[SEED_BYTES],uint8_t ek[PKE_PK_BYTES],uint8_t dk[PKE_SK_BYTES]){
    uint8_t de[SEED_BYTES+1]; memcpy(de,d,SEED_BYTES); de[SEED_BYTES]=(uint8_t)KYBER_K;
    uint8_t rs[64]; sha3_512(de,SEED_BYTES+1,rs);    /* G(d||k) -> rho (public) and sigma (secret) */
    uint8_t *rho=rs,*sigma=rs+32;
    poly s[KYBER_K],e[KYBER_K],t[KYBER_K];
    for(int i=0;i<KYBER_K;i++){                       /* sample noise, move to NTT domain */
        sample_poly(s[i],sigma,(uint8_t)i,KYBER_ETA1);
        sample_poly(e[i],sigma,(uint8_t)(KYBER_K+i),KYBER_ETA1);
        poly_ntt(s[i]); poly_ntt(e[i]);
    }
    for(int i=0;i<KYBER_K;i++){                       /* t_i = sum_j A[i][j]*s[j] + e_i */
        poly acc; memset(acc,0,sizeof(acc)); poly a,tmp;
        for(int j=0;j<KYBER_K;j++){ gen_a_entry(a,rho,i,j); poly_basemul(tmp,a,s[j]); poly_add(acc,acc,tmp); }
        poly_add(t[i],acc,e[i]);
    }
    for(int i=0;i<KYBER_K;i++){ byte_encode(ek+i*POLY_BYTES,t[i],12); byte_encode(dk+i*POLY_BYTES,s[i],12); }
    memcpy(ek+KYBER_K*POLY_BYTES,rho,SEED_BYTES);     /* public key = t || rho */
    /* #3: d, sigma, s and e are secret; wipe them (t and rho are public). */
    secure_zero(de,sizeof de); secure_zero(rs,sizeof rs);
    secure_zero(s,sizeof s);   secure_zero(e,sizeof e);
}

/* Encrypt one 32-byte message m using fresh coins. Mirrors KeyGen but with the
   transpose A^T: u carries the randomness, v carries the message scaled by
   q/2 (so a 0/1 bit becomes a far-apart 0 or ~1665). */
static void kpke_encrypt(const uint8_t ek[PKE_PK_BYTES],const uint8_t m[32],
                         const uint8_t coins[SEED_BYTES],uint8_t c[CT_BYTES]){
    const uint8_t*rho=ek+KYBER_K*POLY_BYTES;
    poly t[KYBER_K]; for(int i=0;i<KYBER_K;i++) byte_decode(t[i],ek+i*POLY_BYTES,12);
    poly r[KYBER_K],e1[KYBER_K],e2,rhat[KYBER_K]; uint8_t N=0;
    for(int i=0;i<KYBER_K;i++) sample_poly(r[i],coins,N++,KYBER_ETA1);   /* r ~ eta1 */
    for(int i=0;i<KYBER_K;i++) sample_poly(e1[i],coins,N++,KYBER_ETA2);  /* e1 ~ eta2 */
    sample_poly(e2,coins,N++,KYBER_ETA2);                                /* e2 ~ eta2 */
    for(int i=0;i<KYBER_K;i++){ memcpy(rhat[i],r[i],sizeof(poly)); poly_ntt(rhat[i]); }
    poly u[KYBER_K];                                  /* u = INTT(A^T . r) + e1 */
    for(int i=0;i<KYBER_K;i++){
        poly acc; memset(acc,0,sizeof(acc)); poly a,tmp;
        for(int j=0;j<KYBER_K;j++){ gen_a_entry(a,rho,j,i); poly_basemul(tmp,a,rhat[j]); poly_add(acc,acc,tmp); }
        poly_intt(acc); poly_add(u[i],acc,e1[i]);
    }
    poly v,acc; memset(acc,0,sizeof(acc)); poly tmp;   /* v = INTT(t^T . r) + e2 + msg */
    for(int j=0;j<KYBER_K;j++){ poly_basemul(tmp,t[j],rhat[j]); poly_add(acc,acc,tmp); }
    poly_intt(acc); poly mu; poly_decompress(mu,m,1);  /* msg bit -> 0 or q/2 */
    poly_add(v,acc,e2); poly_add(v,v,mu);
    for(int i=0;i<KYBER_K;i++) poly_compress(c+i*32*KYBER_DU,u[i],KYBER_DU); /* shrink u (du bits) */
    poly_compress(c+CT_C1_BYTES,v,KYBER_DV);                                 /* shrink v (dv bits) */
    /* #3: r, e1, e2, rhat and the decompressed message mu are secret. */
    secure_zero(r,sizeof r);   secure_zero(e1,sizeof e1); secure_zero(e2,sizeof e2);
    secure_zero(rhat,sizeof rhat); secure_zero(mu,sizeof mu);
}

/* Decrypt: w = v - s^T u. The noise terms nearly cancel, leaving v's message
   plus a small error; rounding each coefficient back to 0 or q/2 recovers the
   bit, as long as the total noise stayed below q/4. */
static void kpke_decrypt(const uint8_t dk[PKE_SK_BYTES],const uint8_t c[CT_BYTES],uint8_t m[32]){
    poly u[KYBER_K],v;
    for(int i=0;i<KYBER_K;i++) poly_decompress(u[i],c+i*32*KYBER_DU,KYBER_DU);
    poly_decompress(v,c+CT_C1_BYTES,KYBER_DV);
    poly s[KYBER_K]; for(int i=0;i<KYBER_K;i++) byte_decode(s[i],dk+i*POLY_BYTES,12);
    poly acc; memset(acc,0,sizeof(acc)); poly tmp;
    for(int j=0;j<KYBER_K;j++){ poly_ntt(u[j]); poly_basemul(tmp,s[j],u[j]); poly_add(acc,acc,tmp); }
    poly_intt(acc); poly w; poly_sub(w,v,acc);
    poly_compress(m,w,1);                              /* round w back to message bits */
    /* #3: the secret key s and the intermediate w (message + noise) are secret. */
    secure_zero(s,sizeof s); secure_zero(w,sizeof w);
}

/* ML-KEM: the FO transform turns CPA encryption into a CCA-secure KEM. */

/* KeyGen: run K-PKE.KeyGen, then bundle the decapsulation key as
   dk = dkPKE || ek || H(ek) || z. H(ek) lets Decaps re-derive things; z is the
   secret used to make rejection deterministic-but-unpredictable. */
static void mlkem_keygen(const uint8_t d[SEED_BYTES],const uint8_t z[SEED_BYTES],uint8_t ek[PKE_PK_BYTES],uint8_t dk[DK_BYTES]){
    uint8_t dkpke[PKE_SK_BYTES];
    kpke_keygen(d,ek,dkpke);
    memcpy(dk,dkpke,PKE_SK_BYTES);
    memcpy(dk+PKE_SK_BYTES,ek,PKE_PK_BYTES);
    sha3_256(ek,PKE_PK_BYTES,dk+PKE_SK_BYTES+PKE_PK_BYTES);  /* H(ek) */
    memcpy(dk+PKE_SK_BYTES+PKE_PK_BYTES+32,z,SEED_BYTES);    /* z */
    secure_zero(dkpke,sizeof dkpke);                         /* #3: secret key copied into dk */
}

/* Encaps: pick a random m, derive the shared secret K and the encryption coins
   r together from G(m || H(ek)) -- so the ciphertext is a deterministic
   function of m. Send c, keep K. */
static int mlkem_encaps(const uint8_t *ek,size_t ek_len,const uint8_t m[32],uint8_t K[SS_BYTES],uint8_t c[CT_BYTES]){
    /* #2 input validation: encapsulation-key length (type) check ... */
    if(ek_len!=PKE_PK_BYTES) return MLKEM_ERR_EK_LEN;
    /* ... and the modulus check: every 12-bit coefficient of t-hat must be < q.
       A non-canonical ek is rejected here rather than silently reduced. */
    { poly tcheck;
      for(int i=0;i<KYBER_K;i++)
          if(byte_decode12_validate(tcheck,ek+i*POLY_BYTES)) return MLKEM_ERR_EK_RANGE; }
    uint8_t g_in[64]; memcpy(g_in,m,32); sha3_256(ek,PKE_PK_BYTES,g_in+32);
    uint8_t Kr[64]; sha3_512(g_in,64,Kr);            /* (K,r) = G(m || H(ek)) */
    memcpy(K,Kr,32);
    kpke_encrypt(ek,m,Kr+32,c);
    secure_zero(g_in,sizeof g_in); secure_zero(Kr,sizeof Kr); /* #3: holds m, K and coins */
    return MLKEM_OK;
}

/* Decaps: recover m', re-derive (K',r'), and RE-ENCRYPT. If the fresh
   ciphertext c' equals the received c, the sender was honest and K' is the key.
   If not, return a pseudo-random reject key J(z||c) instead of failing -- this
   "implicit rejection" is what stops chosen-ciphertext attacks. */
static int mlkem_decaps(const uint8_t *dk,size_t dk_len,const uint8_t *c,size_t c_len,uint8_t K[SS_BYTES]){
    /* #2 input validation: length (type) checks before touching key or ct. */
    if(dk_len!=DK_BYTES) return MLKEM_ERR_DK_LEN;
    if(c_len !=CT_BYTES) return MLKEM_ERR_CT_LEN;
    const uint8_t*dkpke=dk;
    const uint8_t*ek   =dk+PKE_SK_BYTES;
    const uint8_t*h    =dk+PKE_SK_BYTES+PKE_PK_BYTES;
    const uint8_t*z    =dk+PKE_SK_BYTES+PKE_PK_BYTES+32;
    uint8_t mp[32]; kpke_decrypt(dkpke,c,mp);          /* m' */
    uint8_t g_in[64]; memcpy(g_in,mp,32); memcpy(g_in+32,h,32);
    uint8_t Kr[64]; sha3_512(g_in,64,Kr);              /* (K',r') = G(m' || H(ek)) */
    uint8_t cprime[CT_BYTES]; kpke_encrypt(ek,mp,Kr+32,cprime);
    uint8_t Kbar[32]; { uint8_t zc[SEED_BYTES+CT_BYTES];
        memcpy(zc,z,SEED_BYTES); memcpy(zc+SEED_BYTES,c,CT_BYTES);
        shake256(zc,SEED_BYTES+CT_BYTES,Kbar,32);       /* Kbar = J(z || c) */
        secure_zero(zc,sizeof zc); }                    /* #3: zc embeds the secret z */
    /* #1 constant-time select: the compare runs over the whole ciphertext (no
       early exit), and the K' vs Kbar choice is a branch-free masked select, so
       Decaps does not leak whether implicit rejection fired. */
    int diff=0; for(int i=0;i<CT_BYTES;i++) diff|=c[i]^cprime[i];
    uint8_t mask=ct_eq0_mask((uint32_t)diff);          /* 0xFF iff c'==c, else 0x00 */
    ct_select(K,Kr,Kbar,32,mask);                      /* K = (c'==c) ? K' : Kbar */
    /* #3: m', the (K',r') buffer, and both candidate keys are secret. */
    secure_zero(mp,sizeof mp); secure_zero(g_in,sizeof g_in);
    secure_zero(Kr,sizeof Kr); secure_zero(Kbar,sizeof Kbar);
    return MLKEM_OK;
}

/* Hardening #4: the entry points an application should actually call. They pull
   their own randomness from the CSPRNG (never the test xorshift) and wipe the
   seed material afterwards. The deterministic mlkem_keygen / mlkem_encaps above
   remain available for KATs and for the internal re-encryption in Decaps. */
static int mlkem_keygen_rand(uint8_t ek[PKE_PK_BYTES],uint8_t dk[DK_BYTES]){
    uint8_t d[SEED_BYTES],z[SEED_BYTES];
    if(randombytes(d,SEED_BYTES)||randombytes(z,SEED_BYTES)){
        secure_zero(d,sizeof d); secure_zero(z,sizeof z); return MLKEM_ERR_RNG; }
    mlkem_keygen(d,z,ek,dk);
    secure_zero(d,sizeof d); secure_zero(z,sizeof z);
    return MLKEM_OK;
}
static int mlkem_encaps_rand(const uint8_t *ek,size_t ek_len,uint8_t K[SS_BYTES],uint8_t c[CT_BYTES]){
    uint8_t m[32];
    if(randombytes(m,sizeof m)){ secure_zero(m,sizeof m); return MLKEM_ERR_RNG; }
    int rv=mlkem_encaps(ek,ek_len,m,K,c);   /* may still reject a malformed ek (#2) */
    secure_zero(m,sizeof m);
    return rv;
}

static void print_hex(const char*label,const uint8_t*d,size_t n){
    printf("%s (%zu bytes):\n  ",label,n);
    for(size_t i=0;i<n;i++){ printf("%02x",d[i]); if((i+1)%32==0&&i+1<n) printf("\n  "); }
    printf("\n");
}

/* Self-tests. The first checks the hash layer against published values (the
   only thing that catches a wrong-but-consistent hash); the rest check the
   maths and the KEM by consistency. All run before the demo and abort on
   failure. */
static unsigned rng=2463534242u;                         /* tiny xorshift, for tests only */
static int rc(void){ rng^=rng<<13; rng^=rng>>17; rng^=rng<<5; return rng%KYBER_Q; }

static int poly_eq(const poly a,const poly b){
    for(int i=0;i<KYBER_N;i++)
        if(((a[i]%KYBER_Q+KYBER_Q)%KYBER_Q)!=((b[i]%KYBER_Q+KYBER_Q)%KYBER_Q)) return 0;
    return 1;
}
/* Plain schoolbook multiply in R_q = Z_q[X]/(X^256+1): the slow reference the
   fast NTT path is checked against. The wrap X^256 = -1 is the minus sign. */
static void school(poly r,const poly a,const poly b){
    long acc[KYBER_N]; for(int i=0;i<KYBER_N;i++) acc[i]=0;
    for(int i=0;i<KYBER_N;i++) for(int j=0;j<KYBER_N;j++){
        long p=(long)a[i]*b[j]; int k=i+j;
        if(k<KYBER_N) acc[k]+=p; else acc[k-KYBER_N]-=p; }
    for(int i=0;i<KYBER_N;i++) r[i]=(int16_t)(((acc[i]%KYBER_Q)+KYBER_Q)%KYBER_Q);
}

static int selftests(void){
    int ok=1;

    /* Hash KATs: empty-string vectors validate Keccak + domain separation
       across all three rates used (72, 136, 168). */
    {
        uint8_t o[64];
        static const uint8_t k256[32]={
            0xa7,0xff,0xc6,0xf8,0xbf,0x1e,0xd7,0x66,0x51,0xc1,0x47,0x56,0xa0,0x61,0xd6,0x62,
            0xf5,0x80,0xff,0x4d,0xe4,0x3b,0x49,0xfa,0x82,0xd8,0x0a,0x4b,0x80,0xf8,0x43,0x4a};
        static const uint8_t k512[64]={
            0xa6,0x9f,0x73,0xcc,0xa2,0x3a,0x9a,0xc5,0xc8,0xb5,0x67,0xdc,0x18,0x5a,0x75,0x6e,
            0x97,0xc9,0x82,0x16,0x4f,0xe2,0x58,0x59,0xe0,0xd1,0xdc,0xc1,0x47,0x5c,0x80,0xa6,
            0x15,0xb2,0x12,0x3a,0xf1,0xf5,0xf9,0x4c,0x11,0xe3,0xe9,0x40,0x2c,0x3a,0xc5,0x58,
            0xf5,0x00,0x19,0x9d,0x95,0xb6,0xd3,0xe3,0x01,0x75,0x85,0x86,0x28,0x1d,0xcd,0x26};
        static const uint8_t s256[32]={
            0x46,0xb9,0xdd,0x2b,0x0b,0xa8,0x8d,0x13,0x23,0x3b,0x3f,0xeb,0x74,0x3e,0xeb,0x24,
            0x3f,0xcd,0x52,0xea,0x62,0xb8,0x1b,0x82,0xb5,0x0c,0x27,0x64,0x6e,0xd5,0x76,0x2f};
        static const uint8_t s128[32]={
            0x7f,0x9c,0x2b,0xa4,0xe8,0x8f,0x82,0x7d,0x61,0x60,0x45,0x50,0x76,0x05,0x85,0x3e,
            0xd7,0x3b,0x80,0x93,0xf6,0xef,0xbc,0x88,0xeb,0x1a,0x6e,0xac,0xfa,0x66,0xef,0x26};
        const uint8_t *e=(const uint8_t*)"";
        sha3_256(e,0,o); if(memcmp(o,k256,32)){ ok=0; printf("  [FAIL] SHA3-256 KAT\n"); }
        sha3_512(e,0,o); if(memcmp(o,k512,64)){ ok=0; printf("  [FAIL] SHA3-512 KAT\n"); }
        shake256(e,0,o,32); if(memcmp(o,s256,32)){ ok=0; printf("  [FAIL] SHAKE256 KAT\n"); }
        shake128(e,0,o,32); if(memcmp(o,s128,32)){ ok=0; printf("  [FAIL] SHAKE128 KAT\n"); }
        if(ok) printf("  [PASS] hash KATs: SHA3-256/512, SHAKE128/256 (empty-string vectors)\n");
    }

    /* INTT(NTT(x)) must return x. */
    for(int t=0;t<50;t++){ poly a,a0; for(int i=0;i<KYBER_N;i++) a[i]=a0[i]=(int16_t)rc();
        poly_ntt(a); poly_intt(a); if(!poly_eq(a,a0)){ ok=0; printf("  [FAIL] NTT.INTT\n"); break; } }
    if(ok) printf("  [PASS] NTT then INTT = identity (50 polys)\n");

    /* The fast NTT product must equal the slow schoolbook product. */
    int m=1;
    for(int t=0;t<50;t++){ poly a,b,ah,bh,ch,cn,cs;
        for(int i=0;i<KYBER_N;i++){ a[i]=(int16_t)rc(); b[i]=(int16_t)rc(); }
        memcpy(ah,a,sizeof a); memcpy(bh,b,sizeof b); poly_ntt(ah); poly_ntt(bh);
        poly_basemul(ch,ah,bh); memcpy(cn,ch,sizeof ch); poly_intt(cn); school(cs,a,b);
        if(!poly_eq(cn,cs)){ m=0; ok=0; printf("  [FAIL] basemul\n"); break; } }
    if(m) printf("  [PASS] INTT(basemul(NTT a,NTT b)) = a*b in R_q (50 trials)\n");

    /* End-to-end: Decaps(Encaps) must agree on K; a flipped ciphertext byte
       must trigger implicit rejection (a different key). */
    int kem=1,rej=1;
    for(int t=0;t<20;t++){
        uint8_t d[32],z[32],msg[32];
        for(int i=0;i<32;i++){ d[i]=(uint8_t)rc(); z[i]=(uint8_t)rc(); msg[i]=(uint8_t)rc(); }
        uint8_t ek[PKE_PK_BYTES]; uint8_t dk[DK_BYTES];
        mlkem_keygen(d,z,ek,dk);
        uint8_t Ka[32],Kb[32],ct[CT_BYTES];
        if(mlkem_encaps(ek,PKE_PK_BYTES,msg,Ka,ct)!=MLKEM_OK){ kem=0; ok=0; printf("  [FAIL] encaps rejected valid ek (trial %d)\n",t); break; }
        if(mlkem_decaps(dk,DK_BYTES,ct,CT_BYTES,Kb)!=MLKEM_OK){ kem=0; ok=0; printf("  [FAIL] decaps rejected valid input (trial %d)\n",t); break; }
        if(memcmp(Ka,Kb,32)!=0){ kem=0; ok=0; printf("  [FAIL] KEM round-trip (trial %d)\n",t); break; }
        uint8_t ctb[CT_BYTES]; memcpy(ctb,ct,CT_BYTES); ctb[0]^=0xFF;
        uint8_t Kr[32]; mlkem_decaps(dk,DK_BYTES,ctb,CT_BYTES,Kr);
        if(memcmp(Kr,Ka,32)==0){ rej=0; ok=0; printf("  [FAIL] implicit rejection (trial %d)\n",t); break; }
    }
    if(kem) printf("  [PASS] KEM round-trip: Decaps(Encaps) recovers shared secret (20 trials)\n");
    if(rej) printf("  [PASS] implicit rejection: tampered ct -> different key (20 trials)\n");

    /* Hardening #2: input validation must reject malformed inputs. */
    {
        uint8_t d[32],z[32]; for(int i=0;i<32;i++){ d[i]=(uint8_t)rc(); z[i]=(uint8_t)rc(); }
        uint8_t ek[PKE_PK_BYTES]; uint8_t dk[DK_BYTES]; mlkem_keygen(d,z,ek,dk);
        uint8_t Kx[32],ctx[CT_BYTES],msg[32]; for(int i=0;i<32;i++) msg[i]=(uint8_t)rc();
        int v=1;
        /* wrong ek length -> EK_LEN */
        if(mlkem_encaps(ek,PKE_PK_BYTES-1,msg,Kx,ctx)!=MLKEM_ERR_EK_LEN){ v=0; ok=0; printf("  [FAIL] encaps accepted short ek\n"); }
        /* non-canonical ek (force a coeff to q=3329=0x0D01 in the first slot) -> EK_RANGE.
           Coeff 0 occupies the low 12 bits of bytes 0..1: set them to q. */
        { uint8_t bad[PKE_PK_BYTES]; memcpy(bad,ek,PKE_PK_BYTES);
          bad[0]=(uint8_t)(KYBER_Q&0xFF); bad[1]=(uint8_t)((bad[1]&0xF0)|((KYBER_Q>>8)&0x0F));
          if(mlkem_encaps(bad,PKE_PK_BYTES,msg,Kx,ctx)!=MLKEM_ERR_EK_RANGE){ v=0; ok=0; printf("  [FAIL] encaps accepted non-canonical ek\n"); } }
        /* a valid ek must still pass */
        if(mlkem_encaps(ek,PKE_PK_BYTES,msg,Kx,ctx)!=MLKEM_OK){ v=0; ok=0; printf("  [FAIL] encaps rejected canonical ek\n"); }
        /* wrong dk / ct lengths -> DK_LEN / CT_LEN */
        if(mlkem_decaps(dk,DK_BYTES-1,ctx,CT_BYTES,Kx)!=MLKEM_ERR_DK_LEN){ v=0; ok=0; printf("  [FAIL] decaps accepted short dk\n"); }
        if(mlkem_decaps(dk,DK_BYTES,ctx,CT_BYTES+1,Kx)!=MLKEM_ERR_CT_LEN){ v=0; ok=0; printf("  [FAIL] decaps accepted wrong ct length\n"); }
        if(v) printf("  [PASS] input validation: bad ek length / non-canonical ek / bad dk,ct length all rejected\n");
    }

    /* Hardening #4: the CSPRNG wrappers must produce working, fresh keys. */
    {
        int r=1;
        uint8_t ek1[PKE_PK_BYTES],dk1[DK_BYTES],ek2[PKE_PK_BYTES],dk2[DK_BYTES];
        if(mlkem_keygen_rand(ek1,dk1)!=MLKEM_OK||mlkem_keygen_rand(ek2,dk2)!=MLKEM_OK){ r=0; ok=0; printf("  [FAIL] keygen_rand returned error\n"); }
        if(r&&memcmp(ek1,ek2,PKE_PK_BYTES)==0){ r=0; ok=0; printf("  [FAIL] keygen_rand produced identical keys (no entropy)\n"); }
        uint8_t Ka[32],Kb[32],ct[CT_BYTES];
        if(r&&mlkem_encaps_rand(ek1,PKE_PK_BYTES,Ka,ct)!=MLKEM_OK){ r=0; ok=0; printf("  [FAIL] encaps_rand returned error\n"); }
        if(r&&mlkem_decaps(dk1,DK_BYTES,ct,CT_BYTES,Kb)!=MLKEM_OK){ r=0; ok=0; printf("  [FAIL] decaps after encaps_rand returned error\n"); }
        if(r&&memcmp(Ka,Kb,32)!=0){ r=0; ok=0; printf("  [FAIL] encaps_rand/decaps shared secret mismatch\n"); }
        if(r) printf("  [PASS] CSPRNG wrappers: fresh keypairs + encaps_rand round-trip\n");
    }

    /* Hardening #6: deterministic regression KAT. With fixed (d,z,m) the whole
       KEM is deterministic, so we pin SHA3-256(ek || ct || K). This locks the
       behavior across edits. It is SELF-GENERATED, NOT the official NIST ACVP
       vector set -- running those needs the NIST response files fed through the
       same deterministic mlkem_keygen / mlkem_encaps entry points used here. */
    {
        uint8_t dk_seed[32]={0x7f,0x9c,0x2b,0xa4,0xe8,0x8f,0x82,0x7d,0x61,0x60,0x45,0x07,0xa7,0x33,0x87,0x12,
                             0x10,0x50,0x40,0x05,0x6f,0xe8,0x3b,0x57,0x11,0x89,0x20,0xc2,0x65,0x23,0x41,0x00};
        uint8_t zz[32]; for(int i=0;i<32;i++) zz[i]=(uint8_t)(0xA0+i);
        uint8_t mm[32]; for(int i=0;i<32;i++) mm[i]=(uint8_t)(0x10+i);
        uint8_t ek[PKE_PK_BYTES],dk[DK_BYTES],Kk[32],ct[CT_BYTES];
        mlkem_keygen(dk_seed,zz,ek,dk);
        mlkem_encaps(ek,PKE_PK_BYTES,mm,Kk,ct);
        size_t L=(size_t)PKE_PK_BYTES+CT_BYTES+32; uint8_t *blob=malloc(L);
        memcpy(blob,ek,PKE_PK_BYTES); memcpy(blob+PKE_PK_BYTES,ct,CT_BYTES);
        memcpy(blob+PKE_PK_BYTES+CT_BYTES,Kk,32);
        uint8_t dig[32]; sha3_256(blob,L,dig); free(blob);
#if   KYBER_K==2   /* ML-KEM-512: SHA3-256(ek||ct||K) for the pinned seeds */
        static const uint8_t exp[32]={
            0x2c,0x41,0xc4,0x11,0xe9,0x9d,0xff,0x38,0xd6,0xdb,0x88,0x7f,0xfc,0x78,0x78,0x64,
            0x3f,0xb4,0x87,0x1a,0x76,0x22,0xac,0x2b,0x76,0x51,0x38,0x6e,0x76,0x33,0x5e,0xfd};
#elif KYBER_K==3   /* ML-KEM-768 */
        static const uint8_t exp[32]={
            0xb7,0x14,0x1a,0x49,0xc3,0xbe,0x46,0x6f,0x7c,0x7d,0xee,0x05,0x9e,0x00,0xd0,0x86,
            0x15,0x35,0x37,0xea,0xef,0xad,0x0c,0xe1,0xa7,0x78,0x5b,0x35,0x04,0x98,0x4a,0xfa};
#else              /* ML-KEM-1024 */
        static const uint8_t exp[32]={
            0x15,0x19,0xf9,0x1f,0xfb,0x2d,0x7f,0x4c,0xad,0x35,0x56,0xcd,0xea,0x9e,0x73,0x61,
            0xdc,0xdd,0x91,0x04,0x6f,0xfb,0xaf,0x79,0xd4,0xeb,0x3f,0x13,0xc5,0x30,0xc9,0xab};
#endif
        if(memcmp(dig,exp,32)){
            ok=0; printf("  [FAIL] deterministic regression KAT (digest changed)\n  got: ");
            for(int i=0;i<32;i++) printf("%02x",dig[i]);
            printf("\n");
        } else {
            printf("  [PASS] deterministic regression KAT (self-generated; not NIST ACVP)\n");
        }
    }
    return ok;
}

int main(void){
    printf("ML-KEM-%d  (FIPS 203, k=%d eta1=%d eta2=%d du=%d dv=%d)\n",
           KYBER_NAME,KYBER_K,KYBER_ETA1,KYBER_ETA2,KYBER_DU,KYBER_DV);
    printf("Self-tests:\n");
    if(!selftests()){ printf("SELF-TESTS FAILED.\n"); return 1; }
    printf("All self-tests passed.\n\n");

    /* Demo with fixed seeds so the output is reproducible. In production d, z
       and m must each come from a cryptographically secure RNG. */
    uint8_t d[32]={0x7f,0x9c,0x2b,0xa4,0xe8,0x8f,0x82,0x7d,0x61,0x60,0x45,0x07,0xa7,0x33,0x87,0x12,
                   0x10,0x50,0x40,0x05,0x6f,0xe8,0x3b,0x57,0x11,0x89,0x20,0xc2,0x65,0x23,0x41,0x00};
    uint8_t z[32]; for(int i=0;i<32;i++) z[i]=(uint8_t)(0xA0+i);
    uint8_t m[32]; for(int i=0;i<32;i++) m[i]=(uint8_t)(0x10+i);

    uint8_t ek[PKE_PK_BYTES]; uint8_t dk[DK_BYTES];
    mlkem_keygen(d,z,ek,dk);                 /* receiver makes a keypair      */
    uint8_t Ka[32],ct[CT_BYTES];
    if(mlkem_encaps(ek,PKE_PK_BYTES,m,Ka,ct)!=MLKEM_OK){ printf("ENCAPS REJECTED INPUT.\n"); return 1; }
    uint8_t Kb[32];
    if(mlkem_decaps(dk,DK_BYTES,ct,CT_BYTES,Kb)!=MLKEM_OK){ printf("DECAPS REJECTED INPUT.\n"); return 1; }

    printf(" ML-KEM-%d full KEM (deterministic demo) \n",KYBER_NAME);
    printf("Sizes: ek=%d  dk=%d  ct=%d  ss=%d\n\n",PKE_PK_BYTES,DK_BYTES,CT_BYTES,SS_BYTES);
    print_hex("ek (first 192 bytes)",ek,PKE_PK_BYTES>192?192:PKE_PK_BYTES);
    printf("   ... (%d bytes total)\n\n",PKE_PK_BYTES);
    print_hex("ct (first 192 bytes)",ct,CT_BYTES>192?192:CT_BYTES);
    printf("   ... (%d bytes total)\n\n",CT_BYTES);
    print_hex("K  (shared secret, Encaps side)",Ka,32);
    print_hex("K' (shared secret, Decaps side)",Kb,32);
    printf("\nShared secrets match: %s\n", memcmp(Ka,Kb,32)==0?"YES":"NO");

    /* #4: the same exchange using the CSPRNG wrappers an application would call.
       Keys differ on every run, so we only report agreement, not the bytes. */
    uint8_t ekr[PKE_PK_BYTES],dkr[DK_BYTES],Kar[32],Kbr[32],ctr[CT_BYTES];
    if(mlkem_keygen_rand(ekr,dkr)!=MLKEM_OK ||
       mlkem_encaps_rand(ekr,PKE_PK_BYTES,Kar,ctr)!=MLKEM_OK ||
       mlkem_decaps(dkr,DK_BYTES,ctr,CT_BYTES,Kbr)!=MLKEM_OK){
        printf("CSPRNG exchange failed (no entropy source?).\n"); return 1;
    }
    printf("CSPRNG-seeded exchange (random keys) match: %s\n", memcmp(Kar,Kbr,32)==0?"YES":"NO");
    return 0;
}