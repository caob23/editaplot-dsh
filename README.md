# editaplot-dsh

<p align="center">
  <strong>DeepSeek Harness 适配 EditaPlot · AI 引导的可编辑科学图表</strong>
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/caob23/editaplot-dsh/actions"><img src="https://img.shields.io/badge/build-scaffold-orange" alt="build"></a>
  <a href="https://github.com/caob23/editaplot-dsh/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="license"></a>
  <a href="https://github.com/caob23/editaplot-dsh"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="python"></a>
  <a href="https://github.com/caob23/editaplot-dsh"><img src="https://img.shields.io/badge/node-%E2%89%A520-green" alt="node"></a>
</p>

---

> **本仓库是 [`hang-jin/editaplot`](https://github.com/hang-jin/editaplot) 的 Apache-2.0 派生作品。**
> 任何在原仓库中允许的修改、再发布、商用、SaaS 化都在本仓库中允许；
> 原版权与 NOTICE 已在 `LICENSE` 与 `NOTICE` 中完整保留。

---

## 这是什么

`editaplot-dsh` 把 [EditaPlot](https://github.com/hang-jin/editaplot) 的"30+ 学术图表模板 + Origin 渲染"能力,作为一组 **MCP (Model Context Protocol) 工具**,注册进 [DeepSeek Harness (DSH)](https://github.com/deepseek-ai/deepseek-harness) 之中。安装之后,任何运行在 DSH 里的 AI Agent 都可以:

- 看到并调用 6 个 `mcp__editaplot__*` 工具
- 在跑通"兼容性检查"之后,把数据喂给模板,直接由本地 Origin 渲染出可编辑的 `.opju`、PNG、PDF 和 TIFF
- 渲染失败时拿到结构化错误码(不要 hack Origin、不要重装、不会被卡)

一句话:**让 AI 给你画可编辑的科学图表,而不是一张位图**。

## 为什么用它

| 维度 | 让 LLM 直接 `matplotlib` / `ggplot` | 本项目 |
|---|---|---|
| 矢量可编辑 | ❌ 改一处要重跑 | ✅ Origin 打开 `.opju` 继续编辑 |
| 期刊 / 学位论文图 | ❌ 风格对不齐 | ✅ 模板来自发表过的工作流 |
| 复杂图(XPS、CV、EIS、FTIR、雷达) | ❌ 现成代码难找 | ✅ 内置 30+ 模板 |
| 数据-视觉一致性 | ⚠️ 自己核 | ✅ 视觉契约 `visual_contract.md` 校验 |
| 离线 | ✅ | ✅ 全部走本地 Origin,数据不出本机 |
| 跑 Origin 2025b 默认布局 | ⚠️ 自定义 | ✅ 模板按 OriginLab 2024b baseline,2025b 视觉差异已记录 |

## 架构

```
DSH (DeepSeek Harness) ──► 加载 bundle ──► cordis.patch.yml
                                              │
                                              ├─ mcp-editaplot row
                                              │   └─ 启动 editaplot_mcp_server.py (stdio)
                                              │       └─ mcp.server.Server + stdio_server
                                              │           └─ 注册 6 个工具
                                              │               ├─ mcp__editaplot__compatibility
                                              │               ├─ mcp__editaplot__list_templates
                                              │               ├─ mcp__editaplot__describe_template
                                              │               ├─ mcp__editaplot__validate_template
                                              │               ├─ mcp__editaplot__render_chart
                                              │               └─ mcp__editaplot__export
                                              │
                                              └─ skill-editaplot row
                                                  └─ 把 skills/editaplot/SKILL.md 复制到 DSH 的 skills 目录
```

关键的工程决策:

- **用 MCP bridge 而不是直接在 DSH 里跑 Python**:保持宿主运行时是 Node/Cordis,不引入额外语言运行时;Python 进程独立可观测、可热替换。
- **优先用 `bundles/<name>/cordis.patch.yml` 接入**:这样安装时 DSH 自动把补丁层挂到当前 profile 之上,**不污染** bundle/base 公共层。
- **`failOnStartupError: false`**:即使 Origin 没装/没启动,DSH 也能起得来,工具会在调用时报错,而不是宿主挂掉。
- **`originpro==1.1.15` 版本锁**:与上游一致,锁定不漂移。

## 安装

### 方式 A:从 npm 安装(推荐)

```bash
# 通过 dsh plugin 从 npm registry 安装,自动注册到当前 profile
dsh plugin --profile web add editaplot-dsh
```

或者在 profile 的 `node_modules` 目录里直接装:

```bash
cd $DSH_HOME/profiles/web
npm install editaplot-dsh
```

DSH 会在 `pnpm install` / `npm install` 时读取 `dsh.bundle.patch` 字段,把 `cordis.patch.yml` 自动应用到目标 profile。

### 方式 B:从 GitHub 直接装

```bash
dsh plugin --profile web add github:caob23/editaplot-dsh
```

DSH 会克隆仓库到 `$DSH_HOME/profiles/web/node_modules/editaplot-dsh/`,然后挂上 bundle。

### 方式 C:本地开发链接

```bash
git clone https://github.com/caob23/editaplot-dsh.git
cd editaplot-dsh
npm install
npm run prepare
cd $DSH_HOME/profiles/web
pnpm link ../../path/to/editaplot-dsh
```

## 前置依赖

| 依赖 | 版本 | 备注 |
|---|---|---|
| Windows | 10 / 11 x64 | 上游 `originpro` 走 COM 自动化,**不**支持 macOS / Linux / WSL / Wine |
| Origin / OriginPro | 2021b – 2026b | 2025b 视觉与 2024b baseline 有差异,详见兼容性表 |
| CPython | 3.10 / 3.11 / 3.12 | MCP server 跑在 stdio 上 |
| `originpro` Python 包 | `==1.1.15` | BSD,OriginLab 官方 |
| `mcp` Python 包 | `>=1.0.0` | Anthropic 开源 MCP SDK |

启动 DSH 之前,在仓库的 Python venv 里把依赖装好:

```bash
cd editaplot-dsh
python -m venv .venv
.venv\Scripts\activate
pip install "mcp>=1.0.0"
```

## 兼容性矩阵

| Origin 版本 | 状态 | 备注 |
|---|---|---|
| 2026b (10.27) | `compatible_unverified` | SR1 修复了 readback bug(2026-08-09) |
| 2025b (10.25) | `compatible_unverified` | **本项目默认目标**;轴/边距/字体默认值变了 |
| 2024b (10.15) | `verified` | **完整 baseline**;所有模板都跑过 |
| 2023b (10.05) | `compatible_unverified` | |
| 2022b (9.95) | `compatible_unverified` | |
| 2021b (9.85) | `compatible_unverified` | |
| ≤ 2020b | `blocked` | 上游 `originpro` 1.1.15 不支持 |

详细每个模板的验证状态见 [docs/SMOKE-RESULTS.md](docs/SMOKE-RESULTS.md)(待真机填写)。

## 暴露给 Agent 的 6 个工具

### `mcp__editaplot__compatibility()`

返回当前 Origin 环境的结构化诊断,**任何渲染请求之前都应该先调它**。

```json
{
  "version_string": "10.25.201",
  "status": "compatible_unverified",
  "target": "2025b",
  "verified_baseline": "2024b",
  "originpro": "1.1.15",
  "warnings": []
}
```

- `verified` —— 2024b baseline,所有模板都跑过
- `compatible_unverified` —— 启用了,但是没在本环境跑过 smoke
- `blocked` —— 启用了,但 originpro 拒绝(版本太老、Automation Server 没开等)

### `mcp__editaplot__list_templates()`

返回所有可用模板的元数据数组(30+):`name`, `description`, `verified_on`, `domain`, `inputs`。

### `mcp__editaplot__describe_template(name)`

返回单个模板的 `visual_contract.md` 内容,包含输入字段、必填项、视觉契约。

### `mcp__editaplot__validate_template(name, data)`

`render` 之前的"纸上模拟":检查数据列与模板要求是否对得上、列名是否一致、缺失字段在哪。

### `mcp__editaplot__render_chart(input)`

**核心工具**。参数:

| 字段 | 类型 | 说明 |
|---|---|---|
| `template` | string | 模板名,例如 `xps`、`cv`、`bland_altman` |
| `data` | string \| object | 数据文件路径(JSON/CSV/OPJU),或内联 data |
| `evidence_role` | enum: `main` / `support` / `verify` | 渲染产物的语义角色 |
| `output_dir` | string | 产物落地目录 |

返回:

```json
{
  "ok": true,
  "opju": "C:/out/xps.opju",
  "images": {
    "png": "C:/out/xps.png",
    "pdf": "C:/out/xps.pdf",
    "tif": "C:/out/xps.tif"
  },
  "evidence_role": "main"
}
```

失败时:

```json
{
  "ok": false,
  "code": "EDITAPLOT_NOT_FOUND",
  "message": "Origin COM Automation Server 不可用。请检查 Origin 是否已安装,Automation Server 是否已启用。",
  "remediation": "Tools → System Variables → 检查 Automation Server 设置"
}
```

### `mcp__editaplot__export(opju, formats)`

把已渲染的 `.opju` 重新导出成指定格式,不需要重跑模板。

## 推荐 Agent 工作流

```text
1. compatibility()                            ← 必走
2. list_templates() / describe_template(x)    ← 选模板
3. validate_template(x, data)                ← 纸上跑一遍
4. render_chart({template, data, output})    ← 真渲染
5. export({{opju, formats}}                   ← 可选,改格式
```

Agent 在 system prompt 里应该被告知:**没有第 1 步,不能调第 4 步**。

## 项目结构

```
editaplot-dsh/
├── package.json                    # npm manifest,带 dsh.bundle.patch 字段
├── cordis.patch.yml                # DSH bundle 补丁(两行:mcp + skill)
├── editaplot_mcp_server.py         # stdio MCP server(6 个工具)
├── pnpm-workspace.yaml             # DSH 期望的 workspace 配置
├── skills/
│   └── editaplot/
│       └── SKILL.md                # DSH 格式的 skill 文档
├── scripts/
│   ├── build-bundle.mjs            # `prepare` 钩子,写 lib/index.js
│   └── push-with-pat.ps1           # 推 GitHub 用
├── tests/
│   └── plugin-install.spec.ts      # vitest smoke
├── docs/
│   ├── PAT-申请指南.md             # GitHub PAT 申请步骤
│   ├── SMOKE-TEST.md               # 真机 smoke 清单
│   ├── SMOKE-RESULTS.md            # 模板:真机 smoke 记录
│   └── TROUBLESHOOTING.md          # 常见问题
├── LICENSE                         # Apache-2.0 全文
├── NOTICE                          # 上游归属 + 派生说明
├── CHANGELOG.md                    # 版本变更
└── CONTRIBUTING.md                 # 贡献指南
```

## 上游声明

- 原项目: <https://github.com/hang-jin/editaplot>
- 上游 LICENSE: Apache-2.0(<https://www.apache.org/licenses/LICENSE-2.0>)
- 派生 LICENSE: 见本仓库 `LICENSE`,copyright `2026 editaplot-dsh contributors`
- 上游 NOTICE 内容已在 `NOTICE` 中完整保留

本项目**不**修改、不重打包、不重分发 `originpro` Python 包或 OriginLab 任何二进制。Origin 是 OriginLab Corporation 的注册商标,本项目与之没有官方关联。

## 开发与测试

```bash
git clone https://github.com/caob23/editaplot-dsh.git
cd editaplot-dsh
npm install
npm run prepare
npx vitest run tests/
```

5 个 smoke test 检查:

1. `package.json` 声明了 `dsh.bundle.patch` 字段
2. `LICENSE` 与 `NOTICE` 是 Apache-2.0 兼容且包含上游归属
3. `cordis.patch.yml` 含 `mcp-editaplot` 行,`transport: stdio`,`failOnStartupError: false`
4. `skills/editaplot/SKILL.md` 引用了 `mcp__editaplot__compatibility`
5. `editaplot_mcp_server.py` 锁定了 `originpro==1.1.15`

## 故障排查

遇到问题先看 [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)。常见症状:

| 症状 | 看哪个章节 |
|---|---|
| DSH 启动后看不到 `mcp__editaplot__*` 工具 | "MCP server 不响应" |
| 渲染失败 `EDITAPLOT_NOT_FOUND` | "Origin 兼容性失败" |
| 2025b 视觉跟 2024b 不一样 | "2025b 渲染出图但视觉不同" |
| 推送 GitHub 报 `schannel` 错 | "push 失败" |

## 路线图

- [ ] 真机 smoke test(2024b / 2025b 完整跑一遍)
- [ ] 把 18 个 commit 合成 1 个 squash commit(可选)
- [ ] 给上游 `hang-jin/editaplot` 提 PR,把 6 个 CLI 子命令(`compat check` / `templates list` 等)加上去
- [ ] 2026b SR1 之后,补一次兼容性验证
- [ ] 在 awesome-dsh-plugin 列表里提交本项目

## 许可

Apache-2.0 —— 详见 [LICENSE](LICENSE) 与 [NOTICE](NOTICE)。
