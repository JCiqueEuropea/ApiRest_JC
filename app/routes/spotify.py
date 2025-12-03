from typing import List, Literal

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import RedirectResponse

from app.services import UserService, SpotifyService

router = APIRouter(prefix="/spotify", tags=["Spotify"])


@router.get("/auth/{user_id}/login")
async def login_spotify(user_id: int):
    user = UserService.get_user(user_id)
    if not user:
        raise HTTPException(404, "User not found")

    url = SpotifyService.get_login_url(user_id)
    return RedirectResponse(url)


@router.get("/search/artist")
async def search_artist(user_id: int, q: str):
    data = await SpotifyService.search_artists_raw(user_id, q)
    if "error" in data:
        raise HTTPException(400 if data["error"] != "no_valid_token" else 401, detail=data)
    return data


@router.get("/search/track")
async def search_track(user_id: int, q: str):
    data = await SpotifyService.search_tracks_raw(user_id, q)
    if "error" in data:
        raise HTTPException(400 if data["error"] != "no_valid_token" else 401, detail=data)
    return data


@router.put("/me/following")
async def follow_artists_or_users(
        user_id: int,
        ids: List[str] = Body(..., description="List of Spotify IDs"),
        target_type: Literal["artist", "user"] = Query(..., alias="type", description="Type of entity to follow")
):
    try:
        await SpotifyService.follow_targets(user_id, ids, target_type)
        return {"message": f"Successfully followed {len(ids)} {target_type}(s)"}
    except ValueError as e:
        if str(e) == "no_valid_token":
            raise HTTPException(401, "User not authenticated with Spotify (Requires new login for scope update)")
        raise HTTPException(400, str(e))
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/me/following/artists")
async def get_followed_artists(user_id: int):
    try:
        artists = await SpotifyService.get_my_followed_artists(user_id)
        return {"count": len(artists), "items": artists}
    except ValueError as e:
        if str(e) == "no_valid_token":
            raise HTTPException(401, "User not authenticated with Spotify")
        raise HTTPException(400, str(e))


@router.get("/me/following/contains")
async def check_following(
        user_id: int,
        ids: str = Query(..., description="IDs separated by comma (ex: id1,id2)"),
        target_type: Literal["artist", "user"] = Query(..., alias="type", description="Entity type")
):
    id_list = [item_id.strip() for item_id in ids.split(",")]

    try:
        results = await SpotifyService.check_if_following(user_id, id_list, target_type)
        response = []
        for spotify_id, is_following in zip(id_list, results):
            response.append({"id": spotify_id, "is_following": is_following})
        return response
    except ValueError as e:
        if str(e) == "no_valid_token":
            raise HTTPException(401, "User not authenticated with Spotify")
        raise HTTPException(400, str(e))
