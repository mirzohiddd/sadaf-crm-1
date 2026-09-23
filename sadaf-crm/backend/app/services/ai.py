"""AI yordamchi.

Ikki rejimda ishlaydi:

1. ANTHROPIC_API_KEY berilgan bo'lsa — haqiqiy model chaqiriladi va unga
   CRM search funksiyalari *tool* sifatida beriladi. Model o'zi kerakli
   funksiyani chaqiradi, biz natijani qaytaramiz.
2. Kalit berilmagan bo'lsa — offline (rule-based) tahlilchi ishlaydi.
   CRM shu holatda ham to'liq ishlaydi, faqat javoblar sodda bo'ladi.

MUHIM: tool funksiyalari HAR DOIM joriy foydalanuvchi bilan chaqiriladi.
Model qanday so'ramasin, operator o'z doirasidan tashqaridagi ma'lumotni
ololmaydi — filtrlash crm.py ichida, model qaroridan mustaqil bajariladi.
"""
from __future__ import annotations

import json
from typing import Any

import httpx

from .. import storage
from ..config import AI_MAX_TOKENS, ANTHROPIC_BASE_URL, ANTHROPIC_MODEL, ANTHROPIC_API_KEY, ai_enabled
from ..security import ROLE_LABELS
from . import crm

MAX_TOOL_ROUNDS = 5


# ——————————————————————————————————————————————————————————
#  Tool ta'riflari
# ——————————————————————————————————————————————————————————

TOOLS: list[dict[str, Any]] = [
    {
        "name": "search_leads",
        "description": "CRM dagi leadlarni qidiradi. Ism, telefon, tur yoki izoh bo'yicha.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Qidiruv so'zi (ism, telefon, tur)"},
                "stage": {"type": "string", "description": "Bosqich nomi, masalan 'Yangi'"},
                "source": {"type": "string", "description": "Manba: Telegram, Instagram, Sayt, Qo'ng'iroq"},
                "period": {"type": "string", "enum": ["today", "week", "month", ""], "description": "Davr filtri"},
                "limit": {"type": "integer", "description": "Nechta yozuv (standart 25)"},
            },
        },
    },
    {
        "name": "search_clients",
        "description": "Mijozlar bazasidan qidiradi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "country": {"type": "string"},
                "status": {"type": "string", "description": "Faol, Yangi yoki Sovuq"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "search_sales",
        "description": "Yopilgan savdolarni qidiradi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "period": {"type": "string", "enum": ["today", "month", ""]},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "search_tasks",
        "description": "Vazifalarni qidiradi.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "only_open": {"type": "boolean", "description": "Faqat bajarilmaganlari"},
                "mine": {"type": "boolean", "description": "Faqat menga berilganlari"},
                "limit": {"type": "integer"},
            },
        },
    },
    {
        "name": "get_dashboard_stats",
        "description": "Umumiy CRM ko'rsatkichlari: leadlar, daromad, konversiya, manbalar, top yo'nalishlar.",
        "input_schema": {
            "type": "object",
            "properties": {"period": {"type": "string", "enum": ["today", "week", "month"]}},
        },
    },
    {
        "name": "get_employee_stats",
        "description": "Bitta hodim kesimidagi natijalar. Ism berilmasa joriy foydalanuvchi olinadi.",
        "input_schema": {
            "type": "object",
            "properties": {"name": {"type": "string", "description": "Hodim ism familiyasi"}},
        },
    },
]


def run_tool(name: str, args: dict[str, Any], user: dict[str, Any]) -> Any:
    """Tool chaqiruvini bajaradi. Doim joriy foydalanuvchi doirasida."""
    args = args or {}
    try:
        if name == "search_leads":
            return crm.search_leads(
                user,
                query=str(args.get("query", "")),
                stage=str(args.get("stage", "")),
                source=str(args.get("source", "")),
                period=str(args.get("period", "")),
                limit=int(args.get("limit", 25)),
            )
        if name == "search_clients":
            return crm.search_clients(
                user,
                query=str(args.get("query", "")),
                country=str(args.get("country", "")),
                status=str(args.get("status", "")),
                limit=int(args.get("limit", 25)),
            )
        if name == "search_sales":
            return crm.search_sales(
                user,
                query=str(args.get("query", "")),
                period=str(args.get("period", "")),
                limit=int(args.get("limit", 25)),
            )
        if name == "search_tasks":
            return crm.search_tasks(
                user,
                query=str(args.get("query", "")),
                only_open=bool(args.get("only_open", False)),
                mine=bool(args.get("mine", False)),
                limit=int(args.get("limit", 25)),
            )
        if name == "get_dashboard_stats":
            return crm.get_dashboard_stats(user, period=str(args.get("period", "month")))
        if name == "get_employee_stats":
            return crm.get_employee_stats(user, name=str(args.get("name", "")))
    except Exception as exc:  # tool xatosi butun suhbatni to'xtatmasin
        return {"error": f"Funksiyani bajarishda xato: {exc}"}
    return {"error": f"Noma'lum funksiya: {name}"}


