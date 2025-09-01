from datetime import datetime
from typing import Annotated
from pydantic import AfterValidator, BaseModel, ConfigDict, field_validator, model_validator, validator


def author_must_start_with_uppercase(value: int) -> int:
    if value[0].islower():
        raise ValueError(f'Author name must start with uppercase letter, is: {value}')
    return value  


def not_empty(value: str) -> str:
    if not value.strip():
        raise ValueError("String must not be empty")

    return value


type NonEmptyString = Annotated[str, AfterValidator(not_empty)]
type AuthorNameContrains = Annotated[str, AfterValidator(author_must_start_with_uppercase)]


class PostCreate(BaseModel):
    title: NonEmptyString
    content: NonEmptyString
    author: AuthorNameContrains


class PostRead(BaseModel):
    id: int
    title: str
    content: str
    author: str
    created_at: datetime
    edited_at: datetime


class PostUpdate(BaseModel):
    title: NonEmptyString
    content: NonEmptyString
    author: AuthorNameContrains

