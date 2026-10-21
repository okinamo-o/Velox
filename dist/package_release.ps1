<#
.SYNOPSIS
    Packages Velox Browser for global distribution (Installer, Portable Zip, Hashes, Update Manifest).
.DESCRIPTION
    Run this script whenever you are ready to ship a new version of Velox.
#>

param(
    [string]$Version = "134.0.6998.180",
    [string]$SrcDir = "D:\Velox\src",
    [string]$DistDir = "D:\Velox\dist",
    [switch]$Rebuild
)

$ErrorActionPreference = "Stop"

Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "       VELOX BROWSER RELEASE PACKAGER        " -ForegroundColor Cyan
Write-Host "==============================================" -ForegroundColor Cyan
Write-Host "Target Version : $Version" -ForegroundColor Yellow
Write-Host "Source Dir     : $SrcDir" -ForegroundColor Yellow
Write-Host "Dist Dir       : $DistDir" -ForegroundColor Yellow

if (!(Test-Path $DistDir)) {
    New-Item -ItemType Directory -Force -Path $DistDir | Out-Null
}

# 1. Build mini_installer if requested or missing
$InstallerSrc = Join-Path $SrcDir "out\Default\mini_installer.exe"
if ($Rebuild -or !(Test-Path $InstallerSrc)) {
    Write-Host "`n[*] Building mini_installer.exe with autoninja..." -ForegroundColor Green
    Push-Location $SrcDir
    try {
        & autoninja -C out/Default mini_installer
        if ($LASTEXITCODE -ne 0) {
            throw "Build failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
}

# 2. Stage VeloxSetup.exe
$SetupTarget = Join-Path $DistDir "VeloxSetup.exe"
Write-Host "`n[*] Staging VeloxSetup.exe..." -ForegroundColor Green
Copy-Item $InstallerSrc $SetupTarget -Force

$SetupHash = (Get-FileHash -Algorithm SHA256 $SetupTarget).Hash
$SetupSize = (Get-Item $SetupTarget).Length
$SetupSizeMB = [math]::Round($SetupSize / 1MB, 2)
Write-Host "    Size : $SetupSizeMB MB ($SetupSize bytes)" -ForegroundColor Gray
Write-Host "    SHA256 : $SetupHash" -ForegroundColor Gray

# 3. Create Portable Zip
$AppDir = "C:\Users\Louay\AppData\Local\Velox\Application"
$PortableZip = Join-Path $DistDir "Velox-v$Version-Portable-x64.zip"

if (Test-Path $AppDir) {
    Write-Host "`n[*] Creating Portable ZIP distribution..." -ForegroundColor Green
    if (Test-Path $PortableZip) {
        Remove-Item $PortableZip -Force
    }
    
    # Exclude logs or crash dumps
    $TempPortable = Join-Path $env:TEMP "Velox-Portable-Staging"
    if (Test-Path $TempPortable) { Remove-Item $TempPortable -Recurse -Force }
    New-Item -ItemType Directory -Path $TempPortable | Out-Null
    
    Copy-Item "$AppDir\*" -Destination $TempPortable -Recurse -Exclude "*.log","*.dmp","*.old" -Force
    if (Test-Path "$TempPortable\134.0.6998.178") {
        Remove-Item "$TempPortable\134.0.6998.178" -Recurse -Force
    }
    Compress-Archive -Path "$TempPortable\*" -DestinationPath $PortableZip -CompressionLevel Optimal
    Remove-Item $TempPortable -Recurse -Force
    
    $ZipHash = (Get-FileHash -Algorithm SHA256 $PortableZip).Hash
    $ZipSizeMB = [math]::Round((Get-Item $PortableZip).Length / 1MB, 2)
    Write-Host "    Size : $ZipSizeMB MB" -ForegroundColor Gray
    Write-Host "    SHA256 : $ZipHash" -ForegroundColor Gray
}

# 4. Generate Auto-Update Manifest (version.json)
$VersionManifest = Join-Path $DistDir "version.json"
Write-Host "`n[*] Generating Update Manifest (version.json)..." -ForegroundColor Green
$ManifestData = [ordered]@{
    product       = "Velox Browser"
    version       = $Version
    channel       = "stable"
    release_date  = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssZ")
    installer     = [ordered]@{
        filename    = "VeloxSetup.exe"
        sha256      = $SetupHash
        size_bytes  = $SetupSize
        download_url= "https://github.com/okinamo-o/Velox/releases/download/v$Version/VeloxSetup.exe"
    }
    portable      = [ordered]@{
        filename    = "Velox-v$Version-Portable-x64.zip"
        sha256      = if ($ZipHash) { $ZipHash } else { "" }
        download_url= "https://github.com/okinamo-o/Velox/releases/download/v$Version/Velox-v$Version-Portable-x64.zip"
    }
    notes         = @(
        "⚡ Velox Shield intelligent tracker & ad blocking built-in",
        "🏝️ Opera One-style Tab Islands with automatic grouping & glowing headers",
        "🚀 Ultra hardware-accelerated Blink rendering engine",
        "🎨 Modern futuristic glow UI with clean non-client frame",
        "🔔 Intelligent dynamic update notifications with one-click restore"
    )
}

$ManifestData | ConvertTo-Json -Depth 5 | Set-Content -Path $VersionManifest -Encoding UTF8
Write-Host "    Manifest written to: $VersionManifest" -ForegroundColor Gray

# 5. Output Release Checklist
Write-Host "`n==============================================" -ForegroundColor Green
Write-Host "         RELEASE PACKAGING COMPLETE!         " -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host "Release Artifacts created in ${DistDir}:" -ForegroundColor Yellow
Write-Host "1. VeloxSetup.exe              (Standalone Installer)" -ForegroundColor White
if (Test-Path $PortableZip) {
    Write-Host "2. Velox-v$Version-Portable-x64.zip (Portable Edition)" -ForegroundColor White
}
Write-Host "3. version.json                (Auto-Update Manifest)" -ForegroundColor White

Write-Host "`nNext Steps to Deploy to Users:" -ForegroundColor Cyan
Write-Host "1. Create a GitHub Release tag 'v$Version' on your repository."
Write-Host "2. Upload 'VeloxSetup.exe' and 'Velox-v$Version-Portable-x64.zip' to the GitHub Release."
Write-Host "3. Deploy the website in 'D:\Velox\dist\website' to Cloudflare Pages or Vercel."
Write-Host "4. Host 'version.json' at your update URL to power the 'Update Velox' button!" -ForegroundColor Green
