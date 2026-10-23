"""Streamlit app: who drove the boom in business creations in France?

Run:  streamlit run app.py
"""
from html import escape

import pandas as pd
import streamlit as st

from utils import constants as C
from utils import viz
from utils.io import (DATA_SOURCE, GEO_SOURCE, annual_csv, load_geojson,
                      load_summary, load_tables, load_trend)
from utils.profile import LOGO_PATH, PROFILE
from utils.style import inject_css

st.set_page_config(page_title="Business creations in France", layout="wide")
inject_css()

annual, quality, tidy = load_tables()
geojson = load_geojson()
trend_all = load_trend()
summary = load_summary()
LABEL2CODE = {v: k for k, v in C.LEGAL_FORM_LABELS.items()}


def identity_block():
    """Identity block required by the instructor (logo, name, program, contacts, course)."""
    P = PROFILE

    def link(url, text):
        return f'<a href="{escape(url)}" target="_blank" rel="noopener">{escape(text)}</a>'

    def short(url):
        return url.replace("https://", "").replace("www.", "").rstrip("/")

    def rows(items):
        return "".join(f"<dt>{escape(k)}</dt><dd>{v}</dd>" for k, v in items)

    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=150)
    st.markdown(
        f'<div class="idname">{escape(P["name"])}</div>'
        f'<dl class="idcard">' + rows([
            ("Program", escape(P["program"])),
            ("Year", escape(P["year"])),
            ("Email", link("mailto:" + P["email"], P["email"])),
            ("LinkedIn", link(P["linkedin"], short(P["linkedin"]))),
            ("GitHub", link(P["github"], short(P["github"]))),
        ]) + "</dl>"
        f'<dl class="idcard">' + rows([
            ("Course", escape(P["course"])),
            ("Project", escape(P["project"])),
            ("Instructor", escape(P["instructor"]) + " – "
             + link("mailto:" + P["instructor_contact"], P["instructor_contact"])),
        ]) + "</dl>",
        unsafe_allow_html=True,
    )
    st.divider()


def note(*paragraphs):
    """Reading notes next to a figure (also the text alternative of the chart)."""
    st.markdown("<div class='note'>" + "".join(f"<p>{p}</p>" for p in paragraphs) + "</div>",
                unsafe_allow_html=True)


def show_chart(fig):
    """Show a Plotly chart at full width (works across Streamlit versions)."""
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def show_table(df, **kwargs):
    """Show a table at full width (works across Streamlit versions)."""
    try:
        st.dataframe(df, width="stretch", hide_index=True, **kwargs)
    except TypeError:
        st.dataframe(df, use_container_width=True, hide_index=True, **kwargs)


# ----------------------------------------------------------------- Filters
complete = annual[annual["annee_complete"] & (annual["niveau"] == "DEP")]
y_min, y_max = int(complete["annee"].min()), int(complete["annee"].max())

with st.sidebar:
    identity_block()
    st.header("Filters")
    start, end = st.select_slider(
        "Period (complete years)",
        options=list(range(y_min, y_max + 1)),
        value=(2019, y_max),
        help="Département data starts in 2012. "
             "2026 is excluded because the year is not over yet.",
    )
    forms = st.multiselect(
        "Legal forms to compare (lines)",
        [C.LEGAL_FORM_LABELS[k] for k in C.LEGAL_FORM_PARTS],
        default=[C.LEGAL_FORM_LABELS[k] for k in C.LEGAL_FORM_PARTS],
    )
    form_label = st.selectbox(
        "Legal form for sectors and map",
        ["Total", "Micro-entrepreneurs", "Companies"],
        help="“Total” = all business creations.",
    )
    st.caption("Annual figures are raw (not seasonally adjusted): sum of the 12 months of "
               "each year. The monthly trend uses seasonally adjusted figures.")

form_code = LABEL2CODE[form_label]
form_color = viz.FORM_COLORS[form_label]
if start >= end:
    st.warning("Pick a period of at least two years to see a change.")
    st.stop()

# ---------------------------------------------------- Tables (pre-aggregated)
fr = annual[(annual["niveau"] == "FRANCE") & (annual["code_secteur"] == "_T")
            & annual["annee_complete"]]


