from pydantic.main import BaseModel


class UserDetails(BaseModel):
    id: str
    firstname: str
    lastname: str


class DataResponse(BaseModel):
    user_details: UserDetails
