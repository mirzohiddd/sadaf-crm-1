"""/api/integrations/sheets — Google Sheets → CRM lead integratsiyasi.

Oqim bir tomonlama: Google Sheetsga yangi qator (lead) tushganda, o'sha
jadvalga ulangan Apps Script trigger shu endpointga POST so'rov yuboradi
va CRM avtomatik lead yaratadi. CRM Google Sheetsga hech narsa yozmaydi —
jadvaldagi mavjud ma'lumotlar hech qachon o'zgartirilmaydi yoki o'chirilmaydi.

Bu odatdagi login/JWT bilan himoyalangan endpointlardan farqli — uni
chaqiruvchi (Apps Script) tizimga "hodim" sifatida kirmaydi, shuning uchun
alohida maxfiy kalit (X-Sheets-Secret header) bilan himoyalangan.

Jadval Meta (Facebook/Instagram) Lead Ads eksporti bo'lishi mumkin — bunda
har qatorda platform, campaign, ad va lead_status kabi ustunlar ham bo'ladi.
Bu maydonlar mavjud bo'lsa, lead yozuviga qo'shimcha ma'lumot sifatida
saqlanadi (mavjud Leads strukturasi buzilmaydi — faqat qo'shimcha maydonlar).

Google Sheets tomonidagi sozlash (Apps Script namunasi) uchun:
    backend/scripts/google-sheets-webhook.gs
"""
from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Header, HTTPException, status

from .. import storage
from ..config import (
    SHEETS_DEFAULT_SOURCE,
    SHEETS_WEBHOOK_SECRET,
    WEBSITE_DEFAULT_SOURCE,
    WEBSITE_WEBHOOK_SECRET,
)
from ..schemas import SheetLeadIn, WebsiteLeadIn
from ..services import assignment, notify
from . import leads as leads_router  # _sync_sale / _sync_client qayta ishlatish uchun

router = APIRouter(prefix="/api/integrations", tags=["integrations"])

# Meta jadvalidagi "platform" ustuni qisqartmalarini CRM'dagi Manba (source)
# nomlariga moslashtiradi — SourceTag.vue shu nomlarni tanib rangli belgi chizadi.
PLATFORM_LABELS = {
    "ig": "Instagram",
    "instagram": "Instagram",
    "fb": "Facebook",
    "facebook": "Facebook",
}


def _digits(phone: Any) -> str:
    return re.sub(r"\D", "", str(phone or ""))


def _find_lead_by_phone(phone: Any) -> dict[str, Any] | None:
    """Telefon raqami bo'yicha mavjud leadni topadi (format farqidan qat'i nazar)."""
    target = _digits(phone)
    if not target:
        return None
    for lead in storage.read("leads"):
        if _digits(lead.get("phone")) == target:
            return lead
    return None


def _find_lead_by_external_id(external_id: Any) -> dict[str, Any] | None:
    """Meta lead ID'si bo'yicha mavjud leadni topadi (eng ishonchli dublikat tekshiruvi)."""
    if not external_id:
        return None
    for lead in storage.read("leads"):
        if str(lead.get("externalId") or "") == str(external_id):
            return lead
    return None


def _split_created_time(created_time: str) -> tuple[str, str]:
    """ISO 8601 ("2026-08-06T07:39:23-05:00") ni CRM formatiga o'giradi:
    sana — DD.MM.YYYY, vaqt — HH:MM. Parslab bo'lmasa — hozirgi sana/vaqt.
    """
    if created_time:
        try:
            dt = datetime.fromisoformat(created_time.strip())
            return dt.strftime("%d.%m.%Y"), dt.strftime("%H:%M")
        except ValueError:
            pass
    return storage.today_uz(), storage.now_time()


def _check_secret(x_sheets_secret: str | None) -> None:
    if not x_sheets_secret or x_sheets_secret != SHEETS_WEBHOOK_SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Noto'g'ri yoki yo'q maxfiy kalit.")


