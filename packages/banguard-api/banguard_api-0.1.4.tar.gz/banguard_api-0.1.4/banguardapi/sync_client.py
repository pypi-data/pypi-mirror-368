from typing import Optional, Union

import requests

from .ban import Ban
from .exceptions import *
from .terraria_player import TerrariaPlayer


class Client:
    BASE_URL = "https://banguard.uk/api/"

    def __init__(self, token: str, check_token: bool = True, timeout: int = 10):
        self._token = token
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"Authorization": self._token})

        if check_token and not self.is_token_valid():
            raise AuthenticationError("Invalid token provided.")

    def _request(self, method: str, endpoint: str, **kwargs):
        """Helper method to send requests and handle errors."""
        url = f"{self.BASE_URL}{endpoint}"

        try:
            response = self._session.request(method, url, timeout=self._timeout, **kwargs)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            status_code = response.status_code
            try:
                error_msg = response.json().get("error", str(e))
            except Exception:
                error_msg = str(e)

            if status_code == 400:
                raise BadRequestError(error_msg)
            elif status_code == 401:
                raise AuthenticationError(error_msg)
            elif status_code == 403:
                raise PermissionDeniedError(error_msg)
            elif status_code == 404:
                raise NotFoundError(error_msg)
            elif status_code == 429:
                raise RateLimitError(error_msg)
            elif 500 <= status_code < 600:
                raise ServerError(error_msg)
            else:
                raise APIError(error_msg)

        except requests.exceptions.RequestException as e:
            raise APIError(f"Network error: {e}")

        try:
            data = response.json()
        except ValueError:
            raise InvalidResponseError("Invalid JSON response from the server.")

        if isinstance(data, dict) and "error" in data:
            raise APIError(data["error"])

        return data

    def is_token_valid(self) -> bool:
        """Return True if the token is valid, False otherwise."""
        try:
            data = self._request("GET", "check-token")
        except AuthenticationError:
            return False
        return data.get("valid", False)

    def get_ban_count(self) -> int:
        """Fetch ban count from the BanGuard API"""
        data = self._request("GET", "ban-count")
        return data.get("ban_count", 0)

    def ban_player(self, player: TerrariaPlayer, category: str) -> Ban:
        """Ban a player"""
        data = {
            "player_uuid": player.terraria_uuid,
            "category": category,
        }
        response = self._request("POST", "ban-player", data=data)
        return Ban.from_dict(
            {**response["ban"], "player": player, "category": category, "server": response["server"]})

    def unban_player(self, ban: Union[Ban, str]) -> None:
        """Unban a player"""
        if isinstance(ban, str):
            data = {
                "ban_id": ban,
            }
        elif isinstance(ban, Ban):
            data = {
                "ban_id": ban.id,
            }
        else:
            raise TypeError("ban must be an instance of Ban or an integer representing the ban ID.")
        try:
            self._request("POST", "unban-player", data=data)
        except NotFoundError as e:
            raise PlayerNotFoundError(str(e)) from e

    def get_player(self, player_uuid: str) -> TerrariaPlayer:
        """Fetch a player from the API"""
        data = {
            "player_uuid": player_uuid,
        }
        try:
            response = self._request("POST", "get-player", data=data)
        except NotFoundError as e:
            raise PlayerNotFoundError(str(e)) from e
        return TerrariaPlayer.from_dict(response.get("player", {}))

    def get_player_bans(self, player: TerrariaPlayer, ip: Optional[str] = None, name: Optional[str] = None) -> list[
        Ban]:
        """Fetch all bans for a player"""
        data = {
            "player_uuid": player.terraria_uuid,
        }
        if ip:
            data["player_ip"] = ip
        if name:
            data["player_name"] = name

        response = self._request("POST", "check-player-ban", data=data)
        return [Ban.from_dict({**ban_data, "player": player}) for ban_data in response.get("bans", [])]

    def get_ban_categories(self) -> list:
        """Fetch the list of ban categories from the API"""
        return self._request("GET", "ban-category-list")["ban_categories"]
