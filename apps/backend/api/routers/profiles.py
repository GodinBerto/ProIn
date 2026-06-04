from packages.database import DatabaseTables
from ..models import Profile
from ..schemas import ProfileSchema
from .utils import create_crud_router

router = create_crud_router(Profile, ProfileSchema, DatabaseTables.PROFILES)
