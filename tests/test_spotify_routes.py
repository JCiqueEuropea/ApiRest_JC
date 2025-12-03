from unittest.mock import patch

from app.errors import AuthenticationError, EntityNotFoundError
from app.models import SpotifyArtist, SpotifyTrack

MOCK_ARTIST = SpotifyArtist(
    id="123", name="Mock Band", href="http://api/1", uri="spotify:artist:1"
)
MOCK_TRACK = SpotifyTrack(
    id="456", name="Mock Song", duration_ms=3000, explicit=False,
    album_name="Mock Album", href="http://api/t", uri="spotify:track:1"
)


class TestSpotifyIntegration:

    @patch("app.services.SpotifyService.process_auth_callback")
    def test_spotify_callback_success(self, mock_process, client):
        mock_process.return_value = True

        response = client.get("/users/auth/callback?code=fake_code&state=1")

        assert response.status_code == 200
        assert response.json()["message"] == "Spotify Connected!"
        mock_process.assert_called_once_with("fake_code", 1)

    def test_spotify_callback_missing_params(self, client):
        response = client.get("/users/auth/callback?code=only_code")
        assert response.status_code == 400
        assert "Missing code or state" in response.json()["detail"]

    @patch("app.services.SpotifyService.find_artist_to_save")
    def test_add_favorite_artist_success(self, mock_find, client, created_user):
        user_id = created_user["id"]
        mock_find.return_value = MOCK_ARTIST

        response = client.post(f"/users/{user_id}/favorites/artists?artist_name=Band")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Mock Band"
        assert data["id"] == "123"

        user_resp = client.get(f"/users/{user_id}")
        assert len(user_resp.json()["favorite_artists"]) == 1

    @patch("app.services.SpotifyService.find_artist_to_save")
    def test_add_favorite_artist_no_token(self, mock_find, client, created_user):
        user_id = created_user["id"]
        mock_find.side_effect = AuthenticationError("Token expired")

        response = client.post(f"/users/{user_id}/favorites/artists?artist_name=Band")

        assert response.status_code == 401
        assert response.json()["error"] == "Unauthorized"

    @patch("app.services.SpotifyService.find_artist_to_save")
    def test_add_favorite_artist_not_found(self, mock_find, client, created_user):
        user_id = created_user["id"]
        mock_find.side_effect = EntityNotFoundError("SpotifyArtist", "UnknownBand")

        response = client.post(f"/users/{user_id}/favorites/artists?artist_name=UnknownBand")

        assert response.status_code == 404
        assert response.json()["error"] == "Not Found"

    @patch("app.services.SpotifyService.follow_targets")
    def test_follow_artist_endpoint(self, mock_follow, client, created_user):
        user_id = created_user["id"]
        mock_follow.return_value = True

        payload = ["id1", "id2"]
        response = client.put(
            f"/spotify/me/following?user_id={user_id}&type=artist",
            json=payload
        )

        assert response.status_code == 200
        mock_follow.assert_called_once()
