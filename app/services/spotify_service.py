from typing import Dict, Any, List

from app.database.memory import token_store
from app.errors import AuthenticationError, ExternalAPIError, EntityNotFoundError
from app.models import SpotifyArtist, SpotifyTrack
from app.spotify import auth, client


class SpotifyService:
    @staticmethod
    def get_login_url(user_id: int) -> str:
        return auth.build_authorize_url(user_id)

    @staticmethod
    async def process_auth_callback(code: str, user_id: int) -> bool:
        token = await auth.exchange_code_for_token(code)
        if not token:
            return False
        token_store[user_id] = token
        return True

    @staticmethod
    def _handle_client_response(data: Dict[str, Any], context: str):
        if "error" in data:
            error_val = data["error"]
            if error_val == "no_valid_token":
                raise AuthenticationError("User session with Spotify expired or invalid. Please login again.")

            msg = error_val
            if isinstance(error_val, dict):
                msg = error_val.get("message", str(error_val))

            raise ExternalAPIError("Spotify", f"{context}: {msg}")
        return data

    @staticmethod
    async def find_artist_to_save(user_id: int, query: str) -> SpotifyArtist:
        data = await client.search_artist(user_id, query, limit=1)
        SpotifyService._handle_client_response(data, "Search Artist")

        items = data.get("artists", {}).get("items", [])
        if not items:
            raise EntityNotFoundError("SpotifyArtist", query)

        raw = items[0]
        return SpotifyArtist(
            id=raw["id"],
            name=raw["name"],
            popularity=raw.get("popularity"),
            genres=raw.get("genres", []),
            href=raw["href"],
            uri=raw["uri"]
        )

    @staticmethod
    async def find_track_to_save(user_id: int, query: str) -> SpotifyTrack:
        data = await client.search_track(user_id, query, limit=1)
        SpotifyService._handle_client_response(data, "Search Track")

        items = data.get("tracks", {}).get("items", [])
        if not items:
            raise EntityNotFoundError("SpotifyTrack", query)

        raw = items[0]
        artists_list = [
            SpotifyArtist(id=a["id"], name=a["name"], href=a["href"], uri=a["uri"])
            for a in raw["artists"]
        ]

        return SpotifyTrack(
            id=raw["id"],
            name=raw["name"],
            popularity=raw.get("popularity"),
            duration_ms=raw["duration_ms"],
            explicit=raw["explicit"],
            artists=artists_list,
            album_name=raw["album"]["name"],
            href=raw["href"],
            uri=raw["uri"]
        )

    @staticmethod
    async def search_artists_raw(user_id: int, q: str):
        return await client.search_artist(user_id, q, limit=10)

    @staticmethod
    async def search_tracks_raw(user_id: int, q: str):
        return await client.search_track(user_id, q, limit=10)

    @staticmethod
    async def follow_targets(user_id: int, ids: List[str], target_type: str) -> bool:
        if target_type not in ["artist", "user"]:
            raise ValueError("Type must be 'artist' or 'user'")

        result = await client.follow_ids(user_id, ids, target_type)
        if "error" in result:
            if result["error"] == "no_valid_token":
                raise ValueError("no_valid_token")
            raise Exception(result["error"])
        return True

    @staticmethod
    async def get_my_followed_artists(user_id: int) -> List[Dict[str, Any]]:
        data = await client.get_followed_artists(user_id)

        if "error" in data:
            if data["error"] == "no_valid_token":
                raise ValueError("no_valid_token")
            raise Exception(data.get("message", "Error getting followed artists"))

        return data.get("artists", {}).get("items", [])

    @staticmethod
    async def check_if_following(user_id: int, ids: List[str], target_type: str) -> dict[str, Any]:
        data = await client.check_following_status(user_id, ids, target_type)

        if isinstance(data, dict) and "error" in data:
            if data["error"] == "no_valid_token":
                raise ValueError("no_valid_token")
            raise Exception(data.get("message", "Error checking following status"))

        return data
