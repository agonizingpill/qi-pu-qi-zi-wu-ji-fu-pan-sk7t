from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.matches_model import matches
from domain.plies_model import plies
from domain.referee_flags_model import referee_flags
from domain.errata_model import errata


def attach_ply(conn, user, data):
    g=get(conn,matches,data.game,lock=True)
    need(g['open'],'对局已封账')
    need(1<=data.number<=600 and 0<=data.gap<=3600 and 0<=data.capture_claim<=50,'棋钟或棋盘字段越界')
    need(not any(x['game']==data.game and x['number']==data.number for x in scan(conn,plies)),'该对局已有此手次')
    return insert(conn,plies,**data.model_dump(),replayed=0,witness=False,adjudicated=False)


def verify_replay(conn, user, data):
    r=get(conn,plies,data.ply,lock=True)
    need(get(conn,matches,r['game'])['open'] and not r['adjudicated'],'无法修改已勘误或冻结的手次')
    need(0<=data.actual<=50,'重放数量越界')
    return update(conn,plies,data.ply,replayed=data.actual,witness=True)
