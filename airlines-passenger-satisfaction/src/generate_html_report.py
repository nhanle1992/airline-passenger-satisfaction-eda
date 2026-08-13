"""Generate a self-contained HTML report with embedded analysis charts."""

from __future__ import annotations

import base64
import io
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/processed/airline_passenger_satisfaction_cleaned.csv"
OUTPUT = ROOT / "reports/airline_passenger_satisfaction_report.html"

NAVY = "#132238"
TEAL = "#0B7A75"
CORAL = "#E76F51"
GOLD = "#E9B949"
PALE = "#E8F2F1"
INK = "#263442"
MUTED = "#64748B"


def image_data(fig: plt.Figure) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def chart_satisfaction(df: pd.DataFrame) -> str:
    rates = df["satisfaction"].value_counts().reindex(["Satisfied", "Neutral or Dissatisfied"])
    fig, ax = plt.subplots(figsize=(8, 4.4))
    bars = ax.bar(["Satisfied", "Neutral / dissatisfied"], rates.values, color=[TEAL, CORAL], width=.62)
    ax.set_title("Overall satisfaction remains below half", loc="left", fontsize=15, color=NAVY, fontweight="bold")
    ax.set_ylabel("Passengers")
    ax.spines[["top", "right", "left"]].set_visible(False)
    ax.grid(axis="y", alpha=.18)
    for bar, value in zip(bars, rates.values):
        ax.text(bar.get_x()+bar.get_width()/2, value+1400, f"{value:,}\n{value/len(df):.1%}", ha="center", fontweight="bold", color=INK)
    ax.set_ylim(0, rates.max()*1.18)
    return image_data(fig)


def chart_service_rates(df: pd.DataFrame) -> str:
    mapping = {
        "cleanliness_rating_clean": "Cleanliness",
        "seat_comfort_rating_clean": "Seat comfort",
        "onboard_service_rating_clean": "Onboard service",
    }
    fig, ax = plt.subplots(figsize=(8.5, 5))
    colors = [TEAL, GOLD, CORAL]
    for (column, label), color in zip(mapping.items(), colors):
        rates = df.dropna(subset=[column]).groupby(column)["is_satisfied"].mean().reindex([1, 2, 3, 4, 5])
        ax.plot(rates.index, rates.values*100, marker="o", linewidth=2.7, markersize=6, label=label, color=color)
    ax.set_title("Higher service ratings align with higher satisfaction", loc="left", fontsize=15, color=NAVY, fontweight="bold")
    ax.set_xlabel("Service rating")
    ax.set_ylabel("Satisfied passengers (%)")
    ax.set_xticks([1, 2, 3, 4, 5])
    ax.set_ylim(0, 75)
    ax.grid(alpha=.18)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, ncol=3, loc="upper left")
    return image_data(fig)


def chart_service_means(df: pd.DataFrame) -> str:
    labels = {
        "inflight_wifi_rating_clean": "Inflight Wi-Fi",
        "online_booking_rating_clean": "Online booking",
        "gate_location_rating_clean": "Gate location",
        "food_drink_rating_clean": "Food & drink",
        "cleanliness_rating_clean": "Cleanliness",
        "onboard_service_rating_clean": "Onboard service",
        "seat_comfort_rating_clean": "Seat comfort",
        "baggage_handling_rating_clean": "Baggage handling",
        "inflight_service_rating_clean": "Inflight service",
    }
    means = df[list(labels)].mean().rename(index=labels).sort_values()
    colors = [CORAL if x < 3 else TEAL if x >= 3.4 else GOLD for x in means]
    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    bars = ax.barh(means.index, means.values, color=colors)
    ax.set_title("Digital touchpoints trail operational service", loc="left", fontsize=15, color=NAVY, fontweight="bold")
    ax.set_xlabel("Mean clean rating (1–5)")
    ax.set_xlim(0, 5)
    ax.axvline(3, color=MUTED, linewidth=1, linestyle="--")
    ax.grid(axis="x", alpha=.15)
    ax.spines[["top", "right", "left"]].set_visible(False)
    for bar, value in zip(bars, means.values):
        ax.text(value+.06, bar.get_y()+bar.get_height()/2, f"{value:.2f}", va="center", color=INK, fontsize=9)
    return image_data(fig)


