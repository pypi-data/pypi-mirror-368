import seaborn as sns
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def logbook_to_pandas(logbook):
    """
    Function to transform a deap logbook to a pandas dataframe.

    Parameters
    ----------
    logbook : deap.tools.Logbook
        The logbook to transform

    Returns
    -------
    df : pd.DataFrame
        The logbook as a pandas dataframe
    """
    data = logbook.chapters["parameters"]
    df = pd.DataFrame(data)
    return df



def plotly_logbook(logbook, population):
    """
    Generate a plot from the logbook with no additional points for "Max per Gen" and "Min per Gen".
    The population points grow based on the number of overlapping individuals.

    Parameters
    ----------
    logbook : deap.tools.Logbook
        The logbook to plot
    population : pd.DataFrame
        The population to plot

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The figure
    """
    df = pd.DataFrame(logbook)

    # Count the number of individuals that share the same (generation, fitness) coordinates
    population['count'] = population.groupby(['population', 'fitness'])['fitness'].transform('count')

    fig = go.Figure()

    # Avg line: Dashed, NO POINTS
    fig.add_trace(go.Scatter(x=df['gen'], y=df['avg'],
                             line=dict(color='rgb(50,130,250)', dash='dash', width=3),  # Soft blue, thicker line
                             mode='lines',  # No markers, just the line
                             name='Avg'))

    # Orange dashed line for the max value of each generation, NO POINTS
    fig.add_trace(go.Scatter(
        x=df['gen'], y=df['max'],
        line=dict(color='rgba(255,165,0,0.8)', dash='dash', width=2),  # Orange dashed line for gen-specific max
        mode='lines',  # No markers, just the line
        name='Max per Gen',
    ))

    # Red dashed line for the min value of each generation, NO POINTS
    fig.add_trace(go.Scatter(
        x=df['gen'], y=df['min'],
        line=dict(color='rgba(255,0,0,0.8)', dash='dash', width=2),  # Red dashed line for gen-specific min
        mode='lines',  # No markers, just the line
        name='Min per Gen',
    ))

    # Neutral gray dashed line for the overall max value
    fig.add_trace(go.Scatter(
        x=df['gen'],
        y=[df['max'].max()] * len(df['gen']),
        line=dict(color='rgba(100,100,100,0.8)', dash='dash', width=2),  # Neutral gray dashed line for overall max
        mode='lines',
        name='Max Overall',
    ))

    # Neutral gray dashed line for the overall min value
    fig.add_trace(go.Scatter(
        x=df['gen'],
        y=[df['min'].min()] * len(df['gen']),
        line=dict(color='rgba(100,100,100,0.8)', dash='dash', width=2),  # Neutral gray dashed line for overall min
        mode='lines',
        name='Min Overall',
    ))

    # Size of the points based on how many individuals share the same (generation, fitness) point
    max_point_size = 15  # Maximum size for the points
    population['scaled_size'] = (population['count'] / population['count'].max()) * max_point_size

    # Plot individuals with varying sizes (the only visible points)
    fig.add_trace(go.Scatter(
        x=population['population'], y=population['fitness'],
        name='Individuals',
        mode='markers',
        marker=dict(color='rgba(30,30,30,0.5)',
                    size=population['scaled_size'],  # Size proportional to the number of overlaps
                    sizemode='diameter',
                    line=dict(color='white', width=1)),  # Semi-transparent markers with white border
    ))

    # Layout improvements: clearer fonts, cleaner grid, and better spacing
    fig.update_layout(
        #title=dict(
        #    text='Fitness Evolution',
        #    x=0.5,  # Center the title
        #    xanchor='center',
        #    yanchor='top',
        #    font=dict(size=24, family='Arial, sans-serif'),  # Professional font
        #),
        xaxis=dict(
            title="Generation",
            tickmode='linear',
            tick0=0,
            dtick=1,
            linecolor='rgba(100,100,100,0.6)',  # Subtle axis line
            tickfont=dict(size=16, color='rgb(50,50,50)'),  # Larger, clearer ticks
            tickangle=-45,  # Rotate the x-axis labels for readability
            gridcolor='rgba(200,200,200,0.3)',  # Subtle grid lines for x-axis
        ),
        yaxis=dict(
            title="Fitness",
            linecolor='rgba(100,100,100,0.6)',  # Subtle axis line
            tickfont=dict(size=16, color='rgb(50,50,50)'),  # Larger, clearer ticks
            gridcolor='rgba(200,200,200,0.3)',  # Subtle grid lines for y-axis
        ),
        legend=dict(
            title="Fitness Metrics",
            font=dict(size=16, color='rgb(50,50,50)'),  # Clear legend title and items
            bordercolor='rgba(0,0,0,0.2)',
            borderwidth=1,
        ),
        font=dict(
            family="Arial, sans-serif",
            size=18,
            color="rgb(50,50,50)"
        ),
        plot_bgcolor='rgba(245,245,245,1)',  # Light gray background for better contrast
        margin=dict(l=50, r=50, t=50, b=100),  # Extra bottom margin for rotated labels
        width=900,  # Increased width for a better viewing experience
        height=600,  # Adjusted height for better aspect ratio
    )

    return fig


