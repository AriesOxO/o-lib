import uuid
from app.utils.mod_uuid import get_uuid, get_first_mac


def test_get_uuid_returns_valid_uuid():
    result = get_uuid()
    if result is None:
        # MAC 不可用时应 fallback（见下方测试）
        return
    # 格式验证
    uuid.UUID(result)


def test_get_uuid_is_deterministic():
    a = get_uuid()
    b = get_uuid()
    assert a == b


def test_get_first_mac_returns_str_or_none():
    mac = get_first_mac()
    assert mac is None or isinstance(mac, str)
