from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from backend.database.database import Base


class Map(Base):
    __tablename__ = "maps"

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
    route_data = Column(
        JSON,
        nullable=False
    )