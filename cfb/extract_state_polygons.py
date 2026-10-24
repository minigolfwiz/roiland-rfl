"""State polygons for the Map Office, traced from Dan's map of Roiland (state/roiland_map.png, 596x596).
The sim's state_coords are pixel coordinates on this image, so the polygons are in sim map units.
Region ids are from skimage.measure.label on the land mask; the assignment was checked by eye (2040 postseason)."""
from PIL import Image; import numpy as np, sys, json
sys.path.insert(0, '/home/claude/cfb2'); import pbp_engine as E
from skimage import measure, segmentation
from scipy import ndimage
a = np.array(Image.open('/home/claude/cfb2/state/roiland_map.png').convert('RGB')).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
water = (b > r + 20) & (b > g); orange = (r > g + 20) & (r > b + 40); dark = (r + g + b) < 3 * 200
land = ~water & ~orange & ~dark
lab, n = measure.label(land, connectivity=1, return_num=True)
ASSIGN = {'Barhold': [43, 26], 'Diveo': [129], 'Tengus': [130], 'Crayellan': [131], 'Far Farris': [134], 'Skeenerland': [136], 'Riveral': [137],
          'Roosevelt': [138], 'East Costique': [147], 'Harrell': [148], 'Tasson': [149], 'Costique': [150], 'Rogaela': [154], 'Kaji Kita': [156],
          'Vaughn Bay': [159], 'Parchynt': [160], 'Fiota': [166], 'Verigon': [167], 'Kaji Daun': [170], 'Antiragal': [198], 'Lawiiri': [204],
          'Ranroman': [206], 'Natzumakis': [207], 'South Antiragal': [208, 214], 'Dove Island': [212], 'Stanton': [273], 'Orlot': [281],   # Dan, 2040: Stanton's north line is the wiggly border at y~447 (Kro Magloire St sits on it); region 214 above it is South Antiragal
          'Phangrine': [287], 'Ciarralotta': [221], 'Eona': [290], 'West Hatesei': [291], 'North Hatesei': [292], 'Hatesei': [294], 'Wolford': [295]}
masks = {nm: np.isin(lab, v) for nm, v in ASSIGN.items()}
def split(region, pairs):
    m = lab == region; dist = ndimage.distance_transform_edt(m); markers = np.zeros(m.shape, int); ys, xs = np.where(m)
    for i, (nm, (x, y)) in enumerate(pairs, 1):
        j = np.argmin((xs - x) ** 2 + (ys - y) ** 2); markers[ys[j], xs[j]] = i
    ws = segmentation.watershed(-dist, markers, mask=m)
    for i, (nm, _) in enumerate(pairs, 1): masks[nm] = ws == i
# Dan, 2040 postseason: Krobe is the whole long coastal region (209). Ekralund is the tiny wedge east of Orlot's
# vertical border, south of Stanton and west of Krobe's coast -- drawn in a lighter fill the land mask misses.
masks['Krobe'] = lab == 209
masks['Ekralund'] = ndimage.binary_dilation(lab == 282, iterations=1)   # ~7x9 px wedge: x 305-311, y 473-481
assert set(masks) == set(E.U['state_coords']), set(E.U['state_coords']) ^ set(masks)
polys, cent = {}, {}
for nm, m in masks.items():
    m = ndimage.binary_dilation(ndimage.binary_fill_holes(ndimage.binary_closing(m, iterations=1)), iterations=1)
    pad = np.pad(m, 1); out = []
    for c in measure.find_contours(pad.astype(float), 0.5):
        if len(c) < 16: continue
        c = measure.approximate_polygon(c, tolerance=0.9) - 1
        out.append([[round(float(x), 1), round(float(y), 1)] for y, x in c])
    polys[nm] = out; ys, xs = np.where(m); cent[nm] = [round(float(xs.mean()), 1), round(float(ys.mean()), 1)]
json.dump({'size': [596, 596], 'states': polys, 'centroids': cent}, open('/home/claude/cfb2/state/state_polygons.json', 'w'), separators=(',', ':'))
print({nm: len(p) for nm, p in polys.items() if len(p) != 1}, 'written')
