# Tennis Top 10 Player Data

Data extracted from [Jeff Sackmann's Tennis Abstract repositories](https://github.com/JeffSackmann), licensed under CC BY-NC-SA 4.0.

**Rankings as of:** December 30, 2024

## ATP Top 10

| Rank | Player | Country |
|------|--------|---------|
| 1 | Jannik Sinner | ITA |
| 2 | Alexander Zverev | GER |
| 3 | Carlos Alcaraz | ESP |
| 4 | Taylor Fritz | USA |
| 5 | Daniil Medvedev | RUS |
| 6 | Casper Ruud | NOR |
| 7 | Novak Djokovic | SRB |
| 8 | Andrey Rublev | RUS |
| 9 | Alex De Minaur | AUS |
| 10 | Grigor Dimitrov | BUL |

## WTA Top 10

| Rank | Player | Country |
|------|--------|---------|
| 1 | Aryna Sabalenka | BLR |
| 2 | Iga Swiatek | POL |
| 3 | Coco Gauff | USA |
| 4 | Jasmine Paolini | ITA |
| 5 | Qinwen Zheng | CHN |
| 6 | Elena Rybakina | KAZ |
| 7 | Jessica Pegula | USA |
| 8 | Emma Navarro | USA |
| 9 | Daria Kasatkina | RUS |
| 10 | Barbora Krejcikova | CZE |

## Data Files

### `/atp/` and `/wta/` directories

- `*_top10_players.csv` - Player biographical data (name, DOB, country, height, hand)
- `*_top10_rankings.csv` - Complete ranking history for each player
- `*_top10_matches.csv` - All matches involving these players (as winner or loser)

### Column Reference

**Players:**
- `player_id`, `name_first`, `name_last`, `hand` (L/R), `dob` (YYYYMMDD), `ioc` (country code), `height` (cm), `wikidata_id`

**Rankings:**
- `ranking_date`, `rank`, `player` (player_id), `points`

**Matches:**
- Tournament info: `tourney_id`, `tourney_name`, `surface`, `draw_size`, `tourney_level`, `tourney_date`
- Match info: `match_num`, `score`, `best_of`, `round`, `minutes`
- Winner/Loser: `*_id`, `*_seed`, `*_entry`, `*_name`, `*_hand`, `*_ht`, `*_ioc`, `*_age`, `*_rank`, `*_rank_points`
- Stats: `w_ace`, `w_df`, `w_svpt`, `w_1stIn`, `w_1stWon`, `w_2ndWon`, `w_SvGms`, `w_bpSaved`, `w_bpFaced` (and `l_*` for loser)

## Data Source

- ATP: https://github.com/JeffSackmann/tennis_atp
- WTA: https://github.com/JeffSackmann/tennis_wta
