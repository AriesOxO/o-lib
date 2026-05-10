from app.utils.mod_favorites import Favorites


def _book(bid, title='Test Book'):
    return {
        'id': bid,
        'hash': 'h' + str(bid),
        'title': title,
        'author': 'author',
        'year': '2024',
        'extension': 'pdf',
        'filesize': 1024,
        'filesizeString': '1 KB',
        'readOnlineUrl': 'https://example.com',
    }


def test_add_and_retrieve(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    assert fav.add(_book('1')) is True
    assert len(fav) == 1
    assert fav.contains('1')


def test_add_duplicate_returns_false(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    fav.add(_book('1'))
    assert fav.add(_book('1')) is False
    assert len(fav) == 1


def test_remove(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    fav.add(_book('1'))
    fav.add(_book('2'))
    assert fav.remove('1') is True
    assert not fav.contains('1')
    assert fav.contains('2')


def test_remove_nonexistent(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    assert fav.remove('nonexistent') is False


def test_persistence(tmp_path):
    p = tmp_path / 'fav.json'
    f1 = Favorites(path=str(p))
    f1.add(_book('1', 'Persisted'))

    f2 = Favorites(path=str(p))
    book = f2.get('1')
    assert book is not None
    assert book['title'] == 'Persisted'


def test_clear(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    fav.add(_book('1'))
    fav.add(_book('2'))
    fav.clear()
    assert len(fav) == 0


def test_book_without_id_rejected(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    assert fav.add({'title': 'no id'}) is False
    assert len(fav) == 0


def test_all_returns_copy(tmp_path):
    fav = Favorites(path=str(tmp_path / 'fav.json'))
    fav.add(_book('1'))
    items = fav.all()
    items.append({'fake': True})
    # 外部修改不影响内部
    assert len(fav) == 1
