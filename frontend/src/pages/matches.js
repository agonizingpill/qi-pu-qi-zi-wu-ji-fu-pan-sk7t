        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "原谱复核开关",
  "module": "对局原件",
  "caption": "对局原件",
  "detail": "裁判长可冻结整局。冻结后手次原件与勘误均保留。",
  "path": "/matches",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "white",
      "label": "白方"
    },
    {
      "name": "black",
      "label": "黑方"
    },
    {
      "name": "round_no",
      "label": "轮次"
    },
    {
      "name": "open",
      "label": "复核中"
    }
  ],
  "layout": "flip",
  "view": "grid",
  "actions": [
    {
      "name": "review_window",
      "label": "设置复核窗口",
      "path": "/matches/review-window",
      "fields": [
        {
          "name": "game",
          "label": "对局号",
          "kind": "text",
          "initial": "G-41"
        },
        {
          "name": "open",
          "label": "是否重开复核",
          "kind": "bool",
          "initial": true
        }
      ],
      "help": "核对异常后再关闭复盘窗口。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "matches";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
