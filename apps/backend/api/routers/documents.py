from packages.database import DatabaseTables
from ..models import Document
from ..schemas import DocumentSchema
from .utils import create_crud_router

router = create_crud_router(Document, DocumentSchema, DatabaseTables.DOCUMENTS)
