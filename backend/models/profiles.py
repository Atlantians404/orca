from sqlalchemy import Column, Integer, String, ForeignKey
from backend.database.database import Base


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    display_name = Column(
        String,
        nullable=False
    )

    language = Column(
        String,
        default="en",
        nullable=False
    )