"""League Office case catalog (Dan, 27 Oct 2026): every case type with its own pool of facts.

A case is built by rolling a subject (who/where), then a handful of facts from the type's pool. Each fact adds a sentence and moves the case's
severity (1-10); the severity then decides how the option menu is built (rfl/cases.py). Two cases of the same type therefore differ in what
happened, how bad it is, and what the ladder of consequences looks like.

Template keys available in text: {name} {pos} {nick} {club} {opp} {oppclub} {game} {when} {flag} {victim} {vpos} {onick} {official} {reporter}
{agent} {spokes} {coach} {gm} {n} {inj_kind} {inj_weeks} {wk} {subst} {other} {opos} {othernick} and anything a subject builder adds.
Tone: neutral wire-report style. Nothing graphic; nothing involving minors.
"""

def F(id, p, ds, grp, text, req=None):
    """A fact: id, probability (or callable), severity change (or callable), exclusive group, sentence, optional requirement on the facts so far."""
    return dict(id=id, p=p, ds=ds, grp=grp, text=text, req=req)

def T(**kw): return kw

# ----------------------------------------------------------------------------------------------------------------------------- on-field
_INJ = lambda f: f.get('inj_weeks')
_INJ_DS = lambda f: 1.2 if f.get('inj_weeks', 0) <= 2 else (2.4 if f.get('inj_weeks', 0) <= 6 else 3.6)
_NO_INJ = lambda f: not f.get('inj_weeks')
HIT_FACTS = [
    F('real_injury', 1.0, _INJ_DS, 'inj', "{victim} ({vpos}, {onick}) left the game with a {inj_kind} and is expected to miss {inj_weeks} {weeks_word}.", _INJ),
    F('victim_returned', .38, .5, 'inj', "{victim} ({vpos}, {onick}) left for a few plays and returned.", _NO_INJ),
    F('victim_stayed', .8, 0.0, 'inj', "{victim} ({vpos}, {onick}) stayed in the game.", _NO_INJ),
    F('apology', .30, -1.0, 'att', "{last} sought out {vlast} after the game to apologize."),
    F('defiant', .12, 1.0, 'att', "{last} told reporters he would play it the same way again."),
    F('club_addressed', .22, -.5, 'att', "The {nick} say they have already addressed the play with {last}."),
    F('film_avoidable', .22, .8, 'film', "The league's film review found the contact was avoidable."),
    F('film_close', .18, -.7, 'film', "Film review showed the contact was close to the whistle."),
    F('worked_over', .10, .6, 'ctx', "It was the second flag of that kind against the {nick} in the game."),
    F('prime', .16, .3, 'ctx', "It happened in front of a national television audience."),
]
HIT_CLOSERS = ["The league office has asked the {nick} for their account.", "{name}'s agent, {agent}, says the player will cooperate with the review.", "The players' union has been notified.", "Officials in the game, led by {official}, reported the play to the league."]

CATALOG = {}
CATALOG['late_hit'] = T(tier='minor', w=3.0, subject='flag', anchor=('unnecessary roughness', 'roughing the passer'), ladder='fine', base=3.2, closers=HIT_CLOSERS,
    title=['Late hit', 'Hit after the whistle', 'Late hit on a ball carrier'],
    openers=["{name} ({pos}, {nick}) was flagged for {flag} {when} on a hit the officials ruled came well after the play was over.",
             "Officials flagged {name} ({pos}, {nick}) for {flag} {when}; replays show the contact landed after the whistle.",
             "{name} ({pos}, {nick}) drew a {flag} flag {when} for driving a player into the turf late."], factors=HIT_FACTS)
CATALOG['defenseless'] = T(tier='minor', w=2.2, subject='flag', anchor=('roughing the passer', 'unnecessary roughness'), ladder='fine', base=3.8, closers=HIT_CLOSERS,
    title=['Hit on a defenseless player', 'Illegal hit on a receiver', 'Contact with a defenseless player'],
    openers=["{name} ({pos}, {nick}) was flagged for {flag} {when} for a hit on a player the officials judged defenseless.",
             "{name} ({pos}, {nick}) hit a player in a defenseless position {when} and was flagged for {flag}.",
             "Officials penalized {name} ({pos}, {nick}) {when} for {flag} after a hit on a receiver who had not yet secured the ball."], factors=HIT_FACTS)
CATALOG['helmet'] = T(tier='minor', w=2.2, subject='flag', anchor=('roughing the passer', 'unnecessary roughness'), ladder='fine', base=3.6, closers=HIT_CLOSERS,
    title=['Helmet-to-helmet contact', 'Contact to the head', 'Illegal use of the helmet'],
    openers=["{name} ({pos}, {nick}) was flagged for {flag} {when} for helmet-to-helmet contact.",
             "{name} ({pos}, {nick}) led with the crown of his helmet {when} and drew a {flag} flag.",
             "A {flag} flag went against {name} ({pos}, {nick}) {when} for contact to the head."],
    factors=HIT_FACTS + [F('repeat_style', .12, .8, 'ctx2', "The league has warned {nick} players about this kind of contact before.")])
