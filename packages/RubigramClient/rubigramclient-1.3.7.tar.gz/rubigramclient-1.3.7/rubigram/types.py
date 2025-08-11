from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional
import rubigram


@dataclass
class Location:
    longitude: Optional[str] = None
    latitude: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "longitude": self.longitude,
            "latitude": self.latitude
        }
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "Location":
        return cls(
            longitude = data.get("longitude"),
            latitude = data.get("latitude"),
        )

@dataclass
class ButtonSelectionItem:
    text: Optional[str] = None
    image_url: Optional[str] = None
    type: Optional[Literal["TextOnly", "TextImgThu", "TextImgBig"]] = None
    
    def _dict(self) -> Dict:
        return {
            "text": self.text,
            "image_url": self.image_url,
            "type": self.type
        }

@dataclass
class ButtonTextbox:
    type_line: Optional[Literal["SingleLine", "MultiLine"]] = None
    type_keypad: Optional[Literal["String", "Number"]] = None
    place_holder: Optional[str] = None
    title: Optional[str] = None
    default_value: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "type_line": self.type_line,
            "type_keypad": self.type_keypad,
            "place_holder": self.place_holder,
            "title": self.title,
            "default_value": self.default_value
        }

@dataclass
class ButtonLocation:
    default_pointer_location: Optional[Location] = None
    default_map_location: Optional[Location] = None
    type: Optional[Literal["Picker", "View"]] = None
    title: Optional[str] = None
    location_image_url: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "default_pointer_location": self.default_pointer_location._dict() if self.default_pointer_location else None,
            "default_map_location": self.default_map_location._dict() if self.default_map_location else None,
            "type": self.type,
            "title": self.title,
            "location_image_url": self.location_image_url
        }
    
@dataclass
class ButtonStringPicker:
    items: Optional[List[str]] = None
    default_value: Optional[str] = None
    title: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "items": self.items,
            "default_value": self.default_value,
            "title": self.title,
        }

@dataclass
class ButtonNumberPicker:
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    default_value: Optional[str] = None
    title: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "min_value": self.min_value,
            "max_value": self.max_value,
            "default_value": self.default_value,
            "title": self.title
        }
    
@dataclass
class ButtonCalendar:
    default_value: Optional[str] = None
    type: Optional[Literal["DatePersian", "DateGregorian"]] = None
    min_year: Optional[str] = None
    max_year: Optional[str] = None
    title: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "default_value": self.default_value,
            "type": self.type,
            "min_year": self.min_year,
            "max_year": self.max_year,
            "title": self.title
        }

@dataclass
class ButtonSelection:
    selection_id: Optional[str] = None
    search_type: Optional[str] = None
    get_type: Optional[str] = None
    items: Optional[ButtonSelectionItem] = None
    is_multi_selection: Optional[bool] = None
    columns_count: Optional[str] = None
    title: Optional[str] = None
    
    def _dict(self) -> Dict:
        return {
            "selection_id": self.selection_id,
            "search_type": self.search_type,
            "get_type": self.get_type,
            "items": self.items._dict() if self.items else None,
            "is_multi_selection": self.is_multi_selection,
            "columns_count": self.columns_count,
            "title": self.title
        }
    
    
    
@dataclass
class Button:
    id: Optional[str] = None
    type: Literal[
        "Simple", "Selection", "Calendar", "NumberPicker", "StringPicker", "Location", "Payment",
        "CameraImage", "CameraVideo", "GalleryImage", "GalleryVideo", "File", "Audio", "RecordAudio",
        "MyPhoneNumber", "MyLocation", "Textbox", "Link", "AskMyPhoneNumber", "AskLocation", "Barcode"
    ] = "Simple"
    button_text: Optional[str] = None
    button_selection: Optional[ButtonSelection] = None
    button_calendar: Optional[ButtonCalendar] = None
    button_number_picker: Optional[ButtonNumberPicker] = None
    button_string_picker: Optional[ButtonStringPicker] = None
    button_location: Optional[ButtonLocation] = None
    button_textbox: Optional[ButtonTextbox] = None
    
    def _dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.type,
            "button_text": self.button_text,
            "button_selection": self.button_selection._dict() if self.button_selection else None,
            "button_calendar": self.button_calendar._dict() if self.button_calendar else None,
            "button_number_picker": self.button_number_picker._dict() if self.button_number_picker else None,
            "button_string_picker": self.button_string_picker._dict() if self.button_string_picker else None,
            "button_location": self.button_location._dict() if self.button_location else None,
            "button_textbox": self.button_textbox._dict() if self.button_textbox else None
        }

