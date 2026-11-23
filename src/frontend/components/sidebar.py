from pathlib import Path

import streamlit as st


def carregar_estilos() -> None:
    css_path = Path(__file__).resolve().parent.parent / "styles" / "main.css"
    if css_path.exists():
        css = css_path.read_text(encoding="utf-8")
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def render_rodape_vitrine() -> None:
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px; margin-bottom: 20px; opacity: 0.3;">
            <span style="font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px;">
                POWERED BY VITRINE DIGITAL
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )