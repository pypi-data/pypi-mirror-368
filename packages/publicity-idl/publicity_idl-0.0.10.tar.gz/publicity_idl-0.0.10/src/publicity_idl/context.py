from .enum import SourceEnum, ContextField
from .domain import Batch, Keyword, Event, Record, User, PushConfig, SourceKeywordOffset, PushConfigKeyword

class Context:
    def __init__(self, fields: dict = None):
        self.fields = fields.copy()  # 复制传入的fields字典

    def get_batch(self):
        return self.fields[ContextField.Batch.value]

    def get_source(self):
        return self.fields[ContextField.Source.value]

    def get_keyword(self):
        return self.fields[ContextField.Keyword.value]

    def get_event(self):
        return self.fields[ContextField.Event.value]

    def get_record(self):
        return self.fields[ContextField.Record.value]

    def get_user(self):
        return self.fields[ContextField.User.value]

    def get_push_config(self):
        return self.fields[ContextField.PushConfig.value]

    def get_push_config_keyword(self):
        return self.fields[ContextField.PushConfigKeyword.value]

    def get_source_keyword_offset(self):
        return self.fields[ContextField.SourceKeywordOffset.value]

    # 返回一个新的Context对象, 包含新的key-value
    def with_field(self, key: str, value: any):
        new_fields = self.fields.copy()
        new_fields[key] = value
        return Context(new_fields)

    def with_source(self, source: SourceEnum):
        return self.with_field(key=ContextField.Source.value, value=source.value)

    def with_batch(self, batch: Batch):
        return self.with_field(key=ContextField.Batch.value, value=batch)

    def with_keyword(self, keyword: Keyword):
        return self.with_field(key=ContextField.Keyword.value, value=keyword)

    def with_event(self, event: Event):
        return self.with_field(key=ContextField.Event.value, value=event)

    def with_user(self, user: User):
        return self.with_field(key=ContextField.User.value, value=user)

    def with_record(self, record: Record):
        return self.with_field(key=ContextField.Record.value, value=record)

    def with_push_config(self, push_config: PushConfig):
        return self.with_field(key=ContextField.PushConfig.value, value=push_config)

    def with_push_config_keyword(self, push_config_keyword: PushConfigKeyword):
        return self.with_field(key=ContextField.PushConfigKeyword.value, value=push_config_keyword)

    def with_source_keyword_offset(self, source_keyword_offset: SourceKeywordOffset):
        return self.with_field(key=ContextField.SourceKeywordOffset.value, value=source_keyword_offset)

    def __str__(self) -> str:
        """自定义字符串表示，直观展示所有字段信息"""
        # 存储格式化后的字段信息
        field_strings = []

        for key, value in self.fields.items():
            # 处理复杂对象，显示其关键属性（假设这些对象都有id属性）
            if isinstance(value, (Batch, Keyword, Event, Record, User, PushConfig,
                                  SourceKeywordOffset, PushConfigKeyword)):
                # 尝试获取id，如果没有则显示对象本身的字符串表示
                obj_id = getattr(value, 'id', None)
                if obj_id is not None:
                    field_strings.append(f"{key}: {value.__class__.__name__}(id={obj_id})")
                else:
                    field_strings.append(f"{key}: {str(value)}")
            # 处理SourceEnum类型
            elif isinstance(value, SourceEnum):
                field_strings.append(f"{key}: {value.name}({value.value})")
            # 其他基础类型直接显示
            else:
                field_strings.append(f"{key}: {value}")

        # 组合成最终的字符串
        return f"Context(fields: {{{', '.join(field_strings)}}})"
