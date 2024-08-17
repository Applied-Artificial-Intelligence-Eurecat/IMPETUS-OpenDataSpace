from sqlalchemy import Column, Boolean, String, ForeignKey, DateTime, Text, JSON, Integer
from sqlalchemy.orm import relationship

from repository.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True, index=True, unique=True)
    username = Column(String(255), primary_key=True, index=True)
    hashed_password = Column(String(255))
    datalibraries = relationship("DataLibrary", back_populates="owner")

class DataLibrary(Base):
    __tablename__ = "data_library"
    
    datalibrary_id = Column(String(255), index=True , primary_key=True) #owner_username:name
    name = Column(String(255), index=True)
    description = Column(Text)
    type_id = Column(Integer) # 0-> general, 1-> file, 2->timeseries
    public = Column(Boolean, default=True)
    owner_id = Column(String(255), ForeignKey("users.user_id"))
    owner = relationship(User, back_populates="datalibraries")
