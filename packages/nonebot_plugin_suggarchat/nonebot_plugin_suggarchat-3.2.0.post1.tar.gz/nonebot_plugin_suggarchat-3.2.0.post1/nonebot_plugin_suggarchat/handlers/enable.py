from nonebot import logger
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.matcher import Matcher

from ..check_rule import is_group_admin
from ..utils.memory import get_memory_data, write_memory_data


async def enable(bot: Bot, event: GroupMessageEvent, matcher: Matcher):
    """处理启用聊天功能的命令"""
    if not await is_group_admin(event, bot):
        await matcher.finish("你没有权限启用聊天功能")
    # 记录日志
    logger.debug(f"{event.group_id} enabled")
    # 获取当前群组的记忆数据
    data = await get_memory_data(event)
    # 检查记忆数据是否与当前群组匹配
    if data["id"] == event.group_id:
        # 如果聊天功能未启用，则启用并发送提示
        if not data["enable"]:
            data["enable"] = True
        await matcher.send("聊天启用")
    # 更新记忆数据
    await write_memory_data(event, data)
