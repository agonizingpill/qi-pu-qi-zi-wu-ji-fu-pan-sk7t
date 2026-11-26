        import {workspace} from '../workspace.js';
        import {el} from '../dom.js';

        const page = {
  "title": "原件错误的复核方向",
  "module": "嫌疑签条",
  "caption": "嫌疑签条",
  "detail": "依据棋钟间隔、提子数量和重复落点标记嫌疑，查看固定留出集得分。",
  "path": "/referee_flags",
  "columns": [
    {
      "name": "code",
      "label": "编号"
    },
    {
      "name": "ply",
      "label": "手次号"
    },
    {
      "name": "reason",
      "label": "模型复核方向"
    },
    {
      "name": "holdout",
      "label": "留出正确率"
    },
    {
      "name": "token",
      "label": "计算号"
    }
  ],
  "layout": "split",
  "view": "grid",
  "actions": [
    {
      "name": "triage",
      "label": "归类要复盘的手次",
      "path": "/referee_flags/triage",
      "fields": [
        {
          "name": "ply",
          "label": "手次号",
          "kind": "text",
          "initial": "MV-32"
        }
      ],
      "help": "线性分类器给出洁净原件或复核情形。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    },
    {
      "name": "attach_flag",
      "label": "留存裁判席嫌疑签条",
      "path": "/referee_flags/attach-flag",
      "fields": [
        {
          "name": "code",
          "label": "签条号",
          "kind": "text",
          "initial": "FLAG-44"
        },
        {
          "name": "token",
          "label": "运算号",
          "kind": "token",
          "initial": ""
        }
      ],
      "help": "将结果关联到原始手次编号。",
      "roles": [
        "operator",
        "reviewer"
      ],
      "success": "已写入"
    }
  ]
};

        export const {title} = page;
        export const key = "referee_flags";
        export async function render(root, role) {
          await workspace(root, role, page);

        }
