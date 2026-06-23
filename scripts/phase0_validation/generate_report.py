#!/usr/bin/env python3
"""
Generate docs/data_source_report.md by aggregating all Phase 0 validation results.

Reads every results/*.json produced by the validate_*.py scripts and produces
a structured Markdown report with:
  - Executive summary table
  - Per-market coverage tables
  - Source recommendation matrix
  - Action items / gaps

Run:
    python generate_report.py

Output: ../../docs/data_source_report.md  (relative to this script)
"""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
RESULTS_DIR = SCRIPT_DIR / "results"
DOCS_DIR = SCRIPT_DIR.parent.parent / "docs"
OUT_FILE = DOCS_DIR / "data_source_report.md"

# Expected result files -> human label mapping
RESULT_FILES: dict[str, str] = {
    "tw_finmind_result.json": "Taiwan (TW)",
    "us_stocks_result.json":  "United States (US)",
    "jp_stocks_result.json":  "Japan (JP)",
    "kr_stocks_result.json":  "Korea (KR)",
    "memory_quotes_result.json": "DRAMeXchange Quotes",
}


# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------


def load_results() -> dict[str, Any]:
    """Load all available result JSON files.

    Returns:
        Dict mapping filename -> parsed JSON or None if missing.
    """
    loaded: dict[str, Any] = {}
    for fname, label in RESULT_FILES.items():
        path = RESULTS_DIR / fname
        if not path.exists():
            logger.warning("Missing results file: %s — run the corresponding validator first.", fname)
            loaded[fname] = None
        else:
            try:
                loaded[fname] = json.loads(path.read_text(encoding="utf-8"))
                logger.info("Loaded %s (%s)", fname, label)
            except json.JSONDecodeError as exc:
                logger.error("JSON parse error in %s: %s", fname, exc)
                loaded[fname] = None
    return loaded


