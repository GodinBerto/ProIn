import uuid
from django.db import models

class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.TextField(null=True, blank=True)
    full_name = models.TextField(null=True, blank=True)
    company_name = models.TextField(null=True, blank=True)
    plan = models.TextField(null=True, blank=True)
    downloads_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    avatar_url = models.TextField(null=True, blank=True)
    phone = models.TextField(null=True, blank=True)
    legal_name = models.TextField(null=True, blank=True)
    tax_id = models.TextField(null=True, blank=True)
    address_line1 = models.TextField(null=True, blank=True)
    address_line2 = models.TextField(null=True, blank=True)
    city = models.TextField(null=True, blank=True)
    state = models.TextField(null=True, blank=True)
    postal_code = models.TextField(null=True, blank=True)
    country = models.TextField(null=True, blank=True)
    website = models.TextField(null=True, blank=True)
    logo_url = models.TextField(null=True, blank=True)
    default_currency = models.TextField(null=True, blank=True)
    default_payment_terms = models.TextField(null=True, blank=True)
    invoice_footer = models.TextField(null=True, blank=True)
    brand_color = models.TextField(null=True, blank=True)
    default_template = models.TextField(null=True, blank=True)
    bank_name = models.TextField(null=True, blank=True)
    bank_account_name = models.TextField(null=True, blank=True)
    bank_account_number = models.TextField(null=True, blank=True)
    bank_swift = models.TextField(null=True, blank=True)
    paypal_email = models.TextField(null=True, blank=True)
    notify_on_view = models.BooleanField(null=True, blank=True)
    notify_weekly = models.BooleanField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'profiles'

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField(null=True, blank=True)
    slug = models.TextField(null=True, blank=True)
    logo_url = models.TextField(null=True, blank=True)
    owner_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'organizations'

class OrganizationMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.UUIDField(null=True, blank=True)
    user_id = models.UUIDField(null=True, blank=True)
    role = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'organization_members'

class OrganizationInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.UUIDField(null=True, blank=True)
    email = models.TextField(null=True, blank=True)
    role = models.TextField(null=True, blank=True)
    token = models.TextField(null=True, blank=True)
    invited_by = models.UUIDField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'organization_invites'

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(null=True, blank=True)
    type = models.TextField(null=True, blank=True)
    number = models.TextField(null=True, blank=True)
    title = models.TextField(null=True, blank=True)
    client_name = models.TextField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)
    status = models.TextField(null=True, blank=True)
    is_public = models.BooleanField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    org_id = models.UUIDField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'documents'

class DocumentShare(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_id = models.UUIDField(null=True, blank=True)
    org_id = models.UUIDField(null=True, blank=True)
    shared_with_user_id = models.UUIDField(null=True, blank=True)
    role = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'document_shares'

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.UUIDField(null=True, blank=True)
    user_id = models.UUIDField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'messages'
