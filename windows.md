# Packaging Kenya Farm Twin as Windows .exe

## Quick Method

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Create the .exe

```bash
pyinstaller --onefile --windowed --name "KenyaFarmTwin" main.py
```

Options:
- `--onefile` = single .exe file
- `--windowed` = no console window
- `--name` = name of the executable

### 3. Find your .exe

```
dist/KenyaFarmTwin.exe
```

---

## Advanced Method (Recommended)

For a cleaner build with better control, create a spec file:

### 1. Create `build.spec`:

```python
# build.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['pcse', 'pcse.models', 'pcse.input', 'pcse.base', 'pcse.util'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KenyaFarmTwin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,  # Add 'app.ico' if you have an icon
)
```

### 2. Build with spec file:

```bash
pyinstaller build.spec
```

---

## Including PCSE Data Files

If the app can't find crop/soil parameters, add PCSE data to the spec:

```python
datas=[
    ('venv/lib/python3.13/site-packages/pcse/data', 'pcse/data'),
],
```

Or for your specific Python path:

```python
import pcse
pcse_path = os.path.dirname(pcse.__file__)

datas=[
    (os.path.join(pcse_path, 'data'), 'pcse/data'),
],
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Missing modules | Add to `hiddenimports` list |
| Large file size (50-150MB) | Normal for PyQt5 apps |
| "Failed to execute script" | Run without `--windowed` to see errors |
| PCSE data not found | Include data folder in `datas` |
| Missing DLLs | Install Visual C++ Redistributable |

---

## Demo Version (No PCSE)

For the demo version without PCSE dependency:

```bash
pyinstaller --onefile --windowed --name "KenyaFarmTwin_Demo" demo.py
```

This creates a smaller .exe since it doesn't need PCSE.

---

## Adding an Icon

1. Create or download a .ico file
2. Add to PyInstaller command:

```bash
pyinstaller --onefile --windowed --icon=app.ico --name "KenyaFarmTwin" main.py
```

Or in spec file:

```python
icon='app.ico',
```
