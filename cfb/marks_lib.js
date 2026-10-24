/* Roiland team marks — shared by the specimen board and the season viewer.
   Every input is a lookup: name, mascot, conference and the two colours Dan chose.
   Expects objects shaped { name, mascot, conf, col:[c1,c2] }. */
/* ---------- the typeface vocabulary, and what each one is for ---------- */
const FONTS = {
  gothic:   { css:'"UnifrakturCook", "Times New Roman", serif', w:700, tr:0,     label:"UnifrakturCook",
              why:"Ghosts, demons, goblins, krakens, ravens — anything that wants to look cursed." },
  classical:{ css:'"Cinzel", Georgia, serif',                   w:900, tr:0.02,  label:"Cinzel",
              why:"Senators, paladins, knights, dukes, monarchs. Roman capitals, carved rather than drawn." },
  slab:     { css:'"Alfa Slab One", Georgia, serif',            w:400, tr:-0.01, label:"Alfa Slab One",
              why:"Bulls, bison, rhinos, locomotives, lumberjacks — weight and brute force." },
  western:  { css:'"Rye", Georgia, serif',                      w:400, tr:0,     label:"Rye",
              why:"Cowboys, rangers, deputies, buccaneers, arrowheads. Frontier woodtype." },
  tech:     { css:'"Orbitron", "Arial Narrow", sans-serif',     w:900, tr:0.03,  label:"Orbitron",
              why:"Cosmonauts, rockets, chargers, cyclones, jets. Anything that moves fast." },
  blocky:   { css:'"Bungee", Impact, sans-serif',               w:400, tr:0,     label:"Bungee",
              why:"Hornets, spiders, rattlers, pythons, badgers — small, sharp and unpleasant." },
  chunky:   { css:'"Bowlby One SC", Verdana, sans-serif',       w:400, tr:0,     label:"Bowlby One SC",
              why:"Slugs, frogs, turtles, otters, whales, parrots. Friendly and round." },
  athletic: { css:'"Oswald", "Arial Narrow", sans-serif',       w:700, tr:0.01,  label:"Oswald",
              why:"Tigers, bears, wildcats, eagles, wolves. The classic condensed jersey face." },
  retro:    { css:'"Righteous", Verdana, sans-serif',           w:400, tr:0.01,  label:"Righteous",
              why:"Flames, allegiants, villagers, shakers — abstractions with no animal to lean on." },
  service:  { css:'"Archivo Black", Helvetica, sans-serif',     w:400, tr:0.01,  label:"Archivo Black",
              why:"The academies: Marines, Navy, Nauticals. Plain, heavy, institutional." },
};
const RULES = [
  ["service",  ["marine","navy","nautical","academy","cadet","admiral","midshipm"]],
  ["gothic",   ["ghost","demon","goblin","gremlin","kraken","monster","raven","crow",
                "vulture","saint","friar","monk","mystic","spectre","phantom","wraith","icefolk","werewol"]],
  ["classical",["senator","paladin","knight","valiant","duke","royal","monarch","cavalier",
                "noble","crusader","trumpeter","legion","emperor","lord","viscount"]],
  ["slab",     ["bull","bison","rhino","elephant","stampede","rumbler","hardhat","lumberjack",
                "locomotive","oiler","thresher","sequoia","spruce","hog","topper","krobber","viking"]],
  ["western",  ["cowboy","roughrider","ranger","deputy","marshall","mountaineer","buccaneer",
                "pirate","arrowhead","wrangler","rider","outlaw","miner"]],
  ["tech",     ["cosmonaut","rocket","charger","flyer","aviator","jacket","striker","cyclone",
                "kite","comet","jet"]],
  ["blocky",   ["hornet","spider","tarantula","rattler","rattlesnake","python","crab","urchin",
                "skunk","badger","hyena","raccoon","wasp","viper","scorpion"]],
  ["chunky",   ["slug","hopper","frog","toad","turtle","aardvark","hedgehog","gecko","pollywog",
                "olive","hare","camel","tapir","otter","mallard","loon","trout","cockatiel",
                "parrot","dolphin","whale","seacat","sandpiper","mockingbird","hummingbird",
                "rockhopper","islander","duck","bullfrog"]],
  ["retro",    ["flame","big blue","lavender","jersey","shaker","villager","spirit","mystic",
                "strike","rumble","delta"]],
];
/* keyword matching is greedy by nature — "bull" catches Bulldogs and Bullfrogs, which are
   a dog and a frog. Named exceptions are checked first and win outright. */
