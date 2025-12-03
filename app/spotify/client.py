import httpx
from app.database import token_store
from app.spotify.auth import refresh_token_with_refresh_token
from typing import Optional, Dict, Any, List

API_BASE = "https://api.spotify.com/v1"


async def _ensure_valid_token_for_user(local_user_id: int) -> Optional[str]:
    token = token_store.get(local_user_id)
    if token is None:
        return None

    if token.is_expired():
        if not token.refresh_token:
            return None
        print(f"Refreshing token for user {local_user_id}")
        refreshed = await refresh_token_with_refresh_token(token.refresh_token)
        if refreshed is None:
            return None
        token_store[local_user_id] = refreshed
        return refreshed.access_token

    return token.access_token


async def _spotify_get(access_token: str, path: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    url = f"{API_BASE}{path}"
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, headers=headers, params=params)
        if resp.status_code == 401:
            return {"error": "token_expired_or_invalid"}
        resp.raise_for_status()
        return resp.json()


async def search_artist(local_user_id: int, q: str, limit: int = 5) -> Dict[str, Any]:
    token = await _ensure_valid_token_for_user(local_user_id)
    if not token:
        return {"error": "no_valid_token"}
    return await _spotify_get(token, "/search", params={"q": q, "type": "artist", "limit": str(limit)})


async def search_track(local_user_id: int, q: str, limit: int = 5) -> Dict[str, Any]:
    token = await _ensure_valid_token_for_user(local_user_id)
    if not token:
        return {"error": "no_valid_token"}
    return await _spotify_get(token, "/search", params={"q": q, "type": "track", "limit": str(limit)})


async def _spotify_put(access_token: str, path: str, params: Optional[Dict[str, str]] = None,
                       json_body: Any = None) -> bool:
    url = f"{API_BASE}{path}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.put(url, headers=headers, params=params, json=json_body)
        if resp.status_code == 401:
            return False
        if resp.status_code not in [200, 204]:
            print(f"Error PUT Spotify: {resp.text}")
            resp.raise_for_status()
        return True


async def follow_ids(local_user_id: int, ids: List[str], type_: str) -> Dict[str, Any]:
    token = await _ensure_valid_token_for_user(local_user_id)
    if not token: return {"error": "no_valid_token"}

    params = {"type": type_}  # 'artist' o 'user'
    body = {"ids": ids}

    try:
        await _spotify_put(token, "/me/following", params=params, json_body=body)
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}


async def get_followed_artists(local_user_id: int, limit: int = 20) -> Dict[str, Any]:
    token = await _ensure_valid_token_for_user(local_user_id)
    if not token: return {"error": "no_valid_token"}

    params = {"type": "artist", "limit": str(limit)}
    return await _spotify_get(token, "/me/following", params=params)


async def check_following_status(local_user_id: int, ids: List[str], type_: str) -> Dict[str, Any]:
    token = await _ensure_valid_token_for_user(local_user_id)
    if not token: return {"error": "no_valid_token"}

    ids_str = ",".join(ids)
    params = {"type": type_, "ids": ids_str}

    return await _spotify_get(token, "/me/following/contains", params=params)