CATALOG['taunt'] = T(tier='minor', w=2.6, subject='flag', anchor=('unnecessary roughness',), ladder='fine', base=2.2, closers=["The league office has notified the {nick}.", "{name} has until Friday to respond to the notice.", "The players' union has been notified."],
    title=['Taunting', 'Taunting after a play', 'Unsportsmanlike conduct'],
    openers=["{name} ({pos}, {nick}) was flagged {when} after standing over an opponent and taunting him.",
             "{name} ({pos}, {nick}) drew a flag {when} for taunting after a play.",
             "Officials flagged {name} ({pos}, {nick}) {when} for taunting in the direction of the opposing bench."],
    factors=[F('mild', .45, -.8, 'sev', "Officials described it as a single gesture."), F('extended', .25, 1.0, 'sev', "Officials said it went on after he was warned."),
             F('opp_responded', .2, .7, 'sev2', "An opposing player responded, and the officials separated them."),
             F('apology', .3, -.8, 'att', "{last} said afterwards the moment got away from him."), F('defiant', .1, .9, 'att', "{last} said afterwards he had nothing to apologize for."),
             F('crowd', .18, .3, 'ctx', "The incident drew a reaction from the home crowd."), F('lead', .22, .4, 'ctx2', "It came at a point when his team was ahead by two scores.")])
CATALOG['gesture'] = T(tier='minor', w=1.2, subject='flag', anchor=('unnecessary roughness',), ladder='fine', base=2.6, closers=["The league office has asked for video of the exchange.", "The {nick} say they will handle it internally."],
    title=['Gesture toward the crowd', 'Obscene gesture', 'Altercation with the stands'],
    openers=["{name} ({pos}, {nick}) was flagged {when} after making an obscene gesture toward the stands.",
             "A flag went against {name} ({pos}, {nick}) {when} after an exchange with fans along the {opp} sideline.",
             "{name} ({pos}, {nick}) was penalized {when} for a gesture directed at spectators."],
    factors=[F('heckled', .45, -.9, 'prov', "Fans near the tunnel had been heckling him for much of the afternoon."), F('thrown', .12, .7, 'prov', "Fans threw an object onto the field earlier in the quarter."),
             F('apology', .35, -.8, 'att', "{last} apologized through the club after the game."), F('repeat', .10, .9, 'att', "He had made a similar gesture in an earlier game."),
             F('security', .15, .6, 'ctx', "Stadium security stepped in and walked him toward the tunnel.")])

CATALOG['flagrant'] = T(tier='moderate', w=2.2, subject='flag', anchor=('roughing the passer', 'unnecessary roughness'), ladder='disc', base=5.0, closers=HIT_CLOSERS + ["The league has opened a formal review under its safety policy."],
    title=['Flagrant hit, ejection', 'Ejection for a dangerous hit', 'Ejected for a hit to the head'],
    openers=["{name} ({pos}, {nick}) was flagged for {flag} {when} and ejected after officials reviewed a hit to the head of {victim}.",
             "{name} ({pos}, {nick}) was ejected {when} after a {flag} flag for a hit the officials called flagrant.",
             "Officials ejected {name} ({pos}, {nick}) {when} for a hit on {victim} ({vpos}, {onick}) that drew a {flag} flag."],
    factors=HIT_FACTS + [F('helmet_off', .08, 1.0, 'ctx3', "The victim's helmet came off on the play."), F('rage', .14, .9, 'att2', "Teammates had to hold {last} back as he left the field.")])
CATALOG['targeting'] = T(tier='moderate', w=1.4, subject='flag_injury', anchor=('roughing the passer', 'unnecessary roughness'), ladder='disc', base=5.5, closers=HIT_CLOSERS,
    title=['Hit that ended a player\'s day', 'Dangerous hit with a serious injury', 'Targeting with injury'],
    openers=["{victim} ({vpos}, {onick}) left the game after a hit from {name} ({pos}, {nick}) that drew a {flag} flag {when}.",
             "{name} ({pos}, {nick}) was flagged for {flag} {when} on a play that ended with {victim} ({vpos}, {onick}) being helped from the field.",
             "A {flag} flag against {name} ({pos}, {nick}) {when} was followed by a long stoppage while {victim} ({vpos}, {onick}) was attended to."],
    factors=[F('real_injury', 1.0, _INJ_DS, 'inj', "{vlast} was diagnosed with a {inj_kind} and is expected to miss {inj_weeks} {weeks_word}."),
             F('film_avoidable', .35, .9, 'film', "The league's film review found the hit was avoidable."), F('film_close', .2, -.8, 'film', "Film review showed the hit was a bang-bang play."),
             F('apology', .35, -1.0, 'att', "{last} reached out to {vlast} after the game."), F('defiant', .1, 1.0, 'att', "{last} said he had no regrets about the hit."),
             F('prior_hit', .12, 1.2, 'ctx', "{last} had been warned by the league about similar contact earlier in his career."), F('union', .2, 0.0, 'ctx2', "The players' union says it will support {last} through the process.")])
