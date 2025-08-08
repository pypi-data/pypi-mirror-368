import logging
import re

logger = logging.getLogger(__name__)

DEFAULT_MARGIN = "0px 0px 0px 0px"


def get_md_card_json(title: str, content: str, extra_elements: list | None = None):
    # 处理飞书图片代理链接，避免接口报错

    # 匹配包含 feishu.cn/api/proxy/down? 的图片链接
    pattern_1 = r"!\[([^\]]*)\]\((https://[^)]*feishu\.cn/api/proxy/down\?[^)]*)\)"
    pattern_2 = r"!\[([^\]]*)\]\((https://[^)]*hailiang\.com/api/proxy/down\?[^)]*)\)"

    # 将图片链接替换为文本描述
    def replace_image(match):
        alt_text = match.group(1) if match.group(1) else "图片"
        logger.warning(f"alt_text: {alt_text}")
        return f"[{alt_text}]"

    processed_content = re.sub(pattern_1, replace_image, content)
    processed_content = re.sub(pattern_2, replace_image, processed_content)

    elements = [{"tag": "markdown", "content": processed_content}]
    if extra_elements:
        elements.extend(extra_elements)
    return {
        "schema": "2.0",
        "config": {},
        "card_link": {},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            # 标题主题样式颜色。支持 "blue"|"wathet"|"turquoise"|"green"|"yellow"|"orange"|"red"|"carmine"|"violet"|"purple"|"indigo"|"grey"|"default"。默认值 default。
            "template": "blue",
            # "padding": "12px 8px 12px 8px"
        },
        "body": {"elements": elements},
    }


def gen_hr():
    return {"tag": "hr", "margin": DEFAULT_MARGIN}


def gen_column_set():
    return {
        "tag": "column_set",
        "horizontal_spacing": "8px",
        "horizontal_align": "left",
        "margin": DEFAULT_MARGIN,
        "columns": [],
    }


def gen_button(content: str, callback_value: str):
    return {
        "tag": "button",
        "text": {"tag": "plain_text", "content": content},
        "type": "default",
        "width": "default",
        "behaviors": [{"type": "callback", "value": {"content": callback_value}}],
        "margin": DEFAULT_MARGIN,
    }


def gen_column(elements: list):
    return {
        "tag": "column",
        "width": "auto",
        "elements": elements,
        "vertical_align": "top",
    }
