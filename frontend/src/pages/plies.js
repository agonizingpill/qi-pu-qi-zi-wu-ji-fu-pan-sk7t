        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "手次原件和实盘重放",
  "module": "棋钟与手次",
  "caption": "棋钟与手次",
  "detail": "记录棋钟时间差、重复落点及提子数量。在棋盘上重放后记入提子见证。",
  "path": "/plies",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "game",
      "label": "对局"
    },
    {
      "name": "number",
      "label": "手次"
    },
    {
      "name": "gap",
      "label": "棋钟差秒"
    },
    {
      "name": "capture_claim",
      "label": "记录提子数"
    },
    {
      "name": "replayed",
      "label": "重放提子数"
    },
    {
      "name": "repeat_move",
      "label": "重复落点"
    },
    {
      "name": "witness",
      "label": "已重放"
    },
    {
      "name": "adjudicated",
      "label": "勘误后确认"
    }
  ],
  "layout": "stack",
  "view": "table",
  "actions": [
    {
      "name": "attach_ply",
      "label": "登记棋谱手次",
      "path": "/plies/attach-ply",
      "fields": [
        {
          "name": "code",
          "label": "手次号",
          "kind": "text",
          "initial": "MV-32"
        },
        {
          "name": "game",
          "label": "对局号",
          "kind": "text",
          "initial": "G-41"
        },
        {
          "name": "number",
          "label": "手次",
          "kind": "int",
          "initial": 32
        },
        {
          "name": "gap",
          "label": "棋钟差秒",
          "kind": "float",
          "initial": 12
        },
        {
          "name": "capture_claim",
          "label": "原件提子",
          "kind": "int",
          "initial": 4
        },
        {
          "name": "repeat_move",
          "label": "落点重复",
          "kind": "bool",
          "initial": true
        }
      ],
      "help": "手次以裁判席原件为准。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "verify_replay",
      "label": "记录实盘重放",
      "path": "/plies/verify-replay",
      "fields": [
        {
          "name": "ply",
          "label": "手次号",
          "kind": "text",
          "initial": "MV-32"
        },
        {
          "name": "actual",
          "label": "棋盘重放提子",
          "kind": "int",
          "initial": 2
        }
      ],
      "help": "复核员逐子重放并保存实数。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "plies";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
