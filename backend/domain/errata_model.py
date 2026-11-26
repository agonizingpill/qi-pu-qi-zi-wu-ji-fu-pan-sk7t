from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String, Table

from core.db import metadata


errata = Table('errata', metadata,
    Column('code', String(64), primary_key=True),
    # 逐签条签认时填 flag；整组重放核对签认时 flag 留空，改填 ply 与 plan。
    Column('flag', String(160), ForeignKey('referee_flags.code'), unique=True),
    Column('ply', String(160), ForeignKey('plies.code')),
    Column('plan', String(64), ForeignKey('reconciliations.code')),
    Column('official', Integer, nullable=False),
    Column('corrigendum', String(160), nullable=False),
    CheckConstraint('official >= 0'),
)
