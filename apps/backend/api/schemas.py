from typing import Optional, Any
from ninja import ModelSchema, Schema
from pydantic import UUID4
from datetime import datetime
from .models import (
    Profile, Organization, OrganizationMember, OrganizationInvite,
    Document, DocumentShare, Message
)

class ProfileSchema(ModelSchema):
    class Meta:
        model = Profile
        fields = "__all__"

class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = "__all__"

class OrganizationMemberSchema(ModelSchema):
    class Meta:
        model = OrganizationMember
        fields = "__all__"

class OrganizationInviteSchema(ModelSchema):
    class Meta:
        model = OrganizationInvite
        fields = "__all__"

class DocumentSchema(ModelSchema):
    class Meta:
        model = Document
        fields = "__all__"

class DocumentShareSchema(ModelSchema):
    class Meta:
        model = DocumentShare
        fields = "__all__"

class MessageSchema(ModelSchema):
    class Meta:
        model = Message
        fields = "__all__"

class HealthResponse(Schema):
    status: str
    timestampUtc: datetime

class DatabaseHealthResponse(Schema):
    status: str
    timestampUtc: datetime
    detail: str
