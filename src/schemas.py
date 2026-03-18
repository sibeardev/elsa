from pydantic import BaseModel, ConfigDict


class BuildingOut(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float

    model_config = ConfigDict(from_attributes=True)


class PhoneOut(BaseModel):
    id: int
    number: str

    model_config = ConfigDict(from_attributes=True)


class ActivityOut(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class OrganizationOut(BaseModel):
    id: int
    name: str
    building: BuildingOut
    phones: list[PhoneOut]
    activities: list[ActivityOut]

    model_config = ConfigDict(from_attributes=True)
