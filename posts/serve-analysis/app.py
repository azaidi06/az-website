"""Story-driven tennis analysis: What happens with a good vs. worse first serve %."""
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

# Page config
st.set_page_config(
    page_title="The First Serve",
    page_icon="🎾",
    layout="wide"
)

# Custom CSS for story layout
st.markdown("""
<style>
    .story-section {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #2c7fbf;
    }
    .story-section.warm { border-left-color: #d9534f; }
    .story-section.green { border-left-color: #5cb85c; }
    .story-section.gold { border-left-color: #f0ad4e; }
    .section-title {
        font-size: 1.4rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .section-text {
        font-size: 0.95rem;
        line-height: 1.6;
        color: #444;
    }
    .highlight-stat {
        display: inline-block;
        background: #2c7fbf;
        color: white;
        padding: 0.1rem 0.5rem;
        border-radius: 4px;
        font-weight: 700;
        font-size: 0.9rem;
    }
    .highlight-stat.red { background: #d9534f; }
    .highlight-stat.green { background: #5cb85c; }
    .highlight-stat.gold { background: #f0ad4e; }
    .big-number {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
    }
    .big-number-label {
        font-size: 0.85rem;
        color: #666;
        margin-top: 0.25rem;
    }
    .stat-card {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .takeaway-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .takeaway-box h4 { margin: 0 0 0.5rem 0; }
    .takeaway-box ul { margin: 0; padding-left: 1.2rem; }
    .takeaway-box li { margin: 0.3rem 0; }
    .divider {
        border: none;
        border-top: 2px dashed #ddd;
        margin: 2rem 0;
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

    atp_rankings = pd.read_csv(f'{DATA_PATH}/atp/atp_top25_rankings.csv')
    wta_rankings = pd.read_csv(f'{DATA_PATH}/wta/wta_top25_rankings.csv')

    latest_atp_date = atp_rankings['ranking_date'].max()
    latest_wta_date = wta_rankings['ranking_date'].max()
    latest_atp = atp_rankings[atp_rankings['ranking_date'] == latest_atp_date][['player', 'rank']]
    latest_wta = wta_rankings[wta_rankings['ranking_date'] == latest_wta_date][['player', 'rank']]

    for df in [atp_players, wta_players]:
        df['full_name'] = df['name_first'] + ' ' + df['name_last']

    atp_players = atp_players.merge(latest_atp, left_on='player_id', right_on='player', how='left')
    wta_players = wta_players.merge(latest_wta, left_on='player_id', right_on='player', how='left')
    atp_players.drop(columns=['player'], inplace=True)
    wta_players.drop(columns=['player'], inplace=True)

    atp_players['tour'], wta_players['tour'] = 'ATP', 'WTA'
    atp_matches['tour'], wta_matches['tour'] = 'ATP', 'WTA'

    atp_matches['tourney_date'] = pd.to_datetime(atp_matches['tourney_date'].astype(str), format='%Y%m%d')
    wta_matches['tourney_date'] = pd.to_datetime(wta_matches['tourney_date'].astype(str), format='%Y%m%d')

    # Load scraped data
    atp_scraped_file = f'{DATA_PATH}/atp/atp_top25_matches_scraped.csv'

    def _safe_id_col(series):
        return series.where(pd.notna(series), -1).astype(int).astype(str).replace('-1', '')

    if pd.api.types.is_float_dtype(atp_matches['winner_id']):
        atp_matches['winner_id'] = _safe_id_col(atp_matches['winner_id'])
        atp_matches['loser_id'] = _safe_id_col(atp_matches['loser_id'])

    if pd.Path(atp_scraped_file).exists():
        try:
            atp_scraped_matches = pd.read_csv(atp_scraped_file)
            if pd.api.types.is_float_dtype(atp_scraped_matches['winner_id']):
                atp_scraped_matches['winner_id'] = _safe_id_col(atp_scraped_matches['winner_id'])
                atp_scraped_matches['loser_id'] = _safe_id_col(atp_scraped_matches['loser_id'])
            atp_scraped_matches['tourney_date'] = pd.to_datetime(
                atp_scraped_matches['tourney_date'].astype(str), format='%Y%m%d'
            )
            atp_scraped_matches = atp_scraped_matches[
                atp_scraped_matches['tourney_date'] >= pd.Timestamp('2025-01-01')
            ]
            atp_scraped_matches = atp_scraped_matches[
                atp_scraped_matches['w_svpt'].astype(float) > 0
            ]
            atp_scraped_matches['tour'] = 'ATP'
            main_keys = set(
                zip(atp_matches['tourney_date'].dt.strftime('%Y-%m-%d'),
                    atp_matches['winner_id'], atp_matches['loser_id'],
                    atp_matches['score'])
            )
            new_scraped = []
            for _, row in atp_scraped_matches.iterrows():
                key = (
                    row['tourney_date'].strftime('%Y-%m-%d'),
                    row['winner_id'], row['loser_id'], row['score']
                )
                if key not in main_keys:
                    new_scraped.append(row)
            if new_scraped:
                atp_scraped_df = pd.DataFrame(new_scraped)
                if 'tour_x' in atp_scraped_df.columns:
                    atp_scraped_df = atp_scraped_df.drop(columns=[c for c in atp_scraped_df.columns if c.endswith('_x') or c.endswith('_y')])
                atp_matches = pd.concat([atp_matches, atp_scraped_df], ignore_index=True)
        except Exception as e:
            print(f"  Warning: Could not load scraped ATP data: {e}")

    serve_cols = ['w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced']
    atp_serve_matches = atp_matches.dropna(subset=serve_cols)
    atp_serve_matches = atp_serve_matches[atp_serve_matches['w_svpt'].astype(float) > 0]
    wta_serve_matches = wta_matches.dropna(subset=serve_cols)
    wta_serve_matches = wta_serve_matches[wta_serve_matches['w_svpt'].astype(float) > 0]

    return {
        'atp_players': atp_players,
        'wta_players': wta_players,
        'atp_matches': atp_serve_matches,
        'wta_matches': wta_serve_matches,
    }


def compute_all_stats(atp_matches, wta_matches, atp_players, wta_players,
                      start_date=None, end_date=None):
    """Compute all stats for both tours."""
    atp_ace = calculate_ace_stats(atp_matches, atp_players, start_date, end_date)
    wta_ace = calculate_ace_stats(wta_matches, wta_players, start_date, end_date)
    atp_1st = calculate_1st_serve_stats(atp_matches, atp_players, start_date, end_date)
    wta_1st = calculate_1st_serve_stats(wta_matches, wta_players, start_date, end_date)
    atp_bp = calculate_bp_stats(atp_matches, atp_players, start_date, end_date)
    wta_bp = calculate_bp_stats(wta_matches, wta_players, start_date, end_date)

    atp_common = set(atp_ace['Player']) & set(atp_1st['Player']) & set(atp_bp['Player'])
    wta_common = set(wta_ace['Player']) & set(wta_1st['Player']) & set(wta_bp['Player'])

    for key in ['atp_ace', 'atp_1st', 'atp_bp', 'wta_ace', 'wta_1st', 'wta_bp']:
        locals()[key] = locals()[key][locals()[key]['Player'].isin(
            atp_common if key.startswith('atp') else wta_common
        )].sort_values('Rank').reset_index(drop=True)

    atp_form = calculate_recent_vs_career(atp_matches, atp_players, start_date=start_date, end_date=end_date).head(15)
    wta_form = calculate_recent_vs_career(wta_matches, wta_players, start_date=start_date, end_date=end_date).head(15)
    atp_surf = serve_by_surface(atp_matches, start_date, end_date)
    wta_surf = serve_by_surface(wta_matches, start_date, end_date)
    atp_surface_stats = player_surface_stats(atp_matches, atp_players, start_date, end_date)
    wta_surface_stats = player_surface_stats(wta_matches, wta_players, start_date, end_date)
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


# =============================================================================
# Story-specific helper functions
# =============================================================================

def compute_player_1st_stats(matches_df, players_df, start_date=None, end_date=None):
    """Compute first serve %, 1st serve won %, and overall service games won % per player."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    results = []

    for _, player in players_df.iterrows():
        pid = player['player_id']
        name = player['full_name']
        rank = player['rank']

        wins = matches_df[matches_df['winner_id'] == pid]
        losses = matches_df[matches_df['loser_id'] == pid]

        # First serve stats
        total_1st_in = wins['w_1stIn'].sum() + losses['l_1stIn'].sum()
        total_svpt = wins['w_svpt'].sum() + losses['l_svpt'].sum()
        total_1st_won = wins['w_1stWon'].sum() + losses['l_1stWon'].sum()

        if total_svpt > 0 and total_1st_in > 0:
            pct_1st = total_1st_in / total_svpt * 100
            pct_1st_won = total_1st_won / total_1st_in * 100

            results.append({
                'Player': name.split()[-1],
                'Rank': rank,
                '1st Serve %': round(pct_1st, 1),
                '1st Serve Won %': round(pct_1st_won, 1),
                'Total Points': total_svpt,
            })

    df = pd.DataFrame(results)
    if df.empty:
        return df
    return df.sort_values('Rank').reset_index(drop=True)


def build_1st_serve_winners(matches_df, start_date=None, end_date=None):
    """For each match, compute the winner's and loser's 1st serve %. Then analyze the relationship."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    df = matches_df.copy()

    df['w_1st_pct'] = df['w_1stIn'] / df['w_svpt'] * 100
    df['l_1st_pct'] = df['l_1stIn'] / df['l_svpt'] * 100
    df['w_1st_won'] = df['w_1stWon'] / df['w_1stIn'] * 100
    df['l_1st_won'] = df['l_1stWon'] / df['l_1stIn'] * 100

    df['diff_1st_pct'] = df['w_1st_pct'] - df['l_1st_pct']
    df['diff_1st_won'] = df['w_1st_won'] - df['l_1st_won']

    # Who has higher 1st serve %?
    df['higher_1st_won_match'] = df['w_1st_pct'] > df['l_1st_pct']

    return df


def create_funnel_chart(stats_1st, color='#2c7fbf'):
    """Create a visual funnel showing the cascade from 1st serve % to match success."""
    avg_1st_pct = stats_1st['1st Serve %'].mean()
    avg_1st_won = stats_1st['1st Serve Won %'].mean()

    # Group into quartiles
    quartiles = stats_1st.copy()
    quartiles['quartile'] = pd.qcut(quartiles['1st Serve %'], 4, labels=['Bottom 25%', 'Q2', 'Q3', 'Top 25%'])
    quartile_stats = quartiles.groupby('quartile', observed=False).agg({
        '1st Serve %': 'mean',
        '1st Serve Won %': 'mean',
        'Rank': 'median'
    }).reset_index()

    colors = ['#d9534f', '#f0ad4e', '#5cb85c', '#2c7fbf']

    fig = go.Figure()

    # Funnel shape: wide at top (1st serve %), narrowing to 1st serve won %
    for i, row in quartile_stats.iterrows():
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=row['1st Serve %'],
            domain={'x': [0, 1], 'y': [0.75 - i*0.2, 0.95 - i*0.2]},
            title={'text': f"<b>{row['quartile']}</b><br>(Avg Rank #{int(row['Rank'])})", 'font': {'size': 11}},
            gauge={
                'shape': "bullet",
                'axis': {'range': [50, 75]},
                'bar': {'color': colors[i]},
                'threshold': {
                    'line': {'color': "red", 'width': 2},
                    'thickness': 0.75,
                    'value': 60
                },
                'steps': [
                    {'range': [50, 57.5], 'color': '#f5f5f5'},
                    {'range': [57.5, 60], 'color': '#e8e8e8'},
                ],
            },
            number={'font': {'size': 18}},
            delta={'reference': 60, 'valueformat': '.1f'},
        ))

    # Second row: 1st serve won % for each quartile
    for i, row in quartile_stats.iterrows():
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=row['1st Serve Won %'],
            domain={'x': [0, 1], 'y': [0.25 - i*0.2, 0.45 - i*0.2]},
            title={'text': f"  1st Serve Won %", 'font': {'size': 10}},
            gauge={
                'shape': "bullet",
                'axis': {'range': [50, 80]},
                'bar': {'color': colors[i]},
                'threshold': {
                    'line': {'color': "green", 'width': 2},
                    'thickness': 0.75,
                    'value': 65
                },
            },
            number={'font': {'size': 16}},
            delta={'reference': 65, 'valueformat': '.1f'},
        ))

    fig.update_layout(
        height=500,
        margin=dict(l=10, r=10, t=40, b=20),
        showlegend=False,
    )

    return fig


def create_1st_pct_vs_match_success_scatter(matches_df, color='#2c7fbf'):
    """Show the relationship between 1st serve % differential and match outcome."""
    df = build_1st_serve_winners(matches_df)

    fig = go.Figure()

    # Color by whether they had higher or lower 1st serve %
    higher = df[df['higher_1st_won_match']].copy()
    lower = df[~df['higher_1st_won_match']].copy()

    fig.add_trace(go.Scatter(
        x=higher['diff_1st_pct'],
        y=higher['diff_1st_won'],
        mode='markers',
        name='Higher 1st %',
        marker=dict(size=6, color=color, opacity=0.5),
        hovertemplate='1st % diff: %{x:.1f}pp<br>1st Won diff: %{y:.1f}pp<extra></extra>',
    ))

    fig.add_trace(go.Scatter(
        x=lower['diff_1st_pct'],
        y=lower['diff_1st_won'],
        mode='markers',
        name='Lower 1st %',
        marker=dict(size=6, color='#d9534f', opacity=0.5),
        hovertemplate='1st % diff: %{x:.1f}pp<br>1st Won diff: %{y:.1f}pp<extra></extra>',
    ))

    # Add trend line
    if len(df) > 10:
        z = np.polyfit(df['diff_1st_pct'], df['diff_1st_won'], 1)
        p = np.poly1d(z)
        x_line = np.linspace(df['diff_1st_pct'].min(), df['diff_1st_pct'].max(), 100)
        fig.add_trace(go.Scatter(
            x=x_line, y=p(x_line),
            mode='lines', name='Trend',
            line=dict(color='black', width=2, dash='dash'),
            showlegend=False,
        ))

    fig.add_hline(y=0, line_dash='dash', line_color='gray', opacity=0.5)
    fig.add_vline(x=0, line_dash='dash', line_color='gray', opacity=0.5)

    # Calculate correlation
    corr = df['diff_1st_pct'].corr(df['diff_1st_won'])

    fig.update_layout(
        xaxis_title='Winner\'s 1st Serve % − Loser\'s 1st Serve % (pp)',
        yaxis_title='Winner\'s 1st Won % − Loser\'s 1st Won % (pp)',
        height=450,
        showlegend=True,
        legend=dict(orientation='h', y=1.08, x=0.5, xanchor='center'),
    )

    return fig, corr


def create_player_1st_scatter(stats_1st, color='#2c7fbf', highlight_player=None):
    """Scatter of 1st Serve % vs 1st Serve Won % for players."""
    fig = go.Figure()

    for _, row in stats_1st.iterrows():
        is_hl = highlight_player and row['Player'] == highlight_player
        marker = dict(
            size=14 if is_hl else 10,
            color='gold' if is_hl else color,
            line=dict(color='darkred', width=2) if is_hl else None,
            opacity=0.8,
        )
        fig.add_trace(go.Scatter(
            x=[row['1st Serve %']], y=[row['1st Serve Won %']],
            mode='markers+text',
            text=[row['Player']],
            textposition='top center',
            textfont=dict(size=9 if is_hl else 8, color='darkred' if is_hl else None),
            marker=marker,
            hovertemplate=f"{row['Player']} (#{row['Rank']})<br>1st Serve %: %{{x}}<br>1st Won %: %{{y}}<extra></extra>",
        ))

    fig.add_hline(y=stats_1st['1st Serve Won %'].mean(), line_dash='dash', line_color='gray', opacity=0.4)
    fig.add_vline(x=stats_1st['1st Serve %'].mean(), line_dash='dash', line_color='gray', opacity=0.4)

    fig.update_layout(
        xaxis_title='First Serve %',
        yaxis_title='First Serve Won %',
        height=450,
        showlegend=False,
    )

    return fig


def create_correlation_matrix(matches_df, start_date=None, end_date=None):
    """Compute and visualize correlations between serve stats and match winning."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    df = matches_df.copy()

    # Create a feature matrix: for each match, what's the player's stat?
    # We'll look at the winner's stats and see if higher values → more likely to win
    features = {
        '1st Serve %': df['w_1stIn'] / df['w_svpt'] * 100,
        '1st Won %': df['w_1stWon'] / df['w_1stIn'] * 100,
        '2nd Won %': df['w_2ndWon'] / (df['w_svpt'] - df['w_1stIn']),
        'Ace Rate': df['w_ace'] / df['w_svpt'] * 100,
        'BP Save %': df['w_bpSaved'] / df['w_bpFaced'].replace(0, np.nan) * 100,
    }

    feat_df = pd.DataFrame(features)
    corr = feat_df.corr()

    # Mask upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.columns,
        text=[[f'{v:.2f}' for v in row] for row in corr.values],
        texttemplate='%{text}',
        textfont={'size': 10},
        colorscale='RdYlBu_r',
        zmin=-0.3,
        zmax=0.3,
    ))

    fig.update_layout(
        height=400,
        xaxis_title='Serve Stat',
        yaxis_title='Serve Stat',
        yaxis_autorange='reversed',
    )

    return fig, corr