def fr_value(code_forme, year):
    return float(fr[(fr["code_forme"] == code_forme) & (fr["annee"] == year)]["creations"].iloc[0])


tot_start, tot_end = fr_value("_T", start), fr_value("_T", end)
mic_start, mic_end = fr_value("MICRO", start), fr_value("MICRO", end)
var_pct = (tot_end / tot_start - 1) * 100
micro_share = mic_end / tot_end * 100
micro_contrib = ((mic_end - mic_start) / (tot_end - tot_start) * 100
                 if tot_end != tot_start else float("nan"))
change_word = "increase" if tot_end >= tot_start else "decrease"

# Monthly momentum (seasonally adjusted): latest year so far vs the year before
last_year = int(trend_all["annee"].max())
prev_year = last_year - 1


def month_avg(code, year):
    s = trend_all[(trend_all["code_forme"] == code) & (trend_all["annee"] == year)]["creations"]
    return float(s.mean())


n_last = int(((trend_all["code_forme"] == "_T") & (trend_all["annee"] == last_year)).sum())
period_txt = f"the first {n_last} months of {last_year}" if n_last < 12 else str(last_year)
tot_last, tot_prev = month_avg("_T", last_year), month_avg("_T", prev_year)
mic_last, mic_prev = month_avg("MICRO", last_year), month_avg("MICRO", prev_year)
mom = (tot_last / tot_prev - 1) * 100
mic_mom = (mic_last / mic_prev - 1) * 100
above = "above" if mom >= 0 else "below"

# ------------------------------------------------------------------ Opening
st.title("Who drove the boom in business creations in France?")
contrib_txt = (f" Micro-entrepreneurs explain <strong>{micro_contrib:.0f}%</strong> of the "
               f"{change_word}." if micro_contrib == micro_contrib else "")
st.markdown(
    f"<p class='lede'>Between {start} and {end}, business creations in France "
    f"{'rose' if var_pct >= 0 else 'fell'} <strong>{abs(var_pct):.0f}%</strong>, "
    f"from {tot_start:,.0f} to {tot_end:,.0f}.{contrib_txt} In {period_txt}, "
    f"seasonally adjusted monthly creations are <strong>{abs(mom):.0f}% {above}</strong> "
    f"{prev_year}.</p>",
    unsafe_allow_html=True,
)

k1, k2, k3, k4 = st.columns(4, gap="large")
k1.metric(f"Creations in {end}", f"{tot_end:,.0f}", f"{var_pct:+.1f}% vs {start}",
          delta_color="off")
k2.metric("Micro-entrepreneur share", f"{micro_share:.0f}%",
          f"{micro_share - mic_start / tot_start * 100:+.1f} pts vs {start}", delta_color="off")
k3.metric("Micro share of change",
          f"{micro_contrib:.0f}%" if micro_contrib == micro_contrib else "n/a",
          help=f"Share of the total {change_word} between the two years explained by "
               "micro-entrepreneurs.")
k4.metric("Index (base 100)", f"{tot_end / tot_start * 100:.0f}", f"base = {start}",
          delta_color="off")

st.markdown(
    f"<p class='meta'>Written for local elected officials and economic-development officers. "
    f"Source: {escape(DATA_SOURCE)}.</p>",
    unsafe_allow_html=True,
)
with st.expander("What counts as a business creation?"):
    st.markdown(
        "- A **business creation** is a new legal unit registered in the INSEE Sirene "
        "register, excluding agriculture. It is **not** a job creation.\n"
        "- **Micro-entrepreneur**: simplified sole-proprietorship regime.\n"
        "- **2023: series break.** The new business-formalities portal changed the "
        "counting date; INSEE neutralised the effect, but comparisons around 2023 "
        "should be read with caution."
    )

# --------------------------------------------------------- Legal forms
if micro_contrib == micro_contrib:
    st.header(f"One regime explains the growth: micro-entrepreneurs account for "
              f"{micro_contrib:.0f}% of the {change_word}")
else:
    st.header("Legal forms followed very different paths")
