from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import plies_service as service
from domain.plies_model import plies
from domain.plies_schemas import AttachPly, VerifyReplay

router = APIRouter()

@router.get('/plies')
def list_plies(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, plies)


@router.post('/plies/attach-ply')
def attach_ply(data: AttachPly, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.attach_ply(conn, user, data)
        record(conn, user, 'plies.attach_ply')
        return output


@router.post('/plies/verify-replay')
def verify_replay(data: VerifyReplay, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.verify_replay(conn, user, data)
        record(conn, user, 'plies.verify_replay')
        return output