# =============================================================================
# Story Rendering Functions
# =============================================================================

def render_story_header(data, tour_filter):
    """Render the opening section of the story."""
    matches = data[f'{tour_filter.lower()}_matches']

    # Compute key numbers
    avg_1st_pct = (matches['w_1stIn'] / matches['w_svpt']).mean() * 100
    avg_1st_won = (matches['w_1stWon'] / matches['w_1stIn']).mean() * 100
    avg_2nd_won = (matches['w_2ndWon'] / (matches['w_svpt'] - matches['w_1stIn'])).mean() * 100

    st.title("🎾 The First Serve: What 60% vs 70% Looks Like on Court")
    st.markdown("""
    In tennis, the first serve is the only shot where you have complete control.
    You choose the toss, the spin, the direction. But here's the question that separates
    good servers from great ones: **does getting more first serves in actually matter?**

    We dug into thousands of matches among the top 25 players on both tours to find out.
    """
    )

    # Big numbers
    st.markdown("---")
    st.subheader(f"Tour Averages — {tour_filter}")
    cols = st.columns(4)
    cols[0].markdown(f"<div class='big-number' style='color:#2c7fbf'>{avg_1st_pct:.1f}%</div><div class='big-number-label'>Avg First Serve In</div>", unsafe_allow_html=True)
    cols[1].markdown(f"<div class='big-number' style='color:#5cb85c'>{avg_1st_won:.1f}%</div><div class='big-number-label'>1st Serve Won</div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div class='big-number' style='color:#f0ad4e'>{avg_2nd_won:.1f}%</div><div class='big-number-label'>2nd Serve Won</div>", unsafe_allow_html=True)
    cols[3].markdown(f"<div class='big-number'>{len(matches):,}</div><div class='big-number-label'>Matches Analyzed</div>", unsafe_allow_html=True)


