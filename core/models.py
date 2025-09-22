import uuid
from django.db import models

class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamp fields.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Meta options for the BaseModel.
        """
        abstract = True