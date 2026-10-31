param(
    [Parameter(Mandatory = $true)]
    [string]$ManifestPath,
    [string]$CertificateThumbprint = $env:VELOX_MANIFEST_SIGNING_CERT_THUMBPRINT
)

$ErrorActionPreference = "Stop"

if ([string]::IsNullOrWhiteSpace($CertificateThumbprint)) {
    throw "Set VELOX_MANIFEST_SIGNING_CERT_THUMBPRINT to a release signing certificate in CurrentUser\My."
}

$normalizedThumbprint = ($CertificateThumbprint -replace '\s', '').ToUpperInvariant()
$certificates = @(Get-ChildItem Cert:\CurrentUser\My | Where-Object {
    $_.Thumbprint -eq $normalizedThumbprint
})
if ($certificates.Count -ne 1 -or !$certificates[0].HasPrivateKey) {
    throw "The requested manifest signing certificate was not found or has no private key."
}

$certificate = $certificates[0]
$rsa = [System.Security.Cryptography.X509Certificates.RSACertificateExtensions]::GetRSAPrivateKey($certificate)
if (!$rsa) {
    throw "The manifest signing certificate does not contain an RSA private key."
}

$manifestPathResolved = (Resolve-Path -LiteralPath $ManifestPath).Path
$manifestJson = [System.IO.File]::ReadAllText($manifestPathResolved, [System.Text.Encoding]::UTF8)
$manifest = $manifestJson | ConvertFrom-Json
if (!$manifest.version -or !$manifest.installer.download_url -or !$manifest.installer.sha256) {
    throw "Manifest must contain version, installer.download_url, and installer.sha256."
}

$payload = "{0}|{1}|{2}" -f $manifest.version, $manifest.installer.download_url, $manifest.installer.sha256
$payloadBytes = [System.Text.Encoding]::UTF8.GetBytes($payload)
$signatureBytes = $rsa.SignData(
    $payloadBytes,
    [System.Security.Cryptography.HashAlgorithmName]::SHA256,
    [System.Security.Cryptography.RSASignaturePadding]::Pkcs1
)
$signatureJson = ConvertTo-Json -InputObject ([Convert]::ToBase64String($signatureBytes)) -Compress
$signaturePattern = '("signature"\s*:\s*)"(?:[^"\\]|\\.)*"'
if (![regex]::IsMatch($manifestJson, $signaturePattern)) {
    throw "Manifest must include an installer.signature field to replace."
}
$signedJson = [regex]::Replace(
    $manifestJson,
    $signaturePattern,
    ('$1' + $signatureJson),
    [System.Text.RegularExpressions.RegexOptions]::None
) -replace "`r`n", "`n"
[System.IO.File]::WriteAllText($manifestPathResolved, $signedJson, [System.Text.UTF8Encoding]::new($false))
