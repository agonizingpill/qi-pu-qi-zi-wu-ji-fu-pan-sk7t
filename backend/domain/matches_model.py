from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


matches = Table('matches', metadata,
    Column('code', String(64), primary_key=True),
    Column('white', String(160), nullable=False),
    Column('black', String(160), nullable=False),
    Column('round_no', Integer, nullable=False),
    Column('open', Boolean, nullable=False),
    CheckConstraint('round_no > 0'),
)
