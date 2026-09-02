# SMOKE-RESULTS.md — 真机 smoke 结果记录

> 每条检查项填一行。日期 / 机器 / Origin 版本必须填。结果分为：✅ pass / ⚠️ pass-with-caveat / ❌ fail / 🚫 skipped。

## 环境

| 项 | 值 |
|---|---|
| 日期 | |
| 操作者 | |
| Windows 版本 | |
| CPython 版本 | |
| Origin 版本 | (例: OriginPro 2025b / 10.25 / build 12345) |
| DSH 版本 | (`dsh --version`) |
| editaplot-dsh commit | |

## 检查项

| # | 项目 | 结果 | 备注 |
|---|---|---|---|
| 1 | bundle 加载 (`pnpm install` + `prepare`) | | |
| 2 | 单元测试 (5 个 smoke) | | |
| 3 | MCP server 干跑 | | |
| 4 | DSH 装载 bundle | | |
| 5 | 列出 MCP 工具 | | |
| 6 | compatibility smoke | | |
| 7 | list_templates | | |
| 8 | render_chart 端到端 | | |
| 9 | fallback (无 Origin) | | |
| 10 | Skill 注入 | | |

## 失败细节

> 任何 ❌ fail 项的 stdout / stderr 完整粘贴。命令: `git log -1 --format=%H`、origin 版本命令行输出等。

```
(paste here)
```

## 下一步

- [ ] 所有 ✅ 后，给上游 hang-jin/editaplot 提 PR
- [ ] 在 awesome-dsh-plugin.com 提交 editaplot-dsh 条目
- [ ] 跑通后，删掉本文件中的"scaffold-only"警告
- [ ] 在 README.md 顶部加一行：Tested on Origin 2025b (10.25) on Windows 11 x64 — YYYY-MM-DD