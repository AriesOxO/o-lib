import os
from app.utils.mod_env import get_env


def test_default_env_is_prod(monkeypatch, tmp_path):
    monkeypatch.delenv('APP_ENV', raising=False)
    monkeypatch.chdir(tmp_path)  # 无 .env 文件
    assert get_env() == 'prod'


def test_env_is_lowercased(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'DEV')
    assert get_env() == 'dev'


def test_env_respects_custom(monkeypatch):
    monkeypatch.setenv('APP_ENV', 'test')
    assert get_env() == 'test'
