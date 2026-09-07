"""So'rov/javob modellari.

CRM yozuvlari erkin shaklda (frontend qanday maydon yuborsa shuni saqlaymiz),
shuning uchun ko'p joyda `extra="allow"` ishlatilgan. Bu mavjud frontendni
o'zgartirmasdan ishlashga imkon beradi.
"""
from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Role = Literal["super_admin", "admin", "manager", "operator"]


class Loose(BaseModel):
    model_config = ConfigDict(extra="allow")


# ——— Auth ———


class LoginIn(BaseModel):
    login: str
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict[str, Any]


class PasswordChangeIn(BaseModel):
    current: str
    next: str = Field(min_length=6)


class ProfileIn(Loose):
    name: str | None = None
    email: str | None = None
    phone: str | None = None


# ——— Hodimlar ———


class EmployeeIn(Loose):
    name: str
    phone: str = ""
    position: str = ""
    birthDate: str = ""
    hireDate: str = ""
    shift: str = ""
    status: str = "Ishlayapti"
    address: str = ""
    deals: int = 0
    crmLogin: str
    crmPassword: str | None = None
    crmRole: Role = "operator"
    managerId: int | None = None


class EmployeeUpdate(Loose):
    crmPassword: str | None = None


# ——— CRM yozuvlari ———


class LeadIn(Loose):
    name: str
    phone: str = ""
    tour: str = ""
    people: int = 1
    amount: float = 0
    manager: str = ""
    source: str = "Telegram"
    stage: str = "Yangi"


class StageIn(BaseModel):
    stage: str


class SheetLeadIn(Loose):
    """Google Sheets Apps Script yuboradigan bitta qator (yangi lead).

    Ikki xil jadval formatini qo'llab-quvvatlaydi:
      1. Oddiy/qo'lda to'ldiriladigan jadval — name, phone, tour, people,
         amount, comment, city, telegram, source.
      2. Meta (Facebook/Instagram) Lead Ads eksporti — qo'shimcha ravishda
         platform, campaign, ad, leadStatus, createdTime, formName,
         externalId maydonlarini yuboradi (pastga qarang).
    Ikkalasi ham bir vaqtda, ixtiyoriy tarzda ishlatilishi mumkin.
    """

    name: str
    phone: str
    tour: str = ""
    people: int = 1
    amount: float = 0
    comment: str = ""
    city: str = ""
    telegram: str = ""
    source: str = ""            # bo'sh bo'lsa — platform yoki SHEETS_DEFAULT_SOURCE ishlatiladi
    rowId: str | int | None = None  # Sheetdagi qator raqami/ID — kuzatuv uchun, ixtiyoriy

    # ——— Meta (Facebook/Instagram) Lead Ads maydonlari — hammasi ixtiyoriy ———
    platform: str = ""          # jadvaldagi "platform" ustuni — masalan "ig", "fb"
    campaign: str = ""          # "campaign_name" ustuni
    ad: str = ""                # "ad_name" ustuni
    leadStatus: str = ""        # "lead_status" ustuni (Meta tomonidagi holat, masalan "CREATED")
    formName: str = ""          # "form_name" ustuni
    createdTime: str = ""       # "created_time" ustuni (ISO 8601) — lead yaratilgan sana/vaqt
    externalId: str = ""        # "id" ustuni — Metadagi lead identifikatori (dublikatni aniqlash uchun)


class WebsiteLeadIn(Loose):
    """Sayt (Lead Form / landing) dan kelgan ariza — `sadaf-landing` frontendi
    ``POST /api/integrations/website/lead`` ga shu ko'rinishda yuboradi
    (frontend: ``src/services/api.js`` -> ``submitLead``).

    - ``destination`` CRM'dagi mavjud ``tour`` maydoniga moslanadi.
    - ``travelDate`` alohida saqlanadi va izohga ham qo'shiladi — mavjud
      Leads jadvali/UI hech qanday o'zgarishsiz uni "Izoh" ustunida darhol
      ko'rsatadi.
    - utm_* maydonlari ixtiyoriy — targetolog/reklama manbasini aniqlash
      uchun leadga qo'shimcha maydon sifatida saqlanadi.
    """

    name: str
    phone: str
    destination: str = ""
    travelDate: str = ""

    utm_source: str = ""
    utm_medium: str = ""
    utm_campaign: str = ""
    utm_content: str = ""
    utm_term: str = ""


class ClientIn(Loose):
    name: str
    phone: str = ""
    country: str = ""


class TourIn(Loose):
    name: str
    country: str = ""
    days: int = 1
    price: float = 0
    seats: int = 0
    status: str = "Faol"


class SaleIn(Loose):
    client: str = ""
    tour: str = ""
    amount: float = 0
    manager: str = ""


class TaskIn(Loose):
    title: str
    to: str
    due: str = ""
    time: str = ""
    priority: str = "O'rta"
    done: bool = False


class TaskUpdate(Loose):
    pass


# ——— Sozlamalar / davomat / AI ———


class SettingsIn(Loose):
    pass


# ——— Analitika maqsadi ———


class AnalyticsGoalIn(BaseModel):
    monthlyTarget: float = Field(ge=0)


class AttendanceOut(BaseModel):
    model_config = ConfigDict(extra="allow")


class AiChatIn(BaseModel):
    message: str
    history: list[dict[str, Any]] = Field(default_factory=list)


class AiChatOut(BaseModel):
    title: str | None = None
    lines: list[str] = Field(default_factory=list)
    text: str = ""
    source: str = "local"