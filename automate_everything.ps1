# Step 1: Start WSL session for MyUbuntu
Start-Process "wsl.exe" -ArgumentList "-d MyUbuntu"
Start-Sleep -Seconds 5  # Give WSL time to boot

# Step 1.5 start MP
Start-Process "D:\programmas_unif\mission_planner_thesis\MissionPlanner.exe"

# Step 2: Bind USB device
Set-Location "D:\burgerlijk_ingenieur\2de jaar\thesis\rpi-copy-code-nieuw"
.\attach_usb_wsl.ps1

# Step 3: Run command inside WSL (MyUbuntu)
$wslCommand = @"
cd /mnt/d/burgerlijk_ingenieur/2de\ jaar/thesis/rpi-copy-code-nieuw
su raman -c 'bash start_mavproxy.sh 172.31.48.1'
"@

wsl.exe -d MyUbuntu bash -c "$wslCommand"
