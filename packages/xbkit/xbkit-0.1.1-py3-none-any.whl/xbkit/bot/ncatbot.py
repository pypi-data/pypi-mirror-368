import asyncio
from dataclasses import dataclass
from mailbox import BabylMessage
from typing import Any, Callable, Literal
from ncatbot.utils import PermissionGroup, get_log
from ncatbot.plugin.event import Func
from ncatbot.core import BaseMessage, GroupMessage
from ncatbot.utils.config import config


# bot的功能注册元数据
@dataclass
class BotFuncMeta:
    permission: PermissionGroup  # 权限类型，如 USER / ADMIN
    name: str  # 功能名
    handler: Callable  # 主处理函数（回调）
    filter: Callable | None = None  # 过滤器函数（回调），可选
    prefix: str | None = None  # 匹配前缀
    regex: str | None = None  # 正则匹配
    permission_raise: bool = False  # 是否提权
    description: str = ""  # 功能描述
    usage: str = ""  # 使用说明
    examples: list[str] | None = None  # 示例
    tags: list[str] | None = None  # 标签
    metadata: dict | None = None  # 附加元数据

    def to_register_kwargs(self):
        kwargs = {k: v for k, v in vars(self).items()}
        kwargs.pop("permission")
        return kwargs


# bot的配置注册元数据
@dataclass
class BotConfigMeta:
    key: str  # 配置名
    default: Any  # 默认值
    on_change: Callable[[str, BabylMessage, Any], Any] = None  # 类型改变
    description: str = ""  # 配置描述
    value_type: Literal["int", "bool", "str", "float"] = ""  # 值类型
    allowed_values: list[Any] = None  # 允许值
    metadata: dict[str, Any] = None  # 元数据

    def to_register_kwargs(self):
        kwargs = {k: v for k, v in vars(self).items()}
        return kwargs


# 提供日志功能
class LoggerMixin:

    @property
    def log(self):
        class_name = self.__class__.__name__
        LOG = get_log(class_name)

        class _LogProxy:
            def __getattr__(self, level):
                def wrapper(msg, *args, **kwargs):
                    return getattr(LOG, level)(f"{msg}", *args, **kwargs)

                return wrapper

        return _LogProxy()


# 插件元数据 注册功能，注册配置，开启功能权限检验回复
class PluginMetaMixin(LoggerMixin):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

        original_on_load = getattr(cls, "on_load", None)

        async def wrapped_on_load(self):
            # 自动调用 配置注册
            self.__reg_bot_config()

            # 调用原来的 on_load（如果有）
            if original_on_load:
                if asyncio.iscoroutinefunction(original_on_load):
                    await original_on_load(self)
                else:
                    original_on_load(self)
            # 自动调用 功能注册
            self.__reg_bot_func()

            self.__open_func_reply()

        setattr(cls, "on_load", wrapped_on_load)

    # 注册bot功能
    def __reg_bot_func(self):
        bot_func_list: list[BotFuncMeta] = getattr(self, "bot_func_list", [])
        reg_func_list = {
            PermissionGroup.USER: getattr(self, "register_user_func", None),
            PermissionGroup.ADMIN: getattr(self, "register_admin_func", None),
            PermissionGroup.ROOT: getattr(self, "register_root_func", None),
        }
        for func in bot_func_list:
            reg_func: Callable = reg_func_list[func.permission]
            if reg_func:
                reg_func(**func.to_register_kwargs())
                self.log.info(
                    f"[{self.__class__.__name__}] 功能注册 功能名:[{func.name}] 功能描述:[{func.description}] 使用说明:[{func.usage}]"
                )

    # 注册bot配置
    def __reg_bot_config(self):
        bot_config_list: list[BotConfigMeta] = getattr(self, "bot_config_list", [])
        reg_config_func = getattr(self, "register_config", None)
        for config in bot_config_list:
            if reg_config_func:
                reg_config_func(**config.to_register_kwargs())
                self.log.info(
                    f"[{self.__class__.__name__}] 配置注册 配置名:[{config.key}] 值类型:[{config.value_type}] 默认值:[{config.default}]"
                )

    # 开启功能权限检验回复
    def __open_func_reply(self):
        _open_func_reply: bool = getattr(self, "_open_func_reply", [])
        if not _open_func_reply:
            return

        _funcs: list[Func] = getattr(self, "_funcs", [])
        for func in _funcs:
            func.reply = True
        self.log.info(f"[{self.__class__.__name__}] 开启功能权限检验回复!")


# 检测群组聊天有没有at机器人, 不关心没at机器人的消息
def check_group_at_me(recv_msg: BaseMessage) -> bool:
    if not isinstance(recv_msg, GroupMessage):
        return True
    for msg in recv_msg.message:
        if msg["type"] == "at" and msg["data"]["qq"] == config.bt_uin:
            return True
    return False


# 拼接文本类型消息
def splicing_text_msg(recv_msg: BaseMessage) -> str:
    text_msg = ""
    for msg in recv_msg.message:
        if msg["type"] == "text":
            text_msg += msg["data"]["text"]
    return text_msg


# 解析文本消息，当被at时
def parse_text_on_at(recv_msg: BaseMessage) -> str | None:
    if not check_group_at_me(recv_msg):
        return None
    return splicing_text_msg(recv_msg)