@router.post("/sheets/lead", status_code=status.HTTP_201_CREATED)
def create_lead_from_sheet(
    body: SheetLeadIn,
    x_sheets_secret: str | None = Header(default=None, alias="X-Sheets-Secret"),
) -> dict[str, Any]:
    """Google Sheetsdan kelgan bitta qatorni CRM lead sifatida yaratadi.

    - Duplikat: avval Meta lead ID (``externalId``) bo'yicha, u bo'lmasa
      telefon raqami bo'yicha mos lead allaqachon bo'lsa — yangisi
      yaratilmaydi, mavjudi qaytariladi (``duplicate: true``).
    - Har bir yangi leadga: unique ID (storage avtomatik beradi), sana,
      vaqt, source va status (bosqich — "Yangi") avtomatik beriladi.
    - Sana/vaqt jadvaldagi ``createdTime`` (Meta eksporti) berilgan bo'lsa
      o'shandan olinadi, aks holda hozirgi vaqt ishlatiladi.
    - Manba (``source``): agar jadvalda aniq ``source`` berilmagan bo'lsa,
      ``platform`` ustunidan ("ig"/"fb") avtomatik chiqariladi.
    - Meta-ga xos maydonlar (platform, campaign, ad, leadStatus, formName,
      externalId) leadga qo'shimcha maydon sifatida saqlanadi — mavjud
      Leads strukturasi (name/phone/tour/stage/...) o'zgarmaydi.
    - Lead aktiv adminlar orasida navbat bilan (round-robin) avtomatik
      biriktiriladi — Super Admin keyinchalik kerak bo'lsa qayta
      biriktirishi mumkin.
    """
    _check_secret(x_sheets_secret)

    name = body.name.strip()
    phone = body.phone.strip()
    if not name or not phone:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Lead uchun ism va telefon shart.")

    external_id = body.externalId.strip()
    existing = _find_lead_by_external_id(external_id) or _find_lead_by_phone(phone)
    if existing:
        return {"ok": True, "duplicate": True, "lead": existing}

    # Aktiv adminlar orasida navbat bilan (round-robin) biriktiriladi.
    assigned = assignment.next_admin()

    platform = body.platform.strip()
    source = body.source.strip() or PLATFORM_LABELS.get(platform.lower(), platform) or SHEETS_DEFAULT_SOURCE
    date, time = _split_created_time(body.createdTime)

    data: dict[str, Any] = {
        "name": name,
        "phone": phone,
        "tour": body.tour,
        "people": body.people or 1,
        "amount": body.amount or 0,
        "comment": body.comment,
        "city": body.city,
        "telegram": body.telegram,
        "source": source,
        "stage": leads_router.STAGES[0],  # "Yangi" — standart boshlang'ich status
        "manager": assigned.get("name", "") if assigned else "",
        "ownerId": None,     # avtomatik yaratilgan — inson egasi yo'q
        "seenBy": [],        # hamma admin uchun "yangi" badge sifatida ko'rinadi
        "date": date,
        "time": time,
    }
    # Meta (Facebook/Instagram) Lead Ads maydonlari — faqat berilgan bo'lsa qo'shiladi.
    if platform:
        data["platform"] = platform
    if body.campaign.strip():
        data["campaign"] = body.campaign.strip()
    if body.ad.strip():
        data["ad"] = body.ad.strip()
    if body.leadStatus.strip():
        data["leadStatus"] = body.leadStatus.strip()
    if body.formName.strip():
        data["formName"] = body.formName.strip()
    if external_id:
        data["externalId"] = external_id
    if body.rowId is not None:
        data["sheetRowId"] = body.rowId

    created = storage.insert("leads", data)
    # Ehtiyot chorasi: agar kelajakda Sheetdan to'g'ridan-to'g'ri "Bron
    # tasdiqlandi" kabi yopilgan bosqich yuborilsa ham, savdo/mijoz
    # sinxronizatsiyasi odatdagidek ishlaydi (hozircha stage har doim "Yangi").
    leads_router._sync_sale(created)
    leads_router._sync_client(created)

    notify.log("Google Sheets", "create", "lead", created.get("name", ""),
               {"amount": created.get("amount", 0)}, actor_id=None)
    notify.broadcast_admins(
        "Yangi lead (Google Sheets)",
        f"{created.get('name')} — {created.get('source')} · {created.get('tour') or '—'}",
        amount=float(created.get("amount") or 0),
        kind="lead",
        link="/ledlar",
    )

    return {"ok": True, "duplicate": False, "lead": created}


