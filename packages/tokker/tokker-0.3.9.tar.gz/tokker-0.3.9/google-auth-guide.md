Set up Google Authentication for Gemini access in 3 minutes:

1) https://console.cloud.google.com/flows/enableapi?apiid=aiplatform.googleapis.com → Enable project

2) https://console.cloud.google.com/iam-admin/serviceaccounts → Select project
   - Create service account → Permissions → Manage access → Role = "Vertex AI User" → Save
   - Keys → Add key → Create new key (JSON) → Download (to "Downloads" folder, used in shell commands below)

3) Move JSON permanently (shell commands or manually)
   - macOS/Linux (zsh/bash):
     ```
     mkdir -p ~/.config/tokker/keys
     latest_json=$(ls -t "$HOME/Downloads"/*.json 2>/dev/null | head -n 1)
     if [ -z "$latest_json" ]; then
       echo "No JSON found in $HOME/Downloads"; exit 1
     fi
     mv "$latest_json" "$HOME/.config/tokker/keys/tokker-google.json"
     chmod 600 "$HOME/.config/tokker/keys/tokker-google.json"
     ```
   - Windows (PowerShell):
     ```
     New-Item -ItemType Directory -Force "$Env:USERPROFILE\AppData\Local\Tokker\Keys" | Out-Null
     $latest = Get-ChildItem "$Env:USERPROFILE\Downloads" -Filter *.json | Sort-Object LastWriteTime -Descending | Select-Object -First 1
     if (-not $latest) { Write-Error "No JSON found in $Env:USERPROFILE\Downloads"; exit 1 }
     Move-Item $latest.FullName "$Env:USERPROFILE\AppData\Local\Tokker\Keys\tokker-google.json"
     ```

4) Set ADC (Application Default Credentials)
   - macOS/Linux (zsh):
   ```zsh
   echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/tokker/keys/tokker-google.json"' >> ~/.zshrc && source ~/.zshrc
   ```
   - macOS/Linux (bash):
   ```bash
   echo 'export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.config/tokker/keys/tokker-google.json"' >> ~/.bashrc && source ~/.bashrc
   ```
   - Windows (PowerShell):
   ```powershell
   setx GOOGLE_APPLICATION_CREDENTIALS "$Env:USERPROFILE\AppData\Local\Tokker\Keys\tokker-google.json"
   ```
   (then open a new terminal)

5) Enable billing in https://console.cloud.google.com/billing/

Enjoy Google Gemini family in Tokker!
```bash
tok 'hello gemini' -m gemini-2.5-flash
```
