from packages.database import DatabaseTables
from ..models import OrganizationMember
from ..schemas import OrganizationMemberSchema
from .utils import create_crud_router

router = create_crud_router(OrganizationMember, OrganizationMemberSchema, DatabaseTables.ORGANIZATION_MEMBERS)
