"""同局重叠重放单的核对引擎。

约束：每张重放单登记一段手次区间的提子总数，逐手分法必须让每张单覆盖手次之和
正好等于其总数；已逐手重放（witness）或已勘误的手次为固定值，其余手次在 0..50
内取值。目标：按现有 SGD 模型给各手的“正常分”加总，分数最高者择优；无解或最高
分并列时交人工待复核。
"""

MAX_CAPTURES = 50
# 搜索规模保护：实盘每组单量很小，超限直接转待复核而非长时间穷举。
NODE_LIMIT = 200_000
SOLUTION_LIMIT = 100_000


class SearchLimit(RuntimeError):
    pass


def merged_groups(sheets):
    """把同一对局内手次区间相互重叠的重放单并为一组（仅相接不重叠者各自成组）。"""
    by_game = {}
    for sheet in sheets:
        by_game.setdefault(sheet['game'], []).append(sheet)
    groups = []
    for game, items in by_game.items():
        intervals = sorted((s['from_number'], s['to_number'], s['code']) for s in items)
        current = []
        cur_lo = cur_hi = None
        for lo, hi, code in intervals:
            if cur_lo is None:
                cur_lo, cur_hi = lo, hi
                current = [code]
            elif lo <= cur_hi:
                cur_hi = max(cur_hi, hi)
                current.append(code)
            else:
                groups.append({'game': game, 'sheets': current})
                cur_lo, cur_hi = lo, hi
                current = [code]
        if current:
            groups.append({'game': game, 'sheets': current})
    return groups


def solve(sheets, plies_by_number, score_of):
    """求一组重叠单的最优逐手分法。

    sheets:  [{code, from_number, to_number, total_captures}]
    plies_by_number: {手次号: ply 行}
    score_of: (ply, 候选提子数) -> 该手取该值时的“正常分”（整数）
    返回 dict: feasible, best(分配 dict), score, totals(各单区间合计), reason, tie
    """
    numbers = sorted({n for s in sheets for n in range(s['from_number'], s['to_number'] + 1)})
    fixed = {}
    free_numbers = []
    for n in numbers:
        ply = plies_by_number.get(n)
        if ply is None:
            return {'feasible': False, 'reason': f'第{n}手缺少手次原件，晚到重放无法凑齐总数', 'tie': False}
        if ply['witness'] or ply['adjudicated']:
            # 逐手重放照实数；已签勘误的手按勘误数固定。
            fixed[n] = ply['replayed']
        else:
            free_numbers.append(n)

    ranges = [(s['from_number'], s['to_number'], s['total_captures'], s['code']) for s in sheets]

    # 固定值先做一次区间合计校验。
    def interval_sum(lo, hi, assign):
        return sum(assign[n] for n in range(lo, hi + 1) if n in assign)

    for lo, hi, total, code in ranges:
        known = interval_sum(lo, hi, fixed)
        unknown = sum(1 for n in range(lo, hi + 1) if n not in fixed)
        if known > total or known + unknown * MAX_CAPTURES < total:
            return {'feasible': False, 'reason': f'重放单 {code} 的总数与逐手重放实数凑不齐', 'tie': False}

    free_set = set(free_numbers)
    best = None
    best_score = None
    tie = False
    nodes = 0
    solutions = 0
    assign = dict(fixed)

    def feasible_partials():
        """每张单在当前已赋值下，剩余自由手能否补到目标总数。"""
        for lo, hi, total, _code in ranges:
            known = interval_sum(lo, hi, assign)
            slots = sum(1 for n in range(lo, hi + 1) if n in free_set and n not in assign)
            if known > total or known + slots * MAX_CAPTURES < total:
                return False
        return True

    def dfs(index):
        nonlocal best, best_score, tie, nodes, solutions
        nodes += 1
        if nodes > NODE_LIMIT or solutions > SOLUTION_LIMIT:
            raise SearchLimit()
        if index == len(free_numbers):
            for lo, hi, total, _code in ranges:
                if interval_sum(lo, hi, assign) != total:
                    return
            solutions += 1
            score = sum(score_of(plies_by_number[n], assign[n]) for n in numbers)
            if best_score is None or score > best_score:
                best_score = score
                best = dict(assign)
                tie = False
            elif score == best_score:
                tie = True
            return
        n = free_numbers[index]
        for value in range(MAX_CAPTURES + 1):
            assign[n] = value
            if feasible_partials():
                dfs(index + 1)
        del assign[n]

    try:
        dfs(0)
    except SearchLimit:
        return {'feasible': False, 'reason': '可行分法过多超出搜索上限，转人工待复核', 'tie': False}

    if best is None:
        return {'feasible': False, 'reason': '逐手分法无法同时对上每张重放单的总数', 'tie': False}

    totals = {code: interval_sum(lo, hi, best) for lo, hi, total, code in ranges}
    return {'feasible': True, 'best': best, 'score': best_score, 'totals': totals,
            'reason': '最高分并列，择优不唯一' if tie else '唯一最高分方案', 'tie': tie}
