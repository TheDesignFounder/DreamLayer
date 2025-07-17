# Dream Layer Windows Dependencies Installation Script (PowerShell)
# This script installs all the necessary dependencies for running Dream Layer on Windows

param(
    [switch]$Force,
    [switch]$SkipPackageManager,
    [string]$PackageManager = "auto"
)

# Ensure we can run scripts
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force -ErrorAction SilentlyContinue

# Colors for output
$Colors = @{
    Red = "Red"
    Green = "Green"
    Yellow = "Yellow"
    Blue = "Blue"
    Purple = "Magenta"
    Cyan = "Cyan"
    White = "White"
    Gray = "Gray"
}

# Functions for colored output
function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "================================" -ForegroundColor $Colors.Purple
    Write-Host $Message -ForegroundColor $Colors.Purple
    Write-Host "================================" -ForegroundColor $Colors.Purple
    Write-Host ""
}

function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor $Colors.Blue -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] " -ForegroundColor $Colors.Green -NoNewline
    Write-Host $Message
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor $Colors.Yellow -NoNewline
    Write-Host $Message
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor $Colors.Red -NoNewline
    Write-Host $Message
}

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] " -ForegroundColor $Colors.Cyan -NoNewline
    Write-Host $Message
}

# Function to check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction SilentlyContinue | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to check Windows version
function Get-WindowsVersion {
    $version = [System.Environment]::OSVersion.Version
    $versionString = "$($version.Major).$($version.Minor).$($version.Build)"
    
    Write-Status "Detected Windows version: $versionString"
    
    if ($version.Major -eq 10 -and $version.Build -ge 17763) {
        Write-Success "Windows 10 (1809+) or Windows 11 detected - Full compatibility"
        return $true
    }
    elseif ($version.Major -eq 10) {
        Write-Warning "Windows 10 (older version) - Some features may be limited"
        return $true
    }
    elseif ($version.Major -eq 6 -and $version.Minor -ge 1) {
        Write-Warning "Windows 7/8 detected - Limited compatibility, consider upgrading"
        return $true
    }
    else {
        Write-Error-Custom "Unsupported Windows version"
        return $false
    }
}

# Function to check for long path support
function Check-LongPathSupport {
    Write-Step "Checking for long path support..."
    $longPathEnabled = Get-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -ErrorAction SilentlyContinue
    if ($longPathEnabled -and $longPathEnabled.LongPathsEnabled -eq 1) {
        Write-Success "Long path support is enabled."
    } else {
        Write-Warning "Long path support is not enabled. This can cause issues with long file paths."
        Write-Warning "To enable it, run the following command in an elevated PowerShell prompt:"
        Write-Warning 'Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1'
    }
}

# Function to detect package manager
function Get-PackageManager {
    Write-Step "Detecting package manager..."
    
    if (Test-Command "winget") {
        Write-Success "Winget detected and available"
        return "winget"
    }
    
    if (Test-Command "choco") {
        Write-Success "Chocolatey detected and available"
        return "chocolatey"
    }
    
    if (Test-Command "scoop") {
        Write-Success "Scoop detected and available"
        return "scoop"
    }
    
    Write-Warning "No package manager detected."
    Write-Warning "Please install a package manager like Winget, Chocolatey, or Scoop."
    Write-Warning "Winget is recommended for modern Windows versions."
    return "none"
}

# Function to install packages using detected package manager
function Install-Package {
    param(
        [string]$PackageManager,
        [string]$PackageName,
        [string]$WingetId = "",
        [string]$ChocoName = "",
        [string]$ScoopName = ""
    )
    
    switch ($PackageManager) {
        "winget" {
            $id = if ($WingetId) { $WingetId } else { $PackageName }
            Write-Status "Installing $PackageName via Winget..."
            winget install $id --accept-package-agreements --accept-source-agreements --silent
        }
        "chocolatey" {
            $name = if ($ChocoName) { $ChocoName } else { $PackageName }
            Write-Status "Installing $PackageName via Chocolatey..."
            choco install $name -y
        }
        "scoop" {
            $name = if ($ScoopName) { $ScoopName } else { $PackageName }
            Write-Status "Installing $PackageName via Scoop..."
            scoop install $name
        }
        default {
            Write-Error-Custom "No package manager available for $PackageName"
            return $false
        }
    }
    
    return $LASTEXITCODE -eq 0
}