CATALOG['fight'] = T(tier='moderate', w=1.8, subject='duel', ladder='disc', base=4.4, closers=["The ruling applies to both players.", "The league office has asked both clubs for statements.", "Officials, led by {official}, filed a joint report."],
    title=['Fight and ejections', 'Brawl on the field', 'Scuffle that emptied the benches'],
    openers=["A scrum after a play turned into a fight. {name} ({nick}) and {other} ({othernick}) were ejected.",
             "{name} ({pos}, {nick}) and {other} ({opos}, {othernick}) were ejected after a fight broke out between the lines.",
             "Tempers boiled over {when2}. {name} ({nick}) and {other} ({othernick}) were thrown out after trading shoves that turned into punches."],
    factors=[F('benches', .35, .9, 'scale', "Both benches cleared before officials restored order."), F('brief', .4, -.6, 'scale', "It was over within seconds."),
             F('punches', .2, 1.0, 'scale2', "Video shows punches thrown by both players."), F('helmet_swing', .06, 2.6, 'scale3', "Video shows {last} swinging his helmet before he was pulled away."),
             F('instigator', .3, .5, 'who', "Officials identified {last} as the aggressor."), F('mutual', .35, -.3, 'who', "Officials described the fight as mutual."),
             F('apologies', .25, -.8, 'att', "Both players apologized after the game."), F('feud', .15, .6, 'ctx', "The two players have a history from an earlier meeting.")])
CATALOG['bench_clear'] = T(tier='moderate', w=.9, subject='duel', ladder='disc', base=4.0, closers=["The league office has asked both clubs for statements.", "Both head coaches have been asked to speak with the commissioner's staff."],
    title=['Bench-clearing incident', 'Sideline melee', 'Benches empty after a late hit'],
    openers=["Both benches emptied {when2} after {name} ({nick}) and {other} ({othernick}) squared off near the sideline.",
             "A late hit led to a bench-clearing scrum {when2}. {name} ({nick}) and {other} ({othernick}) were singled out by officials.",
             "Players from both teams poured onto the field {when2} after an exchange between {name} ({nick}) and {other} ({othernick})."],
    factors=[F('coaches_in', .3, .8, 'a', "Assistant coaches from both sides were seen in the scrum."), F('fan', .1, 1.0, 'b', "A fan reached over the railing during the melee."),
             F('quick', .45, -.6, 'c', "Order was restored in under a minute."), F('ejections', .4, .6, 'd', "Officials ejected four players in total."), F('no_ejections', .25, -.4, 'd', "Officials issued only a warning to both benches.")])
CATALOG['coach_sideline'] = T(tier='minor', w=1.6, subject='coach', ladder='coach', base=2.8, closers=["The {nick} say they will not comment further.", "The league office has notified {coach}."],
    title=['Sideline conduct', 'Coach berates officials', 'Heated exchange with the officiating crew'],
    openers=["Head coach {name} ({nick}) berated officials over a no-call and continued after the final whistle.",
             "{name}, head coach of the {nick}, was flagged for sideline conduct after a heated exchange with {official}.",
             "{name} ({nick}) followed an official onto the field to argue a call and was warned twice."],
    factors=[F('flag15', .35, .5, 'pen', "{last} drew a 15-yard unsportsmanlike flag for it."), F('apology', .25, -.8, 'att', "{last} said in his postgame news conference that he lost his composure."),
             F('defiant', .12, .9, 'att', "{last} said in his postgame news conference that the crew had 'lost control of the game'."), F('repeat', .14, .8, 'ctx', "It is the second such incident involving {last} this season."),
             F('replay', .18, -.4, 'ctx2', "Replays later showed the call he was arguing was missed.")])

# ----------------------------------------------------------------------------------------------------------------------------- off-field minor
CATALOG['comments'] = T(tier='minor', w=2.2, subject='player', ladder='fine', base=2.4, closers=["The league's media policy lists fines for public criticism of officials.", "The {nick} have not commented.", "The players' union says it is reviewing the remarks."],
    title=['Comments about the officials', 'Public criticism of a crew', 'Remarks after a loss'],
    openers=["{name} ({pos}, {nick}) told reporters after the game that the officiating crew had 'decided the outcome'.",
             "{name} ({pos}, {nick}) accused {official}'s crew of favoring the {opp} in remarks to reporters.",
             "{name} ({pos}, {nick}) said in a postgame interview that the officials 'should be ashamed'."],
    factors=[F('viral', .3, .6, 'a', "The comments went public the same night and drew wide attention."), F('named', .2, 1.0, 'b', "{last} named an official in the remarks."),
             F('profane', .25, .7, 'c', "The remarks included profanity that aired live."), F('walked_back', .3, -1.0, 'd', "{last} walked the comments back on social media the next morning."),
             F('doubled', .08, 1.1, 'd', "{last} repeated the comments in a second interview the next day."), F('call', .25, -.4, 'e', "The call he was reacting to was later acknowledged by the league as an error.")])
