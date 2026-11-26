from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


plies = Table('plies', metadata,
    Column('code', String(64), primary_key=True),
    Column('game', String(160), ForeignKey('matches.code'), nullable=False),
    Column('number', Integer, nullable=False),
    Column('gap', Float, nullable=False),
    Column('capture_claim', Integer, nullable=False),
    Column('replayed', Integer, nullable=False),
    Column('repeat_move', Boolean, nullable=False),
    Column('witness', Boolean, nullable=False),
    Column('adjudicated', Boolean, nullable=False),
    CheckConstraint('number > 0'),
    CheckConstraint('gap >= 0'),
    CheckConstraint('capture_claim between 0 and 50'),
    CheckConstraint('replayed between 0 and 50'),
)
