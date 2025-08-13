import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    READY_FOR_REVIEW = "ready_for_review"
    IN_REVIEW = "in_review"
    DONE = "done"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TasksSorting(str, Enum):
    created_at = "created_at"
    updated_at = "updated_at"
    priority = "priority"
    due_date = "due_date"


class HistoryChangeType(str, Enum):
    TASK_CREATED = "task_created"
    FIELD_CHANGED = "field_changed"
    COMMENT_ADDED = "comment_added"
    COMMENT_DELETED = "comment_deleted"
    SUBTASK_ADDED = "subtask_added"
    SUBTASK_DELETED = "subtask_deleted"
    SUBTASK_COMPLETED = "subtask_completed"
    SUBTASK_REOPENED = "subtask_reopened"
    LABELS_ADDED = "labels_added"
    LABELS_REMOVED = "labels_removed"


class SubtaskCreate(BaseModel):
    title: str = Field(..., description="The title of the subtask")
    description: Optional[str] = Field(None, description="The description of the subtask")


class Subtask(BaseModel):
    subtask_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="The title of the subtask")
    description: Optional[str] = Field(None, description="The description of the subtask")
    completed: bool = Field(default=False, description="Whether the subtask is completed")
    created_at: datetime = Field(..., description="When the subtask was created")
    updated_at: datetime = Field(..., description="When the subtask was last updated")


class CommentCreate(BaseModel):
    text: str = Field(..., description="The comment text")


class Comment(BaseModel):
    comment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = Field(..., description="The comment text")
    author_id: str = Field(..., description="The ID of the comment author")
    created_at: datetime = Field(..., description="When the comment was created")


class TaskHistoryEntry(BaseModel):
    history_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    change_type: HistoryChangeType = Field(..., description="The type of change")
    field_name: Optional[str] = Field(None, description="The name of the field that changed")
    old_value: Optional[Union[str, int, float, bool, List[str]]] = Field(None, description="The old value")
    new_value: Optional[Union[str, int, float, bool, List[str]]] = Field(None, description="The new value")
    changed_by: str = Field(..., description="The ID of the user who made the change")
    changed_at: datetime = Field(..., description="When the change was made")
    additional_data: Optional[dict] = Field(None, description="Additional data related to the change")


class TaskHistory(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: List[TaskHistoryEntry] = Field(..., description="The history of changes")


class PaginatedTaskHistory(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    history: List[TaskHistoryEntry] = Field(..., description="The history entries")
    last_evaluated_key: Optional[str] = Field(None, description="The key for pagination")
    has_more: bool = Field(..., description="Whether there are more history entries")


class TaskCreate(BaseModel):
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="The status of the task")
    assignee: Optional[str] = Field(None, description="The assignee of the task")
    reporter: Optional[str] = Field(None, description="The reporter of the task")
    labels: List[str] = Field(default_factory=list, description="The labels of the task")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="The priority of the task")
    start_date: Optional[datetime] = Field(None, description="The start date of the task")
    end_date: Optional[datetime] = Field(None, description="The end date of the task")

    def to_task(
        self,
        *,
        integration_id: str,
        created_by: str,
        updated_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        subtasks: Optional[List[Subtask]] = None,
        comments: Optional[List[Comment]] = None,
        history: Optional[List[TaskHistoryEntry]] = None,
    ) -> "Task":
        now = datetime.now(timezone.utc)
        created_at = created_at or now
        updated_at = updated_at or now
        updated_by = updated_by or created_by

        return Task(
            integration_id=integration_id,
            title=self.title,
            description=self.description,
            status=self.status,
            assignee=self.assignee,
            reporter=self.reporter,
            labels=list(self.labels),
            priority=self.priority,
            start_date=self.start_date,
            end_date=self.end_date,
            subtasks=subtasks or [],
            comments=comments or [],
            history=history or [],
            created_at=created_at,
            updated_at=updated_at,
            created_by=created_by,
            updated_by=updated_by,
        )


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    assignee: Optional[str] = Field(None, description="The assignee of the task")
    reporter: Optional[str] = Field(None, description="The reporter of the task")
    labels: Optional[List[str]] = Field(None, description="The labels of the task")
    priority: Optional[TaskPriority] = Field(None, description="The priority of the task")
    start_date: Optional[datetime] = Field(None, description="The start date of the task")
    end_date: Optional[datetime] = Field(None, description="The end date of the task")


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str = Field(..., description="The ID of the integration")
    title: str = Field(..., description="The title of the task")
    description: Optional[str] = Field(None, description="The description of the task")
    status: TaskStatus = Field(..., description="The status of the task")
    assignee: Optional[str] = Field(None, description="The assignee of the task")
    reporter: Optional[str] = Field(None, description="The reporter of the task")
    labels: List[str] = Field(default_factory=list, description="The labels of the task")
    priority: TaskPriority = Field(..., description="The priority of the task")
    start_date: Optional[datetime] = Field(None, description="The start date of the task")
    end_date: Optional[datetime] = Field(None, description="The end date of the task")
    subtasks: List[Subtask] = Field(default_factory=list, description="The subtasks of the task")
    comments: List[Comment] = Field(default_factory=list, description="The comments on the task")
    history: List[TaskHistoryEntry] = Field(default_factory=list, description="The history of changes")
    created_at: datetime = Field(..., description="When the task was created")
    updated_at: datetime = Field(..., description="When the task was last updated")
    created_by: str = Field(..., description="Who created the task")
    updated_by: str = Field(..., description="Who last updated the task")


class PaginatedTasks(BaseModel):
    tasks: List[Task] = Field(..., description="The list of tasks")
    last_evaluated_key: Optional[str] = Field(None, description="The key for pagination")
    has_more: bool = Field(..., description="Whether there are more tasks")
