import base64
import urllib.parse
from typing import Optional

import httpx

from app.models import SpotifyToken
from app.settings import get_settings

settings = get_settings()

AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"


def build_authorize_url(local_user_id: int) -> str:
    params = {
        "client_id": settings.spotify_client_id,
        "response_type": "code",
        "redirect_uri": settings.spotify_redirect_uri,
        "state": str(local_user_id),
        "scope": "user-read-private user-read-email user-follow-read user-follow-modify"
    }
    return f"{AUTH_URL}?{urllib.parse.urlencode(params)}"


def _get_auth_header():
    auth_str = f"{settings.spotify_client_id}:{settings.spotify_client_secret}"
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    return {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }


async def exchange_code_for_token(code: str) -> Optional[SpotifyToken]:
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.spotify_redirect_uri
        }
        try:
            resp = await client.post(TOKEN_URL, data=data, headers=_get_auth_header())
            if resp.status_code != 200:
                print(f"Auth Error: {resp.text}")
                return None
            return SpotifyToken(**resp.json())
        except Exception as e:
            print(f"Exception during token exchange: {e}")
            return None


async def refresh_token_with_refresh_token(refresh_token: str) -> Optional[SpotifyToken]:
    async with httpx.AsyncClient() as client:
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token
        }
        resp = await client.post(TOKEN_URL, data=data, headers=_get_auth_header())
        if resp.status_code != 200:
            return None

        token_data = resp.json()
        if "refresh_token" not in token_data:
            token_data["refresh_token"] = refresh_token

        return SpotifyToken(**token_data)
