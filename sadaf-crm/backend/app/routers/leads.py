"""/api/leads — ledlar, bosqichlar va avtomatik savdo yozuvi."""
from __future__ import annotations

import re
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from .. import storage
from ..deps import ensure_access, is_global, require, scope_rows
from ..schemas import LeadIn, Loose, StageIn
from ..services import notify
from ..services import assignment
from ..services.crm import WON_STAGES

router = APIRouter(prefix="/api/leads", tags=["leads"])

STAGES = (
    "Yangi", "Mijoz bilan bog'lanilmadi", "Bog'lanildi", "Taklif yuborildi",
    "To'lov qilindi", "Bron tasdiqlandi", "Bekor qilindi", "Sifatsiz lead",
)

# Lead shu bosqichga o'tganda Mijozlar bazasiga avtomatik qo'shiladi.
BOOKED_STAGE = "Bron tasdiqlandi"


def _managers_of(name: str) -> list[int]:
    """Lead mas'uli va adminlarning id ro'yxati (bildirishnoma uchun)."""
    ids = [int(u["id"]) for u in storage.read("users") if u.get("name") == name]
    return ids


def _sync_sale(lead: dict[str, Any]) -> None:
    """Lead yopilganda sales.json ga yozuv qo'shadi (takrorlanmaydi)."""
    sales = storage.read("sales")
    exists = any(int(s.get("leadId", 0)) == int(lead["id"]) for s in sales)
    won = lead.get("stage") in WON_STAGES

    if won and not exists:
        storage.insert(
            "sales",
            {
                "leadId": int(lead["id"]),
                "client": lead.get("name", ""),
                "phone": lead.get("phone", ""),
                "tour": lead.get("tour", ""),
                "people": lead.get("people", 1),
                "amount": float(lead.get("amount") or 0),
                "manager": lead.get("manager", ""),
                "ownerId": lead.get("ownerId"),
                "source": lead.get("source", ""),
                "stage": lead.get("stage"),
                "date": lead.get("date") or storage.today_uz(),
            },
        )
    elif not won and exists:
        storage.write("sales", [s for s in sales if int(s.get("leadId", 0)) != int(lead["id"])])


def _digits(phone: Any) -> str:
    return re.sub(r"\D", "", str(phone or ""))


def _find_client_by_phone(phone: Any) -> dict[str, Any] | None:
    """Telefon raqami bo'yicha mavjud mijozni topadi (formatdan qat'i nazar)."""
    target = _digits(phone)
    if not target:
        return None
    for c in storage.read("clients"):
        if _digits(c.get("phone")) == target:
            return c
    return None


def _sync_client(lead: dict[str, Any]) -> None:
    """Lead "Bron tasdiqlandi" bosqichiga o'tganda Mijozlar bazasiga
    avtomatik qo'shadi (yoki mavjud mijozni yangilaydi).

    - Telefon raqami bo'yicha dublikat mijoz yaratilmaydi.
    - leadId, mas'ul (admin/manager) va telefon raqami saqlanadi.
    - Mijozni qo'lda kiritish bilan hech qanday to'qnashuv bo'lmaydi —
      bu funksiya faqat shu lead uchun mos yozuvni yaratadi/yangilaydi.
    """
    if lead.get("stage") != BOOKED_STAGE:
        return

    phone = lead.get("phone", "")
    existing = _find_client_by_phone(phone)

    patch: dict[str, Any] = {
        "name": lead.get("name", ""),
        "phone": phone,
        "leadId": int(lead["id"]),
        "manager": lead.get("manager", ""),
        "ownerId": lead.get("ownerId"),
        "source": lead.get("source", ""),
        "lastTour": lead.get("tour", ""),
        "lastDate": lead.get("date") or storage.today_uz(),
    }

    if existing:
        storage.update("clients", int(existing["id"]), patch)
    else:
        patch.setdefault("country", "")
        patch.setdefault("trips", 0)
        patch.setdefault("total", 0)
        patch.setdefault("status", "Faol")
        patch.setdefault("vip", False)
        storage.insert("clients", patch)


