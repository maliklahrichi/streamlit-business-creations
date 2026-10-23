"""Visual identity: injects assets/style.css into the page.

Fonts and theme colours are declared in .streamlit/config.toml (fonts are served
from ./static/fonts); the stylesheet only handles what the theme cannot.
"""
import streamlit as st

from utils import constants as C

CSS_PATH = C.ROOT / "assets" / "style.css"


def inject_css() -> None:
    st.html(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>")
