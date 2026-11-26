from sqlalchemy import select

from core.queueing import submit, result
from core.records import get, insert, need, scan, update
from domain.matches_model import matches
from domain.plies_model import plies
from domain.referee_flags_model import referee_flags
from domain.errata_model import errata


def issue_erratum(conn, user, data):
    flag=get(conn,referee_flags,data.flag)
    ref=get(conn,plies,flag['ply'])
    match=get(conn,matches,ref['game'],lock=True)
    ply=get(conn,plies,flag['ply'],lock=True)
    need(match['open'] and not ply['adjudicated'],'该手次已封存')
    need(ply['witness'],'提子冲突须先实盘重放')
    need(len(data.corrigendum)>=8,'请填写完整裁判说明')
    notice=insert(conn,errata,**data.model_dump(),official=ply['replayed'])
    update(conn,plies,ply['code'],adjudicated=True)
    return notice
