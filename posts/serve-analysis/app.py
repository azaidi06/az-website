"""Streamlit dashboard for tennis serve analysis."""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

from serve_utils import (
    calculate_ace_stats, calculate_1st_serve_stats, calculate_bp_stats,
    create_scatter_with_filters, calc_tour_averages, prepare_serve_features,
    calculate_recent_vs_career, serve_by_surface, player_surface_stats,
    calc_predictive, filter_by_date_range, calculate_player_comparison,
    calculate_trend_stats
)

# Scatter tab configuration for generic rendering
SCATTER_TAB_CONFIG = {
    'ace': {
        'header': 'Ace Production: Risk vs Reward',
        'caption': 'Big servers hit more aces but often double fault more too.',
        'stat_cols': ['Ace Rate %', 'DF Rate %'],
        'stat_labels': {'Ace Rate %': 'Ace Rate', 'DF Rate %': 'DF Rate'},
        'stats_key': 'ace',
        'x_col': 'Ace Rate %',
        'y_col': 'DF Rate %',
        'x_label': 'Ace Rate %',
        'y_label': 'Double Fault Rate %',
        'trend_type': 'ace',
    },
    '1st': {
        'header': 'First Serve: Accuracy vs Effectiveness',
        'caption': 'Getting the first serve in is important, but winning the point matters more.',
        'stat_cols': ['1st Serve %', '1st Serve Won %'],
        'stat_labels': {'1st Serve %': '1st Serve In', '1st Serve Won %': '1st Serve Won'},
        'stats_key': '1st',
        'x_col': '1st Serve %',
        'y_col': '1st Serve Won %',
        'x_label': '1st Serve In %',
        'y_label': '1st Serve Won %',
        'trend_type': '1st',
    },
    'bp': {
        'header': 'Break Point Performance',
        'caption': 'Clutch players both save break points on serve and convert them on return.',
        'stat_cols': ['BP Save %', 'BP Convert %'],
        'stat_labels': {'BP Save %': 'Break Point Save', 'BP Convert %': 'Break Point Convert'},
        'stats_key': 'bp',
        'x_col': 'BP Save %',
        'y_col': 'BP Convert %',
        'x_label': 'Break Point Save %',
        'y_label': 'Break Point Convert %',
        'trend_type': 'bp',
    },
}

