"""Shared roster-generation constants (used by initial gen and offseason recruiting)."""
ROSTER_TEMPLATE = [("QB",4),("RB",5),("WR",8),("TE",4),("OL",10),
                   ("DL",8),("LB",7),("CB",6),("S",5),("K",2),("P",2),("ATH",1)]
ARCHETYPES = {
 "QB": [("Pocket Passer",.34),("Dual-Threat",.28),("Gunslinger",.18),("Game Manager",.20)],
 "RB": [("Power Back",.28),("Speed Back",.28),("All-Purpose",.30),("Short-Yardage Bruiser",.14)],
 "WR": [("Deep Threat",.26),("Possession",.30),("Slot Technician",.26),("Contested-Catch",.18)],
 "TE": [("Receiving TE",.40),("Blocking TE",.32),("Hybrid",.28)],
 "OL": [("Pass Protector",.36),("Run Mauler",.36),("Balanced",.28)],
 "DL": [("Edge Rusher",.36),("Run Stuffer",.34),("Interior Penetrator",.30)],
 "LB": [("Coverage LB",.30),("Run-Stopping LB",.40),("Blitzer",.30)],
 "CB": [("Shutdown",.25),("Ball-Hawk",.35),("Press",.40)],
 "S":  [("Center Fielder",.35),("Box Safety",.35),("Hybrid Safety",.30)],
 "K":  [("Big Leg",.45),("Accurate",.55)],
 "P":  [("Big Leg",.5),("Directional",.5)],
 "ATH":[("Return Ace",.6),("Gadget",.4)],
}
