import os

def search_text(path, text):
    matches = []
    for root, dirs, files in os.walk(path):
        for f in files:
            if f.endswith(('.grd', '.grdp', '.cc', '.h', '.rc')):
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                        lines = fh.readlines()
                        for i, line in enumerate(lines):
                            if text in line:
                                matches.append(f"{fp}:{i+1}: {line.strip()[:100]}")
                except:
                    pass
    return matches

print("--- Searching 'Customize Chromium' ---")
for m in search_text('D:/Velox/src/chrome/app', 'Customize')[:10]:
    print(m)

print("--- Searching 'google_api_keys_info' ---")
for m in search_text('D:/Velox/src/chrome/browser/ui', 'GoogleApiKeys')[:10]:
    print(m)

print("--- Searching icons in chrome/app/theme/chromium ---")
theme_dir = 'D:/Velox/src/chrome/app/theme/chromium'
if os.path.exists(theme_dir):
    for root, dirs, files in os.walk(theme_dir):
        for f in files:
            if f.endswith('.ico'):
                print(os.path.join(root, f))