sel_codes = [LABEL2CODE[f] for f in forms] + ["_T"]
line = fr[fr["code_forme"].isin(sel_codes) & fr["annee"].between(start, end)].copy()
base = line[line["annee"] == start].set_index("code_forme")["creations"]
line["indice"] = line.apply(lambda r: r["creations"] / base[r["code_forme"]] * 100, axis=1)
end_idx = line[line["annee"] == end].set_index("forme_legale")["indice"]
fig_col, note_col = st.columns([7, 3], gap="large")
with fig_col:
    show_chart(viz.index_lines(line, start))
with note_col:
    note(
        f"<strong>How to read it.</strong> Line chart: one line per legal form. Horizontal axis: "
        f"year. Vertical axis: number of creations indexed to {start} = 100, so 135 means "
        f"35% more creations than in {start}.",
        f"In {end}, the index stands at " + ", ".join(
            f"{escape(k)} {v:.0f}" for k, v in end_idx.items()) + ".",
        "The vertical dashed line marks 2023, when the counting method changed.",
    )

# ------------------------------------------------------ Monthly momentum
st.header(f"Monthly creations in {period_txt} are {abs(mom):.0f}% {above} {prev_year}")
tr = trend_all[(trend_all["annee"] >= start) & trend_all["code_forme"].isin(sel_codes)]
t_tot = tr[tr["code_forme"] == "_T"].sort_values("date")
fig_col, note_col = st.columns([7, 3], gap="large")
with fig_col:
    show_chart(viz.trend_lines(tr))
with note_col:
    note(
        "<strong>How to read it.</strong> Monthly lines, seasonally adjusted: the usual "
        "yearly pattern is removed, so months can be compared. Vertical axis: creations per "
        "month, starting at zero.",
        f"The total goes from {t_tot['creations'].iloc[0]:,.0f} in {t_tot['date'].min():%B %Y} "
        f"to {t_tot['creations'].iloc[-1]:,.0f} in {t_tot['date'].max():%B %Y}. "
        f"Micro-entrepreneurs: {mic_last:,.0f} a month on average in {period_txt}, "
        f"{abs(mic_mom):.0f}% {'above' if mic_mom >= 0 else 'below'} {prev_year}.",
        "The grey band is the spring 2020 lockdown. The trend continues past the end year of "
        "the filter on purpose. INSEE revises the latest months: read the last points as a "
        "trend. This dataset says nothing about whether these businesses survive.",
    )

# ------------------------------------------------------------ Sectors
sec = annual[(annual["niveau"] == "FRANCE") & (annual["code_forme"] == form_code)
             & annual["code_secteur"].isin(C.SECTOR_SHORT)]
d0 = sec[sec["annee"] == start].set_index("code_secteur")["creations"]
d1 = sec[sec["annee"] == end].set_index("code_secteur")["creations"]
sectors = pd.DataFrame({"debut": d0, "fin": d1}).dropna()
sectors["variation"] = sectors["fin"] - sectors["debut"]
sectors["variation_pct"] = (sectors["fin"] / sectors["debut"] - 1) * 100
sectors["secteur_court"] = sectors.index.map(C.SECTOR_SHORT)
top = sectors["variation"].idxmax()
worst = sectors["variation"].idxmin()
st.header(f"{C.SECTOR_SHORT[top]} gains the most: "
          f"{sectors.loc[top, 'variation']:+,.0f} creations")
fig_col, note_col = st.columns([7, 3], gap="large")
with fig_col:
    show_chart(viz.sector_bars(sectors.reset_index(), form_label))
with note_col:
    note(
        f"<strong>How to read it.</strong> One horizontal bar per sector: change in the number "
        f"of creations between {start} and {end} for “{escape(form_label)}” "
        f"(horizontal axis). A bar to the right of zero is an increase.",
        f"Largest change: {escape(C.SECTOR_SHORT[top])} "
        f"({sectors.loc[top, 'variation']:+,.0f}, {sectors.loc[top, 'variation_pct']:+.0f}%). "
        f"Smallest: {escape(C.SECTOR_SHORT[worst])} ({sectors.loc[worst, 'variation']:+,.0f}).",
        "Change the legal form in the sidebar to see whether the pattern holds.",
    )

# -------------------------------------------------------------- Territories
dep = annual[(annual["niveau"] == "DEP") & (annual["code_secteur"] == "_T")
             & (annual["code_forme"] == form_code)]
