from typing import List, Optional
from pydantic import BaseModel, Field


class OssConfig(BaseModel):
    access_key_id: str
    access_key_secret: str
    bucket_name: str
    endpoint: str
    endpoint_public: str
    cdn_host: str
    prefix: str


class Config(BaseModel):
    max_img_width: Optional[int] = Field(description="maximum image with in px", default=None)
    disable_image: Optional[bool] = Field(description="disable image extraction", default=False)
    disable_color: Optional[bool] = Field(
        description="prevent adding html tags with colors", default=False
    )
    disable_escaping: Optional[bool] = Field(
        description="prevent escaping of characters", default=False
    )
    disable_notes: Optional[bool] = Field(description="do not add presenter notes", default=False)
    enable_slides: Optional[bool] = Field(description="add slide deliniation", default=True)
    upload_image: Optional[bool] = Field(description="upload image, need oss config", default=True)
    oss_config: Optional[OssConfig] | None = Field(description="add oss config", default=None)
    
    allow_image_format: Optional[List[str]] = Field(description='support image type', default=None)
    min_image_width: Optional[int] = Field(description='drop if image width less this value', default=None)
    min_image_height: Optional[int] = Field(description='drop if image height less this value', default=None)
    skip_duplicate_image: Optional[bool] = Field(description="drop image if duplicate in same card", default=True)
