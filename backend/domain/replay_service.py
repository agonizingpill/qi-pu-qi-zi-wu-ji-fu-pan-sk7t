from sqlalchemy import select

from core.records import get, insert, need, scan, update
from domain.learning import normal_score
from domain.matches_model import matches
from domain.plies_model import plies
from domain.errata_model import errata
from domain.replay_model import replay_sheets
from domain.reconciliation_model import reconciliations
from domain import reconcile_engine


def _game_sheets(conn, game):
    rows = [dict(r) for r in conn.execute(
        select(replay_sheets).where(replay_sheets.c.game == game)
        .order_by(replay_sheets.c.seq, replay_sheets.c.code)).mappings()]
    return rows


def _game_plies(conn, game):
    return [dict(r) for r in conn.execute(
        select(plies).where(plies.c.game == game).order_by(plies.c.number)).mappings()]


def attach_sheet(conn, user, data, makeup=False):
    game = get(conn, matches, data.game, lock=True)
    need(game['open'], '对局已封账')
    need(data.from_number <= data.to_number, '重放区间起止手次有误')
    need(0 <= data.total_captures <= 30000, '重放总数越界')
    existing = scan(conn, replay_sheets)
    need(not any(s['code'] == data.code for s in existing), '重放单编号已存在')
    ply_rows = _game_plies(conn, data.game)
    covered = [p for p in ply_rows if data.from_number <= p['number'] <= data.to_number]
    need(len(covered) == data.to_number - data.from_number + 1,
         '重放区间内有手次尚未登记原件，先补齐手次')
    seq = max((s['seq'] for s in existing if s['game'] == data.game), default=-1) + 1
    sheet = insert(conn, replay_sheets, code=data.code, game=data.game,
                   from_number=data.from_number, to_number=data.to_number,
                   total_captures=data.total_captures, makeup=makeup, seq=seq)
    # 新单（含补单）到达即强制重算同局各组；已有方案一律先作废，补单先办妥就作废旧方案。
    _recompute_game(conn, data.game, force=True)
    return sheet


def _recompute_game(conn, game, force=False):
    sheets = _game_sheets(conn, game)
    ply_rows = _game_plies(conn, game)
    plies_by_number = {p['number']: p for p in ply_rows}

    existing = scan(conn, reconciliations)

    # 强制模式（新重放单/补单到达）：旧的待办方案作废，已签认的保持 signed 不动。
    if force:
        for plan in existing:
            if plan['game'] == game and plan['status'] in ('ready', 'review'):
                update(conn, reconciliations, plan['code'], status='superseded',
                       reason='新重放单（含补单）到达，旧方案作废')
        existing = scan(conn, reconciliations)

    for group in reconcile_engine.merged_groups(sheets):
        member_codes = group['sheets']
        # 非强制模式下，该组已有有效方案则保留（保证 seed 幂等、不重复造方案）。
        if not force and any(p['game'] == game and p['status'] in ('ready', 'review')
                             and set(p['sheets'] or []) == set(member_codes) for p in existing):
            continue
        members = [s for s in sheets if s['code'] in member_codes]
        outcome = reconcile_engine.solve(members, plies_by_number, normal_score)
        plan_code = 'RC-' + game.replace(' ', '') + '-' + '-'.join(
            s['code'].replace(' ', '') for s in members)
        # 同组重算时复用编号会撞主键，加序号后缀。
        suffix = 1
        unique_code = plan_code
        while any(p['code'] == unique_code for p in scan(conn, reconciliations)):
            suffix += 1
            unique_code = f'{plan_code}-r{suffix}'
        if outcome['feasible'] and not outcome['tie']:
            status, reason = 'ready', outcome['reason']
        else:
            status, reason = 'review', outcome['reason']
        insert(conn, reconciliations, code=unique_code, game=game, status=status,
               score=outcome['score'] if outcome['feasible'] else 0, reason=reason,
               sheets=member_codes,
               allocation=outcome.get('best', {}),
               sheet_totals=outcome.get('totals', {}))


def recompute(conn, user, data):
    get(conn, matches, data.game, lock=True)
    need(_game_sheets(conn, data.game), '该对局尚无重放单，无法核对')
    _recompute_game(conn, data.game, force=True)
    return [p for p in scan(conn, reconciliations) if p['game'] == data.game]


def current_plan_for_sheet(conn, game, sheet_code):
    """补单重算后，定位包含该单的分组当前有效方案（ready/review）。"""
    candidates = [p for p in scan(conn, reconciliations)
                  if p['game'] == game and p['status'] in ('ready', 'review')
                  and sheet_code in (p['sheets'] or [])]
    return candidates[-1] if candidates else None


def sign_group(conn, user, data):
    """整组签认：任一手动不了则整组不入簿，原谱照留（本事务回滚）。

    补单与签认同时提交时，补单先办妥——由 API 层在独立事务落库并重算（即便随后
    签认被拒，补单与重算结果仍保留）；本函数只负责整组入簿，失败不影响已落库补单。
    """
    plan = get(conn, reconciliations, data.plan, lock=True)
    game = get(conn, matches, plan['game'], lock=True)
    need(game['open'], '对局已封账')
    need(plan['status'] != 'signed', '该组已签认入簿')
    need(plan['status'] != 'superseded', '补单已使原方案作废，请按最新方案核对')
    need(plan['status'] == 'ready', '方案待复核，暂不能整组签认')

    allocation = {int(k): v for k, v in plan['allocation'].items()}
    ply_rows = _game_plies(conn, plan['game'])
    by_number = {p['number']: p for p in ply_rows}

    # 逐手把关：已勘误或已封存的手签不了 -> 整组不入簿。
    for number in sorted(allocation):
        ply = by_number.get(number)
        need(ply is not None, f'第{number}手缺原件，整组不入簿')
        need(not ply['adjudicated'], f'第{number}手已勘误封存，整组不入簿')

    # 全部通过才写入：每手一条勘误，official 取方案分配数；原谱 plies 保持不变。
    for number in sorted(allocation):
        ply = by_number[number]
        erratum_code = f"ER-{plan['code']}-{number}"
        insert(conn, errata, code=erratum_code, flag=None, ply=ply['code'],
               plan=plan['code'], official=allocation[number],
               corrigendum=f'第{number}手按同局重叠重放单核对结果勘误（方案{plan["code"]}）')
        update(conn, plies, ply['code'], adjudicated=True)

    update(conn, reconciliations, plan['code'], status='signed', reason='整组签认入簿')
    return get(conn, reconciliations, plan['code'])
