from packages.database import DatabaseTables
from ..models import OrganizationInvite
from ..schemas import OrganizationInviteSchema
from .utils import create_crud_router

router = create_crud_router(OrganizationInvite, OrganizationInviteSchema, DatabaseTables.ORGANIZATION_INVITES)
