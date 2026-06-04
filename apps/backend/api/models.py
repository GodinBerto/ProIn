import uuid
from django.db import models


class OrganizationRole(models.TextChoices):
    OWNER = 'owner', 'Owner'
    ADMIN = 'admin', 'Admin'
    MEMBER = 'member', 'Member'


class DocumentType(models.TextChoices):
    INVOICE = 'invoice', 'Invoice'
    PROPOSAL = 'proposal', 'Proposal'


class DocumentStatus(models.TextChoices):
    DRAFT = 'draft', 'Draft'
    SENT = 'sent', 'Sent'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'
    PAID = 'paid', 'Paid'
    UNPAID = 'unpaid', 'Unpaid'
    OVERDUE = 'overdue', 'Overdue'


class DocumentShareRole(models.TextChoices):
    VIEWER = 'viewer', 'Viewer'
    EDITOR = 'editor', 'Editor'


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.TextField(unique=True)
    full_name = models.TextField(null=True, blank=True)
    company_name = models.TextField(null=True, blank=True)
    plan = models.TextField(default='free')
    downloads_used = models.IntegerField(default=0)
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
    default_currency = models.TextField(default='USD')
    default_payment_terms = models.TextField(null=True, blank=True)
    invoice_footer = models.TextField(null=True, blank=True)
    brand_color = models.TextField(null=True, blank=True)
    default_template = models.TextField(null=True, blank=True)
    bank_name = models.TextField(null=True, blank=True)
    bank_account_name = models.TextField(null=True, blank=True)
    bank_account_number = models.TextField(null=True, blank=True)
    bank_swift = models.TextField(null=True, blank=True)
    paypal_email = models.TextField(null=True, blank=True)
    notify_on_view = models.BooleanField(default=True)
    notify_weekly = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'profiles'
        ordering = ['-created_at']

class Organization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.TextField()
    slug = models.TextField(unique=True)
    logo_url = models.TextField(null=True, blank=True)
    owner_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'organizations'
        ordering = ['-created_at']

class OrganizationMember(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.UUIDField()
    user_id = models.UUIDField()
    role = models.TextField(choices=OrganizationRole.choices, default=OrganizationRole.MEMBER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'organization_members'
        ordering = ['-created_at']
        unique_together = (('org_id', 'user_id'),)

class OrganizationInvite(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.UUIDField()
    email = models.TextField()
    role = models.TextField(choices=OrganizationRole.choices, default=OrganizationRole.MEMBER)
    token = models.TextField(unique=True)
    invited_by = models.UUIDField(null=True, blank=True)
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'organization_invites'
        ordering = ['-created_at']

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField()
    type = models.TextField(choices=DocumentType.choices)
    number = models.TextField()
    title = models.TextField(null=True, blank=True)
    client_name = models.TextField(null=True, blank=True)
    data = models.JSONField(default=dict)
    status = models.TextField(choices=DocumentStatus.choices, default=DocumentStatus.DRAFT)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    org_id = models.UUIDField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = 'documents'
        ordering = ['-created_at']

class DocumentShare(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_id = models.UUIDField()
    org_id = models.UUIDField(null=True, blank=True)
    shared_with_user_id = models.UUIDField(null=True, blank=True)
    role = models.TextField(choices=DocumentShareRole.choices, default=DocumentShareRole.VIEWER)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'document_shares'
        ordering = ['-created_at']
        unique_together = (('document_id', 'shared_with_user_id'),)

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    org_id = models.UUIDField()
    user_id = models.UUIDField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'messages'
        ordering = ['-created_at']
