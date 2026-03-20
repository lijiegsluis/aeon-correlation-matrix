# Aeon Correlation Matrix

**Cross-Asset Correlation · Macro Regime Classifier · Regime-Driven Allocation Framework**

*LiJie Guo · Aeon Nimbus Research · lijieguo.substack.com · [LinkedIn](https://www.linkedin.com/in/lijieguo-es/)*

---

## Overview

True diversification — the kind that survives a risk-off event rather than failing at exactly the moment it is needed — requires a structural understanding of how assets co-move across regimes, not just in tranquil markets. This tool provides two capabilities that together address that problem. The first is a cross-asset correlation matrix covering eight major asset classes, annotated with the economic logic behind each structural relationship. The second is a macro regime classifier that takes six observable indicators as inputs, identifies the current economic regime from a taxonomy of seven states, and outputs the historically optimal allocation framework for that regime. Both are implemented without external dependencies.

```bash
python main.py
```

Python 3.8 or later. No external dependencies.

---

## Modules

| Module | Function |
|--------|----------|
| Correlation Matrix | 8×8 cross-asset Pearson correlation matrix with rolling 3-year estimates and interpretive annotations |
| Macro Regime Classifier | Input six macro indicators → regime identification → model allocation with rationale |

---

## Methodology

### Cross-Asset Correlation

The Pearson correlation coefficient quantifies the linear co-movement between two return series. For assets X and Y:

```
ρ(X,Y) = Cov(X,Y) / (σ_X · σ_Y)     ρ ∈ [−1, +1]
```

A coefficient of +1 implies perfect co-movement and zero diversification benefit; 0 implies orthogonal returns, the theoretical ideal for diversification; −1 implies a perfect inverse relationship, the maximum hedge. The matrix here uses rolling three-year estimates from liquid cross-asset returns — a window long enough to smooth short-term noise but short enough to capture structural regime shifts.

The key structural relationships and their economic interpretations:

| Pair | ρ (approx.) | Mechanism |
|------|-------------|-----------|
| SPX / VIX | −0.85 | VIX is a measure of implied equity volatility — it spikes precisely when equities fall, making it the most direct hedge of equity tail risk |
| SPX / EM Equity | +0.82 | Emerging market equities are high-beta expressions of global risk appetite; they amplify the directionality of US equities |
| US 10Y / HY Credit | +0.62 | Both are rate-sensitive instruments; rising yields compress both Treasury prices and credit spreads compress as economy strengthens |
| Gold / DXY | −0.60 | Gold is priced in dollars; dollar appreciation mechanically reduces gold's value in local currency terms |
| SPX / US10Y | −0.42 | The classical flight-to-quality relationship — in equity drawdowns, capital rotates to government bonds, supporting their price |

### Correlation Breakdown Under Stress

The critical insight that distinguishes portfolio risk management from simple diversification: in acute risk-off events, correlations between risky assets converge toward 1.0. The diversification within the equity allocation — US, emerging markets, sectors, factors — provides no protection precisely when protection is needed most. This is the correlation contagion phenomenon observed in every major drawdown from 1987 to 2020.

Genuine hedging requires structural negative correlation to equities: US Treasuries (flight-to-quality), gold (real asset, fear bid), and volatility instruments (VIX products). The 60/40 equity/bond portfolio functions well in this regard under most conditions — but breaks down in stagflationary environments where both asset classes face simultaneous headwinds. 2022 was the starkest illustration: a year in which both equities and bonds generated deeply negative returns, producing the worst 60/40 outcome since the 1930s, driven by the Fed's rate hiking cycle forcing simultaneous repricing of both duration and equity risk premium.

### Macro Regime Classification

The classifier uses six observable macro indicators to diagnose the current economic regime:

| Indicator | Interpretation |
|-----------|----------------|
| 2s10s yield curve spread | Inversion is a historically reliable leading indicator of recession, typically with a 12–18 month lag |
| US 10-year yield level | Elevated yields reflect restrictive policy and compress equity multiples through the discount rate channel |
| VIX | Above 20 signals risk-off positioning; above 28 historically marks crisis or acute dislocations |
| ISM Manufacturing PMI | Below 50 indicates manufacturing contraction; trend and breadth matter as much as the level |
| Core CPI year-over-year | Above 3.5% combined with sub-50 ISM defines the stagflationary quadrant — the most difficult regime for traditional portfolios |
| Unemployment rate | Rising unemployment signals late-cycle deceleration and increases recession probability |

**Regime taxonomy and derived allocations:**

| Regime | Equities | Fixed Income | Gold | Commodities | Cash |
|--------|----------|--------------|------|-------------|------|
| Stagflationary Risk-Off | 30% | 18% | 28% | 18% | 6% |
| Stagflation | 40% | 16% | 24% | 14% | 6% |
| Risk-Off / Recession | 38% | 38% | 16% | 3% | 5% |
| Late-Cycle Deceleration | 50% | 30% | 13% | 3% | 4% |
| Mid-Cycle Expansion | 62% | 22% | 10% | 4% | 2% |
| Early Recovery | 65% | 18% | 10% | 5% | 2% |
| Early Cycle Expansion | 72% | 13% | 8% | 5% | 2% |

These allocations encode the historical empirical performance of asset classes through the economic cycle. Equities dominate in early and mid-cycle expansion, when growth is accelerating, policy is accommodative, and earnings revisions are positive. Fixed income moves to parity with equities in recession as rates fall and duration is rewarded. Commodities and gold absorb capital in stagflationary regimes where neither bonds nor equities offer real returns.

---

## Why This Matters

The portfolio variance formula reveals why correlation is foundational rather than supplementary to risk management:

```
σ²_p = Σᵢ Σⱼ wᵢ wⱼ ρᵢⱼ σᵢ σⱼ
```

In a high-correlation portfolio, the cross-terms dominate and the portfolio variance approaches the weighted average of individual asset variances — diversification provides no meaningful reduction. Understanding the correlation structure is therefore not an optional analytical layer; it is the determinant of whether a diversification strategy actually diversifies.

The regime framework adds a temporal dimension to this structural analysis. Correlations are not stationary — they shift materially across economic cycles. A PM who understands that VIX above 28, an inverted yield curve, and sub-48 ISM together define a recession onset regime will position defensively in bonds and gold regardless of individual security conviction, because the macro backdrop dominates asset class returns in such environments. This is not market timing in the pejorative sense; it is the strategic allocation framework within which tactical stock selection operates.

The asymmetry of 2022 — simultaneous drawdowns in both equities and bonds — illustrates that even the most robust structural correlations (the equity/bond negative correlation) are regime-conditional. Risk management that ignores this is fragile by construction.

---

## Example Output

```
════════════════════════════════════════════════════════════════
  CROSS-ASSET CORRELATION MATRIX  (Rolling 3-year estimates)
════════════════════════════════════════════════════════════════

              SPX    US10Y   Gold   WTI    DXY    EM Eq  HY Cr  VIX
  SPX       [1.00]  -0.42   0.08   0.55  -0.48   0.82  -0.21  -0.85
  US10Y     -0.42  [1.00]   0.28  -0.38   0.12  -0.31   0.62   0.40
  Gold       0.08   0.28  [1.00]   0.18  -0.60   0.12   0.14   0.05
  WTI Oil    0.55  -0.38   0.18  [1.00]  -0.31   0.44  -0.18  -0.48
  DXY       -0.48   0.12  -0.60  -0.31  [1.00]  -0.55  -0.12   0.44
  EM Equity  0.82  -0.31   0.12   0.44  -0.55  [1.00]  -0.18  -0.78
  HY Credit -0.21   0.62   0.14  -0.18  -0.12  -0.18  [1.00]   0.22
  VIX       -0.85   0.40   0.05  -0.48   0.44  -0.78   0.22  [1.00]

════════════════════════════════════════════════════════════════
  MACRO REGIME CLASSIFIER
════════════════════════════════════════════════════════════════
  2s10s: −18bp | 10Y: 4.69% | VIX: 21.7 | ISM: 48.4 | CPI: 3.1% | UE: 4.2%

  Regime identified: Late-Cycle Deceleration

  Signal interpretation:
  → Inverted curve (−18bp): late-cycle / pre-recession signal
  → ISM below 50 (48.4): manufacturing contraction in progress
  → VIX elevated (21.7): risk-off positioning warranted
  → Sticky inflation (3.1%): limits the pace and depth of policy easing

  Model Allocation:
  Equities      ████████████████████████████████████████████████ 50%
  Fixed Income  ██████████████████████████████ 30%
  Gold          ████████████ 13%
  Commodities   ███ 3%
  Cash          ████ 4%
```

---

*LiJie Guo · Aeon Nimbus Research · lijieguo.substack.com · [LinkedIn](https://www.linkedin.com/in/lijieguo-es/)*
