from app.utils.mod_history import SearchHistory


def test_add_and_retrieve(tmp_path):
    h = SearchHistory(path=str(tmp_path / 'hist.json'))
    h.add('三体')
    h.add('Python')
    assert h.all() == ['Python', '三体']


def test_deduplication(tmp_path):
    h = SearchHistory(path=str(tmp_path / 'hist.json'))
    h.add('a')
    h.add('b')
    h.add('a')  # 重复，应该移到最前
    assert h.all() == ['a', 'b']


def test_max_size_limit(tmp_path):
    h = SearchHistory(path=str(tmp_path / 'hist.json'), max_size=3)
    for i in range(5):
        h.add(f'item{i}')
    assert len(h) == 3
    assert h.all() == ['item4', 'item3', 'item2']


def test_empty_keyword_ignored(tmp_path):
    h = SearchHistory(path=str(tmp_path / 'hist.json'))
    h.add('')
    h.add('   ')
    h.add(None)  # type: ignore
    assert len(h) == 0


def test_persistence(tmp_path):
    p = tmp_path / 'hist.json'
    h1 = SearchHistory(path=str(p))
    h1.add('persist')

    h2 = SearchHistory(path=str(p))
    assert h2.all() == ['persist']


def test_clear(tmp_path):
    h = SearchHistory(path=str(tmp_path / 'hist.json'))
    h.add('a')
    h.add('b')
    h.clear()
    assert h.all() == []


def test_remove(tmp_path):
    h = SearchHistory(path=str(tmp_path / 'hist.json'))
    h.add('a')
    h.add('b')
    h.remove('a')
    assert h.all() == ['b']
