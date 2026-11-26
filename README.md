# 棋谱棋子误记复盘

合川围棋裁判组保留原棋谱，将筛出的手次交给棋盘重放，并把提子差写入有签认的勘误簿。

## 现场工作与联系人

模拟客户为合川围棋裁判组。赛事对局、棋钟手次、误记嫌疑分类、裁判勘误；提子冲突未重放禁止锁定勘误。

- 对局原件 `matches`，字段为 `white`（白方）、`black`（黑方）、`round_no`（轮次）、`open`（复核中）。模型约束位于 `backend/domain/matches_model.py`，规则位于 `matches_service.py`。
- 棋钟与手次 `plies`，字段为 `game`（对局）、`number`（手次）、`gap`（棋钟差秒）、`capture_claim`（记录提子数）、`replayed`（重放提子数）、`repeat_move`（重复落点）、`witness`（已重放）、`adjudicated`（勘误后确认）。模型约束位于 `backend/domain/plies_model.py`，规则位于 `plies_service.py`。
- 嫌疑签条 `referee_flags`，字段为 `ply`（手次号）、`reason`（模型复核方向）、`holdout`（留出正确率）、`token`（计算号）。模型约束位于 `backend/domain/referee_flags_model.py`，规则位于 `referee_flags_service.py`。
- 裁判勘误本 `errata`，字段为 `flag`（嫌疑签条，逐签条签认时填）、`ply`（手次，整组签认时填）、`plan`（核对方案）、`official`（签认提子数）、`corrigendum`（勘误说明）。模型约束位于 `backend/domain/errata_model.py`，规则位于 `errata_service.py`。
- 实盘重放单 `replay_sheets`，字段为 `game`（对局）、`from_number`/`to_number`（覆盖手次区间）、`total_captures`（该段提子总数）、`makeup`（是否补单）、`seq`（到达序）。一张单只记一段的提子总数，多张单可覆盖同一手。模型位于 `backend/domain/replay_model.py`，规则位于 `replay_service.py`。
- 同局重叠单核对方案 `reconciliations`，字段为 `game`、`status`（`ready` 可签认 / `review` 待复核 / `superseded` 已作废 / `signed` 已签认入簿）、`score`（各手“正常分”加总）、`sheets`（同组重放单）、`allocation`（逐手分法）、`sheet_totals`（各单区间合计）、`reason`。模型位于 `backend/domain/reconciliation_model.py`，纯算法在 `reconcile_engine.py`。

### 重叠重放单核对规则

实盘重放有时只记一段的提子总数，几张重放单还会记到同一手。勘误页把同局区间重叠的单并为一组一起核对：

1. 逐手分法必须让每张单覆盖手次之和正好等于其登记总数；已逐手重放（`witness`）或已勘误（`adjudicated`）的手为固定值，其余手在 0–50 内取值。
2. 按现有 SGD hinge 模型给各手在候选提子数下的“正常”类判别分加总，取唯一最高分方案（`ready`）。
3. 无解或最高分并列时不择优，置 `review` 待复核；晚到重放若缺手次原件或凑不齐总数，同样待复核。
4. 补单与签认可同一次请求提交：补单先在独立事务办妥，作废旧方案并重算；随后签认在独立事务进行，任一手签不了则整组不入簿、原谱照留，但已办妥的补单保留。
5. 整组签认通过后每手写一条勘误（`official` 取方案分配数），原谱 `plies` 提子数不变，只置 `adjudicated`。

团队为模拟的6 人裁判组，维护业余联赛现场棋谱。

棋钟、转录格和裁判手写更正单分开登记。跳手时序难定位，提子票据可能和实盘不符，封账后难证明勘误采用了哪次重放。

原始手次和裁判重放进入复盘台，比赛记录员签发可追溯的正式勘误。

### 一天的业务操作

1. 09:00 查阅 G-41 黑白双方原始谱。
2. 09:20 登记第 32 手，记录提子四枚。
3. 10:00 计算嫌疑类别。
4. 11:00 把疑似重复落点锁定到 FLAG-44。
5. 13:00 重放前签认被拒绝。
6. 13:30 裁判重放，发现仅提两枚。
7. 14:00 签发 ER-44，原谱提子数字仍保留。

## 启动

```sh
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

打开 `http://127.0.0.1:18314`。FastAPI OpenAPI 在 `http://127.0.0.1:19314/docs`。
Compose 运行 Nginx、Python FastAPI、独立 Redis 消费进程、SQL 数据库和 Redis，SQL 与 Redis 使用命名卷。
本机开发时，在 Python 3.11 环境安装 `backend/requirements.txt` 后从 backend 目录运行 `uvicorn core.app:app`。须提供 `DATABASE_URL`、`REDIS_URL`、`JWT_SECRET`，`SEED_DEMO` 控制演示初始化。

| 演示账号 | 权限 |
|---|---|
| operator@demo.test | 提交领域记录和计算请求 |
| reviewer@demo.test | 提交记录并执行有业务约束的复核操作 |
| viewer@demo.test | 浏览业务台账 |

三个本地演示账号均使用 `DemoC0de!2026`。角色在 `backend/core/roles.py` 和 `frontend/src/store.js` 中声明。计算状态在 worker、queueing、API 和同一前端 store 中使用。

## 页面与接口

| 业务任务 | FastAPI 路由 | 页面 |
|---|---|---|
| 对局原件 | `/matches` /matches/review-window | `frontend/src/pages/matches.js` |
| 棋钟与手次 | `/plies` /plies/attach-ply，/plies/verify-replay | `frontend/src/pages/plies.js` |
| 嫌疑签条 | `/referee_flags` /referee_flags/triage，/referee_flags/attach-flag | `frontend/src/pages/referee_flags.js` |
| 裁判勘误本 | `/errata` /errata/issue-erratum | `frontend/src/pages/errata.js` |
| 实盘重放单与同局核对 | `/replay-sheets` /replay-sheets/attach-sheet，/replay-sheets/attach-makeup；`/reconciliations` /reconciliations/recompute，/reconciliations/sign-group | `frontend/src/pages/errata.js` |

SQL 实体与约束在 `backend/domain` 下维护。前端使用原生 ES modules。核心算子为 SGDClassifier hinge。在固定种子生成的三类模拟原件特征上训练 SGD hinge，按类留出 27 条，回传判别分数。

棋谱手次只记录统计特征，线下重放负责核对围棋规则。

[MIT](LICENSE)
