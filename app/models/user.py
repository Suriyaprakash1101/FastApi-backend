

# from sqlalchemy import Column,String,UUID
# import uuid

# class User():
#     __tablename__ = "users"
    
#     id = Column(as_uuid=True, primary_key = True,default = uuid.uuid4)
#     email = Column(String,unique=True,index=True,nullable=False)
#     name = Column(String,nullable=False)
#     password = Column(String,nullable=False)
#     address = Column(String,nullable=True)
    
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from ..database import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # Fixed: UUID type
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    password = Column(String, nullable=False)
    address = Column(String, nullable=True)