# Function to install Python
function Install-Python {
    param([string]$PackageManager)
    
    if (Test-Command "python") {
        try {
            $pythonVersion = python --version 2>&1
            Write-Status "Python is already installed: $pythonVersion"
            
            # Check version
            $versionMatch = $pythonVersion -match "Python (\d+)\.(\d+)"
            if ($versionMatch) {
                $major = [int]$Matches[1]
                $minor = [int]$Matches[2]
                
                if ($major -eq 3 -and $minor -ge 8) {
                    Write-Success "Python version is compatible (3.8+)"
                    return $true
                }
                else {
                    Write-Warning "Python 3.8+ is recommended. Current version: $pythonVersion"
                }
            }
        }
        catch {
            Write-Warning "Could not determine Python version"
        }
    }
    
    Write-Step "Installing Python..."
    $result = Install-Package $PackageManager "Python" -WingetId "Python.Python.3.11" -ChocoName "python" -ScoopName "python"
    
    if ($result) {
        # Refresh PATH
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        
        # Verify installation
        if (Test-Command "python") {
            Write-Success "Python installed successfully"
            
            # Upgrade pip
            Write-Step "Upgrading pip..."
            python -m pip install --upgrade pip
            return $true
        }
    }
    
    Write-Error-Custom "Failed to install Python"
    return $false
}

# Function to install Node.js
function Install-NodeJS {
    param([string]$PackageManager)
    
    if (Test-Command "node") {
        try {
            $nodeVersion = node --version
            Write-Status "Node.js is already installed: $nodeVersion"
            
            $versionNumber = $nodeVersion -replace "v", "" -split "\." | Select-Object -First 1
            if ([int]$versionNumber -ge 16) {
                Write-Success "Node.js version is compatible (16+)"
            }
            else {
                Write-Warning "Node.js 16+ is recommended. Current version: $nodeVersion"
            }
        }
        catch {
            Write-Warning "Could not determine Node.js version"
        }
    }
    else {
        Write-Step "Installing Node.js..."
        $result = Install-Package $PackageManager "Node.js" -WingetId "OpenJS.NodeJS" -ChocoName "nodejs" -ScoopName "nodejs"
        
        if ($result) {
            # Refresh PATH
            $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        }
    }
    
    # Verify Node.js and npm
    if (Test-Command "node" -and Test-Command "npm") {
        Write-Success "Node.js and npm are available"
        
        # Update npm
        Write-Step "Updating npm..."
        try {
            npm install -g npm@latest
        }
        catch {
            Write-Warning "Could not update npm, but it's available"
        }
        return $true
    }
    
    Write-Error-Custom "Failed to install Node.js"
    return $false
}

# Function to install system dependencies
function Install-SystemDependencies {
    param([string]$PackageManager)
    
    Write-Step "Installing system dependencies..."
    
    $packages = @(
        @{ Name = "Git"; WingetId = "Git.Git"; ChocoName = "git"; ScoopName = "git" },
        @{ Name = "FFmpeg"; WingetId = "Gyan.FFmpeg"; ChocoName = "ffmpeg"; ScoopName = "ffmpeg" },
        @{ Name = "7-Zip"; WingetId = "7zip.7zip"; ChocoName = "7zip"; ScoopName = "7zip" }
    )
    
    foreach ($package in $packages) {
        $commandName = $package.Name.ToLower()
        if ($commandName -eq "7-zip") { $commandName = "7z" }
        
        if (-not (Test-Command $commandName)) {
            Write-Status "Installing $($package.Name)..."
            Install-Package $PackageManager $package.Name -WingetId $package.WingetId -ChocoName $package.ChocoName -ScoopName $package.ScoopName
        }
        else {
            Write-Status "$($package.Name) is already installed"
        }
    }
    
    # Refresh PATH
    $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
    
    Write-Success "System dependencies installation completed"
}