CATALOG['social'] = T(tier='minor', w=2.4, subject='player', ladder='fine', base=2.4, closers=["The post has since been deleted.", "The {nick} say they have spoken with {name}.", "The league's social media policy allows fines for posts that criticize the game or its personnel."],
    title=['Social media post', 'Inflammatory post', 'Post about the league office'],
    openers=["{name} ({pos}, {nick}) posted a message criticizing the league's scheduling and broadcast decisions.",
             "{name} ({pos}, {nick}) posted a video taunting {opp} fans that went viral.",
             "{name} ({pos}, {nick}) posted remarks about an opponent that the league described as unprofessional."],
    factors=[F('viral', .3, .7, 'a', "It was shared widely before it was removed."), F('opponent_named', .2, .8, 'b', "It named an opposing player."), F('apology', .3, -.9, 'c', "{last} apologized in a follow-up post."),
             F('refused', .08, 1.0, 'c', "{last} declined to delete it when the league asked him to."), F('night', .2, -.3, 'd', "He said it was written late at night and in frustration."),
             F('profane', .22, .5, 'e', "The post contained profanity.")])
CATALOG['media'] = T(tier='minor', w=1.6, subject='player', ladder='fine', base=1.8, closers=["The league requires players to be available to media after games.", "The {nick} say the player had a family matter."],
    title=['Missed media availability', 'Refused to speak to reporters', 'Left the stadium before media availability'],
    openers=["{name} ({pos}, {nick}) left the stadium without speaking to reporters after the game despite being named a player of the game.",
             "{name} ({pos}, {nick}) did not appear for a mandatory media session this week.",
             "{name} ({pos}, {nick}) walked out of a postgame news conference after one question."],
    factors=[F('repeat', .2, .8, 'a', "It is the second missed session this season."), F('excused', .2, -1.0, 'b', "The {nick} say he had been excused for a family matter, but the league was not told."),
             F('rude', .12, .8, 'c', "He made a remark to a reporter on his way out."), F('apology', .3, -.7, 'd', "{last} apologized to the media relations staff the next day.")])
CATALOG['equip'] = T(tier='minor', w=1.8, subject='player', ladder='fine', base=1.8, closers=["The league's uniform policy provides for fines on a sliding scale.", "The {nick} equipment staff say they will review the pregame process."],
    title=['Equipment violation', 'Uniform violation', 'Non-approved gear'],
    openers=["{name} ({pos}, {nick}) wore non-approved gear on the field after being warned in the pregame check.",
             "{name} ({pos}, {nick}) wore a visor that was not cleared by the league after an official told him to remove it.",
             "{name} ({pos}, {nick}) took the field with a modified chin strap that the league had not approved."],
    factors=[F('warned', .5, .5, 'a', "He had been warned about the same item in practice."), F('safety', .18, 1.0, 'b', "The league's equipment staff said the item posed a safety concern."),
             F('sponsor', .12, .5, 'c', "The gear carried a logo from a company that is not a league sponsor."), F('first', .4, -.7, 'd', "It was his first equipment violation."),
             F('removed', .3, -.5, 'e', "He removed it at halftime.")])
CATALOG['fan'] = T(tier='minor', w=1.0, subject='player', ladder='fine', base=3.4, closers=["Stadium security filed a report with the league.", "The {nick} say the player was provoked."],
    title=['Confrontation with a fan', 'Exchange with a spectator', 'Incident in the tunnel'],
    openers=["{name} ({pos}, {nick}) had a heated exchange with a fan in the tunnel after the game.",
             "{name} ({pos}, {nick}) threw a towel at a fan who was heckling him after the game.",
             "{name} ({pos}, {nick}) was filmed shoving a phone away from a fan outside the visitors' locker room."],
    factors=[F('video', .5, .6, 'a', "Video of the exchange circulated on social media."), F('contact', .22, 1.2, 'b', "There was physical contact."), F('no_contact', .5, -.4, 'b', "There was no physical contact."),
             F('provoked', .3, -.9, 'c', "The fan had been shouting insults at him."), F('police', .1, 1.0, 'd', "Local police took a report but did not make an arrest."), F('apology', .3, -.8, 'e', "{last} apologized to the fan through the club.")])

# ----------------------------------------------------------------------------------------------------------------------------- serious
CATALOG['ped'] = T(tier='serious', w=3.0, subject='player', ladder='ped', base=5.0, closers=["The program's first-offense range is 2 to 6 games for most substances; repeat offenses carry much longer penalties.", "The players' union says it is reviewing the test results."],
    title=['Performance-enhancing substance', 'Failed drug test', 'Positive test'],
    openers=["{name} ({pos}, {nick}) tested positive for {subst} under the league's drug-testing program.",
             "{name} ({pos}, {nick}) has been notified of a positive test for {subst}.",
             "The league's drug-testing program flagged a sample from {name} ({pos}, {nick}) for {subst}."],
    factors=[F('supplement', .35, -1.2, 'story', "He says the source was an over-the-counter supplement."), F('prescription', .15, -1.0, 'story', "He says he was taking a prescribed medication and did not know it was banned."),
             F('denies', .2, .3, 'story', "He denies knowingly taking anything."), F('admits', .12, -.6, 'story', "He has acknowledged the violation."),
             F('masking', .12, 1.8, 'sub', "The sample also contained a masking agent."), F('second', .1, 2.0, 'prior', "It is his second positive test."),
             F('retest', .3, 0.0, 'proc', "His B sample confirmed the result."), F('cooperating', .3, -.6, 'coop', "He has agreed to enter the league's counseling and testing program.")])
