import datetime
from enum import Enum
from typing import List, Optional, Dict, Union, Any, Literal
from pydantic import BaseModel, Field, ConfigDict


class RatingType(str, Enum):
    ADMINS = "admins"
    ADVOCATES = "advocates"
    COMBINE_OPERATORS = "combine_operators"
    BUS_DRIVERS = "bus_drivers"
    TRACTOR_DRIVERS = "tractor_drivers"
    CATCHERS = "catchers"
    COLLECTORS = "collectors"
    CORN_PILOTS = "corn_pilots"
    CRYPTO_ASC = "crypto_asc"
    CRYPTO_BTC = "crypto_btc"
    ELECTRIC_TRAIN_DRIVERS = "electric_train_drivers"
    LVL_FAMILIES = "lvl_families"
    LVL_PLAYERS = "lvl_players"
    MECHANICS = "mechanics"
    RICHEST = "richest"
    OUTBIDS = "outbids"
    PILOTS = "pilots"
    SELLERS = "sellers"
    TAXI_DRIVERS = "taxi_drivers"
    TRAM_DRIVERS = "tram_drivers"
    TRUCKERS = "truckers"
    CLADMENS = "cladmens"


class EstateType(str, Enum):
    HOUSES = "houses"
    BUSINESSES = "businesses"


class SSFont(str, Enum):
    ARIAL_BOLD = 'arialbd.ttf'
    ARIAL_BOLD_ITALIC = 'arialbdi.ttf'
    BITTER_BOLD = 'bitterbd.ttf'
    BITTER_BOLD_ITALIC = 'bitterbdi.ttf'
    MONTSERRAT_BOLD = 'montserratbd.ttf'
    MONTSERRAT_BOLD_ITALIC = 'montserratbdi.ttf'
    NUNITO_BOLD = 'nunitobd.ttf'
    NUNITO_BOLD_ITALIC = 'nunitobdi.ttf'
    OPENSANS_BOLD = 'opensansbd.ttf'
    OPENSANS_BOLD_ITALIC = 'opensansbdi.ttf'
    UBUNTU_BOLD = 'ubuntubd.ttf'
    UBUNTU_BOLD_ITALIC = 'ubuntubdi.ttf'
    ROBOTO_BOLD = 'robotobd.ttf'
    ROBOTO_BOLD_ITALIC = 'robotobdi.ttf'
    SF_PRO_DISPLAY_BOLD = 'SF-Pro-Display-Bold.otf'


class ValidationError(BaseModel):
    loc: List[Union[str, int]]
    msg: str
    type: str


class HTTPValidationError(BaseModel):
    detail: Optional[List[ValidationError]] = None


class AuctionInfo(BaseModel):
    active: bool
    minimal_bet: int
    time_end: Optional[datetime.datetime]
    start_price: int


class Coordinates(BaseModel):
    x: float
    y: float


class HouseEntry(BaseModel):
    id: int
    owner: Optional[str]
    name: Optional[str]
    auction: AuctionInfo
    coordinates: Coordinates


class BusinessEntry(BaseModel):
    id: int
    owner: Optional[str]
    name: str
    auction: AuctionInfo
    coordinates: Coordinates


class EstateResponse(BaseModel):
    server_id: int
    server_label: str
    updated_at: datetime.datetime
    houses: List[HouseEntry]
    businesses: List[BusinessEntry]


class CheckRpNameData(BaseModel):
    value: Optional[str]
    is_existing: bool
    is_confirmed: bool
    nationalities_chart: Optional[str]


class CheckRpResponse(BaseModel):
    first_name: CheckRpNameData
    last_name: CheckRpNameData
    nickname: str


class ServerInfo(BaseModel):
    server_id: int
    server_label: str


class PlayerGeneral(BaseModel):
    account_id: int
    skin_id: int
    nickname: str
    gender: str
    played_hours: int
    phone_number: Optional[int]
    health: int
    hunger: int
    max_hunger: int
    drug_addict_lvl: int
    marriage: Optional[str]
    job_label: Optional[str]


class PlayerFraction(BaseModel):
    fraction_id: Optional[int]
    fraction_label: Optional[str]
    rank_number: Optional[int]
    rank_label: Optional[str]


class IndividualAccounts(BaseModel):
    account_1: Optional[int] = Field(None, alias="1")
    account_2: Optional[int] = Field(None, alias="2")
    account_3: Optional[int] = Field(None, alias="3")
    account_4: Optional[int] = Field(None, alias="4")
    account_5: Optional[int] = Field(None, alias="5")
    account_6: Optional[int] = Field(None, alias="6")


class PlayerMoney(BaseModel):
    az_coins: int
    total_money: int
    cash: int
    bank_balance: int
    deposit: int
    have_bank_card: bool
    charity_money: int
    phone_balance: Optional[int]
    individual_accounts: IndividualAccounts


class PlayerLvl(BaseModel):
    lvl: int
    current_xp: int
    max_xp: int


class PlayerPunishes(BaseModel):
    law_count: int
    wanted_lvl: int
    warns_count: int


class PlayerVIP(BaseModel):
    vip_lvl: Optional[int]
    vip_label: Optional[str]
    vip_expiration_date: Optional[datetime.datetime]
    have_addition_vip: bool
    addition_vip_expiration_date: Optional[datetime.datetime]


class PlayerFamilyInfo(BaseModel):
    family_id: int
    family_name: Optional[str]


class PlayerRatingEntry(BaseModel):
    rating_type: RatingType
    position: int
    value: Any


