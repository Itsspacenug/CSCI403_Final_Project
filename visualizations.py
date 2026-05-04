import warnings
warnings.filterwarnings("ignore", category=Warning)
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# only load columns we need from the large snotel file
snotel = pd.read_csv("snotel_all_stations.csv",
                     usecols=["station_name", "date", "swe_in"],
                     parse_dates=["date"])
oni = pd.read_csv("cleaned_Monthly_ONI.csv")
streamflow = pd.read_csv("streamflow.csv", parse_dates=["date"])


# Chart 1: Statewide mean April 1 SWE by year, ENSO phase color-coded

april1 = snotel[(snotel["date"].dt.month == 4) & (snotel["date"].dt.day == 1)]
annual_swe = (april1
              .assign(year=april1["date"].dt.year)
              .groupby("year")["swe_in"]
              .mean()
              .reset_index())

winter_oni = (oni[oni["month"].isin([1, 2])]
              .groupby("year")["oni"]
              .mean()
              .reset_index()
              .rename(columns={"oni": "avg_oni"}))
winter_oni["phase"] = pd.cut(
    winter_oni["avg_oni"],
    bins=[-99, -0.5, 0.5, 99],
    labels=["La Niña", "Neutral", "El Niño"]
)

df1 = annual_swe.merge(winter_oni, on="year", how="left")
phase_colors = {"El Niño": "#e07b54", "La Niña": "#5b8db8", "Neutral": "#888888"}

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(df1["year"], df1["swe_in"], color="#cccccc", linewidth=1, zorder=1)
for phase, color in phase_colors.items():
    mask = df1["phase"] == phase
    ax.scatter(df1.loc[mask, "year"], df1.loc[mask, "swe_in"],
               label=phase, color=color, s=50, zorder=2)

ax.set_title("Statewide Mean April 1 SWE by Year", fontsize=14, fontweight="bold")
ax.set_xlabel("Year")
ax.set_ylabel("Mean SWE (in)")
ax.legend(title="ENSO Phase")
ax.grid(axis="y", linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("chart1_swe_enso.png", dpi=150)
plt.close()
print("Saved chart1_swe_enso.png")


# Chart 2: Heatmap — peak SWE by basin (station name prefix) × decade

snotel["basin"] = snotel["station_name"].str.split().str[0]
snotel["year"] = snotel["date"].dt.year
snotel["decade"] = (snotel["year"] // 10 * 10).astype(str) + "s"

peak_swe = (snotel
            .groupby(["basin", "year", "decade"])["swe_in"]
            .max()
            .reset_index()
            .groupby(["basin", "decade"])["swe_in"]
            .mean()
            .unstack("decade"))

fig, ax = plt.subplots(figsize=(10, max(4, len(peak_swe) * 0.35)))
im = ax.imshow(peak_swe.values, aspect="auto", cmap="YlOrRd")

ax.set_xticks(range(len(peak_swe.columns)))
ax.set_xticklabels(peak_swe.columns, fontsize=9)
ax.set_yticks(range(len(peak_swe.index)))
ax.set_yticklabels(peak_swe.index, fontsize=8)
ax.set_title("Peak SWE by Basin × Decade (in)", fontsize=14, fontweight="bold")

plt.colorbar(im, ax=ax, label="Avg Peak SWE (in)")
fig.tight_layout()
fig.savefig("chart2_heatmap.png", dpi=150)
plt.close()
print("Saved chart2_heatmap.png")


# Chart 3: Scatter — April 1 SWE vs. summer streamflow by gauge

april1_annual = (april1
                 .assign(year=april1["date"].dt.year)
                 .groupby("year")["swe_in"]
                 .mean()
                 .reset_index())

summer_flow = (streamflow[streamflow["date"].dt.month.between(6, 8)]
               .assign(year=streamflow["date"].dt.year)
               .groupby(["site_name", "year"])["discharge_cfs"]
               .mean()
               .reset_index())

df3 = summer_flow.merge(april1_annual, on="year", how="inner")
gauges = df3["site_name"].unique()
colors = plt.cm.tab10(np.linspace(0, 1, len(gauges)))

fig, ax = plt.subplots(figsize=(9, 6))
for gauge, color in zip(gauges, colors):
    sub = df3[df3["site_name"] == gauge]
    ax.scatter(sub["swe_in"], sub["discharge_cfs"],
               label=gauge, color=color, alpha=0.75, s=45)

ax.set_title("April 1 SWE vs. Summer Discharge by Gauge", fontsize=14, fontweight="bold")
ax.set_xlabel("Statewide Mean April 1 SWE (in)")
ax.set_ylabel("Mean Summer Discharge (cfs)")
ax.legend(title="Gauge", fontsize=7, title_fontsize=8)
ax.grid(linestyle="--", alpha=0.4)
fig.tight_layout()
fig.savefig("chart3_swe_streamflow.png", dpi=150)
plt.close()
print("Saved chart3_swe_streamflow.png")