# ——————————————————————————————————————————————————————————
#  System prompt
# ——————————————————————————————————————————————————————————


def build_system(user: dict[str, Any]) -> str:
    role = user.get("role", "operator")
    scope = {
        "super_admin": "Butun tizim ma'lumotlarini ko'radi.",
        "admin": "Butun tizim ma'lumotlarini ko'radi.",
        "manager": "Faqat o'z jamoasi ma'lumotlarini ko'radi.",
        "operator": "Faqat o'ziga biriktirilgan ma'lumotlarni ko'radi.",
    }.get(role, "Faqat o'ziga biriktirilgan ma'lumotlarni ko'radi.")

    return (
        "Sen SADAF CRM — turagentlik uchun mo'ljallangan tizimning ichki yordamchisisan.\n\n"
        f"Joriy foydalanuvchi: {user.get('name')} (login: {user.get('login')}).\n"
        f"Roli: {ROLE_LABELS.get(role, role)}. {scope}\n\n"
        "Qoidalar:\n"
        "1. Foydalanuvchi qaysi tilda yozsa — o'sha tilda javob ber (o'zbek, rus yoki ingliz).\n"
        "2. Oddiy suhbatga (salomlashish, 'qalaysan', 'rahmat') tabiiy va qisqa javob ber. "
        "Bunday holatda hech qanday funksiya chaqirish shart emas.\n"
        "3. CRM ma'lumoti kerak bo'lsa — berilgan funksiyalardan foydalan. Raqamlarni o'zingdan "
        "to'qima; faqat funksiya qaytargan ma'lumotga tayan.\n"
        "4. Funksiyalar allaqachon foydalanuvchi huquqiga qarab filtrlangan. Agar natija bo'sh "
        "bo'lsa — 'ma'lumot yo'q yoki sizga ochiq emas' deb ayt, taxmin qilma.\n"
        "5. Boshqa xodimlarning parollari, login ma'lumotlari yoki maxfiy shaxsiy "
        "ma'lumotlarini hech qachon oshkor qilma.\n"
        "6. Javob qisqa va aniq bo'lsin. Ro'yxat kerak bo'lsa qisqa punktlar ishlat. "
        "Summalarni $ bilan yoz.\n"
    )


# ——————————————————————————————————————————————————————————
#  Anthropic rejimi
# ——————————————————————————————————————————————————————————


