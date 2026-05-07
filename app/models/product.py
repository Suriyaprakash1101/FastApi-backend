from sqlalchemy import Column, String, Integer, Float, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from ..database import Base
import uuid

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_name = Column(String, unique=True, nullable=False, index=True)
    
    # Relationship with Product
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    product_name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
   
    category = relationship("Category", back_populates="products")