p = dep[dep["annee"].isin([start, end])].pivot_table(
    index=["code_geo", "lieu"], columns="annee", values="creations").reset_index()
p["variation_pct"] = (p[end] / p[start] - 1) * 100
p = p.rename(columns={start: "creations_debut", end: "creations_fin"})
p["variation_abs"] = p["creations_fin"] - p["creations_debut"]
metro = p[~p["code_geo"].isin(C.OVERSEAS_DEPS)]
overseas = p[p["code_geo"].isin(C.OVERSEAS_DEPS)]

n_up = int((metro["variation_pct"] > 0).sum())
best = metro.loc[metro["variation_pct"].idxmax()]
big = metro.loc[metro["variation_abs"].idxmax()]
st.header(f"{n_up} of {len(metro)} mainland départements gained creations")
metric = st.radio("Map indicator", ["Change (%)", f"Creations in {end}"], horizontal=True)
col = "variation_pct" if metric.startswith("Change") else "creations_fin"
fig_col, note_col = st.columns([7, 3], gap="large")
with fig_col:
    show_chart(viz.dept_map(metro, geojson, col, metric, color=form_color))
    st.caption(f"Base map: {GEO_SOURCE}.")
with note_col:
    if best["lieu"] == big["lieu"]:
        lead = (f"{escape(best['lieu'])} leads both in growth ({best['variation_pct']:+.0f}%) "
                f"and in volume ({best['variation_abs']:+,.0f} creations).")
    else:
        lead = (f"Fastest growth: {escape(best['lieu'])} ({best['variation_pct']:+.0f}%, but only "
                f"{best['variation_abs']:+,.0f} creations). Largest increase in volume: "
                f"{escape(big['lieu'])} ({big['variation_abs']:+,.0f}, "
                f"{big['variation_pct']:+.0f}%).")
    note(
        "<strong>How to read it.</strong> Map of mainland France, one shape per département. "
        + ("Darker = larger change in the number of creations between the two years."
           if col == "variation_pct" else f"Darker = more creations in {end}.")
        + " Hover a département for its name and figures.",
        lead,
        "Overseas départements are in the table below.",
    )

rank_mode = st.radio("Rank départements by", ["Change (%)", "Change (number of creations)"],
                     horizontal=True)
pct_rank = rank_mode == "Change (%)"
rcol = "variation_pct" if pct_rank else "variation_abs"
c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown("**10 fastest-growing départements**" if pct_rank
                else "**10 largest increases (number of creations)**")
    show_chart(viz.rank_bars(metro.nlargest(10, rcol), rcol, rank_mode, pct=pct_rank,
                             color=form_color))
with c2:
    st.markdown("**10 slowest-growing départements**" if pct_rank
                else "**10 smallest increases (number of creations)**")
    show_chart(viz.rank_bars(metro.nsmallest(10, rcol), rcol, rank_mode, pct=pct_rank,
                             color=form_color))
st.caption(
    "Two horizontal bar charts ranking mainland départements. "
    + ("A small département can show a large percentage change with few creations: "
       "switch to the number of creations to see the volumes."
       if pct_rank else
       "In absolute numbers, large départements dominate: switch to percentages to compare "
       "growth regardless of size.")
)
with st.expander("Overseas départements (not on the map)"):
    ov = overseas[["code_geo", "lieu", "creations_debut", "creations_fin", "variation_pct"]].copy()
    ov.columns = ["Code", "Département", f"Creations {start}", f"Creations {end}", "Change (%)"]
    show_table(ov.round(1))

# ------------------------------------------------------------ Data quality
st.header("Can you trust these numbers?")
q = pd.DataFrame(quality)
q["Result"] = q["ok"].map({True: "✅ OK", False: "❌ Failed"})
show_table(q[["controle", "Result", "detail"]].rename(
    columns={"controle": "Check", "detail": "Detail"}))
m1, m2, m3 = st.columns(3, gap="large")
m1.metric("Rows analysed", f"{len(tidy):,}")
m2.metric("Missing values", int(tidy["creations"].isna().sum()))
m3.metric("Duplicates", int(tidy.duplicated(subset=["niveau", "code_geo", "code_secteur",
                                                    "code_forme", "frequence", "brut", "periode"]).sum()))

