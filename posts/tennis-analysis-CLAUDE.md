# Tennis Analysis CLAUDE.md

Project-specific instructions for tennis analysis notebooks and data.

## Data Sources

**Raw Data:** Jeff Sackmann's Tennis Abstract repositories (CC BY-NC-SA 4.0)
- ATP: `data/tennis_atp/` (git submodule)
- WTA: `data/tennis_wta/` (git submodule)

**Extracted Subsets:**
- `data/top10/` - Top 10 players (Dec 30, 2024 rankings)
- `data/top25/` - Top 25 players

### Data Files Structure

Each tour directory (`atp/`, `wta/`) contains:
- `*_topN_players.csv` - Player biographical data
- `*_topN_rankings.csv` - Complete ranking history
- `*_topN_matches.csv` - All matches involving these players

### Key Columns

**Players:**
| Column | Description |
|--------|-------------|
| `player_id` | Unique identifier (use for joins) |
| `name_first`, `name_last` | Name components |
| `full_name` | Created as `name_first + ' ' + name_last` |
| `hand` | L/R |
| `dob` | Date of birth (YYYYMMDD format) |
| `ioc` | Country code |
| `height` | In centimeters |

**Matches:**
| Column | Description |
|--------|-------------|
| `tourney_date` | Tournament date (YYYYMMDD, parse to datetime) |
| `surface` | Hard, Clay, Grass, Carpet |
| `tourney_level` | G=Grand Slam, M=Masters, A=ATP 500/250, F=Finals, D=Davis/BJK Cup |
| `winner_id`, `loser_id` | Player IDs |
| `score` | Match score string |
| `minutes` | Match duration |

**Serve Statistics (prefixed `w_` for winner, `l_` for loser):**
| Column | Description |
|--------|-------------|
| `*_ace` | Aces |
| `*_df` | Double faults |
| `*_svpt` | Total serve points |
| `*_1stIn` | First serves in |
| `*_1stWon` | Points won on first serve |
| `*_2ndWon` | Points won on second serve |
| `*_bpSaved` | Break points saved |
| `*_bpFaced` | Break points faced |

## Notebooks

### `posts/tennis-eda/tennis-eda.ipynb`
Interactive dashboard with Top 10 player analysis:
- Player overview and win rates
- Rankings history with range slider
- Surface performance heatmaps
- Head-to-head matrices
- Serve analysis
- Tournament level performance

### `posts/serve-analysis/serve-analysis.ipynb`
Deep dive into serve statistics with Top 25 players:
- Tour averages comparison
- Winner vs loser differentials
- Ace production scatter plots
- First serve accuracy vs effectiveness
- Break point performance
- Surface impact on serve stats

## Code Patterns

### Data Loading
```python
DATA_PATH = '../../data/top25'  # or top10
atp_players = pd.read_csv(f'{DATA_PATH}/atp/atp_top25_players.csv')
atp_matches = pd.read_csv(f'{DATA_PATH}/atp/atp_top25_matches.csv')
wta_players = pd.read_csv(f'{DATA_PATH}/wta/wta_top25_players.csv')
wta_matches = pd.read_csv(f'{DATA_PATH}/wta/wta_top25_matches.csv')

# Always create full_name
for df in [atp_players, wta_players]:
    df['full_name'] = df['name_first'] + ' ' + df['name_last']

# Parse dates
atp_matches['tourney_date'] = pd.to_datetime(atp_matches['tourney_date'].astype(str), format='%Y%m%d')
```

### Filtering for Serve Data
```python
serve_cols = ['w_ace', 'w_df', 'w_svpt', 'w_1stIn', 'w_1stWon', 'w_2ndWon', 'w_SvGms', 'w_bpSaved', 'w_bpFaced']
atp_serve_matches = atp_matches.dropna(subset=serve_cols)
```

### Player Statistics Pattern
```python
def calculate_stats(matches_df, players_df):
    results = []
    for _, player in players_df.iterrows():
        pid, name = player['player_id'], player['full_name']

        # Get wins and losses separately
        wins = matches_df[matches_df['winner_id'] == pid][['w_col1', 'w_col2']].copy()
        wins.columns = ['col1', 'col2']  # Normalize column names
        losses = matches_df[matches_df['loser_id'] == pid][['l_col1', 'l_col2']].copy()
        losses.columns = ['col1', 'col2']

        all_matches = pd.concat([wins, losses]).dropna()

        if len(all_matches) >= 20:  # Minimum match threshold
            results.append({
                'Player': name.split()[-1],  # Last name only for display
                'Stat': calculate_something(all_matches)
            })
    return pd.DataFrame(results)
```

### Adding Rank (if needed for sorting)
```python
# CSV row order may not equal ranking - add explicit rank if available
atp_players['rank'] = range(1, len(atp_players) + 1)
```

## Visualization Patterns

### Tour Colors
- **ATP:** `#1f77b4` (blue)
- **WTA:** `#e377c2` (pink)

### Panel Tabsets for ATP/WTA
```markdown
::: {.panel-tabset}

## ATP
```python code here```

## WTA
```python code here```

:::
```

### Interactive Scatter with Player Selection
```python
def create_scatter_with_filters(df, color, x_col, y_col, x_label, y_label, div_id):
    fig = go.Figure()
    for i, row in df.iterrows():
        fig.add_trace(go.Scatter(
            x=[row[x_col]], y=[row[y_col]],
            mode='markers+text',
            text=[row['Player']], textposition='top center',
            marker=dict(size=10, color=color),
            name=row['Player']
        ))
    # Add reference lines at mean
    fig.add_hline(y=df[y_col].mean(), line_dash='dash', line_color='gray', opacity=0.5)
    fig.add_vline(x=df[x_col].mean(), line_dash='dash', line_color='gray', opacity=0.5)
    return fig

# Use with custom div_id for JavaScript targeting
html = fig.to_html(full_html=False, include_plotlyjs=False, div_id='my-chart-id')
display(HTML(html))
```

### Global Player Selection Widget
When multiple charts need synchronized player filtering, use:
1. Calculate all stats upfront in a single cell
2. Create canonical player list (intersection of all charts)
3. Add HTML/JS widget with `display(HTML(widget_html))`
4. Use `Plotly.restyle(el, {visible: visibility_array})` to sync charts

## Extract Scripts

### `data/extract_top10.py`
Extracts top 10 player data. Modify `ATP_TOP_10` and `WTA_TOP_10` lists with player IDs.

### `data/extract_top25.py`
Same pattern for top 25 players.

To run:
```bash
cd data
python extract_top25.py
```

## Testing

```bash
# Render single notebook
quarto render posts/serve-analysis/serve-analysis.ipynb --execute

# Preview site
quarto preview
```

## Common Issues

1. **Missing serve data:** Many older matches lack serve statistics. Filter with `dropna(subset=serve_cols)`.

2. **Player ID mismatches:** Always join on `player_id`, not name (names can have variants).

3. **Date parsing:** Dates are stored as YYYYMMDD integers. Use `format='%Y%m%d'` with `pd.to_datetime()`.

4. **JavaScript in f-strings:** When embedding JS in Python f-strings, escape braces `{{` and `}}`. For template literals with `${}`, use string concatenation: `'.' + tour + '-player'` instead of template syntax.

5. **Plotly in Quarto:** Use `fig.to_html(full_html=False, include_plotlyjs=False, div_id='unique-id')` for charts that need JavaScript interaction. Quarto includes Plotly globally.