def _check_website_secret(x_website_secret: str | None) -> None:
    if not x_website_secret or x_website_secret != WEBSITE_WEBHOOK_SECRET:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Noto'g'ri yoki yo'q maxfiy kalit.")


@router.post("/website/lead", status_code=status.HTTP_201_CREATED)
def create_lead_from_website(
    body: WebsiteLeadIn,
    x_website_secret: str | None = Header(default=None, alias="X-Website-Secret"),
) -> dict[str, Any]:
    """Lead Form (``sadaf-landing``) dan kelgan arizani CRM lead sifatida yaratadi.

    Bu endpoint login qilinmagan tashrifchi tomonidan chaqiriladi (forma
    JWT bilan ishlamaydi), shuning uchun ``/api/leads`` (JWT talab qiladigan
    ichki CRM endpointi) o'rniga alohida, maxfiy kalit (``X-Website-Secret``)
    bilan himoyalangan yo'l ishlatiladi. Mavjud ``/api/leads`` va Google
    Sheets webhooki hech qanday o'zgarishsiz qoladi.

    - Duplikat oldini olish: telefon raqami bo'yicha (formatdan qat'i
      nazar) — agar shu raqamda lead allaqachon bo'lsa, yangisi
      yaratilmaydi, mavjudi ``duplicate: true`` bilan qaytariladi.
    - ``destination`` → mavjud ``tour`` maydoniga yoziladi (Leads jadvalida
      "Tur" ustunida ko'rinadi).
    - ``travelDate`` → alohida saqlanadi va "Izoh" ustunida ham ko'rinadi.
    - Lead darhol ``createdAt``/``date``/``time`` bilan, "Yangi" bosqichda
      va aktiv adminlar orasida navbat bilan (round-robin) biriktirilgan
      holda yaratiladi — CRM ochiq oynalarga WebSocket orqali zudlik bilan
      bildirishnoma boradi (qo'shimcha sozlash shart emas).
    """
    _check_website_secret(x_website_secret)

    name = body.name.strip()
    phone = body.phone.strip()
    if not name or not phone:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Lead uchun ism va telefon shart.")

    existing = _find_lead_by_phone(phone)
    if existing:
        return {"ok": True, "duplicate": True, "lead": existing}

    assigned = assignment.next_admin()
    now_iso = datetime.now().astimezone().isoformat()

    comment_parts = []
    if body.travelDate:
        comment_parts.append(f"Reja qilingan sana: {body.travelDate}")
    if body.utm_source or body.utm_campaign:
        comment_parts.append(
            f"UTM: {body.utm_source or '—'} / {body.utm_medium or '—'} / {body.utm_campaign or '—'}"
        )

    data: dict[str, Any] = {
        "name": name,
        "phone": phone,
        "tour": body.destination.strip(),
        "people": 1,
        "amount": 0,
        "comment": " · ".join(comment_parts),
        "source": WEBSITE_DEFAULT_SOURCE,
        "stage": leads_router.STAGES[0],  # "Yangi" — standart boshlang'ich status
        "manager": assigned.get("name", "") if assigned else "",
        "ownerId": None,      # avtomatik yaratilgan — inson egasi yo'q
        "seenBy": [],         # hamma admin uchun "yangi" badge sifatida ko'rinadi
        "date": storage.today_uz(),
        "time": storage.now_time(),
        "createdAt": now_iso,
    }
    # Ariza formasidagi qo'shimcha maydonlar — mavjud Leads strukturasi
    # (name/phone/tour/stage/...) o'zgarmaydi, faqat qo'shimcha saqlanadi.
    if body.travelDate:
        data["travelDate"] = body.travelDate
    for field in ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term"):
        value = getattr(body, field)
        if value:
            data[field] = value

    created = storage.insert("leads", data)
    leads_router._sync_sale(created)
    leads_router._sync_client(created)

    notify.log("Lead Form", "create", "lead", created.get("name", ""),
               {"amount": created.get("amount", 0)}, actor_id=None)
    notify.broadcast_admins(
        "Yangi lead (Sayt arizasi)",
        f"{created.get('name')} — {created.get('source')} · {created.get('tour') or '—'}",
        amount=float(created.get("amount") or 0),
        kind="lead",
        link="/ledlar",
    )

    return {"ok": True, "duplicate": False, "lead": created}