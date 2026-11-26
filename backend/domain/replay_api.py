from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import replay_service as service
from domain.replay_model import replay_sheets
from domain.reconciliation_model import reconciliations
from domain.replay_schemas import AttachSheet, Recompute, SignGroup

router = APIRouter()


@router.get('/replay-sheets')
def list_sheets(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, replay_sheets)


@router.get('/reconciliations')
def list_reconciliations(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, reconciliations)


@router.post('/replay-sheets/attach-sheet')
def attach_sheet(data: AttachSheet, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.attach_sheet(conn, user, data, makeup=False)
        record(conn, user, 'replay.attach_sheet')
        return output


@router.post('/replay-sheets/attach-makeup')
def attach_makeup(data: AttachSheet, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.attach_sheet(conn, user, data, makeup=True)
        record(conn, user, 'replay.attach_makeup')
        return output


@router.post('/reconciliations/recompute')
def recompute(data: Recompute, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.recompute(conn, user, data)
        record(conn, user, 'reconciliation.recompute')
        return output


@router.post('/reconciliations/sign-group')
def sign_group(data: SignGroup, user=Depends(actor)):
    allow(user, ('reviewer',))
    plan_code = data.plan
    # 补单与签认同一次请求：补单先在独立事务办妥，签认再独立提交；
    # 签认被拒时整组不入簿，但已办妥的补单与重算结果保留。
    if data.makeup is not None:
        with transaction() as conn:
            service.attach_sheet(conn, user, data.makeup, makeup=True)
            record(conn, user, 'replay.attach_makeup')
            # 补单已作废旧方案，改签该补单所在组重算后的当前方案。
            current = service.current_plan_for_sheet(conn, data.makeup.game, data.makeup.code)
            if current is not None:
                plan_code = current['code']
    with transaction() as conn:
        output = service.sign_group(conn, user, SignGroup(plan=plan_code, makeup=None))
        record(conn, user, 'reconciliation.sign_group')
        return output
