from packages.database import DatabaseTables
from ..models import Message
from ..schemas import MessageSchema
from .utils import create_crud_router

router = create_crud_router(Message, MessageSchema, DatabaseTables.MESSAGES)
