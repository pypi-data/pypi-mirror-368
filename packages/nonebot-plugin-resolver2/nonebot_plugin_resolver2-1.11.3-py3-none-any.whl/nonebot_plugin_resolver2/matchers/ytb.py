from pathlib import Path
import re
from typing import Any

from nonebot import logger, on_keyword
from nonebot.adapters.onebot.v11 import Bot, MessageEvent
from nonebot.params import PausePromptResult
from nonebot.rule import Rule
from nonebot.typing import T_State

from ..config import NEED_UPLOAD, NICKNAME, ytb_cookies_file
from ..download.ytdlp import get_video_info, ytdlp_download_audio, ytdlp_download_video
from ..exception import handle_exception
from ..utils import keep_zh_en_num
from .filter import is_not_in_disabled_groups
from .helper import obhelper

ytb = on_keyword(keywords={"youtube.com", "youtu.be"}, rule=Rule(is_not_in_disabled_groups))


@ytb.handle()
@handle_exception()
async def _(event: MessageEvent, state: T_State):
    message = event.message.extract_plain_text().strip()
    pattern = (
        # https://youtu.be/EKkzbbLYPuI?si=K_S9zIp5g7DhigVz
        # https://www.youtube.com/watch?v=1LnPnmKALL8&list=RD8AxpdwegNKc&index=2
        r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/[A-Za-z\d\._\?%&\+\-=/#]+"
    )
    matched = re.search(pattern, message)
    if not matched:
        logger.warning(f"{message} 中的链接不支持，已忽略")
        await ytb.finish()

    url = matched.group(0)
    try:
        info_dict = await get_video_info(url, ytb_cookies_file)
        title = info_dict.get("title", "未知")
    except Exception:
        logger.error(f"油管标题获取失败 | {url}", exc_info=True)
        await ytb.finish(f"{NICKNAME}解析 | 油管 - 标题获取出错")
    await ytb.send(f"{NICKNAME}解析 | 油管 - {title}")
    state["url"] = url
    state["title"] = title
    await ytb.pause("您需要下载音频(0)，还是视频(1)")


@ytb.handle()
async def _(
    bot: Bot,
    event: MessageEvent,
    state: T_State,
    pause_result: Any = PausePromptResult(),
):
    # 回应用户
    await bot.call_api("set_msg_emoji_like", message_id=event.message_id, emoji_id="282")
    # 撤回 选择类型 的 prompt
    await bot.delete_msg(message_id=pause_result["message_id"])
    # 获取 url 和 title
    url: str = state["url"]
    title: str = state["title"]
    # 下载视频或音频
    video_path: Path | None = None
    audio_path: Path | None = None
    # 判断是否下载视频
    type = event.message.extract_plain_text().strip()
    is_video = type == "1"
    try:
        if is_video:
            video_path = await ytdlp_download_video(url, ytb_cookies_file)
        else:
            audio_path = await ytdlp_download_audio(url, ytb_cookies_file)
    except Exception:
        media_type = "视频" if is_video else "音频"
        logger.error(f"{media_type}下载失败 | {url}", exc_info=True)
        await ytb.finish(f"{media_type}下载失败", reply_message=True)
    # 发送视频或音频
    if video_path:
        await ytb.send(obhelper.video_seg(video_path))
    elif audio_path:
        await ytb.send(obhelper.record_seg(audio_path))
        if NEED_UPLOAD:
            file_name = f"{keep_zh_en_num(title)}.flac"
            await ytb.send(obhelper.file_seg(audio_path, file_name))