const OVERRIDE = {
  "Bulldogs":"athletic", "Bullfrogs":"chunky", "Delta Dogs":"athletic",
  "Allegiants":"retro", "Avians":"athletic", "Bullhorns":"slab",
};
function fontFor(mascot){
  if (OVERRIDE[mascot]) return OVERRIDE[mascot];
  const m = (mascot || "").toLowerCase();
  for (const [key, words] of RULES) if (words.some(w => m.includes(w))) return key;
  return "athletic";                      // predators and the classics
}

/* ---------- a shape for each conference ---------- */
const SHAPES = {
  "Power North":    "M16 1.6 29 5.8v10.4C29 23 23.4 28.4 16 30.4 8.6 28.4 3 23 3 16.2V5.8z",       // heater shield
  "Jyras Bay":      "M16 1.9A14.1 14.1 0 1 1 15.99 1.9z",                                            // roundel
  "Great Fourteen": "M3.4 3.4h25.2v16.2c0 5.4-5.6 9.2-12.6 11-7-1.8-12.6-5.6-12.6-11z",              // flat-top shield
  "Western Coast":  "M8.6 2.6h14.8a6 6 0 0 1 6 6v14.8a6 6 0 0 1-6 6H8.6a6 6 0 0 1-6-6V8.6a6 6 0 0 1 6-6z", // rounded square
  "Broad South":    "M16 1.9 28.1 8.9v14.2L16 30.1 3.9 23.1V8.9z",                                   // hexagon
  "Mountain Valley":"M16 1.8 29.2 12v12.4a4 4 0 0 1-4 4H6.8a4 4 0 0 1-4-4V12z",                       // peaked house
  "Vapor Stream":   "M16 1.8 30.2 16 16 30.2 1.8 16z",                                               // diamond
  "Low Sixteen":    "M11.4 2.6h9.2l8.8 8.8v9.2l-8.8 8.8h-9.2l-8.8-8.8v-9.2z",                        // octagon
  "Brass Belt":     "M16 2.2 20 4l4.4-1 1.6 4.3 4 2.3-1.6 4.3 1.6 4.3-4 2.3-1.6 4.3-4.4-1-4 1.8-4-1.8-4.4 1-1.6-4.3-4-2.3L4.2 16l-1.6-4.3 4-2.3L8.2 5l4.4 1z", // cog
  "East Forest":    "M16 1.6c6 5 10 10.2 10 15.4 0 6.4-4.4 11.4-10 13.4C10.4 28.4 6 23.4 6 17 6 11.8 10 6.6 16 1.6z", // leaf
  "Evening Star":   "M16 1.8l3.6 7.3 8.1 1.2-5.9 5.7 1.4 8-7.2-3.8-7.2 3.8 1.4-8-5.9-5.7 8.1-1.2z",  // star
  "Southwestern":   "M16 2.2 29.4 25.4a3.4 3.4 0 0 1-3 5.1H5.6a3.4 3.4 0 0 1-3-5.1z",                // triangle
  // guest programmes are not in a conference; a plain disc keeps them visibly apart
  "Subdivision":    "M16 3.4A12.6 12.6 0 1 1 15.99 3.4z",
};
const SHAPE_NOTE = {
  "Power North":"heater shield", "Jyras Bay":"roundel", "Great Fourteen":"flat-top shield",
  "Western Coast":"rounded square", "Broad South":"hexagon", "Mountain Valley":"peaked house",
  "Vapor Stream":"diamond", "Low Sixteen":"octagon", "Brass Belt":"cog", "East Forest":"leaf",
  "Evening Star":"star", "Southwestern":"triangle",
};

/* ---------- colour: the mark has to survive both page themes ---------- */
function lum(hex){
  const n = parseInt(hex.slice(1), 16);
  const f = v => { v /= 255; return v <= .03928 ? v/12.92 : Math.pow((v+.055)/1.055, 2.4); };
  return .2126*f(n>>16 & 255) + .7152*f(n>>8 & 255) + .0722*f(n & 255);
}
/* real contrast ratio, not a luminance gap: several teams pair two colours that differ
   in brightness but still leave the letters barely legible at 20 pixels */