CATALOG['dui'] = T(tier='serious', w=2.4, subject='player', ladder='conduct', base=4.8, closers=["The club has issued a short statement and says it is cooperating with the league.", "The league's policy provides for discipline whether or not criminal charges result."],
    title=['Arrest for driving under the influence', 'DUI arrest', 'Impaired driving arrest'],
    openers=["{name} ({pos}, {nick}) was arrested early on {dow} on suspicion of driving under the influence.",
             "Police arrested {name} ({pos}, {nick}) overnight after a traffic stop; officers reported a blood alcohol level above the legal limit.",
             "{name} ({pos}, {nick}) was stopped by police on {dow} and charged with driving under the influence."],
    factors=[F('crash', .16, 2.2, 'a', "His vehicle struck a parked car, but no one was injured."), F('high_bac', .22, 1.4, 'b', "Police reported a blood alcohol level nearly twice the legal limit."),
             F('first', .55, -.7, 'c', "He has no prior arrests, according to police."), F('prior', .12, 1.6, 'c', "It is his second alcohol-related arrest."),
             F('cooperative', .45, -.6, 'd', "He was cooperative with officers."), F('uncooperative', .12, 1.0, 'd', "Officers said he was uncooperative."),
             F('ride', .3, .4, 'e', "A teammate was in the car."), F('apology', .35, -.5, 'f', "{last} apologized through his agent, {agent}.")])
CATALOG['gambling'] = T(tier='serious', w=.9, subject='player', ladder='conduct', base=5.0, story='investigation', closers=["The league's integrity unit has been notified.", "The league's gambling policy bars players from betting on any league game."],
    title=['Gambling policy violation', 'Betting on league games', 'Sports betting investigation'],
    openers=["The league's integrity unit says {name} ({pos}, {nick}) placed bets on league games through an account in a relative's name.",
             "{name} ({pos}, {nick}) is under investigation after betting records show wagers placed from a device he owns.",
             "A sportsbook flagged unusual activity linked to {name} ({pos}, {nick}); the league has opened a review."],
    factors=[F('not_own', .55, -1.4, 'a', "None of the bets were on {nick} games."), F('own', .1, 3.0, 'a', "Some of the bets were on {nick} games."),
             F('small', .45, -.6, 'b', "The wagers were small and spread over several weeks."), F('large', .15, 1.2, 'b', "The wagers were large."),
             F('admits', .2, -.6, 'c', "{last} has acknowledged the activity through his agent."), F('denies', .25, .3, 'c', "{last} denies placing the bets."), F('first', .6, -.4, 'd', "He has no prior policy violations.")])
CATALOG['firearm'] = T(tier='serious', w=1.6, subject='player', ladder='conduct', base=4.4, closers=["The club reported the incident to the league itself.", "The league's policy prohibits firearms in club facilities and at team events."],
    title=['Firearm at the facility', 'Firearm in a team vehicle', 'Firearm violation'],
    openers=["{name} ({pos}, {nick}) brought a firearm into the team facility in violation of league policy.",
             "Security found a firearm in {name}'s ({pos}, {nick}) bag at the team hotel before the game.",
             "A firearm belonging to {name} ({pos}, {nick}) was discovered in his locker during a routine check."],
    factors=[F('licensed', .65, -1.0, 'a', "The firearm was licensed."), F('unlicensed', .1, 2.2, 'a', "The firearm was not licensed in the state."),
             F('loaded', .3, .9, 'b', "It was loaded."), F('unloaded', .5, -.4, 'b', "It was unloaded and secured."), F('self_reported', .3, -1.0, 'c', "He reported it himself."),
             F('discharged', .04, 2.5, 'd', "The weapon discharged; no one was hurt."), F('apology', .3, -.5, 'e', "{last} apologized to teammates and staff.")])
CATALOG['assault_misd'] = T(tier='serious', w=1.1, subject='player', ladder='conduct', base=5.8, story='court', closers=["The league's conduct policy lets the commissioner act without waiting for the courts.", "The club says it is gathering facts."],
    title=['Misdemeanor assault charge', 'Altercation at a nightclub', 'Charged after an incident'],
    openers=["{name} ({pos}, {nick}) was charged with misdemeanor assault after an altercation outside a restaurant.",
             "Police cited {name} ({pos}, {nick}) for assault after a fight at a nightclub.",
             "{name} ({pos}, {nick}) is facing a misdemeanor assault charge after a dispute in a parking lot."],
    factors=[F('injury', .3, 1.5, 'a', "The other man was treated at a hospital and released."), F('no_injury', .4, -.8, 'a', "No one required medical treatment."),
             F('video', .35, .8, 'b', "Video of the incident was shared online."), F('provoked', .3, -.8, 'c', "{last}'s attorney says he was defending himself."), F('prior', .1, 1.5, 'd', "It is his second police incident in two years."),
             F('settled', .15, -1.0, 'e', "The two men have reached a private settlement.")])
