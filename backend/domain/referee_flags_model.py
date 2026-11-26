from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


referee_flags = Table('referee_flags', metadata,
    Column('code', String(64), primary_key=True),
    Column('ply', String(160), ForeignKey('plies.code'), nullable=False),
    Column('reason', String(160), nullable=False),
    Column('holdout', Float, nullable=False),
    Column('token', String(64), nullable=False, unique=True),
    CheckConstraint('holdout between 0 and 1'),
)