def chart_class(df: pd.DataFrame) -> str:
    order = ["Business", "Economy Plus", "Economy"]
    raw = df.groupby("travel_class")["is_satisfied"].mean().reindex(order)*100
    adjusted = pd.Series({"Business":54.4, "Economy Plus":28.4, "Economy":30.9}).reindex(order)
    x = np.arange(len(order)); width=.34
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    b1=ax.bar(x-width/2, raw.values, width, label="Observed", color=TEAL)
    b2=ax.bar(x+width/2, adjusted.values, width, label="Adjusted", color=GOLD)
    ax.set_title("Business class leads before and after adjustment", loc="left", fontsize=15, color=NAVY, fontweight="bold")
    ax.set_ylabel("Satisfied passengers (%)"); ax.set_xticks(x, order); ax.set_ylim(0,80)
    ax.spines[["top","right","left"]].set_visible(False); ax.grid(axis="y",alpha=.17); ax.legend(frameon=False)
    for bars in [b1,b2]:
        for bar in bars: ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+1.5,f"{bar.get_height():.1f}%",ha="center",fontsize=9,fontweight="bold")
    return image_data(fig)


def chart_delays(df: pd.DataFrame) -> str:
    dep_order=["No delay","Short (1-15)","Moderate (16-60)","Long (>60)"]
    arr_order=dep_order
    dep=df.groupby("departure_delay_band")["is_satisfied"].mean().reindex(dep_order)*100
    arr=df[df.arrival_delay_band!="Missing"].groupby("arrival_delay_band")["is_satisfied"].mean().reindex(arr_order)*100
    x=np.arange(4)
    fig,ax=plt.subplots(figsize=(8.5,4.9))
    ax.plot(x,dep.values,marker="o",linewidth=2.8,label="Departure delay",color=TEAL)
    ax.plot(x,arr.values,marker="o",linewidth=2.8,label="Arrival delay",color=CORAL)
    ax.set_title("Satisfaction weakens as disruption grows",loc="left",fontsize=15,color=NAVY,fontweight="bold")
    ax.set_ylabel("Satisfied passengers (%)"); ax.set_xticks(x,["None","1–15","16–60",">60"]); ax.set_xlabel("Delay band (dataset units)"); ax.set_ylim(25,52)
    ax.spines[["top","right"]].set_visible(False);ax.grid(alpha=.18);ax.legend(frameon=False)
    for series,color in [(dep,TEAL),(arr,CORAL)]:
        for xi,v in zip(x,series.values):ax.text(xi,v+1,f"{v:.1f}%",ha="center",fontsize=8,color=color,fontweight="bold")
    return image_data(fig)


def chart_context(df: pd.DataFrame) -> str:
    table=df.groupby(["travel_class","travel_type"])["is_satisfied"].mean().mul(100).unstack().reindex(["Business","Economy Plus","Economy"])
    fig,ax=plt.subplots(figsize=(8.2,4.8))
    sns.heatmap(table,annot=True,fmt=".1f",cmap=sns.light_palette(TEAL,as_cmap=True),vmin=0,vmax=80,cbar_kws={"label":"Satisfaction rate (%)"},ax=ax)
    ax.set_title("Travel purpose reshapes the class story",loc="left",fontsize=15,color=NAVY,fontweight="bold")
    ax.set_xlabel("Travel purpose");ax.set_ylabel("Travel class")
    return image_data(fig)


def main() -> None:
    df = pd.read_csv(DATA)
    charts = {
        "satisfaction": chart_satisfaction(df),
        "service_rates": chart_service_rates(df),
        "service_means": chart_service_means(df),
        "class": chart_class(df),
        "delays": chart_delays(df),
        "context": chart_context(df),
    }
    html = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="Airline passenger satisfaction analysis of 129,880 survey records.">
