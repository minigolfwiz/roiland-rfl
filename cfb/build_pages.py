"""Build the published HTML for the specimen board and the season viewer.

Both inject the same marks library, so a change to the mark system reaches both pages.
"""
import sys, os
sys.path.insert(0, '/home/claude/cfb2')
BASE = '/home/claude/cfb2'

def build(template, data_file, out):
    html = open(os.path.join(BASE, template)).read()
    html = html.replace('__MARKS__', open(os.path.join(BASE, 'marks_lib.js')).read())
    html = html.replace('__DATA__', open(os.path.join(BASE, data_file)).read())
    assert '__DATA__' not in html and '__MARKS__' not in html, template
    path = os.path.join(BASE, out)
    open(path, 'w').write(html)
    return out, os.path.getsize(path)

if __name__ == '__main__':
    for args in (('team_marks_template.html', 'state/marks.json', 'team_marks.html'),
                 ('season_viewer_template.html', 'state/schedule_view.json', 'season_viewer.html'),
                 ('committee_week_template.html', 'state/committee_week.json', 'committee_week.html'),
                 ('committee_room_template.html', 'state/committee_board.json', 'committee_room.html'),
                 ('playoff_board_template.html', 'state/playoff_board.json', 'playoff_board.html'),
                 ('draft_board_template.html', 'state/draft_board.json', 'draft_board.html'),
                 ('preseason_template.html', 'state/preseason.json', 'preseason.html'),
                 ('decade_template.html', 'state/decade.json', 'decade.html'),
                 ('coach_board_template.html', 'state/coach_board.json', 'coach_board.html')):
        n, sz = build(*args)
        print('  %-24s %8.1f KB' % (n, sz/1024))