CATALOG['reckless'] = T(tier='serious', w=1.0, subject='player', ladder='conduct', base=3.4, closers=["The league's conduct policy covers dangerous behavior regardless of charges.", "The {nick} have asked for the player's account."],
    title=['Reckless driving', 'Street racing citation', 'Arrest after a pursuit'],
    openers=["{name} ({pos}, {nick}) was cited for reckless driving after police clocked him at more than 40 mph over the limit.",
             "Police say {name} ({pos}, {nick}) was involved in an informal street race on {dow} night.",
             "{name} ({pos}, {nick}) was stopped after leading an officer on a short pursuit."],
    factors=[F('passenger', .25, .8, 'a', "He had a passenger in the car."), F('speed', .3, 1.0, 'b', "Police said he was traveling above 100 mph."), F('first', .55, -.6, 'c', "He has no prior driving violations."),
             F('apology', .3, -.5, 'd', "{last} said he made a bad decision."), F('suspended_license', .1, 1.2, 'e', "His license had been suspended.")])

# ----------------------------------------------------------------------------------------------------------------------------- club level
CATALOG['filming'] = T(tier='club', w=1.5, subject='club', ladder='club', base=5.0, closers=["The league's competition committee takes illegal filming seriously.", "The club says it will cooperate."],
    title=['Illegal filming', 'Unauthorized video', 'Filming an opponent\'s practice'],
    openers=["A video staffer for the {nick} was found filming an opponent's walkthrough from an unauthorized spot.",
             "Security found an unauthorized camera aimed at the {opp} sideline during pregame warmups for the {nick}.",
             "League security reports a {nick} employee was filming the {opp} bench signals from the press box."],
    factors=[F('one_employee', .45, -1.2, 'a', "The club says it was a mistake by one employee."), F('coach_aware', .15, 2.0, 'a', "Documents suggest coaching staff were aware of the practice."),
             F('first', .6, -.6, 'b', "The club has no prior violation."), F('repeat', .1, 2.2, 'b', "The club was disciplined for a similar violation within the last five years."),
             F('footage', .3, .7, 'c', "Investigators recovered footage from several earlier games."), F('fired', .25, -.8, 'd', "The employee has been dismissed.")])
CATALOG['injury_report'] = T(tier='club', w=1.3, subject='club', ladder='club', base=3.6, closers=["The league requires accurate injury reports every week.", "The {nick} say the report was submitted in good faith."],
    title=['Injury report violation', 'Misleading injury report', 'Inaccurate injury listing'],
    openers=["The league says the {nick} listed a starter as 'questionable' who was known to be out for the game.",
             "The {nick} left a player off the injury report who had missed practice all week.",
             "The league is reviewing a {nick} injury report after a player listed as healthy was ruled out an hour before kickoff."],
    factors=[F('star', .35, .9, 'a', "The player is one of the club's best known."), F('repeat', .15, 1.4, 'b', "It is the second such filing from the club this season."),
             F('bet', .08, 1.0, 'c', "The timing drew interest from the league's integrity unit."), F('honest', .3, -1.0, 'd', "The club says the player's status changed on game day."),
             F('coach_comment', .2, .5, 'e', "{coach} told reporters the report was 'a formality'.")])
CATALOG['draft_leak'] = T(tier='club', w=.7, subject='club', ladder='club', base=4.2, closers=["The league's draft rules bar clubs from disclosing selections before they are announced.", "The {nick} say they have started an internal review."],
    title=['Draft information leak', 'Premature draft announcement', 'Leaked draft board'],
    openers=["A {nick} staffer disclosed the club's pick before it was announced.",
             "The {nick}'s draft board was posted online, according to the league.",
             "The {nick} confirmed a trade to a player before the league announced it."],
    factors=[F('social', .4, .6, 'a', "The disclosure was made on a personal social media account."), F('gm_aware', .1, 1.8, 'b', "The league says GM {gm} knew about it beforehand."),
             F('contained', .4, -.8, 'c', "The disclosure was confined to a small group."), F('advantage', .12, 1.5, 'd', "Another club may have benefited.")])
CATALOG['owner_comments'] = T(tier='club', w=.7, subject='club', ladder='club', base=3.4, closers=["The league's constitution gives the commissioner authority over public statements by owners.", "The {nick} say the remarks were taken out of context."],
    title=['Owner\'s public remarks', 'Public criticism of the league', 'Remarks about a rival club'],
    openers=["The {nick}'s owner criticized the league's officiating and scheduling in a radio interview.",
             "The {nick}'s owner made remarks about a rival club's ownership that the league called inappropriate.",
             "An owner's comment about the league's broadcast partners drew a formal complaint."],
    factors=[F('repeat', .2, 1.2, 'a', "It is the second time this season."), F('apology', .3, -.9, 'b', "The owner issued a statement of regret."), F('profane', .12, .8, 'c', "The interview included profanity."), F('rivals', .2, .5, 'd', "Another club filed a complaint.")])
