from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import referee_flags_service as service
from domain.referee_flags_model import referee_flags
from domain.referee_flags_schemas import Triage, AttachFlag

router = APIRouter()

@router.get('/referee_flags')
def list_referee_flags(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, referee_flags)


@router.post('/referee_flags/triage')
def triage(data: Triage, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.triage(conn, user, data)
        record(conn, user, 'referee_flags.triage')
        return output


@router.post('/referee_flags/attach-flag')
def attach_flag(data: AttachFlag, user=Depends(actor)):
    allow(user, ('operator', 'reviewer'))
    with transaction() as conn:
        output = service.attach_flag(conn, user, data)
        record(conn, user, 'referee_flags.attach_flag')
        return output
