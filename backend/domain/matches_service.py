from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.matches_model import matches
from domain.plies_model import plies
from domain.referee_flags_model import referee_flags
from domain.errata_model import errata


def review_window(conn, user, data):
    get(conn,matches,data.game,lock=True)
    outstanding=[r for r in scan(conn,plies) if r['game']==data.game and r['capture_claim']!=r['replayed'] and
                 not r['adjudicated']]
    need(data.open or not outstanding,'尚有提子疑点待勘误')
    return update(conn,matches,data.game,open=data.open)
