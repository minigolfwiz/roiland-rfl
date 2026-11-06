"""Repo packing for the big games database (Dan approved 5 Nov 2026 to slim weekly uploads).
games_db.pkl is split into one gzip per SEASON (state/games_db_shards/sNN.pkl.gz). Shards are
byte-deterministic (protocol 4, gzip mtime=0), so a finished season never changes and git only
stores the current season's shard each week.
  python3 repo_pack.py pack   [state_dir] [out_dir]   # games_db.pkl -> shards
  python3 repo_pack.py unpack [shard_dir] [state_dir] # shards -> games_db.pkl  (use on a fresh clone)
"""
import sys, os, re, gzip, pickle, glob, collections, hashlib

def _seas(k):
    m = re.match(r'S(\d+)', str(k)); return int(m.group(1)) if m else 0

def _gz(b):
    import io, zlib
    buf = io.BytesIO()
    with gzip.GzipFile(fileobj=buf, mode='wb', compresslevel=9, mtime=0) as g: g.write(b)
    return buf.getvalue()

def pack(state='state', out=None):
    out = out or os.path.join(state, 'games_db_shards'); os.makedirs(out, exist_ok=True)
    db = pickle.load(open(os.path.join(state, 'games_db.pkl'), 'rb'))
    by = collections.OrderedDict()
    for k, v in db.items(): by.setdefault(_seas(k), {})[k] = v
    for sn, sub in by.items():
        sub = pickle.loads(pickle.dumps(sub, protocol=4))      # normalise object sharing
        open(os.path.join(out, 's%02d.pkl.gz' % sn), 'wb').write(_gz(pickle.dumps(sub, protocol=4)))
    return len(db), len(by)

def unpack(shards, state='state'):
    db = {}
    for p in sorted(glob.glob(os.path.join(shards, 's*.pkl.gz')), key=lambda p: int(re.findall(r's(\d+)', os.path.basename(p))[0])):
        db.update(pickle.load(gzip.open(p, 'rb')))
    pickle.dump(db, open(os.path.join(state, 'games_db.pkl'), 'wb'))
    return len(db)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == 'pack': print(pack(*(a[1:3])))
    elif a and a[0] == 'unpack': print(unpack(*(a[1:3])))
    else: print(__doc__)
