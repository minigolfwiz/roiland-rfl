"""Payload for the Map Office: every state (seed + adjacency), every school (369), every named city."""
import sys, json
sys.path.insert(0, '/home/claude/cfb2')
import pbp_engine as E, committee as CM

def main(out='/home/claude/cfb2/state/map_office.json'):
    U = E.U
    states = [{"name": s, "x": xy[0], "y": xy[1], "adj": U["state_adj"].get(s, [])} for s, xy in U["state_coords"].items()]
    schools = []
    for name, info in U["schools"].items():
        fbs = info["level"] == "FBS"
        g = CM.GEO.get(name, {})
        conf = U["team_conf"].get(name)
        locked = (U.get("school_coords") or {}).get(name)
        schools.append({"id": name, "full": g.get("full_name", name), "state": info["state"], "level": "FBS" if fbs else "SUB", "locked": list(locked) if locked else None,
                        "conf": conf, "tier": U["tiers"].get(conf) if conf else None,
                        "colors": U["team_colors"].get(name, ["#555", "#999"]) if fbs else ["#777", "#bbb"]})
    cities = {}
    def add(city, st, role):
        k = city + "|" + st
        cities.setdefault(k, {"name": city, "state": st, "roles": []})
        if role not in cities[k]["roles"]: cities[k]["roles"].append(role)
    for b, (c, st) in U["bowls"].items(): add(c, st, "bowl: " + b)
    for conf, (c, st) in U["ccg_sites"].items(): add(c, st, "title game: " + conf)
    for y, (c, st) in U["champ_sites"].items(): add(c, st, "national championship " + str(y))
    for c, st in U["host_cities"].items(): add(c, st, "host city")
    for c, st in U.get("champ_site_candidates", {}).items(): add(c, st, "championship candidate")
    add("Burke Bay", "Dove Island", "former bowl site (Lumber Bowl, to 2037)")
    import base64
    img = base64.b64encode(open('/home/claude/cfb2/state/roiland_map.png', 'rb').read()).decode()
    polys = json.load(open('/home/claude/cfb2/state/state_polygons.json'))
    for k, v in (U.get("city_coords") or {}).items():
        add(v["city"], v["state"], "placed in the Map Office" if v.get("custom") else "")
        cities[k]["locked"] = list(v["xy"]); cities[k]["custom"] = bool(v.get("custom"))
        cities[k]["roles"] = [r for r in cities[k]["roles"] if r]
    payload = {"states": states, "schools": schools, "cities": list(cities.values()),
               "img": "data:image/png;base64," + img, "img_size": polys["size"], "polys": polys["states"], "centroids": polys["centroids"],
               "confs": list(U["tiers"]), "tiers": U["tiers"]}
    json.dump(payload, open(out, "w"), separators=(",", ":"))
    return payload

if __name__ == "__main__":
    p = main(); print(len(p["states"]), "states", len(p["schools"]), "schools", len(p["cities"]), "cities")
