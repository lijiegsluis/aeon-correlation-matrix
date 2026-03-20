"""
Cross-Asset Correlation & Macro Regime Classifier
==================================================
Aeon Nimbus Research
Uses Python standard library only (math, statistics).
"""

import math
import statistics


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

ASSETS = ["SPX", "US10Y", "Gold", "WTI Oil", "DXY", "EM Equity", "HY Credit", "VIX"]

CORR_MATRIX = [
    [ 1.00, -0.42,  0.08,  0.55, -0.48,  0.82, -0.21, -0.85],
    [-0.42,  1.00,  0.28, -0.38,  0.12, -0.31,  0.62,  0.40],
    [ 0.08,  0.28,  1.00,  0.18, -0.60,  0.12,  0.14,  0.05],
    [ 0.55, -0.38,  0.18,  1.00, -0.31,  0.44, -0.18, -0.48],
    [-0.48,  0.12, -0.60, -0.31,  1.00, -0.55, -0.12,  0.44],
    [ 0.82, -0.31,  0.12,  0.44, -0.55,  1.00, -0.18, -0.78],
    [-0.21,  0.62,  0.14, -0.18, -0.12, -0.18,  1.00,  0.22],
    [-0.85,  0.40,  0.05, -0.48,  0.44, -0.78,  0.22,  1.00],
]

