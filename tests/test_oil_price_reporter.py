"""
Tests for oil_price_reporter.py
"""

import os
import sys
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest

from oil_price_reporter import (
    _change_html,
    build_html,
    build_text,
    has_successful_quotes,
    main,
)


SAMPLE_SECTIONS = [
    {
        "key": "energy",
        "title": "能源",
        "title_en": "Energy",
        "items": [
            {
                "symbol": "CL=F",
                "name": "WTI 原油 (纽约商品交易所)",
                "name_en": "WTI Crude Oil (NYMEX)",
                "unit": "USD/桶",
                "price": 82.50,
                "change": 1.20,
                "change_pct": 1.48,
                "error": None,
            },
            {
                "symbol": "BZ=F",
                "name": "布伦特原油 (ICE)",
                "name_en": "Brent Crude Oil (ICE)",
                "unit": "USD/桶",
                "price": 86.10,
                "change": -0.50,
                "change_pct": -0.58,
                "error": None,
            },
        ],
        "notes": [
            "OPEC 一篮子油价：https://www.opec.org/opec_web/en/data_graphs/40.htm",
        ],
    },
    {
        "key": "metals",
        "title": "贵金属",
        "title_en": "Precious Metals",
        "items": [
            {
                "symbol": "GC=F",
                "name": "黄金 (COMEX)",
                "name_en": "Gold Futures (COMEX)",
                "unit": "USD/盎司",
                "price": 2350.40,
                "change": 10.25,
                "change_pct": 0.44,
                "error": None,
            }
        ],
        "notes": [],
    },
    {
        "key": "fx",
        "title": "外汇",
        "title_en": "Foreign Exchange",
        "items": [
            {
                "symbol": "USDCNY=X",
                "name": "美元/人民币",
                "name_en": "USD/CNY",
                "unit": "CNY",
                "price": 7.22,
                "change": 0.03,
                "change_pct": 0.42,
                "error": None,
            },
            {
                "symbol": "EURUSD=X",
                "name": "欧元/美元",
                "name_en": "EUR/USD",
                "unit": "USD",
                "price": None,
                "change": None,
                "change_pct": None,
                "error": "无数据",
            },
        ],
        "notes": [],
    },
]

REPORT_TIME = "2024-01-15 00:00:00"


def test_change_html_positive():
    html = _change_html(1.20, 1.48)
    assert "▲" in html
    assert "+1.20" in html
    assert "+1.48%" in html
    assert "#43a047" in html


def test_change_html_negative():
    html = _change_html(-0.50, -0.58)
    assert "▼" in html
    assert "-0.50" in html
    assert "-0.58%" in html
    assert "#e53935" in html


def test_change_html_none():
    html = _change_html(None, None)
    assert "N/A" in html


def test_build_text_contains_header_and_sections():
    text = build_text(SAMPLE_SECTIONS, REPORT_TIME)
    assert "全球市场晨报" in text
    assert REPORT_TIME in text
    assert "[能源 / Energy]" in text
    assert "[贵金属 / Precious Metals]" in text
    assert "[外汇 / Foreign Exchange]" in text


def test_build_text_contains_gold_and_fx():
    text = build_text(SAMPLE_SECTIONS, REPORT_TIME)
    assert "黄金 (COMEX)" in text
    assert "2350.40" in text
    assert "美元/人民币" in text
    assert "7.22" in text


def test_build_text_contains_error_and_notes():
    text = build_text(SAMPLE_SECTIONS, REPORT_TIME)
    assert "欧元/美元: 错误 - 无数据" in text
    assert "https://www.opec.org/opec_web/en/data_graphs/40.htm" in text


def test_build_html_is_html():
    html = build_html(SAMPLE_SECTIONS, REPORT_TIME)
    assert html.strip().startswith("<!DOCTYPE html>")
    assert "</html>" in html


def test_build_html_contains_sections_and_values():
    html = build_html(SAMPLE_SECTIONS, REPORT_TIME)
    assert "全球市场晨报" in html
    assert "能源 <span>Energy</span>" in html
    assert "贵金属 <span>Precious Metals</span>" in html
    assert "外汇 <span>Foreign Exchange</span>" in html
    assert "2350.40" in html
    assert "7.22" in html


def test_build_html_contains_error_and_note():
    html = build_html(SAMPLE_SECTIONS, REPORT_TIME)
    assert "无数据" in html
    assert "https://www.opec.org/opec_web/en/data_graphs/40.htm" in html


def test_has_successful_quotes_true():
    assert has_successful_quotes(SAMPLE_SECTIONS) is True


def test_has_successful_quotes_false():
    failed_sections = [
        {
            "key": "fx",
            "title": "外汇",
            "title_en": "Foreign Exchange",
            "items": [
                {
                    "symbol": "USDCNY=X",
                    "name": "美元/人民币",
                    "name_en": "USD/CNY",
                    "unit": "CNY",
                    "price": None,
                    "change": None,
                    "change_pct": None,
                    "error": "网络异常",
                }
            ],
            "notes": [],
        }
    ]
    assert has_successful_quotes(failed_sections) is False


def test_main_exits_nonzero_when_all_fetches_fail(monkeypatch):
    failed_sections = [
        {
            "key": "energy",
            "title": "能源",
            "title_en": "Energy",
            "items": [
                {
                    "symbol": "CL=F",
                    "name": "WTI 原油 (纽约商品交易所)",
                    "name_en": "WTI Crude Oil (NYMEX)",
                    "unit": "USD/桶",
                    "price": None,
                    "change": None,
                    "change_pct": None,
                    "error": "网络异常",
                }
            ],
            "notes": [],
        }
    ]

    monkeypatch.delenv("EMAIL_SENDER", raising=False)
    monkeypatch.delenv("EMAIL_PASSWORD", raising=False)
    monkeypatch.delenv("EMAIL_RECEIVER", raising=False)

    with patch("oil_price_reporter.fetch_market_sections", return_value=failed_sections):
        with pytest.raises(SystemExit) as exc_info:
            main()

    assert exc_info.value.code == 1
