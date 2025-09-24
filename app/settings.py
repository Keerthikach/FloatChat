from pydantic import BaseModel, Field
import os

class Settings(BaseModel):
    api_key: str = Field(default=os.getenv("API_KEY", "dev-key"))
    allowed_variables: list[str] = ["temperature", "salinity", "oxygen", "chlorophyll", "nitrate"]
    max_bbox_area_deg2: float = 2000.0
    max_date_years: int = 5

settings = Settings()
