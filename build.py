# _*_ coding:utf-8 _*_
"""
Olib 打包脚本
用法:
    python build.py                # 默认 onedir 模式打包
    python build.py --onefile      # 单文件模式（体积更大，启动慢）
    python build.py --no-zip       # 跳过 zip 压缩
"""
import argparse
import shutil
import sys
import zipfile
from pathlib import Path

import PyInstaller.__main__

# 未使用的 Qt 模块，可减少 30-50 MB
EXCLUDES = [
    'PyQt5.QtWebEngineCore',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtQml',
    'PyQt5.QtQuick',
    'PyQt5.QtQuickWidgets',
    'PyQt5.QtMultimedia',
    'PyQt5.QtMultimediaWidgets',
    'PyQt5.Qt3DCore',
    'PyQt5.Qt3DRender',
    'PyQt5.Qt3DInput',
    'PyQt5.Qt3DLogic',
    'PyQt5.Qt3DAnimation',
    'PyQt5.Qt3DExtras',
    'PyQt5.QtPositioning',
    'PyQt5.QtLocation',
    'PyQt5.QtBluetooth',
    'PyQt5.QtNfc',
    'PyQt5.QtSensors',
    'PyQt5.QtSerialPort',
    'PyQt5.QtSql',
    'PyQt5.QtTest',
    'PyQt5.QtDesigner',
    'PyQt5.QtHelp',
    'PyQt5.QtXmlPatterns',
    'PyQt5.QtDBus',
    'PyQt5.QtRemoteObjects',
    'PyQt5.QtWebChannel',
    'PyQt5.QtWebSockets',
    'tkinter',
    'unittest',
    'pydoc',
    'pythonwin',
    'pywin.mfc',
    'pywin.tools',
    'pywin.debugger',
    'pywin.dialogs',
    'pywin.Demos',
]

# 保留的 Qt 翻译语言（只保留中英文，可减少 3-4 MB）
KEEP_QT_LANGUAGES = {'zh_CN', 'zh_TW', 'en'}


def get_platform_config():
    """平台相关配置"""
    if sys.platform == 'win32':
        return {
            'icon': 'logo.ico',
            'artifact': 'Olib-windows',
        }
    if sys.platform == 'darwin':
        # macOS 需要 .icns，如果没有则不指定
        icns = Path('logo.icns')
        return {
            'icon': str(icns) if icns.exists() else None,
            'artifact': 'Olib-macos',
        }
    return {
        'icon': None,
        'artifact': 'Olib-linux',
    }


def prune_build_artifacts():
    """精简 onedir 构建产物中的冗余文件"""
    dist_internal = Path('dist') / 'Olib' / '_internal'
    if not dist_internal.exists():
        # 不同 PyInstaller 版本路径不同
        dist_internal = Path('dist') / 'Olib'
        if not dist_internal.exists():
            return

    freed = 0

    # 1. 精简 Qt 翻译文件
    translations_dir = dist_internal / 'PyQt5' / 'Qt5' / 'translations'
    if not translations_dir.exists():
        translations_dir = dist_internal / 'translations'
    if translations_dir.exists():
        for qm in translations_dir.glob('*.qm'):
            # 保留文件名包含的语言前缀
            keep = any(lang in qm.stem for lang in KEEP_QT_LANGUAGES)
            if not keep:
                freed += qm.stat().st_size
                qm.unlink()
        print(f'[Prune] Removed unused Qt translations, freed {freed / 1024 / 1024:.1f} MB')

    # 2. 删除 pywin32 的 Pythonwin（GUI 开发工具，运行时不需要）
    pythonwin = dist_internal / 'Pythonwin'
    if pythonwin.exists():
        size = sum(f.stat().st_size for f in pythonwin.rglob('*') if f.is_file())
        shutil.rmtree(pythonwin, ignore_errors=True)
        freed += size
        print(f'[Prune] Removed Pythonwin ({size / 1024 / 1024:.1f} MB)')

    # 3. 删除 win32 调试符号和文档
    for pattern in ['**/*.pdb', '**/*.exp', '**/*.lib']:
        for f in dist_internal.glob(pattern):
            if f.is_file():
                freed += f.stat().st_size
                f.unlink()

    print(f'[Prune] Total freed: {freed / 1024 / 1024:.1f} MB')


def build(onefile: bool = False, make_zip: bool = True):
    # 清理之前的构建
    for d in ('build', 'dist'):
        if Path(d).exists():
            shutil.rmtree(d)

    cfg = get_platform_config()

    args = [
        'app.py',
        '--name=Olib',
        '--windowed',
        '--clean',
        '--noconfirm',
    ]

    if cfg['icon']:
        args.append(f'--icon={cfg["icon"]}')

    if onefile:
        args.append('--onefile')
    else:
        args.append('--onedir')

    for mod in EXCLUDES:
        args.extend(['--exclude-module', mod])

    print(f'Running PyInstaller with {len(args)} args...')
    PyInstaller.__main__.run(args)

    # 后置精简（仅 onedir 模式，onefile 模式已经打包成单文件无法修改）
    if not onefile:
        prune_build_artifacts()

    # 统计产物体积
    dist = Path('dist')
    if onefile:
        # Windows 是 .exe，其他平台无扩展名
        candidates = list(dist.glob('Olib*'))
        if candidates:
            size_mb = candidates[0].stat().st_size / 1024 / 1024
            print(f'\n[Result] {candidates[0]} = {size_mb:.1f} MB')
        return

    # onedir 模式
    app_dir = dist / 'Olib'
    if sys.platform == 'darwin':
        # macOS 生成 .app
        app_dir = dist / 'Olib.app'
        if not app_dir.exists():
            app_dir = dist / 'Olib'

    if not app_dir.exists():
        print(f'[Error] Build output not found at {app_dir}')
        return

    total = sum(f.stat().st_size for f in app_dir.rglob('*') if f.is_file())
    print(f'\n[Result] {app_dir} = {total / 1024 / 1024:.1f} MB')

    if make_zip:
        out_zip = dist / f'{cfg["artifact"]}.zip'
        print(f'Compressing to {out_zip}...')
        with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
            for f in app_dir.rglob('*'):
                if f.is_file():
                    z.write(f, f.relative_to(dist))
        zip_size = out_zip.stat().st_size / 1024 / 1024
        print(f'[Zip] {out_zip} = {zip_size:.1f} MB')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--onefile', action='store_true', help='打包为单文件可执行程序')
    parser.add_argument('--no-zip', action='store_true', help='跳过 zip 压缩')
    args = parser.parse_args()

    build(onefile=args.onefile, make_zip=not args.no_zip)
