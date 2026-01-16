from pydantic import BaseModel


class BuildingOut(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float

    class Config:
        from_attributes = True


class PhoneOut(BaseModel):
    id: int
    number: str

    class Config:
        from_attributes = True


class ActivityOut(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class OrganizationOut(BaseModel):
    id: int
    name: str
    building: BuildingOut
    phones: list[PhoneOut]
    activities: list[ActivityOut]

    class Config:
        from_attributes = True
