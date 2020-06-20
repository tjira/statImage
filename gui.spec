# -*- mode: python -*-

block_cipher = None
datas = [('/usr/lib/python3/dist-packages/PIL', 'PIL'), ('/usr/lib/python3/dist-packages/numpy', 'numpy')]


a = Analysis(
	['gui.py'],
	pathex=[],
	binaries=[],
	datas=datas,
	hiddenimports=['pkg_resources.py2_warn'],
	hookspath=[],
	runtime_hooks=[],
	excludes=[],
	win_no_prefer_redirects=False,
	win_private_assemblies=False,
	cipher=block_cipher,
	noarchive=False
	)

pyz = PYZ(
	a.pure,
	a.zipped_data,
	cipher=block_cipher
	)

exe = EXE(
	pyz,
	a.scripts,
	a.binaries,
	a.zipfiles,
	a.datas,
	[],
	name='statImage',
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	runtime_tmpdir=None,
	console=True
	)
