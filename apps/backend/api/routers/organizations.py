from packages.database import DatabaseTables
from ..models import Organization
from ..schemas import OrganizationSchema
from .utils import create_crud_router

router = create_crud_router(Organization, OrganizationSchema, DatabaseTables.ORGANIZATIONS)
