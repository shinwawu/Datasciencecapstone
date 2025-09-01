# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df["Payload Mass (kg)"].max()
min_payload = spacex_df["Payload Mass (kg)"].min()

# ---- cria opções do dropdown (CORREÇÃO) ----
launch_sites = sorted(spacex_df["Launch Site"].unique())
site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": s, "value": s} for s in launch_sites
]

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": 40},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            placeholder="Select Launch Site",
            clearable=False,
            style={"width": "60%", "margin": "0 auto"},
        ),
        html.Br(),
        # TASK 2: Pie chart
        html.Div(dcc.Graph(id="success-pie-chart")),
        html.Br(),
        html.P("Payload range (Kg):"),
        # TASK 3: Range slider
        dcc.RangeSlider(
            id="payload-slider",
            min=int(min_payload),
            max=int(max_payload),
            step=1000,
            value=[int(min_payload), int(max_payload)],
            tooltip={"placement": "bottom", "always_visible": True},
            marks={
                int(min_payload): str(int(min_payload)),
                int((min_payload + max_payload) / 2): str(
                    int((min_payload + max_payload) / 2)
                ),
                int(max_payload): str(int(max_payload)),
            },
            allowCross=False,
        ),
        # TASK 4: Scatter chart
        html.Div(dcc.Graph(id="success-payload-scatter-chart")),
    ]
)


# TASK 2: callback do Pie Chart
@app.callback(Output("success-pie-chart", "figure"), Input("site-dropdown", "value"))
def update_pie(selected_site):
    if selected_site == "ALL":
        success_df = (
            spacex_df[spacex_df["class"] == 1]
            .groupby("Launch Site", as_index=False)["class"]
            .count()
            .rename(columns={"class": "Successes"})
        )
        fig = px.pie(
            success_df,
            values="Successes",
            names="Launch Site",
            title="Total Successful Launches by Site",
        )
        return fig
    else:
        site_df = spacex_df[spacex_df["Launch Site"] == selected_site]
        outcome_df = (
            site_df["class"]
            .value_counts()
            .rename_axis("Outcome")
            .reset_index(name="Count")
        )
        outcome_df["Outcome"] = outcome_df["Outcome"].map({1: "Success", 0: "Failure"})
        fig = px.pie(
            outcome_df,
            values="Count",
            names="Outcome",
            title=f"Success vs Failure for {selected_site}",
        )
        return fig


# TASK 4: callback do Scatter
@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    [Input("site-dropdown", "value"), Input("payload-slider", "value")],
)
def update_scatter(selected_site, payload_range):
    low, high = payload_range
    filtered_df = spacex_df[
        (spacex_df["Payload Mass (kg)"] >= low)
        & (spacex_df["Payload Mass (kg)"] <= high)
    ]
    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df["Launch Site"] == selected_site]

    color_col = (
        "Booster Version Category"
        if "Booster Version Category" in filtered_df.columns
        else ("Booster Version" if "Booster Version" in filtered_df.columns else None)
    )

    fig = px.scatter(
        filtered_df,
        x="Payload Mass (kg)",
        y="class",
        color=color_col,
        hover_data=["Launch Site"] + ([color_col] if color_col else []),
        title=(
            "Correlation between Payload and Success"
            if selected_site == "ALL"
            else f"Payload vs Success for {selected_site}"
        ),
    )
    fig.update_yaxes(
        tickmode="array", tickvals=[0, 1], ticktext=["Failure (0)", "Success (1)"]
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
