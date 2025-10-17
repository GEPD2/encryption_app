import javax.swing.*;
import java.awt.BorderLayout;
import java.awt.Font;
import java.awt.event.*;
import java.io.*;
import java.nio.file.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

public class Installer extends JFrame {
    private JLabel statusBar;
    private JButton installButton;
    private char[] sudoPassword = null;
    public Installer() {
        setTitle("Simple Installer");
        setSize(700, 300);
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLayout(new BorderLayout(8, 8));
        // label
        JLabel welcomeLabel = new JLabel("Welcome to the Installer! Press Install to continue.", SwingConstants.CENTER);
        welcomeLabel.setFont(new Font("SansSerif", Font.BOLD, 16));
        add(welcomeLabel, BorderLayout.NORTH);
        // button
        installButton = new JButton("Install");
        installButton.addActionListener(new InstallAction());
        add(installButton, BorderLayout.CENTER);
        // status bar
        statusBar = new JLabel("Ready");
        statusBar.setBorder(BorderFactory.createEmptyBorder(10, 10, 10, 10));
        add(statusBar, BorderLayout.SOUTH);
    }
    private class InstallAction implements ActionListener {
        @Override
        public void actionPerformed(ActionEvent e) {
            installButton.setEnabled(false);
            updateStatus("Starting installation...");
            new Thread(() -> runInstallation()).start();
        }
    }
    private void runInstallation() {
        try {
            String os = System.getProperty("os.name").toLowerCase(Locale.ROOT);
            updateStatus("Detected OS: " + os);
            String distro = null;
            if (os.contains("linux")) {
                distro = detectLinuxDistro();
            }
            // Define installation strategies
            List<InstallStrategy> strategies = getInstallStrategies(os, distro);
            // Check if we need sudo
            boolean needsSudo = strategies.stream().anyMatch(s -> s.needsSudo);
            if (needsSudo && os.contains("linux")) {
                promptAndHandleSudoPassword(strategies);
            }
            // Check Python
            if (!runCommandAndCheck("python3", "--version") && !runCommandAndCheck("python", "--version")) {
                updateStatus("Python3 not found. Installation aborted.");
                clearSudoPassword();
                return;
            }
            updateStatus("Python3 detected. Checking pip...");
            if (!runCommandAndCheck("pip", "--version") && !runCommandAndCheck("pip3", "--version")) {
                updateStatus("pip not found. Attempting install via ensurepip...");
                if (!runCommand("python3", "-m", "ensurepip", "--default-pip")) {
                    runCommand("python", "-m", "ensurepip", "--default-pip");
                }
            }
            // Install libraries
            installLibraries(strategies);
            // Install whirlpool
            installWhirlpool();
            updateStatus("Installation complete!");
            clearSudoPassword();
            
        } catch (Exception ex) {
            updateStatus("Error: " + ex.getMessage());
            ex.printStackTrace();
            clearSudoPassword();
        } finally {
            SwingUtilities.invokeLater(() -> installButton.setEnabled(true));
        }
    }
    private String detectLinuxDistro() {
        try {
            Path path = Paths.get("/etc/os-release");
            if (Files.exists(path)) {
                List<String> lines = Files.readAllLines(path);
                for (String line : lines) {
                    if (line.startsWith("ID=")) {
                        return line.split("=", 2)[1].replace("\"", "").trim();
                    }
                }
            }
        } catch (Exception e) {
            updateStatus("Could not detect Linux distribution: " + e.getMessage());
        }
        return null;
    }
    private List<InstallStrategy> getInstallStrategies(String os, String distro) {
        List<InstallStrategy> strategies = new ArrayList<>();
        
        // Always try pip first (user install)
        strategies.add(new InstallStrategy("pip install --user", false));
        
        if (os.contains("win")) {
            // On Windows, use pip (winget doesn't work well for Python packages)
            strategies.add(new InstallStrategy("pip install", false));
        } else if (os.contains("linux") && distro != null) {
            switch (distro) {
                case "debian":
                case "ubuntu":
                case "kali":
                    strategies.add(new InstallStrategy("sudo apt install -y python3-", true));
                    break;
                case "fedora":
                case "rhel":
                case "centos":
                    strategies.add(new InstallStrategy("sudo dnf install -y python3-", true));
                    break;
                case "arch":
                case "manjaro":
                    strategies.add(new InstallStrategy("sudo pacman -S --noconfirm python-", true));
                    break;
                case "opensuse":
                case "sles":
                    strategies.add(new InstallStrategy("sudo zypper install -y python3-", true));
                    break;
                default:
                    strategies.add(new InstallStrategy("sudo apt install -y python3-", true));
            }
        }
        strategies.add(new InstallStrategy("pip install", false));
        
        return strategies;
    }
    private void promptAndHandleSudoPassword(List<InstallStrategy> strategies) {
        sudoPassword = promptForSudoPassword();
        if (sudoPassword == null) {
            updateStatus("Sudo password not provided. System-level installs skipped; will attempt user installs only.");
            strategies.removeIf(s -> s.needsSudo);
        } else {
            updateStatus("Sudo password provided (will be used for privileged installs).");
        }
    }
    private void installLibraries(List<InstallStrategy> strategies) {
        // Only install libraries that aren't in standard library
        List<String> libraries = Arrays.asList("kivy", "numpy", "pycryptodome", "matplotlib");
        updateStatus("Installing libraries: " + String.join(", ", libraries));
        for (String lib : libraries) {
            boolean installed = false;
            for (InstallStrategy strategy : strategies) {
                String cmd = strategy.commandTemplate + lib;
                
                if (strategy.needsSudo && sudoPassword != null) {
                    if (runShellCommandWithSudo(cmd, sudoPassword)) {
                        installed = true;
                        updateStatus("✓ Installed (system): " + lib);
                        break;
                    }
                } else {
                    if (runShellCommand(cmd)) {
                        installed = true;
                        updateStatus("✓ Installed: " + lib);
                        break;
                    }
                }
            }
            if (!installed) {
                updateStatus("✗ Failed to install " + lib);
            }
        }
    }
    private void installWhirlpool() {
        if (!runCommandAndCheck("pip", "show", "whirlpool")) {
            updateStatus("Installing Whirlpool manually...");
            // Create a temporary directory for the clone
            String tempDir = System.getProperty("java.io.tmpdir") + "python-whirlpool-" + System.currentTimeMillis();
            String commands = String.format(
                "git clone https://github.com/oohlaf/python-whirlpool.git \"%s\" && " +
                "cd \"%s\" && " +
                "python3 setup.py develop --user",
                tempDir, tempDir
            );
            if (!runShellCommand(commands)) {
                updateStatus("Manual Whirlpool install failed.");
            } else {
                // Try to clean up
                try {
                    runShellCommand("rm -rf \"" + tempDir + "\"");
                } catch (Exception e) {
                    // Ignore cleanup errors
                }
            }
        } else {
            updateStatus("Whirlpool already installed.");
        }
    }
    private static class InstallStrategy {
        String commandTemplate;
        boolean needsSudo;
        InstallStrategy(String commandTemplate, boolean needsSudo) {
            this.commandTemplate = commandTemplate;
            this.needsSudo = needsSudo;
        }
    }
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            Installer installer = new Installer();
            installer.setVisible(true);
        });
    }
}
