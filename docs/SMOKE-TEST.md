# 真机 smoke 测试清单

> **状态：未验证**。本文档描述在**真有 Origin/OriginPro 2025b** 的 Windows 10/11 x64 机器上需要做的端到端验证。本仓库目前**仅在骨架层验证过**（YAML 语法、文件结构、合约）。

## 环境要求

- Windows 10 或 11，x64
- CPython 3.10 / 3.11 / 3.12
- 已安装并激活 **Origin/OriginPro 2025b**（10.25）
- 已克隆上游 `hang-jin/editaplot` 到本地（`git clone https://github.com/hang-jin/editaplot.git`）
- 已克隆 `caob23/editaplot-dsh` 到本地
- 已安装 DeepSeek Harness (`dsh --version` 可用)
- 已有 GitHub PAT 或 SSH key 配好

## 准备

```powershell
# 假设工作目录在 C:\work
cd C:\work

# 上游 + 派生仓库
git clone https://github.com/hang-jin/editaplot.git
git clone https://github.com/caob23/editaplot-dsh.git

# 装 MCP server 依赖
python -m venv editaplot-dsh\.venv
.\editaplot-dsh\.venv\Scripts\Activate.ps1
pip install mcp>=1.0.0
```

## 检查项

### 1. bundle 加载
```powershell
cd C:\work\editaplot-dsh
pnpm install
pnpm run prepare
```
**期望**：看到 `editaplot-dsh: built lib/index.js + lib/index.d.ts`，无报错。

### 2. 单元测试
```powershell
pnpm dlx vitest run tests/
```
**期望**：5 个 smoke test 全过（package.json字段 / NOTICE / patch.yml / SKILL.md / originpro 锁版本）。

### 3. MCP server 干跑（无 Origin）
```powershell
.\editaplot-dsh\.venv\Scripts\python.exe editaplot-dsh\editaplot_mcp_server.py
```
**期望**：进程启动并停在 stdio 监听状态（没有 MCP client 接入前是挂起的）。Ctrl-C 退出。

### 4. DSH 装载 bundle
```powershell
cd C:\work\deepseek-harness
pnpm dsh plugin --profile web add ..\editaplot-dsh
pnpm dsh web --profile web
```
**期望**：DSH 启动过程中不报错（`failOnStartupError: false` 允许 Origin 缺失）。

进入 GUI → Settings → Plugins。期望看到 `editaplot-dsh` 列出、状态为 **mounted**。

### 5. 列出 MCP 工具
打开一个新的 DSH 会话，在 system prompt 中应能看到：
```
mcp__editaplot__compatibility()
mcp__editaplot__list_templates()
mcp__editaplot__describe_template(name)
mcp__editaplot__validate_template(name, data)
mcp__editaplot__render_chart(input)
mcp__editaplot__export(opju, formats)
```

如果**看不到**，说明 DSH 没认到 MCP bridge。回到步骤 4 检查 `cordis.patch.yml` 的 `serverName: editaplot` 和 `transport: stdio`。

### 6. compatibility smoke（**真机才有意义**）
```
User: 检查 Origin 兼容性
Model: 调用 mcp__editaplot__compatibility()
```
**期望**：返回结构化 JSON，包含
- `version_string`：检测到的 Origin 版本（如 `10.25`）
- `status`：`verified` / `compatible_unverified` / `blocked`
- `verified_baseline`：写死 `2024b`
- `target`：写死 `2025b`

**已知行为**：2025b 上应该返回 `compatible_unverified`（不是 baseline）。

### 7. list_templates
```
User: 列出可用模板
Model: 调用 mcp__editaplot__list_templates()
```
**期望**：返回 30+ 模板的列表，每条带 `verified_on` 字段（指向 2024b）。

### 8. render_chart 端到端（**最重要**）
```
User: 用 C:\data\demo.csv 画一个 xps
Model:
  1. compatibility() — OK
  2. describe_template("xps") — OK
  3. validate_template("xps", "C:/data/demo.csv") — OK
  4. render_chart({template: "xps", data: "C:/data/demo.csv", output_dir: "C:/out"})
```
**期望**：
- 输出目录出现：`xps.opju`、`xps.png`、`xps.pdf`、`xps.tif`
- OPJU 可在 Origin 中打开并继续编辑
- PNG/PDF/TIF 视觉无重叠、无裁切、轴标清晰

### 9. fallback 行为
```
User: 在没装 Origin 的机器上跑 render_chart
```
**期望**：
- `compatibility()` 返回 `blocked`
- `render_chart()` 返回结构化错误：
  ```json
  {"ok": false, "code": "EDITAPLOT_NOT_FOUND", "message": "..."}
  ```
- DSH 进程**不挂掉**

### 10. Skill 注入
进入 DSH 模型目录（或 `~/.dsh/skills/`），应该看到：
```
skills/
  editaplot/
    SKILL.md
```
**期望**：文件存在且包含 `mcp__editaplot__compatibility` 工具描述。

## 记录结果

每条检查项的实际结果记到 `docs/SMOKE-RESULTS.md`（下面有个空模板）。

## 已知风险

| 风险 | 影响 |
|---|---|
| DSH Loader 不认 `transport: stdio` 字段名 | MCP server 启不来 — 需要回到 `cordis.patch.yml` 改字段 |
| 上游 `editaplot.cmd` CLI 子命令命名跟我猜的不同 | 5 个 CLI 子命令 (`compat check`, `templates list`, `templates describe`, `render`, `export`) 命名要对得上 — 不对就要改 `editaplot_mcp_server.py` |
| 上游 `evidence_role` 参数不接受 `main / support / verify` | render_chart 报错 — 需要调参数值 |
| `skill-editaplot` row 的 `sourceDir/targetDir/skills` 字段是 DSH 实际 schema — 我没找到官方文档佐证 | SKILL.md 可能没自动复制 — 需要看 DSH 源码 `packages/skill*` 是否已有 skill 复制机制 |

## 上游协同建议

真机跑通后，**给上游 hang-jin/editaplot 提一个 PR**，让他们知道有 DSH 集成。如果上游愿意加 `compat check`、`templates list`、`templates describe`、`render`、`export` 这些子命令（或暴露它们作为 CLI 入口），整个适配层会稳得多。

在此之前，`editaplot-dsh` 只是一个骨架。