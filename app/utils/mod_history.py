# _*_ coding:utf-8 _*_
# 搜索历史管理
import json
from pathlib import Path
from typing import List
from loguru import logger


class SearchHistory:
    """本地 JSON 存储的搜索历史，最多保留 N 条"""

    def __init__(self, path: str = 'config/search_history.json', max_size: int = 20):
        self.path = Path(path)
        self.max_size = max_size
        self._items: List[str] = []
        self._load()

    def _load(self):
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding='utf-8'))
            if isinstance(data, list):
                self._items = [str(x) for x in data if x]
        except Exception as e:
            logger.warning(f"搜索历史加载失败: {e}")
            self._items = []

    def _save(self):
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(self._items, ensure_ascii=False, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.warning(f"搜索历史保存失败: {e}")

    def add(self, keyword: str):
        if not keyword or not keyword.strip():
            return
        keyword = keyword.strip()
        # 去重，最新的放最前
        if keyword in self._items:
            self._items.remove(keyword)
        self._items.insert(0, keyword)
        # 限制长度
        if len(self._items) > self.max_size:
            self._items = self._items[:self.max_size]
        self._save()

    def remove(self, keyword: str):
        if keyword in self._items:
            self._items.remove(keyword)
            self._save()

    def clear(self):
        self._items = []
        self._save()

    def all(self) -> List[str]:
        return list(self._items)

    def __len__(self):
        return len(self._items)
