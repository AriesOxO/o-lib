# _*_ coding:utf-8 _*_
# 本地收藏夹管理
import json
from pathlib import Path
from typing import List, Optional
from loguru import logger


class Favorites:
    """本地 JSON 存储用户收藏的书籍"""

    def __init__(self, path: str = 'config/favorites.json'):
        self.path = Path(path)
        self._items: List[dict] = []
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(data, list):
                self._items = [x for x in data if isinstance(x, dict) and x.get('id')]
        except Exception as e:
            logger.warning(f"收藏夹加载失败: {e}")
            self._items = []

    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._items, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.warning(f"收藏夹保存失败: {e}")

    @staticmethod
    def _book_to_record(book: dict) -> dict:
        """从搜索结果书籍 dict 提取关键字段存储"""
        return {
            'id': book.get('id'),
            'hash': book.get('hash'),
            'title': book.get('title'),
            'author': book.get('author'),
            'year': book.get('year'),
            'extension': book.get('extension'),
            'filesize': book.get('filesize'),
            'filesizeString': book.get('filesizeString'),
            'readOnlineUrl': book.get('readOnlineUrl'),
        }

    def add(self, book: dict) -> bool:
        """添加书籍到收藏夹，已存在返回 False"""
        record = self._book_to_record(book)
        if not record['id']:
            return False
        if self.contains(record['id']):
            return False
        self._items.insert(0, record)
        self._save()
        return True

    def remove(self, book_id) -> bool:
        """按 id 从收藏夹移除"""
        before = len(self._items)
        self._items = [b for b in self._items if b.get('id') != book_id]
        if len(self._items) != before:
            self._save()
            return True
        return False

    def contains(self, book_id) -> bool:
        return any(b.get('id') == book_id for b in self._items)

    def get(self, book_id) -> Optional[dict]:
        for b in self._items:
            if b.get('id') == book_id:
                return b
        return None

    def all(self) -> List[dict]:
        return list(self._items)

    def clear(self):
        self._items = []
        self._save()

    def __len__(self):
        return len(self._items)
