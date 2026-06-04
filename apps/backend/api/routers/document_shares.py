from packages.database import DatabaseTables
from ..models import DocumentShare
from ..schemas import DocumentShareSchema
from .utils import create_crud_router

router = create_crud_router(DocumentShare, DocumentShareSchema, DatabaseTables.DOCUMENT_SHARES)
