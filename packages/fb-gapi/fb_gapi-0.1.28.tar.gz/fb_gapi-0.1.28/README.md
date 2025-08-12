
# Facebook Messenger Graph API Python Async SDK ( v23.0 )

A lightweight Python SDK for sending messages (text and image attachments) using the Facebook Graph API along with the Facebook Messenger Send API.

## Installation

```python
pip install -U fb_gapi
```

## 🚀 Features

- **Send Text Messages**: Easily send text messages to users.
- **Send Remote Attachments**: Send remote attachments by URL.
- **Send Local Attachments**: Send local attachments by file path.
- **Get Conversation History**: Fetch the latest conversation history.
- **Error Handling**: The SDK will raise a `MessengerAPIError` when the Facebook API responds with an error.

## 🚀 Getting Started

1. `Create an App` on [Meta Developer Account](https://developers.facebook.com/apps/creation/) and connect it to your Page.
2. Add a callback URL to your app. eg: `https://example.com/callback` to communicate with your server.
3. Get the `Facebook Page Access Token` from your created app.
4. Send a GET request to your callback URL to verify the connection. eg: `https://example.com/callback?hub.verify_token=VERIFY_TOKEN`.
5. All set! You can now use the SDK.

## 📝 Usage

### 📦 Import the client
```python
from fb_gapi import MessengerClient
```

### 🔒 Initialize with your Page Access Token 
```python
client = MessengerClient(access_token="YOUR_PAGE_ACCESS_TOKEN")
```

### ✉️ Sending a Text Message
```python
async def asend_text():
    response = await client.asend_text(
        recipient_id="USER_PSID", message_text="Hello from Python!"
    )
    print(response)
```

### 🖼️ Sending an Attachment By URL
```python
async def asend_remote_attachment():
    response = await client.asend_remote_attachment(
        recipient_id="USER_PSID",
        image_url="https://example.com/image.jpg",
    )
    print(response)
```

### 🖼️ Sending a Local Attachment
```python
async def asend_local_attachment():
    response = await client.asend_local_attachment(
        recipient_id="USER_PSID", file_path="./test.png"
    )
    print(response)
```

### 👨 Get User Name (Only for verified app by Meta)
```python
async def aget_user_name():
    response = await client.aget_user_name(user_id="USER_PSID")
    print(response)
```

### 🗒️ Get Conversation History (Optional Limit upto 9)
```python
async def aget_chat_history_limited():
    response = await client.aget_chat_history(recipient_id="USER_PSID", limit=5)
    print(response)
```

### ⚠️ Error Handling
This SDK will raise a `MessengerAPIError` when the Facebook API responds with an error.

### Example:
```python
async def aexample_error_handling():
    try:
        await client.asend_text("invalid_user_id", "Hi!")
    except MessengerAPIError as e:
        print(f"GAPI Error: {e}")
```

### Error Output Example:
```
MessengerAPIError (HTTP 400): [OAuthException] Invalid OAuth access token. (code 190)
```

Note: USER_PSID means `page scoped user id`, which you can get from the response of the webhook callback set for your page.

## 📚 Requirements
- Python 3.9+

## 🛠️ TODO

- **Improve conversation history limit.**
- **Add support for templates.**
- **Add support for quick replies.**
- **Add support for actions.**
- **Add support for custom buttons.**
- **Add support for comment and replies.**

## 📃 License

MIT License. Use freely and contribute!