# Page config
st.set_page_config(
    page_title="Tennis Serve Analysis",
    page_icon="🎾",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: bold; }
    .metric-label { font-size: 0.9rem; opacity: 0.9; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_data():
    """Load and preprocess ATP and WTA data."""
    DATA_PATH = '../../data/top25'

    atp_players = pd.read_csv(f'{DATA_PATH}/atp/atp_top25_players.csv')
    atp_matches = pd.read_csv(f'{DATA_PATH}/atp/atp_top25_matches.csv')
    wta_players = pd.read_csv(f'{DATA_PATH}/wta/wta_top25_players.csv')
    wta_matches = pd.read_csv(f'{DATA_PATH}/wta/wta_top25_matches.csv')

    # Load rankings to get actual current rankings
    atp_rankings = pd.read_csv(f'{DATA_PATH}/atp/atp_top25_rankings.csv')
    wta_rankings = pd.read_csv(f'{DATA_PATH}/wta/wta_top25_rankings.csv')

    # Get most recent ranking for each player
    latest_atp_date = atp_rankings['ranking_date'].max()
    latest_wta_date = wta_rankings['ranking_date'].max()
    latest_atp = atp_rankings[atp_rankings['ranking_date'] == latest_atp_date][['player', 'rank']]
    latest_wta = wta_rankings[wta_rankings['ranking_date'] == latest_wta_date][['player', 'rank']]

    # Process player names
    for df in [atp_players, wta_players]:
        df['full_name'] = df['name_first'] + ' ' + df['name_last']

    # Merge with rankings to get actual ranks
    atp_players = atp_players.merge(latest_atp, left_on='player_id', right_on='player', how='left')
    wta_players = wta_players.merge(latest_wta, left_on='player_id', right_on='player', how='left')
    atp_players.drop(columns=['player'], inplace=True)
    wta_players.drop(columns=['player'], inplace=True)

    atp_players['tour'], wta_players['tour'] = 'ATP', 'WTA'
    atp_matches['tour'], wta_matches['tour'] = 'ATP', 'WTA'

    # Parse dates
    atp_matches['tourney_date'] = pd.to_datetime(atp_matches['tourney_date'].astype(str), format='%Y%m%d')
    wta_matches['tourney_date'] = pd.to_datetime(wta_matches['tourney_date'].astype(str), format='%Y%m%d')

    # Filter to matches with serve data
    serve_cols = ['w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced']
    atp_serve_matches = atp_matches.dropna(subset=serve_cols)
    wta_serve_matches = wta_matches.dropna(subset=serve_cols)

    return {
        'atp_players': atp_players,
        'wta_players': wta_players,
        'atp_matches': atp_serve_matches,
        'wta_matches': wta_serve_matches,
    }


@st.cache_data
def compute_all_stats(atp_matches, wta_matches, atp_players, wta_players,
                      start_date=None, end_date=None):
    """Compute all stats for both tours."""
    # Ace stats
    atp_ace = calculate_ace_stats(atp_matches, atp_players, start_date, end_date)
    wta_ace = calculate_ace_stats(wta_matches, wta_players, start_date, end_date)

    # First serve stats
    atp_1st = calculate_1st_serve_stats(atp_matches, atp_players, start_date, end_date)
    wta_1st = calculate_1st_serve_stats(wta_matches, wta_players, start_date, end_date)

    # Break point stats
    atp_bp = calculate_bp_stats(atp_matches, atp_players, start_date, end_date)
    wta_bp = calculate_bp_stats(wta_matches, wta_players, start_date, end_date)

    # Common players (those with data in all charts)
    atp_common = set(atp_ace['Player']) & set(atp_1st['Player']) & set(atp_bp['Player'])
    wta_common = set(wta_ace['Player']) & set(wta_1st['Player']) & set(wta_bp['Player'])

    # Filter to common players
    atp_ace = atp_ace[atp_ace['Player'].isin(atp_common)].sort_values('Rank').reset_index(drop=True)
    atp_1st = atp_1st[atp_1st['Player'].isin(atp_common)].sort_values('Rank').reset_index(drop=True)
    atp_bp = atp_bp[atp_bp['Player'].isin(atp_common)].sort_values('Rank').reset_index(drop=True)
    wta_ace = wta_ace[wta_ace['Player'].isin(wta_common)].sort_values('Rank').reset_index(drop=True)
    wta_1st = wta_1st[wta_1st['Player'].isin(wta_common)].sort_values('Rank').reset_index(drop=True)
    wta_bp = wta_bp[wta_bp['Player'].isin(wta_common)].sort_values('Rank').reset_index(drop=True)

    # Recent form
    atp_form = calculate_recent_vs_career(atp_matches, atp_players, start_date=start_date, end_date=end_date).head(15)
    wta_form = calculate_recent_vs_career(wta_matches, wta_players, start_date=start_date, end_date=end_date).head(15)

    # Surface stats
    atp_surf = serve_by_surface(atp_matches, start_date, end_date)
    wta_surf = serve_by_surface(wta_matches, start_date, end_date)
    atp_surface_stats = player_surface_stats(atp_matches, atp_players, start_date, end_date)
    wta_surface_stats = player_surface_stats(wta_matches, wta_players, start_date, end_date)

    # Predictive stats
    atp_pred = calc_predictive(atp_matches, start_date, end_date)
    wta_pred = calc_predictive(wta_matches, start_date, end_date)

    return {
        'atp_ace': atp_ace, 'wta_ace': wta_ace,
        'atp_1st': atp_1st, 'wta_1st': wta_1st,
        'atp_bp': atp_bp, 'wta_bp': wta_bp,
        'atp_common': atp_common, 'wta_common': wta_common,
        'atp_form': atp_form, 'wta_form': wta_form,
        'atp_surf': atp_surf, 'wta_surf': wta_surf,
        'atp_surface_stats': atp_surface_stats, 'wta_surface_stats': wta_surface_stats,
        'atp_pred': atp_pred, 'wta_pred': wta_pred,
    }


def filter_by_surface(matches, surfaces):
    """Filter matches by selected surfaces."""
    if not surfaces or 'All' in surfaces:
        return matches
    return matches[matches['surface'].isin(surfaces)]


def filter_stats_by_players(stats_df, selected_players):
    """Filter stats dataframe by selected players."""
    if not selected_players:
        return stats_df
    return stats_df[stats_df['Player'].isin(selected_players)]


# =============================================================================
# Visualization Functions
# =============================================================================

def generate_player_analysis(player_name, comparison, trend_data, stat_type):
    """Generate dynamic text analysis for highlighted player."""
    if not comparison:
        return None

    insights = []
    strengths = []
    weaknesses = []

    for stat_key, stat_data in comparison['stats'].items():
        delta = stat_data['delta']
        value = stat_data['value']
        label = stat_key.replace(' %', '')

        if abs(delta) > 1.5:  # Notable difference
            insights.append(f"{label}: {value}% ({delta:+.1f} vs group avg)")

            # Track for summary
            is_good = stat_data['better']
            if is_good:
                strengths.append(label.lower())
            else:
                weaknesses.append(label.lower())

    # Add trend insight if available
    if trend_data:
        x_change = trend_data['recent']['x'] - trend_data['earlier']['x']
        y_change = trend_data['recent']['y'] - trend_data['earlier']['y']
        if abs(x_change) > 1.5 or abs(y_change) > 1.5:
            trend_dir = "improving" if (x_change > 0 or y_change > 0) else "declining"
            insights.append(f"Trend: {trend_dir} over the last year")

    # Generate summary sentence
    summary = None
    if strengths and not weaknesses:
        summary = f"{player_name} excels in {' and '.join(strengths)} compared to peers."
    elif weaknesses and not strengths:
        summary = f"{player_name} has room to improve in {' and '.join(weaknesses)}."
    elif strengths and weaknesses:
        summary = f"{player_name} stands out for {strengths[0]}, though {weaknesses[0]} lags behind."

    return {'bullets': insights, 'summary': summary}


def render_comparison_card(comparison, stat_labels):
    """Render a comparison card showing highlighted player vs group average."""
    if not comparison:
        return

    cols = st.columns(len(comparison['stats']))
    for i, (stat_key, stat_data) in enumerate(comparison['stats'].items()):
        label = stat_labels.get(stat_key, stat_key)
        delta_color = 'green' if stat_data['better'] else 'red'
        delta_sign = '+' if stat_data['delta'] > 0 else ''

        with cols[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
                        padding: 0.8rem; border-radius: 8px; text-align: center;
                        border-left: 4px solid {delta_color};">
                <div style="font-size: 0.75rem; color: #666;">{label}</div>
                <div style="font-size: 1.4rem; font-weight: bold;">{stat_data['value']}%</div>
                <div style="font-size: 0.8rem; color: {delta_color};">
                    {delta_sign}{stat_data['delta']}% vs avg ({stat_data['avg']}%)
                </div>
            </div>
            """, unsafe_allow_html=True)


def create_filtered_scatter(df, color, x_col, y_col, x_label, y_label,
                            highlight_player=None, trend_data=None, comparison=None):
    """Create scatter plot with optional highlighting, trend arrows, and annotations."""
    fig = go.Figure()

    # Calculate group average for annotations
    x_avg = df[x_col].mean() if len(df) > 0 else 0
    y_avg = df[y_col].mean() if len(df) > 0 else 0

    for _, row in df.iterrows():
        is_highlighted = highlight_player and row['Player'] == highlight_player
        marker = dict(
            size=16 if is_highlighted else 12,
            color='gold' if is_highlighted else color,
            line=dict(color='darkred', width=3) if is_highlighted else None
        )
        fig.add_trace(go.Scatter(
            x=[row[x_col]], y=[row[y_col]],
            mode='markers+text',
            text=[row['Player']], textposition='top center',
            textfont=dict(size=11 if is_highlighted else 9, color='darkred' if is_highlighted else None),
            marker=marker,
            name=row['Player'],
            hovertemplate=f"{row['Player']} (#{row['Rank']})<br>{x_label}: %{{x}}<br>{y_label}: %{{y}}<extra></extra>"
        ))

    # Add trend arrow for highlighted player (earlier -> recent)
    if trend_data and highlight_player:
        # Earlier point (faded)
        fig.add_trace(go.Scatter(
            x=[trend_data['earlier']['x']],
            y=[trend_data['earlier']['y']],
            mode='markers',
            marker=dict(size=14, color='gold', opacity=0.4,
                       line=dict(color='darkred', width=2)),
            name=f'{highlight_player} (Earlier)',
            hovertemplate=f"{highlight_player} Earlier<br>{x_label}: %{{x}}<br>{y_label}: %{{y}}<br>({trend_data['earlier']['n_matches']} matches)<extra></extra>",
            showlegend=False
        ))

        # Arrow from earlier to recent
        fig.add_annotation(
            x=trend_data['recent']['x'],
            y=trend_data['recent']['y'],
            ax=trend_data['earlier']['x'],
            ay=trend_data['earlier']['y'],
            xref='x', yref='y',
            axref='x', ayref='y',
            showarrow=True,
            arrowhead=2,
            arrowsize=1.5,
            arrowwidth=2,
            arrowcolor='darkred',
            opacity=0.7
        )

        # Label for the trend
        fig.add_annotation(
            x=trend_data['earlier']['x'],
            y=trend_data['earlier']['y'],
            text="1yr ago",
            showarrow=False,
            yshift=-15,
            font=dict(size=9, color='gray')
        )

    fig.update_layout(
        showlegend=False,
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=450,
        margin=dict(t=40, r=20)
    )

    # Add average reference lines
    if len(df) > 0:
        fig.add_hline(y=y_avg, line_dash='dash', line_color='gray', opacity=0.5)
        fig.add_vline(x=x_avg, line_dash='dash', line_color='gray', opacity=0.5)

    return fig


def render_overview_tab(data, stats, tour_filter, start_date=None, end_date=None):
    """Render the Overview tab."""
    st.header("Tour Averages")

    # Check if we have match data
    matches = filter_by_date_range(data[f'{tour_filter.lower()}_matches'], start_date, end_date)
    if matches.empty:
        st.warning("No match data available for the selected time period.")
        return

    # Calculate tour averages for selected tour
    tour_avg = calc_tour_averages(data[f'{tour_filter.lower()}_matches'], start_date, end_date)

    # Display metrics
    st.subheader(f"{tour_filter} Tour Averages")
    cols = st.columns(4)
    for i, (metric, val) in enumerate(tour_avg.items()):
        cols[i].metric(metric, f"{val:.1f}")

    # Bar chart
    st.subheader("Tour Statistics")
    fig = go.Figure()
    metrics = list(tour_avg.keys())
    color = '#1f77b4' if tour_filter == 'ATP' else '#e377c2'

    fig.add_trace(go.Bar(
        name=tour_filter, x=metrics, y=list(tour_avg.values()),
        marker_color=color,
        text=[f'{v:.1f}' for v in tour_avg.values()], textposition='outside'
    ))

    fig.update_layout(
        height=400, yaxis_title='Value',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # Winner vs Loser Differentials
    st.subheader("Winner vs Loser Differentials")
    st.caption("How much better do winners serve than losers?")

    features = prepare_serve_features(data[f'{tour_filter.lower()}_matches'], start_date, end_date)

    diff_cols = ['diff_1st_pct', 'diff_1st_won', 'diff_2nd_won', 'diff_bp_save', 'diff_ace_rate']
    diff_labels = ['1st In %', '1st Won %', '2nd Won %', 'BP Save %', 'Ace Rate']

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=tour_filter, x=diff_labels, y=features[diff_cols].mean().values,
        marker_color=color,
        text=[f'+{v:.1f}' for v in features[diff_cols].mean().values], textposition='outside'
    ))

    fig.add_hline(y=0, line_dash='dash', line_color='gray')
    fig.update_layout(
        height=400, yaxis_title='Percentage Point Advantage',
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_recent_form_tab(stats, tour_filter):
    """Render the Recent Form tab."""
    st.header("Recent Form Analysis")
    st.caption("Comparing last 20 matches to career averages (Ace Rate)")

    form_key = f'{tour_filter.lower()}_form'
    form_data = stats[form_key]

    if form_data.empty:
        st.info("Not enough match data to calculate recent form. Try a longer time period.")
        return

    color = '#1f77b4' if tour_filter == 'ATP' else '#e377c2'
    render_form_chart(form_data, color)


def render_form_chart(form_df, color):
    """Render a single form chart."""
    if form_df.empty:
        return

    colors = ['#2ca02c' if d > 0 else '#d62728' for d in form_df['Delta']]

    fig = go.Figure(go.Bar(
        y=form_df['Player'],
        x=form_df['Delta'],
        orientation='h',
        marker_color=colors,
        text=[f"{d:+.1f}%" for d in form_df['Delta']],
        textposition='outside',
        hovertemplate='%{y}<br>Recent: %{customdata[0]:.1f}%<br>Career: %{customdata[1]:.1f}%<extra></extra>',
        customdata=form_df[['Recent Ace %', 'Career Ace %']].values
    ))

    fig.add_vline(x=0, line_dash='dash', line_color='gray')
    fig.update_layout(
        height=450,
        xaxis_title='Ace Rate Change (Recent vs Career)',
        yaxis=dict(autorange='reversed'),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_scatter_tab(stats, tour_filter, selected_players, highlight_player, data, tab_type):
    """Generic scatter tab renderer."""
    config = SCATTER_TAB_CONFIG[tab_type]

    st.header(config['header'])
    st.caption(config['caption'])

    # Get the right stats dataframe based on tour and tab type
    stats_key = f"{tour_filter.lower()}_{config['stats_key']}"
    stats_df = filter_stats_by_players(stats[stats_key], selected_players)

    # Calculate comparison and trend for highlighted player
    comparison = None
    trend_data = None
    if highlight_player and highlight_player in stats_df['Player'].values:
        comparison = calculate_player_comparison(stats_df, highlight_player, config['stat_cols'])
        if data:
            matches_key = f"{tour_filter.lower()}_matches"
            players_key = f"{tour_filter.lower()}_players"
            trend_data = calculate_trend_stats(data[matches_key], data[players_key],
                                               highlight_player, config['trend_type'])

    # Render scatter plot
    color = '#1f77b4' if tour_filter == 'ATP' else '#e377c2'
    fig = create_filtered_scatter(
        stats_df, color,
        config['x_col'], config['y_col'],
        config['x_label'], config['y_label'],
        highlight_player, trend_data, comparison
    )
    st.plotly_chart(fig, use_container_width=True)

    # Show comparison card and analysis below
    if highlight_player and comparison:
        st.markdown("---")
        st.markdown(f"### {highlight_player} vs Selected Players")
        render_comparison_card(comparison, config['stat_labels'])
        if trend_data:
            st.caption(f"Trend: Last year ({trend_data['recent']['n_matches']} matches) vs earlier ({trend_data['earlier']['n_matches']} matches)")

        analysis = generate_player_analysis(highlight_player, comparison, trend_data, config['trend_type'])
        if analysis and analysis['bullets']:
            st.markdown("#### Analysis")
            for bullet in analysis['bullets']:
                st.caption(f"- {bullet}")
            if analysis['summary']:
                st.markdown(f"**{analysis['summary']}**")


def render_surface_tab(stats, tour_filter):
    """Render the Surface Analysis tab."""
    st.header("Surface Impact")
    st.caption("Grass favors servers (fast, low bounce). Clay neutralizes the serve (slow, high bounce).")

    surf_key = f'{tour_filter.lower()}_surf'
    surf_data = stats[surf_key]

    # Check if we have surface data
    if surf_data.empty:
        st.info("Not enough match data per surface. Try a longer time period.")
        return

    # Surface comparison chart
    fig = make_subplots(rows=1, cols=2, subplot_titles=('Aces per Match', '1st Serve Win %'),
                        horizontal_spacing=0.12)

    colors = {'Hard': '#1f77b4', 'Clay': '#d62728', 'Grass': '#2ca02c'}

    for surf in surf_data['Surface']:
        val = surf_data[surf_data['Surface']==surf]['Aces/Match'].values[0]
        fig.add_trace(go.Bar(
            name=surf, x=[tour_filter], y=[val], marker_color=colors[surf],
            text=[f'{val:.1f}'], textposition='outside',
            showlegend=(surf=='Hard')
        ), row=1, col=1)

    for surf in surf_data['Surface']:
        val = surf_data[surf_data['Surface']==surf]['1st Won %'].values[0]
        fig.add_trace(go.Bar(
            name=surf, x=[tour_filter], y=[val], marker_color=colors[surf],
            showlegend=False
        ), row=1, col=2)

    fig.update_layout(height=400, barmode='group',
                      legend=dict(orientation='h', y=1.15, x=0.5, xanchor='center'))
    st.plotly_chart(fig, use_container_width=True)

    # Player surface heatmaps
    st.subheader("Player Surface Profiles")
    st.caption("How does each player's serve performance vary across surfaces?")

    def prepare_pivot(surface_stats, common_players):
        filtered = surface_stats[surface_stats['Player'].isin(common_players) & (surface_stats['Rank'] <= 12)]
        if filtered.empty:
            return pd.DataFrame()
        pivot = filtered.pivot(index='Player', columns='Surface', values='Ace Rate %')
        order = filtered.drop_duplicates('Player').sort_values('Rank')['Player'].tolist()
        # Only reindex columns that exist
        available_cols = [c for c in ['Hard', 'Clay', 'Grass'] if c in pivot.columns]
        if not available_cols:
            return pd.DataFrame()
        return pivot.reindex(order)[available_cols]

    surface_stats_key = f'{tour_filter.lower()}_surface_stats'
    common_key = f'{tour_filter.lower()}_common'
    colorscale = 'Blues' if tour_filter == 'ATP' else 'RdPu'

    pivot = prepare_pivot(stats[surface_stats_key], stats[common_key])
    if pivot.empty:
        st.info("Not enough player data per surface. Try a longer time period.")
        return
    render_heatmap(pivot, colorscale)


def render_heatmap(pivot, colorscale):
    """Render a heatmap for surface analysis."""
    if pivot.empty:
        return

    fig = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),  # Use actual columns from pivot
        y=pivot.index.tolist(),
        colorscale=colorscale,
        text=[[f'{v:.1f}%' if pd.notna(v) else '' for v in row] for row in pivot.values],
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='%{y}<br>%{x}: %{z:.1f}%<extra></extra>',
        showscale=False
    ))
    fig.update_layout(height=400, yaxis=dict(autorange='reversed'))
    st.plotly_chart(fig, use_container_width=True)


def render_predictive_tab(stats, tour_filter):
    """Render the Predictive Stats tab."""
    st.header("Which Stats Predict Winning?")
    st.caption("How often does the match winner have the better serve stat?")

    pred_key = f'{tour_filter.lower()}_pred'
    pred = stats[pred_key]

    if pred.empty:
        st.info("Not enough match data to calculate predictive stats. Try a longer time period.")
        return

    pred = pred.copy()
    pred['Above 50%'] = pred['Winner Better %'] - 50
    color = '#1f77b4' if tour_filter == 'ATP' else '#e377c2'

    fig = go.Figure(go.Bar(
        y=pred['Stat'],
        x=pred['Above 50%'],
        orientation='h',
        marker_color=color,
        text=[f"+{x:.1f}%" for x in pred['Above 50%']],
        textposition='outside',
        hovertemplate='%{y}<br>Winner better: %{customdata:.1f}%<extra></extra>',
        customdata=pred['Winner Better %'],
    ))
    fig.add_vline(x=0, line_dash='dash', line_color='gray')

    fig.update_layout(
        height=400,
        xaxis_title='Predictive Power Above 50% (Random Chance)',
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info("**Interpretation**: 0 = coin flip (50%). Higher values indicate the stat is more predictive of winning.")


# =============================================================================
# Main App
# =============================================================================

def main():
    st.title("🎾 Tennis Serve Analysis")
    st.markdown("*A deep dive into serve statistics and their correlation with match outcomes*")

    # Load data
    data = load_data()

    # Sidebar
    st.sidebar.header("Filters")

    def reset_filters():
        """Reset dependent session state when filters change."""
        if 'players' in st.session_state:
            del st.session_state['players']
        if 'highlight_player' in st.session_state:
            del st.session_state['highlight_player']

    # Tour selector (ATP default)
    tour_filter = st.sidebar.radio("Tour", ["ATP", "WTA"], index=0,
                                   key="tour_filter", on_change=reset_filters)

    # Date Range Filter
    st.sidebar.markdown("---")
    st.sidebar.subheader("Date Range")
    date_preset = st.sidebar.selectbox(
        "Time Period",
        ["All Time", "Last 5 Years", "Last 1 Year", "Custom"],
        index=0,
        key="date_preset",
        on_change=reset_filters
    )

    # Calculate dates based on preset
    if date_preset == "Custom":
        col1, col2 = st.sidebar.columns(2)
        start_date = col1.date_input("Start", value=datetime(2020, 1, 1))
        end_date = col2.date_input("End", value=datetime.today())
    elif date_preset == "Last 1 Year":
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
    elif date_preset == "Last 5 Years":
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365*5)
    else:  # All Time
        start_date = None
        end_date = None

    # Compute stats with date filtering
    stats = compute_all_stats(
        data['atp_matches'], data['wta_matches'],
        data['atp_players'], data['wta_players'],
        start_date, end_date
    )

    # Quick filters
    st.sidebar.markdown("---")
    st.sidebar.subheader("Player Filter")

    quick_filter = st.sidebar.selectbox(
        "Quick Select",
        ["Top 5", "Top 10", "All Players"],
        index=0,
        key="quick_filter",
        on_change=reset_filters
    )

    # Get player list for selected tour
    all_players = stats[f'{tour_filter.lower()}_ace']['Player'].tolist()

    # Handle case where date filter returns no data
    if not all_players:
        st.sidebar.warning("No player data for selected time period. Try a longer date range.")
        return

    # Apply quick filter
    if quick_filter == "Top 5":
        default_players = all_players[:5]
    elif quick_filter == "Top 10":
        default_players = all_players[:10]
    else:
        default_players = all_players

    # Player multiselect (single list for selected tour)
    selected_players = st.sidebar.multiselect(
        f"{tour_filter} Players",
        all_players,
        default=default_players,
        key="players"
    )

    # Highlight Player
    st.sidebar.markdown("---")
    st.sidebar.subheader("Highlight Player")
    highlight_options = ["None"] + selected_players
    highlight_player = st.sidebar.selectbox(
        "Highlight in Scatter Plots",
        highlight_options,
        index=0,
        key="highlight_player"
    )
    highlight_player = None if highlight_player == "None" else highlight_player

    # Data coverage info
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Coverage")
    # Calculate filtered match counts for selected tour
    filtered_matches = filter_by_date_range(data[f'{tour_filter.lower()}_matches'], start_date, end_date)
    st.sidebar.markdown(f"**{tour_filter}**: {len(filtered_matches):,} matches")

    # Tabs
    tabs = st.tabs([
        "📊 Overview",
        "📈 Recent Form",
        "🎯 Ace Production",
        "🎾 First Serve",
        "💪 Break Points",
        "🌍 Surface Analysis",
        "🔮 Predictive Stats"
    ])

    with tabs[0]:
        render_overview_tab(data, stats, tour_filter, start_date, end_date)

    with tabs[1]:
        render_recent_form_tab(stats, tour_filter)

    with tabs[2]:
        render_scatter_tab(stats, tour_filter, selected_players, highlight_player, data, 'ace')

    with tabs[3]:
        render_scatter_tab(stats, tour_filter, selected_players, highlight_player, data, '1st')

    with tabs[4]:
        render_scatter_tab(stats, tour_filter, selected_players, highlight_player, data, 'bp')

    with tabs[5]:
        render_surface_tab(stats, tour_filter)

    with tabs[6]:
        render_predictive_tab(stats, tour_filter)

    # Key Takeaways
    st.markdown("---")
    st.header("Key Takeaways")
    st.markdown("""
    - **Winners outserve losers** across all metrics, with the biggest gaps in 1st serve win % and break point save %
    - **ATP players hit 2x more aces** than WTA players on average
    - **Break point save %** is the most predictive stat - it combines serving ability with clutch performance
    - **Surface matters**: Grass produces the most aces; clay neutralizes serve advantages
    """)


if __name__ == "__main__":
    main()
