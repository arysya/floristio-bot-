import base64
import logging
import time
import uuid
import warnings

import httpx

warnings.filterwarnings("ignore", message="Unverified HTTPS request")

logger = logging.getLogger(__name__)

AUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"


class GigaChatClient:
    def __init__(self):
        from config import GIGACHAT_CLIENT_ID, GIGACHAT_CLIENT_SECRET
        self._client_id = GIGACHAT_CLIENT_ID
        self._secret = GIGACHAT_CLIENT_SECRET
        self._token: str | None = None
        self._expires_at: float = 0

    def _auth_header(self) -> str:
        creds = f"{self._client_id}:{self._secret}"
        return base64.b64encode(creds.encode()).decode()

    async def _refresh_token(self):
        headers = {
            "Authorization": f"Basic {self._auth_header()}",
            "RqUID": str(uuid.uuid4()),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        async with httpx.AsyncClient(verify=False) as client:
            r = await client.post(AUTH_URL, headers=headers, data={"scope": "GIGACHAT_API_PERS"})
            r.raise_for_status()
            data = r.json()
            self._token = data["access_token"]
            # expires_at — Unix timestamp в миллисекундах
            self._expires_at = data.get("expires_at", 0) / 1000

    async def _get_token(self) -> str:
        if not self._token or self._expires_at < time.time() + 60:
            await self._refresh_token()
        return self._token

    async def ask(self, user_message: str, system_prompt: str) -> str:
        token = await self._get_token()
        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 512,
        }
        async with httpx.AsyncClient(verify=False) as client:
            r = await client.post(
                CHAT_URL,
                headers={"Authorization": f"Bearer {token}"},
                json=payload,
                timeout=30,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
