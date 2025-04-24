# Build Desktop App

```
$ uv run streamlit-desktop-app build app.py \
  --name Gs2Canvas \
  --pyinstaller-options \
  --windowed \
  --codesign-identity E1A9E339B01C843A312D9B0918922D10A04A0D3F \
  --osx-entitlements-file entitlements.plist \
  --icon icon.png
```
