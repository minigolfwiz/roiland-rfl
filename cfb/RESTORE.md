# Roiland CFB — restore notes
Code and templates live in this folder. Live state is gzipped under `state/` (season_state, rosters, coaches, universe, sub_rosters, seed_registry).
To restore: copy this folder to `/home/claude/cfb2`, then `gunzip -k state/*.pkl.gz`.
`games_db.pkl` (the all-time results database) is stored separately as split gzip parts under `state/games_db/` when present; join with `cat games_db.pkl.gz.part* | gunzip > state/games_db.pkl`.
Progress log: `PENDING.md`. Committed after each offseason stage / week.
