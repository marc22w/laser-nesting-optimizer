"""Porneste aplicatia web fara browser si apasa butonul demo."""
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parent.parent / "app.py")


def test_aplicatia_porneste():
    at = AppTest.from_file(APP, default_timeout=60).run()
    assert not at.exception


def test_butonul_demo():
    at = AppTest.from_file(APP, default_timeout=120).run()
    demo = next(b for b in at.button if "demo" in b.label)
    demo.click().run()
    assert not at.exception
    rez = at.session_state["rezultat"]
    assert rez is not None and rez.numar_piese == 13
