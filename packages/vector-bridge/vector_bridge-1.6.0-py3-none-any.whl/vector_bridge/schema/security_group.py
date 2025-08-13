from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field

DEFAULT_SECURITY_GROUP = "default"


class SecurityGroupsSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"


# Define individual permission models for each category
class LogsPermissions(BaseModel):
    read: bool


class NotificationsPermissions(BaseModel):
    read: bool
    listen_websocket: bool


class UsagePermissions(BaseModel):
    read: bool


class UserPermissions(BaseModel):
    read_env_variables: bool
    write_env_variables: bool


class IntegrationsPermissions(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool
    add_user: bool
    update_users_security_group: bool
    remove_user: bool


class InstructionsPermissions(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool
    add_agent: bool
    remove_agent: bool
    add_subordinate: bool
    remove_subordinate: bool


class FunctionsPermissions(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool
    run: bool


class WorkflowsPermissions(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool


class ChatPermissions(BaseModel):
    read: bool
    delete: bool


class MessagePermissions(BaseModel):
    create: bool
    read: bool
    delete: bool


class AIKnowledgeFileStoragePermissions(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool
    grant_revoke_access: bool


class AIKnowledgeDatabasePermissions(BaseModel):
    create: bool
    read: bool
    update: bool
    delete: bool


class DatabaseStatePermissions(BaseModel):
    apply_changes: bool
    discard_changes: bool
    preview_schema_changes: bool


class DatabaseChangesetManagementPermissions(BaseModel):
    add_schema: bool
    delete_schema: bool
    add_property: bool
    update_property: bool
    delete_property: bool
    add_filter: bool
    update_filter: bool
    delete_filter: bool


# Aggregate all permission categories into a single Permissions class
class Permissions(BaseModel):
    logs: LogsPermissions
    notifications: NotificationsPermissions
    usage: UsagePermissions
    user: UserPermissions
    integrations: IntegrationsPermissions
    instructions: InstructionsPermissions
    functions: FunctionsPermissions
    workflows: WorkflowsPermissions
    chat: ChatPermissions
    message: MessagePermissions
    ai_knowledge_file_storage: AIKnowledgeFileStoragePermissions
    ai_knowledge_database: AIKnowledgeDatabasePermissions
    database_state: DatabaseStatePermissions
    database_changeset_management: DatabaseChangesetManagementPermissions


# Security Group Models
class SecurityGroupCreate(BaseModel):
    group_name: str
    description: str


class SecurityGroup(SecurityGroupCreate):
    group_id: str = Field(default_factory=lambda: str(uuid4()))
    organization_id: str = Field(default=None)
    group_permissions: Permissions
    created_at: datetime
    updated_at: datetime

    @property
    def uuid(self):
        return self.group_id


class SecurityGroupUpdate(BaseModel):
    permissions: Permissions


class PaginatedSecurityGroups(BaseModel):
    security_groups: List[SecurityGroup]
    limit: int
    last_evaluated_key: Optional[str] = None
    has_more: bool
