import httpx
from httpx_retries import RetryTransport, Retry
from .exceptions import MessengerAPIError
from .utils import *
import requests


class MessengerClient:
    """
    A client for sending messages via the Facebook Messenger Send API.

    Args:
        access_token (str): Your Facebook Page access token.
        api_version (str): Version of the Facebook Graph API to use (default: "v22.0").

    Raises:
        ValueError: If the access token is not provided.
    """

    def __init__(
        self, access_token: str, api_version: str = "v23.0", max_retries: int = 3
    ):
        if not access_token:
            raise ValueError("An access token must be provided.")
        self.access_token = access_token
        self.api_version = api_version
        self.max_retries = max_retries
        self.api_base_url = f"https://graph.facebook.com/{self.api_version}/me"

        retry_config = Retry(
            total=max_retries,
            allowed_methods=["GET", "POST"],
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=0.5,
            backoff_jitter=0.5,
            max_backoff_wait=10,
        )

        transport = RetryTransport(retry=retry_config)
        self.client = httpx.AsyncClient(
            transport=transport, timeout=10.0, follow_redirects=True
        )

    def get_user_name(self, user_id: int) -> str:
        """
        Fetches the sender's name using their Facebook PSID.

        Args:
            user_id (int): The PSID of the user.

        Returns:
            str: Full name of the user.

        Raises:
            MessengerAPIError: If the API call fails.
        """

        url = f"https://graph.facebook.com/{self.api_version}/{user_id}"
        params = {"access_token": self.access_token, "fields": "name"}

        response = requests.get(url, params=params)

        if response.status_code != 200:
            self._raise_api_error(response)

        data = response.json()
        return data.get("name", "")

    async def aget_user_name(self, user_id: int) -> str:
        """
        Fetches the sender's name using their Facebook PSID.

        Args:
            user_id (int): The PSID of the user.

        Returns:
            str: Full name of the user.

        Raises:
            MessengerAPIError: If the API call fails.
        """

        url = f"https://graph.facebook.com/{self.api_version}/{user_id}"
        params = {"access_token": self.access_token, "fields": "name"}

        response = await self.client.get(url, params=params)
        if response.status_code != 200:
            await self._raise_api_error(response)

        data = response.json()
        return data.get("name", "")

    def send_text(self, recipient_id: int, message_text: str) -> dict:
        """
        Sends a plain text message to a Facebook user.

        Args:
            recipient_id (int): The PSID (Page-scoped ID) of the message recipient.
            message_text (str): The text content of the message.

        Returns:
            dict: A JSON response from the Facebook API indicating success or failure.

        Raises:
            MessengerAPIError: If the API responds with an error.
        """

        url = f"{self.api_base_url}/messages"
        payload = message_payload(recipient_id, message_text)
        params = {"access_token": self.access_token}

        response = requests.post(url, params=params, json=payload)
        if response.status_code != 200:
            self._raise_api_error(response)

        return response.json()

    async def asend_text(self, recipient_id: int, message_text: str) -> dict:
        """
        Sends a plain text message to a Facebook user.

        Args:
            recipient_id (int): The PSID (Page-scoped ID) of the message recipient.
            message_text (str): The text content of the message.

        Returns:
            dict: A JSON response from the Facebook API indicating success or failure.

        Raises:
            MessengerAPIError: If the API responds with an error.
        """

        url = f"{self.api_base_url}/messages"
        payload = message_payload(recipient_id, message_text)
        params = {"access_token": self.access_token}

        response = await self.client.post(url, params=params, json=payload)
        if response.status_code != 200:
            await self._raise_api_error(response)

        return response.json()

    def send_postback_template(
        self, recipient_id: int, text: str, buttons: list[dict]
    ) -> dict:
        """
        Sends a button template message with postback buttons to a Facebook user.

        Args:
            recipient_id (int): The PSID (Page-scoped ID) of the message recipient.
            text (str): The text displayed above the buttons.
            buttons (list[dict]): A list of button dictionaries, each containing 'type', 'title', and 'payload' keys.

        Returns:
            dict: A JSON response from the Facebook API indicating success or failure.

        Raises:
            MessengerAPIError: If the API responds with an error.
        """

        url = f"{self.api_base_url}/messages"
        params = {"access_token": self.access_token}
        payload = postback_payload(recipient_id, text, buttons)

        response = requests.post(url, params=params, json=payload)
        if response.status_code != 200:
            self._raise_api_error(response)

        return response.json()

    async def asend_postback_template(
        self, recipient_id: int, text: str, buttons: list[dict]
    ) -> dict:
        """
        Sends a button template message with postback buttons to a Facebook user.

        Args:
            recipient_id (int): The PSID (Page-scoped ID) of the message recipient.
            text (str): The text displayed above the buttons.
            buttons (list[dict]): A list of button dictionaries, each containing 'type', 'title', and 'payload' keys.

        Returns:
            dict: A JSON response from the Facebook API indicating success or failure.

        Raises:
            MessengerAPIError: If the API responds with an error.
        """

        url = f"{self.api_base_url}/messages"
        params = {"access_token": self.access_token}
        payload = postback_payload(recipient_id, text, buttons)

        response = await self.client.post(url, params=params, json=payload)
        if response.status_code != 200:
            await self._raise_api_error(response)

        return response.json()

    def send_remote_attachment(self, recipient_id: int, image_url: str) -> dict:
        """
        Sends an image attachment to a Facebook user via a publicly accessible URL.

        Args:
            recipient_id (int): The PSID (Page-scoped ID) of the message recipient.
            image_url (str): URL of the image to be sent as an attachment.

        Returns:
            dict: A JSON response from the Facebook API indicating success or failure.

        Raises:
            MessengerAPIError: If the API responds with an error.
        """

        url = f"{self.api_base_url}/messages"
        payload = attachment_payload_remote(recipient_id, image_url)
        params = {"access_token": self.access_token}

        response = requests.post(url, params=params, json=payload)
        if response.status_code != 200:
            self._raise_api_error(response)

        return response.json()

    async def asend_remote_attachment(self, recipient_id: int, image_url: str) -> dict:
        """
        Sends an image attachment to a Facebook user via a publicly accessible URL.

        Args:
            recipient_id (int): The PSID (Page-scoped ID) of the message recipient.
            image_url (str): URL of the image to be sent as an attachment.

        Returns:
            dict: A JSON response from the Facebook API indicating success or failure.

        Raises:
            MessengerAPIError: If the API responds with an error.
        """

        url = f"{self.api_base_url}/messages"
        payload = attachment_payload_remote(recipient_id, image_url)
        params = {"access_token": self.access_token}

        response = await self.client.post(url, params=params, json=payload)
        if response.status_code != 200:
            await self._raise_api_error(response)

        return response.json()

    def send_local_attachment(self, recipient_id: int, file_path: str) -> dict:
        """
        Sends a local image file to a user by first uploading it and then sending via attachment_id.

        Args:
            recipient_id (int): The PSID of the user.
            file_path (str): The path to the local image file.

        Returns:
            dict: Facebook API response JSON.

        Raises:
            MessengerAPIError: If any part of the upload or message send fails.
        """

        attachment_id = self._upload_image(file_path)
        return self._send_image_by_attachment_id(recipient_id, attachment_id)

    async def asend_local_attachment(self, recipient_id: int, file_path: str) -> dict:
        """
        Sends a local image file to a user by first uploading it and then sending via attachment_id.

        Args:
            recipient_id (int): The PSID of the user.
            file_path (str): The path to the local image file.

        Returns:
            dict: Facebook API response JSON.

        Raises:
            MessengerAPIError: If any part of the upload or message send fails.
        """

        attachment_id = await self._aupload_image(file_path)
        return await self._asend_image_by_attachment_id(recipient_id, attachment_id)

    def _upload_image(self, file_path: str) -> str:
        """
        Uploads a local image and returns the attachment_id.

        Args:
            file_path (str): Path to the local image file.

        Returns:
            str: Facebook-generated attachment_id.

        Raises:
            MessengerAPIError: If upload fails.
        """

        url = f"{self.api_base_url}/message_attachments"
        params = {"access_token": self.access_token}
        files = attachment_upload_local(file_path)

        try:
            response = requests.post(url, params=params, files=files)
            response.raise_for_status()
            data = response.json()
            attachment_id = data.get("attachment_id")

            if not attachment_id:
                raise MessengerAPIError(response.status_code, data)

            return attachment_id

        except httpx.RequestError as e:
            raise MessengerAPIError(500, {"error": {"message": str(e)}})

    async def _aupload_image(self, file_path: str) -> str:
        """
        Uploads a local image and returns the attachment_id.

        Args:
            file_path (str): Path to the local image file.

        Returns:
            str: Facebook-generated attachment_id.

        Raises:
            MessengerAPIError: If upload fails.
        """

        url = f"{self.api_base_url}/message_attachments"
        params = {"access_token": self.access_token}
        files = await aattachment_upload_local(file_path)

        try:
            response = await self.client.post(url, params=params, files=files)
            response.raise_for_status()
            data = response.json()
            attachment_id = data.get("attachment_id")

            if not attachment_id:
                raise MessengerAPIError(response.status_code, data)

            return attachment_id

        except httpx.RequestError as e:
            raise MessengerAPIError(500, {"error": {"message": str(e)}})

    def _send_image_by_attachment_id(
        self, recipient_id: int, attachment_id: str
    ) -> dict:
        """
        Sends a message using a previously uploaded image attachment.

        Args:
            recipient_id (int): The PSID of the user.
            attachment_id (str): The image attachment ID from Facebook.

        Returns:
            dict: Facebook API response.

        Raises:
            MessengerAPIError: If sending the message fails.
        """

        url = f"{self.api_base_url}/messages"
        params = {"access_token": self.access_token}
        payload = attachment_payload_local(recipient_id, attachment_id)

        response = requests.post(url, params=params, json=payload)
        if response.status_code != 200:
            self._raise_api_error(response)

        return response.json()

    async def _asend_image_by_attachment_id(
        self, recipient_id: int, attachment_id: str
    ) -> dict:
        """
        Sends a message using a previously uploaded image attachment.

        Args:
            recipient_id (int): The PSID of the user.
            attachment_id (str): The image attachment ID from Facebook.

        Returns:
            dict: Facebook API response.

        Raises:
            MessengerAPIError: If sending the message fails.
        """

        url = f"{self.api_base_url}/messages"
        params = {"access_token": self.access_token}
        payload = attachment_payload_local(recipient_id, attachment_id)

        response = await self.client.post(url, params=params, json=payload)
        if response.status_code != 200:
            await self._araise_api_error(response)

        return response.json()

    def get_chat_history(self, recipient_id: int, limit: int = None) -> list:
        """
        Fetches the latest incoming and outgoing messages from the Facebook Conversations API.

        Args:
            access_token (str): Facebook Page Access Token.
            user_id (int): PSID to filter only the specific user's messages. Defaults to None.
            limit (int, optional): Maximum number of messages to retrieve.

        Returns:
            list: A list of dictionaries with 'sender' and 'message' keys.
        """

        url = f"{self.api_base_url}/conversations"
        params = {
            "access_token": self.access_token,
            "fields": "messages{message,from,created_time}",
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            self._raise_api_error(response)

        fb_json = response.json()
        messages_list = extract_chat_messages(recipient_id, fb_json)
        messages_list.sort(key=lambda m: m.get("created_time", ""), reverse=True)

        return messages_list[:limit]

    async def aget_chat_history(self, recipient_id: int, limit: int = None) -> list:
        """
        Fetches the latest incoming and outgoing messages from the Facebook Conversations API.

        Args:
            access_token (str): Facebook Page Access Token.
            user_id (int): PSID to filter only the specific user's messages. Defaults to None.
            limit (int, optional): Maximum number of messages to retrieve.

        Returns:
            list: A list of dictionaries with 'sender' and 'message' keys.
        """

        url = f"{self.api_base_url}/conversations"
        params = {
            "access_token": self.access_token,
            "fields": "messages{message,from,created_time}",
        }

        response = await self.client.get(url, params=params)
        if response.status_code != 200:
            await self._raise_api_error(response)

        fb_json = response.json()
        messages_list = extract_chat_messages(recipient_id, fb_json)
        messages_list.sort(key=lambda m: m.get("created_time", ""), reverse=True)

        return messages_list[:limit]

    def get_user_labels(self, user_id: int) -> list[str]:
        """
        Fetches all custom label names assigned to a user.

        Args:
            user_id (int): The PSID of the user.

        Returns:
            list[str]: A list of label names.

        Raises:
            MessengerAPIError: If the API call fails.
        """
        url = f"https://graph.facebook.com/{self.api_version}/{user_id}/custom_labels"
        params = {
            "access_token": self.access_token,
            "fields": "page_label_name",
        }

        response = requests.get(url, params=params)

        if response.status_code != 200:
            self._raise_api_error(response)

        data = response.json()
        labels_data = data.get("data", [])
        return [label.get("page_label_name", "") for label in labels_data]

    async def aget_user_labels(self, user_id: int) -> list[str]:
        """
        Asynchronously fetches all custom label names assigned to a user.

        Args:
            user_id (int): The PSID of the user.

        Returns:
            list[str]: A list of label names.

        Raises:
            MessengerAPIError: If the API call fails.
        """
        url = f"https://graph.facebook.com/{self.api_version}/{user_id}/custom_labels"
        params = {
            "access_token": self.access_token,
            "fields": "page_label_name",
        }

        try:
            response = await self.client.get(url, params=params)
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise MessengerAPIError(
                response.status_code, {"error": {"message": str(e)}}
            )

        data = response.json()
        labels_data = data.get("data", [])
        return [label.get("page_label_name", "") for label in labels_data]

    def _raise_api_error(self, response: httpx.Response):
        """
        Raises an exception with the error details from the API response.
        Args:
            response (httpx.Response): The HTTP response object.
        Raises:
            MessengerAPIError: Custom error class for handling API errors.
        """

        try:
            error_json = response.json()
        except Exception:
            error_json = {"error": {"message": response.aread()}}

        raise MessengerAPIError(response.status_code, error_json)

    async def _araise_api_error(self, response: httpx.Response):
        """
        Raises an exception with the error details from the API response.
        Args:
            response (httpx.Response): The HTTP response object.
        Raises:
            MessengerAPIError: Custom error class for handling API errors.
        """

        try:
            error_json = response.json()
        except Exception:
            error_json = {"error": {"message": await response.aread()}}

        raise MessengerAPIError(response.status_code, error_json)

    async def aclose(self):
        """
        Closes the HTTP client connection.
        """

        await self.client.aclose()
