from typing import List

from fastapi import APIRouter, status, Request, HTTPException
from fastapi.responses import JSONResponse

from app.models import User, UserCreate, SpotifyArtist, SpotifyTrack
from app.services import UserService, SpotifyService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=List[User])
async def list_users():
    return UserService.list_users()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
async def create_user(user_data: UserCreate):
    return UserService.create_user(user_data)


@router.get("/{user_id}", response_model=User)
async def get_user(user_id: int):
    return UserService.get_user(user_id)


@router.put("/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserCreate):
    return UserService.update_user(user_id, user_data)


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    UserService.delete_user(user_id)
    return {"message": "User deleted successfully"}


@router.get("/auth/callback")
async def spotify_callback(request: Request):
    code = request.query_params.get("code")
    error = request.query_params.get("error")
    state = request.query_params.get("state")

    if error:
        raise HTTPException(400, detail=f"Spotify Error: {error}")
    if not code or not state:
        raise HTTPException(400, detail="Missing code or state")

    try:
        user_id = int(state)
    except ValueError:
        raise HTTPException(400, "Invalid state (user_id)")

    success = await SpotifyService.process_auth_callback(code, user_id)
    if not success:
        raise HTTPException(500, "Authentication failed")

    return JSONResponse({"message": "Spotify Connected!", "user_id": user_id})


@router.post("/{user_id}/favorites/artists", response_model=SpotifyArtist)
async def add_favorite_artist(user_id: int, artist_name: str):
    user = UserService.get_user(user_id)
    if not user: raise HTTPException(404, "User not found")

    try:
        artist_obj = await SpotifyService.find_artist_to_save(user_id, artist_name)
    except ValueError as e:
        if str(e) == "no_valid_token":
            raise HTTPException(401, "User not logged in Spotify")
        raise HTTPException(500, str(e))

    if not artist_obj:
        raise HTTPException(404, "Artist not found on Spotify")

    if any(a.id == artist_obj.id for a in user.favorite_artists):
        return artist_obj

    user.favorite_artists.append(artist_obj)
    return artist_obj


@router.post("/{user_id}/favorites/tracks", response_model=SpotifyTrack)
async def add_favorite_track(user_id: int, track_name: str):
    user = UserService.get_user(user_id)
    if not user: raise HTTPException(404, "User not found")

    try:
        track_obj = await SpotifyService.find_track_to_save(user_id, track_name)
    except ValueError as e:
        if str(e) == "no_valid_token":
            raise HTTPException(401, "User not logged in Spotify")
        raise HTTPException(500, str(e))

    if not track_obj:
        raise HTTPException(404, "Track not found on Spotify")

    if any(t.id == track_obj.id for t in user.favorite_tracks):
        return track_obj

    user.favorite_tracks.append(track_obj)
    return track_obj
