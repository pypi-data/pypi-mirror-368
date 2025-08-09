import re

from nonebot import logger, on_message
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from ..config import NICKNAME
from ..download import DOWNLOADER
from ..exception import handle_exception
from ..parsers import XiaoHongShuParser
from .filter import is_not_in_disabled_groups
from .helper import obhelper
from .preprocess import ExtractText, r_keywords

xiaohongshu = on_message(rule=is_not_in_disabled_groups & r_keywords("xiaohongshu.com", "xhslink.com"))

xhs_parser = XiaoHongShuParser()


@xiaohongshu.handle()
@handle_exception()
async def _(text: str = ExtractText()):
    pattern = r"(http:|https:)\/\/(xhslink|(www\.)xiaohongshu).com\/[A-Za-z\d._?%&+\-=\/#@]*"
    matched = re.search(pattern, text)
    if not matched:
        logger.info(f"{text} 不是可达的小红书链接，忽略")
        return
    # 解析 url
    parse_result = await xhs_parser.parse_url(matched.group(0))
    # 如果是图文
    if parse_result.pic_urls:
        await xiaohongshu.send(f"{NICKNAME}解析 | 小红书 - 图文")
        img_path_list = await DOWNLOADER.download_imgs_without_raise(parse_result.pic_urls)
        # 发送图片
        segs: list[MessageSegment | Message | str] = [
            parse_result.title,
            *(obhelper.img_seg(img_path) for img_path in img_path_list),
        ]
        await obhelper.send_segments(segs)
    # 如果是视频
    elif parse_result.video_url:
        await xiaohongshu.send(f"{NICKNAME}解析 | 小红书 - 视频 - {parse_result.title}")
        video_path = await DOWNLOADER.download_video(parse_result.video_url)
        await xiaohongshu.finish(obhelper.video_seg(video_path))
