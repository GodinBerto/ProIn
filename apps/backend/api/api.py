from ninja import NinjaAPI
from .auth import AuthBearer
from .routers import (
    auth_router,
    health_router,
    workers_router,
    profiles_router,
    organizations_router,
    organization_members_router,
    organization_invites_router,
    documents_router,
    document_shares_router,
    messages_router,
)

api = NinjaAPI()
auth_bearer = AuthBearer()

api.add_router("/", health_router)
api.add_router("/auth", auth_router)
api.add_router("/workers", workers_router)
api.add_router("/profiles", profiles_router, auth=auth_bearer)
api.add_router("/organizations", organizations_router, auth=auth_bearer)
api.add_router("/organization_members", organization_members_router, auth=auth_bearer)
api.add_router("/organization_invites", organization_invites_router, auth=auth_bearer)
api.add_router("/documents", documents_router, auth=auth_bearer)
api.add_router("/document_shares", document_shares_router, auth=auth_bearer)
api.add_router("/messages", messages_router, auth=auth_bearer)
