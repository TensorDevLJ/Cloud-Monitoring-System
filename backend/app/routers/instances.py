"""
Instance management routes
"""
# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
# pyrefly: ignore [missing-import]
from app import models, schemas, auth

router = APIRouter(prefix="/instances", tags=["Instances"])


@router.get("/", response_model=List[schemas.Instance])
async def list_instances(
    skip: int = 0,
    limit: int = 100,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """List all instances"""
    # Just list all instances for now, or filter by user if not admin
    if not current_user or not current_user.is_admin:
        instances = await models.Instance.find_all().skip(skip).limit(limit).to_list()
    else:
        instances = await models.Instance.find_all().skip(skip).limit(limit).to_list()
    
    # Add id string mapping to schema compat
    for i in instances:
        i.id = str(i.id)
    return instances


@router.get("/{instance_id}", response_model=schemas.Instance)
async def get_instance(
    instance_id: str,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Get instance by ID"""
    instance = await models.Instance.find_one(models.Instance.instance_id == instance_id)
    if not instance:
        # Fallback to mongodb _id if valid
        try:
            # pyrefly: ignore [missing-import]
            from bson import ObjectId
            if ObjectId.is_valid(instance_id):
                instance = await models.Instance.get(instance_id)
        except Exception:
            pass
        
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Check permissions (only if authenticated)
    if current_user and not current_user.is_admin and instance.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    instance.id = str(instance.id)
    return instance


@router.post("/", response_model=schemas.Instance, status_code=status.HTTP_201_CREATED)
async def add_instance(
    instance: schemas.InstanceCreate,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Add a new instance"""
    # Check if instance already exists
    existing = await models.Instance.find_one(
        models.Instance.instance_id == instance.instance_id
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instance ID already exists"
        )
    
    # Create new instance
    db_instance = models.Instance(
        **instance.dict(),
        owner_id=str(current_user.id),
        status="active"
    )
    
    await db_instance.insert()
    db_instance.id = str(db_instance.id)
    return db_instance


@router.put("/{instance_id}", response_model=schemas.Instance)
async def update_instance(
    instance_id: str,
    instance_update: schemas.InstanceUpdate,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Update an instance"""
    instance = await models.Instance.find_one(models.Instance.instance_id == instance_id)
    if not instance:
        try:
            # pyrefly: ignore [missing-import]
            from bson import ObjectId
            if ObjectId.is_valid(instance_id):
                instance = await models.Instance.get(instance_id)
        except Exception:
            pass
        
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Check permissions
    if not current_user.is_admin and instance.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields
    update_data = instance_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(instance, field, value)
    
    await instance.save()
    instance.id = str(instance.id)
    return instance


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(
    instance_id: str,
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Delete an instance"""
    instance = await models.Instance.find_one(models.Instance.instance_id == instance_id)
    if not instance:
        try:
            # pyrefly: ignore [missing-import]
            from bson import ObjectId
            if ObjectId.is_valid(instance_id):
                instance = await models.Instance.get(instance_id)
        except Exception:
            pass
        
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Check permissions
    if not current_user.is_admin and instance.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await instance.delete()
    return None


@router.get("/{instance_id}/alerts", response_model=List[schemas.Alert])
async def get_instance_alerts(
    instance_id: str,
    active_only: bool = True,
    current_user: Optional[models.User] = Depends(auth.get_optional_current_user)
):
    """Get alerts for an instance"""
    instance = await models.Instance.find_one(models.Instance.instance_id == instance_id)
    if not instance:
        try:
            # pyrefly: ignore [missing-import]
            from bson import ObjectId
            if ObjectId.is_valid(instance_id):
                instance = await models.Instance.get(instance_id)
        except Exception:
            pass
        
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    
    # Check permissions (only if authenticated)
    if current_user and not current_user.is_admin and instance.owner_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    query = models.Alert.find(models.Alert.instance_id == str(instance.id))
    
    if active_only:
        query = query.find(models.Alert.status == "active")
    
    alerts = await query.sort(-models.Alert.triggered_at).to_list()
    
    for a in alerts:
        a.id = str(a.id)
        
    return alerts
