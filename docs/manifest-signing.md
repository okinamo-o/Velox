# Release manifest signing

Velox update manifests use RSA-2048 with SHA-256. The browser contains only the
DER public key in `get_installed_version_win.cc`; the private key is held by the
release operator in the Windows `CurrentUser\My` certificate store.

The current local signing certificate thumbprint is
`B06B7709750333CCCC0A36A1B9542DAF37C48DC3`. Set it for a release session:

```powershell
$env:VELOX_MANIFEST_SIGNING_CERT_THUMBPRINT = "B06B7709750333CCCC0A36A1B9542DAF37C48DC3"
```

`dist/package_release.ps1` signs `version|installer.download_url|installer.sha256`
with that certificate and writes the same signed manifest to `dist/version.json`
and `dist/website/version.json`. Keep the non-exportable private key protected
in the release operator's certificate store. Do not export it into the
repository or place it in a build artifact. If it is lost, rotate the pinned
public key in a browser release before signing manifests with a replacement key.

Rotating this key requires updating the pinned DER public key in the browser,
building and distributing that browser version, then signing manifests with the
new private key. Do not publish a manifest signed by a key that the released
browser does not pin.

Release packaging also requires all six binaries to pass trusted Authenticode
verification for publisher `VELOX`. Self-signed test certificates are rejected
by the release check and by the native updater.
