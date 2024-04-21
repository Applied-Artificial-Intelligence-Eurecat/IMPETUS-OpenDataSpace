from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from db.postgres import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True, index=True, unique=True)
    username = Column(String(255), primary_key=True, index=True)
    hashed_password = Column(String(255))
    datadefinitions = relationship("ODSDataDefinition", back_populates="owner")
class ODSDataDefinition(Base):
    __tablename__ = "ods_data_definition"

    definition_id = Column(String(255), primary_key=True, index=True)
    definition_name = Column(String(255), index=True)
    definition_type = Column(Integer)
    owner_id = Column(String(255), ForeignKey("users.user_id"))
    owner = relationship(User, back_populates="datadefinitions")
    creation_time = Column(DateTime)
    