class FindPlayerResponse(BaseModel):
    server: ServerInfo
    general: PlayerGeneral
    fraction: PlayerFraction
    money: PlayerMoney
    lvl: PlayerLvl
    punishes: PlayerPunishes
    vip_info: PlayerVIP
    family: Optional[PlayerFamilyInfo] = None
    ratings: List[PlayerRatingEntry] = []
    is_cached: bool = Field(False, alias="isCached")
    updated_at: datetime.datetime = Field(alias="updatedAt")


class MembersPlayer(BaseModel):
    account_id: Optional[int]
    nickname: str
    is_online: bool
    is_leader: bool
    rank_number: int
    rank_label: Optional[str]
    ingame_id: Optional[int]
    nickname_color: Optional[int]


class MembersRecord(BaseModel):
    online_players: int
    leader_nickname: Optional[str]
    modified_at: Optional[datetime.datetime]
    modified_by: Literal["system", "admin"]


class MembersResponse(BaseModel):
    server_id: int
    fraction_id: int
    server_label: str
    fraction_label: str
    total_players: int
    total_online: int
    leader_nickname: Optional[str]
    is_leader_online: bool
    online_updated_at: datetime.datetime
    members_updated_at: datetime.datetime
    online_record: MembersRecord
    players: List[MembersPlayer]


class OnlineEntry(BaseModel):
    date: datetime.date
    hours: int
    minutes: int
    seconds: int


class OnlineResponse(BaseModel):
    online: List[OnlineEntry]
    have_active_session: bool
    active_session_login_at: Optional[datetime.datetime]
    last_login_at: Optional[datetime.datetime]
    last_logout_at: Optional[datetime.datetime]


class NicknameHistoryEntry(BaseModel):
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime.datetime


class MoneyHistoryEntry(BaseModel):
    date: datetime.date
    value: int


class RatingPlayer(BaseModel):
    position: int
    nickname: str
    value: Any
    server_id: Optional[int] = None
    server_label: Optional[str] = None
    additional_value: Optional[Any] = None
    az_coins: Optional[int] = None
    family: Optional[str] = None


class RatingResponse(BaseModel):
    server_id: int
    server_label: str
    rating_type: RatingType
    updated_at: datetime.datetime
    players: List[RatingPlayer]


class RpNickResponse(BaseModel):
    name: str
    surname: str
    nickname: str


class ServerStatusResponse(BaseModel):
    server_id: int
    server_ip: str
    server_port: int
    server_label: str
    online_players: int
    max_players: int
    is_closed: bool
    server_vk: Optional[str] = None
    server_discord: Optional[str] = None
    main_admin_vk: Optional[str] = None
    deputy_main_admin_vk: Optional[str] = None
    updated_at: datetime.datetime


class TokenResponse(BaseModel):
    id: int
    project_label: str
    token: Optional[str]
    activated: bool
    disabled_logs: bool
    service: bool
    subscription_until: Optional[datetime.datetime]
    created_at: datetime.datetime
    modified_at: datetime.datetime


class RequestLogEntry(BaseModel):
    id: int
    api_method: Optional[str]
    http_method: str
    params: Dict[str, Any]
    ip_address: str
    created_at: datetime.datetime


class RequestLogResponse(BaseModel):
    data: List[RequestLogEntry]
    next_request_start_id: Optional[int]


class RequestStatsResponse(BaseModel):
    total_count: int
    methods: Dict[str, int]


class LeaderEntry(BaseModel):
    fraction_id: int
    fraction_label: str
    nickname: str
    ingame_id: int
    phone_number: Optional[int]
    afk: Optional[int]


class LeadersResponse(BaseModel):
    data: List[LeaderEntry]
    server_id: int
    server_label: str
    updated_at: datetime.datetime


class InterviewEntry(BaseModel):
    fraction_id: int
    fraction_label: str
    place: Optional[str]
    time: Optional[str]


class InterviewsResponse(BaseModel):
    server_id: int
    server_label: str
    data: List[InterviewEntry]
    updated_at: datetime.datetime


class PlayerEntry(BaseModel):
    color: int
    ping: int
    id: int
    lvl: int
    nickname: str


class PlayersResponse(BaseModel):
    server_id: int
    server_label: str
    players: List[PlayerEntry]
    updated_at: datetime.datetime


class TerritoriesCount(BaseModel):
    grove: int = 0
    ballas: int = 0
    vagos: int = 0
    rifa: int = 0
    aztec: int = 0
    nw: int = 0


class MapResponse(BaseModel):
    server_id: int
    server_label: str
    updated_at: datetime.datetime
    image: str = Field(..., alias="image", description="Карта сервера в формате base64")
    territories_count: TerritoriesCount
    model_config = ConfigDict(populate_by_name=True)


class BotAccount(BaseModel):
    nickname: str
    avg_sessions_per_day: float
    avg_session_duration_seconds: float


class BotDetectionResponse(BaseModel):
    accounts: List[BotAccount]


class CheckrRpManualOverrideEntry(BaseModel):
    value: str
    status: Literal["confirmed", "denied"]


class CheckRpManualOverridesListResponse(BaseModel):
    names: List[CheckrRpManualOverrideEntry]
    surnames: List[CheckrRpManualOverrideEntry]


class AIResponse(BaseModel):
    lines: List[str]


class FamilyMember(BaseModel):
    account_id: int
    nickname: str
    family_rank: int
    quests: int
    warns: int
    is_online: bool
    ingame_id: Optional[int] = None
    is_leader: bool
    is_deputy: bool
    last_login_at: datetime.datetime


class FamilyResponse(BaseModel):
    server_id: int
    server_label: str
    family_id: int
    name: Optional[str]
    lvl: Optional[int]
    flag_id: Optional[int] = None
    leader_nickname: Optional[str] = None
    is_leader_online: bool
    total_members_count: int
    online_members_count: int
    total_deputies_count: int
    online_deputies_count: int
    members: List[FamilyMember]
    updated_at: datetime.datetime