# Function to install Python dependencies
function Install-PythonDependencies {
    Write-Step "Installing Python dependencies..."
    
    # Install backend dependencies
    if (Test-Path "dream_layer_backend\requirements.txt") {
        Write-Step "Installing Dream Layer backend dependencies..."
        try {
            python -m pip install -r "dream_layer_backend\requirements.txt"
            Write-Success "Backend dependencies installed"
        }
        catch {
            Write-Error-Custom "Failed to install backend dependencies: $($_.Exception.Message)"
            return $false
        }
    }
    else {
        Write-Warning "dream_layer_backend\requirements.txt not found"
    }
    
    # Install ComfyUI dependencies
    if (Test-Path "ComfyUI\requirements.txt") {
        Write-Step "Installing ComfyUI dependencies..."
        try {
            python -m pip install -r "ComfyUI\requirements.txt"
            Write-Success "ComfyUI dependencies installed"
        }
        catch {
            Write-Error-Custom "Failed to install ComfyUI dependencies: $($_.Exception.Message)"
            return $false
        }
    }
    else {
        Write-Warning "ComfyUI\requirements.txt not found"
    }
    
    # Install PyTorch with automatic GPU detection
    Write-Step "Installing PyTorch..."
    
    # Check for NVIDIA GPU and drivers
    $hasNvidiaGPU = $false
    try {
        $nvidiaSmiResult = nvidia-smi
        if ($nvidiaSmiResult) {
            $hasNvidiaGPU = $true
        }
    }
    catch {
        # nvidia-smi not found or failed to run
    }

    if ($hasNvidiaGPU) {
        Write-Status "NVIDIA GPU detected. Installing PyTorch with CUDA support..."
        Write-Status "This will enable GPU acceleration for faster AI processing."
        try {
            python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
            Write-Success "PyTorch with CUDA support installed successfully."
        }
        catch {
            Write-Error-Custom "Failed to install PyTorch with CUDA support."
            Write-Error-Custom "Please ensure you have the latest NVIDIA drivers installed."
            Write-Error-Custom "You can also try installing it manually by running the following command:"
            Write-Error-Custom "python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
            return $false
        }
    }
    else {
        Write-Status "No NVIDIA GPU detected. Installing the CPU version of PyTorch."
        try {
            python -m pip install torch torchvision torchaudio
            Write-Success "PyTorch (CPU version) installed successfully."
        }
        catch {
            Write-Error-Custom "Failed to install PyTorch (CPU version): $($_.Exception.Message)"
            return $false
        }
    }
    
    return $true
}

# Function to install frontend dependencies
function Install-FrontendDependencies {
    Write-Step "Installing frontend dependencies..."
    
    if (Test-Path "dream_layer_frontend\package.json") {
        try {
            Push-Location "dream_layer_frontend"
            Write-Status "Installing Node.js dependencies..."
            npm install
            Write-Success "Frontend dependencies installed"
            return $true
        }
        catch {
            Write-Error-Custom "Failed to install frontend dependencies: $($_.Exception.Message)"
            return $false
        }
        finally {
            Pop-Location
        }
    }
    else {
        Write-Warning "dream_layer_frontend\package.json not found"
        return $false
    }
}

# Function to setup environment
function Set-Environment {
    Write-Step "Setting up environment..."
    
    # Create necessary directories
    $directories = @("logs", "dream_layer_backend\input", "dream_layer_backend\served_images")
    foreach ($dir in $directories) {
        if (-not (Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Status "Created directory: $dir"
        }
    }
    
    # Create .env template if it doesn't exist
    if (-not (Test-Path ".env")) {
        Write-Step "Creating .env template..."
        $envContent = @"
# Dream Layer Environment Configuration
# Copy this file and update with your actual values

# API Keys (optional - for external services)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=true

# ComfyUI Configuration
COMFYUI_PATH=../ComfyUI
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
"@
        $envContent | Out-File -FilePath ".env" -Encoding UTF8
        Write-Success "Created .env template"
        Write-Warning "Please update .env with your actual configuration"
    }
    
    Write-Success "Environment setup completed"
}

# Function to run post-installation tests
function Test-Installation {
    Write-Step "Running post-installation tests..."
    
    # Test Python
    try {
        $pythonTest = python -c "import flask, PIL, requests; print('Python dependencies OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Python dependencies test passed"
        }
        else {
            Write-Error-Custom "Python dependencies test failed"
        }
    }
    catch {
        Write-Error-Custom "Python dependencies test failed: $($_.Exception.Message)"
    }
    
    # Test Node.js
    try {
        $nodeTest = node -e "console.log('Node.js test OK')" 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Node.js test passed"
        }
        else {
            Write-Error-Custom "Node.js test failed"
        }
    }
    catch {
        Write-Error-Custom "Node.js test failed: $($_.Exception.Message)"
    }
    
    # Test npm
    try {
        npm --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Success "npm test passed"
        }
        else {
            Write-Error-Custom "npm test failed"
        }
    }
    catch {
        Write-Error-Custom "npm test failed: $($_.Exception.Message)"
    }
}