<title>Airline Passenger Satisfaction — Analysis Report</title>
<style>
:root{{--navy:{NAVY};--teal:{TEAL};--coral:{CORAL};--gold:{GOLD};--pale:{PALE};--ink:{INK};--muted:{MUTED};--paper:#F7F8FA;--white:#fff;}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.65}}
.wrap{{width:min(1160px,calc(100% - 40px));margin:auto}} .topbar{{background:var(--navy);color:#fff;position:sticky;top:0;z-index:20;box-shadow:0 4px 18px #13223822}}
.nav{{min-height:64px;display:flex;align-items:center;justify-content:space-between;gap:24px}} .brand{{font-weight:800;letter-spacing:.02em}} .links{{display:flex;gap:20px;flex-wrap:wrap}} .links a{{color:#dce7ee;text-decoration:none;font-size:.9rem}} .links a:hover,.links a:focus{{color:#fff}}
.hero{{background:linear-gradient(135deg,var(--navy) 0%,#1c3852 62%,#155e63 100%);color:#fff;padding:84px 0 76px;position:relative;overflow:hidden}}
.hero:after{{content:"";position:absolute;width:420px;height:420px;border:90px solid #ffffff0c;border-radius:50%;right:-110px;top:-140px}} .eyebrow{{text-transform:uppercase;letter-spacing:.14em;color:#96e0d7;font-size:.76rem;font-weight:800}}
h1{{font-size:clamp(2.5rem,6vw,5.4rem);line-height:1.02;letter-spacing:-.055em;max-width:900px;margin:14px 0 24px}} .lede{{font-size:1.16rem;max-width:760px;color:#d9e5ec}}
.hero-meta{{display:flex;gap:14px;flex-wrap:wrap;margin-top:32px}} .pill{{border:1px solid #ffffff30;background:#ffffff0d;padding:8px 13px;border-radius:999px;font-size:.85rem}}
main{{padding:56px 0 90px}} section{{scroll-margin-top:84px;margin:0 0 72px}} .section-label{{color:var(--teal);font-size:.78rem;font-weight:850;text-transform:uppercase;letter-spacing:.13em}}
h2{{color:var(--navy);font-size:clamp(1.8rem,3vw,2.7rem);letter-spacing:-.035em;line-height:1.12;margin:8px 0 18px}} h3{{color:var(--navy);font-size:1.18rem;margin:0 0 8px}} .intro{{max-width:850px;font-size:1.05rem;color:#526170}}
.kpis{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin-top:-86px;position:relative;z-index:3;margin-bottom:72px}} .kpi{{background:#fff;border-radius:18px;padding:24px;box-shadow:0 14px 40px #13223812;border:1px solid #e7ebef}}
.kpi b{{display:block;font-size:2rem;line-height:1;color:var(--navy);margin-bottom:10px}} .kpi span{{font-size:.86rem;color:var(--muted)}}
.grid2{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:24px}} .card{{background:#fff;border:1px solid #e4e9ed;border-radius:20px;padding:28px;box-shadow:0 8px 28px #1322380a}} .card p:last-child{{margin-bottom:0}}
.chart{{background:#fff;border:1px solid #e4e9ed;border-radius:20px;padding:20px;box-shadow:0 8px 28px #1322380a}} .chart img{{display:block;width:100%;height:auto}} .caption{{font-size:.82rem;color:var(--muted);margin:8px 8px 0}}
.callout{{border-left:5px solid var(--teal);background:var(--pale);padding:22px 24px;border-radius:0 16px 16px 0;margin:24px 0}} .callout strong{{color:var(--navy)}}
.hypotheses{{display:grid;gap:18px}} .hypothesis{{display:grid;grid-template-columns:74px 1fr auto;gap:20px;align-items:start;background:#fff;padding:25px;border-radius:18px;border:1px solid #e3e8ec}}
.hnum{{height:54px;width:54px;border-radius:14px;background:var(--navy);color:#fff;display:grid;place-items:center;font-weight:850}} .decision{{white-space:nowrap;color:#08665f;background:#dff4ef;border:1px solid #bce8de;padding:6px 10px;border-radius:999px;font-size:.78rem;font-weight:850}}
.metrics{{display:flex;gap:10px;flex-wrap:wrap;margin-top:12px}} .metric{{background:#f0f4f6;border-radius:9px;padding:6px 9px;font-size:.8rem;color:#465867}}
.insights{{counter-reset:item;display:grid;grid-template-columns:repeat(2,1fr);gap:18px}} .insight{{counter-increment:item;background:var(--navy);color:#eaf2f6;border-radius:18px;padding:26px;min-height:190px}} .insight:before{{content:"0" counter(item);display:block;color:#78d4ca;font-weight:850;margin-bottom:22px}} .insight h3{{color:#fff}} .insight p{{color:#cbd8df}}
.recommendations{{display:grid;gap:14px}} .rec{{background:#fff;border:1px solid #e4e9ed;border-radius:16px;padding:22px;display:grid;grid-template-columns:48px 1fr;gap:16px}} .icon{{width:42px;height:42px;border-radius:12px;background:#e3f1ef;color:var(--teal);font-weight:900;display:grid;place-items:center}}
.note{{font-size:.86rem;color:var(--muted)}} footer{{background:var(--navy);color:#c8d5dc;padding:34px 0;font-size:.86rem}} footer strong{{color:#fff}}
@media(max-width:850px){{.links{{display:none}}.kpis{{grid-template-columns:repeat(2,1fr)}}.grid2,.insights{{grid-template-columns:1fr}}.hypothesis{{grid-template-columns:58px 1fr}}.decision{{grid-column:2}}}}
@media(max-width:520px){{.wrap{{width:min(100% - 24px,1160px)}}.hero{{padding:64px 0 70px}}.kpis{{grid-template-columns:1fr;margin-top:-52px}}.card,.chart{{padding:18px}}h1{{font-size:2.55rem}}}}
@media print{{.topbar{{display:none}}body{{background:#fff}}.hero{{padding:40px 0}}.kpis{{margin-top:20px}}section{{break-inside:avoid}}}}
</style>
</head>
<body>
<header class="topbar"><div class="wrap nav"><div class="brand">AIRLINE EXPERIENCE / 2026</div><nav class="links" aria-label="Report sections"><a href="#problem">Problem</a><a href="#data">Data</a><a href="#analysis">Analysis</a><a href="#insights">Insights</a><a href="#recommendations">Recommendations</a></nav></div></header>
<div class="hero"><div class="wrap"><div class="eyebrow">Passenger satisfaction research</div><h1>Where the passenger experience earns loyalty—and where it loses altitude.</h1><p class="lede">A complete exploratory and statistical analysis of 129,880 airline passenger surveys, connecting service quality, cabin class, and disruption to overall satisfaction.</p><div class="hero-meta"><span class="pill">129,880 survey records</span><span class="pill">24 source variables</span><span class="pill">3 tested hypotheses</span><span class="pill">Observational study</span></div></div></div>
<main><div class="wrap">
<div class="kpis"><div class="kpi"><b>43.4%</b><span>Overall satisfaction rate</span></div><div class="kpi"><b>69.4%</b><span>Business-class satisfaction</span></div><div class="kpi"><b>3.64</b><span>Highest service mean: inflight service</span></div><div class="kpi"><b>0.30%</b><span>Records missing arrival delay</span></div></div>

<section id="problem"><div class="section-label">01 / Problem statement</div><h2>Turn passenger feedback into a focused service strategy.</h2><p class="intro">Airlines compete on more than price and schedule. Cleanliness, comfort, onboard service, digital touchpoints, cabin experience, and operational reliability all shape whether a journey feels worth repeating. This project asks which observed experience factors are most closely associated with overall passenger satisfaction—and whether those patterns persist once passenger and trip context are considered.</p>
<div class="grid2" style="margin-top:24px"><div class="card"><h3>Business objective</h3><p>Identify service attributes and passenger segments with the strongest satisfaction gaps so improvement effort can be directed toward the moments most likely to matter.</p></div><div class="card"><h3>Analytical objective</h3><p>Describe the sample, visualize relationships, and formally test service quality, travel class, and delay hypotheses using effect sizes, adjusted models, and sensitivity checks.</p></div></div></section>

<section id="data"><div class="section-label">02 / Data overview</div><h2>A large, analysis-ready survey with transparent limitations.</h2><div class="grid2"><div class="card"><h3>What the data contains</h3><p>Passenger age and recorded gender; first-time or returning status; business or personal travel; cabin class; flight distance and delays; fourteen service ratings; and a binary satisfaction outcome.</p><p class="note">City, device, fare, route, aircraft, loyalty tier, delay cause, and repeat-customer history are unavailable.</p></div><div class="card"><h3>Quality review</h3><p>All 129,880 IDs are unique. There are no complete duplicate rows, malformed values, invalid rating ranges, or engineered-feature mismatches. The 393 missing arrival delays were retained and flagged rather than imputed.</p><p class="note">Undocumented zero service ratings are preserved in source fields and excluded only in dedicated clean analysis fields.</p></div></div>
<div class="grid2" style="margin-top:24px"><div class="chart"><img src="data:image/png;base64,{charts['satisfaction']}" alt="Bar chart showing 43.4 percent satisfied and 56.6 percent neutral or dissatisfied"><p class="caption">The outcome combines neutral and dissatisfied passengers into a single category.</p></div><div class="card"><h3>Who is represented?</h3><p><strong>81.7%</strong> are returning customers and <strong>69.1%</strong> travel for business. Business class represents 47.9%, Economy 44.9%, and Economy Plus 7.2%. Median age is 40 and the recorded gender split is nearly even.</p><div class="callout"><strong>Interpretation guardrail:</strong> overall results reflect a sample dominated by returning and business-purpose travelers. Segment composition must be considered before making operational conclusions.</div></div></div></section>

<section id="analysis"><div class="section-label">03 / Analysis</div><h2>The evidence builds across three connected stories.</h2>
<h3 style="margin-top:28px">Service quality</h3><p class="intro">Operational service is rated more strongly than digital touchpoints. More importantly, the three services in the first hypothesis separate satisfied from unsatisfied passengers.</p><div class="grid2" style="margin-top:20px"><div class="chart"><img src="data:image/png;base64,{charts['service_means']}" alt="Horizontal bar chart of mean service ratings"><p class="caption">Clean means treat undocumented zero ratings as missing.</p></div><div class="chart"><img src="data:image/png;base64,{charts['service_rates']}" alt="Line chart of satisfaction rate by cleanliness seat comfort and onboard service ratings"><p class="caption">Observed rates rise most clearly at ratings 4 and 5; seat comfort is less orderly at ratings 1–3.</p></div></div>
<h3 style="margin-top:38px">Travel class and context</h3><p class="intro">Business class has a large raw advantage, and it remains after adjustment. Yet travel purpose changes the level of satisfaction within every class.</p><div class="grid2" style="margin-top:20px"><div class="chart"><img src="data:image/png;base64,{charts['class']}" alt="Grouped bar chart comparing observed and adjusted satisfaction by travel class"><p class="caption">Adjusted probabilities account for age, gender, customer status, travel purpose, flight distance, and departure delay.</p></div><div class="chart"><img src="data:image/png;base64,{charts['context']}" alt="Heatmap of satisfaction rates by travel class and travel purpose"><p class="caption">Business-purpose travel has a higher baseline across all three classes.</p></div></div>
<h3 style="margin-top:38px">Flight disruption</h3><p class="intro">Satisfaction falls rapidly from no delay to moderate delay. Formal models confirm that the pattern is nonlinear: the steepest decline occurs early, then flattens or partially rebounds at longer durations.</p><div class="chart" style="margin-top:20px"><img src="data:image/png;base64,{charts['delays']}" alt="Line chart showing satisfaction rates declining across departure and arrival delay bands"><p class="caption">All extreme but plausible delay values were retained. Delay units are not documented in the source.</p></div>
</section>

<section id="testing"><div class="section-label">04 / Hypothesis testing</div><h2>All three null hypotheses are rejected—effect size gives the result meaning.</h2><div class="hypotheses">
<article class="hypothesis"><div class="hnum">H1</div><div><h3>Service quality is associated with satisfaction</h3><p>The joint categorical logistic model for cleanliness, seat comfort, and onboard service was significant. In the adjusted trend model, a one-point increase corresponded with odds ratios of 1.44, 1.32, and 1.82 respectively.</p><div class="metrics"><span class="metric">LR = 33,591.61</span><span class="metric">df = 12</span><span class="metric">p &lt; 10⁻³⁰⁰</span><span class="metric">N = 129,861</span></div></div><span class="decision">REJECT H0</span></article>
<article class="hypothesis"><div class="hnum">H2</div><div><h3>Business class has materially higher satisfaction</h3><p>Business class leads Economy by 50.7 percentage points and Economy Plus by 44.8 points in the raw data. The global association is substantial (Cramér’s V = 0.503) and remains after adjustment.</p><div class="metrics"><span class="metric">χ² = 32,906.17</span><span class="metric">df = 2</span><span class="metric">p &lt; 10⁻³⁰⁰</span><span class="metric">Cramér’s V = .503</span></div></div><span class="decision">REJECT H0</span></article>
<article class="hypothesis"><div class="hnum">H3</div><div><h3>Delay is associated with lower satisfaction</h3><p>Departure and arrival delay are both significant, with nonlinear spline models fitting better than a constant linear effect. At 60 units, adjusted satisfaction is 9.7 points lower for departure delay and 11.6 points lower for arrival delay versus zero.</p><div class="metrics"><span class="metric">Departure p = 6.58 × 10⁻¹⁵⁵</span><span class="metric">Arrival p = 3.18 × 10⁻²⁹⁸</span><span class="metric">Spline form retained</span></div></div><span class="decision">REJECT H0</span></article>
</div><p class="note" style="margin-top:16px">Rejecting a null hypothesis indicates evidence of association in this dataset. It does not prove causation.</p></section>

<section id="insights"><div class="section-label">05 / Key insights</div><h2>Four ideas explain the passenger experience.</h2><div class="insights"><article class="insight"><h3>The biggest controllable signal is onboard service.</h3><p>Among the three core measures, onboard service has the largest adjusted one-point association with satisfaction. It is both a service-design priority and a frontline coaching opportunity.</p></article><article class="insight"><h3>Digital experience is the clearest quality gap.</h3><p>Inflight Wi-Fi and online booking hold the two lowest clean mean ratings. Improving them can address visible friction without assuming they alone will change overall satisfaction.</p></article><article class="insight"><h3>Class is powerful, but context is inseparable.</h3><p>Business class remains ahead after adjustment, while travel purpose and returning status substantially reshape the raw class comparison. Segment-level action is more useful than a single fleetwide average.</p></article><article class="insight"><h3>Disruption hurts early and then plateaus.</h3><p>The delay effect is nonlinear. Preventing small disruptions from becoming moderate ones may offer more leverage than treating every additional unit as equally damaging.</p></article></div></section>

<section id="recommendations"><div class="section-label">06 / Recommendations</div><h2>Translate evidence into a focused operating agenda.</h2><div class="recommendations">
<article class="rec"><div class="icon">1</div><div><h3>Prioritize onboard-service consistency</h3><p>Use flight- and crew-level quality monitoring, targeted coaching, and service-recovery playbooks. Track onboard-service ratings together with satisfaction, not in isolation.</p></div></article>
<article class="rec"><div class="icon">2</div><div><h3>Repair the digital journey</h3><p>Investigate Wi-Fi reliability and online-booking friction with task-level diagnostics. Add device and journey-stage data in future surveys so product teams can locate failure points.</p></div></article>
<article class="rec"><div class="icon">3</div><div><h3>Design class-specific improvement plans</h3><p>Protect the Business-class experience while focusing Economy and Economy Plus work on core comfort and service basics. Separate business-purpose from personal-purpose performance in reporting.</p></div></article>
<article class="rec"><div class="icon">4</div><div><h3>Intervene before delays become moderate</h3><p>Set operational triggers at early delay thresholds, improve proactive communication, and measure whether recovery actions narrow the satisfaction gap among disrupted passengers.</p></div></article>
<article class="rec"><div class="icon">5</div><div><h3>Build the data needed for causal and retention decisions</h3><p>Add stable customer IDs, survey and booking dates, route, fare, loyalty tier, aircraft, delay cause, compensation, city, and device. These fields enable true cohort retention and stronger causal evaluation.</p></div></article>
</div></section>

<section id="limitations"><div class="section-label">07 / Interpretation notes</div><h2>What this report can—and cannot—claim.</h2><div class="grid2"><div class="card"><h3>What is supported</h3><p>Strong, repeatable associations between satisfaction and service ratings, cabin class, and flight disruption; transparent effect sizes; adjusted comparisons using available covariates; and consistent sensitivity results.</p></div><div class="card"><h3>What is not supported</h3><p>Causal claims, true customer retention, neutral-versus-dissatisfied separation, or conclusions based on unavailable route, fare, device, city, loyalty, aircraft, and disruption-cause information.</p></div></div></section>
</div></main>
<footer><div class="wrap"><strong>Airline Passenger Satisfaction Analysis</strong><br>Prepared from 129,880 cleaned passenger survey records. Source units and rating-zero definitions remain undocumented.</div></footer>
</body></html>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(html, encoding="utf-8")
    print(f"Created {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()

