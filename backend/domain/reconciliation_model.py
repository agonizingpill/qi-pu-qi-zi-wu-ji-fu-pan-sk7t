from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, JSON, String, Table

from core.db import metadata


# 同局重叠重放单的核对方案：一组单一次择优结果。
# status: ready（唯一最高分，可签认）/ review（无解或最高分并列，待复核）/
#         superseded（补单到达后作废旧方案）/ signed（已整组签认入簿）
reconciliations = Table('reconciliations', metadata,
    Column('code', String(64), primary_key=True),
    Column('game', String(160), ForeignKey('matches.code'), nullable=False),
    Column('status', String(16), nullable=False),
    Column('score', Integer, nullable=False),
    Column('reason', String(160), nullable=False),
    # 组成员：重放单编号；分配：{手次号: 提子数}；各单核对：{单号: 区间合计}
    Column('sheets', JSON, nullable=False),
    Column('allocation', JSON, nullable=False),
    Column('sheet_totals', JSON, nullable=False),
    CheckConstraint("status in ('ready','review','superseded','signed')"),
)