@dataclass
class KeypadRow:
    buttons: List[Button]
    
    def _dict(self) -> Dict:
        return {
            "buttons": [button._dict() for button in self.buttons]
        }

@dataclass
class Keypad:
    rows: List[KeypadRow]
    resize_keyboard: bool = True
    on_time_keyboard: bool = False
    
    def _dict(self) -> Dict:
        return {
            "rows": [row._dict() for row in self.rows],
            "resize_keyboard": self.resize_keyboard,
            "one_time_keyboard": self.on_time_keyboard
        }

@dataclass
class MessageId:
    client: Optional["rubigram.Client"] = None
    message_id: Optional[str] = None
    file_id: Optional[str] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "MessageId":
        return cls(
            message_id = data.get("message_id"),
            file_id = data.get("file_id")
        )
        

@dataclass
class PollStatus:
    state: Optional[Literal["Open", "Closed"]] = None
    selection_index: Optional[int] = None
    percent_vote_options: Optional[List[int]] = None
    total_vote: Optional[int] = None
    show_total_votes: Optional[bool] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "PollStatus":
        return cls(
            state = data.get("state"),
            selection_index = data.get("selection_index"),
            percent_vote_options = data.get("percent_vote_options"),
            total_vote = data.get("total_vote"),
            show_total_votes = data.get("show_total_votes"),
        )

@dataclass
class File:
    file_id: Optional[str] = None
    file_name: Optional[str] = None
    size: Optional[str] = None
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "File":
        return cls(
            file_id = data.get("file_id"),
            file_name = data.get("file_name"),
            size = data.get("size"),
        )
    
@dataclass
class LiveLocation:
    start_time: Optional[str] = None
    live_period: Optional[int] = None
    current_location: Optional[Location] = None
    user_id: Optional[str] = None
    status: Optional[Literal["Stopped", "Live"]] = None
    last_update_time: Optional[str] = None
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "LiveLocation":
        return cls(
            start_time = data.get("start_time"),
            live_period = data.get("live_period"),
            current_location = Location.read(data.get("current_location")) if "current_location" in data else None,
            user_id = data.get("user_id"),
            status = data.get("status"),
            last_update_time = data.get("last_update_time")
        )
    
@dataclass
class Poll:
    question: Optional[str] = None
    options: Optional[List[str]] = None
    poll_status: Optional[PollStatus] = None
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "Poll":
        return cls(
            question = data.get("question"),
            options = data.get("options"),
            poll_status = PollStatus.read(data.get("poll_status")) if "poll_status" in data else None
        )
    
@dataclass
class ContactMessage:
    phone_number: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "ContactMessage":
        return cls(
            phone_number = data.get("phone_number"),
            first_name = data.get("first_name"),
            last_name = data.get("last_name")
        )
    
@dataclass
class Sticker:
    sticker_id: Optional[str] = None
    file: Optional[File] = None
    emoji_character: Optional[str] = None
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "Sticker":
        return cls(
            sticker_id = data.get("sticker_id"),
            file = File.read(data.get("file")) if "file" in data else None,
            emoji_character = data.get("emoji_character")
        )

@dataclass
class ForwardedFrom:
    type_from: Optional[Literal["User", "Channel", "Bot"]] = None
    message_id: Optional[str] = None
    from_chat_id: Optional[str] = None
    from_sender_id: Optional[str] = None
    
    @classmethod
    def read(cls, data: dict[str, Any]) -> "ForwardedFrom":
        return cls(
            type_from = data.get("type_from"),
            message_id = data.get("message_id"),
            from_chat_id = data.get("from_chat_id"),
            from_sender_id = data.get("from_sender_id")
        )

@dataclass
class AuxData:
    start_id: Optional[str] = None
    button_id: Optional[str] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "AuxData":
        return cls(
            start_id = data.get("start_id"),
            button_id = data.get("button_id")
        )
    
@dataclass
class PaymentStatus:
    payment_id: Optional[str] = None
    status: Optional[Literal["Paid", "NotPaid"]] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "PaymentStatus":
        return cls(
            payment_id = data.get("payment_id"),
            status = data.get("status")
        )

@dataclass
class Chat:
    chat_id: Optional[str] = None
    chat_type: Optional[Literal["User", "Bot", "Group", "Channel"]] = None
    user_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    title: Optional[str] = None
    username: Optional[str] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "Chat":
        return cls(
            chat_id = data.get("chat_id"),
            chat_type = data.get("chat_type"),
            user_id = data.get("user_id"),
            first_name = data.get("first_name"),
            last_name = data.get("last_name"),
            title = data.get("title"),
            username = data.get("username")
        )

