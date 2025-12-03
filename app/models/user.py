from typing import List

from pydantic import BaseModel, Field, field_validator

from .spotify import SpotifyArtist, SpotifyTrack


class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=250, description="Full name of the user")

    age: int = Field(..., gt=18, lt=120, description="User age, must be adult (+18)")

    music_preferences: List[str] = Field(default_factory=list, max_length=20, description="List of preferred genres")

    @field_validator('name')
    @classmethod
    def name_must_be_title_case(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('Name cannot be empty or whitespace')
        return v.title()

    @field_validator('music_preferences')
    @classmethod
    def validate_genres(cls, v: List[str]) -> List[str]:
        cleaned = [g.strip() for g in v if g.strip()]
        return cleaned


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    favorite_artists: List[SpotifyArtist] = Field(default_factory=list)
    favorite_tracks: List[SpotifyTrack] = Field(default_factory=list)
