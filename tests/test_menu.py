"""Main reply-keyboard menu matching."""

from app.bot.handlers.menu import _strip_vs, is_main_menu_button
from app.bot.i18n import btn_feed, btn_settings


def test_menu_buttons_match_with_and_without_variation_selector():
    assert is_main_menu_button(btn_feed("ru"))
    assert is_main_menu_button(btn_settings("ru"))
    # Clients may drop U+FE0F on the gear emoji
    assert is_main_menu_button(_strip_vs(btn_settings("en")))
    assert is_main_menu_button("⚙ " + btn_settings("ru").split(" ", 1)[-1].replace("\ufe0f", ""))
    assert not is_main_menu_button("hello")
    assert not is_main_menu_button(None)
