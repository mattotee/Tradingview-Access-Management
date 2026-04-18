import os
import json
import platform
import requests
import config
import helper
from urllib3 import encode_multipart_formdata
from datetime import datetime, timezone


class TradingView:
    """
    Handles all communication with the TradingView internal API.
    Session cookie is cached locally in a JSON file so we don't
    re-authenticate on every request.
    """

    def __init__(self):
        self.sessionid = self._load_session()

        # Test if the cached session is still valid
        if not self._session_valid():
            print("[TV] Session invalid or expired - re-authenticating")
            self._authenticate()
        else:
            print("[TV] Session valid - reusing cached sessionid")

    # ─────────────────────────────────────────────
    # Session management
    # ─────────────────────────────────────────────

    def _load_session(self):
        """Load session cookie from local file cache."""
        try:
            if os.path.exists(config.SESSION_FILE):
                with open(config.SESSION_FILE, "r") as f:
                    data = json.load(f)
                    return data.get("sessionid", "")
        except Exception as e:
            print(f"[TV] Could not load session file: {e}")
        return ""

    def _save_session(self):
        """Save session cookie to local file cache."""
        try:
            os.makedirs(os.path.dirname(config.SESSION_FILE), exist_ok=True)
            with open(config.SESSION_FILE, "w") as f:
                json.dump({"sessionid": self.sessionid}, f)
            print("[TV] Session saved to file")
        except Exception as e:
            print(f"[TV] Could not save session file: {e}")

    def _session_valid(self):
        """Check if the cached session cookie is still valid."""
        if not self.sessionid:
            return False
        try:
            headers = {"cookie": "sessionid=" + self.sessionid}
            response = requests.get(config.TV_URLS["tvcoins"], headers=headers, timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"[TV] Session validation error: {e}")
            return False

    def _authenticate(self):
        """Log in to TradingView and cache the session cookie."""
        username = config.TV_USERNAME
        password = config.TV_PASSWORD

        if not username or not password:
            raise ValueError("[TV] TV_SERVICE_USERNAME or TV_SERVICE_PASSWORD not set in environment")

        payload = {"username": username, "password": password, "remember": "on"}
        body, content_type = encode_multipart_formdata(payload)

        user_agent = (
            "TWAPI/3.0 ("
            + platform.system()
            + "; "
            + platform.version()
            + "; "
            + platform.release()
            + ")"
        )

        headers = {
            "origin": "https://www.tradingview.com",
            "User-Agent": user_agent,
            "Content-Type": content_type,
            "referer": "https://www.tradingview.com",
        }

        response = requests.post(
            config.TV_URLS["signin"], data=body, headers=headers, timeout=15
        )

        if response.status_code != 200:
            raise Exception(f"[TV] Authentication failed - status {response.status_code}: {response.text}")

        cookies = response.cookies.get_dict()
        if "sessionid" not in cookies:
            raise Exception("[TV] Authentication failed - no sessionid in response cookies")

        self.sessionid = cookies["sessionid"]
        self._save_session()
        print("[TV] Authentication successful")

    def _auth_headers(self, content_type="application/x-www-form-urlencoded"):
        return {
            "origin": "https://www.tradingview.com",
            "Content-Type": content_type,
            "Cookie": "sessionid=" + self.sessionid,
        }

    # ─────────────────────────────────────────────
    # Core API methods
    # ─────────────────────────────────────────────

    def validate_username(self, username):
        """
        Check if a TradingView username exists.
        Returns dict with validUser (bool) and verifiedUsername (str).
        """
        try:
            response = requests.get(
                config.TV_URLS["username_hint"] + "?s=" + username,
                timeout=10,
            )
            users_list = response.json()
            for user in users_list:
                if user["username"].lower() == username.lower():
                    return {"valid": True, "username": user["username"]}
            return {"valid": False, "username": ""}
        except Exception as e:
            raise Exception(f"[TV] validate_username error: {e}")

    def get_access_details(self, username, pine_id):
        """
        Get current access details for a user on a specific script.
        Returns a dict with hasAccess, noExpiration, currentExpiration.
        """
        payload = {"pine_id": pine_id, "username": username}
        headers = self._auth_headers()

        response = requests.post(
            config.TV_URLS["list_users"] + "?limit=10&order_by=-created",
            headers=headers,
            data=payload,
            timeout=10,
        )
        response_json = response.json()
        users = response_json.get("results", [])

        has_access = False
        no_expiration = False
        expiration = str(datetime.now(timezone.utc))

        for user in users:
            if user["username"].lower() == username.lower():
                has_access = True
                str_expiration = user.get("expiration")
                if str_expiration is not None:
                    expiration = user["expiration"]
                else:
                    no_expiration = True

        return {
            "pine_id": pine_id,
            "username": username,
            "hasAccess": has_access,
            "noExpiration": no_expiration,
            "currentExpiration": expiration,
        }

    def add_access(self, access_details, extension_type, extension_length):
        """
        Grant or extend access for a user on a script.
        extension_type: "D", "W", "M", "Y", "L" (lifetime)
        extension_length: int
        """
        access_details["status"] = "not_applied"

        payload = {
            "pine_id": access_details["pine_id"],
            "username_recip": access_details["username"],
        }

        if extension_type.upper() == "L":
            # Lifetime - no expiration date in payload
            access_details["noExpiration"] = True
        else:
            expiration = helper.get_access_extension(
                access_details["currentExpiration"],
                extension_type,
                extension_length,
            )
            payload["expiration"] = expiration
            access_details["expiration"] = expiration

        # Use modify endpoint if user already has access, add endpoint if new
        endpoint = "modify_access" if access_details["hasAccess"] else "add_access"
        body, content_type = encode_multipart_formdata(payload)

        headers = self._auth_headers(content_type)
        response = requests.post(config.TV_URLS[endpoint], data=body, headers=headers, timeout=10)

        access_details["status"] = (
            "success" if response.status_code in (200, 201) else f"failure_{response.status_code}"
        )
        print(f"[TV] add_access {access_details['username']} on {access_details['pine_id']}: {access_details['status']}")
        return access_details

    def remove_access(self, access_details):
        """Revoke access for a user on a script."""
        payload = {
            "pine_id": access_details["pine_id"],
            "username_recip": access_details["username"],
        }
        body, content_type = encode_multipart_formdata(payload)
        headers = self._auth_headers(content_type)

        response = requests.post(config.TV_URLS["remove_access"], data=body, headers=headers, timeout=10)

        access_details["status"] = (
            "success" if response.status_code == 200 else f"failure_{response.status_code}"
        )
        print(f"[TV] remove_access {access_details['username']} on {access_details['pine_id']}: {access_details['status']}")
        return access_details
