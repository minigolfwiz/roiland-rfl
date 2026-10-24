"""Sim window orchestrator: simulate weeks -> rebuild site -> print report (spec 8 + 12)."""
import sys; sys.path.insert(0,'/home/claude/cfb2')
import season as SE
import media_poll as MP
import webapp as SITE

def run(n_weeks=1):
    s = SE.simulate_window(n_weeks)
    path, size = SITE.build_site()
    wk = s["next_week"] - 1
    print(f"=== through Week {wk} | site rebuilt: {path} ({size/1e6:.1f} MB) ===")
    t40, R = SE.top40(s, with_ratings=True)
    _mp, _ = MP.compute_media_poll(s)
    s["media_poll_current"] = _mp
    print("Top 10 (NET):", ", ".join(f"{i+1}. {t} ({s['record'][t]['W']}-{s['record'][t]['L']}, EM {R['em'][t]:+.1f})" for i, t in enumerate(t40[:10])))
    print()
    for line in SE.storylines(s, n_weeks=n_weeks):
        print(" -", line)
    return s

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    run(n)