with st.expander("What was done to the data (step by step)"):
    if summary:
        s = summary
        dropped = ", ".join(s["dropped_columns"])
        st.markdown(
            f"1. **Loaded** the raw INSEE CSV as text ({s['raw_rows']:,} rows × "
            f"{s['raw_columns']} columns), so nothing is silently converted.\n"
            f"2. **Renamed** the 9 useful columns and **dropped** {len(s['dropped_columns'])} "
            f"technical ones ({dropped})"
            + (": each holds one single value, so they carry no information.\n"
               if s["dropped_are_constant"] else ".\n")
            + f"3. **Converted** values to numbers ({s['invalid_numbers']} invalid) and periods "
            "to real dates (months) or quarters.\n"
            "4. **Added readable labels** from the INSEE metadata file. Place names are matched "
            "on level + code, because the same code can be both a region and a département "
            "(a bug found and fixed during the project).\n"
            f"5. **Removed exact duplicates** ({s['duplicates_removed']} found).\n"
            "6. **Ran the checks above**: if one fails, the build stops.\n"
            f"7. **Aggregated** the raw monthly figures into annual totals (complete 12-month "
            f"years only): {s['annual_rows']:,} rows with a base-100 index and year-on-year growth."
        )
        show_table(pd.DataFrame({
            "": ["Rows", "Columns", "Duplicate rows", "Invalid numbers",
                 "Months covered", "Places"],
            "Raw file": [f"{s['raw_rows']:,}", str(s["raw_columns"]),
                         str(s["duplicates_removed"]), "not checked (stored as text)",
                         f"{s['first_month']} → {s['last_month']}", "-"],
            "Clean table": [f"{s['clean_rows']:,}", str(s["clean_columns"]), "0",
                            str(s["invalid_numbers"]),
                            f"{s['first_month']} → {s['last_month']}",
                            f"1 France + {s['places'].get('REG', 0)} regions + "
                            f"{s['places'].get('DEP', 0)} départements"],
        }))
        st.caption("Cleaning never alters a value: it renames, converts types and adds labels.")
    else:
        st.info("Run `python -m scripts.build_data` to generate the preparation summary.")
st.download_button(
    "Download the clean annual table (CSV)", annual_csv(),
    file_name="business_creations_annual_clean.csv", mime="text/csv",
    help="All places, sectors and legal forms; annual totals, base-100 index and growth.",
)

st.markdown(
    "<ul class='limits'>"
    "<li><strong>Not jobs.</strong> A business creation is not a job creation: "
    "micro-enterprises weigh heavily in the figures.</li>"
    "<li><strong>2023 break.</strong> The new business-formalities portal changed how "
    "creations are counted.</li>"
    "<li><strong>Raw and adjusted.</strong> Annual figures are raw; the monthly trend is "
    "seasonally adjusted, and INSEE revises the latest months.</li>"
    "<li><strong>Little detail by département.</strong> Sector detail is limited, so the map "
    "uses the total.</li>"
    "<li><strong>No causes.</strong> The data show correlations, not causes, and say nothing "
    "about business survival.</li>"
    "<li><strong>Aggregated data.</strong> No personal data is used.</li>"
    "</ul>",
    unsafe_allow_html=True,
)

# -------------------------------------------------------- Conclusions
st.header("What to remember")
st.markdown(
    "<dl class='remember'>"
    f"<dt>Finding</dt><dd>{var_pct:+.0f}% creations between {start} and {end}, largely driven "
    f"by micro-entrepreneurs. Seasonally adjusted monthly creations are {abs(mom):.0f}% "
    f"{above} {prev_year} in {period_txt}: the momentum has not reversed.</dd>"
    "<dt>Implication</dt><dd>For a territory, a high creation rate does not automatically "
    "mean more jobs: survival rates and the move from micro-enterprise to company must be "
    "tracked too.</dd>"
    "<dt>Next steps</dt><dd>Cross-check with business failures, population and employment "
    "data to measure the quality of this dynamic.</dd>"
    "</dl>",
    unsafe_allow_html=True,
)
