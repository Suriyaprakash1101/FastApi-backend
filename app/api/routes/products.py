from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import Optional
from uuid import UUID

from app.models.product import Product, Category
from app.Schemas.productSchema import (
    ProductCreate, ProductResponse, 
    CategoryResponse, ProductListResponse,CategoryCreate
)
from app.database import get_db
from app.utils.auth import get_current_user
from typing import List
from app.Schemas.productSchema import BulkProductCreate, BulkProductResponse

from app.Schemas.productSchema import BulkProductCreate, BulkProductResponse, ProductCreateBulk

router = APIRouter(prefix="/products", tags=["products"])

# ==================== CATEGORY ENDPOINTS ====================

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    """Create a new category"""
    existing_category = db.query(Category).filter(Category.category_name == category.category_name).first()
    if existing_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists")
    
    db_category = Category(category_name=category.category_name)
    
    try:
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category could not be created")

@router.get("/categories", response_model=list[CategoryResponse])
def get_all_categories(db: Session = Depends(get_db)):
    """Get all categories"""
    categories = db.query(Category).all()
    return categories

# ==================== PRODUCT ENDPOINTS ====================

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product: ProductCreate, 
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """Add a new product (authentication required)"""
    # Verify category exists
    category = db.query(Category).filter(Category.category_id == product.category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    # Check if product with same name exists
    existing_product = db.query(Product).filter(Product.product_name == product.product_name).first()
    if existing_product:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product with this name already exists")
    
    db_product = Product(
        product_name=product.product_name,
        description=product.description,
        price=product.price,
        quantity=product.quantity,
        category_id=product.category_id
    )
    
    try:
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product could not be created")

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    """Get a single product by ID"""
    product = db.query(Product).filter(Product.product_id == product_id).first()
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product

@router.get("/category/{category_id}/products", response_model=ProductListResponse)
def get_products_by_category(
    category_id: UUID,
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    db: Session = Depends(get_db)
):
    """Get all products for a specific category with pagination"""
    # Verify category exists
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    # Get products for the category with pagination
    query = db.query(Product).filter(Product.category_id == category_id)
    total = query.count()
    products = query.offset(skip).limit(limit).all()
    
    # Calculate total pages
    pages = (total + limit - 1) // limit if total > 0 else 0
    
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=len(products),
        pages=pages
    )
    




@router.post("/category/{category_id}/bulk-products", response_model=BulkProductResponse, status_code=status.HTTP_201_CREATED)
def add_bulk_products_by_category(
    category_id: UUID,
    products_data: BulkProductCreate,
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user)
):
    """
    Add multiple products to a specific category at once
    """
    # Verify category exists
    category = db.query(Category).filter(Category.category_id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    
    added_products = []
    errors = []
    
    for product_data in products_data.products:
        # Check if product with same name exists
        existing_product = db.query(Product).filter(Product.product_name == product_data.product_name).first()
        if existing_product:
            errors.append(f"Product '{product_data.product_name}' already exists - skipped")
            continue
        
        # Create product with the category_id from URL
        db_product = Product(
            product_name=product_data.product_name,
            description=product_data.description,
            price=product_data.price,
            quantity=product_data.quantity,
            category_id=category_id  # Use the category_id from URL
        )
        
        try:
            db.add(db_product)
            db.commit()
            db.refresh(db_product)
            added_products.append(db_product)
        except IntegrityError as e:
            db.rollback()
            errors.append(f"Failed to add '{product_data.product_name}': {str(e)}")
    
    return BulkProductResponse(
        message=f"Successfully added {len(added_products)} products to {category.category_name} category",
        total_added=len(added_products),
        products=added_products,
        failed_count=len(errors),
        errors=errors if errors else None
    )
    
    
@router.get("/", response_model=ProductListResponse)
def get_all_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of products to return"),
    search: Optional[str] = Query(None, description="Search by product name"),
    db: Session = Depends(get_db)
):
    """Get all products with pagination"""
    query = db.query(Product)
    
    # Apply search filter if provided
    if search:
        query = query.filter(Product.product_name.ilike(f"%{search}%"))
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    products = query.offset(skip).limit(limit).all()
    
    # Calculate total pages
    pages = (total + limit - 1) // limit if total > 0 else 0
    
    return ProductListResponse(
        items=products,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        size=len(products),
        pages=pages
    )