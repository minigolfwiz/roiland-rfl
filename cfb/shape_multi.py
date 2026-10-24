import sys, statistics; sys.path.insert(0,'/home/claude/cfb2')
import season_shape as SS
rows=[]
for k,off in enumerate((8_100_000, 8_200_000, 8_300_000, 8_400_000)):
    r=SS.run(off)
    rows.append(r)
    print("  seed %d: und %d | 0-1L %d | best %-5s | top5 mL %.1f | top15 mL %.1f | max15 %d | pts %.2f"%(
        k+1,r['undefeated'],r['zero_or_one'],r['best_record'],r['top5_mean_losses'],
        r['top15_mean_losses'],r['top15_max_losses'],r['pts_per_team']))
print()
print("  MEAN over %d seasons: und %.2f | 0-1L %.1f | top5 mL %.2f | top15 mL %.2f | pts %.2f"%(
    len(rows),
    statistics.mean(r['undefeated'] for r in rows),
    statistics.mean(r['zero_or_one'] for r in rows),
    statistics.mean(r['top5_mean_losses'] for r in rows),
    statistics.mean(r['top15_mean_losses'] for r in rows),
    statistics.mean(r['pts_per_team'] for r in rows)))
print("  CANON 12-season mean:  und 0.08 | 0-1L 2.0 | top5 mL 1.62 | top15 mL 2.36")
