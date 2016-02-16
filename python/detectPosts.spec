# -*- mode: python -*-
a = Analysis(['detectPosts.py'],
             pathex=['.\\'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='detectPosts.exe',
          debug=False,
          strip=None,
          upx=True,
          icon='bird.ico',
          console=True )
