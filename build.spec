# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main_modular.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('stratagems.json', '.'),
        # 不需要手动添加 modules 和 gui，PyInstaller 会自动处理 Python 模块
    ],
    hiddenimports=[
        'customtkinter',
        'pynput',
        'pypinyin',
        'alibabacloud_nls',
        'websocket',
        'modules.aliyun_asr',
        'modules.vosk_asr',
        'modules.audio_processor',
        'modules.config_manager',
        'modules.key_executor',
        'modules.log_manager',
        'modules.stratagem_engine',
        'modules.stratagem_manager',
        'modules.stratagem_matcher',
        'gui.gui_main_tab',
        'gui.gui_settings_tab',
        'gui.gui_test_tab',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
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
    name='Helldiver Voice Assistant',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # 图标文件路径
)
