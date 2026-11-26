        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "裁判勘误签认",
  "module": "裁判勘误本",
  "caption": "裁判勘误本",
  "detail": "涉提子差异时必须有实盘重放。保留原谱，勘误册另外标出正确提子数。",
  "path": "/errata",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "flag",
      "label": "嫌疑签条"
    },
    {
      "name": "official",
      "label": "签认提子数"
    },
    {
      "name": "corrigendum",
      "label": "勘误说明"
    }
  ],
  "layout": "flip",
  "view": "stack",
  "actions": [
    {
      "name": "issue_erratum",
      "label": "签出棋谱勘误",
      "path": "/errata/issue-erratum",
      "fields": [
        {
          "name": "code",
          "label": "勘误单号",
          "kind": "text",
          "initial": "ER-44"
        },
        {
          "name": "flag",
          "label": "签条号",
          "kind": "text",
          "initial": "FLAG-44"
        },
        {
          "name": "corrigendum",
          "label": "勘误说明",
          "kind": "text",
          "initial": "第32手按双人重放提子数勘误"
        }
      ],
      "help": "勘误不调换原谱，只在裁判勘误本附更正数。",
      "roles": [
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "errata";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
