from django.db.models import Q
from packages.database import DatabaseTables
from ..models import Organization, OrganizationMember
from ..schemas import OrganizationSchema
from .utils import create_crud_router

router = create_crud_router(Organization, OrganizationSchema, DatabaseTables.ORGANIZATIONS)

@router.get("/user/me", response=list[OrganizationSchema])
def list_user_organizations(request):
    user_id = request.auth.get("sub")
    if not user_id:
        return []
    
    member_org_ids = OrganizationMember.objects.filter(user_id=user_id).values_list('org_id', flat=True)
    return Organization.objects.filter(Q(owner_id=user_id) | Q(id__in=member_org_ids)).distinct()
