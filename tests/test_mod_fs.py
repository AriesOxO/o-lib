import sys
from pathlib import Path
from app.utils.mod_fs import open_in_file_manager, default_download_dir


def test_open_nonexistent_returns_false(tmp_path):
    missing = tmp_path / 'does_not_exist'
    assert open_in_file_manager(missing) is False


def test_default_download_dir_returns_path():
    result = default_download_dir()
    assert isinstance(result, Path)
    # 应该在用户目录下
    assert Path.home() in result.parents or Path.home() == result.parent


def test_open_existing_calls_platform_cmd(tmp_path, monkeypatch):
    called = []

    def fake_popen(args, **kwargs):
        called.append(args)
        class P: pass
        return P()

    def fake_startfile(path):
        called.append(['startfile', path])

    monkeypatch.setattr('subprocess.Popen', fake_popen)
    if sys.platform == 'win32':
        import os as _os
        monkeypatch.setattr(_os, 'startfile', fake_startfile, raising=False)

    result = open_in_file_manager(tmp_path)
    assert result is True
    assert len(called) == 1
