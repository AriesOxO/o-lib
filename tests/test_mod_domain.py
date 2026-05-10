import importlib
import app.utils.mod_domain as mod_domain


def test_prod_host_from_env(monkeypatch):
    monkeypatch.setenv('OLIB_PROD_HOST', 'example.com')
    monkeypatch.setenv('APP_ENV', 'prod')
    import app.common.config
    importlib.reload(app.common.config)
    importlib.reload(mod_domain)
    assert mod_domain.get_domain() == 'https://example.com'


def test_dev_host_default(monkeypatch):
    monkeypatch.delenv('OLIB_DEV_HOST', raising=False)
    monkeypatch.setenv('APP_ENV', 'dev')
    import app.common.config
    importlib.reload(app.common.config)
    importlib.reload(mod_domain)
    assert mod_domain.get_domain() == 'http://127.0.0.1:8000'


def test_missing_host_returns_empty(monkeypatch):
    monkeypatch.setenv('OLIB_PROD_HOST', '')
    monkeypatch.setenv('APP_ENV', 'prod')
    import app.common.config
    importlib.reload(app.common.config)
    importlib.reload(mod_domain)
    assert mod_domain.get_domain() == ''
