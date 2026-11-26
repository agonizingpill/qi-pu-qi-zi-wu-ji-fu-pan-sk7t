import {request} from '../api.js';
import {el, display} from '../dom.js';
import {status, dataView, titleBlock} from '../widgets.js';
import {ROLES} from '../store.js';

const STATUS_TEXT = {ready: '可签认', review: '待复核', superseded: '已作废', signed: '已签认入簿'};

const errataColumns = [
  {name: 'code', label: '编号'},
  {name: 'flag', label: '嫌疑签条'},
  {name: 'ply', label: '手次'},
  {name: 'plan', label: '核对方案'},
  {name: 'official', label: '签认提子数'},
  {name: 'corrigendum', label: '勘误说明'},
];

function field(label, name, kind, initial) {
  return el('label', {}, el('span', {}, label),
    el('input', {name, required: '', type: kind === 'int' ? 'number' : 'text', value: initial ?? ''}));
}

function actionForm(title, help, fields, onSubmit, refresh) {
  const notice = status('');
  const button = el('button', {type: 'submit'}, title);
  const form = el('form', {class: 'action'},
    el('h3', {}, title), el('p', {}, help),
    el('div', {class: 'fields'}, fields), button, notice);
  form.addEventListener('submit', async event => {
    event.preventDefault();
    button.disabled = true;
    notice.className = 'status';
    try {
      const data = Object.fromEntries(new FormData(form).entries());
      for (const f of fields) {
        if (f.type === 'number') data[f.name] = Number(data[f.name]);
      }
      await onSubmit(data);
      notice.textContent = '已写入';
      notice.classList.add('ok');
      await refresh();
    } catch (error) {
      notice.textContent = error.message;
      notice.classList.add('error');
    } finally {
      button.disabled = false;
    }
  });
  return form;
}

function planCard(plan, role, refresh) {
  const badge = el('span', {class: 'badge ' + plan.status}, STATUS_TEXT[plan.status] || plan.status);
  const allocation = Object.entries(plan.allocation)
    .sort((a, b) => Number(a[0]) - Number(b[0]))
    .map(([number, value]) => `第${number}手=${value}`).join('，');
  const totals = Object.entries(plan.sheet_totals || {}).map(([code, sum]) => `${code}合计${sum}`).join('，');
  const card = el('article', {class: 'record plan-' + plan.status},
    el('h3', {}, plan.code, ' ', badge),
    el('dl', {},
      el('dt', {}, '对局'), el('dd', {}, plan.game),
      el('dt', {}, '同组重放单'), el('dd', {}, display(plan.sheets)),
      el('dt', {}, '状态说明'), el('dd', {}, plan.reason),
      el('dt', {}, '正常分加总'), el('dd', {}, String(plan.score)),
      el('dt', {}, '逐手分法'), el('dd', {}, allocation || '—'),
      el('dt', {}, '各单核对'), el('dd', {}, totals || '—')));

  if (role === 'reviewer' && (plan.status === 'ready' || plan.status === 'review' ||
      plan.status === 'superseded')) {
    const planInput = el('input', {name: 'plan', type: 'hidden', value: plan.code});
    const note = status('');
    const btn = el('button', {type: 'submit'}, '整组签认入簿');
    const form = el('form', {class: 'sign'}, planInput, btn, note);
    form.addEventListener('submit', async event => {
      event.preventDefault();
      btn.disabled = true;
      note.className = 'status';
      try {
        const r = await request('/reconciliations/sign-group', {plan: plan.code});
        note.textContent = '整组已签认：' + display(r.code);
        note.classList.add('ok');
        await refresh();
      } catch (error) {
        note.textContent = error.message;
        note.classList.add('error');
      } finally {
        btn.disabled = false;
      }
    });
    card.append(form);
  }
  return card;
}

export const {title} = {title: '裁判勘误与重放单核对'};
export const key = 'errata';

