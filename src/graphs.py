import plotly.express as px
import plotly.colors as pc
import plotly.graph_objects as go
import pandas as pd

# Resources:
# color codes: https://htmlcolorcodes.com/
# plotly choropleth layout geo: https://plotly.com/python/reference/layout/geo/
# plotly choropleth map configuration: https://plotly.com/python/map-configuration/
# plotly builtin color scales: https://plotly.com/python/builtin-colorscales/

def adjust_color(color, factor):
    """Lighten (>1) or darken (<1) a hex color.
    RGB values need to be between 0 and 255
    """
    r, g, b = pc.hex_to_rgb(color)
    r = max(0, min(255, int(r * factor)))
    g = max(0, min(255, int(g * factor)))
    b = max(0, min(255, int(b * factor)))
    return "#{:02x}{:02x}{:02x}".format(r, g, b) # return as hex format

def show_colorscale(base_color):
    """Display generated 3-step colorscale for a single base color."""
    colors = [
        adjust_color(base_color, 1.5),  # lighter
        base_color,                     # original
        adjust_color(base_color, 0.5)   # darker
    ]

    fig = go.Figure(
        data=[go.Heatmap(
            z=[list(range(len(colors)))],
            colorscale=[[i/(len(colors)-1), c] for i, c in enumerate(colors)],
            showscale=False
        )]
    )
    fig.update_layout(
        title=f"Generated scale for {base_color}",
        xaxis=dict(showticklabels=False),
        yaxis=dict(showticklabels=False)
    )
    fig.show()


def plot_bar(df, x_col, y_col, title="", orientation="h", top_n=None
             , color="#FFA500", height=500, width=800, order_axis=False):
    """
    Create a styled Plotly bar chart for Streamlit dashboards.
    It handles horizontal and vertical bar charts, custom ordering, coloring,
    and label formatting to match a dark theme.

    Parameters:
    - df: pandas DataFrame
    - x_col: column name for numeric values for x-axis values
    - y_col: column name for categorical labels for y-axis labels
    - title: chart title
    - orientation: "h" (horizontal) or "v" (vertical)
    - top_n: If provided, only the top N rows (by `x_col` or `y_col`) will be shown
    - color: a single hex color for all bars, or a list of color hex codes to create a gradient (continuous scale)
    - height, width: chart size in pixels
    - order_axis: Whether to order the axis by the values rather than the default category order.
        For horizontal bars: sorts descending (largest at top). If false, order by labels
        For vertical bars: sorts ascending. If false, order by labels
    """
    plot_df = df.copy()

    # -- Filter top N rows if requested --
    if top_n:
        # for horizontal bars: top N by x_col
        if orientation == "h":
            plot_df = plot_df.nlargest(top_n, x_col)
        # for vertical bars: Top N by y_col
        else:
            plot_df = plot_df.nlargest(top_n, y_col)

    # -- Sort axis if requested --
    if order_axis:
        # for horizontal bars: sort descending so largest bars are at the top
        if orientation == "h":
            plot_df = plot_df.sort_values(by=x_col, ascending=False)
        # for vertical bars: sort ascending (useful for chronological data like years)
        else:
            plot_df = plot_df.sort_values(by=x_col, ascending=True)

    # --- decide color mode ---
    is_gradient = isinstance(color, (list, tuple))
    # for gradient, pick numeric column to map colors to
    color_arg = None
    color_continuous_scale = None
    color_discrete_sequence = None

    if is_gradient:
        # Which numeric column to map to depends on orientation
        color_arg = x_col if orientation == "h" else y_col
        color_continuous_scale = list(color)
        # ensure numeric column is numeric to avoid issues
        # (attempt to coerce if possible)
        try:
            plot_df[color_arg] = pd.to_numeric(plot_df[color_arg], errors="coerce")
        except Exception:
            pass
    else:
        color_discrete_sequence = [color]

    # -- Create bar chart --
    if orientation == "h":
        fig = px.bar(
            plot_df,
            x=x_col,    # numeric values (length of bars)
            y=y_col,    # categories
            text=x_col, # show values on bars
            orientation="h",
            title=title,
            color=color_arg,
            color_continuous_scale=color_continuous_scale,
            color_discrete_sequence=color_discrete_sequence
            #color_discrete_sequence=[color] if isinstance(color, str) else None,    # single color
            #color_continuous_scale=color if isinstance(color, list) else None       # gradient color
        )
    else:
        fig = px.bar(
            plot_df,
            x=x_col,    # categories (like years)
            y=y_col,    # numeric values
            text=y_col, # show values on bars
            orientation="v",
            title = title,
            color=color_arg,
            color_continuous_scale=color_continuous_scale,
            color_discrete_sequence=color_discrete_sequence
            #color_discrete_sequence=[color] if isinstance(color, str) else None,    # single color
            #color_continuous_scale=color if isinstance(color, list) else None       # gradient color
        )

    # -- style bar labels --
    fig.update_traces(
        textposition="outside",         # place labels outside bars
        textfont_color="#f0f0f0",       # light labels (for dark background)
        cliponaxis=False               # allow labels to overflow plot area if needed
    )

    fig.update_layout(
        plot_bgcolor="#1e1e1e",     # dark grey background (plot area)
        paper_bgcolor="#1e1e1e",    # dark grey background (outer area)
        font_color="#f0f0f0",       # light text
        title_font_color="#f0f0f0", # lgith title
        yaxis={'categoryorder': 'total ascending'} if orientation == "h" else None, # largest bars at top
        xaxis={'categoryorder': 'total ascending'} if orientation == "v" and order_axis else None,
        width=width,
        height=height,
        margin=dict(l=150 if orientation=="h" else 60,  # wide left margin for horizontal labels
                    r=40, t=60, b=60),
        coloraxis_showscale=False   # do not show the color bar
    )
    return fig

