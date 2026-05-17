from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, field_validator

class ORMBase(BaseModel):
    id: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("*")
    @classmethod
    def val_dates(cls, obj):
        if (isinstance(obj, date)):
            return datetime.strftime(obj, '%Y-%m-%d')
        else: return obj