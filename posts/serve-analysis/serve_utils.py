"""Utility functions for tennis serve analysis."""
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# =============================================================================
# Data Processing Functions
# =============================================================================

def filter_by_date_range(matches_df, start_date=None, end_date=None):
    """Filter matches by date range."""
    if start_date is not None:
        matches_df = matches_df[matches_df['tourney_date'] >= pd.Timestamp(start_date)]
    if end_date is not None:
        matches_df = matches_df[matches_df['tourney_date'] <= pd.Timestamp(end_date)]
    return matches_df


def calculate_min_matches(start_date, end_date, base_min=20):
    """Calculate appropriate min_matches threshold based on date range.

    Shorter time periods require lower thresholds since players play ~15-25 matches/year.
    """
    if start_date is None or end_date is None:
        return base_min
    days = (pd.Timestamp(end_date) - pd.Timestamp(start_date)).days
    if days <= 365:
        return max(5, base_min // 4)  # 5 matches for 1 year
    elif days <= 365 * 2:
        return max(8, base_min // 3)
    elif days <= 365 * 3:
        return max(10, base_min // 2)
    return base_min


def _calculate_player_stats(matches_df, players_df, win_cols, lose_cols, renamed_cols,
                            stat_calcs, min_matches=20):
    """Generic player stat calculator. Combines wins/losses and applies stat_calcs function."""
    results = []
    for _, player in players_df.iterrows():
        pid, name, rank = player['player_id'], player['full_name'], player['rank']
        wins = matches_df[matches_df['winner_id'] == pid][win_cols].copy()
        wins.columns = renamed_cols
        losses = matches_df[matches_df['loser_id'] == pid][lose_cols].copy()
        losses.columns = renamed_cols
        all_m = pd.concat([wins, losses]).dropna()
        if len(all_m) >= min_matches:
            stats = {'Player': name.split()[-1], 'Rank': rank}
            stats.update(stat_calcs(all_m))
            results.append(stats)
    result_df = pd.DataFrame(results)
    if result_df.empty:
        return result_df
    return result_df.sort_values('Rank').reset_index(drop=True)


def calculate_ace_stats(matches_df, players_df, start_date=None, end_date=None):
    """Calculate ace and double fault rates per player, including rank."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    min_matches = calculate_min_matches(start_date, end_date, base_min=20)
    def calc(df):
        return {
            'Ace Rate %': round((df['aces'] / df['svpt']).mean() * 100, 1),
            'DF Rate %': round((df['df'] / df['svpt']).mean() * 100, 1),
        }
    return _calculate_player_stats(
        matches_df, players_df,
        ['w_ace', 'w_df', 'w_svpt'], ['l_ace', 'l_df', 'l_svpt'], ['aces', 'df', 'svpt'],
        calc, min_matches=min_matches
    )


def calculate_1st_serve_stats(matches_df, players_df, start_date=None, end_date=None):
    """Calculate first serve percentages per player, including rank."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    min_matches = calculate_min_matches(start_date, end_date, base_min=20)
    def calc(df):
        return {
            '1st Serve %': round((df['1stIn'] / df['svpt']).mean() * 100, 1),
            '1st Serve Won %': round((df['1stWon'] / df['1stIn']).mean() * 100, 1),
        }
    return _calculate_player_stats(
        matches_df, players_df,
        ['w_1stIn', 'w_svpt', 'w_1stWon'], ['l_1stIn', 'l_svpt', 'l_1stWon'],
        ['1stIn', 'svpt', '1stWon'], calc, min_matches=min_matches
    )


def calculate_bp_stats(matches_df, players_df, start_date=None, end_date=None):
    """Calculate break point stats per player, including rank."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    # Dynamic threshold based on date range (base 50, scales down for shorter periods)
    min_bp = calculate_min_matches(start_date, end_date, base_min=50)
    results = []
    for _, player in players_df.iterrows():
        pid, name, rank = player['player_id'], player['full_name'], player['rank']
        wins = matches_df[matches_df['winner_id'] == pid]
        losses = matches_df[matches_df['loser_id'] == pid]
        bp_faced = wins['w_bpFaced'].sum() + losses['l_bpFaced'].sum()
        bp_saved = wins['w_bpSaved'].sum() + losses['l_bpSaved'].sum()
        bp_opp = wins['l_bpFaced'].sum() + losses['w_bpFaced'].sum()
        bp_conv = (wins['l_bpFaced'].sum() - wins['l_bpSaved'].sum()) + (losses['w_bpFaced'].sum() - losses['w_bpSaved'].sum())
        if bp_faced >= min_bp and bp_opp >= min_bp:
            results.append({
                'Player': name.split()[-1],
                'Rank': rank,
                'BP Save %': round(bp_saved / bp_faced * 100, 1),
                'BP Convert %': round(bp_conv / bp_opp * 100, 1),
            })
    df = pd.DataFrame(results)
    if df.empty:
        return df
    return df.sort_values('Rank').reset_index(drop=True)


def calc_tour_averages(matches, start_date=None, end_date=None):
    """Calculate tour-wide serve averages."""
    matches = filter_by_date_range(matches, start_date, end_date)
    return {
        'Aces/Match': matches['w_ace'].mean() + matches['l_ace'].mean(),
        '1st Serve In %': (matches['w_1stIn'] / matches['w_svpt']).mean() * 100,
        '1st Serve Won %': (matches['w_1stWon'] / matches['w_1stIn']).mean() * 100,
        '2nd Serve Won %': (matches['w_2ndWon'] / (matches['w_svpt'] - matches['w_1stIn'])).mean() * 100
    }


def prepare_serve_features(matches_df, start_date=None, end_date=None):
    """Prepare serve features and calculate winner-loser differentials."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    df = matches_df.copy()
    for p in ['w', 'l']:
        df[f'{p}_1st_pct'] = df[f'{p}_1stIn'] / df[f'{p}_svpt'] * 100
        df[f'{p}_1st_won_pct'] = df[f'{p}_1stWon'] / df[f'{p}_1stIn'] * 100
        second = df[f'{p}_svpt'] - df[f'{p}_1stIn']
        df[f'{p}_2nd_won_pct'] = np.where(second > 0, df[f'{p}_2ndWon'] / second * 100, np.nan)
        df[f'{p}_bp_save_pct'] = np.where(df[f'{p}_bpFaced'] > 0, df[f'{p}_bpSaved'] / df[f'{p}_bpFaced'] * 100, np.nan)
        df[f'{p}_ace_rate'] = df[f'{p}_ace'] / df[f'{p}_svpt'] * 100

    # Original names: diff_1st_pct, diff_1st_won, diff_2nd_won, diff_bp_save, diff_ace_rate
    diff_mapping = {'1st_pct': 'diff_1st_pct', '1st_won_pct': 'diff_1st_won',
                    '2nd_won_pct': 'diff_2nd_won', 'bp_save_pct': 'diff_bp_save',
                    'ace_rate': 'diff_ace_rate'}
    for stat, diff_col in diff_mapping.items():
        df[diff_col] = df[f'w_{stat}'] - df[f'l_{stat}']
    return df.replace([np.inf, -np.inf], np.nan)


def calculate_recent_vs_career(matches_df, players_df, n_recent=20, start_date=None, end_date=None):
    """Compare recent form (last n matches) to career averages."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    results = []
    for _, player in players_df.iterrows():
        pid = player['player_id']
        name = player['full_name']
        rank = player['rank']

        # Get all matches for player
        wins = matches_df[matches_df['winner_id'] == pid].copy()
        losses = matches_df[matches_df['loser_id'] == pid].copy()

        # Calculate ace rate for each match
        wins['ace_rate'] = wins['w_ace'] / wins['w_svpt']
        wins['match_date'] = wins['tourney_date']
        losses['ace_rate'] = losses['l_ace'] / losses['l_svpt']
        losses['match_date'] = losses['tourney_date']

        all_matches = pd.concat([
            wins[['match_date', 'ace_rate']],
            losses[['match_date', 'ace_rate']]
        ]).dropna().sort_values('match_date', ascending=False)

        if len(all_matches) >= n_recent:
            recent = all_matches.head(n_recent)
            career = all_matches

            recent_ace = recent['ace_rate'].mean() * 100
            career_ace = career['ace_rate'].mean() * 100
            delta = recent_ace - career_ace

            results.append({
                'Player': name.split()[-1],
                'Rank': rank,
                'Recent Ace %': round(recent_ace, 2),
                'Career Ace %': round(career_ace, 2),
                'Delta': round(delta, 2),
                'Trend': 'up' if delta > 0.3 else ('down' if delta < -0.3 else 'stable')
            })

    result_df = pd.DataFrame(results)
    if result_df.empty:
        return result_df
    return result_df.sort_values('Rank').reset_index(drop=True)


def serve_by_surface(matches_df, start_date=None, end_date=None):
    """Calculate serve stats by surface."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    # Dynamic threshold for minimum matches per surface
    min_surf_matches = calculate_min_matches(start_date, end_date, base_min=50)
    results = []
    for surface in ['Hard', 'Clay', 'Grass']:
        surf = matches_df[matches_df['surface'] == surface].dropna(subset=['w_ace', 'w_svpt'])
        if len(surf) >= min_surf_matches:
            results.append({
                'Surface': surface,
                'Aces/Match': round((surf['w_ace'] + surf['l_ace']).mean(), 1),
                '1st Won %': round((surf['w_1stWon'] / surf['w_1stIn']).mean() * 100, 1),
            })
    # Return empty DataFrame with correct columns if no results
    if not results:
        return pd.DataFrame(columns=['Surface', 'Aces/Match', '1st Won %'])
    return pd.DataFrame(results)


def player_surface_stats(matches_df, players_df, start_date=None, end_date=None):
    """Calculate serve stats by surface for each player."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)
    results = []
    for _, player in players_df.iterrows():
        pid = player['player_id']
        name = player['full_name'].split()[-1]
        rank = player['rank']

        for surface in ['Hard', 'Clay', 'Grass']:
            surf_matches = matches_df[matches_df['surface'] == surface]
            wins = surf_matches[surf_matches['winner_id'] == pid]
            losses = surf_matches[surf_matches['loser_id'] == pid]

            all_aces = pd.concat([wins['w_ace'], losses['l_ace']])
            all_svpt = pd.concat([wins['w_svpt'], losses['l_svpt']])

            if len(all_aces.dropna()) >= 10:
                ace_rate = (all_aces / all_svpt).mean() * 100
                results.append({
                    'Player': name,
                    'Rank': rank,
                    'Surface': surface,
                    'Ace Rate %': round(ace_rate, 1),
                    'Matches': len(all_aces.dropna())
                })

    return pd.DataFrame(results)


def calc_predictive(matches_df, start_date=None, end_date=None):
    """Calculate how often winner has better serve stat."""
    matches_df = filter_by_date_range(matches_df, start_date, end_date)

    # Handle empty input
    if matches_df.empty:
        return pd.DataFrame(columns=['Stat', 'Winner Better %'])

    df = matches_df.copy()
    df['w_1st_won'] = df['w_1stWon'] / df['w_1stIn']
    df['l_1st_won'] = df['l_1stWon'] / df['l_1stIn']
    df['w_2nd_won'] = df['w_2ndWon'] / (df['w_svpt'] - df['w_1stIn'])
    df['l_2nd_won'] = df['l_2ndWon'] / (df['l_svpt'] - df['l_1stIn'])
    df['w_ace'] = df['w_ace'] / df['w_svpt']
    df['l_ace'] = df['l_ace'] / df['l_svpt']
    df['w_bp'] = df['w_bpSaved'] / df['w_bpFaced'].replace(0, np.nan)
    df['l_bp'] = df['l_bpSaved'] / df['l_bpFaced'].replace(0, np.nan)
    df = df.dropna()

    # Handle case where dropna removes all rows
    if df.empty:
        return pd.DataFrame(columns=['Stat', 'Winner Better %'])

    return pd.DataFrame([
        {'Stat': '1st Serve Won %', 'Winner Better %': round((df['w_1st_won'] > df['l_1st_won']).mean() * 100, 1)},
        {'Stat': '2nd Serve Won %', 'Winner Better %': round((df['w_2nd_won'] > df['l_2nd_won']).mean() * 100, 1)},
        {'Stat': 'Ace Rate', 'Winner Better %': round((df['w_ace'] > df['l_ace']).mean() * 100, 1)},
        {'Stat': 'BP Save %', 'Winner Better %': round((df['w_bp'] > df['l_bp']).mean() * 100, 1)},
    ])


# =============================================================================
# Comparative & Trend Analysis
# =============================================================================

def calculate_player_comparison(stats_df, highlight_player, stat_cols):
    """Calculate how highlighted player compares to others in the group.

    Returns dict with player stats, group average, and deltas.
    """
    if not highlight_player or highlight_player not in stats_df['Player'].values:
        return None

    player_row = stats_df[stats_df['Player'] == highlight_player].iloc[0]
    others = stats_df[stats_df['Player'] != highlight_player]

    if len(others) == 0:
        return None

    comparison = {
        'player': highlight_player,
        'rank': int(player_row['Rank']),
        'stats': {}
    }

    for col in stat_cols:
        player_val = player_row[col]
        others_avg = others[col].mean()
        delta = player_val - others_avg
        comparison['stats'][col] = {
            'value': round(player_val, 1),
            'avg': round(others_avg, 1),
            'delta': round(delta, 1),
            'better': delta > 0 if 'DF' not in col else delta < 0  # Lower DF is better
        }

    return comparison


def calculate_trend_stats(matches_df, players_df, player_name, stat_type='ace',
                          recent_days=365, min_matches=10):
    """Calculate trend data for a player (recent vs earlier performance).

    stat_type: 'ace' for ace stats, '1st' for first serve, 'bp' for break points
    Returns dict with recent and earlier stats, or None if insufficient data.
    """
    from datetime import datetime, timedelta

    # Find player ID
    player_row = players_df[players_df['full_name'].str.endswith(player_name)]
    if len(player_row) == 0:
        return None

    pid = player_row.iloc[0]['player_id']
    cutoff_date = pd.Timestamp(datetime.today() - timedelta(days=recent_days))

    # Get wins and losses
    wins = matches_df[matches_df['winner_id'] == pid].copy()
    losses = matches_df[matches_df['loser_id'] == pid].copy()

    if stat_type == 'ace':
        wins['stat1'] = wins['w_ace'] / wins['w_svpt'] * 100  # Ace Rate
        wins['stat2'] = wins['w_df'] / wins['w_svpt'] * 100   # DF Rate
        losses['stat1'] = losses['l_ace'] / losses['l_svpt'] * 100
        losses['stat2'] = losses['l_df'] / losses['l_svpt'] * 100
    elif stat_type == '1st':
        wins['stat1'] = wins['w_1stIn'] / wins['w_svpt'] * 100  # 1st Serve %
        wins['stat2'] = wins['w_1stWon'] / wins['w_1stIn'] * 100  # 1st Won %
        losses['stat1'] = losses['l_1stIn'] / losses['l_svpt'] * 100
        losses['stat2'] = losses['l_1stWon'] / losses['l_1stIn'] * 100
    elif stat_type == 'bp':
        # BP stats need aggregation, not per-match averages
        wins['stat1'] = wins['w_bpSaved'] / wins['w_bpFaced'].replace(0, np.nan) * 100
        wins['stat2'] = (wins['l_bpFaced'] - wins['l_bpSaved']) / wins['l_bpFaced'].replace(0, np.nan) * 100
        losses['stat1'] = losses['l_bpSaved'] / losses['l_bpFaced'].replace(0, np.nan) * 100
        losses['stat2'] = (losses['w_bpFaced'] - losses['w_bpSaved']) / losses['w_bpFaced'].replace(0, np.nan) * 100

    wins['match_date'] = wins['tourney_date']
    losses['match_date'] = losses['tourney_date']

    all_matches = pd.concat([
        wins[['match_date', 'stat1', 'stat2']],
        losses[['match_date', 'stat1', 'stat2']]
    ]).dropna()

    recent = all_matches[all_matches['match_date'] >= cutoff_date]
    earlier = all_matches[all_matches['match_date'] < cutoff_date]

    if len(recent) < min_matches or len(earlier) < min_matches:
        return None

    return {
        'recent': {
            'x': round(recent['stat1'].mean(), 1),
            'y': round(recent['stat2'].mean(), 1),
            'n_matches': len(recent)
        },
        'earlier': {
            'x': round(earlier['stat1'].mean(), 1),
            'y': round(earlier['stat2'].mean(), 1),
            'n_matches': len(earlier)
        }
    }


# =============================================================================
# Visualization Helpers
# =============================================================================

def create_scatter_with_filters(df, color, x_col, y_col, x_label, y_label, div_id):
    """Create interactive scatter plot with player toggles and vertical legend."""
    fig = go.Figure()

    # Add one trace per player (sorted by rank from df)
    for i, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row[x_col]], y=[row[y_col]],
            mode='markers+text',
            text=[row['Player']], textposition='top center',
            textfont=dict(size=9),
            marker=dict(size=10, color=color),
            name=row['Player'],
            hovertemplate=f"{row['Player']} (#{row['Rank']})<br>{x_label}: %{{x}}<br>{y_label}: %{{y}}<extra></extra>"
        ))

    # Compact vertical legend on right (no per-chart buttons - using global control)
    fig.update_layout(
        legend=dict(
            orientation="v",
            yanchor="top", y=0.95,
            xanchor="left", x=1.02,
            itemclick="toggle",
            itemdoubleclick="toggleothers"
        ),
        xaxis_title=x_label,
        yaxis_title=y_label,
        height=500,
        margin=dict(t=60, r=150)
    )

    # Add average reference lines
    fig.add_hline(y=df[y_col].mean(), line_dash='dash', line_color='gray', opacity=0.5)
    fig.add_vline(x=df[x_col].mean(), line_dash='dash', line_color='gray', opacity=0.5)

    return fig
