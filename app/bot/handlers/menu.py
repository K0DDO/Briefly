"""Persistent reply-keyboard menu — always wins over FSM states."""

from __future__ import annotations

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.i18n import (
    SUPPORTED_LANGS,
    btn_feed,
    btn_search,
    btn_settings,
    btn_trends,
)
from app.models import User

router = Router(name="menu")


def _strip_vs(text: str) -> str:
    """Normalize emoji variation selectors (Telegram clients differ on ⚙️ vs ⚙)."""
    return (text or "").replace("\ufe0f", "").strip()


def _menu_labels() -> dict[str, set[str]]:
    feed = set()
    search = set()
    trends = set()
    settings = set()
    for lang in SUPPORTED_LANGS:
        feed.add(_strip_vs(btn_feed(lang)))
        search.add(_strip_vs(btn_search(lang)))
        trends.add(_strip_vs(btn_trends(lang)))
        settings.add(_strip_vs(btn_settings(lang)))
    return {
        "feed": feed,
        "search": search,
        "trends": trends,
        "settings": settings,
    }


_LABELS = _menu_labels()
_ALL_MENU = frozenset().union(*_LABELS.values())


def is_main_menu_button(text: str | None) -> bool:
    return _strip_vs(text or "") in _ALL_MENU


def _which(text: str | None) -> str | None:
    key = _strip_vs(text or "")
    for name, labels in _LABELS.items():
        if key in labels:
            return name
    return None


@router.message(F.text.func(lambda s: bool(s) and _strip_vs(s) in _ALL_MENU))
async def main_menu_button(
    message: Message,
    session: AsyncSession,
    db_user: User,
    state: FSMContext,
) -> None:
    """Bottom reply keyboard — clear any FSM and open the section."""
    await state.clear()
    which = _which(message.text)
    if which == "feed":
        from app.bot.handlers.news import open_feed

        await open_feed(message, session, db_user)
        return
    if which == "search":
        from app.bot.handlers.search import ask_search
        from app.bot.states import SearchStates

        await state.set_state(SearchStates.waiting_query)
        await ask_search(message, session, db_user)
        return
    if which == "settings":
        from app.bot.handlers.settings import open_settings

        await open_settings(message, session, db_user)
        return
    if which == "trends":
        from app.bot.handlers.trends import show_trends_msg

        await show_trends_msg(message, session, db_user)
