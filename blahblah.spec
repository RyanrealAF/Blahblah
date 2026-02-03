# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        # Bundle libsndfile for Windows
        ('C:\\Windows\\System32\\libsndfile-1.dll', '.'),
        # Bundle fluidsynth
        ('C:\\Program Files\\FluidSynth\\bin\\fluidsynth.exe', '.'),
        ('C:\\Program Files\\FluidSynth\\share\\soundfonts\\FluidR3_GM.sf2', 'soundfonts/'),
    ],
    datas=[
        # Include all pipeline modules
        ('pipeline/', 'pipeline/'),
        # Include web templates and static files
        ('web/templates/', 'web/templates/'),
        ('web/static/', 'web/static/'),
        # Include requirements.txt for reference
        ('requirements.txt', '.'),
        # Include model config
        ('model/config.json', 'model/'),
    ],
    hiddenimports=[
        'librosa',
        'librosa.core',
        'librosa.feature',
        'librosa.effects',
        'librosa.util',
        'numpy',
        'numpy.random',
        'scipy',
        'scipy.io',
        'scipy.signal',
        'mido',
        'mido.backends',
        'pretty_midi',
        'soundfile',
        'torch',
        'torch.nn',
        'torch.optim',
        'pandas',
        'flask',
        'flask.json',
        'flask_cors',
        'uvicorn',
        'uvicorn.config',
        'uvicorn.server',
        'mir_eval',
        'mir_eval.util',
        'mir_eval.separation',
        'mir_eval.transcription',
        'tqdm',
        'tqdm.std',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='blahblah',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico'
)