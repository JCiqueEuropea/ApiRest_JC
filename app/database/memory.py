from typing import List, Dict

from app.models import User, SpotifyToken

fake_db: List[User] = []
token_store: Dict[int, SpotifyToken] = {}