CATALOG['facility'] = T(tier='club', w=.8, subject='club', ladder='club', base=3.8, closers=["The league's facility standards require corrective action within thirty days.", "The {nick} say repairs are under way."],
    title=['Facility and field conditions', 'Unsafe field conditions', 'Visiting locker room complaint'],
    openers=["The league found the {nick}'s field did not meet its safety standard during Sunday's game.",
             "The {opp} complained that the visiting locker room at the {nick}'s stadium was unusable.",
             "A league inspector found unresolved drainage problems on the {nick}'s field after two complaints."],
    factors=[F('injuries', .25, 1.4, 'a', "Players from both clubs complained of footing on the sideline."), F('repeat', .2, 1.2, 'b', "The club had been warned earlier in the year."),
             F('weather', .3, -.9, 'c', "Heavy rain earlier in the week was a factor."), F('fix', .3, -.6, 'd', "The club has already begun repairs.")])
CATALOG['sideline_gm'] = T(tier='club', w=.8, subject='gm', ladder='coach', base=3.8, closers=["The league's conduct policy covers club executives.", "The {nick} have asked for a chance to respond."],
    title=['Executive conduct', 'General manager\'s comments', 'Executive confrontation'],
    openers=["{name}, general manager of the {nick}, confronted {official} in the tunnel after the game.",
             "{name} ({nick} GM) criticized the league office publicly after a disputed call.",
             "{name} ({nick} GM) was ejected from the press box after an argument with stadium staff."],
    factors=[F('profane', .3, .7, 'a', "Witnesses said the exchange was profane."), F('apology', .3, -.9, 'b', "{last} later apologized."), F('repeat', .12, 1.2, 'c', "He has been warned before."), F('video', .25, .5, 'd', "A video of the exchange was widely shared.")])

# ----------------------------------------------------------------------------------------------------------------------------- investigations (two-stage club cases)
CATALOG['bounty'] = T(tier='moderate', w=.7, subject='club', ladder='club', base=5.0, story='investigation', closers=["The league has opened a formal investigation.", "The {nick} say the allegation is false."],
    title=['Bounty allegation', 'Pay-for-injury allegation', 'Allegation of a bounty program'],
    openers=["The league is looking into allegations that {nick} defenders were offered cash for knocking opponents out of games.",
             "A former {nick} assistant told investigators the club ran an informal bounty pool.",
             "{opp} players say they were targeted by the {nick} after a pregame message from a coach."],
    factors=[F('documents', .25, 1.2, 'a', "Investigators have requested internal messages."), F('coach_named', .3, .8, 'b', "{coach} is named in the complaint."), F('denial', .5, -.4, 'c', "The club denied the allegation."),
             F('real_injuries', .3, .8, 'd', "Several opposing players left games with injuries this season.")])
CATALOG['hazing'] = T(tier='moderate', w=.8, subject='club', ladder='club', base=4.6, story='investigation', closers=["The league's workplace policy bars hazing in any form.", "The {nick} have retained outside counsel."],
    title=['Hazing complaint', 'Rookie treatment complaint', 'Allegation of hazing'],
    openers=["A rookie complained to the players' union about treatment by veterans on the {nick}.",
             "The league is investigating a hazing complaint at the {nick}'s training camp.",
             "A former {nick} player alleged in an interview that veterans pressured rookies into paying for team events."],
    factors=[F('veterans', .3, .6, 'a', "The complaint names several veterans."), F('money', .4, .4, 'b', "The complaint involves money rookies were asked to pay."), F('coach_aware', .2, 1.2, 'c', "The complaint says coaches knew."),
             F('club_response', .35, -.7, 'd', "The club says it has spoken with the players involved.")])
CATALOG['tampering'] = T(tier='club', w=1.4, subject='club', ladder='club', base=5.2, story='investigation', closers=["The league's investigators say they have text records.", "The league investigates tampering complaints at the request of other clubs."],
    title=['Tampering', 'Tampering complaint', 'Contact with a player under contract'],
    openers=["The {nick} are accused of contacting a player under contract with another club before the window opened.",
             "The {opp} filed a tampering complaint against the {nick} over a conversation with a player's agent.",
             "The league is reviewing reports that the {nick}'s GM, {gm}, spoke with a pending free agent's representatives."],
    factors=[F('agent', .35, .6, 'a', "The agent for the player says no such conversation took place."), F('texts', .3, 1.2, 'b', "Investigators say they have text messages."), F('public', .15, .8, 'c', "The player discussed the club publicly."),
             F('first', .6, -.6, 'd', "The club has no prior violations.")])
