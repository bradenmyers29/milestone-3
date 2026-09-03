from pybaseball import statcast_pitcher
import pandas as pd
import os
import time


# ============================================================
# SETTINGS
# ============================================================

START_DATE = "2025-04-01"
END_DATE = "2025-09-28"

OUTPUT_DIR = "data"

RAW_FILE = f"{OUTPUT_DIR}/pitch_data_5_countries.csv"
SUMMARY_FILE = f"{OUTPUT_DIR}/pitch_summary_5_countries.csv"


# ============================================================
# PITCHERS
# ============================================================
#
# 5 countries
# 5 pitchers per country
# 2025 MLB regular season
#
# MLBAM IDs are the IDs used by Baseball Savant.
# ============================================================

pitchers = [

    # --------------------------------------------------------
    # USA
    # --------------------------------------------------------

    {
        "name": "Gerrit Cole",
        "country": "USA",
        "mlbam_id": 543037,
    },
    {
        "name": "Zack Wheeler",
        "country": "USA",
        "mlbam_id": 554430,
    },
    {
        "name": "Corbin Burnes",
        "country": "USA",
        "mlbam_id": 669203,
    },
    {
        "name": "Max Fried",
        "country": "USA",
        "mlbam_id": 608331,
    },
    {
        "name": "Chris Sale",
        "country": "USA",
        "mlbam_id": 519242,
    },


    # --------------------------------------------------------
    # JAPAN
    # --------------------------------------------------------

    {
        "name": "Shohei Ohtani",
        "country": "Japan",
        "mlbam_id": 660271,
    },
    {
        "name": "Yoshinobu Yamamoto",
        "country": "Japan",
        "mlbam_id": 808967,
    },
    {
        "name": "Shota Imanaga",
        "country": "Japan",
        "mlbam_id": 684007,
    },
    {
        "name": "Yusei Kikuchi",
        "country": "Japan",
        "mlbam_id": 579328,
    },
    {
        "name": "Kodai Senga",
        "country": "Japan",
        "mlbam_id": 673540,
    },


    # --------------------------------------------------------
    # DOMINICAN REPUBLIC
    # --------------------------------------------------------

    {
        "name": "Sandy Alcantara",
        "country": "Dominican Republic",
        "mlbam_id": 645261,
    },
    {
        "name": "Luis Castillo",
        "country": "Dominican Republic",
        "mlbam_id": 622491,
    },
    {
        "name": "Framber Valdez",
        "country": "Dominican Republic",
        "mlbam_id": 664285,
    },
    {
        "name": "Cristopher Sanchez",
        "country": "Dominican Republic",
        "mlbam_id": 650911,
    },
    {
        "name": "Ronel Blanco",
        "country": "Dominican Republic",
        "mlbam_id": 669854,
    },


    # --------------------------------------------------------
    # VENEZUELA
    # --------------------------------------------------------

    {
        "name": "Pablo Lopez",
        "country": "Venezuela",
        "mlbam_id": 641154,
    },
    {
        "name": "Martin Perez",
        "country": "Venezuela",
        "mlbam_id": 542583,
    },
    {
        "name": "Jesus Luzardo",
        "country": "Venezuela",
        "mlbam_id": 666200,
    },
    {
        "name": "Ranger Suarez",
        "country": "Venezuela",
        "mlbam_id": 624133,
    },
    {
        "name": "Carlos Carrasco",
        "country": "Venezuela",
        "mlbam_id": 471911,
    },


    # --------------------------------------------------------
    # CUBA
    # --------------------------------------------------------

    {
        "name": "Aroldis Chapman",
        "country": "Cuba",
        "mlbam_id": 547973,
    },
    {
        "name": "Raisel Iglesias",
        "country": "Cuba",
        "mlbam_id": 628452,
    },
    {
        "name": "Yariel Rodriguez",
        "country": "Cuba",
        "mlbam_id": 684320,
    },
    {
        "name": "Yennier Cano",
        "country": "Cuba",
        "mlbam_id": 666974,
    },
    {
        "name": "Johan Oviedo",
        "country": "Cuba",
        "mlbam_id": 670912,
    },
]


# ============================================================
# CREATE OUTPUT DIRECTORY
# ============================================================

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ============================================================
# DOWNLOAD STATCAST DATA
# ============================================================

all_data = []

print()
print("=" * 65)
print("MLB PITCH PREFERENCE BY NATIONALITY")
print("2025 REGULAR SEASON")
print("=" * 65)
print()

