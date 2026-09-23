"""Birinchi ishga tushirishda boshlang'ich ma'lumot."""
from __future__ import annotations
from typing import Any
from . import storage
from .config import ADMIN_LOGIN, ADMIN_NAME, ADMIN_PASSWORD
from .security import ROLES, hash_password
def default_settings(user_id: int) -> dict[str, Any]:
    """Har bir account uchun alohida ko'rinish sozlamalari."""
    return {
        "userId": int(user_id),
        "appearance": {
            "mode": "color",
            "color": "#f4f7fb",
            "image": "",
            "imageSrcset": "",
            "dim": 0,
            "accent": "#f08a63",
            "cardSolidity": 82,
        },
        "sidebarCollapsed": False,
        "language": "uz",
    }
def ensure_settings(user_id: int) -> dict[str, Any]:
    rows = storage.read("settings")
    for row in rows:
        if int(row.get("userId", 0)) == int(user_id):
            return row
    return storage.insert("settings", default_settings(user_id))

def default_analytics_goal() -> dict[str, Any]:
    return {
        "monthlyTarget": 50000,
        "updatedBy": None,
        "updatedByName": "",
    }


def ensure_analytics_goal() -> dict[str, Any]:
    rows = storage.read("analytics_goals")
    if rows:
        return rows[0]
    return storage.insert("analytics_goals", default_analytics_goal())
def ensure_super_admin(login: str, password: str, name: str) -> None:
    """Berilgan login bilan super admin mavjud bo'lmasa — yaratadi."""
    users = storage.read("users")
    if any(u.get("login") == login for u in users):
        return
    admin = storage.insert(
        "users",
        {
            "name": name,
            "login": login,
            "passwordHash": hash_password(password),
            "role": "super_admin",
            "email": f"{login}@sadaf.uz",
            "phone": "+998 90 000 00 00",
            "position": "Administrator",
            "shift": "To'liq kun",
            "status": "Ishlayapti",
            "birthDate": "",
            "hireDate": storage.today_uz(),
            "address": "",
            "deals": 0,
            "managerId": None,
            "active": True,
        },
    )
    ensure_settings(int(admin["id"]))
    print(f"[seed] Super Admin yaratildi — login: {login}")


def _normalize_roles() -> None:
    """Ba'zan (masalan eski/qo'lda tahrirlangan ``users.json``da) rol
    "Super_Admin" kabi noto'g'ri katta-kichik harfda saqlanib qolishi
    mumkin — bu holda foydalanuvchi to'g'ri login/parol bilan kirsa ham,
    tizim uni "super_admin" deb tanimay, oddiy hodim huquqlari bilan
    ko'rsatadi (chunki barcha ruxsat tekshiruvlari aniq ``"super_admin"``
    satriga qarab solishtiradi). Bu funksiya har ishga tushishda mos
    kelmagan yozuvlarni avtomatik tuzatadi.
    """
    canonical = {r.lower(): r for r in ROLES}
    for u in storage.read("users"):
        role = u.get("role")
        if role and role not in ROLES:
            fixed = canonical.get(str(role).strip().lower())
            if fixed:
                storage.update("users", int(u["id"]), {"role": fixed})
                print(f"[seed] Rol tuzatildi: {u.get('login')} — '{role}' -> '{fixed}'")


def run() -> None:
    storage.ensure_files()
    _normalize_roles()
    users = storage.read("users")
    if not any(u.get("role") == "super_admin" for u in users):
        ensure_super_admin(ADMIN_LOGIN, ADMIN_PASSWORD, ADMIN_NAME)

    ensure_super_admin("menejer", "12345", "Menejer")