function ratio(x, y){
  const a = lum(x), b = lum(y);
  return (Math.max(a, b) + .05) / (Math.min(a, b) + .05);
}
function pair(col){
  const [a, b] = col;
  // the badge takes whichever colour reads as a shape on the page
  const main = (lum(a) > 0.78 && lum(b) <= 0.78) ? b : a;
  const other = main === a ? b : a;
  // Keep the team's own second colour wherever it is legible — bold display letters hold
  // up to about 2.5:1 — and only fall back where it genuinely is not, taking whichever of
  // ink or paper contrasts better rather than guessing from brightness.
  if (ratio(main, other) >= 2.5) return [main, other];
  const ink = "#14171a", paper = "#ffffff";
  return [main, ratio(main, ink) >= ratio(main, paper) ? ink : paper];
}
function initials(name){
  const w = name.split(/\s+/).filter(x => x.length > 1 || /^[A-Z]/.test(x));
  return (w.length > 1 ? w.map(x => x[0]).join("") : name.slice(0, 1)).slice(0, 3).toUpperCase();
}
function hash(s){ let h = 2166136261; for (const c of s) h = Math.imul(h ^ c.charCodeAt(0), 16777619); return h >>> 0; }

/* a quiet band behind the letters, so two teams in one conference still differ */
const DEVICES = [
  () => "",
  c => `<path d="M0 21 16 12l16 9v3.4L16 15.6 0 24.4z" fill="${c}" opacity=".34"/>`,
  c => `<path d="M-2 26 26-2h7L5 33z" fill="${c}" opacity=".3"/>`,
  c => `<rect x="12.6" y="-2" width="6.8" height="36" fill="${c}" opacity=".3"/>`,
  c => `<rect x="-2" y="12.6" width="36" height="6.8" fill="${c}" opacity=".3"/>`,
];

function mark(t){
  const [c1, c2] = pair(t.col);
  const ini = initials(t.name);
  const key = fontFor(t.mascot);
  const F = FONTS[key];
  const shape = SHAPES[t.conf] || SHAPES["Western Coast"];
  const id = "c" + hash(t.name + t.conf);
  const dev = DEVICES[hash(t.name) % DEVICES.length];
  return `<svg viewBox="0 0 32 32" role="img" aria-label="${t.name}">
    <defs><clipPath id="${id}"><path d="${shape}"/></clipPath></defs>
    <path d="${shape}" fill="${c1}"/>
    <g clip-path="url(#${id})">${dev(c2)}</g>
    <path d="${shape}" fill="none" stroke="${c2}" stroke-width="1.5" opacity=".6"/>
    <text class="mono" data-conf="${t.conf}" x="16" y="16" text-anchor="middle" dominant-baseline="central"
      fill="${c2}" font-family='${F.css}' font-weight="${F.w}" font-size="14"
      letter-spacing="${F.tr}em">${ini}</text>
  </svg>`;
}

/* ---------- fit the letters to the badge once the real fonts have arrived ----------
   Each face has its own cap height and sidebearings, so a fixed font-size would sit
   high in one and overflow in another. Measure what actually rendered, then scale and
   centre it. This also means a face that fails to load still lands correctly. */
/* how much of the 32-unit box each shape can actually hold letters in: a hexagon is
   nearly all usable, a diamond narrows to nothing at the corners */
const ROOM = {
  "Jyras Bay":1.00, "Broad South":1.00, "Low Sixteen":1.00, "Western Coast":1.00,
  "Brass Belt":0.94, "Power North":0.94, "Great Fourteen":0.96, "Mountain Valley":0.92,
  "East Forest":0.90, "Vapor Stream":0.76, "Evening Star":0.72, "Southwestern":0.80,
  "Subdivision":0.92,
};
function fitAll(root){
  (root || document).querySelectorAll("svg text.mono").forEach(tx => {
    tx.removeAttribute("transform");
    let b;
    try { b = tx.getBBox(); } catch (e) { return; }
    if (!b.width || !b.height) return;
    const room = ROOM[tx.dataset.conf] ?? 0.94;
    const n = tx.textContent.length;
    const wide = (n > 2 ? 23 : n > 1 ? 21 : 18) * room;
    const tall = (n > 2 ? 15 : 16.5) * room;
    const k = Math.min(wide / b.width, tall / b.height);
    const cx = b.x + b.width / 2, cy = b.y + b.height / 2;
    tx.setAttribute("transform",
      `translate(${16 - cx * k} ${16 - cy * k}) scale(${k.toFixed(4)})`);
  });
}
