"""Seed registry + permanent games database + audit replay.
Spec 1: every game gets a mechanical seed (BASE + counter) assigned BEFORE simulation;
box scores stored permanently; any game reproducible via replay_game(game_id).
"""
import pickle, os
import pbp_engine as E

DB_PATH = '/home/claude/cfb2/state/games_db.pkl'
REG_PATH = '/home/claude/cfb2/state/seed_registry.pkl'

def _load(path, default):
    if os.path.exists(path):
        with open(path,'rb') as f: return pickle.load(f)
    return default

def load_db():  return _load(DB_PATH, {})
def load_reg(): return _load(REG_PATH, {"base": E.BASE_SEED, "counter": 0, "assigned": {}})

def save_db(db):
    with open(DB_PATH,'wb') as f: pickle.dump(db, f)
def save_reg(r):
    with open(REG_PATH,'wb') as f: pickle.dump(r, f)

def assign_seed(reg, game_id):
    """Mechanical: seed exists before the game does. Never reassigned (double-sim guard)."""
    if game_id in reg["assigned"]:
        raise RuntimeError(f"DOUBLE-SIM GUARD: {game_id} already has seed {reg['assigned'][game_id]}")
    seed = reg["base"] + reg["counter"]
    reg["assigned"][game_id] = seed
    reg["counter"] += 1
    return seed

def play_and_store(game_id, home, away, site="home", rivalry=False,
                   unavailable_home=frozenset(), unavailable_away=frozenset()):
    db, reg = load_db(), load_reg()
    if game_id in db:
        raise RuntimeError(f"DOUBLE-SIM GUARD: {game_id} already in games_db")
    seed = assign_seed(reg, game_id)
    box, _pbp = E.simulate_game(home, away, seed, site=site, rivalry=rivalry,
                                unavailable_home=unavailable_home, unavailable_away=unavailable_away,
                                keep_pbp=False)   # pbp reproducible on demand; box stored permanently
    box["game_id"] = game_id
    box["unav_h"] = sorted(unavailable_home); box["unav_a"] = sorted(unavailable_away)
    db[game_id] = box
    save_db(db); save_reg(reg)
    return box

def replay_game(game_id, with_pbp=True):
    """Audit: deterministic replay from stored seed. Must reproduce the stored final exactly."""
    db = load_db()
    if game_id not in db: raise KeyError(game_id)
    b = db[game_id]
    box, pbp = E.simulate_game(b["home"], b["away"], b["seed"], site=b["site"], rivalry=b["rivalry"],
                               unavailable_home=frozenset(b["unav_h"]), unavailable_away=frozenset(b["unav_a"]),
                               keep_pbp=with_pbp)
    verified = (box["home_score"], box["away_score"]) == (b["home_score"], b["away_score"])
    return box, pbp, verified

if __name__ == "__main__":
    # demo: store one game, then replay-audit it
    for p in (DB_PATH, REG_PATH):
        if os.path.exists(p): os.remove(p)
    box = play_and_store("DEMO_Lornaman_Ciarralotta", "Lornaman", "Ciarralotta", site="neutral")
    print(f"stored: {box['game_id']} seed={box['seed']}  {box['away']} {box['away_score']} - {box['home_score']} {box['home']}")
    rbox, rpbp, ok = replay_game("DEMO_Lornaman_Ciarralotta")
    print("REPLAY AUDIT:", "VERIFIED - identical" if ok else "MISMATCH!")
    print(f"replayed {len(rpbp)} plays; last scoring play: {rbox['scoring_plays'][-1]['desc']}")
    try:
        play_and_store("DEMO_Lornaman_Ciarralotta", "Lornaman", "Ciarralotta")
    except RuntimeError as e:
        print("double-sim guard:", e)