@router.get("")
def list_leads(user: dict[str, Any] = Depends(require("leads", "read"))) -> list[dict[str, Any]]:
    return scope_rows(storage.read("leads"), user, resource="leads")


@router.get("/stages")
def list_stages(user: dict[str, Any] = Depends(require("leads", "read"))) -> list[str]:
    return list(STAGES)


@router.get("/new-count")
def new_leads_count(user: dict[str, Any] = Depends(require("leads", "read"))) -> dict[str, int]:
    """Joriy foydalanuvchi hali ko'rmagan leadlar soni ("Ledlar" menyusidagi belgi).

    - Har bir admin uchun alohida hisoblanadi (lead.seenBy ro'yxatiga qarab).
    - Super Admin uchun scope_rows orqali barcha leadlar hisobga olinadi,
      oddiy Admin/menejer uchun faqat o'ziga tegishli leadlar.
    - "seenBy" maydoni umuman yo'q eski (funksiya qo'shilishidan oldingi)
      leadlar allaqachon ko'rilgan deb hisoblanadi — birdaniga katta son
      chiqib ketmasligi uchun.
    """
    rows = scope_rows(storage.read("leads"), user, resource="leads")
    uid = int(user["id"])
    count = sum(1 for row in rows if row.get("seenBy") is not None and uid not in row["seenBy"])
    return {"count": count}


@router.patch("/{lead_id}/seen")
def mark_lead_seen(lead_id: int, user: dict[str, Any] = Depends(require("leads", "read"))) -> dict[str, Any]:
    """Joriy foydalanuvchi shu leadni ko'rdi — endi u uning uchun yangi hisoblanmaydi."""
    current = ensure_access(storage.get_one("leads", lead_id), user, resource="leads")
    uid = int(user["id"])
    seen = list(current.get("seenBy") or [])
    if uid in seen:
        return current
    seen.append(uid)
    return storage.update("leads", lead_id, {"seenBy": seen}) or current


