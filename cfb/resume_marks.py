"""Quality win / quality loss / bad loss, judged against the CURRENT rankings.

Dan, 2041 week 6: the marks used to be read off the computer rating rank (top 30 = quality,
below 90 = bad on the weekly tool; 25 / 60 in the Committee Room), which carries preseason
expectation around all year -- Kaji Daun was still a "quality" opponent at 2-3. Now:

  * quality win / quality loss: the opponent is in the current top 25 -- Dan's own board
    once the committee is official (week 10 on), the media poll before that
  * bad loss: the opponent is nowhere in the current poll (no committee place, not even
    receiving media votes) AND sits outside the top 60 of the in-season computer rating.
    The poll cannot say who is bad, only who is good, so the bottom still needs the rating
    -- but a team the voters have on their sheets can never be a bad loss.

Subdivision guests get no mark either way, as before. The engine's own résumé scoring in
committee.committee_rank is untouched; this is about what the pages show Dan.
"""

QUALITY_TOP = 25
BAD_BELOW = 60


def current_rank(s):
    """{team: rank} from the ranking of record right now."""
    if s.get('committee_official') and s.get('committee_poll_current'):
        return {t: int(r) for r, t in s['committee_poll_current']}
    return {t: int(r) for r, t in (s.get('media_poll_current') or [])}


def mark(won, opp, poll_rank, rating_rank):
    """'qw' | 'ql' | 'bl' | None."""
    if rating_rank is None:          # subdivision guest
        return None
    pr = poll_rank.get(opp)
    if pr is not None and pr <= QUALITY_TOP:
        return 'qw' if won else 'ql'
    if (not won) and pr is None and rating_rank > BAD_BELOW:
        return 'bl'
    return None


def source_label(s):
    return 'committee board' if (s.get('committee_official') and s.get('committee_poll_current')) else 'media poll'
