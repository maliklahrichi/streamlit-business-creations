# Storyboard: "The boom in business creations: who really drove it?"

**Author:** Malik Lahrichi (student no. 20231512, group DE1) · EFREI Paris · Data Analysis & Visualization 2026
**Audience:** local elected officials and economic-development officers (non-specialists, little time).
**Question:** between two chosen years, how did business creations in France change, who drove the
increase (legal form, sector, territory), and is the momentum continuing?
**Data:** INSEE, *Créations d'entreprises – séries longues*, data.gouv.fr, Open Licence 2.0.

## Story arc
Hook (one number) → context (what a "creation" is) → insight (one regime explains the boom) →
momentum (is it still going?) → drill-down (sectors, territories) → trust (data quality, limits) → action.

## Scene by scene
Each section is titled by its finding (the title updates with the filters). Figure on the left,
reading note on the right.

| # | Section title (example, default view) | Chart and why | Message the reader keeps | Interaction |
|---|---------------------------------------|---------------|--------------------------|-------------|
| 0 | Opening statement + 4 KPIs | Text and KPI tiles: the answer in five seconds | +35% creations; micro-entrepreneurs explain 86% of it | Period slider, legal-form filters; everything updates |
| 1 | "What counts as a business creation?" (expander) | Text | A creation is a new legal unit, not a job | Expander with the 2023 series break |
| 2 | "One regime explains the growth: micro-entrepreneurs account for 86% of the increase" | Lines indexed to 100: comparing trajectories from a common start | Micro ×1.5, companies ×1.35, classic sole proprietors −26% | Hover; legal-form multiselect |
| 3 | "Monthly creations in the first 9 months of 2026 are 12% above 2025" | Lines starting at zero: honest scale, shows 2026 and the 2020 lockdown dip | No reversal so far | Hover (unified tooltip) |
| 4 | "Professional, scientific, technical & support services gains the most: +101,265 creations" | Sorted bars: easy to rank | The sector story differs from the legal-form story | Legal-form selectbox |
| 5 | "96 of 96 mainland départements gained creations" | Choropleth for geography; bars for exact rank | Lozère +59% is only +305 creations, Paris +53% is +41,616 | Map indicator, ranking by % or by number, hover |
| 6 | "Can you trust these numbers?" | Table of checks, before/after table, download | Figures are consistent (départements add up to France) | Expander "what was done to the data", CSV download |
| 7 | "What to remember" | Finding / implication / next steps | Creation is not employment; track survival | none |

## Design choices
- Headlines state the finding; one message per section.
- Neutral interface (ink on white). Colour means a legal form and nothing else (amber = micro,
  blue = companies, brick = sole proprietors, dashed ink = total). Palette checked for colour-blind
  readers (all pairs) and for contrast (at least 3:1 on white).
- Direction of change is shown by position (left or right of zero), not by a second colour code.
- Typography: Archivo (wide, bold) for headlines; Atkinson Hyperlegible Next for text, designed for
  legibility. Fonts are embedded (no third-party request).
- Every chart has labelled axes, units, tooltips and a reading note that also acts as its text alternative.
- Raw figures for annual sums (they match the official totals), seasonally adjusted figures for the monthly trend.

## Honest limits shown in the app
Creation ≠ job; 2023 series break; the latest months are revised by INSEE; no information on business
survival; correlation, not causation; aggregated data only.
