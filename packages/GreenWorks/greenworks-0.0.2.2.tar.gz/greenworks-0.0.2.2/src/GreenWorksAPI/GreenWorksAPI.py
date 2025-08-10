# GreenWorks-Core/Main.py
from dataclasses import dataclass
from zoneinfo import ZoneInfo
from datetime import datetime
import time
import requests
import json
from .Records import Login_object, Mower_operating_status, User_info_object, Mower_properties
from .Enums import MowerState



@dataclass
class Mower:
    id: int
    name: str
    sn: str
    is_online: bool
    properties: Mower_properties
    operating_status: Mower_operating_status
    model: str = "Greenworks Mower"  # Default model name, can be overridden

class GreenWorksAPI:
    """Greenworks - API Wrapper for Greenworks robotic lawn mower."""
    base_url = "https://xapi.globetools.systems/v2/"

    def __init__(self, email: str, password: str, timezone: str):
        """Initialize the GreenWorks class with user credentials."""
        self.login_info = self._login_user(email, password)
        self.user_info = self._get_user_info()
        self.UserTimezone = ZoneInfo(timezone)

    def _login_user(self, email: str, password: str):
        try:
            print(f"Logging in with email: {email}")  # Debugging output
            # Send POST request to the API
            url = f"{self.base_url}user_auth"
            body = {
                "corp_id": "100fa2b00b622800",
                "email": email,
                "password": password,
            }
            response = requests.post(url, json=body, timeout=10)
            data = response.json()

            data["expire_in"] = time.time() + data["expire_in"] - 300  # Set expiration time for access token

            # Eventuelt check for nødvendige felter
            if "user_id" not in data or "access_token" not in data:
                raise ValueError("Login-svar mangler nødvendige felter: 'user_id' og/eller 'access_token'")

            return Login_object(**data)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise RuntimeError(f"Fejl ved login: {e}") from e

    def _get_user_info(self) -> User_info_object:
        try:
            response = self.__request(f"user/{self.login_info.user_id}")
            data = response.json()

            return User_info_object(**data)

        except Exception as e:
            raise RuntimeError(f"Fejl") from e

    def _get_mower_operating_status(self, product_id: int, mower_id: int) -> Mower_operating_status:
        try:
            endpoint = f"product/{product_id}/v_device/{mower_id}"
            response = self.__request(endpoint, params={"datapoints": "32"})
            response.raise_for_status()  # Stopper ved 4xx/5xx


            # Feltet "32" er en streng med JSON-indhold
            raw_32 = response.json().get("32", "{}")
            parsed_32 = json.loads(raw_32)
            data = parsed_32.get("request", {})

            return Mower_operating_status(
                battery_status=data.get("battery_status", -1),
                mower_main_state=MowerState(data.get("mower_main_state", -1)),
                next_start=datetime.fromtimestamp(data.get("next_start", ""), tz=self.UserTimezone),
                request_time=datetime.fromisoformat(data.get("request_time", "").replace("Z", "+00:00")).astimezone(self.UserTimezone)
            )
        except Exception as e:
            print(f"An error occurred: {e}")
            raise RuntimeError(f"Fejl ved hentning af plæneklipperens driftsstatus: {e}") from e

    def _get_device_properties(self, product_id: int, device_id: int) -> Mower_properties:
        endpoint = f"product/{product_id}/device/{device_id}/property"

        try:
            response = self.__request(endpoint)
            response.raise_for_status()  
            
            data = response.json()
            return Mower_properties(**data) 

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {self.base_url}{endpoint}: {e}") from e

    def refresh_access_token(self):
        print(f"Refreshing access token")
        url = f"{self.base_url}user/token/refresh"
        body = {
            "refresh_token": self.login_info.refresh_token,
        }
        headers = {
            "Access-Token": self.login_info.access_token
        }
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            response.raise_for_status()  
            data = response.json()
            self.login_info.access_token = data.get("access_token")
            self.login_info.refresh_token = data.get("refresh_token")
            self.login_info.expire_in = int(time.time() + 3500)

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {url}: {e}") from e

    def get_devices(self) -> list[Mower]:
        Mowers: list[Mower] = []
        try:
            endpoint = f"user/{self.login_info.user_id}/subscribe/devices?version=0"
            response = self.__request(endpoint)
            response.raise_for_status()  # Stopper hvis status != 2xx

            data = response.json()

            # Tjek at 'list' findes i JSON og er en liste
            devices = data.get("list")
            if not isinstance(devices, list):
                raise ValueError("JSON-svar indeholder ikke en gyldig 'list' af enheder")
            
            # Returner en liste af Mower objekter
            for device in devices:
                mower_properties = self._get_device_properties(device.get("product_id"), device.get("id"))
                if mower_properties is None:
                    raise ValueError(f"Kunne ikke hente egenskaber for enhed med ID {device.get('id')}")
                mower_operating_status = self._get_mower_operating_status(device.get("product_id"), device.get("id"))
                if mower_operating_status is None:
                    raise ValueError(f"Kunne ikke hente tilstand for enhed med ID {device.get('id')}")
                # Opret Mower objekt med de hentede data
                mower = Mower(
                    id=device.get("id"),
                    name=device.get("name"),
                    sn=device.get("sn"),
                    is_online=device.get("is_online"),
                    properties=mower_properties,
                    operating_status=mower_operating_status
                )
                # Tilføj Mower objektet til listen
                Mowers.append(mower)

            return Mowers  # Returner listen af Mower objekter
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

    def pause_mower(self, mower_id: int, duration: int = 0):
        """
        Placeholder for a method to pause the mower.
        This method should implement the logic to pause the mower.
        """
        # Implement logic to pause the mower
        pass

    def unpause_mower(self, mower_id: int):
        """
        Placeholder for a method to unpause the mower.
        This method should implement the logic to unpause the mower.
        """
        # Implement logic to unpause the mower
        pass

    def dock_mower(self, mower_id: int):

        """
        Placeholder for a method to dock the mower.
        This method should implement the logic to dock the mower.
        """
        # Implement logic to dock the mower
        pass

    def cancel_docking(self, mower_id: int):
        """
        Placeholder for a method to cancel docking of the mower.
        This method should implement the logic to cancel docking of the mower.
        """
        # Implement logic to cancel docking of the mower
        pass

    # private method for requesting data from api
    def __request(self, endpoint:str, params={}, body={}):
        if time.time() > self.login_info.expire_in:
            self.refresh_access_token()
        try:
            url = f"{self.base_url}{endpoint}"
            header = {'Content-Type':'application/json', "Access-Token": self.login_info.access_token}
            #print(f"Request URL: {url}")  # Debugging output
            #print(f"Request Headers: {header}")  # Debugging output
            
            
            response = requests.get(url,json=body, headers=header,params=params,timeout=10)
            #print(f"Response: {response.json()}")  # Debugging output

            response.raise_for_status()  # Kaster exception på 4xx/5xx
            return response
    
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Fejl under API-kald til {self.base_url}{endpoint}: {e}, {response.text}, {response.status_code}, {response.headers}, {e.args}") from e

        except ValueError as e:
            raise RuntimeError(f"Ugyldigt JSON-svar fra {self.base_url}{endpoint}: {e}") from e

        except TypeError as e:
            raise RuntimeError(f"Fejl ved oprettelse af mower_info_object: {e}") from e
        



        

class UnauthorizedException(Exception):
    pass