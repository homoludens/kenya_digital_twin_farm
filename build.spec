# build.spec

import pcse
pcse_path = os.path.dirname(pcse.__file__)



a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
		(pcse_path, 'pcse'),
	],
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
    bootloader_ignore_signsals=False,
    strip=False,
    upx=True,
    console=False,
    icon='agro.ico',  # Add 'app.ico' if you have an icon
)