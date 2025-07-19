from pydantic import BaseModel, Field, field_validator, EmailStr

from app.config import DefaultSettings


class RegistrationForm(BaseModel):
    email: EmailStr = Field(examples=["your_email@domen.com"])
    username: str
    password: str = Field(examples=["your_password"], min_length=8)

    name: str
    age: int
    about: str
    hobby: str
    goals: int
    person_type: int

    @field_validator("password")
    def validate_password(cls, password):
        password = DefaultSettings().PWD_CONTEXT.hash(password)
        return password
