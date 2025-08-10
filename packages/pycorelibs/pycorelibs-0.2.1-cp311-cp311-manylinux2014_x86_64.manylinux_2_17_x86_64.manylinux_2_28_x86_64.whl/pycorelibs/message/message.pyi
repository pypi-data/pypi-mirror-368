from pydantic import BaseModel

class MessageModel(BaseModel):
    text: str
    msg_id: str | None
    priority: int | None
    created: float | None
