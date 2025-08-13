from typing import Optional

from krutrim_client._models import BaseModel  


__all__ = ["BucketCreateResponse"]


class BucketCreateResponse(BaseModel):
    
    krn: Optional[str] = None
    bucketName: Optional[str] = None
    createdAt: Optional[str] = None
