from sqlalchemy import Boolean, CheckConstraint, Column, Float, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


errata = Table('errata', metadata,
    Column('code', String(64), primary_key=True),
    Column('flag', String(160), ForeignKey('referee_flags.code'), nullable=False, unique=True),
    Column('official', Integer, nullable=False),
    Column('corrigendum', String(160), nullable=False),
    CheckConstraint('official >= 0'),
)
