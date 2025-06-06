#this script should first run on windows to make the usb device (telemetry radio available on wsl)

# Check for admin rights
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(`
    [Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "This script must be run as Administrator!"
    Start-Sleep -Seconds 3
    exit 1
}

# Define the bus ID (you can customize this)
$busid = "1-8"

# Run the commands
Write-Output "Binding USB device with busid $busid..."
usbipd bind --busid $busid

Write-Output "Attaching USB device to WSL..."
usbipd attach --wsl --busid $busid

Write-Output "Done!"