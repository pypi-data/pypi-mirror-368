from typing import cast

from .abc import TeamData, UserData
from .base import BaseClient


class TTClient(BaseClient):
    async def send_post(self, chat_id: int, text: str) -> None:
        data = {'chat_id': chat_id, 'text': text}
        await self.api_call('/bot/message', 'POST', data)

    async def send_private_post(self, user_id: int, text: str) -> None:
        data = {'user_id': user_id, 'text': text}
        await self.api_call('/msg/post/private', 'POST', data)

    async def get_user_data(self, ids: list[int]) -> list[UserData]:
        data = await self.api_call(f'/user/list?ids={",".join(map(str, ids))}', 'GET')
        return cast(list[UserData], data['users'])

    async def get_team_data(self, ids: list[int]) -> list[TeamData]:
        data = await self.api_call(f'/core/org?ids={",".join(map(str, ids))}', 'GET')
        return cast(list[TeamData], data['orgs'])

    async def get_chat_data(self, ids: list[int]) -> list[dict]:
        data = await self.api_call(f'/core/chat?ids={",".join(map(str, ids))}', 'GET')
        return cast(list[dict], data['chats'])
