from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    title = Column(
        String,
        nullable=False
    )

    summary = Column(
        Text,
        nullable=True
    )