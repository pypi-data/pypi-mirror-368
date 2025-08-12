from typing import Union

from globalgenie.storage.session.agent import AgentSession
from globalgenie.storage.session.team import TeamSession
from globalgenie.storage.session.v2.workflow import WorkflowSession as WorkflowSessionV2
from globalgenie.storage.session.workflow import WorkflowSession

Session = Union[AgentSession, TeamSession, WorkflowSession, WorkflowSessionV2]

__all__ = [
    "AgentSession",
    "TeamSession",
    "WorkflowSession",
    "WorkflowSessionV2",
    "Session",
]
