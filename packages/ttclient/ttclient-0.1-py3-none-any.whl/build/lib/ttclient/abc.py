from datetime import datetime
from typing import TypedDict


class UserData(TypedDict):
    id: int                             # User ID
    name: str                           # Name
    name_trans: str | None              # Transliterated name for search
    info: str | None                    # Self description
    info_parsed: list[dict] | None      # Parsed description (with post parser)
    unique_name: str                    # Unique name (@uname)
    deleted: bool                       # Flag for deleted accounts
    active: bool                        # Flag for actiovation state
    time_updated: datetime              # Last data updation
    time_created: datetime              # Registarion datetime
    is_bot: bool                        # Flag for bots
    owner_id: int | None                # If bot, his owner id (user id)
    organizations: list[int] | None     # User member of this teams
    timezone_offset_minutes: int | None  # Timezone, offset in minutes


class TeamData(TypedDict):
    id: int
    slug: str | None
    title: str
    description: str | None
    email_domain: str | None
    time_created: datetime
    time_updated: datetime
    two_step_required: bool
    is_member: bool
    is_admin: bool
    state: str
    inviter_id: int
    guests: list[int]
    users: list[int]
    admins: list[int]
    groups: list[int]
    description_parsed: str | None
    default_chat_id: int | None
