import json
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from sqlalchemy import Column, BigInteger, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.sql import func
from sqlalchemy_serializer import SerializerMixin

do_base = declarative_base()

class Keyword(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 支持从 ORM 模型转换

    id: Optional[int] = None
    keyword: Optional[str] = Field(default=None, max_length=255)
    heat: Optional[float] = Field(default=0)
    create_time: Optional[datetime] = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(default_factory=datetime.now)

    @classmethod
    def from_orm(cls, orm_obj: "KeywordDO") -> "Keyword":
        return cls.model_validate(orm_obj.to_dict())

    def to_orm(self) -> "KeywordDO":
        return KeywordDO(
            id=self.id,
            keyword=self.keyword,
            heat=self.heat,
            create_time=self.create_time,
            update_time=self.update_time,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Keyword":
        """从字典创建Keyword对象"""
        return cls.model_validate(data)

    def __str__(self) -> str:
        return self.model_dump_json()

class KeywordDO(do_base, SerializerMixin):
    __tablename__ = 'keyword'
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    keyword = Column(String(255), nullable=False)
    heat = Column(Float, default=0)
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), comment='更新时间')

    def __str__(self):
        return f"<{self.__tablename__} {self.to_dict()}>"


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 支持 ORM 转换

    id: Optional[int] = None
    keyword_id: Optional[int] = Field(None, comment='关键词id')
    name: Optional[str] = Field(None, max_length=255, comment='事件名')
    heat: Optional[float] = Field(0, comment='热度')
    sentiment: Optional[float] = Field(None, comment='情感值')
    create_time: Optional[datetime] = Field(default_factory=datetime.now, comment='创建时间')
    update_time: Optional[datetime] = Field(default_factory=datetime.now, comment='更新时间')

    record_cnt: Optional[int] = Field(default=0, exclude=True)
    @classmethod
    def from_orm(cls, orm_obj: "EventDO") -> "Event":
        """从数据库模型转换（直接使用Pydantic内置解析）"""
        return cls.model_validate(orm_obj.to_dict())

    def to_orm(self) -> "EventDO":
        """转换为数据库模型"""
        return EventDO(
            id=self.id,
            keyword_id=self.keyword_id,
            name=self.name,
            heat=self.heat,
            sentiment=self.sentiment,
            create_time=self.create_time,
            update_time=self.update_time
        )

    def __str__(self) -> str:
        return self.model_dump_json()

class EventDO(do_base, SerializerMixin):
    __tablename__ = 'event'
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    keyword_id = Column(BigInteger, nullable=False, comment='关键词id')
    name = Column(String(255), nullable=False, unique=True, comment='事件名')
    heat = Column(Float, default=0, comment='热度')
    sentiment = Column(Float, comment='情感值')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), comment='更新时间')

    def __str__(self):
        return f"<{self.__tablename__} {self.to_dict()}>"

