$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$outputDir = Join-Path $root "output"

New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$backendOut = Join-Path $outputDir "backend-smoke.out.log"
$backendErr = Join-Path $outputDir "backend-smoke.err.log"
$frontendOut = Join-Path $outputDir "frontend-smoke.out.log"
$frontendErr = Join-Path $outputDir "frontend-smoke.err.log"
$screenshot = Join-Path $outputDir "edge-lab-console-smoke.png"

$backend = Start-Process python `
  -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000" `
  -WorkingDirectory $backendDir `
  -RedirectStandardOutput $backendOut `
  -RedirectStandardError $backendErr `
  -PassThru

$frontend = Start-Process cmd.exe `
  -ArgumentList "/c", "npm run dev -- --host 127.0.0.1 --port 4178" `
  -WorkingDirectory $frontendDir `
  -RedirectStandardOutput $frontendOut `
  -RedirectStandardError $frontendErr `
  -PassThru

try {
  $backendOk = $false
  $frontendOk = $false
  for ($i = 0; $i -lt 40; $i++) {
    try {
      $backendOk = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:8000/api/health").StatusCode -eq 200
      $frontendOk = (Invoke-WebRequest -UseBasicParsing "http://127.0.0.1:4178").StatusCode -eq 200
      if ($backendOk -and $frontendOk) { break }
    } catch {
      Start-Sleep -Milliseconds 750
    }
  }

  if (-not ($backendOk -and $frontendOk)) {
    throw "Local servers did not become ready in time."
  }

  npx --yes --package @playwright/cli playwright-cli install-browser chromium | Out-Null
  npx --yes --package @playwright/cli playwright-cli open http://127.0.0.1:4178 --session edge-lab
  npx --yes --package @playwright/cli playwright-cli run-code "await page.waitForTimeout(1800)" --session edge-lab | Out-Null
  $title = npx --yes --package @playwright/cli playwright-cli eval "document.querySelector('h1')?.textContent" --session edge-lab
  $runNames = npx --yes --package @playwright/cli playwright-cli eval "Array.from(document.querySelectorAll('.run-row h3')).map((el) => el.textContent).join('|')" --session edge-lab

  if ($title -notmatch "EdgeLab Console") {
    throw "UI smoke test failed: expected EdgeLab Console heading."
  }

  if ($runNames -notmatch "Jetson Thermal Sweep") {
    throw "UI smoke test failed: expected seeded run names in the queue."
  }

  npx --yes --package @playwright/cli playwright-cli close --session edge-lab
} finally {
  if ($backend -and !$backend.HasExited) { Stop-Process -Id $backend.Id -Force }
  if ($frontend -and !$frontend.HasExited) { Stop-Process -Id $frontend.Id -Force }
}