def plot_map(df, country_col, y_col, title="", color=None):
    """
    Plot a choropleth map.

    Args:
        df (pd.DataFrame): DataFrame with data.
        country_col (str): Column with country names.
        y_col (str): Column with values.
        title (str): Figure title.
        color (str | list | None): Color specification:
            - None -> default 3-color scale
            - str (hex or named) -> used as middle color, fading from `base_min`
            - list of colors -> used as full scale
            - Plotly built-in name (e.g., 'Viridis')
    """

    if color is None:
        color = ["#FFD580", "#FFA500", "#FF7F00"]

    # If user provides a single color string, turn it into a 2-color scale
    elif (isinstance(color, str)
          and color.startswith("#") and len(color) in [4, 7]
          and not color.lower() in px.colors.named_colorscales()):
        # Single custom color → make a 3-step scale (light, base, dark)
        color = [
            adjust_color(color, 0.75),  # darker version
            color,  # base
            adjust_color(color, 1.25),  # lighter version

        ]

    plot_df = df.copy()

    fig_map = px.choropleth(
        plot_df,
        locations=country_col,
        locationmode="country names",
        color=y_col,
        hover_name="Country",
        color_continuous_scale=color,
        title=title
    )

    fig_map.update_layout(
        plot_bgcolor="#1e1e1e",  # background of plotting area outside of map
        paper_bgcolor="#1e1e1e",  # background of entire figure canvas
        font_color="#f0f0f0",  # default text color
        title_font_color="#f0f0f0",  # title text color
        geo=dict(bgcolor="#1e1e1e"),  # map background color (oceans)
        margin=dict(l=0, r=0, t=50, b=0),  # padding around figure
        coloraxis_showscale=False  # hide  color bar
    )

    # define border color of countries with values
    fig_map.update_traces(
        marker=dict(line=dict(color="#1e1e1e", width=0.5))
    )

    # show all countries without data
    fig_map.update_geos(
        showland=True,  # show land layer for missing countries
        landcolor="#333333",  # define color of missing countries
        lakecolor= "#1e1e1e",       # define color of lakes
        showcoastlines=True,  # show coastlines of continents
        coastlinecolor="#1e1e1e",  # define color of coastlines
        showcountries=True,  # shows borders between all countries
        countrycolor="#1e1e1e",  # define color of the border of  countries
        projection_type="equirectangular"
    )

    return fig_map

# -----------------------------
# Test code
# -----------------------------
# Only runs when the file is executed directly, not when imported
if __name__ == "__main__":

    base_color = "#FFA500"
    #show_colorscale(base_color)

    # set colors
    orange = "#FFA500"
    orange_gradient = ["#FFCC66", "#FFA500", "#FF8800"]
    blue = "#1E90FF"
    blue_gradient = ["#66B2FF",  "#1E90FF", "#125E99"]
    green = "#2BA42B"
    green_gradient = ["#70D070", "#2BA42B", "#238C23"]

    # --- Map ---
    map_df = pd.DataFrame({
        'Country': ['USA', 'Canada', 'Brazil'],
        'Count': [10, 20, 40]  # all other countries missing
    })

    # 1. Use default custom list
    fig_map = plot_map(map_df,
                       country_col="Country",
                       y_col="Count",
                       title="1. Default Colors")
    fig_map.show()

    # 2. Use prespecified gradient
    fig_map = plot_map(map_df
                       , country_col='Country'
                       , y_col='Count'
                       , color=green_gradient
                       , title="2. predefined gradient")
    fig_map.show()

    # 3. Use single color:
    fig_map = plot_map(map_df
                       , country_col='Country'
                       , y_col='Count'
                       , color=green
                       , title="3. Single green input"
                       )
    fig_map.show()

    # 4. Use a built-in Plotly scale
    fig_map = plot_map(map_df,
                       country_col="Country",
                       y_col="Count",
                       color="Blues",
                       title="4. Blues")
    fig_map.show()

    # 5. Use a colorname as string: should throw error
    #fig_map = plot_map(map_df
    #                   , country_col='Country'
    #                   , y_col='Count'
    #                   , color="orange"
    #                   , title="5. Name of color"
    #                   )
    #fig_map.show()

    # --- Bar Charts ---

    # Example dataset
    data = {
        "Category": ["A", "B", "C", "D", "E"],
        "Value": [10, 23, 7, 15, 30]
    }
    df = pd.DataFrame(data)



    # --- Horizontal bar chart test ---
    fig_h = plot_bar(
        df,
        x_col="Value",
        y_col="Category",
        title="Horizontal Bar Chart (Top 5)",
        orientation="h",
        top_n=5,
        order_axis=True,
        color=green
    )
    fig_h.show()

    # --- Vertical bar chart test ---
    fig_v = plot_bar(
        df,
        x_col="Category",
        y_col="Value",
        title="Vertical Bar Chart (Top 5)",
        orientation="v",
        #top_n=5,
        order_axis=False,
        color=green
    )
    fig_v.show()

    # --- Vertical bar chart with gradient color scale ---
    fig_grad = plot_bar(
        df,
        x_col="Category",
        y_col="Value",
        title="Vertical Bar Chart (Gradient)",
        orientation="v",
        order_axis=True,
        color=blue_gradient
    )
    fig_grad.show()

    # --- Vertical bar chart with gradient color scale ---
    fig_grad = plot_bar(
        df,
        x_col="Category",
        y_col="Value",
        title="Vertical Bar Chart (Gradient)",
        orientation="v",
        order_axis=True,
        color=orange_gradient
    )
    fig_grad.show()

