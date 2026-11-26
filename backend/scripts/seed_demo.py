import json
from sqlalchemy import func, select

from core.db import transaction
from domain.demo import FIXTURES
from domain.replay_model import replay_sheets
from domain import replay_service


def seed():
    sizes = {}
    with transaction() as conn:
        for table, rows in FIXTURES:
            for row in rows:
                present = conn.scalar(select(table.c.code).where(table.c.code == row['code']))
                if present is None:
                    conn.execute(table.insert().values(**row))
            sizes[table.name] = conn.scalar(select(func.count()).select_from(table))

        # 重放单直接入库，需补跑一次同局核对，生成待签认/待复核方案。
        games = {r['game'] for r in conn.execute(select(replay_sheets.c.game).distinct()).mappings()}
        for game in games:
            replay_service._recompute_game(conn, game)

    return sizes


if __name__ == '__main__':
    print(json.dumps(seed(), ensure_ascii=False, sort_keys=True))