# ---------------------------------------------------------------------------
# Markdown helpers
# ---------------------------------------------------------------------------


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a GitHub-flavoured Markdown table string.

    Args:
        headers: Column header strings.
        rows:    List of row lists (all strings).

    Returns:
        Multi-line Markdown table string.
    """
    sep = ["-" * max(len(h), 4) for h in headers]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def _status_emoji(status: str) -> str:
    mapping = {
        "success": "✅",
        "no_data": "⚠️",
        "fail": "❌",
        "quota_exceeded": "🚫",
        "auth_fail": "🔑",
        "rate_limited": "⏳",
        "skipped": "⏭️",
        "none": "❌",
    }
    return mapping.get(status, "❓")


def _pct(n: int, total: int) -> str:
    if total == 0:
        return "N/A"
    return f"{round(n / total * 100, 1)}%"


# ---------------------------------------------------------------------------
# Section builders
# ---------------------------------------------------------------------------


def _section_tw(data: dict[str, Any] | None) -> str:
    if data is None:
        return "> ⚠️ **tw_finmind_result.json not found** — run `validate_tw_finmind.py` first.\n"

    summary = data.get("summary", {})
    period = data.get("period", {})
    results = data.get("results", [])

    lines = [
        f"**Source:** FinMind (`TaiwanStockPrice`)  ",
        f"**Period:** {period.get('start_date')} → {period.get('end_date')}  ",
        f"**Total tickers:** {summary.get('total')}  ",
        "",
        _md_table(
            ["Metric", "Count", "Pct"],
            [
                ["Success", str(summary.get("success", 0)), _pct(summary.get("success", 0), summary.get("total", 1))],
                ["No Data", str(summary.get("no_data", 0)), _pct(summary.get("no_data", 0), summary.get("total", 1))],
                ["Fail",    str(summary.get("fail", 0)),    _pct(summary.get("fail", 0),    summary.get("total", 1))],
            ],
        ),
        "",
    ]

    if summary.get("quota_hit"):
        lines.append("> 🚫 **Quota exceeded** during run — not all tickers were tested.\n")

    # Per-ticker table (compact)
    ticker_rows = []
    for r in results:
        st = r.get("status", "?")
        ticker_rows.append([
            r.get("ticker", ""),
            r.get("name", ""),
            f"{_status_emoji(st)} {st}",
            str(r.get("row_count", "")),
            str(r.get("last_date", "")),
        ])

    if ticker_rows:
        lines.append(
            _md_table(
                ["Ticker", "Name", "Status", "Rows", "Last Date"],
                ticker_rows,
            )
        )

    return "\n".join(lines)


def _section_us(data: dict[str, Any] | None) -> str:
    if data is None:
        return "> ⚠️ **us_stocks_result.json not found** — run `validate_us_stocks.py` first.\n"

    summary = data.get("summary", {})
    coverage = summary.get("source_coverage", {})
    results = data.get("results", [])
    period = summary.get("period", {})

    lines = [
        f"**Sources:** FinMind (`USStockPrice`), Stooq (CSV), Alpha Vantage  ",
        f"**Period:** {period.get('start_date')} → {period.get('end_date')}  ",
        f"**Total tickers:** {summary.get('total_tickers')}  ",
        "",
        "### Source Coverage",
        _md_table(
            ["Source", "Success", "Total", "Coverage %"],
            [
                [
                    src.capitalize(),
                    str(coverage.get(src, {}).get("success", 0)),
                    str(coverage.get(src, {}).get("total", 0)),
                    f"{coverage.get(src, {}).get('pct', 0)}%",
                ]
                for src in ("finmind", "stooq", "alphavantage")
            ],
        ),
        "",
    ]

    no_src = summary.get("tickers_with_no_source", [])
    if no_src:
        lines.append(f"> ⚠️ **No source available for:** {', '.join(no_src)}\n")

    # Per-ticker table
    ticker_rows = []
    for r in results:
        fm = r.get("finmind", {})
        stooq = r.get("stooq", {})
        av = r.get("alphavantage", {})
        ticker_rows.append([
            r.get("ticker", ""),
            f"{_status_emoji(fm.get('status', 'fail'))} {fm.get('status', '?')}",
            f"{_status_emoji(stooq.get('status', 'fail'))} {stooq.get('status', '?')}",
            f"{_status_emoji(av.get('status', 'fail'))} {av.get('status', '?')}",
            r.get("best_source", "none"),
        ])

    if ticker_rows:
        lines.append("\n### Per-Ticker Coverage")
        lines.append(
            _md_table(
                ["Ticker", "FinMind", "Stooq", "AlphaVantage", "Best Source"],
                ticker_rows,
            )
        )

    return "\n".join(lines)


def _section_jp(data: dict[str, Any] | None) -> str:
    if data is None:
        return "> ⚠️ **jp_stocks_result.json not found** — run `validate_jp_stocks.py` first.\n"

    summary = data.get("summary", {})
    coverage = summary.get("source_coverage", {})
    results = data.get("results", [])
    period = summary.get("period", {})
    notes = data.get("notes", {})

    lines = [
        f"**Sources:** Stooq (`<code>.jp`), yfinance (`<code>.T`)  ",
        f"**Period:** {period.get('start_date')} → {period.get('end_date')}  ",
        f"**Total tickers:** {summary.get('total_tickers')}  ",
        "",
    ]

    if notes.get("kioxia"):
        lines.append(f"> 📌 **Kioxia note:** {notes['kioxia']}\n")

    lines += [
        "### Source Coverage",
        _md_table(
            ["Source", "Success", "Total", "Coverage %"],
            [
                [
                    src.capitalize(),
                    str(coverage.get(src, {}).get("success", 0)),
                    str(coverage.get(src, {}).get("total", 0)),
                    f"{coverage.get(src, {}).get('pct', 0)}%",
                ]
                for src in ("stooq", "yfinance")
            ],
        ),
        "",
    ]

    no_src = summary.get("tickers_with_no_source", [])
    if no_src:
        lines.append(f"> ⚠️ **No source available for:** {', '.join(no_src)}\n")

    ticker_rows = []
    for r in results:
        stooq = r.get("stooq", {})
        yf = r.get("yfinance", {})
        ticker_rows.append([
            r.get("code", ""),
            r.get("yf_symbol", ""),
            f"{_status_emoji(stooq.get('status', 'fail'))} {stooq.get('status', '?')}",
            f"{_status_emoji(yf.get('status', 'fail'))} {yf.get('status', '?')}",
            r.get("best_source", "none"),
        ])

    if ticker_rows:
        lines.append("\n### Per-Ticker Coverage")
        lines.append(
            _md_table(
                ["Code", "yfinance Symbol", "Stooq", "yfinance", "Best Source"],
                ticker_rows,
            )
        )

    return "\n".join(lines)


def _section_kr(data: dict[str, Any] | None) -> str:
    if data is None:
        return "> ⚠️ **kr_stocks_result.json not found** — run `validate_kr_stocks.py` first.\n"

    summary = data.get("summary", {})
    coverage = summary.get("source_coverage", {})
    results = data.get("results", [])
    period = summary.get("period", {})
    notes = data.get("notes", {})

    lines = [
        f"**Sources:** yfinance (`.KS`/`.KQ`), Stooq (`.kr`)  ",
        f"**Period:** {period.get('start_date')} → {period.get('end_date')}  ",
        f"**Total tickers:** {summary.get('total_tickers')}  ",
        "",
    ]

    if notes.get("stooq_coverage"):
        lines.append(f"> 📌 **Stooq note:** {notes['stooq_coverage']}\n")

    lines += [
        "### Source Coverage",
        _md_table(
            ["Source", "Success", "Total", "Coverage %"],
            [
                [
                    src.capitalize(),
                    str(coverage.get(src, {}).get("success", 0)),
                    str(coverage.get(src, {}).get("total", 0)),
                    f"{coverage.get(src, {}).get('pct', 0)}%",
                ]
                for src in ("yfinance", "stooq")
            ],
        ),
        "",
    ]

    no_src = summary.get("tickers_with_no_source", [])
    if no_src:
        lines.append(f"> ⚠️ **No source available for:** {', '.join(no_src)}\n")

    ticker_rows = []
    for r in results:
        yf = r.get("yfinance", {})
        stooq = r.get("stooq", {})
        ticker_rows.append([
            r.get("ticker", ""),
            r.get("exchange", ""),
            f"{_status_emoji(yf.get('status', 'fail'))} {yf.get('status', '?')}",
            f"{_status_emoji(stooq.get('status', 'fail'))} {stooq.get('status', '?')}",
            r.get("best_source", "none"),
        ])

    if ticker_rows:
        lines.append("\n### Per-Ticker Coverage")
        lines.append(
            _md_table(
                ["Ticker", "Exchange", "yfinance", "Stooq", "Best Source"],
                ticker_rows,
            )
        )

    return "\n".join(lines)


def _section_dram(data: dict[str, Any] | None) -> str:
    if data is None:
        return "> ⚠️ **memory_quotes_result.json not found** — run `validate_memory_quotes.py` first.\n"

    summary = data.get("summary", {})
    results = data.get("results", [])

    lines = [
        f"**Source:** DRAMeXchange (`{data.get('base_url', '')}`)  ",
        f"**URLs tested:** {summary.get('total_urls')}  ",
        f"**Playwright needed:** {'Yes' if summary.get('playwright_needed') else 'No'}  ",
        "",
        f"> **Recommendation:** `{summary.get('recommendation', 'UNKNOWN')}`  ",
        f"> {summary.get('recommendation_detail', '')}",
        "",
    ]

    url_rows = []
    for r in results:
        parse = r.get("parse") or {}
        url_rows.append([
            r.get("label", ""),
            str(r.get("http_code", "N/A")),
            str(parse.get("tables_found", "N/A")),
            str(parse.get("text_length", "N/A")),
            "Yes" if parse.get("js_render_likely") else "No",
        ])

    if url_rows:
        lines.append(
            _md_table(
                ["Page", "HTTP", "Tables Found", "Text Len", "JS Render?"],
                url_rows,
            )
        )

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Executive summary
# ---------------------------------------------------------------------------


def _exec_summary(all_data: dict[str, Any]) -> str:
    tw = all_data.get("tw_finmind_result.json")
    us = all_data.get("us_stocks_result.json")
    jp = all_data.get("jp_stocks_result.json")
    kr = all_data.get("kr_stocks_result.json")
    dram = all_data.get("memory_quotes_result.json")

    def _coverage(d: dict | None, market: str) -> list[str]:
        if d is None:
            return [market, "N/A", "N/A", "❓ Not run", "N/A"]

        if market == "TW":
            s = d.get("summary", {})
            total = s.get("total", 0)
            success = s.get("success", 0)
            src = "FinMind"
            status = "✅ OK" if s.get("quota_hit") is False and success > 0 else "⚠️ Partial"
            return [market, str(total), str(success), status, src]

        if market == "US":
            s = d.get("summary", {})
            total = s.get("total_tickers", 0)
            cov = s.get("source_coverage", {})
            best = max(cov, key=lambda k: cov[k].get("success", 0)) if cov else "N/A"
            best_cnt = cov.get(best, {}).get("success", 0) if cov else 0
            status = "✅ OK" if best_cnt > 0 else "❌ No data"
            return [market, str(total), str(best_cnt), status, best.capitalize() if cov else "N/A"]

        if market in ("JP", "KR"):
            s = d.get("summary", {})
            total = s.get("total_tickers", 0)
            cov = s.get("source_coverage", {})
            best = max(cov, key=lambda k: cov[k].get("success", 0)) if cov else "N/A"
            best_cnt = cov.get(best, {}).get("success", 0) if cov else 0
            status = "✅ OK" if best_cnt > 0 else "❌ No data"
            return [market, str(total), str(best_cnt), status, best.capitalize() if cov else "N/A"]

        if market == "DRAM":
            s = d.get("summary", {})
            playwright = s.get("playwright_needed", False)
            status = "⚠️ JS Render" if playwright else "✅ Static OK"
            return [market, str(s.get("total_urls", "")), "N/A", status, "Playwright" if playwright else "requests+BS4"]

        return [market, "?", "?", "?", "?"]

    rows = [
        _coverage(tw,   "TW"),
        _coverage(us,   "US"),
        _coverage(jp,   "JP"),
        _coverage(kr,   "KR"),
        _coverage(dram, "DRAM"),
    ]

    return _md_table(
        ["Market", "Tickers", "Best Coverage", "Status", "Recommended Source"],
        rows,
    )


# ---------------------------------------------------------------------------
# Main report generator
# ---------------------------------------------------------------------------


def build_report(all_data: dict[str, Any]) -> str:
    """Build the full Markdown report string.

    Args:
        all_data: Dict mapping filename -> parsed JSON (or None).

    Returns:
        Complete Markdown document as a string.
    """
    today = date.today().isoformat()

    sections = [
        f"# IC MemTrend Dashboard — Phase 0 Data Source Validation Report",
        f"",
        f"**Generated:** {today}  ",
        f"**Phase:** 0 — Data source feasibility validation  ",
        f"**Purpose:** Determine which data sources provide reliable price history",
        f"for memory/semiconductor stocks across TW, US, JP, KR markets.",
        f"",
        f"---",
        f"",
        f"## Executive Summary",
        f"",
        _exec_summary(all_data),
        f"",
        f"---",
        f"",
        f"## Taiwan (TW) — FinMind",
        f"",
        _section_tw(all_data.get("tw_finmind_result.json")),
        f"",
        f"---",
        f"",
        f"## United States (US) — FinMind / Stooq / Alpha Vantage",
        f"",
        _section_us(all_data.get("us_stocks_result.json")),
        f"",
        f"---",
        f"",
        f"## Japan (JP) — Stooq / yfinance",
        f"",
        _section_jp(all_data.get("jp_stocks_result.json")),
        f"",
        f"---",
        f"",
        f"## Korea (KR) — yfinance / Stooq",
        f"",
        _section_kr(all_data.get("kr_stocks_result.json")),
        f"",
        f"---",
        f"",
        f"## DRAMeXchange Memory Price Quotes",
        f"",
        _section_dram(all_data.get("memory_quotes_result.json")),
        f"",
        f"---",
        f"",
        f"## Source Recommendation Matrix",
        f"",
        _md_table(
            ["Market", "Primary Source", "Fallback", "Notes"],
            [
                ["TW",   "FinMind (`TaiwanStockPrice`)", "—",          "Free token required; 39 tickers tested"],
                ["US",   "Stooq (CSV)",                  "Alpha Vantage", "No key for Stooq; AV free=25 req/day"],
                ["JP",   "Stooq (`.jp`)",                "yfinance",   "Kioxia (285A) IPO Dec 2024; limited history"],
                ["KR",   "yfinance (`.KS`/`.KQ`)",       "Stooq (`.kr`)", "Stooq KR partial; KOSDAQ often missing"],
                ["DRAM", "Playwright + BS4",              "Manual CSV", "JS rendering required for DRAMeXchange"],
            ],
        ),
        f"",
        f"---",
        f"",
        f"## Action Items",
        f"",
        "- [ ] **TW**: Register free FinMind account and set `FINMIND_TOKEN` in `.env`",
        "- [ ] **US**: Obtain free Alpha Vantage key (`ALPHAVANTAGE_KEY`) as FinMind fallback",
        "- [ ] **JP**: Verify Kioxia (285A.T) coverage once 1+ year of history is available",
        "- [ ] **KR**: Cross-validate yfinance data against KRX official data for top 3 tickers",
        "- [ ] **DRAM**: Implement Playwright scraper if static HTML proves insufficient",
        "- [ ] **All**: Set up daily cron to refresh quotes; handle market holidays per exchange",
        "- [ ] **DB**: Design `price_history` table with `(ticker, market, date)` composite PK",
        f"",
        f"---",
        f"",
        f"*Report auto-generated by `scripts/phase0_validation/generate_report.py`*",
        f"",
    ]

    return "\n".join(sections)


def main() -> None:
    """Load all results and write the consolidated Markdown report."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    all_data = load_results()

    missing = [f for f, d in all_data.items() if d is None]
    if missing:
        logger.warning(
            "%d result file(s) missing — report will have placeholders: %s",
            len(missing),
            missing,
        )

    report_md = build_report(all_data)
    OUT_FILE.write_text(report_md, encoding="utf-8")
    logger.info("Report written to %s", OUT_FILE)


if __name__ == "__main__":
    main()
