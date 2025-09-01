from sqlalchemy import Integer, String, DateTime, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime, timezone


class Base(DeclarativeBase):
    pass