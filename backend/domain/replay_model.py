from sqlalchemy import Boolean, CheckConstraint, Column, ForeignKey, Integer, String, Table

from core.db import metadata


# 实盘重放单：只登记一段手次区间内的提子总数，多张单可能覆盖同一手。
replay_sheets = Table('replay_sheets', metadata,
    Column('code', String(64), primary_key=True),
    Column('game', String(160), ForeignKey('matches.code'), nullable=False),
    Column('from_number', Integer, nullable=False),
    Column('to_number', Integer, nullable=False),
    Column('total_captures', Integer, nullable=False),
    Column('makeup', Boolean, nullable=False),
    Column('seq', Integer, nullable=False),
    CheckConstraint('from_number > 0'),
    CheckConstraint('to_number >= from_number'),
    CheckConstraint('total_captures between 0 and 30000'),
    CheckConstraint('seq >= 0'),
)