for i, pitcher in enumerate(pitchers, start=1):

    name = pitcher["name"]
    country = pitcher["country"]
    mlbam_id = pitcher["mlbam_id"]

    print(
        f"[{i:02d}/25] "
        f"{name} — {country}"
    )

    try:

        data = statcast_pitcher(
            START_DATE,
            END_DATE,
            mlbam_id
        )

        if data.empty:
            print("       WARNING: No data returned.")
            continue

        # Add our identifying information
        data["pitcher_name"] = name
        data["country"] = country

        all_data.append(data)

        print(
            f"       {len(data):,} pitches downloaded"
        )

    except Exception as e:

        print(
            f"       ERROR: {e}"
        )

    # Be polite to Baseball Savant
    time.sleep(2)


# ============================================================
# CHECK THAT DATA WAS DOWNLOADED
# ============================================================

if not all_data:

    raise RuntimeError(
        "No Statcast data was downloaded."
    )


# ============================================================
# COMBINE ALL PITCHERS
# ============================================================

df = pd.concat(
    all_data,
    ignore_index=True
)


# ============================================================
# KEEP VARIABLES WE NEED
# ============================================================

columns = [

    "pitcher_name",
    "country",

    "game_date",

    "pitch_type",
    "pitch_name",

    "release_speed",
    "release_spin_rate",

    "pfx_x",
    "pfx_z",

    "plate_x",
    "plate_z",

    "p_throws",
    "stand",

    "balls",
    "strikes",

    "description",

]


# Some Statcast versions may not contain every column,
# so only keep columns that exist.

columns = [
    column
    for column in columns
    if column in df.columns
]

df = df[columns]


# ============================================================
# SAVE RAW PITCH-LEVEL DATA
# ============================================================

df.to_csv(
    RAW_FILE,
    index=False
)


# ============================================================
# CREATE PITCH-TYPE SUMMARY
# ============================================================

summary = (
    df
    .groupby(
        [
            "country",
            "pitcher_name",
            "pitch_type",
            "pitch_name",
        ],
        dropna=False
    )
    .agg(
        pitches=("pitch_type", "size"),

        avg_velocity=(
            "release_speed",
            "mean"
        ),

        avg_spin=(
            "release_spin_rate",
            "mean"
        ),

        avg_horizontal_break=(
            "pfx_x",
            "mean"
        ),

        avg_vertical_break=(
            "pfx_z",
            "mean"
        ),
    )
    .reset_index()
)


# ============================================================
# CALCULATE PITCH USAGE %
# ============================================================

summary["usage_pct"] = (
    summary["pitches"]
    /
    summary.groupby(
        ["country", "pitcher_name"]
    )["pitches"].transform("sum")
    * 100
)


# ============================================================
# ROUND NUMBERS
# ============================================================

summary["usage_pct"] = (
    summary["usage_pct"]
    .round(2)
)

summary["avg_velocity"] = (
    summary["avg_velocity"]
    .round(2)
)

summary["avg_spin"] = (
    summary["avg_spin"]
    .round(0)
)

summary["avg_horizontal_break"] = (
    summary["avg_horizontal_break"]
    .round(2)
)

summary["avg_vertical_break"] = (
    summary["avg_vertical_break"]
    .round(2)
)


# ============================================================
# SORT SUMMARY
# ============================================================

summary = summary.sort_values(
    [
        "country",
        "pitcher_name",
        "usage_pct"
    ],
    ascending=[
        True,
        True,
        False
    ]
)


# ============================================================
# SAVE SUMMARY
# ============================================================

summary.to_csv(
    SUMMARY_FILE,
    index=False
)


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 65)
print("SUCCESS")
print("=" * 65)

print()
print(
    f"Total pitches downloaded: {len(df):,}"
)

print()
print("Pitches by country:")
print(
    df.groupby("country")
      .size()
      .sort_values(ascending=False)
)

print()
print("Pitchers successfully downloaded:")

successful = (
    df[["country", "pitcher_name"]]
    .drop_duplicates()
    .sort_values(
        ["country", "pitcher_name"]
    )
)

for country, group in successful.groupby("country"):

    print()
    print(f"{country}:")

    for name in group["pitcher_name"]:
        print(f"  ✓ {name}")


print()
print("Files created:")
print()
print(f"  {RAW_FILE}")
print(f"  {SUMMARY_FILE}")

print()
print("=" * 65)