export async function render(root, role) {
  const ledger = el('section', {class: 'ledger', 'aria-label': '裁判勘误本'});
  const plansPanel = el('section', {class: 'ledger', 'aria-label': '同局重叠单核对'});
  const sheetsPanel = el('section', {class: 'ledger', 'aria-label': '实盘重放单'});

  const refresh = async () => {
    try {
      const [errataRows, sheets, plans] = await Promise.all([
        request('/errata'), request('/replay-sheets'), request('/reconciliations')]);
      ledger.replaceChildren(el('h2', {}, '裁判勘误本（保留原谱，另记更正数）'),
        dataView(errataRows, errataColumns, 'table'));
      sheetsPanel.replaceChildren(el('h2', {}, '实盘重放单（一段区间的提子总数）'),
        dataView(sheets, [
          {name: 'code', label: '单号'}, {name: 'game', label: '对局'},
          {name: 'from_number', label: '起手'}, {name: 'to_number', label: '止手'},
          {name: 'total_captures', label: '提子总数'},
          {name: 'makeup', label: '补单'}, {name: 'seq', label: '到达序'},
        ], 'table'));
      const current = plans.filter(p => p.status !== 'superseded');
      const cards = current.length
        ? el('div', {class: 'records grid'}, current.map(p => planCard(p, role, refresh)))
        : status('暂无核对方案，先登记重放单。');
      plansPanel.replaceChildren(
        el('h2', {}, '同局重叠单核对（逐手分法对齐每张单总数，按正常分加总择优）'),
        el('p', {class: 'intro'}, '无解或最高分并列时标“待复核”；补单到达后旧方案自动作废。'),
        cards);
    } catch (error) {
      plansPanel.replaceChildren(status(error.message, 'error'));
    }
  };

  const actions = el('section', {class: 'actions'});
  if (role === 'operator' || role === 'reviewer') {
    actions.append(actionForm('登记实盘重放单', '只记一段手次区间的提子总数；多张单可覆盖同一手，提交即自动核对。', [
      field('重放单号', 'code', 'text', 'RS-1'),
      field('对局号', 'game', 'text', 'G-41'),
      field('起手', 'from_number', 'int', 31),
      field('止手', 'to_number', 'int', 33),
      field('提子总数', 'total_captures', 'int', 5),
    ], data => request('/replay-sheets/attach-sheet', data), refresh));
    actions.append(actionForm('登记补单（同局后到）', '补单先办妥即作废旧方案并重算；可在签认时一并提交。', [
      field('补单号', 'code', 'text', 'RS-2'),
      field('对局号', 'game', 'text', 'G-41'),
      field('起手', 'from_number', 'int', 32),
      field('止手', 'to_number', 'int', 32),
      field('提子总数', 'total_captures', 'int', 2),
    ], data => request('/replay-sheets/attach-makeup', data), refresh));
  }
  if (role === 'reviewer') {
    actions.append(actionForm('补单并整组签认', '补单先办妥再签最新方案；任一手签不了则整组不入簿，原谱照留。', [
      field('原方案号', 'plan', 'text', 'RC-G41-RS-1'),
      field('补单号', 'code', 'text', 'RS-3'),
      field('对局号', 'game', 'text', 'G-41'),
      field('起手', 'from_number', 'int', 31),
      field('止手', 'to_number', 'int', 31),
      field('提子总数', 'total_captures', 'int', 1),
    ], data => request('/reconciliations/sign-group', {
      plan: data.plan,
      makeup: {code: data.code, game: data.game, from_number: data.from_number,
               to_number: data.to_number, total_captures: data.total_captures},
    }), refresh));
    actions.append(actionForm('手动重新核对', '按现有重放单与逐手重放实数重新择优。', [
      field('对局号', 'game', 'text', 'G-41'),
    ], data => request('/reconciliations/recompute', data), refresh));
    actions.append(actionForm('签出棋谱勘误（逐签条）', '不调换原谱，只在裁判勘误本附更正数；提子冲突须先实盘重放。', [
      field('勘误单号', 'code', 'text', 'ER-44'),
      field('签条号', 'flag', 'text', 'FLAG-44'),
      field('勘误说明', 'corrigendum', 'text', '第32手按双人重放提子数勘误'),
    ], data => request('/errata/issue-erratum', data), refresh));
  }

  root.replaceChildren(
    titleBlock('裁判勘误本', '裁判勘误与重放单核对',
      '同局重叠的重放单一起核对：逐手分法须对上每张单的总数，按现有模型给各手正常分加总择优；'
      '无解或最高分并列转待复核。补单先办妥即作废旧方案；整组签认时任一手签不了则整组不入簿，原谱照留。'),
    el('div', {class: 'work stack'},
      el('div', {class: 'ledger-col'}, plansPanel, sheetsPanel, ledger),
      actions));
  await refresh();
}