CATALOG['cap'] = T(tier='club', w=1.1, subject='club', ladder='club', base=5.6, story='investigation', closers=["The league's cap office audits every club each year.", "The {nick} say it was a paperwork error."],
    title=['Undisclosed payment', 'Side arrangement', 'Cap audit finding'],
    openers=["The league found the {nick} paid a player through a side arrangement that was not reported to the cap office.",
             "A cap audit flagged $2 million in unreported payments to {nick} players.",
             "The {nick} are accused of structuring a contract to hide part of it from the cap."],
    factors=[F('gm_apology', .3, -.9, 'a', "GM {gm} said it was a paperwork error."), F('intent', .2, 1.8, 'b', "Emails suggest the arrangement was intentional."), F('amount', .35, .8, 'c', "The amount is larger than first reported."),
             F('cooperating', .4, -.6, 'd', "The club has opened its books to the league."), F('repeat', .08, 1.5, 'e', "The club was cited for something similar in the past.")])

# ----------------------------------------------------------------------------------------------------------------------------- felony (major): the league applies its own, much harsher standard than the courts or the real NFL
FELONY_CUES = dict(
    strong=["Police released a report that describes the allegation in detail.", "Investigators say they have recorded evidence.", "The arrest was made on a warrant after a formal complaint.", "Court filings cite medical records."],
    mixed=["Accounts of what happened differ.", "Police have not released the report.", "The complainant's statement is the main evidence so far.", "His attorney says there is video that tells a different story."],
    weak=["Police describe the matter as an ongoing inquiry.", "His attorney says the complaint is a dispute and has produced messages he says contradict it.", "No charges have been filed yet.", "There are no independent witnesses so far."])
FELONY_STATUS = dict(
    strong=["was arrested and charged", "was arrested on a warrant and charged", "was taken into custody and formally charged"],
    mixed=["was arrested and is awaiting formal charges", "was arrested; prosecutors are reviewing the case", "was taken into custody for questioning"],
    weak=["is under investigation; no arrest has been made", "has been questioned by police; no charges have been filed", "is the subject of a police investigation"])
FELONY = {
    'domestic': dict(w=1.0, title=['Domestic violence charge', 'Domestic violence arrest', 'Charged in a domestic incident'], what="in a domestic violence case", min_games=(16, 24), ban_on_conviction=True, extra=["Police were called to his home after a report from a household member.", "The responding officers documented injuries and a damaged property report.", "A protective order has been requested by the complainant."]),
    'assault': dict(w=1.0, title=['Felony assault charge', 'Aggravated assault arrest', 'Charged with aggravated assault'], what="with felony assault", min_games=(16, 24), ban_on_conviction=True, extra=["The other man was hospitalized, according to police.", "Police say a weapon may have been involved.", "Witnesses told officers the fight began outside a venue."]),
    'sexual': dict(w=.5, title=['Sexual assault allegation', 'Charged after a complaint to police', 'Sexual assault investigation'], what="after a complaint of sexual assault", min_games=(16, 24), ban_on_conviction=True, extra=["The complainant's identity has not been released.", "Police say the complainant has been cooperative with investigators.", "The league's security staff have been in contact with local police."]),
    'dui_injury': dict(w=.9, title=['Felony DUI with injury', 'DUI crash with injuries', 'Charged in an impaired-driving crash'], what="with felony driving under the influence causing injury", min_games=(8, 16), ban_on_conviction=False, extra=["Another driver was hospitalized after the crash.", "Police say a blood test was taken at the scene.", "The vehicle was destroyed in the collision."]),
    'trafficking': dict(w=.5, title=['Drug distribution charge', 'Trafficking arrest', 'Charged with distribution'], what="with felony drug distribution", min_games=(12, 20), ban_on_conviction=True, extra=["Police say a search of his residence turned up a large quantity.", "Investigators say the case followed a months-long inquiry.", "Two other people were arrested in the same operation."]),
    'weapons': dict(w=.8, title=['Felony weapons charge', 'Illegal weapon arrest', 'Weapons arrest'], what="with felony illegal possession of a weapon", min_games=(10, 18), ban_on_conviction=False, extra=["Police say the weapon was found during a traffic stop.", "Officers say the weapon was unregistered and had been altered.", "The arrest followed a report of shots fired near his home."]),
    'robbery': dict(w=.5, title=['Robbery charge', 'Burglary arrest', 'Charged with burglary'], what="with felony burglary", min_games=(10, 18), ban_on_conviction=False, extra=["Police say surveillance footage led them to him.", "Police say a second person has been identified.", "The victim is a former acquaintance, according to the report."]),
    'fraud': dict(w=.6, title=['Fraud charge', 'Financial fraud arrest', 'Charged in a fraud investigation'], what="with felony fraud", min_games=(8, 16), ban_on_conviction=False, extra=["Prosecutors say the scheme involved a charity he founded.", "Investigators say the case involves more than a million dollars.", "The charges follow a federal inquiry into his business."]),
}
for _k, _v in FELONY.items():
    CATALOG['felony_' + _k] = T(tier='major', w=_v['w'], subject='player', ladder='felony', base=8.0, story='felony', felony=_k, title=_v['title'], openers=[], factors=[], closers=[])
