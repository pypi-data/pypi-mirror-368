from rubigram.types import Update, InlineMessage
from typing import Union

def command(commands: Union[str, list[str]], prefixe: str = "/"):
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage" and message.new_message.text:
            text = message.new_message.text
            COMMANDS = commands if isinstance(commands, list) else [commands]
            for cmd in COMMANDS:
                if text.lower().startswith(prefixe + cmd):
                    return True
        return False
    return filter

def button(id: Union[str, list[str]]):
    def filter(message: InlineMessage):
        if isinstance(message, InlineMessage):
            button_id = message.aux_data.button_id
            ID = id if isinstance(id, list) else [id]
            for i in ID:
                if button_id == i:
                    return True
        return False
    return filter

def chat(chat_id: Union[str, list[str]]):
    def filter(message: Union[Update, InlineMessage]):
        chat_ids = chat_id if isinstance(chat_id, list) else [chat_id]
        if isinstance(message, Update) or isinstance(message, InlineMessage):
            return message.chat_id in chat_ids
        return False
    return filter

def text():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return bool(message.new_message.text)
        return False
    return filter

def file():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return bool(message.new_message.file)
        return False
    return filter

def private():
    def filter(message: Update):
        if isinstance(message, Update) and message.type == "NewMessage":
            return message.new_message.sender_type in ["User", "Bot"]
        return False
    return filter