@router.get("/assignment")
def assignment_state(user: dict[str, Any] = Depends(require("leads", "read"))) -> dict[str, Any]:
    """Round-robin navbatining joriy holati — faqat Super Admin ko'ra oladi.

    Har bir lead qaysi adminga biriktirilgani lead.manager maydonida
    ko'rinadi (Super Admin uchun to'liq ro'yxat GET /api/leads orqali
    allaqachon ochiq); bu endpoint esa navbatning o'zini — kim faol
    admin ekanini va keyingi lead kimga tegishini — ko'rsatadi.
    """
    if not is_global(user, "leads"):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Faqat Super Admin ko'ra oladi.")
    admins = assignment.active_admins()
    upcoming = assignment.peek_next_admin()
    return {
        "activeAdmins": [{"id": int(a["id"]), "name": a.get("name", "")} for a in admins],
        "nextAdminId": int(upcoming["id"]) if upcoming else None,
        "nextAdminName": upcoming.get("name", "") if upcoming else None,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_lead(body: LeadIn, user: dict[str, Any] = Depends(require("leads", "write"))) -> dict[str, Any]:
    data = body.model_dump()
    data.setdefault("date", storage.today_uz())
    data.setdefault("time", storage.now_time())
    data["ownerId"] = int(user["id"])
    # Yaratuvchi leadni allaqachon ko'rgan hisoblanadi — badge unga yangi
    # ko'rsatilmaydi, boshqa barcha adminlar uchun esa "yangi" bo'lib qoladi.
    data["seenBy"] = [int(user["id"])]

    # Operator va oddiy Admin leadni faqat o'ziga biriktira oladi — "Mas'ul
    # odam"ni tanlay olmaydi. Faqat Super Admin (leads uchun global rol)
    # leadni istalgan adminga/hodimga biriktira oladi.
    if not is_global(user, "leads") and user.get("role") in ("operator", "admin"):
        data["manager"] = user.get("name", "")
    elif not data.get("manager"):
        # Super Admin "Mas'ul odam"ni tanlamasa — lead aktiv adminlar
        # orasida navbat bilan (round-robin) avtomatik taqsimlanadi.
        assigned = assignment.next_admin()
        data["manager"] = assigned.get("name", "") if assigned else user.get("name", "")

    created = storage.insert("leads", data)
    _sync_sale(created)
    _sync_client(created)

    notify.log(user.get("name", ""), "create", "lead", created.get("name", ""),
               {"amount": created.get("amount", 0)}, actor_id=int(user["id"]))
    notify.broadcast_admins(
        "Yangi lead",
        f"{created.get('name')} — {created.get('source')} · {created.get('tour') or '—'}",
        exclude=int(user["id"]),
        amount=float(created.get("amount") or 0),
        kind="lead",
        link="/ledlar",
    )
    targets = [i for i in _managers_of(created.get("manager", "")) if i != int(user["id"])]
    notify.push(targets, "Sizga yangi lead biriktirildi", created.get("name", ""),
                amount=float(created.get("amount") or 0), kind="lead", link="/ledlar")
    return created


@router.put("/{lead_id}")
def update_lead(
    lead_id: int, body: Loose, user: dict[str, Any] = Depends(require("leads", "write"))
) -> dict[str, Any]:
    current = ensure_access(storage.get_one("leads", lead_id), user, resource="leads")
    # "seenBy" faqat /seen endpoint orqali o'zgaradi — oddiy tahrirlash uni
    # qayta yozib yubormasligi kerak (frontend forma lead obyektini to'liq
    # nusxalab yuborgani uchun bu maydon patch ichida bo'lishi mumkin).
    patch = {k: v for k, v in body.model_dump().items() if k not in ("id", "ownerId", "seenBy")}

    # Operator va oddiy Admin "Mas'ul odam"ni o'zgartira olmaydi — bu maydon
    # faqat Super Admin uchun ochiq.
    if not is_global(user, "leads") and user.get("role") in ("operator", "admin"):
        patch.pop("manager", None)

    updated = storage.update("leads", lead_id, patch)
    if updated:
        _sync_sale(updated)
        _sync_client(updated)
    notify.log(user.get("name", ""), "update", "lead", (updated or current).get("name", ""),
               actor_id=int(user["id"]))
    return updated or current


@router.patch("/{lead_id}/stage")
def move_stage(
    lead_id: int, body: StageIn, user: dict[str, Any] = Depends(require("leads", "write"))
) -> dict[str, Any]:
    current = ensure_access(storage.get_one("leads", lead_id), user, resource="leads")
    if body.stage not in STAGES:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"Noma'lum bosqich: {body.stage}")

    old = current.get("stage")
    if old == body.stage:
        return current

    history = list(current.get("history") or [])
    history.append(
        {
            "title": body.stage,
            "date": f"{storage.today_uz()} {storage.now_time()}",
            "author": user.get("name", ""),
            "text": f"{old} → {body.stage}",
            "color": "bg-emerald-500",
        }
    )
    updated = storage.update("leads", lead_id, {"stage": body.stage, "history": history})
    if updated:
        _sync_sale(updated)
        _sync_client(updated)

    notify.log(user.get("name", ""), "stage", "lead", current.get("name", ""),
               {"from": old, "to": body.stage, "amount": current.get("amount", 0)},
               actor_id=int(user["id"]))

    if body.stage in WON_STAGES:
        notify.broadcast_admins(
            "Bitim yopildi",
            f"{current.get('name')} — {body.stage}",
            exclude=int(user["id"]),
            amount=float(current.get("amount") or 0),
            kind="sale",
            link="/ledlar",
        )
    return updated or current


@router.delete("/{lead_id}")
def delete_lead(lead_id: int, user: dict[str, Any] = Depends(require("leads", "delete"))) -> dict[str, Any]:
    current = ensure_access(storage.get_one("leads", lead_id), user, resource="leads")
    storage.delete("leads", lead_id)
    storage.write("sales", [s for s in storage.read("sales") if int(s.get("leadId", 0)) != int(lead_id)])
    notify.log(user.get("name", ""), "delete", "lead", current.get("name", ""), actor_id=int(user["id"]))
    return {"ok": True, "id": lead_id}