# Function to display final instructions
function Show-FinalInstructions {
    Write-Header "INSTALLATION COMPLETE!"
    
    Write-Host "✅ All dependencies have been installed successfully!" -ForegroundColor $Colors.Green
    Write-Host ""
    
    Write-Host "Next steps:" -ForegroundColor $Colors.Cyan
    Write-Host "1. " -ForegroundColor $Colors.Yellow -NoNewline
    Write-Host "Configure your environment:" -ForegroundColor $Colors.Yellow
    Write-Host "   • Edit " -NoNewline
    Write-Host ".env" -ForegroundColor $Colors.Blue -NoNewline
    Write-Host " with your API keys and preferences"
    Write-Host ""
    
    Write-Host "2. " -ForegroundColor $Colors.Yellow -NoNewline
    Write-Host "Start the application:" -ForegroundColor $Colors.Yellow
    Write-Host "   • Run: " -NoNewline
    Write-Host "start_dream_layer.bat" -ForegroundColor $Colors.Blue -NoNewline
    Write-Host ""
    
    Write-Host "3. " -ForegroundColor $Colors.Yellow -NoNewline
    Write-Host "Access the application:" -ForegroundColor $Colors.Yellow
    Write-Host "   • Frontend: " -NoNewline
    Write-Host "http://localhost:8080" -ForegroundColor $Colors.Blue
    Write-Host "   • Main API: " -NoNewline
    Write-Host "http://localhost:5002" -ForegroundColor $Colors.Blue
    Write-Host "   • ComfyUI: " -NoNewline
    Write-Host "http://localhost:8188" -ForegroundColor $Colors.Blue
    Write-Host ""
    
    Write-Host "Troubleshooting:" -ForegroundColor $Colors.Cyan
    Write-Host "• Check logs in the " -NoNewline
    Write-Host "logs\" -ForegroundColor $Colors.Blue -NoNewline
    Write-Host " directory"
    Write-Host "• Ensure all ports (8080, 5001-5004, 8188) are available"
    Write-Host "• Update Python packages: " -NoNewline
    Write-Host "python -m pip install --upgrade -r requirements.txt" -ForegroundColor $Colors.Blue
    Write-Host "• Update Node packages: " -NoNewline
    Write-Host "cd dream_layer_frontend && npm update" -ForegroundColor $Colors.Blue
    Write-Host ""
    
    Write-Host "Happy creating with Dream Layer! 🎨✨" -ForegroundColor $Colors.Green
}

# Main installation function
function Start-Installation {
    Write-Header "DREAM LAYER WINDOWS INSTALLATION (PowerShell)"
    
    Write-Host "This script will install all dependencies required for Dream Layer:" -ForegroundColor $Colors.Cyan
    Write-Host "• Package manager (Winget/Chocolatey)"
    Write-Host "• Python 3.8+ and pip"
    Write-Host "• Node.js 16+ and npm"
    Write-Host "• System libraries (Git, FFmpeg, etc.)"
    Write-Host "• Python packages (Flask, PyTorch, ComfyUI dependencies)"
    Write-Host "• Node.js packages (React, TypeScript, Vite)"
    Write-Host ""
    
    if (-not $Force) {
        $response = Read-Host "Do you want to continue? (y/N)"
        if ($response -notmatch "^[Yy]") {
            Write-Status "Installation cancelled"
            exit 0
        }
    }
    
    # Check if running in correct directory
    if (-not (Test-Path "dream_layer_backend")) {
        Write-Error-Custom "This script must be run from the Dream Layer project root directory!"
        Write-Error-Custom "Please navigate to the DreamLayer folder and try again."
        exit 1
    }
    
    # Check administrator privileges
    if (Test-Administrator) {
        Write-Success "Running as Administrator - Full privileges available"
    }
    else {
        Write-Warning "Not running as Administrator - Some installations may fail"
        Write-Status "Consider right-clicking and selecting 'Run as Administrator'"
    }
    
    try {
        # Check Windows version
        Write-Header "SYSTEM CHECK"
        if (-not (Get-WindowsVersion)) {
            exit 1
        }

        # Check for long path support
        Check-LongPathSupport
        
        # Get package manager
        $packageManager = Get-PackageManager
        if ($packageManager -eq "none") {
            exit 1
        }
        
        # Install Python
        Write-Header "PYTHON INSTALLATION"
        if (-not (Install-Python $packageManager)) {
            exit 1
        }
        
        # Install Node.js
        Write-Header "NODE.JS INSTALLATION"
        if (-not (Install-NodeJS $packageManager)) {
            exit 1
        }
        
        # Install system dependencies
        Write-Header "SYSTEM DEPENDENCIES"
        Install-SystemDependencies $packageManager
        
        # Install Python dependencies
        Write-Header "PYTHON DEPENDENCIES"
        if (-not (Install-PythonDependencies)) {
            exit 1
        }
        
        # Install frontend dependencies
        Write-Header "FRONTEND DEPENDENCIES"
        if (-not (Install-FrontendDependencies)) {
            exit 1
        }
        
        # Setup environment
        Write-Header "ENVIRONMENT SETUP"
        Set-Environment
        
        # Run tests
        Write-Header "POST-INSTALLATION TESTS"
        Test-Installation
        
        # Display final instructions
        Show-FinalInstructions
        
        exit 0
    }
    catch {
        Write-Error-Custom "Installation failed: $($_.Exception.Message)"
        Write-Error-Custom "Stack trace: $($_.ScriptStackTrace)"
        exit 1
    }
}

# Run main function if script is executed directly
if ($MyInvocation.InvocationName -ne '.') {
    Start-Installation
} 