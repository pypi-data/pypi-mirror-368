import datetime
import json
import aiohttp
from typing import List, Optional, Union, Literal, Dict
from pydantic import TypeAdapter

from .models import (ServerStatusResponse, RatingResponse, CheckRpResponse, RpNickResponse, EstateResponse, MembersResponse,
                     FindPlayerResponse, OnlineResponse, TokenResponse, RequestLogResponse, RequestStatsResponse,
                     LeadersResponse, InterviewsResponse, PlayersResponse, MapResponse, RatingType, EstateType,
                     BotDetectionResponse, CheckRpManualOverridesListResponse, AIResponse, SSFont, FamilyResponse,
                     NicknameHistoryEntry, MoneyHistoryEntry)
from . import api


class VprikolAPI:
    def __init__(self, token: Optional[str] = None, base_url: str = "https://apitest.szx.su/"):
        self.base_url = base_url
        self.headers = {"User-Agent": "vprikol-python-lib"}
        if token:
            self.headers["VP-API-Token"] = token

    async def get_token_information(self, token_id: Union[int, Literal["current", "all", "deactivated"]] = "current") -> Union[TokenResponse, List[TokenResponse]]:
        response_json = await api.get_json(self.base_url, f"token/{token_id}", self.headers)
        if isinstance(response_json, list):
            return TypeAdapter(List[TokenResponse]).validate_python(response_json)
        return TokenResponse.model_validate(response_json)

    async def get_server_status(self, server_id: int) -> ServerStatusResponse:
        params = {"server_id": str(server_id)}
        response_json = await api.get_json(self.base_url, "status", self.headers, params=params)
        return ServerStatusResponse.model_validate(response_json)

    async def get_rating(self, server_id: int, rating_type: RatingType) -> RatingResponse:
        params = {"server_id": str(server_id), "rating_type": rating_type.value}
        response_json = await api.get_json(self.base_url, "rating", self.headers, params=params)
        return RatingResponse.model_validate(response_json)

    async def get_estate(self, server_id: int, estate_type: Optional[EstateType] = None, nickname: Optional[str] = None, min_id: Optional[int] = None, max_id: Optional[int] = None) -> EstateResponse:
        params = {"server_id": str(server_id)}
        if estate_type:
            params["type"] = estate_type.value
        if nickname:
            params["nickname"] = nickname
        if min_id is not None:
            params["min_id"] = str(min_id)
        if max_id is not None:
            params["max_id"] = str(max_id)

        response_json = await api.get_json(self.base_url, "estate", self.headers, params=params)
        return EstateResponse.model_validate(response_json)

    async def check_rp_nickname(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> CheckRpResponse:
        params = {}
        if first_name:
            params["first_name"] = first_name
        if last_name:
            params["last_name"] = last_name

        response_json = await api.get_json(self.base_url, "checkrp", self.headers, params=params)
        return CheckRpResponse.model_validate(response_json)

    async def generate_rp_nickname(self, gender: str, nation: str) -> RpNickResponse:
        params = {"gender": gender, "nation": nation}
        response_json = await api.get_json(self.base_url, "rpnick", self.headers, params=params)
        return RpNickResponse.model_validate(response_json)

    async def generate_ss(self, screen: bytes, commands: List[str], text_top: bool = True, font: SSFont = SSFont.ARIAL_BOLD,
                          text_size: float = 0.95, commands_colors: Optional[Dict[str, str]] = None) -> bytes:
        form_data = aiohttp.FormData()
        form_data.add_field("screen", screen, filename="screen.png", content_type="image/png")

        for command in commands:
            form_data.add_field("commands", command)

        form_data.add_field("text_top", str(text_top).lower())
        form_data.add_field("font", font.value)
        form_data.add_field("text_size", str(text_size))
        form_data.add_field("commands_colors", json.dumps(commands_colors) if commands_colors else "{}")

        response_bytes = await api.post_form(self.base_url, "ss", self.headers, data=form_data)
        return response_bytes

    async def generate_ai_situation(self, theme_prompt: str) -> AIResponse:
        params = {"theme_prompt": theme_prompt}
        response_json = await api.post_json(self.base_url, "ai/situation", self.headers, params=params)
        return AIResponse.model_validate(response_json)

    async def get_leaders(self, server_id: int) -> LeadersResponse:
        params = {"server_id": str(server_id)}
        response_json = await api.get_json(self.base_url, "ingame/leaders", self.headers, params=params)
        return LeadersResponse.model_validate(response_json)

    async def get_deputies(self, server_id: int) -> LeadersResponse:
        params = {"server_id": str(server_id)}
        response_json = await api.get_json(self.base_url, "ingame/deputies", self.headers, params=params)
        return LeadersResponse.model_validate(response_json)

    async def get_interviews(self, server_id: int) -> InterviewsResponse:
        params = {"server_id": str(server_id)}
        response_json = await api.get_json(self.base_url, "ingame/interviews", self.headers, params=params)
        return InterviewsResponse.model_validate(response_json)

    async def get_players(self, server_id: int) -> PlayersResponse:
        params = {"server_id": str(server_id)}
        response_json = await api.get_json(self.base_url, "ingame/players", self.headers, params=params)
        return PlayersResponse.model_validate(response_json)

    async def get_server_map(self, server_id: int, only_ghetto: bool = False) -> MapResponse:
        params = {"server_id": str(server_id), "only_ghetto": str(only_ghetto).lower()}
        response_json = await api.get_json(self.base_url, "ingame/map", self.headers, params=params)
        return MapResponse.model_validate(response_json)

    async def get_token_requests_history(self, token_id: Union[int, Literal["current"]] = "current", limit: int = 50, request_start_id: Optional[int] = None,
                                         date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None,
                                         api_method: Optional[str] = None, ip_address: Optional[str] = None) -> RequestLogResponse:
        params = {"limit": str(limit)}
        if request_start_id is not None:
            params["request_start_id"] = str(request_start_id)
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        if api_method:
            params["api_method"] = api_method
        if ip_address:
            params["ip_address"] = ip_address

        response_json = await api.get_json(self.base_url, f"token/{token_id}/requests", self.headers, params=params)
        return RequestLogResponse.model_validate(response_json)

    async def get_token_requests_stats(self, token_id: Union[int, Literal["current"]] = "current",
                                       date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None,
                                       api_method: Optional[str] = None, ip_address: Optional[str] = None) -> RequestStatsResponse:
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()
        if api_method:
            params["api_method"] = api_method
        if ip_address:
            params["ip_address"] = ip_address

        response_json = await api.get_json(self.base_url, f"token/{token_id}/requests/stats", self.headers, params=params)
        return RequestStatsResponse.model_validate(response_json)

    async def find_player(self, server_id: int, nickname: Optional[str] = None, account_id: Optional[int] = None) -> FindPlayerResponse:
        if not nickname and not account_id:
            raise ValueError("Необходимо указать nickname или account_id.")

        params = {"server_id": str(server_id)}
        if nickname:
            params["nickname"] = nickname
        if account_id is not None:
            params["account_id"] = str(account_id)

        response_json = await api.get_json(self.base_url, "player/find", self.headers, params=params)
        return FindPlayerResponse.model_validate(response_json)

    async def get_player_online(self, server_id: int, nickname: str, date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None) -> OnlineResponse:
        params = {"server_id": str(server_id), "nickname": nickname}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()

        response_json = await api.get_json(self.base_url, "player/online", self.headers, params=params)
        return OnlineResponse.model_validate(response_json)

    async def get_player_history(self, server_id: int, history_type: Literal['nickname', 'total_money'], nickname: Optional[str] = None, account_id: Optional[int] = None,
                                 date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None) -> Union[List[NicknameHistoryEntry], List[MoneyHistoryEntry]]:
        if not nickname and not account_id:
            raise ValueError("Необходимо указать nickname или account_id.")

        params = {"server_id": str(server_id), "type": history_type}
        if nickname:
            params["nickname"] = nickname
        if account_id is not None:
            params["account_id"] = str(account_id)
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()

        response_json = await api.get_json(self.base_url, "player/history", self.headers, params=params)

        if not response_json:
            return []
        if history_type == 'nickname':
            return TypeAdapter(List[NicknameHistoryEntry]).validate_python(response_json)
        else:
            return TypeAdapter(List[MoneyHistoryEntry]).validate_python(response_json)

    async def get_fraction_members(self, server_id: int, fraction_id: int) -> MembersResponse:
        params = {"server_id": str(server_id), "fraction_id": str(fraction_id)}
        response_json = await api.get_json(self.base_url, "fraction/members", self.headers, params=params)
        return MembersResponse.model_validate(response_json)

    async def get_manual_checkrp_overrides(self) -> CheckRpManualOverridesListResponse:
        response_json = await api.get_json(self.base_url, "internal/checkrp/overrides", self.headers)
        return CheckRpManualOverridesListResponse.model_validate(response_json)

    async def confirm_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        params = {"type": value_type, "value": value}
        await api.post_empty(self.base_url, "internal/checkrp/confirm", self.headers, params=params)

    async def deny_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        params = {"type": value_type, "value": value}
        await api.post_empty(self.base_url, "internal/checkrp/deny", self.headers, params=params)

    async def reset_rp_name(self, value_type: Literal["firstname", "surname"], value: str) -> None:
        params = {"type": value_type, "value": value}
        await api.delete_empty(self.base_url, "internal/checkrp/reset", self.headers, params=params)

    async def get_current_ip(self) -> str:
        return await api.get_json(self.base_url, "internal/ip", self.headers)

    async def list_disabled_methods(self) -> List[str]:
        response_json = await api.get_json(self.base_url, "internal/disabled-methods", self.headers)
        return TypeAdapter(List[str]).validate_python(response_json)

    async def disable_method(self, method_name: str) -> None:
        params = {"method_name": method_name}
        await api.post_empty(self.base_url, "internal/disabled-methods", self.headers, params=params)

    async def enable_method(self, method_name: str) -> None:
        params = {"method_name": method_name}
        await api.delete_empty(self.base_url, "internal/disabled-methods", self.headers, params=params)

    async def detect_bots(self, server_id: int, date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None) -> BotDetectionResponse:
        params = {"server_id": str(server_id)}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()

        response_json = await api.get_json(self.base_url, "internal/detect-bots", self.headers, params=params)
        return BotDetectionResponse.model_validate(response_json)

    async def get_family_by_id(self, server_id: int, family_id: int) -> FamilyResponse:
        params = {"server_id": str(server_id), "family_id": str(family_id)}
        response_json = await api.get_json(self.base_url, "family", self.headers, params=params)
        return FamilyResponse.model_validate(response_json)

    async def find_family(self, server_id: int, nickname: Optional[str] = None, name: Optional[str] = None) -> FamilyResponse:
        params = {"server_id": str(server_id)}
        if nickname:
            params["nickname"] = nickname
        if name:
            params["name"] = name

        response_json = await api.get_json(self.base_url, "family/find", self.headers, params=params)
        return FamilyResponse.model_validate(response_json)

    async def create_token(self, project_label: str, service: bool = False, disabled_logs: bool = False, subscription_days: Optional[int] = None) -> TokenResponse:
        body = {"project_label": project_label, "service": service, "disabled_logs": disabled_logs, "subscription_days": subscription_days}
        response_json = await api.post_json(self.base_url, "internal/token", self.headers, body=body)
        return TokenResponse.model_validate(response_json)

    async def update_token(self, token_id: int, project_label: Optional[str] = None, activated: Optional[bool] = None, service: Optional[bool] = None,
                           disabled_logs: Optional[bool] = None, add_subscription_days: Optional[int] = None) -> TokenResponse:
        body = {}
        if project_label is not None:
            body["project_label"] = project_label
        if activated is not None:
            body["activated"] = activated
        if service is not None:
            body["service"] = service
        if disabled_logs is not None:
            body["disabled_logs"] = disabled_logs
        if add_subscription_days is not None:
            body["add_subscription_days"] = add_subscription_days

        response_json = await api.put_json(self.base_url, f"internal/token/{token_id}", self.headers, body=body)
        return TokenResponse.model_validate(response_json)

    async def delete_token(self, token_id: int) -> None:
        await api.delete_empty(self.base_url, f"internal/token/{token_id}", self.headers)

    async def reissue_token(self, token_id: int) -> TokenResponse:
        response_json = await api.post_json(self.base_url, f"internal/token/{token_id}/reissue", self.headers)
        return TokenResponse.model_validate(response_json)

    async def find_tokens_by_ip(self, ip_address: str) -> List[TokenResponse]:
        response_json = await api.get_json(self.base_url, f"internal/token/find-by-ip/{ip_address}", self.headers)
        return TypeAdapter(List[TokenResponse]).validate_python(response_json)

    async def get_overall_requests_stats(self, date_from: Optional[datetime.datetime] = None, date_to: Optional[datetime.datetime] = None) -> RequestStatsResponse:
        params = {}
        if date_from:
            params["date_from"] = date_from.isoformat()
        if date_to:
            params["date_to"] = date_to.isoformat()

        response_json = await api.get_json(self.base_url, "internal/requests/stats", self.headers, params=params)
        return RequestStatsResponse.model_validate(response_json)
