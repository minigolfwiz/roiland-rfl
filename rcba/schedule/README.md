# RCBA 21-22 Schedule Garden

Source for the Schedule Garden artifact (season starts Mon Nov 1, 2021; ends Sun Mar 6, 2022).

- `engine.js`: conference rotations, tournaments, budget tiers and styles, non-conference matching and dating.
- `data.json`: 374 schools (conference, state, map xy, prestige, alumni, conference strength, titles) plus 41 host cities and tier cut points.
- `ui.html` + `build.py`: page template; `python3 build.py` inlines data and engine into `page.html`.
- Autosave lives in the artifact db: `plan2122/meta` and `plan2122/games`.
