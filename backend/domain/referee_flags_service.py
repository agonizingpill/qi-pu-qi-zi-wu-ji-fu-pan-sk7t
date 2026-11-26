from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.matches_model import matches
from domain.plies_model import plies
from domain.referee_flags_model import referee_flags
from domain.errata_model import errata


def triage(conn, user, data):
    row=get(conn,plies,data.ply)
    need(get(conn,matches,row['game'])['open'],'对局已封账')
    return submit(user,{'source':row})


def attach_flag(conn, user, data):
    outcome=result(user,data.token)
    row=outcome['input']['source']; metrics=outcome['result']
    need(not get(conn,plies,row['code'])['adjudicated'],'原件已经勘误')
    return insert(conn,referee_flags,code=data.code,ply=row['code'],reason=metrics['label'],
                  holdout=metrics['held_accuracy'],token=data.token)
