from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional

class CategoryCreate(BaseModel):
    category_name: str

class CategoryResponse(BaseModel):
    category_id: UUID
    category_name: str
    
    class Config:
        from_attributes = True

class ProductCreate(BaseModel):
    product_name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    category_id: UUID

class ProductResponse(BaseModel):
    product_id: UUID
    product_name: str
    description: Optional[str] = None
    price: float
    quantity: int
    category_id: UUID
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    total: int
    page: int
    size: int
    pages: int
    

class BulkProductCreate(BaseModel):
    products: List[ProductCreate]

class BulkProductResponse(BaseModel):
    message: str
    total_added: int
    products: List[ProductResponse]
    failed_count: int
    errors: Optional[List[str]] = None
    
    

class ProductCreateBulk(BaseModel):
    """Schema for bulk product creation without category_id"""
    product_name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    # No category_id here - it will come from URL

class BulkProductCreate(BaseModel):
    products: List[ProductCreateBulk]  # Use the new schema