# PowerShell script to automate GitHub Actions self-hosted runner setup

# Define variables
$runnerVersion = "2.322.0"
$runnerZip = "actions-runner-win-x64-$runnerVersion.zip"
$runnerUri = "https://github.com/actions/runner/releases/download/v$runnerVersion/$runnerZip"
$expectedSHA256 = "ace5de018c88492ca80a2323af53ff3f43d2c82741853efb302928f250516015"
$repoUrl = "https://github.com/whispr-dev" # Replace with your GitHub repository URL
$runnerToken = "A7XY5YIM5CT7XI4TO4P7DN3H4I2SC" # Replace with your actual runner token from GitHub
$runnerDir = "$PWD\actions-runner"

# Create and enter runner directory
if (!(Test-Path -Path $runnerDir)) {
    New-Item -ItemType Directory -Path $runnerDir
}
Set-Location -Path $runnerDir

# Download the runner package
Write-Host "Downloading GitHub Actions runner package..."
Invoke-WebRequest -Uri $runnerUri -OutFile $runnerZip

# Validate the SHA256 checksum
Write-Host "Validating checksum..."
$fileHash = (Get-FileHash -Path $runnerZip -Algorithm SHA256).Hash.ToUpper()
if ($fileHash -ne $expectedSHA256.ToUpper()) {
    throw "Computed checksum ($fileHash) does not match expected checksum ($expectedSHA256). Aborting."
} else {
    Write-Host "Checksum validation passed."
}

# Extract the runner package
Write-Host "Extracting runner package..."
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory((Join-Path $runnerDir $runnerZip), $runnerDir)

# Configure the runner
Write-Host "Configuring runner..."
& "$runnerDir\config.cmd" --url $"https:\\github.com\whispr-dev" --token $A7XY5YLZ5FJTQTF3MDUOK3LH4JEP4

# Start the runner
Write-Host "Starting the runner..."
& "$runnerDir\run.cmd"