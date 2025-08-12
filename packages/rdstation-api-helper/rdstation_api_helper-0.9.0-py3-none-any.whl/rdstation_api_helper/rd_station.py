"""
RD Station API Helper
"""
import base64
import json
import logging
import os
import re
import requests
import time

from dotenv import load_dotenv
from rdstation_api_helper.utils import save_to_json_file, parallel_decorator
from typing import Optional, Any
from urllib.parse import unquote

load_dotenv()


class RDStationAPI:
    """Functions to query RD Station API endpoints"""

    def __init__(self):
        self.RD_CLIENT_ID = os.getenv("RDSTATION_CLIENT_ID")
        self.RD_CLIENT_SECRET = os.getenv("RDSTATION_CLIENT_SECRET")
        self.RD_REFRESH_TOKEN = os.getenv("RDSTATION_REFRESH_TOKEN")
        self.RD_API_TOKEN = self.get_access_token()

    def get_access_token(self) -> str:
        """
        Obtain a new access token from RD Station using the refresh token.

        Returns:
            str: The new access token.

        Raises:
            AuthenticationError: If authentication fails or the API returns an error.
            APIError: For other API-related errors.
        """
        import requests
        from .exceptions import AuthenticationError, APIError

        url = "https://api.rd.services/auth/token"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {
            "client_id": self.RD_CLIENT_ID,
            "client_secret": self.RD_CLIENT_SECRET,
            "refresh_token": self.RD_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(url, headers=headers, json=data)
        except requests.exceptions.RequestException as e:
            raise APIError("Failed to connect to RD Station API for token refresh.", original_error=e)

        if response.status_code == 200:
            token = response.json().get("access_token")
            if not token:
                raise AuthenticationError("No access_token found in RD Station API response.")
            return token

        elif response.status_code == 400:
            raise AuthenticationError(f"Authentication failed: {response.text}")

        else:
            raise APIError(f"Unexpected error from RD Station API: {response.status_code} - {response.text}")

    def get_segmentations(self, save_json_file: bool = False) -> list[dict[str, Any]]:

        logging.info("Fetching segmentations...")

        url = "https://api.rd.services/platform/segmentations"
        params = {"page": 1, "page_size": 100}
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        all_results = []

        while True:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                logging.info(f"Error: {response.status_code}")
                break

            data = response.json()
            segmentations = data.get("segmentations", [])
            num_items = len(segmentations)

            logging.info(f"Page {params['page']} - Found {num_items} items")

            # Add current page's data to the results
            all_results.extend(segmentations)

            params["page"] += 1  # Increment the page number

            if num_items < 100:  # Break if no items was less than a full page
                break

        logging.info(f"Fetched {len(all_results)} total items.")

        if save_json_file:
            save_to_json_file(all_results, "rd_segmentations.json")

        return all_results

    def get_segmentation_contacts(self, segmentation_list: list[dict[str, Any]],
                                  limit: int = 100, sleep_time: float = 0.6,
                                  save_json_file: bool = False) -> list[dict[str, Any]]:
        dict_count = 0
        dict_length = len(segmentation_list)

        all_results = []

        for item in segmentation_list:
            logging.info(f"Processing segmentation: {item['id']} - {item['name']}")

            dict_count += 1
            contact_count = 0

            segmentation_id = item["id"]
            segmentation_name = item["name"]

            url = f"https://api.rd.services/platform/segmentations/{segmentation_id}/contacts"
            params = {"page": 1, "page_size": limit, "order": "last_conversion_date"}
            headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

            while True:
                req = requests.Request("GET", url, headers=headers, params=params).prepare()
                logging.debug(f"Requesting: {req.url}")

                response = requests.get(url, headers=headers, params=params)

                if response.status_code != 200:
                    logging.info(f"Error: {response.status_code}")
                    break

                data = response.json()

                contacts = data.get("contacts", [])
                num_items = len(contacts)
                contact_count += num_items

                logging.info(
                    f"{dict_count}/{dict_length} - id: {segmentation_id}, p.{params['page']}, found {contact_count} items"  # noqa
                )

                # Append segmentation_id and segmentation_name to each contact
                for contact in contacts:
                    contact["segmentation_id"] = segmentation_id
                    contact["segmentation_name"] = segmentation_name

                # Add current page's data to the results
                all_results.extend(contacts)

                params["page"] += 1  # Increment the page number

                if num_items < limit:  # Break if no items was less than a full page
                    break

                # Sleep for 0.5 seconds to respect 2 requests per second
                time.sleep(sleep_time)

        logging.info(f"Fetched {len(all_results)} total items.")

        if save_json_file:
            save_to_json_file(all_results, "rd_segmentation_contacts.json")

        return all_results

    def get_contact_data(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """Fetch a single contact data with retry handling."""

        url = f"https://api.rd.services/platform/contacts/{uuid_value}"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        try:
            response = requests.get(url, headers=headers)

            return response.status_code, response.json()

        except requests.exceptions.RequestException as e:
            logging.info(f"Request failed for {uuid_value}: {e}.")
            raise

    @parallel_decorator(max_workers=3, sleep_time=20, key_parameter="uuid")
    def get_contact_data_parallel(self, uuid_value):
        return self.get_contact_data(uuid_value)

    def get_contact_events(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """Fetch a single contact conversion events and process traffic_source and UTM params."""

        url = f"https://api.rd.services/platform/contacts/{uuid_value}/events?event_type=CONVERSION"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        def decode_traffic_source(encoded_str):
            try:
                # Remove 'encoded_' prefix if present
                if encoded_str.startswith("encoded_"):
                    encoded_str = encoded_str[len("encoded_"):]
                # Add padding if needed
                missing_padding = len(encoded_str) % 4
                if missing_padding:
                    encoded_str += '=' * (4 - missing_padding)
                decoded_bytes = base64.b64decode(encoded_str)
                decoded_str = decoded_bytes.decode("utf-8")
                return json.loads(decoded_str)
            except Exception as e:
                logging.info(f"Failed to decode traffic_source: {e}")
                return None

        def extract_utm_params(traffic_source_string):
            utm_keys = ["utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content"]
            utm_dict = {k: None for k in utm_keys}
            if not traffic_source_string:
                return utm_dict
            # Split by '&', then '='
            for part in traffic_source_string.split('&'):
                if '=' in part:
                    k, v = part.split('=', 1)
                    if k in utm_dict:
                        utm_dict[k] = v
            return utm_dict

        try:
            response = requests.get(url, headers=headers)
            status_code = response.status_code
            data = response.json()

            if not isinstance(data, list):
                data = [data]

            processed = []
            for item in data:
                payload = item.get("payload", {})
                traffic_source_encoded = payload.pop("traffic_source", None)
                traffic_source_decoded = (
                    decode_traffic_source(traffic_source_encoded)
                    if traffic_source_encoded else None
                )
                if traffic_source_decoded:
                    item["traffic_source"] = traffic_source_decoded
                    # Extract UTM params from current_session.value
                    current_session = traffic_source_decoded.get("current_session", {})
                    utm_values = extract_utm_params(current_session.get("value"))
                    for k, v in utm_values.items():
                        if v is not None:
                            item[k] = self.decode_if_needed(v)

                processed.append(item)

            return status_code, processed

        except requests.exceptions.RequestException as e:
            logging.info(f"Request failed for {uuid_value}: {e}.")
            raise

    @parallel_decorator(max_workers=3, sleep_time=20, key_parameter="uuid")
    def get_contact_events_parallel(self, uuid_value):
        return self.get_contact_events(uuid_value)

    def get_contact_funnel_status(self, uuid_value: str) -> tuple[int, Optional[list[dict[str, Any]]]]:
        """Fetch a single contact funnel status."""

        url = f"https://api.rd.services/platform/contacts/{uuid_value}/funnels/default"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        try:
            response = requests.get(url, headers=headers)

            return response.status_code, response.json()

        except requests.exceptions.RequestException as e:
            logging.info(f"Request failed for {uuid_value}: {e}.")
            raise

    @parallel_decorator(max_workers=3, sleep_time=20, key_parameter="uuid")
    def get_contact_funnel_status_parallel(self, uuid_value):
        return self.get_contact_funnel_status(uuid_value)

    @staticmethod
    def process_in_batches(all_data: list, batch_size=500):
        # Generator to yield batches of contacts
        for i in range(0, len(all_data), batch_size):
            yield all_data[i: i + batch_size]

    @staticmethod
    def decode_if_needed(text_string: str) -> str:
        """
        Decodes a string that may be encoded with percent-encoding and/or Unicode escape sequences.

        Parameters:
            text_string (str): The input string that may be encoded.

        Returns:
            str: The fully decoded string.
        """
        # Decode percent-encoded sequences if present.
        if re.search(r"%[0-9A-Fa-f]{2}", text_string):
            text_string = unquote(text_string)

        # Decode Unicode escapes if the literal "\u" is found.
        if "\\u" in text_string:
            try:
                text_string = text_string.encode("utf-8").decode(
                    "unicode_escape"
                )  # noqa: W605
            except Exception as e:
                logging.info("Unicode escape decoding failed:", e)

        return text_string

    # def classify_value(self, value: str, mapping: dict) -> list:
    #     """
    #     Processes a single string value:

    #     Parameters:
    #         value (str): The input string to classify.
    #         mapping (dict): A dictionary where keys are classification labels and values are regex strings.

    #     Returns:
    #         list: A list of classification labels that match the input value.
    #     """
    #     if value == "" or value is None:
    #         return []

    #     # Step 1: Decode the string.
    #     decoded_value = self.decode_if_needed(value)

    #     # Step 2: Normalize the string.
    #     normalized_value = decoded_value.strip().lower()

    #     # Step 3: Remove any "admissao" or "admissão" occurrences.
    #     normalized_value = re.sub(r"admiss[aã]o", "", normalized_value)

    #     matches = []
    #     # Step 4: Iterate over the mapping and search using the provided regex patterns.
    #     for key, regex_pattern in mapping.items():
    #         if re.search(regex_pattern, normalized_value, re.IGNORECASE):
    #             matches.append(key)

    #     return matches
