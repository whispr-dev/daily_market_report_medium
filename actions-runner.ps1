mkdir actions-runner; cd actions-runner

Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.322.0/actions-runner-win-x64-2.322.0.zip -OutFile actions-runner-win-x64-2.322.0.zip

if((Get-FileHash -Path actions-runner-win-x64-2.322.0.zip -Algorithm SHA256).Hash.ToUpper() -ne 'ace5de018c88492ca80a2323af53ff3f43d2c82741853efb302928f250516015'.ToUpper()){ throw 'Computed checksum did not match' }

Add-Type -AssemblyName System.IO.Compression.FileSystem ; [System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD/actions-runner-win-x64-2.322.0.zip", "$PWD")


###

./config.cmd --url https://github.com/whispr-dev --token A7XY5YIM5CT7XI4TO4P7DN3H4I2SC

./run.cmd


###


