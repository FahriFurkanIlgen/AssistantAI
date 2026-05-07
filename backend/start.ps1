# Backend başlatma scripti
# Kullanım: .\start.ps1

$envFile = Join-Path $PSScriptRoot ".env"

# .env dosyasını oku ve ortam değişkenlerine yükle
Get-Content $envFile | ForEach-Object {
    if ($_ -match "^\s*([^#][^=]+?)\s*=\s*(.*)\s*$") {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim().Trim('"')
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

Write-Host "✅ .env yüklendi" -ForegroundColor Green
Write-Host "🚀 Backend başlatılıyor: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📖 Swagger: http://localhost:8000/docs" -ForegroundColor Cyan

& "$PSScriptRoot\venv\Scripts\uvicorn.exe" app.main:app `
    --app-dir "$PSScriptRoot" `
    --reload `
    --host 0.0.0.0 `
    --port 8000
