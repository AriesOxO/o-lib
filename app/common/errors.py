# _*_ coding:utf-8 _*_
# 错误码定义，替代散落在代码中的魔法数字
from enum import IntEnum


class SearchError(IntEnum):
    """搜索业务错误码"""
    EMPTY_RESULT = 0      # 搜索成功但结果为空
    UNKNOWN = -1          # 未知异常
    BLOCKED_KEYWORD = -999  # 搜索词违禁
    RATE_LIMIT = 999      # 速率限制
    PARSE_ERROR = -2      # 响应解析失败
    NETWORK_ERROR = -3    # 网络请求失败
    CONFIG_MISSING = -4   # 服务器地址未配置

    @property
    def user_message(self) -> tuple[str, str]:
        """用户友好的标题和内容"""
        return {
            SearchError.EMPTY_RESULT: ("结果为空", "本次搜索结果为空，请更改搜索条件。"),
            SearchError.UNKNOWN: ("未知异常", "出现未知问题，请稍后重试。"),
            SearchError.BLOCKED_KEYWORD: ("搜索词异常", "请修改搜索词！"),
            SearchError.RATE_LIMIT: ("速率限制", "服务器压力巨大，当前搜索限制为 15 次/分钟，请稍后再试。"),
            SearchError.PARSE_ERROR: ("响应格式异常", "服务端返回数据无法解析，请稍后重试。"),
            SearchError.NETWORK_ERROR: ("网络错误", "无法连接服务器，请检查网络。"),
            SearchError.CONFIG_MISSING: ("服务器未配置", "请通过环境变量 OLIB_PROD_HOST 配置服务器地址。"),
        }[self]


class DownloadError(IntEnum):
    """下载业务错误码"""
    SUCCESS = 0
    RATE_LIMIT = 999
    NETWORK_ERROR = -1
    CANCELLED = -2
    CONFIG_MISSING = -3