def render_story_section_1(data, stats, tour_filter, start_date, end_date):
    """Section 1: The baseline — what does a 'good' first serve look like?"""
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='story-section'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📐 The Baseline: What Does 60% vs 70% Look Like?</div>", unsafe_allow_html=True)
    st.markdown("""
    **The first serve percentage** — how often a player's first delivery finds the box — is the most
    fundamental serve stat. But the gap between a 60% server and a 70% server is huge in practical terms.

    A player serving 60% of firsts will find the box **6 out of 10 times**. The other 4 go into the net or wide —
    and that's a **second serve**, which gives the opponent a much easier return.
    """
    )

    # Player scatter: 1st serve % vs 1st serve won %
    stats_1st = compute_player_1st_stats(
        data[f'{tour_filter.lower()}_matches'],
        data[f'{tour_filter.lower()}_players'],
        start_date, end_date
    )

    if not stats_1st.empty:
        fig = create_player_1st_scatter(stats_1st, '#2c7fbf')

        # Add quadrant labels
        x_mean = stats_1st['1st Serve %'].mean()
        y_mean = stats_1st['1st Serve Won %'].mean()
        fig.add_annotation(
            x=72, y=80, text="Great server",
            showarrow=False, font=dict(size=12, color='green', opacity=0.6),
        )
        fig.add_annotation(
            x=55, y=72, text="Struggles",
            showarrow=False, font=dict(size=12, color='red', opacity=0.6),
        )
        fig.add_annotation(
            x=72, y=72, text="Safe but flat",
            showarrow=False, font=dict(size=12, color='gray', opacity=0.5),
        )
        fig.add_annotation(
            x=55, y=80, text="Risky",
            showarrow=False, font=dict(size=12, color='gray', opacity=0.5),
        )

        st.plotly_chart(fig, use_container_width=True)

        # Key insight boxes
        st.markdown("---")
        col1, col2, col3 = st.columns(3)

        # Find best and worst 1st serve %
        best = stats_1st.loc[stats_1st['1st Serve %'].idxmax()]
        worst = stats_1st.loc[stats_1st['1st Serve %'].idxmin()]

        col1.markdown(f"""
        <div class='stat-card'>
            <div style='font-size:0.8rem;color:#666'>Highest 1st Serve %</div>
            <div style='font-size:1.2rem;font-weight:700'>#{best['Rank']} {best['Player']}</div>
            <div style='font-size:2rem;font-weight:800;color:#2c7fbf'>{best['1st Serve %']}%</div>
            <div style='font-size:0.75rem;color:#888'>Won {best['1st Serve Won %']}% of points</div>
        </div>
        """, unsafe_allow_html=True)

        col2.markdown(f"""
        <div class='stat-card'>
            <div style='font-size:0.8rem;color:#666'>Tour Average</div>
            <div style='font-size:1.2rem;font-weight:700'>Field Avg</div>
            <div style='font-size:2rem;font-weight:800;color:#f0ad4e'>{stats_1st['1st Serve %'].mean():.1f}%</div>
            <div style='font-size:0.75rem;color:#888'>Won {stats_1st['1st Serve Won %'].mean():.1f}% of points</div>
        </div>
        """, unsafe_allow_html=True)

        col3.markdown(f"""
        <div class='stat-card'>
            <div style='font-size:0.8rem;color:#666'>Lowest 1st Serve %</div>
            <div style='font-size:1.2rem;font-weight:700'>#{worst['Rank']} {worst['Player']}</div>
            <div style='font-size:2rem;font-weight:800;color:#d9534f'>{worst['1st Serve %']}%</div>
            <div style='font-size:0.75rem;color:#888'>Won {worst['1st Serve Won %']}% of points</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_story_section_2(matches_df, stats, tour_filter, start_date, end_date):
    """Section 2: The cascade — what happens when you miss more first serves."""
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='story-section warm'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>📉 The Cascade: Missing First Serves Costs Points</div>", unsafe_allow_html=True)
    st.markdown("""
    Here's the chain reaction. When a player misses more first serves:

    1. **More second serves** — which opponents attack aggressively
    2. **Lower point win rate** — second serves are easier to return
    3. **More break points faced** — the opponent gets more chances to break
    4. **Higher break probability** — the serve game unravels

Let's look at what the data shows.
    """
    )

    # Match-level scatter: 1st serve % diff vs 1st serve won % diff
    fig, corr = create_1st_pct_vs_match_success_scatter(matches_df, '#2c7fbf')
    st.plotly_chart(fig, use_container_width=True)

    # Correlation interpretation
    st.markdown(f"""
    <div class='story-section green'>
    <div class='section-title'>The Bottom Line</div>
    <div class='section-text'>
    The correlation between <span class='highlight-stat'>1st Serve % differential</span> and
    <span class='highlight-stat green'>1st Serve Won % differential</span> is
    <span class='highlight-stat gold' style='font-size:1.2rem'>r = {corr:.3f}</span>.
    <br><br>
    What this means: When a player gets more first serves in than their opponent,
    they don't just get *more* first serves — they also win a *higher percentage* of points on them.
    This is the cascade effect: more first serves → more points won → harder to break.
    </div>
    </div>
    """, unsafe_allow_html=True)

    # Breakdown by quartile
    st.markdown("<br>### How the Top and Bottom Performers Compare", unsafe_allow_html=True)
    df = build_1st_serve_winners(matches_df, start_date, end_date)

    # Group by who had higher 1st serve %
    higher = df[df['higher_1st_won_match']]
    lower = df[~df['higher_1st_won_match']]

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"""
    <div class='stat-card' style='border-left:4px solid #5cb85c'>
        <div style='font-size:0.8rem;color:#666'>Higher 1st Serve % Won</div>
        <div style='font-size:2rem;font-weight:800;color:#5cb85c'>{len(higher):,}</div>
        <div style='font-size:0.75rem;color:#888'>matches ({(len(higher)/len(df)*100):.1f}%)</div>
    </div>
    """, unsafe_allow_html=True)
    col2.markdown(f"""
    <div class='stat-card' style='border-left:4px solid #f0ad4e'>
        <div style='font-size:0.8rem;color:#666'>Avg 1st Won Diff</div>
        <div style='font-size:2rem;font-weight:800;color:#f0ad4e'>+{higher['diff_1st_won'].mean():.1f}pp</div>
        <div style='font-size:0.75rem;color:#888'>when 1st % is higher</div>
    </div>
    """, unsafe_allow_html=True)
    col3.markdown(f"""
    <div class='stat-card' style='border-left:4px solid #d9534f'>
        <div style='font-size:0.8rem;color:#666'>Avg 1st Won Diff</div>
        <div style='font-size:2rem;font-weight:800;color:#d9534f'>{lower['diff_1st_won'].mean():.1f}pp</div>
        <div style='font-size:0.75rem;color:#888'>when 1st % is lower</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_story_section_3(matches_df, stats, tour_filter, start_date, end_date):
    """Section 3: The predictive power — which stats actually predict winning?"""
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='story-section gold'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🔮 Predictive Power: What Actually Determines Winners?</div>", unsafe_allow_html=True)
    st.markdown("""
    We calculated how much each serve stat predicts match outcomes — i.e., how often does the
    winner have the better stat? If 1st serve % is so important, why isn't it the #1 predictor?
    """)

    pred_key = f'{tour_filter.lower()}_pred'
    pred = stats[pred_key]

    if not pred.empty:
        pred = pred.copy()
        pred['Above 50%'] = pred['Winner Better %'] - 50

        fig = go.Figure(go.Bar(
            y=pred['Stat'],
            x=pred['Above 50%'],
            orientation='h',
            marker_color='#2c7fbf',
            text=[f"+{x:.1f}%" for x in pred['Above 50%']],
            textposition='outside',
            hovertemplate='%{y}<br>Predictive: %{customdata:.1f}%<extra></extra>',
            customdata=pred['Winner Better %'],
        ))
        fig.add_vline(x=0, line_dash='dash', line_color='gray')
        fig.update_layout(
            height=350,
            xaxis_title='Predictive Power Above Random (50%)',
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class='story-section'>
        <div class='section-title'>Why 1st Serve Won % Wins (Not 1st Serve %)</div>
        <div class='section-text'>
        Here's the insight: getting the first serve IN doesn't matter as much as winning the point
        on it. A player with a 55% first serve but winning 75% of them is often more effective
        than a player with 70% first serve but winning only 65% of them.
        <br><br>
        <span class='highlight-stat'>1st Serve Won %</span> captures the quality of the serve,
        not just the quantity. It's the difference between a safe second serve and a missed first serve.
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_story_section_4(matches_df, stats, tour_filter, start_date, end_date):
    """Section 4: Surface context — where does the first serve matter most?"""
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='story-section green'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>🌍 Surface Context: Where Does the First Serve Matter Most?</div>", unsafe_allow_html=True)
    st.markdown("""
    The importance of the first serve isn't the same on every surface. On grass, a big first serve
    can end the point instantly. On clay, the slower surface gives returners more time.
    """)

    surf_key = f'{tour_filter.lower()}_surf'
    surf_data = stats[surf_key]

    if not surf_data.empty:
        fig = make_subplots(rows=1, cols=2, subplot_titles=('Aces per Match', '1st Serve Win %'),
                            horizontal_spacing=0.15)

        colors = {'Hard': '#1f77b4', 'Clay': '#d62728', 'Grass': '#2ca02c'}

        for surf in surf_data['Surface']:
            val = surf_data[surf_data['Surface']==surf]['Aces/Match'].values[0]
            fig.add_trace(go.Bar(
                name=surf, x=[tour_filter], y=[val], marker_color=colors.get(surf, '#888'),
                text=[f'{val:.1f}'], textposition='outside',
            ), row=1, col=1)

            val2 = surf_data[surf_data['Surface']==surf]['1st Won %'].values[0]
            fig.add_trace(go.Bar(
                name=surf, x=[tour_filter], y=[val2], marker_color=colors.get(surf, '#888'),
            ), row=1, col=2)

        fig.update_layout(height=350, barmode='group')
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("""
        <div class='story-section'>
        <div class='section-text'>
        <strong>Grass</strong> is the great equalizer for big servers — the fast surface and low bounce make
        first serves devastating. <strong>Clay</strong> is the great neutralizer — the slow surface and high bounce
        give returners more time to react, making second serves more viable.
        <br><br>
        On clay, a 60% first serve player has more breathing room. On grass, that same player
        gets punished more often.
        </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_story_section_5(matches_df, stats, tour_filter, start_date, end_date):
    """Section 5: The takeaway — what should players change?"""
    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown("<div class='takeaway-box'>", unsafe_allow_html=True)
    st.markdown("<h4>🎯 The Bottom Line</h4>", unsafe_allow_html=True)
    st.markdown("""
    After analyzing thousands of matches, here's what the first serve data tells us:
    """)

    pred_key = f'{tour_filter.lower()}_pred'
    pred = stats[pred_key]
    df = build_1st_serve_winners(matches_df, start_date, end_date)
    higher_win_rate = len(df[df['higher_1st_won_match']]) / len(df) * 100

    tour_key = f'{tour_filter.lower()}_1st'
    avg_1st = stats[tour_key]['1st Serve %'].mean() if not stats[tour_key].empty else 62

    takeaways = [
        f"<li><strong>Getting more first serves in wins matches</strong> — {higher_win_rate:.0f}% of matches go to the player with the higher 1st serve %</li>",
        f"<li><strong>Quality beats quantity</strong> — The most predictive stat is <em>1st Serve Won %</em>, not 1st Serve %</li>",
        "<li><strong>The cascade is real</strong> — More first serves → more points won → fewer break points faced → more service games held</li>",
        "<li><strong>Surface changes everything</strong> — On clay, a lower 1st serve % is more forgivable. On grass, it's deadly.</li>",
        f"<li><strong>The gap matters</strong> — A ~{avg_1st:.0f}% tour average means every 1pp above/below is meaningful</li>",
    ]

    st.markdown(f"""
    <ul style='margin:0;padding-left:1.5rem;font-size:1rem;line-height:1.8'>
    {''.join(takeaways)}
    </ul>
    """, unsafe_allow_html=True)

    st.markdown("""
    <br>
    <strong>The takeaway for players:</strong> Don't just chase a higher first serve %. Chase a higher
    <em>first serve win rate</em>. That means: serve with purpose, target the right spots,
    and trust your first serve even when you're missing. Because when it goes in, it should end the point.
    """)

    st.markdown("""
    <br><br>
    <div style='text-align:center;color:#888;font-size:0.8rem;'>
    Data: ATP & WTA Top 25 players · Matches filtered for serve statistics ·
    Current as of May 2026
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# =============================================================================
# Main App
# =============================================================================

def main():
    # Load data
    data = load_data()

    # Sidebar
    st.sidebar.header("Filters")

    def reset_filters():
        if 'highlight_player' in st.session_state:
            del st.session_state['highlight_player']

    tour_filter = st.sidebar.radio("Tour", ["ATP", "WTA"], index=0,
                                   key="tour_filter", on_change=reset_filters)

    st.sidebar.markdown("---")
    st.sidebar.subheader("Date Range")
    date_preset = st.sidebar.selectbox(
        "Time Period",
        ["All Time", "Last 5 Years", "Last 1 Year", "Custom"],
        index=1,
        key="date_preset",
        on_change=reset_filters
    )

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
    else:
        start_date = None
        end_date = None

    # Compute stats
    stats = compute_all_stats(
        data['atp_matches'], data['wta_matches'],
        data['atp_players'], data['wta_players'],
        start_date, end_date
    )

    # Highlight Player selector
    st.sidebar.markdown("---")
    st.sidebar.subheader("Highlight Player")
    all_players = stats[f'{tour_filter.lower()}_1st']['Player'].tolist() if not stats[f'{tour_filter.lower()}_1st'].empty else []
    if all_players:
        highlight_options = ["None"] + all_players
        highlight_player = st.sidebar.selectbox(
            "Highlight", highlight_options, index=0, key="highlight_player"
        )
        highlight_player = None if highlight_player == "None" else highlight_player
    else:
        highlight_player = None

    # Data coverage
    st.sidebar.markdown("---")
    st.sidebar.subheader("Data Coverage")
    filtered_matches = filter_by_date_range(data[f'{tour_filter.lower()}_matches'], start_date, end_date)
    st.sidebar.markdown(f"**{tour_filter}**: {len(filtered_matches):,} matches")

    # Check for empty data
    if filtered_matches.empty:
        st.warning("No match data available for the selected time period.")
        return

    # ====== THE STORY ======
    render_story_header(data, tour_filter)

    # Section 1: Baseline
    render_story_section_1(data, stats, tour_filter, start_date, end_date)

    # Section 2: Cascade
    render_story_section_2(filtered_matches, stats, tour_filter, start_date, end_date)

    # Section 3: Predictive
    render_story_section_3(filtered_matches, stats, tour_filter, start_date, end_date)

    # Section 4: Surface
    render_story_section_4(filtered_matches, stats, tour_filter, start_date, end_date)

    # Section 5: Takeaway
    render_story_section_5(filtered_matches, stats, tour_filter, start_date, end_date)


if __name__ == "__main__":
    main()
