import json
from abc import ABC, abstractmethod

from lark_helper.constants.message import MessageType


class MessageContent(ABC):
    @property
    @abstractmethod
    def message_type(self) -> MessageType:
        pass

    @abstractmethod
    def json_str(self) -> str:
        pass

    @classmethod
    @abstractmethod
    def from_json_str(cls, json_str: str):
        pass


class TextMessageContent(MessageContent):
    def __init__(self, text: str):
        self.text = text

    def json_str(self) -> str:
        return json.dumps({"text": self.text}, ensure_ascii=False)

    @property
    def message_type(self) -> MessageType:
        return MessageType.TEXT

    @classmethod
    def from_json_str(cls, json_str: str):
        return cls(json.loads(json_str).get("text"))


class PostMessageContent(MessageContent):
    def __init__(self, content: list[list[dict]]):
        self.content = content

    def json_str(self) -> str:
        return json.dumps({"zh_cn": {"content": self.content}}, ensure_ascii=False)

    @property
    def message_type(self) -> MessageType:
        return MessageType.POST

    @classmethod
    def from_json_str(cls, json_str: str):
        return cls(json.loads(json_str).get("content"))


class ImageMessageContent(MessageContent):
    def __init__(self, image_key: str):
        self.image_key = image_key

    def json_str(self) -> str:
        return json.dumps({"image_key": self.image_key}, ensure_ascii=False)

    @property
    def message_type(self) -> MessageType:
        return MessageType.IMAGE

    @classmethod
    def from_json_str(cls, json_str: str):
        return cls(json.loads(json_str).get("image_key"))


class InteractiveMessageContent(MessageContent):
    def __init__(self, card_json: dict):
        self.card_json = card_json

    def json_str(self) -> str:
        return json.dumps(self.card_json, ensure_ascii=False)

    @property
    def message_type(self) -> MessageType:
        return MessageType.INTERACTIVE

    @classmethod
    def from_json_str(cls, json_str: str):
        return cls(json.loads(json_str))


class MarkdownMessageContent(PostMessageContent):
    def __init__(self, text: str):
        content = [[{"tag": "md", "text": text}]]
        super().__init__(content)
