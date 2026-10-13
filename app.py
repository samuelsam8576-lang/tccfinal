from __future__ import annotations

import html
import io
import re
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from typing import Any, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

try:
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split
except Exception:  # pragma: no cover
    RandomForestRegressor = None
    mean_absolute_error = None
    r2_score = None
    train_test_split = None

st.set_page_config(page_title="EcoRadar | Partículas no ar e qualidade da água", page_icon="🌊", layout="wide")

def obter_css_tema(modo_visual: str) -> str:
    if modo_visual == "Noturno":
        return """
        <style>
        :root {
            --bg-main: #030916;
            --bg-secondary: #071427;
            --panel: rgba(7, 21, 39, 0.92);
            --panel-soft: rgba(7, 21, 39, 0.78);
            --panel-strong: rgba(5, 18, 35, 0.96);
            --line: rgba(100, 181, 246, 0.18);
            --line-strong: rgba(148, 197, 255, 0.30);
            --text-main: #eef6ff;
            --text-soft: #9fc1e3;
            --text-muted: #6f93b6;
            --accent: #4cc9f0;
            --accent-2: #2f80ed;
            --shadow: 0 18px 40px rgba(0, 0, 0, 0.28);
            --radius-xl: 28px;
            --radius-lg: 22px;
            --radius-md: 18px;
        }
        html, body, [class*="css"]  {
            font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }
        .stApp {
            background:
                radial-gradient(circle at 15% 0%, rgba(44, 130, 201, 0.16), transparent 24%),
                radial-gradient(circle at 100% 0%, rgba(65, 182, 230, 0.18), transparent 20%),
                linear-gradient(180deg, #020611 0%, #05111f 50%, #020814 100%);
            color: var(--text-main);
        }
        .block-container {
            padding-top: 1rem;
            padding-bottom: 2.4rem;
            max-width: 1380px;
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #031020 0%, #07182b 100%);
            border-right: 1px solid rgba(120, 180, 255, 0.12);
            min-width: 340px !important;
            max-width: 340px !important;
        }
        [data-testid="stSidebar"] * {
            color: #ebf5ff;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] .stTextInput input,
        [data-testid="stSidebar"] .stNumberInput input,
        [data-testid="stSidebar"] .stDateInput input,
        [data-testid="stSidebar"] .stSlider,
        [data-testid="stSidebar"] [data-baseweb="base-input"] {
            background: rgba(255,255,255,0.04) !important;
            border-radius: 14px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
        }
        [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {
            gap: 0.4rem;
        }
        [data-testid="stSidebar"] .stRadio label {
            background: rgba(255,255,255,0.04);
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.10);
        }
        .hero-box {
            background:
                radial-gradient(circle at 90% 10%, rgba(118, 211, 255, 0.18), transparent 26%),
                linear-gradient(100deg, rgba(3, 14, 33, 0.98) 0%, rgba(7, 32, 58, 0.98) 48%, rgba(59, 156, 197, 0.92) 100%);
            color: white;
            border-radius: var(--radius-xl);
            padding: 28px 28px 22px 28px;
            margin-bottom: 1rem;
            box-shadow: 0 24px 60px rgba(0, 6, 18, 0.42);
            border: 1px solid rgba(152, 219, 255, 0.14);
            position: relative;
            overflow: hidden;
        }
        .hero-box::after {
            content: "";
            position: absolute;
            right: -40px;
            top: -40px;
            width: 300px;
            height: 300px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(155, 223, 255, 0.16), transparent 60%);
            pointer-events: none;
        }
        .hero-copy {
            position: relative;
            z-index: 1;
        }
        .hero-box h1 {
            margin: 0;
            font-size: 2.05rem;
            line-height: 1.08;
            letter-spacing: -0.04em;
            color: #ffffff;
        }
        .hero-subtitle {
            margin-top: 0.35rem;
            font-size: 0.95rem;
            color: rgba(235, 245, 255, 0.88);
        }
        .hero-badges {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }
        .hero-badge {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.72);
            border-radius: 999px;
            padding: 0.38rem 0.82rem;
            font-size: 0.84rem;
            font-weight: 600;
            color: #f8fbff;
            backdrop-filter: blur(6px);
        }
        .top-kpi-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.9rem;
            margin-bottom: 1rem;
        }
        .top-kpi-card {
            background: linear-gradient(180deg, rgba(4, 16, 31, 0.94) 0%, rgba(6, 22, 42, 0.88) 100%);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            box-shadow: var(--shadow);
            min-height: 124px;
            position: relative;
            overflow: hidden;
        }
        .top-kpi-card::before {
            content: "";
            position: absolute;
            inset: 0 auto auto 0;
            width: 100%;
            height: 1px;
            background: linear-gradient(90deg, rgba(87, 170, 255, 0.0), rgba(118, 211, 255, 0.75), rgba(87, 170, 255, 0.0));
            opacity: 0.5;
        }
        .kpi-label {
            display: flex;
            align-items: center;
            gap: 0.35rem;
            font-size: 0.73rem;
            text-transform: uppercase;
            letter-spacing: 0.11em;
            color: var(--text-soft);
            margin-bottom: 0.7rem;
        }
        .kpi-value {
            font-size: 2rem;
            line-height: 1;
            font-weight: 700;
            letter-spacing: -0.04em;
            color: var(--text-main);
            margin-bottom: 0.38rem;
        }
        .kpi-sub {
            color: var(--text-muted);
            font-size: 0.84rem;
            line-height: 1.35;
        }

        .model-metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.9rem;
            margin: 0.9rem 0 1rem 0;
        }
        .model-metric-card {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 1rem 1.05rem;
            box-shadow: var(--shadow);
            min-height: 168px;
            position: relative;
            overflow: hidden;
        }
        .model-metric-card::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 3px;
            opacity: 0.9;
        }
        .model-metric-card.metric-accuracy::before { background: linear-gradient(90deg, #22c55e, #86efac); }
        .model-metric-card.metric-mae::before { background: linear-gradient(90deg, #f59e0b, #fcd34d); }
        .model-metric-card.metric-r2::before { background: linear-gradient(90deg, #3b82f6, #67e8f9); }
        .model-metric-head {
            display: flex;
            align-items: center;
            gap: 0.7rem;
            margin-bottom: 0.85rem;
        }
        .model-metric-icon {
            width: 40px;
            height: 40px;
            border-radius: 13px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.15rem;
            flex: 0 0 40px;
            border: 1px solid var(--line);
        }
        .metric-accuracy .model-metric-icon { background: rgba(34, 197, 94, 0.12); }
        .metric-mae .model-metric-icon { background: rgba(245, 158, 11, 0.12); }
        .metric-r2 .model-metric-icon { background: rgba(59, 130, 246, 0.12); }
        .model-metric-title {
            color: var(--text-soft);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
        }
        .model-metric-value {
            color: var(--text-main);
            font-size: 2rem;
            line-height: 1;
            font-weight: 750;
            letter-spacing: -0.04em;
            margin-bottom: 0.55rem;
        }
        .model-metric-caption {
            color: var(--text-muted);
            font-size: 0.84rem;
            line-height: 1.42;
        }
        .model-metric-formula {
            margin-top: 0.55rem;
            color: var(--text-soft);
            font-size: 0.75rem;
            font-weight: 600;
        }
        @media (max-width: 900px) {
            .model-metrics-grid { grid-template-columns: 1fr; }
            .model-metric-card { min-height: auto; }
        }
        .mini-note {
            background: rgba(8, 20, 37, 0.86);
            color: #d7e9fb;
            border: 1px solid rgba(120, 180, 255, 0.14);
            padding: 0.95rem 1rem;
            border-radius: 18px;
            margin-bottom: 0.85rem;
            box-shadow: 0 10px 26px rgba(0, 0, 0, 0.18);
        }
        .section-card {
            background: linear-gradient(180deg, rgba(7, 20, 37, 0.92) 0%, rgba(7, 18, 33, 0.86) 100%);
            border: 1px solid rgba(120, 180, 255, 0.12);
            border-radius: 22px;
            padding: 18px 18px 14px 18px;
            box-shadow: 0 14px 32px rgba(0, 0, 0, 0.22);
            margin-bottom: 0.8rem;
            backdrop-filter: blur(8px);
        }
        .section-card h3 {
            margin: 0 0 0.35rem 0;
            font-size: 1.05rem;
            color: #eef6ff;
            letter-spacing: -0.02em;
        }
        .section-card p {
            margin: 0;
            color: #9fc1e3;
            font-size: 0.94rem;
            line-height: 1.55;
        }
        .section-card .card-footnote {
            margin-top: 10px;
            color: #6f93b6;
            font-size: 0.84rem;
        }
        .status-ok, .status-warn, .status-neutral {
            display: inline-block;
            padding: 0.24rem 0.58rem;
            border-radius: 999px;
            font-weight: 700;
            font-size: 0.76rem;
            border: 1px solid transparent;
        }
        .status-ok {
            background: rgba(34, 197, 94, 0.12);
            color: #b8f7d2;
            border-color: rgba(34, 197, 94, 0.18);
        }
        .status-warn {
            background: rgba(245, 158, 11, 0.12);
            color: #fde68a;
            border-color: rgba(245, 158, 11, 0.18);
        }
        .status-neutral {
            background: rgba(148, 163, 184, 0.10);
            color: #dbeafe;
            border-color: rgba(148, 163, 184, 0.16);
        }
        div[data-testid="metric-container"] {
            background: linear-gradient(180deg, rgba(5, 18, 35, 0.96) 0%, rgba(7, 20, 37, 0.90) 100%);
            border: 1px solid rgba(120, 180, 255, 0.14);
            padding: 18px;
            border-radius: 18px;
            box-shadow: 0 14px 30px rgba(0, 0, 0, 0.20);
        }
        div[data-testid="metric-container"] * {
            color: #eef6ff !important;
        }
        div[data-baseweb="tab-list"] {
            gap: 0.55rem;
            margin-bottom: 0.8rem;
            flex-wrap: wrap;
        }
        div[data-baseweb="tab"] {
            min-height: 42px;
            border-radius: 999px;
            padding: 0 16px;
            background: rgba(7, 20, 37, 0.92);
            color: #d9ebff;
            border: 1px solid rgba(255,255,255,0.20);
            box-shadow: none;
        }
        div[data-baseweb="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, rgba(9, 31, 55, 1) 0%, rgba(11, 42, 74, 1) 100%);
            border: 1px solid rgba(145, 216, 255, 0.38);
            color: #ffffff;
        }
        [data-testid="stDataFrame"], .stPlotlyChart {
            background: transparent;
        }
        .stExpander {
            border: 1px solid rgba(120, 180, 255, 0.12) !important;
            background: rgba(7, 20, 37, 0.76) !important;
            border-radius: 18px !important;
        }
        .stAlert {
            border-radius: 18px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        @media (max-width: 980px) {
            .top-kpi-grid {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }
        }
        @media (max-width: 640px) {
            .top-kpi-grid {
                grid-template-columns: 1fr;
            }
            .hero-box h1 {
                font-size: 1.7rem;
            }
        }
        </style>
        """
    return """
    <style>
    :root {
        --bg-main: #f4f9ff;
        --bg-secondary: #eaf3ff;
        --panel: rgba(255,255,255,0.96);
        --panel-soft: rgba(255,255,255,0.90);
        --line: rgba(61, 129, 195, 0.14);
        --line-strong: rgba(61, 129, 195, 0.24);
        --text-main: #0d2744;
        --text-soft: #3b6288;
        --text-muted: #6d89a6;
        --accent: #2563eb;
        --accent-2: #06b6d4;
        --shadow: 0 18px 40px rgba(30, 64, 105, 0.08);
    }
    html, body, [class*="css"]  {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }
    .stApp {
        background:
            radial-gradient(circle at top right, rgba(114, 182, 255, 0.18), transparent 22%),
            linear-gradient(180deg, #f7fbff 0%, #edf6ff 52%, #f8fbff 100%);
        color: var(--text-main);
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2.4rem;
        max-width: 1380px;
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0e2844 0%, #153f67 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
        min-width: 340px !important;
        max-width: 340px !important;
    }
    [data-testid="stSidebar"] * {
        color: #f8fbff;
    }
    [data-testid="stSidebar"] [data-baseweb="select"] > div,
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stNumberInput input,
    [data-testid="stSidebar"] .stDateInput input,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] [data-baseweb="base-input"] {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
    }
    .hero-box {
        background:
            radial-gradient(circle at 90% 10%, rgba(255,255,255,0.20), transparent 24%),
            linear-gradient(100deg, #0d2744 0%, #14416e 48%, #50add1 100%);
        color: white;
        border-radius: 28px;
        padding: 28px 28px 22px 28px;
        margin-bottom: 1rem;
        box-shadow: 0 24px 60px rgba(27, 68, 112, 0.14);
        border: 1px solid rgba(255,255,255,0.20);
        position: relative;
        overflow: hidden;
    }
    .hero-box h1 {
        margin: 0;
        font-size: 2.05rem;
        line-height: 1.08;
        letter-spacing: -0.04em;
        color: #ffffff;
    }
    .hero-subtitle {
        margin-top: 0.35rem;
        font-size: 0.95rem;
        color: rgba(240, 248, 255, 0.94);
    }
    .hero-badges {
        display: flex;
        gap: 0.5rem;
        flex-wrap: wrap;
        margin-top: 1rem;
    }
    .hero-badge {
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.72);
        border-radius: 999px;
        padding: 0.38rem 0.82rem;
        font-size: 0.84rem;
        font-weight: 600;
        color: #ffffff;
    }
    .top-kpi-card {
        background: linear-gradient(180deg, rgba(255,255,255,0.98) 0%, rgba(249,252,255,0.94) 100%);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem 1.1rem;
        box-shadow: var(--shadow);
        min-height: 124px;
    }
    .kpi-label {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        font-size: 0.73rem;
        text-transform: uppercase;
        letter-spacing: 0.11em;
        color: var(--text-soft);
        margin-bottom: 0.7rem;
    }
    .kpi-value {
        font-size: 2rem;
        line-height: 1;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: var(--text-main);
        margin-bottom: 0.38rem;
    }
    .kpi-sub {
        color: var(--text-muted);
        font-size: 0.84rem;
        line-height: 1.35;
    }

    .model-metrics-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 0.9rem;
        margin: 0.9rem 0 1rem 0;
    }
    .model-metric-card {
        background: var(--panel);
        border: 1px solid var(--line);
        border-radius: 20px;
        padding: 1rem 1.05rem;
        box-shadow: var(--shadow);
        min-height: 168px;
        position: relative;
        overflow: hidden;
    }
    .model-metric-card::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 3px;
        opacity: 0.9;
    }
    .model-metric-card.metric-accuracy::before { background: linear-gradient(90deg, #22c55e, #86efac); }
    .model-metric-card.metric-mae::before { background: linear-gradient(90deg, #f59e0b, #fcd34d); }
    .model-metric-card.metric-r2::before { background: linear-gradient(90deg, #3b82f6, #67e8f9); }
    .model-metric-head {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin-bottom: 0.85rem;
    }
    .model-metric-icon {
        width: 40px;
        height: 40px;
        border-radius: 13px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.15rem;
        flex: 0 0 40px;
        border: 1px solid var(--line);
    }
    .metric-accuracy .model-metric-icon { background: rgba(34, 197, 94, 0.12); }
    .metric-mae .model-metric-icon { background: rgba(245, 158, 11, 0.12); }
    .metric-r2 .model-metric-icon { background: rgba(59, 130, 246, 0.12); }
    .model-metric-title {
        color: var(--text-soft);
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }
    .model-metric-value {
        color: var(--text-main);
        font-size: 2rem;
        line-height: 1;
        font-weight: 750;
        letter-spacing: -0.04em;
        margin-bottom: 0.55rem;
    }
    .model-metric-caption {
        color: var(--text-muted);
        font-size: 0.84rem;
        line-height: 1.42;
    }
    .model-metric-formula {
        margin-top: 0.55rem;
        color: var(--text-soft);
        font-size: 0.75rem;
        font-weight: 600;
    }
    @media (max-width: 900px) {
        .model-metrics-grid { grid-template-columns: 1fr; }
        .model-metric-card { min-height: auto; }
    }
    .mini-note {
        background: rgba(255,255,255,0.94);
        color: #21496f;
        border: 1px solid rgba(61, 129, 195, 0.14);
        padding: 0.95rem 1rem;
        border-radius: 18px;
        margin-bottom: 0.85rem;
        box-shadow: 0 12px 28px rgba(30, 64, 105, 0.06);
    }
    .section-card {
        background: rgba(255,255,255,0.95);
        border: 1px solid rgba(61, 129, 195, 0.12);
        border-radius: 22px;
        padding: 18px 18px 14px 18px;
        box-shadow: 0 14px 28px rgba(30, 64, 105, 0.05);
        margin-bottom: 0.8rem;
    }
    .section-card h3 {
        margin: 0 0 0.35rem 0;
        font-size: 1.05rem;
        color: #0d2744;
    }
    .section-card p {
        margin: 0;
        color: #456989;
        font-size: 0.94rem;
        line-height: 1.55;
    }
    .section-card .card-footnote {
        margin-top: 10px;
        color: #6d89a6;
        font-size: 0.84rem;
    }
    .stTabs [data-baseweb="tab-list"],
    div[data-baseweb="tab-list"] {
        gap: 0.55rem;
        margin-bottom: 0.8rem;
        flex-wrap: wrap;
        background: transparent !important;
    }
    .stTabs button[role="tab"],
    div[data-baseweb="tab"] {
        min-height: 42px;
        border-radius: 999px !important;
        padding: 0 16px !important;
        background: rgba(255,255,255,0.86) !important;
        color: #18456e !important;
        border: 1px solid rgba(61, 129, 195, 0.20) !important;
        box-shadow: none !important;
    }
    .stTabs button[role="tab"] p {
        color: #18456e !important;
        font-weight: 600 !important;
    }
    .stTabs button[role="tab"][aria-selected="true"],
    div[data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(180deg, #ffffff 0%, #f1f8ff 100%) !important;
        color: #0d2744 !important;
        border: 1px solid rgba(59, 130, 246, 0.40) !important;
        box-shadow: 0 8px 20px rgba(37, 99, 235, 0.08) !important;
    }
    .stTabs button[role="tab"][aria-selected="true"] p {
        color: #0d2744 !important;
    }
    .stTabs [data-testid="stMarkdownContainer"] p {
        color: inherit;
    }
    .stPlotlyChart {
        background: rgba(255,255,255,0.72);
        border: 1px solid rgba(61, 129, 195, 0.12);
        border-radius: 22px;
        padding: 0.35rem;
        box-shadow: 0 10px 24px rgba(30, 64, 105, 0.05);
    }
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.72);
        border-radius: 20px;
        border: 1px solid rgba(61, 129, 195, 0.10);
    }
    .stExpander {
        border: 1px solid rgba(61, 129, 195, 0.12) !important;
        background: rgba(255,255,255,0.78) !important;
        border-radius: 18px !important;
    }
    .stAlert {
        border-radius: 18px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    @media (max-width: 980px) {
        .hero-box h1 {
            font-size: 1.8rem;
        }
    }
    @media (max-width: 640px) {
        .hero-box h1 {
            font-size: 1.7rem;
        }
    }
    </style>
    """


