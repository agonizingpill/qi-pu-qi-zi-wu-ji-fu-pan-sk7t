from fastapi import APIRouter, Depends

from core.auth import actor, allow
from core.audit import record
from core.db import transaction
from core.records import scan
from domain import matches_service as service
from domain.matches_model import matches
from domain.matches_schemas import ReviewWindow

router = APIRouter()

@router.get('/matches')
def list_matches(user=Depends(actor)):
    with transaction() as conn:
        return scan(conn, matches)


@router.post('/matches/review-window')
def review_window(data: ReviewWindow, user=Depends(actor)):
    allow(user, ('reviewer',))
    with transaction() as conn:
        output = service.review_window(conn, user, data)
        record(conn, user, 'matches.review_window')
        return output
