import re

from nonebot import logger, on_keyword
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.rule import Rule

from ..config import NICKNAME
from ..exception import handle_exception
from ..parsers import AcfunParser
from .filter import is_not_in_disabled_groups
from .helper import obhelper

acfun = on_keyword(keywords={"acfun.cn"}, rule=Rule(is_not_in_disabled_groups))

parser = AcfunParser()


@acfun.handle()
@handle_exception()
async def _(event: MessageEvent) -> None:
    message: str = event.message.extract_plain_text().strip()
    matched = re.search(r"(?:ac=|/ac)(\d+)", message)
    if not matched:
        logger.info("acfun 链接中不包含 acid, 忽略")
        return
    acid = int(matched.group(1))
    url = f"https://www.acfun.cn/v/ac{acid}"
    m3u8_url, video_desc = await parser.parse_url(url)
    await acfun.send(f"{NICKNAME}解析 | 猴山 - {video_desc}")

    video_file = await parser.download_video(m3u8_url, acid)
    await acfun.send(obhelper.video_seg(video_file))