REGIMES = [
    {
        "name": "Stagflationary Risk-Off",
        "description": (
            "The worst macro environment: growth contracting while inflation remains "
            "elevated and markets in stress. Historical parallels: 1973-74, 2022 peak."
        ),
        "condition": lambda d: d["cpi"] > 3.5 and d["ism"] < 50 and d["vix"] > 28,
        "signals": [
            ("CPI > 3.5%", lambda d: d["cpi"] > 3.5),
            ("ISM < 50 (contraction)", lambda d: d["ism"] < 50),
            ("VIX > 28 (market stress)", lambda d: d["vix"] > 28),
        ],
        "alloc": {
            "Equities":    30,
            "Fixed Income": 18,
            "Gold":        28,
            "Commodities": 18,
            "Cash":         6,
        },
    },
    {
        "name": "Stagflation",
        "description": (
            "Growth is contracting while inflation stays high — the classic policy "
            "dilemma. Central banks cannot cut without re-igniting inflation. "
            "Historical parallels: 1970s oil shocks, 2021-22."
        ),
        "condition": lambda d: d["cpi"] > 3.5 and d["ism"] < 50,
        "signals": [
            ("CPI > 3.5% (elevated inflation)", lambda d: d["cpi"] > 3.5),
            ("ISM < 50 (manufacturing contraction)", lambda d: d["ism"] < 50),
        ],
        "alloc": {
            "Equities":    40,
            "Fixed Income": 16,
            "Gold":        24,
            "Commodities": 14,
            "Cash":         6,
        },
    },
    {
        "name": "Risk-Off / Recession",
        "description": (
            "Markets pricing acute risk: either VIX spiking above 28 or the yield "
            "curve deeply inverted (spread < -30bp). Flight-to-quality dynamics dominate. "
            "Historical parallels: 2008-09 GFC, 2020 COVID crash."
        ),
        "condition": lambda d: d["vix"] > 28 or d["spread"] < -30,
        "signals": [
            ("VIX > 28 (acute market stress)", lambda d: d["vix"] > 28),
            ("2s10s < -30bp (deep inversion)", lambda d: d["spread"] < -30),
        ],
        "alloc": {
            "Equities":    38,
            "Fixed Income": 38,
            "Gold":        16,
            "Commodities":  3,
            "Cash":         5,
        },
    },
    {
        "name": "Late-Cycle Deceleration",
        "description": (
            "The expansion is exhausted: the curve has inverted, manufacturing is "
            "contracting, and the labour market has begun to soften. A recession is "
            "the base case within 6-18 months. Historical parallels: 2000, 2006-07, 2019."
        ),
        "condition": lambda d: d["spread"] < 0 and d["ism"] < 50 and d["unemp"] > 4,
        "signals": [
            ("2s10s < 0 (inverted curve)", lambda d: d["spread"] < 0),
            ("ISM < 50 (manufacturing contraction)", lambda d: d["ism"] < 50),
            ("Unemployment > 4%", lambda d: d["unemp"] > 4),
        ],
        "alloc": {
            "Equities":    50,
            "Fixed Income": 30,
            "Gold":        13,
            "Commodities":  3,
            "Cash":         4,
        },
    },
    {
        "name": "Early Recovery",
        "description": (
            "The recession trough has passed: the curve is re-steepening, ISM turning "
            "up through 50, but slack in the labour market remains. Risk assets typically "
            "stage their strongest absolute returns in this phase. Historical parallels: "
            "2009 H2, 2020 Q3-Q4."
        ),
        "condition": lambda d: d["spread"] > 20 and d["ism"] > 50 and d["unemp"] > 4.5,
        "signals": [
            ("2s10s > 20bp (steepening)", lambda d: d["spread"] > 20),
            ("ISM > 50 (expansion)", lambda d: d["ism"] > 50),
            ("Unemployment > 4.5% (labour slack)", lambda d: d["unemp"] > 4.5),
        ],
        "alloc": {
            "Equities":    65,
            "Fixed Income": 18,
            "Gold":        10,
            "Commodities":  5,
            "Cash":         2,
        },
    },
    {
        "name": "Early Cycle Expansion",
        "description": (
            "Broad-based growth acceleration with a healthy curve and tight labour "
            "market. Historically the sweet spot for risk assets with low drawdown "
            "risk. Historical parallels: 2003-04, 2010-11, 2017."
        ),
        "condition": lambda d: d["spread"] > 50 and d["ism"] > 53 and d["unemp"] < 4,
        "signals": [
            ("2s10s > 50bp (steep curve)", lambda d: d["spread"] > 50),
            ("ISM > 53 (robust expansion)", lambda d: d["ism"] > 53),
            ("Unemployment < 4% (tight labour market)", lambda d: d["unemp"] < 4),
        ],
        "alloc": {
            "Equities":    72,
            "Fixed Income": 13,
            "Gold":         8,
            "Commodities":  5,
            "Cash":         2,
        },
    },
    {
        "name": "Mid-Cycle Expansion",
        "description": (
            "No dominant macro stress signal. The expansion is intact but unexceptional. "
            "A balanced allocation reflects moderate risk appetite. Historical parallels: "
            "2004-05, 2013-14, 2018 mid-year."
        ),
        "condition": lambda d: True,
        "signals": [],
        "alloc": {
            "Equities":    62,
            "Fixed Income": 22,
            "Gold":        10,
            "Commodities":  4,
            "Cash":         2,
        },
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def corr_symbol(r: float) -> str:
    """Return a strength symbol for a Pearson correlation value."""
    if r >= 0.999:
        return "  1  "
    elif r > 0.6:
        return " +++ "
    elif r >= 0.3:
        return "  ++ "
    elif r >= 0:
        return "   + "
    elif r >= -0.3:
        return "   - "
    elif r >= -0.6:
        return "  -- "
    else:
        return " --- "


def bar_chart(value: float, max_width: int = 40) -> str:
    """Return an ASCII bar proportional to value (assumed 0-100)."""
    filled = round(value / 100 * max_width)
    return "[" + "#" * filled + " " * (max_width - filled) + "]"


def separator(char: str = "-", width: int = 78) -> str:
    return char * width


def section_header(title: str, width: int = 78) -> str:
    pad = (width - len(title) - 2) // 2
    return "\n" + "=" * width + "\n" + " " * pad + title + "\n" + "=" * width


def prompt_float(prompt: str, default: float) -> float:
    raw = input(f"  {prompt} [default {default}]: ").strip()
    if raw == "":
        return default
    try:
        return float(raw)
    except ValueError:
        print(f"  Invalid input — using default {default}")
        return default


# ---------------------------------------------------------------------------
# Module 1: Cross-Asset Correlation Matrix
# ---------------------------------------------------------------------------

def run_correlation_matrix() -> None:
    print(section_header("MODULE 1 — CROSS-ASSET CORRELATION MATRIX"))
    print()
    print("  Rolling 3-Year Estimates (hardcoded research values)")
    print("  Period reference: approx. 2021-2024 multi-regime window")
    print()

    # Column width allocations
    label_w = 10   # row label
    cell_w  = 14   # each cell: symbol (5) + value (6) + padding

    # Header row
    header = " " * label_w
    for asset in ASSETS:
        short = asset[:7]
        header += short.center(cell_w)
    print(header)
    print(separator("-", label_w + cell_w * len(ASSETS)))

    for i, row_asset in enumerate(ASSETS):
        line = row_asset[:label_w].ljust(label_w)
        for j, _ in enumerate(ASSETS):
            r = CORR_MATRIX[i][j]
            sym = corr_symbol(r)
            if i == j:
                cell = "  diag ".center(cell_w)
            else:
                val_str = f"{r:+.2f}"
                cell = f"{sym}{val_str}".center(cell_w)
            line += cell
        print(line)

    print(separator("-", label_w + cell_w * len(ASSETS)))

    # Legend
    print()
    print("  LEGEND")
    print("  +++  correlation > +0.60  (risk concentration — assets move together)")
    print("  ++   correlation +0.30 to +0.60")
    print("  +    correlation  0.00 to +0.30  (mild positive co-movement)")
    print("  -    correlation  0.00 to -0.30  (mild negative co-movement)")
    print("  --   correlation -0.30 to -0.60")
    print("  ---  correlation < -0.60  (genuine diversification)")
    print()

    # Interpretive commentary
    print(separator("="))
    print("  INTERPRETIVE COMMENTARY")
    print(separator("-"))

    commentary = [
        ("SPX vs VIX (-0.85, +++---):",
         "The strongest and most reliable pair in the matrix. VIX is structurally "
         "short volatility relative to equities — when equity prices fall, implied "
         "volatility explodes. A -0.85 correlation means VIX is approximately an "
         "85% mirror of SPX daily moves. Long VIX (via options) is the canonical "
         "equity tail hedge."),

        ("SPX vs EM Equity (+0.82, +++):",
         "Emerging market equities behave as a high-beta version of U.S. equities. "
         "A 0.82 correlation means EM adds very little diversification in a global "
         "risk-off event — EM sells off harder and faster than SPX. True "
         "geographic diversification requires genuine macro independence, not just "
         "different country labels."),

        ("Gold vs DXY (-0.60, ---):",
         "Gold is priced in U.S. dollars, so a stronger dollar mechanically "
         "pressures gold in foreign currency terms, reducing global demand. This "
         "is one of the most structurally stable pairs in macro — DXY strength "
         "during risk-off events is a key headwind for gold even as the metal "
         "benefits from flight-to-quality flows."),

        ("US10Y vs HY Credit (+0.62, +++):",
         "Counterintuitive at first: when Treasury yields fall (price rises), HY "
         "credit spreads tighten and HY total returns rise. Both benefit from "
         "falling rates environments. However this correlation breaks sharply "
         "during credit stress events, when HY spreads blow out while Treasuries "
         "rally as a safe haven."),

        ("SPX vs WTI Oil (+0.55, ++):",
         "A moderate positive correlation reflecting the pro-growth linkage: "
         "economic expansion drives both corporate earnings (SPX) and energy "
         "demand (WTI). This correlation has been unstable historically — supply "
         "shocks (e.g., 1973, 2022) can cause oil to spike while equities fall."),

        ("US10Y as flight-to-quality (-0.42 vs SPX):",
         "The classic 60/40 rationale: bonds partially offset equity drawdowns. "
         "A -0.42 correlation is meaningful but not perfect. Critically, this "
         "correlation turned positive in 2022 when inflation forced both assets "
         "down simultaneously — the clearest recent evidence that the stock-bond "
         "hedge is regime-dependent, not structural."),

        ("EM Equity vs DXY (-0.55, --):",
         "Dollar strength is a direct headwind for EM: it raises the cost of "
         "USD-denominated EM debt servicing, tightens EM financial conditions, "
         "and typically coincides with capital outflows from EM. A strong dollar "
         "environment is structurally bearish for EM as an asset class."),
    ]

    for title, body in commentary:
        print(f"\n  {title}")
        # Wrap body to ~72 chars
        words = body.split()
        line = "    "
        for word in words:
            if len(line) + len(word) + 1 > 76:
                print(line)
                line = "    " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)

    print()


# ---------------------------------------------------------------------------
# Module 2: Macro Regime Classifier
# ---------------------------------------------------------------------------

def run_regime_classifier() -> None:
    print(section_header("MODULE 2 — MACRO REGIME CLASSIFIER"))
    print()
    print("  Enter current macro indicators.")
    print("  Press ENTER to accept the default value shown in brackets.")
    print()

    data = {
        "spread": prompt_float("2s10s Yield Curve Spread (basis points, e.g. -18 means inverted)", -18.0),
        "y10":    prompt_float("US 10Y Yield (%)",                                                  4.69),
        "vix":    prompt_float("VIX Level",                                                        21.7),
        "ism":    prompt_float("ISM Manufacturing PMI",                                            48.4),
        "cpi":    prompt_float("Core CPI YoY (%)",                                                  3.1),
        "unemp":  prompt_float("Unemployment Rate (%)",                                             4.2),
    }

    print()
    print(separator("="))
    print("  INPUT SUMMARY")
    print(separator("-"))
    curve_label = "INVERTED" if data["spread"] < 0 else "NORMAL"
    print(f"  2s10s Spread:    {data['spread']:+.1f} bp  ({curve_label})")
    print(f"  US 10Y Yield:    {data['y10']:.2f}%")
    print(f"  VIX:             {data['vix']:.1f}  ({'ELEVATED' if data['vix'] > 25 else 'MODERATE' if data['vix'] > 18 else 'LOW'})")
    print(f"  ISM Mfg PMI:     {data['ism']:.1f}  ({'EXPANSION' if data['ism'] >= 50 else 'CONTRACTION'})")
    print(f"  Core CPI YoY:    {data['cpi']:.1f}%")
    print(f"  Unemployment:    {data['unemp']:.1f}%")
    print()

    # Classify
    matched = None
    for regime in REGIMES:
        if regime["condition"](data):
            matched = regime
            break

    print(separator("="))
    print(f"  REGIME CLASSIFICATION:  {matched['name'].upper()}")
    print(separator("="))
    print()

    # Wrap description
    words = matched["description"].split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 76:
            print(line)
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(line)
    print()

    # Active signals
    print(separator("-"))
    print("  ACTIVE SIGNALS")
    print(separator("-"))
    active_signals = [label for label, fn in matched["signals"] if fn(data)]
    if active_signals:
        for sig in active_signals:
            print(f"  [TRIGGERED]  {sig}")
    else:
        print("  No specific trigger signals — Mid-Cycle default applies.")
    print()

    # Additional macro context
    print(separator("-"))
    print("  MACRO CONTEXT NOTES")
    print(separator("-"))
    notes = []

    if data["spread"] < -50:
        notes.append("Deep inversion (< -50bp): historically precedes recession by 12-18 months with high reliability.")
    elif data["spread"] < 0:
        notes.append("Curve inverted: yield curve inversion has preceded every U.S. recession since 1970.")
    elif data["spread"] > 100:
        notes.append("Steep curve (> 100bp): typical of early recovery or policy accommodation phase.")

    if data["vix"] > 35:
        notes.append("VIX above 35: acute fear regime. Historically a buying opportunity on a 12-month horizon.")
    elif data["vix"] > 25:
        notes.append("VIX elevated (25-35): market pricing meaningful tail risk. Defensiveness warranted.")
    elif data["vix"] < 14:
        notes.append("VIX below 14: complacency zone. Historically associated with late-cycle and drawdown risk.")

    if data["cpi"] > 4.0:
        notes.append("CPI above 4%: Federal Reserve policy likely restrictive, compressing equity multiples.")
    elif data["cpi"] < 2.0:
        notes.append("CPI below 2%: disinflationary — central bank has room to cut; positive for duration.")

    if data["ism"] < 45:
        notes.append("ISM below 45: severe manufacturing contraction — recessionary signal, not merely soft patch.")
    elif data["ism"] > 57:
        notes.append("ISM above 57: robust expansion — capacity pressures building, watch for inflation re-acceleration.")

    if data["unemp"] > 5.5:
        notes.append("Unemployment above 5.5%: substantial labour market slack — early cycle conditions.")
    elif data["unemp"] < 3.5:
        notes.append("Unemployment below 3.5%: very tight labour market — wage inflation risk, late-cycle signal.")

    if not notes:
        notes.append("Indicators within normal mid-cycle ranges. No extreme readings to flag.")

    for note in notes:
        words = note.split()
        line = "  > "
        for word in words:
            if len(line) + len(word) + 1 > 76:
                print(line)
                line = "    " + word + " "
            else:
                line += word + " "
        if line.strip():
            print(line)
        print()

    # Allocation
    print(separator("="))
    print(f"  MODEL-DERIVED ALLOCATION — {matched['name'].upper()}")
    print(separator("-"))
    alloc = matched["alloc"]
    max_label = max(len(k) for k in alloc)
    for asset, pct in alloc.items():
        label = asset.ljust(max_label)
        bar = bar_chart(pct, max_width=36)
        print(f"  {label}  {bar}  {pct:5.1f}%")
    print()
    total = sum(alloc.values())
    print(f"  {'TOTAL'.ljust(max_label)}  {'':38}  {total:5.1f}%")
    print()
    print(separator("-"))
    print("  NOTE: These allocations are regime-based model outputs for")
    print("  educational and research purposes only. They are not investment")
    print("  advice. Always apply your own risk tolerance, constraints, and")
    print("  investment horizon before making any allocation decision.")
    print()


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def main() -> None:
    print()
    print("=" * 78)
    print("  AEON NIMBUS RESEARCH".center(78))
    print("  Cross-Asset Correlation & Macro Regime Classifier".center(78))
    print("  Python Standard Library Only — No External Dependencies".center(78))
    print("=" * 78)
    print()

    while True:
        print("  Select a module:")
        print("    [1]  Cross-Asset Correlation Matrix")
        print("    [2]  Macro Regime Classifier")
        print("    [3]  Run Both")
        print("    [q]  Quit")
        print()
        choice = input("  Enter choice: ").strip().lower()
        print()

        if choice == "1":
            run_correlation_matrix()
        elif choice == "2":
            run_regime_classifier()
        elif choice == "3":
            run_correlation_matrix()
            run_regime_classifier()
        elif choice in ("q", "quit", "exit"):
            print("  Exiting. Aeon Nimbus Research.")
            print()
            break
        else:
            print("  Unrecognised input. Please enter 1, 2, 3, or q.")
            print()

        print()
        again = input("  Return to menu? [Y/n]: ").strip().lower()
        print()
        if again in ("n", "no"):
            print("  Exiting. Aeon Nimbus Research.")
            print()
            break


if __name__ == "__main__":
    main()
