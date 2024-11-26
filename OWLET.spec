# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

datas = [('icons/owlet_a1.png', 'icons')]
datas += collect_data_files('llvmlite')
datas += collect_data_files('libsndfile')
datas += collect_data_files('resampy')
datas += collect_data_files('_soundfile_data')
datas += [('ffmpeg/*', 'ffmpeg')]
datas += [('eyetracker/shape_predictor_68_face_landmarks.dat', 'eyetracker')]
datas += [('_soundfile_data/libsndfile.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libsndfile_x86_64.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libFLAC.8.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbis.0.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbis.0.4.9.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbis.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbisenc.2.0.12.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbisenc.2.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbisenc.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbisenc.3.3.8.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbisenc.3.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libvorbisenc.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libopus.0.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libogg.0.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libogg.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libmp3lame.dylib', '_soundfile_data')]
datas += [('_soundfile_data/libmp3lame.0.dylib', '_soundfile_data')]

block_cipher = None


a = Analysis(['OWLET.py'],
	     pathex=['eyetracker'],
             binaries=[],
             datas=datas,
             hiddenimports=["sklearn.utils._cython_blas" , "sklearn.neighbors.typedefs" , "sklearn.neighbors.quad_tree", "sklearn.tree._utils", "sklearn.neighbors._typedefs", "sklearn.utils._typedefs", "sklearn.neighbors._partition_nodes", "sklearn.utils._typedefs", "sklearn.utils._weight_vector"],
             hookspath=['./pyinstaller-hooks'],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='OWLET',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='owlet_icon.png')
app = BUNDLE(exe,
             name='OWLET.app',
             icon='owlet_icon.png',
             bundle_identifier=None)