class Record(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 支持从 ORM 模型转换

    id: Optional[int] = None
    keyword_id: Optional[int] = None
    event_id: Optional[int] = None
    third_id: Optional[str] = Field(default=None, max_length=64)
    source: Optional[str] = Field(default=None, max_length=32)
    author: Optional[str] = Field(default=None, max_length=128)
    title: Optional[str] = Field(default=None, max_length=128)
    content: Optional[str] = Field(default=None, max_length=1024)
    heat: Optional[float] = Field(default=0)
    sentiment: Optional[float] = None
    publish_datetime: Optional[datetime] = None
    url: Optional[str] = Field(default=None, max_length=512)
    ext: Optional[dict] = None
    create_time: Optional[datetime] = Field(default_factory=datetime.now)
    update_time: Optional[datetime] = Field(default_factory=datetime.now)

    event_pos: Optional[int] = Field(default=None, exclude=True)

    @classmethod
    def from_orm(cls, orm_obj: "RecordDO") -> "Record":
        return cls.model_validate(orm_obj.to_dict())

    def to_orm(self) -> "RecordDO":
        return RecordDO(
            id=self.id,
            keyword_id=self.keyword_id,
            event_id=self.event_id,
            third_id=self.third_id,
            source=self.source,
            author=self.author,
            title=self.title,
            content=self.content,
            heat=self.heat,
            sentiment=self.sentiment,
            publish_datetime=self.publish_datetime,
            url=self.url,
            ext=json.dumps(self.ext),
            create_time=self.create_time,
            update_time=self.update_time,
        )

    @classmethod
    def from_dict(cls, data: dict) -> "Record":
        """从字典创建Record对象"""
        return cls.model_validate(data)

    def __str__(self) -> str:
        return self.model_dump_json()

class RecordDO(do_base, SerializerMixin):
    __tablename__ = 'record'
    __table_args__ = {'mysql_charset': 'utf8mb4'}
    __allow_unmapped__ = True  # 允许业务定义未持久化的拓展字段

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    keyword_id = Column(BigInteger, nullable=False, comment='关键词id')
    event_id = Column(BigInteger, nullable=False, comment='事件id')

    third_id = Column(String(64), nullable=False, comment='第三方id')
    source = Column(String(32), nullable=False, comment='渠道')
    author = Column(String(128), nullable=False, comment='作者')
    title = Column(String(128), nullable=False, comment='标题')
    content = Column(String(1024), comment='内容')
    heat = Column(Float, default=0, comment='热度')
    sentiment = Column(Float, comment='情感值')
    publish_datetime = Column(DateTime, nullable=False, comment='发布时间')
    url = Column(String(512), nullable=False, comment='链接')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(),
                         onupdate=func.now(), comment='更新时间')

    # 原始字段，存储JSON字符串
    _ext = Column('ext', Text, comment='拓展字段')

    # 业务字段，不持久化
    event_pos: Optional[int] = None

    @hybrid_property
    def ext(self):
        """获取ext字段时会自动将JSON字符串转为字典"""
        if self._ext is None:
            return {}
        try:
            return json.loads(self._ext)
        except (json.JSONDecodeError, TypeError):
            return {}

    @ext.setter
    def ext(self, value):
        """设置ext字段时会自动将字典转为JSON字符串"""
        if value is None:
            self._ext = None
        elif isinstance(value, str):
            # 如果是字符串，直接存储（假设已经是JSON字符串）
            self._ext = value
        else:
            # 如果是字典或其他可序列化对象，转为JSON
            self._ext = json.dumps(value, ensure_ascii=False)

    def to_dict(self):
        """重写SerializerMixin的to_dict方法，确保ext返回字典"""
        result = super().to_dict()
        if '_ext' in result:
            result['ext'] = self.ext  # 使用property返回字典
            del result['_ext']
        return result

    def __str__(self):
        return f"<{self.__tablename__} {self.to_dict()}>"

class SourceKeywordOffset(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 支持ORM转换

    id: Optional[int] = None
    keyword_id: Optional[int] = Field(None, comment='关键词id')
    source: Optional[str] = Field(None, max_length=32, comment='渠道')
    create_time: Optional[datetime] = Field(default=datetime.min, comment='创建时间')
    update_time: Optional[datetime] = None

    @classmethod
    def from_orm(cls, orm_obj: "SourceKeywordOffsetDO") -> "SourceKeywordOffset":
        """从数据库模型转换"""
        return cls.model_validate(orm_obj.to_dict())

    def to_orm(self) -> "SourceKeywordOffsetDO":
        """转换为数据库模型"""
        return SourceKeywordOffsetDO(
            id=self.id,
            keyword_id=self.keyword_id,
            source=self.source,
            create_time=self.create_time,
            update_time=self.update_time
        )

    def __str__(self) -> str:
        return self.model_dump_json()

class SourceKeywordOffsetDO(do_base, SerializerMixin):
    __tablename__ = 'source_keyword_offset'
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    keyword_id = Column(BigInteger, nullable=False, comment='关键词id')
    source = Column(String(32), nullable=False, comment='渠道')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), comment='更新时间')

    def __str__(self):
        return f"<SourceKeywordOffsetDO(id={self.id}, keyword_id={self.keyword_id}, source={self.source})>"

class ConfigKeyword(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # 支持 ORM 转换

    id: Optional[int] = None
    config_id: Optional[int] = None
    keyword_id: Optional[int] = None
    create_time: Optional[datetime] = None

    @classmethod
    def from_orm(cls, orm_obj: "ConfigKeywordDO") -> "ConfigKeyword":
        """从数据库模型转换"""
        return cls.model_validate(orm_obj.to_dict())

    def to_orm(self) -> "ConfigKeywordDO":
        """转换为数据库模型"""
        return ConfigKeywordDO(
            id=self.id,
            config_id=self.config_id,
            keyword_id=self.keyword_id,
            create_time=self.create_time
        )

    def __str__(self) -> str:
        return self.model_dump_json()

class ConfigKeywordDO(do_base, SerializerMixin):
    __tablename__ = 'config_keyword'
    __table_args__ = {'mysql_charset': 'utf8mb4'}

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    config_id = Column(BigInteger, nullable=False)
    keyword_id = Column(BigInteger, nullable=False)
    create_time = Column(DateTime, server_default=func.now(),
                        onupdate=func.now(), comment='创建时间')

    def __str__(self):
        return f"<{self.__tablename__} {self.to_dict()}>"

