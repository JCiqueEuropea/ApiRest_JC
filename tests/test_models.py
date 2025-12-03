import pytest
from pydantic import ValidationError

from app.models.user import UserCreate


class TestUserModels:

    def test_valid_user_creation(self):
        user = UserCreate(name="  juan perez  ", age=20, music_preferences=["Rock"])
        assert user.name == "Juan Perez"
        assert user.age == 20

    def test_invalid_age_under_18(self):
        with pytest.raises(ValidationError) as exc:
            UserCreate(name="Kid", age=15)

        errors = exc.value.errors()
        assert errors[0]['type'] == 'greater_than'
        assert errors[0]['loc'] == ('age',)

    def test_invalid_name_empty(self):
        with pytest.raises(ValueError, match="Name cannot be empty"):
            UserCreate(name="   ", age=25)

    def test_clean_music_preferences(self):
        user = UserCreate(name="Test", age=25, music_preferences=["Rock", "", "  ", "Jazz"])
        assert len(user.music_preferences) == 2
        assert "Rock" in user.music_preferences
        assert "Jazz" in user.music_preferences
