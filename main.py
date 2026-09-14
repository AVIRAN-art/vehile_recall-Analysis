import requests
import pandas as pd
import streamlit as st
import seaborn as sns
st.set_page_config(
    page_title="Vehicle Recall Analysis",
    layout="wide"
)

st.title("Vehicle Recall Analysis")

st.subheader("Created by Aviran Hainhorn")

st.write(
    "Comparison of unique recall campaigns for selected SUV models, "
    "model years 2021–2025"
)
import matplotlib.pyplot as plt

vehicles = [
    {"make": "BMW", "model": "X5"},
    {"make": "Toyota", "model": "Highlander"},
    {"make": "Ford", "model": "Explorer"}
]
years = range(2021, 2026)

all_recalls = []

base_url = "https://api.nhtsa.gov/recalls/recallsByVehicle"

for vehicle in vehicles:

    for year in years:

        request_parameters = {
            "make": vehicle["make"],
            "model": vehicle["model"],
            "modelYear": year
        }

        response = requests.get(
            base_url,
            params=request_parameters
        )

        recall_data = response.json()

        all_recalls.extend(
            recall_data["results"]
        )

        print(
            vehicle["make"],
            vehicle["model"],
            year,
            "status:", response.status_code,
            "records:", recall_data["Count"]
        )
    print("כמות רשומות:", len(all_recalls))

recalls_df = pd.DataFrame(all_recalls)
print("מבנה הטבלה:", recalls_df.shape)
print(recalls_df.columns.tolist())
print(recalls_df.head())

research_columns = [
    "Make",
    "Model",
    "ModelYear",
    "NHTSACampaignNumber"
]
research_df = recalls_df[research_columns].copy()

print("כמות רשומות:",research_df.shape[0])
print("כמות עמודות:",research_df.shape[1])
print(research_df.head())


recalls_by_model = (
    research_df
    .groupby(["Make", "Model"])
    ["NHTSACampaignNumber"]
    .nunique()
)
recalls_by_model_df = recalls_by_model.reset_index()

recalls_by_model_df = recalls_by_model_df.rename(
    columns={
        "NHTSACampaignNumber": "UniqueRecalls"
    }
)
print(recalls_by_model_df)


recalls_by_year = (
    research_df
    .groupby(["Make", "Model", "ModelYear"])
    ["NHTSACampaignNumber"]
    .nunique()
)
recalls_by_year_df = recalls_by_year.reset_index()
recalls_by_year_df = recalls_by_year_df.rename(
    columns={
        "NHTSACampaignNumber": "UniqueRecalls"
    }
)
print(recalls_by_year_df)

st.subheader("Unique Recall Campaigns by Vehicle Model")

st.dataframe(
    recalls_by_model_df,
    hide_index=True,
    use_container_width=True
)

fig1 = plt.figure(figsize=(10, 5))

sns.barplot(
    data=recalls_by_model_df,
    x="Model",
    y="UniqueRecalls",
    hue="Make",
    errorbar=None
)

plt.title("Unique Recall Campaigns by SUV Model")
plt.xlabel("Vehicle Model")
plt.ylabel("Number of Unique Recall Campaigns")
plt.tight_layout()

st.pyplot(fig1)

st.subheader("Unique Recall Campaigns by Model Year")

fig2 = plt.figure(figsize=(10, 5))

sns.lineplot(
    data=recalls_by_year_df,
    x="ModelYear",
    y="UniqueRecalls",
    hue="Model",
    marker="o"
)

plt.title("Unique Recall Campaigns by Model Year")
plt.xlabel("Model Year")
plt.ylabel("Number of Unique Recall Campaigns")
plt.tight_layout()

st.pyplot(fig2)

st.subheader("Key Findings")



st.subheader("Key Findings")

st.subheader("Key Findings")

st.write(
    """
    - Ford Explorer had the highest number of unique recall campaigns: 52.
    - BMW X5 had 25 unique recall campaigns.
    - Toyota Highlander had the lowest number: 12.
    - Ford Explorer had the highest yearly count in every model year examined.
    - Recall campaigns may affect more than one model year, so yearly counts
      should not be added together to calculate the overall unique total.
    """
)

st.subheader("Explore a Vehicle Model")

selected_model = st.selectbox(
    "Choose a vehicle model:",
    recalls_by_year_df["Model"].unique()
)

selected_model_df = recalls_by_year_df[
    recalls_by_year_df["Model"] == selected_model
]

st.dataframe(
    selected_model_df,
    hide_index=True,
    width="stretch"
)

st.line_chart(
    selected_model_df,
    x="ModelYear",
    y="UniqueRecalls"
)

st.subheader("Campaigns Affecting Multiple Model Years")

st.write(
    "This analysis examines how many recall campaigns affected "
    "more than one model year."
)

# Count how many model years are affected by each campaign
campaign_year_counts_df = (
    research_df
    .groupby([
        "Make",
        "Model",
        "NHTSACampaignNumber"
    ])
    ["ModelYear"]
    .nunique()
    .reset_index(name="AffectedModelYears")
)

# Mark campaigns that affect more than one model year
campaign_year_counts_df["IsMultiYear"] = (
    campaign_year_counts_df["AffectedModelYears"] > 1
)

# Create a summary for each vehicle model
multi_year_summary_df = (
    campaign_year_counts_df
    .groupby(["Make", "Model"])
    .agg(
        TotalUniqueCampaigns=(
            "NHTSACampaignNumber",
            "nunique"
        ),
        MultiYearCampaigns=(
            "IsMultiYear",
            "sum"
        ),
        MultiYearShare=(
            "IsMultiYear",
            "mean"
        )
    )
    .reset_index()
)

# Convert the share to percentage
multi_year_summary_df["MultiYearShare"] = (
    multi_year_summary_df["MultiYearShare"] * 100
).round(0)

# Create a display copy with clearer column names
multi_year_display_df = multi_year_summary_df.copy()

multi_year_display_df = multi_year_display_df.rename(
    columns={
        "Make": "Make",
        "Model": "Model",
        "TotalUniqueCampaigns": "Total Unique Campaigns",
        "MultiYearCampaigns": "Multi-Year Campaigns",
        "MultiYearShare": "Multi-Year Campaign Share"
    }
)

# Add the percentage symbol for the displayed table
multi_year_display_df["Multi-Year Campaign Share"] = (
    multi_year_display_df["Multi-Year Campaign Share"]
    .astype(int)
    .astype(str)
    + "%"
)

st.dataframe(
    multi_year_display_df,
    hide_index=True,
    width="stretch"
)

# Create a chart
fig3 = plt.figure(figsize=(10, 5))

sns.barplot(
    data=multi_year_summary_df,
    x="Model",
    y="MultiYearShare",
    hue="Make",
    errorbar=None
)

plt.title("Share of Campaigns Affecting Multiple Model Years")
plt.xlabel("Vehicle Model")
plt.ylabel("Multi-Year Campaign Share (%)")
plt.ylim(0, 100)
plt.tight_layout()

st.pyplot(fig3)

st.write(
    """
    Toyota Highlander had the lowest total number of unique recall
    campaigns, but the highest proportion of campaigns affecting
    multiple model years.

    This suggests that Toyota's smaller group of recall campaigns
    tended to cover a broader range of the selected model years.
    This does not necessarily indicate greater severity or lower
    vehicle safety.
    """
)