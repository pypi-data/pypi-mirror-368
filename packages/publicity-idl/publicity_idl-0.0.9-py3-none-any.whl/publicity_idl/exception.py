from datetime import datetime
from .enum import SourceEnum

class GoodException(Exception):
    """
    :param code: 错误码（整数或字符串）
    :param ext: 扩展字段（字典类型，用于携带额外信息）
    """

    def __init__(self, code: int, name: str, ext: dict | None = None):
        self.code = code        # 错误码
        self.name = name        # 异常名称
        self.message = ""       # 错误信息
        self.ext = ext or {}    # 扩展字段，默认为空字典
        super().__init__(name)  # 调用父类构造器，确保异常信息可被捕获

    def with_msg(self, msg: str):
        self.message = msg
        return self

    def with_field(self, key: str, value: any):
        self.ext[key] = value
        return self

    def with_source(self, source: SourceEnum):
        return self.with_field(key="source", value=source.value)

    def with_batch_id(self, batch_id: int):
        return self.with_field(key="batch_id", value=batch_id)

    def with_keyword_id(self, keyword_id: int):
        return self.with_field(key="keyword_id", value=keyword_id)

    def with_event_id(self, event_id: int):
        return self.with_field(key="event_id", value=event_id)

    def with_config_id(self, config_id: int):
        return self.with_field(key="config_id", value=config_id)

    def with_user_id(self, user_id: int):
        return self.with_field(key="user_id", value=user_id)

    def with_status(self, status: int):
        return self.with_field(key="status", value=status)

    def with_third_id(self, third_id: str):
        return self.with_field(key="third_id", value=third_id)

    def with_url(self, url: str):
        return self.with_field(key="url", value=url)

    def with_publish_time(self, publish_time: datetime):
        return self.with_field(key="publish_time", value=publish_time)

    def __str__(self) -> str:
        return f"GoodException(code={self.code}, name={self.name}, message={self.message!r}, ext={self.ext!r})"


# 命名规范: 前五位-端口或业务ID  后四位-错误码
MySQLException_UNKNOWN = GoodException(33060000, "未知错误")
MySQLException_SELECT = GoodException(33060001, "查询数据失败")
MySQLException_INSERT = GoodException(33060002, "插入数据失败")
MySQLException_UPDATE = GoodException(33060003, "更新数据失败")
MySQLException_DELETE = GoodException(33060004, "删除数据失败")
