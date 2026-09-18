"""Lead eslatmalari uchun fon vazifasi (background task).

Har 20 soniyada barcha eslatmalarni tekshiradi: muddati (``dueAt``) kelib,
hali ``notified`` qilinmagan eslatmalarni topib, ularni ``notified=True``
deb belgilaydi va tegishli foydalanuvchiga (eslatmani yaratgan/egasiga)
``/api/notifications`` orqali bildirishnoma yuboradi.

Eslatma: bu vazifa eslatmani "bajarilgan" (``done``) deb belgilamaydi —
faqat xabar berilganini (``notified``) belgilaydi. "Bajarildi" holatini
foydalanuvchi o'zi ``PATCH /api/reminders/{id}/done`` orqali belgilaydi.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any

from .. import storage
from . import notify

CHECK_INTERVAL_SECONDS = 20


def check_due() -> list[dict[str, Any]]:
    """Muddati kelgan va hali xabar berilmagan eslatmalarni topib,
    ``notified=True`` deb belgilaydi va bildirishnoma yuboradi.

    Xabar berilgan eslatmalar ro'yxatini qaytaradi (testlash uchun qulay).
    """
    now = datetime.now().isoformat(timespec="minutes")
    rows = storage.read("reminders")
    due = [
        r
        for r in rows
        if not r.get("done") and not r.get("notified") and str(r.get("dueAt") or "") <= now
    ]
    for reminder in due:
        storage.update("reminders", int(reminder["id"]), {"notified": True})
        owner_id = reminder.get("ownerId")
        lead_name = reminder.get("leadName") or "Lead"
        note = reminder.get("note") or ""
        notify.push(
            [owner_id] if owner_id is not None else [],
            title=f"Eslatma: {lead_name}",
            detail=note,
            kind="reminder",
            link=f"/ledlar?lead={reminder.get('leadId')}",
        )
    return due


async def run_forever() -> None:
    """Server ishlab turgan davomida davriy ravishda ``check_due()`` ni
    chaqiradi. Bitta tekshiruvdagi kutilmagan xato butun vazifani
    to'xtatmasin uchun ``try/except`` bilan o'raladi.
    """
    while True:
        try:
            check_due()
        except Exception as exc:  # noqa: BLE001
            print(f"[sadaf] Eslatmalarni tekshirishda xato: {exc}")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
