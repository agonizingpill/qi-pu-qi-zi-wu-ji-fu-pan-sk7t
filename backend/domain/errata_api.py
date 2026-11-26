from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import errata_service as service
from domain.errata_model import errata
from domain.errata_schemas import IssueErratum

router = APIRouter()

@router.get('/errata')
def list_errata(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, errata)


@router.post('/errata/issue-erratum')
def issue_erratum(data: IssueErratum, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.issue_erratum(conn, user, data)
        record(conn, user, 'errata.issue_erratum')
        return output
