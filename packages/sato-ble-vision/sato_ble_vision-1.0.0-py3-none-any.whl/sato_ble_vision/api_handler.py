import requests
import time
from .config import AUTH_URL, RESOLVE_URL,AUTHORIZATION_HEADER_VALUE  # Ensure these are defined in your config

# Global variables to store the access token and its expiration time.
ACCESS_TOKEN = None
TOKEN_EXPIRATION = 0 


def get_auth_token():
    from .config import AUTH_URL, RESOLVE_URL,AUTHORIZATION_HEADER_VALUE
    """
    Sends a POST request to the authentication endpoint using the provided
    Authorization header, and retrieves a new access token.
    Adjust the payload as needed if your endpoint requires additional data.
    """
    global ACCESS_TOKEN, TOKEN_EXPIRATION
    headers = {
        "Authorization": AUTHORIZATION_HEADER_VALUE,
        "Content-Type": "application/json"
    }
    
    try:
        # The payload here may be empty if your endpoint just reads the header.
        response = requests.post(AUTH_URL, headers=headers, json={})
        response.raise_for_status()
        data = response.json()
        
        # Check for 'access_token' in the response.
        if "access_token" in data:
            ACCESS_TOKEN = data["access_token"]
            # Set token lifetime to 15 minutes (900 seconds). Adjust if needed.
            TOKEN_EXPIRATION = time.time() + 900
            print("New authentication token acquired.")
            return ACCESS_TOKEN
        else:
            print("Authentication failed: No access token received.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Authentication Error: {e}")
        return None

def get_valid_token():
    """
    Checks if the stored access token is present and unexpired.
    If not, it calls get_auth_token() to get a new one.
    """
    global ACCESS_TOKEN, TOKEN_EXPIRATION
    if ACCESS_TOKEN is None or time.time() >= TOKEN_EXPIRATION:
        print("Token expired or missing, requesting a new one...")
        return get_auth_token()
    return ACCESS_TOKEN

def get_tag_id(payload):
    from .config import RESOLVE_URL
    """
    Sends a POST request to the tag retrieval (Resolve) endpoint using the valid access token.
    Extracts the tag ID from the 'externalId' field inside the 'data' list.
    """
    token = get_valid_token()
    if not token:
        print("Cannot get tag id: Authentication failed.")
        return None

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(RESOLVE_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print(f"Tag id response: {response_data}")

        # Updated logic to extract tag ID from nested structure
        if "data" in response_data and isinstance(response_data["data"], list) and response_data["data"]:
            tag_id = response_data["data"][0].get("externalId")
            if tag_id:
                return tag_id
            else:
                print("Tag id (externalId) is missing in the data.")
                return None
        else:
            print("No valid data in response.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving tag id: {e}")
        return None

    try:
        response = requests.post(RESOLVE_URL, json=payload, headers=headers)
        response.raise_for_status()
        response_data = response.json()
        print(f"Tag id response: {response_data}")
        if "tag_id" in response_data:
            return response_data["tag_id"]
        else:
            print("Tag id not found in response.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving tag id: {e}")
        return None

def send_to_resolve_api(payload):
    """
    This function ensures that a valid authentication token is available and then
    sends a POST request to the Resolve API to retrieve the tag id.
    Returns the tag id if successful, or None otherwise.
    """
    tag_id = get_tag_id(payload)
    if tag_id:
        print(f"Successfully retrieved tag id: {tag_id}")
        return tag_id
    else:
        print("Failed to retrieve tag id.")
        return None