def aplicar_tema_interface(modo_visual: str) -> None:
    st.markdown(obter_css_tema(modo_visual), unsafe_allow_html=True)
    st.markdown(
        """
        <style>
        .chart-interpretation {
            margin: -0.15rem 0 1.15rem 0;
            padding: 1rem 1.1rem 0.95rem 1.1rem;
            border-radius: 18px;
            background: var(--panel-soft);
            border: 1px solid var(--line);
            border-left: 4px solid var(--accent);
            box-shadow: var(--shadow);
        }
        .chart-interpretation-head {
            display: flex;
            align-items: center;
            gap: 0.55rem;
            margin-bottom: 0.55rem;
            color: var(--text-main);
            font-weight: 750;
            font-size: 0.94rem;
        }
        .chart-interpretation-subtitle {
            color: var(--text-soft);
            font-size: 0.83rem;
            line-height: 1.45;
            margin-bottom: 0.55rem;
        }
        .chart-interpretation ul {
            margin: 0.25rem 0 0.45rem 1.1rem;
            padding: 0;
        }
        .chart-interpretation li {
            color: var(--text-soft);
            margin: 0.32rem 0;
            line-height: 1.48;
            font-size: 0.88rem;
        }
        .chart-interpretation li strong {
            color: var(--text-main);
        }
        .chart-interpretation-note {
            margin-top: 0.7rem;
            padding-top: 0.65rem;
            border-top: 1px solid var(--line);
            color: var(--text-muted);
            font-size: 0.76rem;
            line-height: 1.45;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    px.defaults.template = "plotly_dark" if modo_visual == "Noturno" else "plotly_white"
    st.session_state["modo_visual_ecoradar"] = modo_visual

def estilizar_figura(fig: go.Figure) -> go.Figure:
    modo_visual = st.session_state.get("modo_visual_ecoradar", "Noturno")
    if modo_visual == "Noturno":
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e2f3ff"),
            legend=dict(bgcolor="rgba(0,0,0,0)")
        )
    else:
        fig.update_layout(
            template="plotly_white",
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="rgba(255,255,255,0)",
            font=dict(color="#12385c"),
            title_font=dict(color="#0d2744"),
            legend=dict(bgcolor="rgba(255,255,255,0)", font=dict(color="#12385c")),
            xaxis=dict(
                title_font=dict(color="#33597d"),
                tickfont=dict(color="#55789a"),
                gridcolor="rgba(62, 109, 156, 0.12)",
                zerolinecolor="rgba(62, 109, 156, 0.16)",
            ),
            yaxis=dict(
                title_font=dict(color="#33597d"),
                tickfont=dict(color="#55789a"),
                gridcolor="rgba(62, 109, 156, 0.12)",
                zerolinecolor="rgba(62, 109, 156, 0.16)",
            ),
        )
        fig.update_annotations(font=dict(color="#33597d"))
    return fig

def _titulo_figura(fig: go.Figure) -> str:
    try:
        titulo = fig.layout.title.text
        if titulo:
            return str(titulo)
    except Exception:
        pass
    return "Visualização ambiental"


def _numero_br(valor: Any, casas: int = 2) -> str:
    try:
        numero = float(valor)
        if not np.isfinite(numero):
            return "—"
        return f"{numero:.{casas}f}".replace(".", ",")
    except Exception:
        return "—"


def _nome_variavel_interpretacao(nome: Any) -> str:
    texto = str(nome or "").strip()
    if not texto:
        return "variável"
    try:
        return nome_amigavel_variavel(texto)
    except Exception:
        return texto.replace("_", " ").strip().title()


def _forca_correlacao(r: float) -> str:
    ar = abs(float(r))
    if ar >= 0.80:
        return "muito forte"
    if ar >= 0.60:
        return "forte"
    if ar >= 0.40:
        return "moderada"
    if ar >= 0.20:
        return "fraca"
    return "muito fraca"


def _direcao_correlacao(r: float) -> str:
    if r > 0.05:
        return "positiva"
    if r < -0.05:
        return "negativa"
    return "próxima de zero"


def _descricao_variavel_conclusao(nome: Any) -> str:
    """Transforma nomes técnicos em expressões naturais para as conclusões."""
    nome_amigavel = _nome_variavel_interpretacao(nome)
    chave = normalizar_texto(nome_amigavel)
    mapa = {
        "pm2.5": "a concentração de PM2.5",
        "pm25": "a concentração de PM2.5",
        "pm10": "a concentração de PM10",
        "no2": "a concentração de NO₂",
        "no₂": "a concentração de NO₂",
        "o3": "a concentração de O₃",
        "o₃": "a concentração de O₃",
        "so2": "a concentração de SO₂",
        "so₂": "a concentração de SO₂",
        "turbidez": "a turbidez da água",
        "ph": "o pH da água",
        "precipitacao da agua": "a precipitação registrada",
        "chuva open-meteo": "o volume de chuva",
        "nivel": "o nível da água",
        "vazao": "a vazão da água",
        "condutividade": "a condutividade da água",
        "temperatura da agua": "a temperatura da água",
        "temp. max open-meteo": "a temperatura máxima",
        "temp. min open-meteo": "a temperatura mínima",
        "vento max open-meteo": "a velocidade máxima do vento",
        "populacao": "a população",
        "chuva": "o volume de chuva",
        "temperatura": "a temperatura",
        "umidade": "a umidade do ar",
        "vento": "a velocidade do vento",
    }
    return mapa.get(chave, f"o valor de {nome_amigavel}")


def _prioridade_variavel_conclusao(nome: Any) -> int:
    """Prioriza água/clima como ponto de partida quando isso deixa a frase mais intuitiva."""
    chave = normalizar_texto(_nome_variavel_interpretacao(nome))
    prioridades = [
        ("turbidez", 0),
        ("ph", 1),
        ("precipit", 2),
        ("chuva", 2),
        ("nivel", 3),
        ("vazao", 4),
        ("condutividade", 5),
        ("temperatura da agua", 6),
        ("pm2.5", 10),
        ("pm25", 10),
        ("pm10", 11),
        ("no2", 12),
        ("o3", 13),
        ("so2", 14),
    ]
    for termo, prioridade in prioridades:
        if termo in chave:
            return prioridade
    return 20


def _ordenar_variaveis_conclusao(a: Any, b: Any) -> tuple[Any, Any]:
    if _prioridade_variavel_conclusao(b) < _prioridade_variavel_conclusao(a):
        return b, a
    return a, b


def _frase_conclusao_relacao(a: Any, b: Any, r: float) -> str:
    """Gera conclusão objetiva sem usar rótulos como 'forte/negativa' no texto principal."""
    a, b = _ordenar_variaveis_conclusao(a, b)
    desc_a = _descricao_variavel_conclusao(a)
    desc_b = _descricao_variavel_conclusao(b)

    if abs(float(r)) < 0.20:
        return (
            f"Os dados não mostram uma tendência clara entre <strong>{html.escape(desc_a)}</strong> "
            f"e <strong>{html.escape(desc_b)}</strong> neste recorte."
        )

    if r > 0:
        return (
            f"Quanto maior <strong>{html.escape(desc_a)}</strong>, maior tende a ser "
            f"<strong>{html.escape(desc_b)}</strong> neste recorte."
        )

    return (
        f"Quanto maior <strong>{html.escape(desc_a)}</strong>, menor tende a ser "
        f"<strong>{html.escape(desc_b)}</strong> neste recorte."
    )



def _lista_segura(valores: Any) -> list[Any]:
    if valores is None:
        return []
    try:
        return list(valores)
    except Exception:
        return []


def _serie_numerica(valores: Any) -> np.ndarray:
    try:
        return pd.to_numeric(pd.Series(_lista_segura(valores)), errors="coerce").to_numpy(dtype=float)
    except Exception:
        return np.array([], dtype=float)


def _coletar_xy_scatter(fig: go.Figure) -> tuple[np.ndarray, np.ndarray]:
    xs: list[float] = []
    ys: list[float] = []
    for trace in fig.data:
        tipo = str(getattr(trace, "type", ""))
        modo = str(getattr(trace, "mode", "") or "")
        if tipo not in {"scatter", "scattergl"}:
            continue
        if "markers" not in modo or "lines" in modo:
            continue
        x_arr = _serie_numerica(getattr(trace, "x", []))
        y_arr = _serie_numerica(getattr(trace, "y", []))
        n = min(len(x_arr), len(y_arr))
        if n == 0:
            continue
        mask = np.isfinite(x_arr[:n]) & np.isfinite(y_arr[:n])
        xs.extend(x_arr[:n][mask].tolist())
        ys.extend(y_arr[:n][mask].tolist())
    return np.asarray(xs, dtype=float), np.asarray(ys, dtype=float)


def _interpretar_heatmap(fig: go.Figure) -> list[str]:
    heat = next((t for t in fig.data if str(getattr(t, "type", "")) == "heatmap"), None)
    if heat is None:
        return []
    try:
        z = np.asarray(heat.z, dtype=float)
        labels_x = [str(v) for v in (list(heat.x) if heat.x is not None else range(z.shape[1]))]
        labels_y = [str(v) for v in (list(heat.y) if heat.y is not None else range(z.shape[0]))]
    except Exception:
        return []

    pares: list[tuple[float, float, str, str]] = []
    vistos: set[tuple[str, str]] = set()
    for i in range(z.shape[0]):
        for j in range(z.shape[1]):
            if i >= len(labels_y) or j >= len(labels_x):
                continue
            a, b = labels_y[i], labels_x[j]
            if a == b:
                continue
            chave = tuple(sorted((a, b)))
            if chave in vistos:
                continue
            valor = z[i, j]
            if not np.isfinite(valor):
                continue
            vistos.add(chave)
            pares.append((abs(float(valor)), float(valor), a, b))

    pares.sort(reverse=True, key=lambda item: item[0])
    if not pares:
        return []

    bullets = ["<strong>Principais conclusões do mapa de correlação:</strong>"]
    for _, r, a, b in pares[:5]:
        bullets.append(
            _frase_conclusao_relacao(a, b, r)
            + f" <span style='opacity:.75'>(r = {_numero_br(r, 2)})</span>"
        )
    return bullets

def _interpretar_splom(fig: go.Figure) -> list[str]:
    traces = [t for t in fig.data if str(getattr(t, "type", "")) == "splom"]
    if not traces:
        return []

    nomes: list[str] | None = None
    blocos: list[np.ndarray] = []
    for trace in traces:
        dims = _lista_segura(getattr(trace, "dimensions", None))
        if len(dims) < 2:
            continue
        if nomes is None:
            nomes = [str(getattr(d, "label", "") or f"Variável {i+1}") for i, d in enumerate(dims)]
        arrs = [_serie_numerica(getattr(d, "values", [])) for d in dims]
        n = min((len(a) for a in arrs), default=0)
        if n == 0:
            continue
        blocos.append(np.column_stack([a[:n] for a in arrs]))

    if not blocos or not nomes:
        return []
    dados = np.vstack(blocos)
    if dados.shape[0] < 3:
        return []

    corr = pd.DataFrame(dados, columns=nomes).corr(numeric_only=True)
    pares = []
    for i in range(len(corr.columns)):
        for j in range(i + 1, len(corr.columns)):
            r = corr.iloc[i, j]
            if pd.notna(r):
                pares.append((abs(float(r)), float(r), corr.columns[i], corr.columns[j]))
    pares.sort(reverse=True, key=lambda x: x[0])

    bullets = ["<strong>Principais conclusões entre as variáveis:</strong>"]
    for _, r, a, b in pares[:5]:
        bullets.append(
            _frase_conclusao_relacao(a, b, r)
            + f" <span style='opacity:.75'>(r = {_numero_br(r, 2)})</span>"
        )
    return bullets

def _interpretar_dispersao(fig: go.Figure, titulo: str) -> list[str]:
    x, y = _coletar_xy_scatter(fig)
    if len(x) < 3:
        return []
    r = float(np.corrcoef(x, y)[0, 1])
    if not np.isfinite(r):
        return []

    partes = re.split(r"\s*×\s*|\s+x\s+|→|—", titulo, maxsplit=1)
    nome_x = partes[0].strip() if partes else "Variável X"
    nome_y = partes[1].strip() if len(partes) > 1 else "Variável Y"

    titulo_norm = normalizar_texto(titulo)

    # Gráficos observado × previsto precisam de uma leitura própria, não causal.
    if ("observado" in titulo_norm and "previsto" in titulo_norm) or "previsao" in titulo_norm:
        mae = float(np.mean(np.abs(y - x)))
        ss_res = float(np.sum((y - x) ** 2))
        ss_tot = float(np.sum((x - np.mean(x)) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
        bullets = [
            f"Quanto mais próximos os pontos estão da linha diagonal, mais próximas estão as previsões dos valores realmente observados.",
            f"Nos pontos exibidos, a diferença média entre o valor observado e o previsto é de aproximadamente "
            f"<strong>{_numero_br(mae, 2)}</strong>."
        ]
        if np.isfinite(r2):
            if r2 >= 0.75:
                bullets.append("O modelo acompanha bem a variação dos valores observados neste recorte.")
            elif r2 >= 0.40:
                bullets.append("O modelo acompanha parte da variação dos valores observados, mas ainda apresenta diferenças relevantes.")
            else:
                bullets.append("O modelo apresenta dificuldade para acompanhar a variação dos valores observados neste recorte.")
            bullets.append(f"<span style='opacity:.75'>R² dos pontos exibidos: {_numero_br(r2, 2)}.</span>")
        return bullets

    bullets = [
        _frase_conclusao_relacao(nome_x, nome_y, r)
        + f" <span style='opacity:.75'>(r = {_numero_br(r, 2)}; {len(x)} observações)</span>"
    ]

    # Acrescenta uma frase especialmente clara para os pares centrais do EcoRadar.
    tx = normalizar_texto(nome_x)
    ty = normalizar_texto(nome_y)
    if ("pm2.5" in tx or "pm25" in tx) and "turbidez" in ty:
        if abs(r) < 0.20:
            bullets.append("Neste conjunto de dados, a turbidez da água e o PM2.5 não variaram de forma suficientemente consistente para indicar uma tendência clara.")
        elif r > 0:
            bullets.append("Em termos simples: <strong>nos dias com maior turbidez da água, também foram observadas maiores concentrações de PM2.5.</strong>")
        else:
            bullets.append("Em termos simples: <strong>nos dias com maior turbidez da água, foram observadas menores concentrações de PM2.5.</strong>")

    return bullets

def _interpretar_linhas(fig: go.Figure, titulo: str) -> list[str]:
    series = []
    todos_valores = []
    for trace in fig.data:
        tipo = str(getattr(trace, "type", ""))
        modo = str(getattr(trace, "mode", "") or "")
        if tipo not in {"scatter", "scattergl"} or "lines" not in modo:
            continue
        y = _serie_numerica(getattr(trace, "y", []))
        if len(y) < 2:
            continue
        mask = np.isfinite(y)
        if mask.sum() < 2:
            continue
        yv = y[mask]
        nome = str(getattr(trace, "name", "") or "Série")
        series.append((nome, float(yv[0]), float(yv[-1]), float(np.nanmin(yv)), float(np.nanmax(yv))))
        todos_valores.extend(yv.tolist())

    if not series:
        return []

    bullets = []
    for nome, inicio, fim, minimo, maximo in sorted(series, key=lambda s: abs(s[2] - s[1]), reverse=True)[:4]:
        dif = fim - inicio
        tendencia = "permaneceu praticamente estável" if abs(dif) < 1e-12 else ("terminou acima do valor inicial" if dif > 0 else "terminou abaixo do valor inicial")
        bullets.append(
            f"<strong>{html.escape(nome)}</strong>: {tendencia} "
            f"({_numero_br(inicio, 2)} → {_numero_br(fim, 2)}), com faixa de {_numero_br(minimo, 2)} a {_numero_br(maximo, 2)}."
        )

    if "pm2.5" in normalizar_texto(titulo) and todos_valores:
        arr = np.asarray(todos_valores, dtype=float)
        acima = int(np.sum(arr > 15))
        bullets.append(
            f"Em relação à linha de 15 μg/m³ exibida no painel, <strong>{acima} de {len(arr)}</strong> pontos ficaram acima desse valor."
        )
    return bullets


def _interpretar_barras(fig: go.Figure, titulo: str) -> list[str]:
    entradas: list[tuple[float, str, str]] = []
    for trace in fig.data:
        if str(getattr(trace, "type", "")) != "bar":
            continue
        orient = str(getattr(trace, "orientation", "") or "v")
        if orient == "h":
            valores = _serie_numerica(getattr(trace, "x", []))
            categorias = _lista_segura(getattr(trace, "y", None))
        else:
            valores = _serie_numerica(getattr(trace, "y", []))
            categorias = _lista_segura(getattr(trace, "x", None))
        nome_trace = str(getattr(trace, "name", "") or "")
        for i, valor in enumerate(valores):
            if np.isfinite(valor):
                categoria = str(categorias[i]) if i < len(categorias) else f"Item {i+1}"
                entradas.append((float(valor), categoria, nome_trace))

    if not entradas:
        return []
    entradas.sort(reverse=True, key=lambda x: x[0])
    titulo_norm = normalizar_texto(titulo)

    if "importancia" in titulo_norm:
        total = sum(max(0.0, e[0]) for e in entradas)
        bullets = ["<strong>Variáveis com maior influência no modelo:</strong>"]
        for valor, categoria, _ in entradas[:3]:
            pct = (valor / total * 100) if total > 0 else np.nan
            bullets.append(
                f"<strong>{html.escape(categoria)}</strong>: {_numero_br(valor, 3)}"
                + (f" (≈ {_numero_br(pct, 1)}% da importância total)" if np.isfinite(pct) else "")
                + "."
            )
        return bullets

    if "balneabilidade" in titulo_norm:
        bullets = ["<strong>Maiores grupos de classificação observados:</strong>"]
        for valor, categoria, nome_trace in entradas[:4]:
            detalhe = f" — {html.escape(nome_trace)}" if nome_trace else ""
            bullets.append(f"<strong>{html.escape(categoria)}</strong>{detalhe}: {int(round(valor))} registro(s).")
        return bullets

    bullets = ["<strong>Maiores valores do gráfico:</strong>"]
    for valor, categoria, nome_trace in entradas[:3]:
        detalhe = f" ({html.escape(nome_trace)})" if nome_trace and nome_trace != categoria else ""
        bullets.append(f"<strong>{html.escape(categoria)}</strong>{detalhe}: {_numero_br(valor, 2)}.")
    menor = min(entradas, key=lambda e: e[0])
    bullets.append(f"O menor valor exibido é de <strong>{html.escape(menor[1])}</strong>: {_numero_br(menor[0], 2)}.")
    return bullets


def _interpretar_mapa(fig: go.Figure) -> list[str]:
    traces = [t for t in fig.data if str(getattr(t, "type", "")) in {"scattermap", "scattermapbox"}]
    if not traces:
        return []

    if len(traces) > 1:
        contagens = []
        for trace in traces:
            n = len(_lista_segura(getattr(trace, "lat", None)))
            nome = str(getattr(trace, "name", "") or "Categoria")
            contagens.append((n, nome))
        contagens.sort(reverse=True)
        bullets = ["<strong>Distribuição espacial por categoria:</strong>"]
        for n, nome in contagens[:5]:
            bullets.append(f"<strong>{html.escape(nome)}</strong>: {n} ponto(s) exibido(s).")
        return bullets

    trace = traces[0]
    marker = getattr(trace, "marker", None)
    if marker is None:
        return ["O mapa mostra a distribuição espacial dos pontos monitorados no recorte selecionado."]

    valores = _serie_numerica(getattr(marker, "color", []))
    if len(valores) == 0 or not np.isfinite(valores).any():
        valores = _serie_numerica(getattr(marker, "size", []))
    nomes = _lista_segura(getattr(trace, "hovertext", None))
    if len(valores) == 0 or not np.isfinite(valores).any():
        return ["O mapa permite comparar a localização dos pontos monitorados e identificar padrões espaciais no recorte selecionado."]

    itens = []
    for i, valor in enumerate(valores):
        if np.isfinite(valor):
            nome = str(nomes[i]) if i < len(nomes) else f"Ponto {i+1}"
            itens.append((float(valor), nome))
    itens.sort(reverse=True)
    bullets = ["<strong>Pontos de maior intensidade no mapa:</strong>"]
    for valor, nome in itens[:3]:
        bullets.append(f"<strong>{html.escape(nome)}</strong>: {_numero_br(valor, 2)}.")
    return bullets


def gerar_interpretacao_figura(fig: go.Figure) -> list[str]:
    titulo = _titulo_figura(fig)
    tipos = {str(getattr(trace, "type", "")) for trace in fig.data}
    titulo_norm = normalizar_texto(titulo)

    if "heatmap" in tipos or "heatmap" in titulo_norm or "correlacao" in titulo_norm:
        bullets = _interpretar_heatmap(fig)
        if bullets:
            return bullets

    if "splom" in tipos or "matriz de dispersao" in titulo_norm:
        bullets = _interpretar_splom(fig)
        if bullets:
            return bullets

    if tipos & {"scattermap", "scattermapbox"}:
        return _interpretar_mapa(fig)

    if "bar" in tipos:
        bullets = _interpretar_barras(fig, titulo)
        if bullets:
            return bullets

    if tipos & {"scatter", "scattergl"}:
        tem_linhas = any("lines" in str(getattr(t, "mode", "") or "") for t in fig.data)
        tem_marcadores_puros = any(
            "markers" in str(getattr(t, "mode", "") or "") and "lines" not in str(getattr(t, "mode", "") or "")
            for t in fig.data
        )
        if tem_marcadores_puros:
            bullets = _interpretar_dispersao(fig, titulo)
            if bullets:
                return bullets
        if tem_linhas:
            bullets = _interpretar_linhas(fig, titulo)
            if bullets:
                return bullets

    return ["A visualização resume os dados disponíveis no recorte atual e deve ser interpretada em conjunto com período, localidade e cobertura das bases."]


def exibir_interpretacao_grafico(fig: go.Figure) -> None:
    if not st.session_state.get("mostrar_interpretacoes_graficos", True):
        return
    titulo = _titulo_figura(fig)
    bullets = gerar_interpretacao_figura(fig)
    itens = "".join(f"<li>{item}</li>" for item in bullets)
    st.markdown(
        f"""
        <div class="chart-interpretation">
            <div class="chart-interpretation-head">🧭 Interpretação simples dos resultados</div>
            <div class="chart-interpretation-subtitle">
                Leitura automática do que aparece em <strong>{html.escape(titulo)}</strong>.
            </div>
            <ul>{itens}</ul>
            <div class="chart-interpretation-note">
                Leitura exploratória: associações, correlações e tendências visuais não demonstram causalidade.
                Os resultados dependem do período, da cobertura e da qualidade das bases utilizadas.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def renderizar_grafico(fig: go.Figure, **kwargs: Any) -> None:
    fig_estilizada = estilizar_figura(fig)
    st.plotly_chart(fig_estilizada, **kwargs)
    exibir_interpretacao_grafico(fig_estilizada)

REQUEST_TIMEOUT = 20
DEFAULT_PM25_DAYS = 15
DEFAULT_CLIMATE_DAYS = 15

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CIDADES = {
    "Aparecida, SP": {"lat": -22.8469, "lon": -45.2297, "ibge": 3502507, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Bananal, SP": {"lat": -22.6819, "lon": -44.3234, "ibge": 3504909, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Caçapava, SP": {"lat": -23.1002, "lon": -45.7064, "ibge": 3508504, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Campos do Jordão, SP": {"lat": -22.7394, "lon": -45.5914, "ibge": 3509700, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Canas, SP": {"lat": -22.7007, "lon": -45.0530, "ibge": 3509957, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Cachoeira Paulista, SP": {"lat": -22.6666, "lon": -45.0094, "ibge": 3508603, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Cruzeiro, SP": {"lat": -22.5765, "lon": -44.9656, "ibge": 3513405, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Guaratinguetá, SP": {"lat": -22.8166, "lon": -45.1927, "ibge": 3518404, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Jacareí, SP": {"lat": -23.3053, "lon": -45.9658, "ibge": 3524402, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Lavrinhas, SP": {"lat": -22.5704, "lon": -44.9026, "ibge": 3526605, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Lorena, SP": {"lat": -22.7333, "lon": -45.1236, "ibge": 3527207, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Pindamonhangaba, SP": {"lat": -22.9246, "lon": -45.4613, "ibge": 3538006, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Piquete, SP": {"lat": -22.6136, "lon": -45.1830, "ibge": 3538501, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Potim, SP": {"lat": -22.8343, "lon": -45.2554, "ibge": 3540754, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Queluz, SP": {"lat": -22.5312, "lon": -44.7782, "ibge": 3539905, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Roseira, SP": {"lat": -22.8940, "lon": -45.3058, "ibge": 3544301, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Santa Branca, SP": {"lat": -23.3963, "lon": -45.8832, "ibge": 3546009, "uf": "SP", "regiao": "Vale do Paraíba"},
    "São Bento do Sapucaí, SP": {"lat": -22.6837, "lon": -45.7312, "ibge": 3548609, "uf": "SP", "regiao": "Vale do Paraíba"},
    "São José dos Campos, SP": {"lat": -23.1791, "lon": -45.8872, "ibge": 3549904, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Taubaté, SP": {"lat": -23.0273, "lon": -45.5553, "ibge": 3554102, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Tremembé, SP": {"lat": -22.9584, "lon": -45.5494, "ibge": 3554805, "uf": "SP", "regiao": "Vale do Paraíba"},
    "Caraguatatuba, SP": {"lat": -23.6197, "lon": -45.4128, "ibge": 3510500, "uf": "SP", "regiao": "Litoral Norte"},
    "Ubatuba, SP": {"lat": -23.4332, "lon": -45.0834, "ibge": 3555406, "uf": "SP", "regiao": "Litoral Norte"},
    "São Sebastião, SP": {"lat": -23.7602, "lon": -45.4042, "ibge": 3550704, "uf": "SP", "regiao": "Litoral Norte"},
    "Ilhabela, SP": {"lat": -23.7781, "lon": -45.3581, "ibge": 3520400, "uf": "SP", "regiao": "Litoral Norte"},
}

REGIOES = {
    "Área completa do estudo": list(CIDADES.keys()),
    "Vale do Paraíba": [cidade for cidade, info in CIDADES.items() if info["regiao"] == "Vale do Paraíba"],
    "Litoral Norte": [cidade for cidade, info in CIDADES.items() if info["regiao"] == "Litoral Norte"],
}

CETESB_BALNEABILIDADE_URL = (
    "https://arcgis.cetesb.sp.gov.br/server/rest/services/Hosted/Praias/FeatureServer/0/query"
    "?where=1%3D1&outFields=*&returnGeometry=true&f=geojson"
)

MANUAL_SOURCE_CONFIG = {
    "CETESB_BALNEABILIDADE": ["cetesb.csv", "cetesb.xlsx", "cetesb.xls", "balneabilidade.csv", "balneabilidade.xlsx", "balneabilidade.xls"],
    "SIMQUA": ["simqua.csv", "simqua.xlsx", "simqua.xls", "agua_cetesb.csv", "agua_cetesb.xlsx"],
}

GUIDES_FONTES = {
    "CETESB_BALNEABILIDADE": "A CETESB tenta carregar balneabilidade automaticamente por API REST. Se falhar, use um CSV/XLSX local.",
    "SIMQUA": "Use um CSV/XLSX exportado do SIMQUA com colunas de data, pH, turbidez, precipitação, nível ou vazão.",
    "OPENMETEO_AR": "O Open-Meteo fornece estimativas de PM2.5 e PM10 baseadas em modelos CAMS; não são medições de um sensor local.",
}


POPULACAO_FALLBACK_IBGE = {
    3502507: 32569,  # Aparecida (SP) — Censo 2022
    3504909: 9969,   # Bananal (SP) — Censo 2022
    3555406: 92981,  # Ubatuba (SP) — Censo 2022
}



def exibir_logo_sidebar() -> None:
    candidatos = [
        BASE_DIR / "ecoradar_logo.png",
        BASE_DIR / "logo_ecoradar.png",
        BASE_DIR / "a_digital_graphic_design_logo_for_ecoradar_a_wate.png",
    ]
    caminho_logo = next((c for c in candidatos if c.exists()), None)
    if caminho_logo is None:
        return

    st.markdown("<div style='padding-top:0.2rem'></div>", unsafe_allow_html=True)
    st.image(str(caminho_logo), use_container_width=True)
    st.markdown("<div style='height:0.45rem'></div>", unsafe_allow_html=True)

def normalizar_texto(texto: Any) -> str:
    if texto is None:
        return ""
    texto = str(texto).strip().lower()
    return "".join(c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c))

def detectar_coluna(df: pd.DataFrame, candidatos: list[str]) -> Optional[str]:
    if df.empty:
        return None
    mapa = {normalizar_texto(col): col for col in df.columns}
    for candidato in candidatos:
        if normalizar_texto(candidato) in mapa:
            return mapa[normalizar_texto(candidato)]
    for coluna in df.columns:
        nome = normalizar_texto(coluna)
        for candidato in candidatos:
            cand = normalizar_texto(candidato)
            if cand == nome or cand in nome:
                return coluna
    return None

def formatar_inteiro_br(valor: int) -> str:
    return f"{valor:,}".replace(",", ".")

def formatar_decimal_br(valor: float, casas: int = 1, sufixo: str = "") -> str:
    if pd.isna(valor):
        return "—"
    return f"{valor:.{casas}f}".replace(".", ",") + sufixo

def classificar_pm25(valor: float) -> tuple[str, str, str]:
    if pd.isna(valor):
        return "Sem leitura", "status-neutral", "Não há leitura suficiente para classificar o material particulado fino."
    if valor <= 15:
        return "Melhor cenário", "status-ok", "A média está próxima da referência de 15 μg/m³ usada como linha de interpretação no painel."
    if valor <= 25:
        return "Atenção", "status-warn", "O material particulado está acima da referência do painel e merece discussão ambiental."
    return "Pressão elevada", "status-warn", "O valor indica pressão ambiental mais alta e reforça a leitura crítica da qualidade do ar."


def formatar_card_valor(valor: Any, casas: int = 1, unidade: str = "", vazio: str = "—") -> str:
    if valor is None or pd.isna(valor):
        return vazio
    numero = float(valor)
    if float(numero).is_integer() and casas == 0:
        base = f"{int(numero)}"
    else:
        base = f"{numero:.{casas}f}".replace(".", ",")
        if casas == 0:
            base = base.split(",")[0]
    return f"{base}{unidade}"



def calcular_acuracia_percentual(y_real: Any, y_previsto: Any) -> float:
    """Calcula uma acurácia percentual intuitiva para regressão usando 100 - MAPE."""
    reais = np.asarray(y_real, dtype=float)
    previstos = np.asarray(y_previsto, dtype=float)
    mascara = np.isfinite(reais) & np.isfinite(previstos) & (np.abs(reais) > 1e-9)
    if not mascara.any():
        return np.nan
    mape = np.mean(np.abs((reais[mascara] - previstos[mascara]) / reais[mascara]))
    return float(np.clip((1.0 - mape) * 100.0, 0.0, 100.0))


def exibir_cards_metricas_modelo(metricas: dict[str, float], unidade_mae: str = "") -> None:
    """Exibe Acurácia, MAE e R² como cartões visuais de avaliação do modelo."""
    if not metricas:
        st.info("As métricas de validação ainda não estão disponíveis para este recorte de dados.")
        return

    acuracia = metricas.get("ACURACIA", np.nan)
    mae = metricas.get("MAE", np.nan)
    r2 = metricas.get("R2", np.nan)

    valor_acuracia = formatar_decimal_br(acuracia, 1, "%") if pd.notna(acuracia) else "—"
    valor_mae = formatar_decimal_br(mae, 2, unidade_mae) if pd.notna(mae) else "—"
    valor_r2 = formatar_decimal_br(r2, 3) if pd.notna(r2) else "—"

    st.markdown(
        f"""
        <div class="model-metrics-grid">
            <div class="model-metric-card metric-accuracy">
                <div class="model-metric-head">
                    <div class="model-metric-icon">🎯</div>
                    <div class="model-metric-title">Acurácia estimada</div>
                </div>
                <div class="model-metric-value">{valor_acuracia}</div>
                <div class="model-metric-caption">Percentual de proximidade entre os valores previstos e observados.</div>
                <div class="model-metric-formula">Cálculo visual: 100 − MAPE</div>
            </div>
            <div class="model-metric-card metric-mae">
                <div class="model-metric-head">
                    <div class="model-metric-icon">📉</div>
                    <div class="model-metric-title">MAE · Erro médio</div>
                </div>
                <div class="model-metric-value">{valor_mae}</div>
                <div class="model-metric-caption">Indica o erro médio absoluto das previsões. Quanto menor, melhor o desempenho.</div>
                <div class="model-metric-formula">Erro médio das previsões</div>
            </div>
            <div class="model-metric-card metric-r2">
                <div class="model-metric-head">
                    <div class="model-metric-icon">📊</div>
                    <div class="model-metric-title">R² · Explicação</div>
                </div>
                <div class="model-metric-value">{valor_r2}</div>
                <div class="model-metric-caption">Indica quanto da variação observada nos dados é explicada pelo modelo.</div>
                <div class="model-metric-formula">Mais próximo de 1 = melhor ajuste</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def resumir_nome_area(nome_area: str) -> str:
    if normalizar_texto(nome_area) == normalizar_texto("Área completa do estudo"):
        return "Área completa"
    return nome_area



def montar_metricas_topo_resumo(df_atual: pd.DataFrame, nome_area: str) -> list[dict[str, str]]:
    base = df_atual.copy()
    for coluna in ["PM2.5", "PM10", "Temperatura"]:
        if coluna in base.columns:
            base[coluna] = pd.to_numeric(base[coluna], errors="coerce")

    municipios = int(base["Cidade"].nunique()) if not base.empty and "Cidade" in base.columns else 0
    pm25_medio = float(base["PM2.5"].dropna().mean()) if "PM2.5" in base.columns and base["PM2.5"].notna().any() else np.nan
    pm10_medio = float(base["PM10"].dropna().mean()) if "PM10" in base.columns and base["PM10"].notna().any() else np.nan
    temperatura_media = float(base["Temperatura"].dropna().mean()) if "Temperatura" in base.columns and base["Temperatura"].notna().any() else np.nan

    return [
        {
            "icone": "⌘",
            "titulo": "Recorte",
            "valor": resumir_nome_area(nome_area),
            "sub": "Área selecionada no painel",
        },
        {
            "icone": "◫",
            "titulo": "Municípios",
            "valor": formatar_inteiro_br(municipios),
            "sub": "Cidades monitoradas",
        },
        {
            "icone": "◌",
            "titulo": "PM2.5 agora",
            "valor": formatar_card_valor(pm25_medio, 1, " μg/m³"),
            "sub": "Estimativa CAMS/Open-Meteo no recorte",
        },
        {
            "icone": "◌",
            "titulo": "PM10 agora",
            "valor": formatar_card_valor(pm10_medio, 1, " μg/m³"),
            "sub": "Estimativa CAMS/Open-Meteo no recorte",
        },
        {
            "icone": "⌁",
            "titulo": "Temperatura média",
            "valor": formatar_card_valor(temperatura_media, 1, " °C"),
            "sub": "Média das estações",
        },
    ]


def montar_metricas_topo_detalhe(df_atual: pd.DataFrame, df_simqua: pd.DataFrame) -> list[dict[str, str]]:
    ph = pd.to_numeric(df_simqua.get("ph"), errors="coerce").mean() if not df_simqua.empty and "ph" in df_simqua.columns else np.nan
    turbidez = pd.to_numeric(df_simqua.get("turbidez"), errors="coerce").mean() if not df_simqua.empty and "turbidez" in df_simqua.columns else np.nan
    oxigenio = pd.to_numeric(df_simqua.get("oxigenio_dissolvido"), errors="coerce").mean() if not df_simqua.empty and "oxigenio_dissolvido" in df_simqua.columns else np.nan
    condutividade = pd.to_numeric(df_simqua.get("condutividade"), errors="coerce").mean() if not df_simqua.empty and "condutividade" in df_simqua.columns else np.nan

    return [
        {
            "icone": "◌",
            "titulo": "pH da água",
            "valor": formatar_card_valor(ph, 1, ""),
            "sub": "Média da série carregada do SIMQUA",
        },
        {
            "icone": "◔",
            "titulo": "Turbidez",
            "valor": formatar_card_valor(turbidez, 0, " NTU"),
            "sub": "Média da série carregada do SIMQUA",
        },
        {
            "icone": "◔",
            "titulo": "Oxigênio dissolvido",
            "valor": formatar_card_valor(oxigenio, 2, " mg/L"),
            "sub": "Média da série carregada do SIMQUA",
        },
        {
            "icone": "≋",
            "titulo": "Condutividade",
            "valor": formatar_card_valor(condutividade, 1, " μS/cm"),
            "sub": "Média da série carregada do SIMQUA",
        },
    ]


def exibir_topo_dashboard(df_atual: pd.DataFrame, df_simqua: pd.DataFrame, nome_area: str, nomes_area: list[str]) -> None:
    municipios_texto = ", ".join(nomes_area)
    st.markdown(
        f"""
        <div class="hero-box">
            <div class="hero-copy">
                <h1>EcoRadar</h1>
                <div class="hero-subtitle">Partículas atmosféricas e qualidade da água</div>
                <div class="hero-badges">
                    <span class="hero-badge">PM2.5 e PM10</span>
                    <span class="hero-badge">Turbidez, pH e oxigênio</span>
                    <span class="hero-badge">Chuva como contexto</span>
                    <span class="hero-badge">Associação exploratória</span>
                </div>
                <div style="margin-top:1rem;padding:0.95rem 1rem;border-radius:18px;background:rgba(255,255,255,0.08);border:1px solid rgba(255,255,255,0.18);color:#eef6ff;line-height:1.55;">
                    <strong>Municípios considerados:</strong> {municipios_texto}
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cards_resumo = montar_metricas_topo_resumo(df_atual, nome_area)
    colunas_resumo = st.columns(len(cards_resumo))
    for coluna, card in zip(colunas_resumo, cards_resumo):
        with coluna:
            st.markdown(
                f"""
                <div class='top-kpi-card'>
                    <div class='kpi-label'><span>{card['icone']}</span><span>{card['titulo']}</span></div>
                    <div class='kpi-value'>{card['valor']}</div>
                    <div class='kpi-sub'>{card['sub']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    cards_detalhe = montar_metricas_topo_detalhe(df_atual, df_simqua)
    colunas_detalhe = st.columns(len(cards_detalhe))
    for coluna, card in zip(colunas_detalhe, cards_detalhe):
        with coluna:
            st.markdown(
                f"""
                <div class='top-kpi-card'>
                    <div class='kpi-label'><span>{card['icone']}</span><span>{card['titulo']}</span></div>
                    <div class='kpi-value'>{card['valor']}</div>
                    <div class='kpi-sub'>{card['sub']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

def nomes_municipios(cidades: list[str]) -> list[str]:

    return [cidade.split(",")[0].strip() for cidade in cidades]

def obter_cidades_area(area: str) -> list[str]:
    return REGIOES.get(area, [area])

def area_tem_litoral(cidades: list[str]) -> bool:
    return any(CIDADES[cidade]["regiao"] == "Litoral Norte" for cidade in cidades)

def converter_texto_para_numero(valor: Any) -> float | int | None:
    if pd.isna(valor):
        return np.nan
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return valor
    texto = str(valor).strip()
    if not texto or texto.lower() in {"nan", "none", "null", "n/a", "na", "-", "--"}:
        return np.nan
    texto = texto.replace(" ", " ").replace(" ", "")
    texto = re.sub(r"[^0-9,\.\-]", "", texto)
    if not texto or texto in {"-", ".", ","}:
        return np.nan
    if "," in texto and "." in texto:
        if texto.rfind(",") > texto.rfind("."):
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", "")
    elif texto.count(",") > 1:
        partes = texto.split(",")
        texto = "".join(partes[:-1]) + "." + partes[-1]
    elif texto.count(".") > 1:
        partes = texto.split(".")
        texto = "".join(partes[:-1]) + "." + partes[-1]
    elif "," in texto:
        texto = texto.replace(",", ".")
    return pd.to_numeric(texto, errors="coerce")

def sanitizar_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df.columns = [str(c).strip().replace('"', "") for c in df.columns]
    possiveis_numericas = [
        "latitude", "lat", "longitude", "lon", "x", "y", "coord", "utm",
        "temperatura", "umidade", "vento", "velocidade", "precipit", "chuva",
        "ph", "turbidez", "vazao", "vazão", "nivel", "nível", "cota", "condutividade",
        "pm25", "pm2.5", "pm10", "no2", "o3", "so2", "co", "aqi", "valor"
    ]
    for col in df.columns:
        col_norm = normalizar_texto(col)
        if any(p in col_norm for p in possiveis_numericas):
            df[col] = df[col].apply(converter_texto_para_numero)
    return df
def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": "EcoRadar-OpenMeteo/1.0"})
    return session

def fetch_json(url: str, timeout: int = REQUEST_TIMEOUT) -> Optional[dict[str, Any]]:
    try:
        response = get_session().get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None

@st.cache_data(ttl=86400)
def carregar_cetesb_balneabilidade_auto() -> pd.DataFrame:
    data = fetch_json(CETESB_BALNEABILIDADE_URL)
    if not data or "features" not in data:
        return pd.DataFrame()
    rows: list[dict[str, Any]] = []
    for feature in data.get("features", []):
        props = feature.get("properties", {}) or {}
        geom = feature.get("geometry", {}) or {}
        coords = geom.get("coordinates") or []
        row = dict(props)
        if isinstance(coords, (list, tuple)) and len(coords) >= 2:
            row["Longitude"] = coords[0]
            row["Latitude"] = coords[1]
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    if "classificacao_texto" in df.columns and "Classificação" not in df.columns:
        df["Classificação"] = df["classificacao_texto"]
    if "data_atual" in df.columns:
        try:
            df["data_atual"] = pd.to_datetime(df["data_atual"], errors="coerce", unit="ms")
        except Exception:
            df["data_atual"] = pd.to_datetime(df["data_atual"], errors="coerce")
    return sanitizar_dataframe(df)

def ler_bytes_tabulares(conteudo: bytes, nome_arquivo: str) -> pd.DataFrame:
    nome = nome_arquivo.lower()
    tentativas = [
        {"sep": ",", "encoding": "utf-8"},
        {"sep": ";", "encoding": "utf-8"},
        {"sep": ",", "encoding": "utf-8-sig"},
        {"sep": ";", "encoding": "utf-8-sig"},
        {"sep": ",", "encoding": "latin-1"},
        {"sep": ";", "encoding": "latin-1"},
    ]
    if nome.endswith((".xlsx", ".xls")):
        try:
            return sanitizar_dataframe(pd.read_excel(io.BytesIO(conteudo)))
        except Exception:
            pass
    for params in tentativas:
        try:
            df = pd.read_csv(io.BytesIO(conteudo), low_memory=False, **params)
            if not df.empty and len(df.columns) > 1:
                return sanitizar_dataframe(df)
        except Exception:
            continue
    return pd.DataFrame()

def carregar_arquivo_tabular(uploaded_file) -> pd.DataFrame:
    if uploaded_file is None:
        return pd.DataFrame()

    if isinstance(uploaded_file, (list, tuple)):
        bases = []
        for arquivo in uploaded_file:
            if arquivo is None:
                continue
            df_item = ler_bytes_tabulares(arquivo.getvalue(), arquivo.name)
            if not df_item.empty:
                df_item = df_item.copy()
                df_item["arquivo_origem"] = arquivo.name
                bases.append(df_item)
        return pd.concat(bases, ignore_index=True) if bases else pd.DataFrame()

    return ler_bytes_tabulares(uploaded_file.getvalue(), uploaded_file.name)

def listar_arquivos_data() -> list[str]:
    return sorted([p.name for p in DATA_DIR.iterdir() if p.is_file()])

def carregar_fonte_local(nome_fonte: str) -> tuple[pd.DataFrame, str]:
    for nome_arquivo in MANUAL_SOURCE_CONFIG.get(nome_fonte, []):
        caminho = DATA_DIR / nome_arquivo
        if caminho.exists():
            try:
                df = ler_bytes_tabulares(caminho.read_bytes(), caminho.name)
                if not df.empty:
                    return df, f"arquivo local: {caminho.name}"
            except Exception:
                continue
    return pd.DataFrame(), "sem arquivo local"

def carregar_fonte_hibrida(nome_fonte: str, uploaded_file=None) -> tuple[pd.DataFrame, str]:
    if nome_fonte == "CETESB_BALNEABILIDADE":
        auto_df = carregar_cetesb_balneabilidade_auto()
        if not auto_df.empty:
            return auto_df, "API/REST oficial"
    if uploaded_file is not None:
        up_df = carregar_arquivo_tabular(uploaded_file)
        if not up_df.empty:
            if isinstance(uploaded_file, (list, tuple)):
                nomes = [arquivo.name for arquivo in uploaded_file if arquivo is not None]
                if len(nomes) == 1:
                    return up_df, f"upload: {nomes[0]}"
                return up_df, f"upload múltiplo: {len(nomes)} arquivos"
            return up_df, f"upload: {uploaded_file.name}"
    return carregar_fonte_local(nome_fonte)

def aplicar_filtro_uf(df: pd.DataFrame, uf: str) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    col_uf = detectar_coluna(df, ["uf", "sigla_uf", "estado", "unidade_federativa"])
    if not col_uf:
        return df.copy()
    return df[df[col_uf].astype(str).str.upper().str.strip() == uf.upper()].copy()

def filtrar_dataset_por_municipios(df: pd.DataFrame, cidades: list[str], filtrar_uf_sp: bool = True) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    base = aplicar_filtro_uf(df.copy(), "SP") if filtrar_uf_sp else df.copy()
    municipios = [normalizar_texto(n) for n in nomes_municipios(cidades)]
    col_municipio = detectar_coluna(base, ["municipio", "município", "cidade", "localidade", "estacao", "estação", "nome_municipio", "nome"])
    if col_municipio:
        serie = base[col_municipio].astype(str).map(normalizar_texto)
        mascara = serie.apply(lambda valor: any(m in valor for m in municipios))
        filtrado = base[mascara].copy()
        return filtrado if not filtrado.empty else base
    return base

def aplicar_filtro_textual(df: pd.DataFrame, termo: str) -> pd.DataFrame:
    termo = normalizar_texto(termo)
    if not termo or df.empty:
        return df.copy()
    text_cols = df.select_dtypes(include=["object", "string"]).columns.tolist()
    if not text_cols:
        return df.copy()
    mascara = pd.Series(False, index=df.index)
    for coluna in text_cols:
        mascara = mascara | df[coluna].astype(str).map(normalizar_texto).str.contains(termo, na=False)
    filtrado = df[mascara].copy()
    return filtrado if not filtrado.empty else df.copy()

def preparar_fonte(df: pd.DataFrame, cidades: list[str], busca_textual: str = "", aplicar_filtro_regional: bool = True) -> tuple[pd.DataFrame, dict[str, Any]]:
    diag = {
        "linhas_originais": len(df),
        "linhas_pos_filtro_regional": 0,
        "linhas_pos_busca": 0,
        "fallback_sem_filtro": False,
        "filtro_regional_aplicado": aplicar_filtro_regional,
    }
    if df.empty:
        return df, diag
    resultado = df.copy()
    if aplicar_filtro_regional:
        filtrado = filtrar_dataset_por_municipios(resultado, cidades, filtrar_uf_sp=True)
        diag["linhas_pos_filtro_regional"] = len(filtrado)
        if filtrado.empty and len(resultado) > 0:
            diag["fallback_sem_filtro"] = True
        else:
            resultado = filtrado
    else:
        diag["linhas_pos_filtro_regional"] = len(resultado)
    if busca_textual.strip():
        buscado = aplicar_filtro_textual(resultado, busca_textual.strip())
        diag["linhas_pos_busca"] = len(buscado)
        resultado = buscado
    else:
        diag["linhas_pos_busca"] = len(resultado)
    return resultado, diag

@st.cache_data(ttl=1800)
def buscar_clima_atual(lat: float, lon: float) -> Optional[dict[str, Any]]:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,relative_humidity_2m,wind_speed_10m,precipitation,uv_index"
        "&timezone=America%2FSao_Paulo"
    )
    data = fetch_json(url)
    return data.get("current") if data else None

@st.cache_data(ttl=1800)
def buscar_qualidade_ar_atual(lat: float, lon: float) -> Optional[dict[str, Any]]:
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&current=pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone"
        "&timezone=America%2FSao_Paulo"
    )
    data = fetch_json(url)
    return data.get("current") if data else None

@st.cache_data(ttl=3600)
def buscar_historico_pm25_real(lat: float, lon: float, dias: int = DEFAULT_PM25_DAYS) -> pd.DataFrame:
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide"
        f"&past_days={dias}"
        "&timezone=America%2FSao_Paulo"
    )
    data = fetch_json(url)
    if not data or "hourly" not in data:
        return pd.DataFrame(columns=["Data", "PM2.5 médio", "PM10 médio", "NO2 médio", "O3 médio", "SO2 médio", "Tendência (MM 3d)"])
    hourly = data["hourly"]
    df = pd.DataFrame({
        "DataHora": pd.to_datetime(hourly.get("time", []), errors="coerce"),
        "PM2.5": hourly.get("pm2_5", []),
        "PM10": hourly.get("pm10", []),
        "NO2": hourly.get("nitrogen_dioxide", []),
        "O3": hourly.get("ozone", []),
        "SO2": hourly.get("sulphur_dioxide", []),
    })
    if df.empty:
        return pd.DataFrame(columns=["Data", "PM2.5 médio", "PM10 médio", "NO2 médio", "O3 médio", "SO2 médio", "Tendência (MM 3d)"])
    df["Data"] = df["DataHora"].dt.date
    diario = (
        df.groupby("Data", as_index=False)[["PM2.5", "PM10", "NO2", "O3", "SO2"]]
        .mean(numeric_only=True)
        .rename(columns={
            "PM2.5": "PM2.5 médio",
            "PM10": "PM10 médio",
            "NO2": "NO2 médio",
            "O3": "O3 médio",
            "SO2": "SO2 médio",
        })
    )
    diario["Tendência (MM 3d)"] = diario["PM2.5 médio"].rolling(window=3).mean().round(1)
    return diario.copy()

@st.cache_data(ttl=3600)
def buscar_historico_clima_real(lat: float, lon: float, dias: int = DEFAULT_CLIMATE_DAYS) -> pd.DataFrame:
    data_final = date.today()
    data_inicial = data_final - timedelta(days=dias - 1)
    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={data_inicial.isoformat()}"
        f"&end_date={data_final.isoformat()}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
        "&timezone=America%2FSao_Paulo"
    )
    data = fetch_json(url)
    if not data or "daily" not in data:
        return pd.DataFrame(columns=["Data", "Temp Máx", "Temp Mín", "Chuva", "Vento Máx"])
    return pd.DataFrame({
        "Data": pd.to_datetime(data["daily"]["time"]),
        "Temp Máx": data["daily"]["temperature_2m_max"],
        "Temp Mín": data["daily"]["temperature_2m_min"],
        "Chuva": data["daily"]["precipitation_sum"],
        "Vento Máx": data["daily"]["wind_speed_10m_max"],
    })

@st.cache_data(ttl=86400)
def puxar_populacao_ibge_valor(cod_ibge: int) -> Optional[int]:
    url = (
        "https://servicodados.ibge.gov.br/api/v3/agregados/9514/periodos/2022/variaveis/93"
        f"?localidades=N6[{cod_ibge}]"
    )
    data = fetch_json(url, timeout=15)
    if not data:
        return POPULACAO_FALLBACK_IBGE.get(cod_ibge)
    try:
        valor = int(data[0]["resultados"][0]["series"][0]["serie"]["2022"])
        if valor > 0:
            return valor
    except Exception:
        pass
    return POPULACAO_FALLBACK_IBGE.get(cod_ibge)

@st.cache_data(ttl=1800)
def montar_painel_regional(cidades: tuple[str, ...], dias_pm25: int, dias_clima: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    registros, h_ar, h_clima = [], [], []
    for cidade in cidades:
        info = CIDADES[cidade]
        clima = buscar_clima_atual(info["lat"], info["lon"])
        ar = buscar_qualidade_ar_atual(info["lat"], info["lon"])
        pop = puxar_populacao_ibge_valor(info["ibge"])
        hist_ar = buscar_historico_pm25_real(info["lat"], info["lon"], dias=dias_pm25)
        hist_cl = buscar_historico_clima_real(info["lat"], info["lon"], dias=dias_clima)
        if clima and ar:
            registros.append({
                "Cidade": cidade.split(",")[0].strip(),
                "Região": info["regiao"],
                "Latitude": info["lat"],
                "Longitude": info["lon"],
                "População": pop,
                "Temperatura": float(clima.get("temperature_2m", 0)),
                "Umidade": float(clima.get("relative_humidity_2m", 0)),
                "Vento": float(clima.get("wind_speed_10m", 0)),
                "Chuva": float(clima.get("precipitation", 0)),
                "PM2.5": float(ar.get("pm2_5", 0)),
                "PM10": float(ar.get("pm10", 0)),
                "NO2": float(ar.get("nitrogen_dioxide", 0)),
                "SO2": float(ar.get("sulphur_dioxide", 0)),
                "O3": float(ar.get("ozone", 0)),
                "Hora atualização": ar.get("time"),
            })
        if not hist_ar.empty:
            tmp = hist_ar.copy()
            tmp["Cidade"] = cidade.split(",")[0].strip()
            tmp["Região"] = info["regiao"]
            h_ar.append(tmp)
        if not hist_cl.empty:
            tmp = hist_cl.copy()
            tmp["Cidade"] = cidade.split(",")[0].strip()
            tmp["Região"] = info["regiao"]
            h_clima.append(tmp)
    return (
        pd.DataFrame(registros),
        pd.concat(h_ar, ignore_index=True) if h_ar else pd.DataFrame(),
        pd.concat(h_clima, ignore_index=True) if h_clima else pd.DataFrame(),
    )

def montar_resumo_executivo(df_atual: pd.DataFrame) -> list[dict[str, str]]:
    if df_atual.empty:
        return []
    pm25_medio = float(df_atual["PM2.5"].mean()) if "PM2.5" in df_atual.columns else np.nan
    cidade_pm25 = df_atual.sort_values(by="PM2.5", ascending=False).iloc[0]["Cidade"] if "PM2.5" in df_atual.columns else "—"
    cidade_chuva = df_atual.sort_values(by="Chuva", ascending=False).iloc[0]["Cidade"] if "Chuva" in df_atual.columns else "—"
    cidade_temp = df_atual.sort_values(by="Temperatura", ascending=False).iloc[0]["Cidade"] if "Temperatura" in df_atual.columns else "—"
    status_pm25, status_css, detalhe = classificar_pm25(pm25_medio)
    return [
        {
            "titulo": "Leitura regional do ar",
            "conteudo": f"PM2.5 médio de {formatar_decimal_br(pm25_medio, 1, ' μg/m³')} com destaque atual para {cidade_pm25}.",
            "badge": f"<span class='{status_css}'>{status_pm25}</span>",
            "rodape": detalhe,
        },
        {
            "titulo": "Município com maior chuva",
            "conteudo": f"No recorte atual, {cidade_chuva} aparece com o maior volume de precipitação entre os municípios carregados.",
            "badge": "<span class='status-neutral'>Clima</span>",
            "rodape": "Esse indicador ajuda a discutir drenagem, arraste e contraste com a poluição atmosférica.",
        },
        {
            "titulo": "Ponto mais quente",
            "conteudo": f"{cidade_temp} lidera a temperatura na leitura atual do painel.",
            "badge": "<span class='status-neutral'>Temperatura</span>",
            "rodape": "A variação térmica ajuda a contextualizar a dispersão de poluentes e o comportamento meteorológico.",
        },
    ]

def exibir_cards_resumo(df_atual: pd.DataFrame) -> None:
    cards = montar_resumo_executivo(df_atual)
    if not cards:
        return
    cols = st.columns(len(cards))
    for col, card in zip(cols, cards):
        col.markdown(
            f"""
            <div class='section-card'>
                <div style='display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:8px;'>
                    <h3>{card['titulo']}</h3>
                    {card['badge']}
                </div>
                <p>{card['conteudo']}</p>
                <div class='card-footnote'>{card['rodape']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

def exibir_contexto_projeto(nome_area: str, nomes_area: list[str]) -> None:
    st.markdown(
        """
        <div class='section-card'>
            <h3>Objetivo e pergunta de pesquisa</h3>
            <p><strong>Objetivo:</strong> investigar se variações nas concentrações atmosféricas estimadas de PM2.5 e PM10 acompanham mudanças em parâmetros medidos da água, considerando chuva e clima.</p>
            <p><strong>Pergunta:</strong> há associação entre partículas no ar e turbidez, pH, oxigênio dissolvido ou condutividade nos mesmos municípios e períodos?</p>
            <p><strong>Hipótese de trabalho:</strong> partículas e compostos transportados pelo ar podem chegar à água por deposição seca ou úmida; a chuva também pode remover partículas do ar e levar materiais do solo aos rios. A direção e a intensidade da relação dependem do local e das condições do evento.</p>
            <div class='card-footnote'>O estudo usa estimativas de PM do modelo CAMS/Open-Meteo e medições do SIMQUA agregadas por dia. Como não mede a deposição nem a composição química das partículas, os resultados indicam associações temporais e não provam que o material particulado causou uma alteração na água.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def exibir_guia_local() -> None:
    with st.expander("Como alimentar as fontes complementares", expanded=False):
        st.markdown("O app segue esta ordem: **API/endpoint oficial → arquivo local em `data/` → upload manual**.")
        exemplos = [{"Fonte": fonte, "Exemplos de arquivo local": ", ".join(nomes[:3])} for fonte, nomes in MANUAL_SOURCE_CONFIG.items()]
        st.dataframe(pd.DataFrame(exemplos), use_container_width=True, hide_index=True)
        arquivos = listar_arquivos_data()
        if arquivos:
            st.dataframe(pd.DataFrame({"Arquivo": arquivos}), use_container_width=True, hide_index=True)
        else:
            st.warning(f"Nenhum arquivo encontrado na pasta `data/`. Caminho procurado: {DATA_DIR}")

def exibir_status_fontes(automaticas: dict[str, bool], origens: dict[str, str], dfs: dict[str, pd.DataFrame], diags: dict[str, dict[str, Any]]) -> None:
    st.markdown("### Integridade das fontes")

    cols = st.columns(max(1, len(automaticas)))
    for col, (nome, ok) in zip(cols, automaticas.items()):
        status = "status-ok" if ok else "status-warn"
        rotulo = "Ativa" if ok else "Falha"
        col.markdown(
            f"""
            <div class='section-card'>
                <h3 style='margin-bottom:10px'>{nome}</h3>
                <div><span class='{status}'>{rotulo}</span></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if origens:
        st.markdown("### Fontes complementares")
        cols2 = st.columns(max(1, len(origens)))
        for col, nome in zip(cols2, origens.keys()):
            origem = origens[nome]
            df = dfs[nome]
            diag = diags[nome]
            detalhes = []
            if origem:
                detalhes.append(origem)
            if diag.get("linhas_originais", 0):
                detalhes.append(f"orig.: {diag.get('linhas_originais', 0)}")
            if diag.get("filtro_regional_aplicado"):
                detalhes.append(f"reg.: {diag.get('linhas_pos_filtro_regional', 0)}")
            if diag.get("fallback_sem_filtro"):
                detalhes.append("sem filtro regional")
            resumo = f"{len(df)} linhas prontas para uso" if not df.empty else "Sem linhas úteis detectadas"
            col.markdown(
                f"""
                <div class='section-card'>
                    <h3 style='margin-bottom:10px'>{nome}</h3>
                    <p style='margin-bottom:8px'>{resumo}</p>
                    <div style='color:#64748b;font-size:0.84rem'>{' • '.join(detalhes) if detalhes else 'Sem detalhes adicionais'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
def exibir_mapa_municipios(df_atual: pd.DataFrame, area: str) -> None:
    if df_atual.empty:
        st.info("Sem dados atuais para o mapa dos municípios.")
        return
    fig = px.scatter_map(
        df_atual,
        lat="Latitude",
        lon="Longitude",
        size="PM2.5",
        color="PM2.5",
        hover_name="Cidade",
        hover_data={"Região": True, "Temperatura": ":.1f", "Chuva": ":.1f", "Umidade": ":.0f", "PM2.5": ":.1f", "Latitude": False, "Longitude": False},
        zoom=7.2,
        center={"lat": df_atual["Latitude"].mean(), "lon": df_atual["Longitude"].mean()},
        title=f"Mapa dos municípios monitorados — {area}",
    )
    renderizar_grafico(fig, use_container_width=True, key=f"mapa_municipios_{normalizar_texto(area)}")

def _inferir_cidade_costeira(valor: Any) -> str:
    texto = normalizar_texto(valor)
    if not texto:
        return ""
    for cidade in ["Ubatuba", "Caraguatatuba", "São Sebastião", "Ilhabela"]:
        if normalizar_texto(cidade) in texto:
            return cidade
    return ""

def _extrair_lat_lon_de_texto(valor: Any) -> tuple[float | None, float | None]:
    if valor is None or pd.isna(valor):
        return None, None
    texto = str(valor)
    numeros = re.findall(r"-?\d+[\.,]?\d*", texto)
    if len(numeros) < 2:
        return None, None
    nums = []
    for n in numeros[:4]:
        try:
            nums.append(float(str(n).replace(",", ".")))
        except Exception:
            continue
    if len(nums) < 2:
        return None, None
    pares = [(nums[i], nums[i + 1]) for i in range(len(nums) - 1)]
    for a, b in pares:
        lat, lon = (a, b)
        if -30 <= lat <= -20 and -50 <= lon <= -40:
            return lat, lon
        lat, lon = (b, a)
        if -30 <= lat <= -20 and -50 <= lon <= -40:
            return lat, lon
    return None, None

def preparar_mapa_qualidade_agua_cetesb(df: pd.DataFrame, cidades: list[str]) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    base = df.copy()
    col_lat = detectar_coluna(base, ["Latitude", "latitude", "lat", "y", "coord_y", "coordenada_y"])
    col_lon = detectar_coluna(base, ["Longitude", "longitude", "lon", "x", "coord_x", "coordenada_x"])
    col_geo = detectar_coluna(base, ["geometry", "geom", "shape", "wkt", "coordenadas", "localizacao", "localização"])
    col_municipio = detectar_coluna(base, ["municipio", "município", "cidade", "localidade", "munic"])
    col_praia = detectar_coluna(base, ["praia", "nome da praia", "nome_praia", "nome"])
    col_status = detectar_coluna(base, ["Classificação", "classificacao_texto", "classificacao", "classificação", "status", "situacao", "situação"])
    col_data = detectar_coluna(base, ["data_atual", "data", "data coleta", "data_medicao", "semana"])

    base["latitude_mapa"] = base[col_lat].apply(converter_texto_para_numero) if col_lat else np.nan
    base["longitude_mapa"] = base[col_lon].apply(converter_texto_para_numero) if col_lon else np.nan

    if col_geo:
        extraidos = base[col_geo].apply(_extrair_lat_lon_de_texto)
        base["latitude_geo"] = extraidos.apply(lambda x: x[0])
        base["longitude_geo"] = extraidos.apply(lambda x: x[1])
        base["latitude_mapa"] = base["latitude_mapa"].fillna(base["latitude_geo"])
        base["longitude_mapa"] = base["longitude_mapa"].fillna(base["longitude_geo"])

    if col_municipio:
        base["Municipio_mapa"] = base[col_municipio].astype(str).str.strip()
    elif col_praia:
        base["Municipio_mapa"] = base[col_praia].apply(_inferir_cidade_costeira)
    else:
        base["Municipio_mapa"] = ""

    municipios_validos = {cidade.split(",")[0].strip() for cidade in cidades if CIDADES[cidade]["regiao"] == "Litoral Norte"}
    if municipios_validos:
        base["Municipio_norm"] = base["Municipio_mapa"].map(normalizar_texto)
        alvo_norm = {normalizar_texto(c) for c in municipios_validos}
        filtrado = base[base["Municipio_norm"].isin(alvo_norm)].copy()
        if not filtrado.empty:
            base = filtrado

    base["Praia_mapa"] = base[col_praia].astype(str).str.strip() if col_praia else "Ponto CETESB"
    base["Classificacao_mapa"] = base[col_status].astype(str).str.strip() if col_status else "Sem classificação"
    base["Data_mapa"] = pd.to_datetime(base[col_data], errors="coerce", dayfirst=True) if col_data else pd.NaT

    latitudes, longitudes, origens = [], [], []
    for _, row in base.iterrows():
        lat = row.get("latitude_mapa")
        lon = row.get("longitude_mapa")
        municipio = str(row.get("Municipio_mapa", "")).strip()
        cidade_ref = None
        for chave, info in CIDADES.items():
            nome = chave.split(",")[0].strip()
            if normalizar_texto(nome) == normalizar_texto(municipio):
                cidade_ref = info
                break
        if pd.notna(lat) and pd.notna(lon) and -30 <= float(lat) <= -20 and -50 <= float(lon) <= -40:
            latitudes.append(float(lat))
            longitudes.append(float(lon))
            origens.append("CETESB")
        elif cidade_ref:
            latitudes.append(cidade_ref["lat"])
            longitudes.append(cidade_ref["lon"])
            origens.append("Município (fallback)")
        else:
            latitudes.append(np.nan)
            longitudes.append(np.nan)
            origens.append("Sem coordenada")

    base["latitude_mapa"] = latitudes
    base["longitude_mapa"] = longitudes
    base["Origem coordenada"] = origens
    base = base.dropna(subset=["latitude_mapa", "longitude_mapa"]).copy()
    return base

def exibir_mapa_costeiro_cetesb(df: pd.DataFrame, cidades: list[str], area: str) -> None:
    if df.empty:
        st.info("Sem dados da CETESB para o mapa costeiro.")
        return
    base = preparar_mapa_qualidade_agua_cetesb(df, cidades)
    if base.empty:
        st.info("Não foi possível montar o mapa da CETESB com as colunas disponíveis. Tente um arquivo com município, praia ou coordenadas.")
        return
    fig = px.scatter_map(
        base,
        lat="latitude_mapa",
        lon="longitude_mapa",
        color="Classificacao_mapa",
        hover_name="Praia_mapa",
        hover_data={
            "Municipio_mapa": True,
            "Origem coordenada": True,
            "Data_mapa": True,
            "latitude_mapa": False,
            "longitude_mapa": False,
        },
        zoom=8,
        center={"lat": base["latitude_mapa"].mean(), "lon": base["longitude_mapa"].mean()},
        title=f"Mapa de qualidade da água costeira — {area}",
    )
    renderizar_grafico(fig, use_container_width=True, key=f"mapa_costeiro_{normalizar_texto(area)}")
    if (base["Origem coordenada"] == "Município (fallback)").any():
        st.caption("Alguns pontos foram posicionados pelo centro do município porque a base da CETESB não trouxe coordenadas válidas em todas as linhas.")

def exibir_panorama_regional(df_atual: pd.DataFrame, df_pm25: pd.DataFrame, df_clima: pd.DataFrame, area: str) -> None:
    if df_atual.empty:
        st.error("Não foi possível montar o panorama atual da área selecionada.")
        return

    base = df_atual.copy()
    for coluna in ["População", "PM2.5", "Chuva", "Temperatura"]:
        if coluna in base.columns:
            base[coluna] = base[coluna].apply(converter_texto_para_numero)

    populacao_valida = pd.to_numeric(base.get("População"), errors="coerce") if "População" in base.columns else pd.Series(dtype=float)
    if "População" not in base.columns:
        base["População"] = np.nan
        base["População_plot"] = 20.0
    else:
        mediana_pop = populacao_valida.dropna().median()
        if pd.isna(mediana_pop) or mediana_pop <= 0:
            mediana_pop = 1.0
        base["População"] = populacao_valida
        base["População_plot"] = base["População"].fillna(mediana_pop).clip(lower=1)

    st.markdown(
        """
        <div class='section-card'>
            <h3>Síntese do panorama</h3>
            <p>Esta visão combina leituras automáticas de clima, poluentes atmosféricos e população para apresentar rapidamente o comportamento ambiental do recorte selecionado.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        base_bar = base.dropna(subset=["PM2.5", "Cidade"]).sort_values(by="PM2.5", ascending=False)
        if not base_bar.empty:
            fig = px.bar(base_bar, x="PM2.5", y="Cidade", orientation="h", color="PM2.5", text_auto=True, title="PM2.5 atual por município")
            renderizar_grafico(fig, use_container_width=True)
        else:
            st.info("Sem dados válidos de PM2.5 para o gráfico por município.")
    with col2:
        base_disp = base.dropna(subset=["PM2.5", "Chuva"]).copy()
        if not base_disp.empty:
            fig = px.scatter(
                base_disp,
                x="PM2.5",
                y="Chuva",
                size="População_plot",
                color="Região",
                hover_name="Cidade",
                hover_data={"População": ":,.0f", "População_plot": False},
                title="PM2.5 × chuva × população",
            )
            renderizar_grafico(fig, use_container_width=True)
        else:
            st.info("Sem dados válidos para montar a dispersão entre PM2.5 e chuva.")
    exibir_mapa_municipios(base, area)

    c3, c4 = st.columns(2)
    with c3:
        if not df_pm25.empty:
            fig = px.line(df_pm25, x="Data", y="PM2.5 médio", color="Cidade", markers=True, title=f"Histórico real de PM2.5 — {area}")
            fig.add_hline(y=15, line_dash="dash", line_color="green", annotation_text="Referência OMS")
            renderizar_grafico(fig, use_container_width=True)
        else:
            st.info("Sem histórico real de PM2.5.")
    with c4:
        if not df_clima.empty:
            fig = px.line(df_clima, x="Data", y="Chuva", color="Cidade", markers=True, title=f"Precipitação diária real — {area}")
            renderizar_grafico(fig, use_container_width=True)
        else:
            st.info("Sem histórico climático real.")

def exibir_aba_litoral(df_cetesb: pd.DataFrame, cidades: list[str], area: str) -> None:
    if not area_tem_litoral(cidades):
        st.warning("A área selecionada não inclui o Litoral Norte. Prefira Litoral Norte ou Área completa do estudo para esta aba.")
    st.markdown("### Balneabilidade e qualidade da água costeira")
    st.markdown(
        """
        <div class='section-card'>
            <h3>Leitura costeira</h3>
            <p>Esta aba resume a classificação das praias e posiciona os pontos da CETESB no mapa. Quando a base vier sem coordenadas válidas, o painel usa o município como fallback para não perder a leitura espacial.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if df_cetesb.empty:
        st.info(GUIDES_FONTES["CETESB_BALNEABILIDADE"])
        return
    col_status = detectar_coluna(df_cetesb, ["Classificação", "classificacao_texto", "classificacao", "classificação", "status", "situacao", "situação"])
    col_municipio = detectar_coluna(df_cetesb, ["municipio", "município", "cidade", "localidade"])
    col_praia = detectar_coluna(df_cetesb, ["praia", "nome da praia"])
    if col_status and col_municipio:
        resumo = df_cetesb.groupby([col_municipio, col_status]).size().reset_index(name="Quantidade")
        fig = px.bar(resumo, x=col_municipio, y="Quantidade", color=col_status, barmode="group", title="Balneabilidade por município")
        renderizar_grafico(fig, use_container_width=True)
    else:
        cols_show = [c for c in [col_municipio, col_praia, col_status] if c] or df_cetesb.columns.tolist()[:8]
        st.dataframe(df_cetesb[cols_show].head(100), use_container_width=True, hide_index=True)
    exibir_mapa_costeiro_cetesb(df_cetesb, cidades, area)
def _mapear_municipio_estudo(valor: Any, cidades: list[str]) -> str:
    texto = str(valor).strip()
    texto_norm = normalizar_texto(texto)
    for cidade in cidades:
        nome = cidade.split(",")[0].strip()
        if normalizar_texto(nome) in texto_norm:
            return nome
    return texto.strip()

def converter_serie_data_flexivel(serie: pd.Series) -> pd.Series:
    """Converte datas ISO (AAAA-MM-DD) e brasileiras (DD/MM/AAAA) sem inverter mês e dia."""
    texto = serie.astype(str).str.strip()
    resultado = pd.Series(pd.NaT, index=serie.index, dtype="datetime64[ns]")

    mascara_iso = texto.str.match(r"^\d{4}-\d{2}-\d{2}(?:[ T]|$)", na=False)
    if mascara_iso.any():
        resultado.loc[mascara_iso] = pd.to_datetime(
            texto.loc[mascara_iso], errors="coerce", yearfirst=True
        )
    if (~mascara_iso).any():
        resultado.loc[~mascara_iso] = pd.to_datetime(
            texto.loc[~mascara_iso], errors="coerce", dayfirst=True
        )
    return resultado


def _preparar_base_fonte(
    df: pd.DataFrame,
    cidades: list[str],
    date_candidates: list[str],
    city_candidates: list[str],
    metric_map: dict[str, list[str]],
    default_city_label: str,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    base = df.copy()
    col_data = detectar_coluna(base, date_candidates)
    if not col_data:
        col_data = detectar_coluna(base, ["ano", "mes", "mês"])
    col_cidade = detectar_coluna(base, city_candidates)
    if detectar_coluna(base, ["ano"]) and detectar_coluna(base, ["mes", "mês"]) and col_data in {"ano", "mes", "mês", None}:
        ano_col = detectar_coluna(base, ["ano"])
        mes_col = detectar_coluna(base, ["mes", "mês"])
        ano = pd.to_numeric(base[ano_col], errors="coerce")
        mes = pd.to_numeric(base[mes_col], errors="coerce")
        base["data_ref"] = pd.to_datetime(dict(year=ano, month=mes, day=1), errors="coerce")
    elif col_data:
        base["data_ref"] = converter_serie_data_flexivel(base[col_data])
    else:
        return pd.DataFrame()
    if col_cidade:
        base["municipio"] = base[col_cidade].apply(lambda x: _mapear_municipio_estudo(x, cidades))
    else:
        base["municipio"] = default_city_label
    base["municipio_norm"] = base["municipio"].map(normalizar_texto)
    for destino, candidatos in metric_map.items():
        col = detectar_coluna(base, candidatos)
        if col:
            base[destino] = pd.to_numeric(base[col], errors="coerce")
    # Remove valores fisicamente impossíveis antes de calcular as médias diárias.
    # O pH é limitado à escala 0–14; os demais indicadores não podem ser negativos.
    if "ph" in base.columns:
        base.loc[~base["ph"].between(0, 14), "ph"] = np.nan
    for coluna in ["oxigenio_dissolvido", "turbidez", "precipitacao_agua", "condutividade", "nivel", "vazao"]:
        if coluna in base.columns:
            base.loc[base[coluna] < 0, coluna] = np.nan
    metricas = [m for m in metric_map.keys() if m in base.columns]
    if not metricas:
        return pd.DataFrame()
    base = base.dropna(subset=["data_ref"]).copy()
    if base.empty:
        return pd.DataFrame()
    base["data"] = pd.to_datetime(base["data_ref"].dt.date)
    agrupada = base.groupby(["municipio", "municipio_norm", "data"], as_index=False)[metricas].mean(numeric_only=True)
    return agrupada

def preparar_base_simqua(df: pd.DataFrame, cidades: list[str]) -> pd.DataFrame:
    return _preparar_base_fonte(
        df,
        cidades,
        ["data", "datahora", "data_hora", "datetime", "timestamp"],
        ["municipio", "município", "cidade", "estacao", "estação", "ponto", "nome"],
        {
            "ph": ["ph", "potencial hidrogenionico", "potencial hidrogeniônico"],
            "turbidez": ["turbidez"],
            "oxigenio_dissolvido": ["oxigenio_dissolvido", "oxigenio dissolvido", "oxigênio dissolvido", "od"],
            "precipitacao_agua": ["precipitacao", "precipitação", "chuva"],
            "nivel": ["nivel", "nível", "cota"],
            "vazao": ["vazao", "vazão"],
            "condutividade": ["condutividade", "condutividade eletrica"],
            "temperatura_agua": ["temperatura", "temperatura da agua", "temperatura da água"],
        },
        default_city_label="Área de estudo",
    )

def preparar_base_cetesb_ar(df_pm25: pd.DataFrame, cidades: list[str]) -> pd.DataFrame:
    if df_pm25.empty or "Data" not in df_pm25.columns:
        return pd.DataFrame()
    base = df_pm25.copy()
    base["data"] = pd.to_datetime(base["Data"], errors="coerce")
    if "Cidade" in base.columns:
        base["municipio"] = base["Cidade"].apply(lambda x: _mapear_municipio_estudo(x, cidades))
    else:
        base["municipio"] = "Área de estudo"
    base["municipio_norm"] = base["municipio"].map(normalizar_texto)

    mapa = {
        "pm25": "PM2.5 médio",
        "pm10": "PM10 médio",
        "no2": "NO2 médio",
        "o3": "O3 médio",
        "so2": "SO2 médio",
        "pm25_tendencia": "Tendência (MM 3d)",
    }
    for destino, origem in mapa.items():
        if origem in base.columns:
            base[destino] = pd.to_numeric(base[origem], errors="coerce")

    metricas = [c for c in ["pm25", "pm10", "no2", "o3", "so2", "pm25_tendencia"] if c in base.columns]
    base = base.dropna(subset=["data"]).copy()
    if "pm25" in base.columns:
        base = base[base["pm25"].notna()].copy()
    if base.empty or not metricas:
        return pd.DataFrame()
    return base.groupby(["municipio", "municipio_norm", "data"], as_index=False)[metricas].mean(numeric_only=True)

def preparar_base_clima_openmeteo(df_clima: pd.DataFrame, cidades: list[str]) -> pd.DataFrame:
    if df_clima.empty or "Data" not in df_clima.columns:
        return pd.DataFrame()
    base = df_clima.copy()
    base["data"] = pd.to_datetime(base["Data"], errors="coerce")
    if "Cidade" in base.columns:
        base["municipio"] = base["Cidade"].apply(lambda x: _mapear_municipio_estudo(x, cidades))
    else:
        base["municipio"] = "Área de estudo"
    base["municipio_norm"] = base["municipio"].map(normalizar_texto)

    mapa = {
        "temp_max_openmeteo": "Temp Máx",
        "temp_min_openmeteo": "Temp Mín",
        "chuva_openmeteo": "Chuva",
        "vento_max_openmeteo": "Vento Máx",
    }
    for destino, origem in mapa.items():
        if origem in base.columns:
            base[destino] = pd.to_numeric(base[origem], errors="coerce")

    metricas = [c for c in ["temp_max_openmeteo", "temp_min_openmeteo", "chuva_openmeteo", "vento_max_openmeteo"] if c in base.columns]
    base = base.dropna(subset=["data"]).copy()
    if base.empty or not metricas:
        return pd.DataFrame()
    return base.groupby(["municipio", "municipio_norm", "data"], as_index=False)[metricas].mean(numeric_only=True)

@st.cache_data(ttl=21600)
def buscar_historico_ar_intervalo(
    lat: float,
    lon: float,
    data_inicial_iso: str,
    data_final_iso: str,
) -> pd.DataFrame:
    """Busca qualidade do ar no mesmo período do SIMQUA e devolve médias diárias."""
    try:
        inicio = date.fromisoformat(data_inicial_iso)
        fim = min(date.fromisoformat(data_final_iso), date.today())
    except Exception:
        return pd.DataFrame()

    if fim < inicio:
        return pd.DataFrame()

    partes: list[pd.DataFrame] = []
    cursor = inicio
    while cursor <= fim:
        fim_bloco = min(cursor + timedelta(days=59), fim)
        url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={lat}&longitude={lon}"
            "&hourly=pm2_5,pm10,nitrogen_dioxide,ozone,sulphur_dioxide"
            f"&start_date={cursor.isoformat()}&end_date={fim_bloco.isoformat()}"
            "&forecast_days=0"
            "&timezone=America%2FSao_Paulo"
        )
        data = fetch_json(url, timeout=30)
        hourly = data.get("hourly", {}) if data else {}
        tempos = hourly.get("time", [])
        if tempos:
            bloco = pd.DataFrame({
                "data_hora": pd.to_datetime(tempos, errors="coerce"),
                "pm25": hourly.get("pm2_5", []),
                "pm10": hourly.get("pm10", []),
                "no2": hourly.get("nitrogen_dioxide", []),
                "o3": hourly.get("ozone", []),
                "so2": hourly.get("sulphur_dioxide", []),
            })
            partes.append(bloco)
        cursor = fim_bloco + timedelta(days=1)

    if not partes:
        return pd.DataFrame()

    hourly_df = pd.concat(partes, ignore_index=True)
    hourly_df = hourly_df.dropna(subset=["data_hora"]).copy()
    for col in ["pm25", "pm10", "no2", "o3", "so2"]:
        hourly_df[col] = pd.to_numeric(hourly_df[col], errors="coerce")
    hourly_df["data"] = pd.to_datetime(hourly_df["data_hora"].dt.date)
    return hourly_df.groupby("data", as_index=False)[["pm25", "pm10", "no2", "o3", "so2"]].mean(numeric_only=True)


@st.cache_data(ttl=21600)
def buscar_historico_clima_intervalo(
    lat: float,
    lon: float,
    data_inicial_iso: str,
    data_final_iso: str,
) -> pd.DataFrame:
    """Busca clima histórico diário compatível com o período do SIMQUA."""
    try:
        inicio = date.fromisoformat(data_inicial_iso)
        fim = min(date.fromisoformat(data_final_iso), date.today())
    except Exception:
        return pd.DataFrame()

    if fim < inicio:
        return pd.DataFrame()

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={lat}&longitude={lon}"
        f"&start_date={inicio.isoformat()}&end_date={fim.isoformat()}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max"
        "&timezone=America%2FSao_Paulo"
    )
    data = fetch_json(url, timeout=30)
    daily = data.get("daily", {}) if data else {}
    tempos = daily.get("time", [])
    if not tempos:
        return pd.DataFrame()

    return pd.DataFrame({
        "data": pd.to_datetime(tempos, errors="coerce"),
        "temp_max_openmeteo": daily.get("temperature_2m_max", []),
        "temp_min_openmeteo": daily.get("temperature_2m_min", []),
        "chuva_openmeteo": daily.get("precipitation_sum", []),
        "vento_max_openmeteo": daily.get("wind_speed_10m_max", []),
    })


def _info_cidade_por_nome(municipio: str) -> Optional[dict[str, Any]]:
    alvo = normalizar_texto(municipio)
    for chave, info in CIDADES.items():
        if normalizar_texto(chave.split(",")[0].strip()) == alvo:
            return info
    return None


def montar_bases_historicas_compativeis_simqua(
    df_simqua: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Monta ar e clima históricos usando exatamente o período disponível em cada município do SIMQUA."""
    if df_simqua.empty or "data" not in df_simqua.columns or "municipio" not in df_simqua.columns:
        return pd.DataFrame(), pd.DataFrame()

    base = df_simqua.copy()
    base["data"] = pd.to_datetime(base["data"], errors="coerce")
    base = base.dropna(subset=["data", "municipio"]).copy()
    base = base[base["data"].dt.date <= date.today()].copy()
    if base.empty:
        return pd.DataFrame(), pd.DataFrame()

    ar_partes: list[pd.DataFrame] = []
    clima_partes: list[pd.DataFrame] = []

    for municipio, grupo in base.groupby("municipio"):
        info = _info_cidade_por_nome(str(municipio))
        if not info:
            continue
        inicio = grupo["data"].min().date()
        fim = min(grupo["data"].max().date(), date.today())
        if fim < inicio:
            continue

        ar = buscar_historico_ar_intervalo(info["lat"], info["lon"], inicio.isoformat(), fim.isoformat())
        if not ar.empty:
            ar = ar.copy()
            ar["municipio"] = str(municipio)
            ar["municipio_norm"] = normalizar_texto(municipio)
            ar_partes.append(ar)

        clima = buscar_historico_clima_intervalo(info["lat"], info["lon"], inicio.isoformat(), fim.isoformat())
        if not clima.empty:
            clima = clima.copy()
            clima["municipio"] = str(municipio)
            clima["municipio_norm"] = normalizar_texto(municipio)
            clima_partes.append(clima)

    df_ar = pd.concat(ar_partes, ignore_index=True) if ar_partes else pd.DataFrame()
    df_clima = pd.concat(clima_partes, ignore_index=True) if clima_partes else pd.DataFrame()
    return df_ar, df_clima


def montar_base_integrada(
    df_ar: pd.DataFrame,
    df_agua: pd.DataFrame,
    df_clima_openmeteo: pd.DataFrame,
) -> pd.DataFrame:
    if df_ar.empty or df_agua.empty:
        return pd.DataFrame()
    base = df_ar.merge(df_agua, on=["municipio", "municipio_norm", "data"], how="inner")
    if base.empty:
        ar_area = df_ar.groupby("data", as_index=False).mean(numeric_only=True)
        agua_area = df_agua.groupby("data", as_index=False).mean(numeric_only=True)
        base = ar_area.merge(agua_area, on="data", how="inner")
        if base.empty:
            return pd.DataFrame()
        base["municipio"] = "Área integrada"
        base["municipio_norm"] = "area integrada"

    if not df_clima_openmeteo.empty:
        if {"municipio", "municipio_norm"}.issubset(df_clima_openmeteo.columns):
            base = base.merge(df_clima_openmeteo, on=["municipio", "municipio_norm", "data"], how="left")
        else:
            base = base.merge(df_clima_openmeteo.groupby("data", as_index=False).mean(numeric_only=True), on="data", how="left")
    return base.sort_values(["municipio", "data"]).copy()

def _adicionar_linha_tendencia(fig: go.Figure, x: pd.Series, y: pd.Series, nome: str = "Tendência") -> go.Figure:
    x_num = pd.to_numeric(x, errors="coerce")
    y_num = pd.to_numeric(y, errors="coerce")
    mascara = x_num.notna() & y_num.notna()
    if mascara.sum() < 2:
        return fig
    coef = np.polyfit(x_num[mascara], y_num[mascara], 1)
    x_line = np.linspace(x_num[mascara].min(), x_num[mascara].max(), 50)
    y_line = coef[0] * x_line + coef[1]
    fig.add_trace(go.Scatter(x=x_line, y=y_line, mode="lines", name=nome))
    return fig

def nome_amigavel_variavel(nome: str) -> str:
    mapa = {
        "pm25": "PM2.5",
        "pm10": "PM10",
        "no2": "NO₂",
        "o3": "O₃",
        "so2": "SO₂",
        "pm25_tendencia": "PM2.5 tendência (MM 3d)",
        "ph": "pH",
        "turbidez": "Turbidez",
        "oxigenio_dissolvido": "Oxigênio dissolvido",
        "precipitacao_agua": "Precipitação da água",
        "chuva_openmeteo": "Chuva Open-Meteo",
        "nivel": "Nível",
        "vazao": "Vazão",
        "condutividade": "Condutividade",
        "temperatura_agua": "Temperatura da água",
        "temp_max_openmeteo": "Temp. máx Open-Meteo",
        "temp_min_openmeteo": "Temp. mín Open-Meteo",
        "vento_max_openmeteo": "Vento máx Open-Meteo",
    }
    return mapa.get(nome, nome.replace("_", " ").title())

def obter_variavel_precipitacao_integrada(base: pd.DataFrame) -> Optional[str]:
    for coluna in ["chuva_openmeteo", "precipitacao_agua"]:
        if coluna in base.columns and base[coluna].notna().sum() >= 3:
            return coluna
    return None

def preparar_mapa_intensidade_integrada(base: pd.DataFrame, variaveis: list[str]) -> pd.DataFrame:
    if base.empty or "municipio" not in base.columns:
        return pd.DataFrame()
    cols_validas = [col for col in variaveis if col in base.columns]
    if not cols_validas:
        return pd.DataFrame()
    agregado = base.groupby("municipio", as_index=False)[cols_validas].mean(numeric_only=True)
    latitudes, longitudes = [], []
    for municipio in agregado["municipio"]:
        lat, lon = np.nan, np.nan
        for chave, info in CIDADES.items():
            nome = chave.split(",")[0].strip()
            if normalizar_texto(nome) == normalizar_texto(municipio):
                lat, lon = info["lat"], info["lon"]
                break
        latitudes.append(lat)
        longitudes.append(lon)
    agregado["Latitude"] = latitudes
    agregado["Longitude"] = longitudes
    return agregado.dropna(subset=["Latitude", "Longitude"]).copy()

def obter_variaveis_clima_ml(base: pd.DataFrame) -> list[str]:
    candidatos = [
        "temp_max_openmeteo", "temp_min_openmeteo", "vento_max_openmeteo", "chuva_openmeteo",
    ]
    return [c for c in candidatos if c in base.columns and base[c].notna().sum() >= 5]


def resumir_associacoes_particulas(base: pd.DataFrame) -> pd.DataFrame:
    """Resume associações de Spearman entre PM2.5/PM10 e parâmetros da água."""
    particulas = [c for c in ["pm25", "pm10"] if c in base.columns]
    indicadores_agua = [
        c for c in ["turbidez", "ph", "oxigenio_dissolvido", "condutividade"]
        if c in base.columns
    ]
    linhas: list[dict[str, Any]] = []
    grupos = base.groupby("municipio", dropna=False) if "municipio" in base.columns else [("Área integrada", base)]
    for municipio, grupo in grupos:
        for particula in particulas:
            for indicador in indicadores_agua:
                colunas = [particula, indicador] + (["data"] if "data" in grupo.columns else [])
                pares = grupo[colunas].copy()
                pares[particula] = pd.to_numeric(pares[particula], errors="coerce")
                pares[indicador] = pd.to_numeric(pares[indicador], errors="coerce")
                pares = pares.dropna(subset=[particula, indicador])
                if len(pares) < 5:
                    continue
                rho = float(pares[particula].corr(pares[indicador], method="spearman"))
                if not np.isfinite(rho):
                    continue
                linhas.append({
                    "Município": str(municipio),
                    "Partícula no ar": f"{nome_amigavel_variavel(particula)} (μg/m³)",
                    "Indicador da água": nome_amigavel_variavel(indicador),
                    "Pares município-dia": len(pares),
                    "Datas distintas": int(pares["data"].nunique()) if "data" in pares.columns else len(pares),
                    "Spearman ρ": rho,
                    "Direção": "Positiva" if rho > 0 else "Negativa" if rho < 0 else "Sem direção",
                })
    return pd.DataFrame(linhas)


def _indices_particao_temporal(dados: pd.DataFrame, proporcao_treino: float = 0.7) -> tuple[pd.Index, pd.Index]:
    """Separa dias mais antigos para treino e dias posteriores para teste."""
    if "data" not in dados.columns or dados.empty:
        return pd.Index([]), pd.Index([])
    datas = pd.to_datetime(dados["data"], errors="coerce").dt.normalize()
    dias = pd.Series(datas.dropna().unique()).sort_values().tolist()
    if len(dias) < 6:
        return pd.Index([]), pd.Index([])
    indice_corte = max(1, min(int(len(dias) * proporcao_treino), len(dias) - 1))
    corte = pd.Timestamp(dias[indice_corte])
    return dados.index[datas < corte], dados.index[datas >= corte]


def rodar_modelagem_turbidez(base: pd.DataFrame) -> Optional[dict[str, Any]]:
    if base.empty or RandomForestRegressor is None or "turbidez" not in base.columns:
        return None

    particulas = [c for c in ["pm25", "pm10"] if c in base.columns and base[c].notna().sum() >= 6]
    if not particulas:
        return None
    features = particulas + obter_variaveis_clima_ml(base)

    trabalho = base.copy()
    trabalho["data"] = pd.to_datetime(trabalho.get("data"), errors="coerce")
    trabalho["turbidez"] = pd.to_numeric(trabalho["turbidez"], errors="coerce")
    trabalho = trabalho.dropna(subset=["data", "turbidez"]).sort_values(["data", "municipio"] if "municipio" in trabalho else ["data"]).copy()
    X = trabalho[features].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(trabalho["turbidez"], errors="coerce")
    features = [c for c in features if X[c].notna().sum() >= 6]
    X = X[features].copy()
    if len(X) < 20:
        return None

    base_ok = trabalho.copy()
    base_ok["turbidez_prevista"] = np.nan
    metricas: dict[str, float] = {}
    idx_treino, idx_teste = _indices_particao_temporal(base_ok)
    if len(idx_treino) >= 10 and len(idx_teste) >= 4:
        X_treino = X.loc[idx_treino].copy()
        X_teste = X.loc[idx_teste].copy()
        medianas_treino = X_treino.median(numeric_only=True)
        features_treino = medianas_treino[medianas_treino.notna()].index.tolist()
        if features_treino:
            X_treino = X_treino[features_treino].fillna(medianas_treino[features_treino])
            X_teste = X_teste[features_treino].fillna(medianas_treino[features_treino])
            avaliador = RandomForestRegressor(n_estimators=350, min_samples_leaf=2, random_state=42)
            avaliador.fit(X_treino, y.loc[idx_treino])
            y_pred = avaliador.predict(X_teste)
            base_ok.loc[idx_teste, "turbidez_prevista"] = y_pred
            if mean_absolute_error is not None:
                metricas["MAE"] = float(mean_absolute_error(y.loc[idx_teste], y_pred))
            if r2_score is not None and len(idx_teste) >= 2:
                metricas["R2"] = float(r2_score(y.loc[idx_teste], y_pred))
            metricas["N_TREINO"] = float(len(idx_treino))
            metricas["N_TESTE"] = float(len(idx_teste))

    medianas = X.median(numeric_only=True)
    X_final = X.fillna(medianas)
    modelo_final = RandomForestRegressor(n_estimators=350, min_samples_leaf=2, random_state=42)
    modelo_final.fit(X_final, y)

    importancias = pd.DataFrame({
        "Variável": [nome_amigavel_variavel(c) for c in features],
        "Importância": modelo_final.feature_importances_,
    }).sort_values("Importância", ascending=False)

    return {
        "base": base_ok,
        "metricas": metricas,
        "importancias": importancias,
        "features": [nome_amigavel_variavel(c) for c in features],
        "n": int(len(base_ok)),
    }

def exibir_aba_integracao(
    df_simqua: pd.DataFrame,
    df_openmeteo_ar: pd.DataFrame,
    df_clima_openmeteo: pd.DataFrame,
    area: str,
) -> None:
    st.markdown("### Partículas atmosféricas e qualidade da água")
    st.markdown(
        """
        **Objetivo do TCC:** analisar se as concentrações diárias de **PM2.5 e PM10** no ar estão associadas
        a mudanças em indicadores da água — **turbidez, pH, oxigênio dissolvido e condutividade** —
        considerando a chuva e o clima como contexto.

        Partículas e compostos atmosféricos podem chegar à superfície por deposição seca ou pela chuva.
        A precipitação também pode lavar partículas do ar e carregar materiais do solo para os rios; por isso,
        uma associação observada não identifica, sozinha, qual caminho ocorreu.
        """
    )
    st.caption(
        "Método: médias diárias do SIMQUA são cruzadas por município e data com estimativas de qualidade do ar "
        "e meteorologia do Open-Meteo, em coordenadas municipais. O produto de ar é baseado em modelos CAMS "
        "(grade global de aproximadamente 45 km), não em um sensor local de PM. "
        "O painel não mede fluxo de deposição nem a composição química das partículas."
    )
    with st.expander("Fontes e referências utilizadas", expanded=False):
        st.markdown(
            """
            - [CETESB — SIMQUA](https://simqua.cetesb.sp.gov.br/): parâmetros e séries automáticas de qualidade da água.
            - [Open-Meteo — Air Quality API](https://open-meteo.com/en/docs/air-quality-api): estimativas de PM2.5 e PM10 baseadas em modelos CAMS.
            - [U.S. EPA — Air-Surface Exchange Process Overview](https://www.epa.gov/cmaq/air-surface-exchange-process-overview): descreve deposição seca e úmida de partículas e gases.
            - [Estudo brasileiro sobre deposição atmosférica no Rio Cachoeira, Bahia](https://www.scielo.br/j/jbchs/a/Rm8766z8CDnzV35P8FvPtTQ/?lang=en): analisa íons e nitrogênio dissolvido na deposição atmosférica.
            """
        )

    if df_simqua.empty:
        st.info(GUIDES_FONTES["SIMQUA"])
    if df_openmeteo_ar.empty:
        st.info(GUIDES_FONTES["OPENMETEO_AR"])

    if df_simqua.empty or df_openmeteo_ar.empty:
        st.warning("Para testar a relação entre partículas e água, carregue uma base SIMQUA e obtenha o histórico de PM do Open-Meteo.")
        return

    base = montar_base_integrada(df_openmeteo_ar, df_simqua, df_clima_openmeteo)
    if base.empty:
        st.warning("As bases foram carregadas, mas não houve cruzamento suficiente por data e município.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("Pares município-dia", len(base))
    c2.metric("Municípios cruzados", base["municipio"].nunique())
    c3.metric("Período", f"{base['data'].min().strftime('%d/%m/%Y')} a {base['data'].max().strftime('%d/%m/%Y')}")

    indicadores_resumo = [
        ("pm25", "PM2.5 médio", " μg/m³"),
        ("pm10", "PM10 médio", " μg/m³"),
        ("turbidez", "Turbidez média", " NTU"),
        ("ph", "pH médio", ""),
    ]
    colunas_resumo = st.columns(len(indicadores_resumo))
    for coluna, (variavel, rotulo, unidade) in zip(colunas_resumo, indicadores_resumo):
        valores = pd.to_numeric(base.get(variavel), errors="coerce") if variavel in base.columns else pd.Series(dtype=float)
        media = valores.mean() if not valores.empty else np.nan
        coluna.metric(rotulo, formatar_card_valor(media, 2 if variavel == "ph" else 1, unidade))

    abas = st.tabs([
        "🌫️ PM × água",
        "🕒 Série temporal",
        "🔥 Correlação",
        "📆 Médias semanais/mensais",
        "⏭️ Efeito defasado",
        "🗺️ Mapa intensidade",
        "🧩 Matriz de dispersão",
        "🤖 ML turbidez",
        "🧾 Base integrada",
    ])

    with abas[0]:
        indicadores_agua = [
            c for c in ["turbidez", "ph", "oxigenio_dissolvido", "condutividade"]
            if c in base.columns and base[c].notna().sum() >= 3
        ]
        if indicadores_agua:
            indicador = st.selectbox(
                "Indicador da qualidade da água",
                indicadores_agua,
                format_func=nome_amigavel_variavel,
                key=f"indicador_agua_{normalizar_texto(area)}",
            )
            colunas_grafico = st.columns(2)
            for coluna, particula in zip(colunas_grafico, ["pm25", "pm10"]):
                if particula not in base.columns:
                    coluna.info(f"Sem dados de {nome_amigavel_variavel(particula)} no período cruzado.")
                    continue
                tmp = base[["municipio", particula, indicador]].dropna().copy()
                if len(tmp) < 3:
                    coluna.info(f"Sem pares suficientes de {nome_amigavel_variavel(particula)} e {nome_amigavel_variavel(indicador)}.")
                    continue
                fig = px.scatter(
                    tmp, x=particula, y=indicador, color="municipio", hover_name="municipio",
                    title=f"{nome_amigavel_variavel(particula)} × {nome_amigavel_variavel(indicador)}",
                    labels={particula: f"{nome_amigavel_variavel(particula)} (μg/m³)", indicador: nome_amigavel_variavel(indicador)},
                )
                fig = _adicionar_linha_tendencia(fig, tmp[particula], tmp[indicador])
                with coluna:
                    renderizar_grafico(fig, use_container_width=True)
        else:
            st.info("A base cruzada ainda não tem indicadores de água suficientes para comparar com PM2.5 e PM10.")

        associacoes = resumir_associacoes_particulas(base)
        if not associacoes.empty:
            st.markdown("#### Resumo das associações")
            st.caption("Spearman ρ resume a direção e a intensidade de uma associação monotônica; não demonstra causalidade nem substitui teste estatístico.")
            exibicao = associacoes.copy()
            exibicao["Spearman ρ"] = exibicao["Spearman ρ"].round(3)
            st.dataframe(exibicao, use_container_width=True, hide_index=True)

    with abas[1]:
        particulas_cols = [c for c in ["pm25", "pm10"] if c in base.columns]
        agua_cols = [c for c in ["turbidez", "ph", "oxigenio_dissolvido", "condutividade"] if c in base.columns]
        if "data" not in base.columns or not particulas_cols or not agua_cols:
            st.info("Sem dados suficientes para a série temporal.")
        else:
            agua_escolhida = st.selectbox(
                "Indicador da água para a série temporal",
                agua_cols,
                format_func=nome_amigavel_variavel,
                key=f"serie_agua_{normalizar_texto(area)}",
            )
            serie = base.groupby("data", as_index=False)[particulas_cols + [agua_escolhida]].mean(numeric_only=True)
            col_ar, col_agua = st.columns(2)
            with col_ar:
                fig_ar = px.line(
                    serie, x="data", y=particulas_cols, markers=True,
                    title="Concentração diária de partículas (μg/m³)",
                    labels={c: nome_amigavel_variavel(c) for c in particulas_cols},
                )
                renderizar_grafico(fig_ar, use_container_width=True)
            with col_agua:
                fig_agua = px.line(
                    serie, x="data", y=agua_escolhida, markers=True,
                    title=f"Série diária — {nome_amigavel_variavel(agua_escolhida)}",
                    labels={agua_escolhida: nome_amigavel_variavel(agua_escolhida)},
                )
                renderizar_grafico(fig_agua, use_container_width=True)

    with abas[2]:
        heat_cols = [c for c in [
            "pm25", "pm10", "turbidez", "ph", "oxigenio_dissolvido", "condutividade", "chuva_openmeteo",
        ] if c in base.columns and base[c].notna().sum() >= 3]
        if len(heat_cols) >= 3:
            corr = base[heat_cols].corr(method="spearman", numeric_only=True)
            fig = px.imshow(corr, text_auto=True, aspect="auto", zmin=-1, zmax=1, color_continuous_scale="RdBu", title="Associação de Spearman — partículas, água e chuva")
            renderizar_grafico(fig, use_container_width=True)
            st.caption("A matriz usa pares disponíveis em cada combinação. Valores próximos de −1 ou +1 indicam associação monotônica; associação não comprova deposição nem causalidade.")
        else:
            st.info("Sem variáveis suficientes para o heatmap.")

    with abas[3]:
        particulas_cols = [c for c in ["pm25", "pm10"] if c in base.columns]
        agua_cols = [c for c in ["turbidez", "ph", "oxigenio_dissolvido", "condutividade"] if c in base.columns]
        if len(particulas_cols) < 1 or len(agua_cols) < 1 or "data" not in base.columns:
            st.info("Sem dados suficientes para o gráfico de médias agregadas.")
        else:
            periodicidade = st.radio("Agregação temporal", ["Semanal", "Mensal"], horizontal=True, key=f"periodicidade_{normalizar_texto(area)}")
            regra = "W" if periodicidade == "Semanal" else "MS"
            serie = base.groupby("data", as_index=False)[particulas_cols + agua_cols].mean(numeric_only=True).set_index("data")
            agregado = serie.resample(regra).mean().reset_index()
            agua_escolhida = st.selectbox(
                "Indicador da água",
                agua_cols,
                format_func=nome_amigavel_variavel,
                key=f"agregado_agua_{normalizar_texto(area)}",
            )
            col_ar, col_agua = st.columns(2)
            with col_ar:
                fig_ar = px.line(agregado, x="data", y=particulas_cols, markers=True, title=f"Médias {periodicidade.lower()} de PM2.5/PM10 (μg/m³)")
                renderizar_grafico(fig_ar, use_container_width=True)
            with col_agua:
                fig_agua = px.line(agregado, x="data", y=agua_escolhida, markers=True, title=f"Média {periodicidade.lower()} — {nome_amigavel_variavel(agua_escolhida)}")
                renderizar_grafico(fig_agua, use_container_width=True)
            colunas_tabela = ["data"] + particulas_cols + [agua_escolhida]
            st.dataframe(agregado[colunas_tabela].rename(columns={c: nome_amigavel_variavel(c) for c in colunas_tabela if c != "data"}), use_container_width=True, hide_index=True)

    with abas[4]:
        indicadores_agua = [c for c in ["turbidez", "ph", "oxigenio_dissolvido", "condutividade"] if c in base.columns and base[c].notna().sum() >= 3]
        particulas_cols = [c for c in ["pm25", "pm10"] if c in base.columns and base[c].notna().sum() >= 3]
        if not indicadores_agua or not particulas_cols:
            st.info("Sem dados coincidentes suficientes de partículas e indicadores da água para a análise defasada.")
        else:
            agua_escolhida = st.selectbox("Indicador futuro da água", indicadores_agua, format_func=nome_amigavel_variavel, key=f"lag_agua_{normalizar_texto(area)}")
            atraso = st.slider("Defasagem entre as datas (dias)", 1, 3, 1, key=f"lag_dias_{normalizar_texto(area)}")
            base_lag = base.sort_values(["municipio", "data"]).copy()
            futura = base_lag[["municipio", "data", agua_escolhida]].copy()
            futura["data"] = pd.to_datetime(futura["data"]) - pd.Timedelta(days=atraso)
            futura = futura.rename(columns={agua_escolhida: "indicador_futuro"})
            pares_lag = base_lag.merge(futura, on=["municipio", "data"], how="inner")
            col_lag_1, col_lag_2 = st.columns(2)
            for coluna, particula in zip([col_lag_1, col_lag_2], particulas_cols):
                tmp = pares_lag[["municipio", particula, "indicador_futuro"]].dropna().copy()
                if len(tmp) < 3:
                    coluna.info(f"Sem pares suficientes para {nome_amigavel_variavel(particula)} e o indicador futuro.")
                    continue
                fig = px.scatter(
                    tmp, x=particula, y="indicador_futuro", color="municipio", hover_name="municipio",
                    title=f"{nome_amigavel_variavel(particula)} hoje × {nome_amigavel_variavel(agua_escolhida)} em {atraso} dia(s)",
                )
                fig = _adicionar_linha_tendencia(fig, tmp[particula], tmp["indicador_futuro"])
                with coluna:
                    renderizar_grafico(fig, use_container_width=True)
            st.caption("A defasagem compara dias de calendário exatos. Mudanças podem refletir chuva, vazão, uso do solo ou outras fontes; não atribua a variação apenas à deposição atmosférica.")

    with abas[5]:
        variaveis_mapa = [c for c in ["pm25", "pm10", "no2", "o3", "turbidez"] if c in base.columns and base[c].notna().sum() >= 3]
        mapa_base = preparar_mapa_intensidade_integrada(base, variaveis_mapa)
        if mapa_base.empty or mapa_base["municipio"].nunique() < 2:
            st.info("O mapa de intensidade fica melhor quando há mais de um município ou estação no recorte integrado.")
        else:
            escolha = st.selectbox("Variável do mapa", variaveis_mapa, format_func=nome_amigavel_variavel, key=f"mapa_var_{normalizar_texto(area)}")
            fig = px.scatter_map(
                mapa_base,
                lat="Latitude",
                lon="Longitude",
                size=escolha,
                color=escolha,
                hover_name="municipio",
                zoom=7.2,
                center={"lat": mapa_base["Latitude"].mean(), "lon": mapa_base["Longitude"].mean()},
                title=f"Mapa de intensidade — {nome_amigavel_variavel(escolha)}",
            )
            renderizar_grafico(fig, use_container_width=True, key=f"mapa_int_{normalizar_texto(area)}_{escolha}")

    with abas[6]:
        vars_matriz = [c for c in ["pm25", "pm10", "no2", "o3", "turbidez", "ph", "precipitacao_agua", "condutividade"] if c in base.columns and base[c].notna().sum() >= 3]
        if len(vars_matriz) < 3:
            st.info("Sem variáveis suficientes para a matriz de dispersão.")
        else:
            matriz = base.dropna(subset=vars_matriz).copy()
            if len(matriz) > 500:
                matriz = matriz.sample(500, random_state=42)
            labels = {col: nome_amigavel_variavel(col) for col in vars_matriz}
            fig = px.scatter_matrix(matriz, dimensions=vars_matriz, color="municipio", title="Matriz de dispersão entre poluentes do ar, água e clima", labels=labels)
            fig.update_traces(diagonal_visible=False, showupperhalf=False)
            renderizar_grafico(fig, use_container_width=True)

    with abas[7]:
        payload = rodar_modelagem_turbidez(base)
        if not payload:
            st.info("O modelo exploratório precisa de pelo menos 20 pares diários válidos de turbidez e PM2.5 ou PM10 no período integrado.")
        else:
            metricas = payload["metricas"]
            if metricas:
                c_mae, c_r2, c_n = st.columns(3)
                c_mae.metric("MAE no período de teste", formatar_decimal_br(metricas.get("MAE", np.nan), 2, " NTU"))
                c_r2.metric("R² no período de teste", formatar_decimal_br(metricas.get("R2", np.nan), 3))
                c_n.metric("Dias-ponto no teste", int(metricas.get("N_TESTE", 0)))
                st.caption(
                    f"Validação temporal: {int(metricas.get('N_TREINO', 0))} observações antigas para treino e "
                    f"{int(metricas.get('N_TESTE', 0))} observações posteriores para teste. R² pode ser negativo."
                )
            else:
                st.info("Há dados para ajustar um modelo exploratório, mas poucos dias para formar um teste temporal separado.")
            st.caption("Preditores: " + ", ".join(payload["features"]) + ". Importância preditiva não significa causa.")
            base_ml = payload["base"].dropna(subset=["turbidez_prevista"]).copy()
            if not base_ml.empty:
                fig = px.scatter(base_ml, x="turbidez", y="turbidez_prevista", color="municipio", hover_name="municipio", title="Turbidez observada × estimada no teste temporal")
                minimo = float(base_ml[["turbidez", "turbidez_prevista"]].min().min())
                maximo = float(base_ml[["turbidez", "turbidez_prevista"]].max().max())
                fig.add_shape(type="line", x0=minimo, y0=minimo, x1=maximo, y1=maximo)
                renderizar_grafico(fig, use_container_width=True)
            fig_imp = px.bar(payload["importancias"], x="Importância", y="Variável", orientation="h", title="Importância preditiva das variáveis no ajuste final")
            renderizar_grafico(fig_imp, use_container_width=True)

    with abas[8]:
        st.dataframe(base.sort_values(["municipio", "data"]), use_container_width=True, hide_index=True)
        st.download_button(
            "📥 Baixar base integrada (CSV)",
            data=base.to_csv(index=False).encode("utf-8"),
            file_name=f"base_integrada_openmeteo_ar_agua_{normalizar_texto(area)}.csv",
            mime="text/csv",
        )

def rodar_modelagem_qualidade_ar(df_atual: pd.DataFrame) -> dict[str, dict[str, Any]]:
    resultados: dict[str, dict[str, Any]] = {}
    if df_atual.empty or RandomForestRegressor is None:
        return resultados
    features = [c for c in ["Temperatura", "Umidade", "Vento", "Chuva", "População"] if c in df_atual.columns]
    if len(features) < 2:
        return resultados
    X = df_atual[features].apply(pd.to_numeric, errors="coerce").fillna(df_atual[features].median(numeric_only=True))
    for alvo in ["PM2.5", "NO2"]:
        if alvo not in df_atual.columns:
            continue
        y = pd.to_numeric(df_atual[alvo], errors="coerce")
        mascara = y.notna()
        if mascara.sum() < 8:
            continue
        X_ok = X.loc[mascara].copy()
        y_ok = y.loc[mascara].copy()
        base_ok = df_atual.loc[mascara].copy()
        metricas = {}
        if train_test_split is not None and len(base_ok) >= 10:
            X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(X_ok, y_ok, base_ok.index, test_size=0.3, random_state=42)
            modelo = RandomForestRegressor(n_estimators=300, random_state=42)
            modelo.fit(X_train, y_train)
            y_pred = modelo.predict(X_test)
            base_ok.loc[idx_test, "previsto_rf"] = y_pred
            acuracia = calcular_acuracia_percentual(y_test, y_pred)
            if pd.notna(acuracia):
                metricas["ACURACIA"] = acuracia
            if mean_absolute_error is not None:
                metricas["MAE"] = float(mean_absolute_error(y_test, y_pred))
            if r2_score is not None and len(y_test) >= 2:
                metricas["R2"] = float(r2_score(y_test, y_pred))
        else:
            modelo = RandomForestRegressor(n_estimators=300, random_state=42)
            modelo.fit(X_ok, y_ok)
            base_ok["previsto_rf"] = modelo.predict(X_ok)
        importancias = pd.DataFrame({"Variavel": features, "Importancia": modelo.feature_importances_}).sort_values("Importancia", ascending=False)
        resultados[alvo] = {"base": base_ok, "metricas": metricas, "importancias": importancias}
    return resultados

def exibir_bloco_predicao_qualidade_ar(df_atual: pd.DataFrame, area: str) -> None:
    st.markdown("### Predição de qualidade do ar")
    st.markdown("Este bloco mantém a modelagem automática com dados meteorológicos e poluentes para apoio ao EcoRadar.")
    resultados = rodar_modelagem_qualidade_ar(df_atual)
    if not resultados:
        st.info("São necessárias observações municipais com temperatura, umidade, vento, chuva e poluentes para estimar PM2.5/NO2.")
        return
    abas = st.tabs([f"🌫️ {alvo}" for alvo in resultados.keys()])
    for aba, alvo in zip(abas, resultados.keys()):
        payload = resultados[alvo]
        with aba:
            exibir_cards_metricas_modelo(payload["metricas"], unidade_mae=" μg/m³")
            base = payload["base"]
            fig = px.scatter(base.dropna(subset=["previsto_rf"]), x=alvo, y="previsto_rf", hover_name="Cidade", title=f"Observado × previsto — {alvo}")
            minimo = float(base[[alvo, "previsto_rf"]].min().min())
            maximo = float(base[[alvo, "previsto_rf"]].max().max())
            fig.add_shape(type="line", x0=minimo, y0=minimo, x1=maximo, y1=maximo)
            renderizar_grafico(fig, use_container_width=True)
            fig_imp = px.bar(payload["importancias"], x="Importancia", y="Variavel", orientation="h", title=f"Importância das variáveis meteorológicas — {alvo}")
            renderizar_grafico(fig_imp, use_container_width=True)



def _treinar_modelo_simulador_agua(
    base: pd.DataFrame,
    alvo: str,
    top_n: int = 4,
) -> Optional[dict[str, Any]]:
    """Treina um simulador exploratório com teste temporal para parâmetros da água."""
    if base.empty or RandomForestRegressor is None or alvo not in base.columns:
        return None

    candidatos = [
        "pm25", "pm10", "chuva_openmeteo", "temp_max_openmeteo", "temp_min_openmeteo",
        "vento_max_openmeteo", "no2", "o3", "so2",
    ]
    features = [
        coluna for coluna in candidatos
        if coluna in base.columns and pd.to_numeric(base[coluna], errors="coerce").notna().sum() >= 6
    ]
    if not any(coluna in features for coluna in ["pm25", "pm10"]):
        return None

    trabalho = base[["data", alvo] + (["municipio"] if "municipio" in base.columns else []) + features].copy()
    trabalho["data"] = pd.to_datetime(trabalho["data"], errors="coerce")
    trabalho[alvo] = pd.to_numeric(trabalho[alvo], errors="coerce")
    trabalho = trabalho.dropna(subset=["data", alvo]).sort_values(["data", "municipio"] if "municipio" in trabalho else ["data"]).copy()
    if len(trabalho) < 20:
        return None

    X = trabalho[features].apply(pd.to_numeric, errors="coerce")
    y = trabalho[alvo]
    idx_treino, idx_teste = _indices_particao_temporal(trabalho)
    if len(idx_treino) < 12 or len(idx_teste) < 4:
        return None

    X_treino_raw = X.loc[idx_treino].copy()
    X_teste_raw = X.loc[idx_teste].copy()
    medianas_treino = X_treino_raw.median(numeric_only=True)
    validas = medianas_treino[medianas_treino.notna()].index.tolist()
    if not any(coluna in validas for coluna in ["pm25", "pm10"]):
        return None
    X_treino = X_treino_raw[validas].fillna(medianas_treino[validas])
    X_teste = X_teste_raw[validas].fillna(medianas_treino[validas])

    # A seleção de variáveis e a avaliação usam somente os dias mais antigos.
    seletor = RandomForestRegressor(n_estimators=350, min_samples_leaf=2, random_state=42)
    seletor.fit(X_treino, y.loc[idx_treino])
    ranking = pd.DataFrame({
        "variavel": validas,
        "importancia": seletor.feature_importances_,
    }).sort_values("importancia", ascending=False)

    features_top = ranking.head(min(top_n, len(ranking)))["variavel"].tolist()
    X_treino_top = X_treino[features_top].copy()
    X_teste_top = X_teste[features_top].copy()
    metricas: dict[str, float] = {}
    avaliador = RandomForestRegressor(n_estimators=400, min_samples_leaf=2, random_state=42)
    avaliador.fit(X_treino_top, y.loc[idx_treino])
    previsto = avaliador.predict(X_teste_top)
    if mean_absolute_error is not None:
        metricas["MAE"] = float(mean_absolute_error(y.loc[idx_teste], previsto))
    if r2_score is not None and len(idx_teste) >= 2:
        metricas["R2"] = float(r2_score(y.loc[idx_teste], previsto))
    metricas["N_TREINO"] = float(len(idx_treino))
    metricas["N_TESTE"] = float(len(idx_teste))

    # O cenário interativo usa um ajuste final treinado com todos os registros disponíveis.
    medianas_finais = X[features_top].median(numeric_only=True)
    X_final = X[features_top].fillna(medianas_finais)
    modelo = RandomForestRegressor(n_estimators=450, min_samples_leaf=2, random_state=42)
    modelo.fit(X_final, y)

    importancia_final = pd.DataFrame({
        "variavel": features_top,
        "importancia": modelo.feature_importances_,
    }).sort_values("importancia", ascending=False)

    estatisticas: dict[str, dict[str, float]] = {}
    for coluna in features_top:
        serie = pd.to_numeric(trabalho[coluna], errors="coerce")
        estatisticas[coluna] = {
            "mediana": float(serie.median()),
            "min": float(serie.min()),
            "max": float(serie.max()),
        }

    alvo_serie = pd.to_numeric(trabalho[alvo], errors="coerce")
    alvo_stats = {
        "mediana": float(alvo_serie.median()),
        "min": float(alvo_serie.min()),
        "max": float(alvo_serie.max()),
        "media": float(alvo_serie.mean()),
    }

    return {
        "alvo": alvo,
        "modelo": modelo,
        "features": features_top,
        "importancias": importancia_final,
        "estatisticas": estatisticas,
        "alvo_stats": alvo_stats,
        "metricas": metricas,
        "n": int(len(trabalho)),
    }


def _frase_comparacao_simulador(valor: float, mediana: float, nome: str, unidade: str = "") -> str:
    if not np.isfinite(valor) or not np.isfinite(mediana):
        return f"Estimativa de {nome}: {_numero_br(valor, 2)}{unidade}."
    diferenca = valor - mediana
    tolerancia = max(abs(mediana) * 0.05, 0.05)
    if abs(diferenca) <= tolerancia:
        return (
            f"A estimativa de {nome} fica próxima da mediana observada no recorte "
            f"({_numero_br(mediana, 2)}{unidade})."
        )
    direcao = "acima" if diferenca > 0 else "abaixo"
    return (
        f"A estimativa de {nome} fica {direcao} da mediana observada no recorte "
        f"({_numero_br(mediana, 2)}{unidade})."
    )


def _card_ranking_simulador(titulo: str, payload: Optional[dict[str, Any]], icone: str) -> None:
    if not payload:
        st.markdown(
            f"""
            <div class='section-card'>
                <h3>{icone} {html.escape(titulo)}</h3>
                <p>Não há dados integrados suficientes para selecionar variáveis e treinar este modelo.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    ranking = payload["importancias"].copy()
    total = float(ranking["importancia"].sum()) if not ranking.empty else 0.0
    itens = []
    for _, row in ranking.iterrows():
        nome = nome_amigavel_variavel(str(row["variavel"]))
        pct = (float(row["importancia"]) / total * 100.0) if total > 0 else 0.0
        itens.append(
            f"<li><strong>{html.escape(nome)}</strong> — aproximadamente {_numero_br(pct, 1)}% da importância do modelo.</li>"
        )

    qualidade = ""
    if payload.get("metricas"):
        m = payload["metricas"]
        partes = []
        if "MAE" in m:
            partes.append(f"MAE {_numero_br(m['MAE'], 2)}")
        if "R2" in m:
            partes.append(f"R² {_numero_br(m['R2'], 2)}")
        if partes:
            qualidade = " • Validação: " + " | ".join(partes)

    st.markdown(
        f"""
        <div class='section-card'>
            <h3>{icone} {html.escape(titulo)}</h3>
            <p>O simulador selecionou as variáveis com maior importância preditiva no trecho de treino. Essa importância não representa causa ou efeito ambiental.</p>
            <ul style='margin-top:0.7rem;margin-bottom:0.4rem;color:var(--text-soft);line-height:1.6'>{''.join(itens)}</ul>
            <div class='card-footnote'>{payload['n']} registros usados{html.escape(qualidade)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def exibir_aba_simulador(
    df_simqua: pd.DataFrame,
    df_openmeteo_ar: pd.DataFrame,
    df_clima_openmeteo: pd.DataFrame,
    area: str,
) -> None:
    st.markdown("### 🧪 Cenários exploratórios para pH e turbidez")
    st.markdown(
        """
        <div class='section-card'>
            <h3>Como funciona</h3>
            <p>
                Informe níveis de <strong>PM2.5 e PM10</strong> e, quando disponíveis, chuva e condições meteorológicas.
                O Random Forest foi ajustado com os dados diários integrados para estimar <strong>pH</strong> e
                <strong>turbidez</strong>. A seleção de variáveis e a avaliação usam uma separação temporal entre
                dias antigos e posteriores.
            </p>
            <div class='card-footnote'>
                Este cenário é uma exploração matemática do conjunto observado, não uma medição ou previsão operacional.
                Não substitui análise laboratorial ou monitoramento CETESB/SIMQUA e não demonstra que PM tenha causado
                alteração na água; o app não mede deposição atmosférica nem a composição química do material particulado.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df_simqua.empty or df_openmeteo_ar.empty:
        st.warning("O simulador precisa de dados do SIMQUA e do histórico de qualidade do ar no mesmo período.")
        return

    base = montar_base_integrada(df_openmeteo_ar, df_simqua, df_clima_openmeteo)
    if base.empty:
        st.warning("Não houve datas coincidentes entre as bases de ar e água para montar o simulador.")
        return

    dias_simqua = int(pd.to_datetime(df_simqua["data"], errors="coerce").dt.date.nunique()) if "data" in df_simqua.columns else 0
    dias_ar = int(pd.to_datetime(df_openmeteo_ar["data"], errors="coerce").dt.date.nunique()) if "data" in df_openmeteo_ar.columns else 0
    dias_integrados = int(pd.to_datetime(base["data"], errors="coerce").dt.date.nunique()) if "data" in base.columns else 0
    d1, d2, d3 = st.columns(3)
    d1.metric("Dias SIMQUA", dias_simqua)
    d2.metric("Dias de ar compatíveis", dias_ar)
    d3.metric("Dias cruzados", dias_integrados)
    st.caption("O treino cruza médias diárias de ar modeladas pelo CAMS/Open-Meteo e medições do SIMQUA nas datas e municípios coincidentes.")

    modelo_turbidez = _treinar_modelo_simulador_agua(base, "turbidez")
    modelo_ph = _treinar_modelo_simulador_agua(base, "ph")

    c1, c2 = st.columns(2)
    with c1:
        _card_ranking_simulador("Variáveis mais relevantes para turbidez", modelo_turbidez, "🌫️")
    with c2:
        _card_ranking_simulador("Variáveis mais relevantes para pH", modelo_ph, "💧")

    modelos_disponiveis = [p for p in [modelo_turbidez, modelo_ph] if p]
    if not modelos_disponiveis:
        valid_turb = int(pd.to_numeric(base.get("turbidez"), errors="coerce").notna().sum()) if "turbidez" in base.columns else 0
        valid_ph = int(pd.to_numeric(base.get("ph"), errors="coerce").notna().sum()) if "ph" in base.columns else 0
        st.info(
            f"O cruzamento produziu {len(base)} registro(s) diário(s), com {valid_turb} valor(es) de turbidez "
            f"e {valid_ph} valor(es) de pH disponíveis. Para treinar o simulador são necessários pelo menos "
            "20 pares município-dia válidos de indicador da água e PM2.5 ou PM10, com datas suficientes para teste temporal."
        )
        return

    features_form: list[str] = []
    for payload in modelos_disponiveis:
        for feature in payload["features"]:
            if feature not in features_form:
                features_form.append(feature)

    # Estatísticas combinadas para sugerir valores iniciais e mostrar a faixa observada.
    stats_form: dict[str, dict[str, float]] = {}
    for feature in features_form:
        serie = pd.to_numeric(base.get(feature), errors="coerce")
        if serie is None or serie.dropna().empty:
            continue
        stats_form[feature] = {
            "mediana": float(serie.median()),
            "min": float(serie.min()),
            "max": float(serie.max()),
        }

    st.markdown("#### Informe partículas e variáveis meteorológicas")
    st.caption("Os campos começam com a mediana observada no recorte. Testes fora da faixa observada são extrapolações.")

    valores_usuario: dict[str, float] = {}
    with st.form(key=f"form_simulador_agua_{normalizar_texto(area)}"):
        colunas = st.columns(2)
        for i, feature in enumerate(features_form):
            stats = stats_form.get(feature, {"mediana": 0.0, "min": 0.0, "max": 0.0})
            nome = nome_amigavel_variavel(feature)
            ajuda = (
                f"Faixa observada no recorte: {_numero_br(stats['min'], 2)} a {_numero_br(stats['max'], 2)}. "
                "É possível testar valores fora dessa faixa, mas a incerteza da estimativa aumenta."
            )
            with colunas[i % 2]:
                valores_usuario[feature] = st.number_input(
                    nome,
                    value=float(round(stats["mediana"], 2)),
                    step=0.10,
                    format="%.2f",
                    help=ajuda,
                    key=f"sim_{normalizar_texto(area)}_{feature}",
                )
        enviar = st.form_submit_button("🧪 Gerar cenário exploratório", type="primary")

    if enviar:
        resultado: dict[str, Any] = {"area": area, "entradas": dict(valores_usuario)}
        for nome_modelo, payload in [("turbidez", modelo_turbidez), ("ph", modelo_ph)]:
            if not payload:
                continue
            linha = pd.DataFrame([[valores_usuario[f] for f in payload["features"]]], columns=payload["features"])
            pred = float(payload["modelo"].predict(linha)[0])
            if nome_modelo == "turbidez":
                pred = max(0.0, pred)
            elif nome_modelo == "ph":
                pred = float(np.clip(pred, 0.0, 14.0))
            resultado[nome_modelo] = pred
        st.session_state["resultado_simulador_agua"] = resultado

    resultado = st.session_state.get("resultado_simulador_agua")
    if not resultado or resultado.get("area") != area:
        return

    st.markdown("#### Resultado da simulação")
    saidas = []
    if "turbidez" in resultado and modelo_turbidez:
        saidas.append(("🌫️", "Turbidez estimada", resultado["turbidez"], " NTU", modelo_turbidez))
    if "ph" in resultado and modelo_ph:
        saidas.append(("💧", "pH estimado", resultado["ph"], "", modelo_ph))

    cols_saida = st.columns(len(saidas)) if saidas else []
    for col, (icone, titulo, valor, unidade, payload) in zip(cols_saida, saidas):
        mediana = payload["alvo_stats"]["mediana"]
        conclusao = _frase_comparacao_simulador(
            valor,
            mediana,
            "turbidez" if "Turbidez" in titulo else "pH",
            unidade,
        )
        with col:
            st.markdown(
                f"""
                <div class='model-metric-card' style='min-height:190px'>
                    <div class='model-metric-head'>
                        <div class='model-metric-icon'>{icone}</div>
                        <div class='model-metric-title'>{html.escape(titulo)}</div>
                    </div>
                    <div class='model-metric-value'>{_numero_br(valor, 2)}{html.escape(unidade)}</div>
                    <div class='model-metric-caption'>{html.escape(conclusao)}</div>
                    <div class='model-metric-formula'>Cenário estimado com os preditores selecionados no ajuste do modelo.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if saidas:
        partes = []
        if "turbidez" in resultado:
            partes.append(f"turbidez próxima de {_numero_br(resultado['turbidez'], 2)} NTU")
        if "ph" in resultado:
            partes.append(f"pH próximo de {_numero_br(resultado['ph'], 2)}")
        st.markdown(
            f"""
            <div class='section-card' style='margin-top:0.9rem'>
                <h3>📌 Conclusão simples</h3>
                <p>Com os valores atmosféricos informados, o modelo estima {' e '.join(partes)} no recorte selecionado.</p>
                <div class='card-footnote'>
                    Interprete o resultado como uma hipótese computacional para exploração no EcoRadar, e não como medição real da qualidade da água.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("Ver valores usados na simulação", expanded=False):
        tabela = pd.DataFrame({
            "Variável": [nome_amigavel_variavel(k) for k in resultado["entradas"].keys()],
            "Valor informado": list(resultado["entradas"].values()),
        })
        st.dataframe(tabela, use_container_width=True, hide_index=True)

def exibir_aba_modelagem(df_atual: pd.DataFrame, area: str) -> None:
    st.markdown("### Contexto complementar: qualidade do ar")
    st.markdown(
        """
        Esta análise meteorológica complementa o TCC, mas não responde à pergunta principal sobre partículas e água.
        A relação central é explorada na aba **Partículas atmosféricas e qualidade da água**, com PM2.5/PM10,
        indicadores do SIMQUA e chuva.
        """
    )
    exibir_bloco_predicao_qualidade_ar(df_atual, area)

with st.sidebar:
    exibir_logo_sidebar()
    st.title("EcoRadar")
    st.markdown("**TCC: partículas do ar e indicadores da qualidade da água.**")
    modo_visual = st.radio("Tema visual", ["Noturno", "Claro"], index=0, horizontal=True)
    st.checkbox("🧭 Mostrar interpretações dos gráficos", value=True, key="mostrar_interpretacoes_graficos", help="Exibe uma leitura simples e automática dos resultados abaixo de cada gráfico.")
    st.markdown("Use a barra lateral para trocar o recorte, ajustar janelas históricas e conectar bases complementares.")
    st.markdown("---")
    opcoes_area = list(REGIOES.keys()) + list(CIDADES.keys())
    area_escolhida = st.selectbox("Selecione a área de análise:", opcoes_area)
    dias_pm25 = st.slider("Janela do histórico de PM2.5 (dias)", 7, 30, DEFAULT_PM25_DAYS)
    dias_clima = st.slider("Janela do histórico climático (dias)", 7, 30, DEFAULT_CLIMATE_DAYS)
    st.markdown("---")
    busca_textual_geral = st.text_input("Filtro textual opcional nas fontes complementares", placeholder="Ex.: pindamonhangaba, simqua, guaratinguetá")
    aplicar_filtro_regional_complementares = st.checkbox("Aplicar filtro regional nas fontes complementares", value=True)
    st.markdown("---")
    with st.expander("Uploads opcionais", expanded=False):
        up_simqua = st.file_uploader("SIMQUA — CSV/XLSX", type=["csv", "xlsx", "xls"], key="up_simqua", accept_multiple_files=True)
        up_cetesb = st.file_uploader("CETESB Balneabilidade/Qualidade da água — CSV/XLSX", type=["csv", "xlsx", "xls"], key="up_cetesb")

def main() -> None:
    aplicar_tema_interface(modo_visual)
    cidades_selecionadas = obter_cidades_area(area_escolhida)
    nome_area = area_escolhida
    nomes_area = nomes_municipios(cidades_selecionadas)

    with st.spinner("Carregando APIs automáticas, arquivos locais e uploads..."):
        df_atual, df_pm25, df_clima = montar_painel_regional(tuple(cidades_selecionadas), dias_pm25, dias_clima)

        raw_cetesb, origem_cetesb = carregar_fonte_hibrida("CETESB_BALNEABILIDADE", up_cetesb)
        raw_simqua, origem_simqua = carregar_fonte_hibrida("SIMQUA", up_simqua)

        df_cetesb, diag_cetesb = preparar_fonte(raw_cetesb, cidades_selecionadas, busca_textual_geral, aplicar_filtro_regional_complementares)
        df_simqua_bruto, diag_simqua = preparar_fonte(raw_simqua, cidades_selecionadas, busca_textual_geral, aplicar_filtro_regional_complementares)

        df_simqua = preparar_base_simqua(df_simqua_bruto, cidades_selecionadas)
        df_cetesb_ar_recente = preparar_base_cetesb_ar(df_pm25, cidades_selecionadas)
        df_clima_recente = preparar_base_clima_openmeteo(df_clima, cidades_selecionadas)

        # Para integrar com o SIMQUA, buscamos ar e clima no MESMO período histórico da água.
        df_ar_historico_simqua, df_clima_historico_simqua = montar_bases_historicas_compativeis_simqua(df_simqua)
        df_cetesb_ar = df_ar_historico_simqua if not df_ar_historico_simqua.empty else df_cetesb_ar_recente
        df_clima_openmeteo = df_clima_historico_simqua if not df_clima_historico_simqua.empty else df_clima_recente

    exibir_topo_dashboard(df_atual, df_simqua, nome_area, nomes_area)
    exibir_contexto_projeto(nome_area, nomes_area)
    exibir_guia_local()

    if not df_simqua.empty and not df_ar_historico_simqua.empty:
        periodo_ini = pd.to_datetime(df_ar_historico_simqua["data"], errors="coerce").min()
        periodo_fim = pd.to_datetime(df_ar_historico_simqua["data"], errors="coerce").max()
        if pd.notna(periodo_ini) and pd.notna(periodo_fim):
            st.caption(
                f"🔗 Integração temporal automática: Open-Meteo Ar carregado de "
                f"{periodo_ini.strftime('%d/%m/%Y')} a {periodo_fim.strftime('%d/%m/%Y')} para coincidir com o SIMQUA."
            )


    if df_atual.empty:
        st.error("Não foi possível montar o panorama principal com as APIs automáticas.")
        st.stop()

    serie_hora = pd.to_datetime(df_atual["Hora atualização"], errors="coerce")
    if serie_hora.notna().any():
        st.caption(f"🕒 Última atualização capturada nas APIs automáticas: {serie_hora.max().strftime('%d/%m/%Y às %H:%M')} (horário local)")

    automaticas = {
        "Open-Meteo clima": not df_clima.empty,
        "Open-Meteo Ar": not df_pm25.empty,
        "IBGE população": df_atual["População"].notna().any(),
        "CETESB REST": not raw_cetesb.empty,
    }
    origens = {
        "Balneabilidade CETESB": origem_cetesb,
        "SIMQUA": origem_simqua,
        "Open-Meteo Ar": "API automática",
        "Open-Meteo clima": "API automática",
    }
    dfs = {
        "Balneabilidade CETESB": df_cetesb,
        "SIMQUA": df_simqua_bruto,
        "Open-Meteo Ar": df_pm25,
        "Open-Meteo clima": df_clima,
    }
    diags = {
        "Balneabilidade CETESB": diag_cetesb,
        "SIMQUA": diag_simqua,
        "Open-Meteo Ar": {"linhas_originais": len(df_pm25), "linhas_pos_filtro_regional": len(df_pm25), "linhas_pos_busca": len(df_pm25), "fallback_sem_filtro": False, "filtro_regional_aplicado": False},
        "Open-Meteo clima": {"linhas_originais": len(df_clima), "linhas_pos_filtro_regional": len(df_clima), "linhas_pos_busca": len(df_clima), "fallback_sem_filtro": False, "filtro_regional_aplicado": False},
    }
    exibir_status_fontes(automaticas, origens, dfs, diags)
    exibir_cards_resumo(df_atual)

    abas = st.tabs([
        "🌎 Panorama regional",
        "🌫️ Partículas do ar × água",
        "🏖️ Litoral Norte e balneabilidade",
        "🔬 Contexto da qualidade do ar",
        "🧪 Simulador exploratório",
    ])
    with abas[0]:
        exibir_panorama_regional(df_atual, df_pm25, df_clima, nome_area)
    with abas[1]:
        exibir_aba_integracao(df_simqua, df_cetesb_ar, df_clima_openmeteo, nome_area)
    with abas[2]:
        exibir_aba_litoral(df_cetesb, cidades_selecionadas, nome_area)
    with abas[3]:
        exibir_aba_modelagem(df_atual, nome_area)
    with abas[4]:
        exibir_aba_simulador(df_simqua, df_cetesb_ar, df_clima_openmeteo, nome_area)

    st.divider()
    st.markdown(
        '''
        ### Arquivos locais esperados em `data/`
        - `simqua.csv` ou `simqua.xlsx`
        - `cetesb.csv` ou `balneabilidade.csv`

        A análise principal cruza médias diárias de PM2.5/PM10, medições do SIMQUA e chuva/clima. Consulte o README do projeto para objetivo, método, limitações e referências.
        '''
    )

if __name__ == "__main__":
    main()