@dataclass
class Bot:
    bot_id: Optional[str] = None
    bot_title: Optional[str] = None
    avatar: Optional[File] = None
    description: Optional[str] = None
    username: Optional[str] = None
    start_message: Optional[str] = None
    share_url: Optional[str] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "Bot":
        return cls(
            bot_id = data.get("bot_id"),
            bot_title = data.get("bot_title"),
            avatar = File.read(data.get("avatar")) if data.get("avatar") else None,
            description = data.get("description"),
            username = data.get("username"),
            start_message = data.get("start_message"),
            share_url = data.get("share_url")
        )

@dataclass
class InlineMessage:
    sender_id: Optional[str] = None
    text: Optional[str] = None
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    file: Optional[File] = None
    location: Optional[Location] = None
    aux_data: Optional[AuxData] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "InlineMessage":
        return cls(
            sender_id = data.get("sender_id"),
            text = data.get("text"),
            message_id = data.get("message_id"),
            chat_id = data.get("chat_id"),
            file = File.read(data.get("file")) if data.get("file") else None,
            location = Location.read(data.get("location")) if data.get("location") else None,
            aux_data = AuxData.read(data.get("aux_data")) if data.get("aux_data") else None
        )

@dataclass
class Message:
    message_id: Optional[str] = None
    text: Optional[str] = None
    time: Optional[str] = None
    is_edited: Optional[bool] = None
    sender_type: Optional[Literal["User", "Bot"]] = None
    sender_id: Optional[str] = None
    aux_data: Optional[AuxData] = None
    file: Optional[File] = None
    reply_to_message_id: Optional[str] = None
    forwarded_from: Optional[ForwardedFrom] = None
    forwarded_no_link: Optional[str] = None
    location: Optional[Location] = None
    sticker: Optional[Sticker] = None
    contact_message: Optional[ContactMessage] = None
    poll: Optional[Poll] = None
    live_location: Optional[LiveLocation] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any]) -> "Message":
        return cls(
            message_id = data["message_id"],
            text = data.get("text"),
            time = data["time"],
            is_edited = data["is_edited"],
            sender_type = data["sender_type"],
            sender_id = data["sender_id"],
            aux_data = AuxData.read(data["aux_data"]) if "aux_data" in data else None,
            file = File.read(data["file"]) if "file" in data else None,
            reply_to_message_id = data.get("reply_to_message_id"),
            forwarded_from = ForwardedFrom.read(data["forwarded_from"]) if "forwarded_from" in data else None,
            forwarded_no_link = data.get("forwarded_no_link"),
            location = Location.read(data["location"]) if "location" in data else None,
            sticker = Sticker.read(data["sticker"]) if "sticker" in data else None,
            contact_message = ContactMessage.read(data["contact_message"]) if "contact_message" in data else None,
            poll = Poll.read(data["poll"]) if "poll" in data else None,
            live_location = LiveLocation.read(data["live_location"]) if "live_location" in data else None
        )

@dataclass
class Update:
    client: Optional["rubigram.Client"] = None
    type: Optional[Literal["NewMessage", "UpdatedMessage", "RemovedMessage", "StartedBot", "StoppedBot", "UpdatedPayment"]] = None
    chat_id: Optional[str] = None
    removed_message_id: Optional[str] =  None
    new_message: Optional[Message] = None
    updated_message: Optional[Message] = None
    updated_payment: Optional[PaymentStatus] = None
    
    @classmethod
    def read(cls, data: Dict[str, Any], client: Optional["rubigram.Client"] = None) -> "Update":
        return cls(
            client = client,
            type = data["type"],
            chat_id = data["chat_id"],
            removed_message_id = data.get("removed_message_id"),
            new_message = Message.read(data["new_message"]) if "new_message" in data else None,
            updated_message = Message.read(data["updated_message"]) if "updated_message" in data else None,
            updated_payment = PaymentStatus.read(data["updated_payment"]) if "updated_payment" in data else None
        )
        
    async def reply_text(self, text: str) -> "MessageId":
        return await self.client.send_message(self.chat_id, text, reply_to_message_id=self.new_message.message_id)
        
    async def reply_file(self, path: str, file_name: str, type: Literal["File", "Image", "Voice", "Music", "Gif", "Video"] = "File") -> "MessageId":
        return await self.client.send_file(self.chat_id, path, file_name, type, reply_to_message_id=self.new_message.message_id)
    
    async def download(self, file_name: str):
        return await self.client.download_file(self.new_message.file.file_id, file_name)