from domain.matches_model import matches
from domain.plies_model import plies
from domain.referee_flags_model import referee_flags
from domain.errata_model import errata
from domain.replay_model import replay_sheets
from domain.reconciliation_model import reconciliations

FIXTURES = [
    (matches, [{'code': 'G-41', 'white': '澄泉', 'black': '青石', 'round_no': 4, 'open': True}]),
    (plies, [
        {'code': 'MV-31', 'game': 'G-41', 'number': 31, 'gap': 8, 'capture_claim': 2,
         'replayed': 1, 'repeat_move': True, 'witness': True, 'adjudicated': False},
        {'code': 'MV-32', 'game': 'G-41', 'number': 32, 'gap': 12, 'capture_claim': 4,
         'replayed': 0, 'repeat_move': True, 'witness': False, 'adjudicated': False},
        {'code': 'MV-33', 'game': 'G-41', 'number': 33, 'gap': 6, 'capture_claim': 1,
         'replayed': 0, 'repeat_move': False, 'witness': False, 'adjudicated': False},
    ]),
    (referee_flags, [{'code': 'FLAG-00',
      'ply': 'MV-31',
      'reason': '原件人工复盘',
      'holdout': 0,
      'token': 'initial'}]),
    (errata, [{'code': 'ER-14', 'flag': 'FLAG-00', 'ply': None, 'plan': None,
               'official': 2, 'corrigendum': '历史只读样条'}]),
    # 两张同局重叠重放单：RS-1 覆盖 31-33 共 5 枚，RS-2 覆盖 31-32 共 3 枚；
    # 第31手已逐手重放固定为 1，由此逐手分法须同时对上两张单总数。
    (replay_sheets, [
        {'code': 'RS-1', 'game': 'G-41', 'from_number': 31, 'to_number': 33,
         'total_captures': 5, 'makeup': False, 'seq': 0},
        {'code': 'RS-2', 'game': 'G-41', 'from_number': 31, 'to_number': 32,
         'total_captures': 3, 'makeup': True, 'seq': 1},
    ]),
    (reconciliations, []),
]