async def ask_model(message: str, history: list[dict[str, Any]], user: dict[str, Any]) -> dict[str, Any]:
    messages: list[dict[str, Any]] = []
    for turn in history[-10:]:
        role = "assistant" if turn.get("role") in ("ai", "assistant") else "user"
        content = str(turn.get("text") or turn.get("content") or "").strip()
        if content:
            messages.append({"role": role, "content": content})
    messages.append({"role": "user", "content": message})

    headers = {
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    used_tools: list[str] = []

    async with httpx.AsyncClient(timeout=60) as client:
        for _ in range(MAX_TOOL_ROUNDS):
            resp = await client.post(
                f"{ANTHROPIC_BASE_URL}/v1/messages",
                headers=headers,
                json={
                    "model": ANTHROPIC_MODEL,
                    "max_tokens": AI_MAX_TOKENS,
                    "system": build_system(user),
                    "tools": TOOLS,
                    "messages": messages,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            blocks = data.get("content", [])

            tool_uses = [b for b in blocks if b.get("type") == "tool_use"]
            if not tool_uses:
                text = "\n".join(
                    b.get("text", "") for b in blocks if b.get("type") == "text"
                ).strip()
                return {"text": text, "source": "anthropic", "tools": used_tools}

            messages.append({"role": "assistant", "content": blocks})
            results = []
            for block in tool_uses:
                used_tools.append(block.get("name", ""))
                output = run_tool(block.get("name", ""), block.get("input") or {}, user)
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.get("id"),
                        "content": json.dumps(output, ensure_ascii=False, default=str)[:12000],
                    }
                )
            messages.append({"role": "user", "content": results})

    return {
        "text": "Savolni qayta ishlashda juda ko'p qadam ketdi. Savolni soddalashtirib ko'ring.",
        "source": "anthropic",
        "tools": used_tools,
    }


# ——————————————————————————————————————————————————————————
#  Offline rejim (API kalitsiz)
# ——————————————————————————————————————————————————————————

SMALLTALK = {
    ("salom", "assalom", "hello", "привет", "hi", "hayrli"):
        "Salom! Men SADAF CRM yordamchisiman. Leadlar, mijozlar, savdolar va vazifalar "
        "bo'yicha savol bering.",
    ("qalaysan", "yaxshimisiz", "ahvol", "как дела", "how are you"):
        "Rahmat, tayyorman! CRM ma'lumotlari bo'yicha nima qiziqtiryapti?",
    ("rahmat", "tashakkur", "спасибо", "thanks"):
        "Arzimaydi! Yana savol bo'lsa yozing.",
    ("xayr", "ko'rishguncha", "пока", "bye"):
        "Xayr! Ishingizga omad.",
    ("kimsan", "sen kimsan", "nima qila olasan", "yordam", "help"):
        "Men CRM ichidagi ma'lumotlarni topaman va hisoblab beraman. Masalan: "
        "\"Ali degan mijozni top\", \"Bugun nechta lead keldi?\", \"Mening leadlarimni ko'rsat\", "
        "\"Bu oy qancha savdo bo'ldi?\", \"Eng ko'p kim sotdi?\", \"Bugungi vazifalarimni ko'rsat\".",
}


def _smalltalk(q: str) -> str | None:
    for keys, answer in SMALLTALK.items():
        if any(k in q for k in keys):
            return answer
    return None


def ask_local(message: str, user: dict[str, Any]) -> dict[str, Any]:
    q = (message or "").lower().strip()
    if not q:
        return {"title": "Savol bering", "lines": ["Masalan: \"Bugun nechta lead keldi?\""], "source": "local"}

    talk = _smalltalk(q)
    if talk:
        return {"title": None, "lines": [talk], "source": "local"}

    stats = crm.get_dashboard_stats(user)
    totals = stats["totals"]

    # Bugungi leadlar
    if "bugun" in q and ("lead" in q or "led" in q):
        rows = crm.search_leads(user, period="today", limit=50)
        lines = [f"Bugun {len(rows)} ta lead keldi."]
        lines += [f"{r.get('name')} — {r.get('source')}, {crm.money(r.get('amount'))}" for r in rows[:8]]
        return {"title": "Bugungi leadlar", "lines": lines, "source": "local"}

    # Bugungi vazifalar
    if "vazifa" in q or "task" in q or "topshiriq" in q:
        rows = crm.search_tasks(user, only_open=True, mine="mening" in q or "menga" in q, limit=20)
        lines = [f"Ochiq vazifalar: {len(rows)} ta."]
        lines += [f"{t.get('title')} — {t.get('to')} ({t.get('due','')} {t.get('time','')})" for t in rows[:8]]
        return {"title": "Vazifalar", "lines": lines, "source": "local"}

    # Savdo / daromad
    if any(k in q for k in ("savdo", "daromad", "tushum", "pul", "summa", "foyda")):
        month = crm.search_sales(user, period="month", limit=500)
        amount = sum(float(s.get("amount") or 0) for s in month)
        return {
            "title": "Savdo",
            "lines": [
                f"Bu oy {len(month)} ta savdo, jami {crm.money(amount)}.",
                f"Barcha vaqt uchun yopilgan summa: {crm.money(totals['revenue'])}.",
                f"Ochiq voronkada: {crm.money(totals['pipeline'])}.",
            ],
            "source": "local",
        }

    # Eng ko'p kim sotdi
    if any(k in q for k in ("eng ko'p kim", "kim ko'p sotdi", "eng yaxshi menejer", "kim sotdi")):
        analytics = crm.get_analytics(user)
        rows = analytics["managers"][:5]
        lines = [f"{m['name']}: {int(m['deals'])} ta lead, {crm.money(m['revenue'])}" for m in rows]
        return {"title": "Menejerlar reytingi", "lines": lines or ["Ma'lumot yo'q."], "source": "local"}

    # Mening leadlarim
    if ("mening" in q or "menga" in q or "o'zim" in q) and ("lead" in q or "led" in q):
        rows = [l for l in crm.leads_of(user) if l.get("manager") == user.get("name")]
        lines = [f"Sizga biriktirilgan {len(rows)} ta lead."]
        lines += [f"{r.get('name')} — {r.get('stage')}, {crm.money(r.get('amount'))}" for r in rows[:10]]
        return {"title": "Mening leadlarim", "lines": lines, "source": "local"}

    # Umumiy holat
    if any(k in q for k in ("umumiy", "holat", "hisobot", "statistika", "tahlil")):
        return {
            "title": "Umumiy holat",
            "lines": [
                f"{totals['leads']} ta lead, {totals['clients']} ta mijoz, {totals['tours']} ta tur.",
                f"Konversiya: {totals['conversion']}, yopilgan summa {crm.money(totals['revenue'])}.",
                f"Ochiq vazifalar: {totals['openTasks']} ta.",
            ],
            "source": "local",
        }

    # Ism bo'yicha qidiruv (mijoz yoki lead)
    words = [w for w in q.replace("?", " ").split() if len(w) > 2]
    for word in words:
        found_clients = crm.search_clients(user, query=word, limit=5)
        found_leads = crm.search_leads(user, query=word, limit=5)
        if found_clients or found_leads:
            lines = []
            for c in found_clients:
                lines.append(
                    f"Mijoz: {c.get('name')} — {c.get('phone')}, {c.get('country')}, "
                    f"{c.get('trips', 0)} sayohat, jami {crm.money(c.get('total'))}."
                )
            for l in found_leads:
                lines.append(
                    f"Lead: {l.get('name')} — {l.get('phone')}, {l.get('stage')}, "
                    f"{crm.money(l.get('amount'))}, mas'ul {l.get('manager') or '—'}."
                )
            return {"title": f"'{word}' bo'yicha topildi", "lines": lines, "source": "local"}

    return {
        "title": "Aniqlashtiring",
        "lines": [
            "Bu savolni CRM ma'lumotlaridan topa olmadim.",
            "Masalan shunday so'rang: \"Ali degan mijozni top\", \"Bugun nechta lead keldi?\", "
            "\"Bu oy qancha savdo bo'ldi?\", \"Eng ko'p kim sotdi?\".",
        ],
        "source": "local",
    }


# ——————————————————————————————————————————————————————————
#  Kirish nuqtasi
# ——————————————————————————————————————————————————————————


async def chat(message: str, history: list[dict[str, Any]], user: dict[str, Any]) -> dict[str, Any]:
    if ai_enabled():
        try:
            result = await ask_model(message, history, user)
            text = (result.get("text") or "").strip()
            if text:
                lines = [ln.strip(" -•") for ln in text.split("\n") if ln.strip()]
                return {"title": None, "lines": lines, "text": text, "source": "anthropic"}
        except Exception:
            # Model ishlamasa CRM to'xtamaydi — offline rejimga tushamiz
            pass

    result = ask_local(message, user)
    result.setdefault("text", "\n".join(result.get("lines", [])))
    return result


def save_history(user_id: int, message: str, answer: dict[str, Any]) -> None:
    """Suhbatni ai_chats.json ga yozadi."""

    def _do(rows: list[dict[str, Any]]) -> None:
        rows.insert(
            0,
            {
                "id": storage.next_id(rows),
                "userId": int(user_id),
                "message": message,
                "answer": answer.get("text") or "\n".join(answer.get("lines", [])),
                "source": answer.get("source", "local"),
                "ts": storage.now_iso(),
            },
        )
        del rows[500:]

    storage.mutate("ai_chats", _do)
