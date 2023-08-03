"""Для доступа ко всем pydantic-схемам в проекте."""
from .charity_project import CharityProjectCreate, CharityProjectUpdate, CharityProjectDB # noqa
from .donation import DonationCreate, DonationDB # noqa
from .user import UserCreate, UserRead, UserUpdate # noqa
