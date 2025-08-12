from pydantic.main import BaseModel


class UserDetails(BaseModel):
    firstname: str
    lastname: str


class DataResponse(BaseModel):
    user_details: UserDetails