def plot_logbook(logbook):
    """
    Generate sns figure from logbook. Evolution of fitness and population.

    Parameters
    ----------
    logbook : deap.tools.Logbook
        The logbook to plot

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The figure
    """
    df = pd.DataFrame(logbook)
    g = sns.lineplot(df.drop(columns=['gen', 'nevals']))
    return g.get_figure()


def plotly_search_space(populations_df: pd.DataFrame, features: list = None, colorscale='Viridis'):
    """
    Generate a plotly figure from populations dataframe with improved axis labels, histograms, and centered correlation values.

    Parameters
    ----------
    populations_df : pd.DataFrame
        The dataframe with the population data
    features : list
        The features to plot (column names of the dataframe)
    colorscale : str
        The colorscale to use for the scatter plots

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The figure
    """
    if features is None:
        features = populations_df.columns.tolist()

    # Separate numeric and categorical features
    numeric_features = populations_df[features].select_dtypes(include='number').columns.tolist()
    categorical_features = [feat for feat in features if feat not in numeric_features]

    # Compute the correlation matrix only for numeric features
    corr_matrix = populations_df[numeric_features].corr()

    # Initialize subplots: lower triangle for scatter plots, upper triangle for correlations, diagonal for histograms
    fig = make_subplots(
        rows=len(features), cols=len(features),
        shared_xaxes=False, shared_yaxes=False,
        vertical_spacing=0.05, horizontal_spacing=0.05,
        subplot_titles=features
    )

    # Fill the subplots
    for i, feat_x in enumerate(features):
        for j, feat_y in enumerate(features):
            if i == j:  # Diagonal: Add histograms for feature distributions
                fig.add_trace(
                    go.Histogram(x=populations_df[feat_x], marker=dict(color='skyblue'),
                                 opacity=1, nbinsx=30),
                    row=i + 1, col=j + 1
                )

            elif i > j:  # Lower triangle: Scatter plots
                if feat_x in numeric_features and feat_y in numeric_features:
                    # Numeric scatter plot
                    fig.add_trace(
                        go.Scatter(
                            x=populations_df[feat_y], y=populations_df[feat_x],
                            mode='markers',
                            marker=dict(
                                color=populations_df['fitness'],
                                colorscale=colorscale,
                                opacity=0.5,
                                size=6,
                                coloraxis='coloraxis1'
                            ),
                            showlegend=False
                        ),
                        row=i + 1, col=j + 1
                    )
                elif feat_x in categorical_features or feat_y in categorical_features:
                    # Categorical scatter plot with fixed color and different symbols
                    fig.add_trace(
                        go.Scatter(
                            x=populations_df[feat_y], y=populations_df[feat_x],
                            mode='markers',
                            marker=dict(
                                color='grey',
                                opacity=0.5,
                                size=6,
                                symbol='circle'
                            ),
                            showlegend=False
                        ),
                        row=i + 1, col=j + 1
                    )

            elif i < j and feat_x in numeric_features and feat_y in numeric_features:  # Upper triangle: Correlation values
                corr_value = corr_matrix.loc[feat_x, feat_y]
                fig.add_trace(
                    go.Heatmap(
                        z=[[corr_value]],
                        colorscale="RdBu",
                        zmin=-1, zmax=1,
                        showscale=False,
                        xgap=1, ygap=1,
                        coloraxis='coloraxis2'
                    ),
                    row=i + 1, col=j + 1
                )
                fig.add_trace(
                    go.Scatter(
                        x=[0], y=[0],
                        text=[f'{corr_value:.2f}'],
                        mode='text',
                        textfont=dict(size=14, color='black', family='Arial', weight='bold'),
                        showlegend=False
                    ),
                    row=i + 1, col=j + 1
                )

    # Update layout
    fig.update_layout(
        height=1200,
        width=1200,
        showlegend=False,
        coloraxis1=dict(colorscale=colorscale, cmin=populations_df['fitness'].min(),
                        cmax=populations_df['fitness'].max(),
                        colorbar=dict(
                            title="Fitness",
                            thickness=15,
                            x=1.02,
                            y=0.5,
                            yanchor='middle'
                        )
                        ),
        coloraxis2=dict(colorscale="RdBu", cmin=-1, cmax=1,
                        colorbar=dict(
                            title="Correlation",
                            thickness=15,
                            x=1.1,
                            y=0.5,
                            yanchor='middle'
                        )
                        )
    )

    # Set consistent axis label fonts and tick parameters
    for i, feature in enumerate(features):
        # Subplot X-axis
        fig.update_xaxes(
            title_text=feature,
            row=len(features),
            col=i + 1,
            title_font=dict(size=16, family='Arial', color='black'),  # Title font settings
            title_standoff=20,
            tickangle=45,
            tickfont=dict(size=12, family='Arial', color='black'),  # Uniform tick font settings
            ticklen=5
        )
        # Subplot Y-axis
        fig.update_yaxes(
            title_text=feature,
            row=i + 1,
            col=1,
            title_font=dict(size=16, family='Arial', color='black'),  # Title font settings
            title_standoff=20,
            tickfont=dict(size=12, family='Arial', color='black'),  # Uniform tick font settings
            ticklen=5
        )

    # Remove x and y ticks from the correlation heatmaps (upper triangle)
    for i in range(len(features)):
        for j in range(len(features)):
            if i < j:
                fig.update_xaxes(showticklabels=False, row=i + 1, col=j + 1)
                fig.update_yaxes(showticklabels=False, row=i + 1, col=j + 1)

    return fig



def plot_search_space(populations_df: pd.DataFrame, height=2, s=25):
    """
    Generate sns figure from populations dataframe and features. Search space.

    Parameters
    ----------
    populations_df : pd.DataFrame
        The dataframe with the population
    height : int
        The height of the figure
    s : int
        The size of the points

    Returns
    -------
    fig : plotly.graph_objects.Figure
        The figure
    """
    sns.set_style("white")
    g = sns.PairGrid(populations_df, diag_sharey=False, height=height)
    g = g.map_upper(sns.scatterplot, s=s, color="r", alpha=0.2)
    g = g.map_lower(
        sns.kdeplot,
        shade=True,
        cmap=sns.color_palette("ch:s=.25,rot=-.25", as_cmap=True)
    )
    g = g.map_diag(sns.kdeplot, shade=True, palette="crest", alpha=0.2, color="red")
    return g
