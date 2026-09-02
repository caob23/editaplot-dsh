# editaplot-dsh

<p align="center">
  <strong>DeepSeek Harness adapter for EditaPlot — AI-guided editable scientific figures</strong>
</p>

<p align="center">
  <a href="README.md">简体中文</a> · <a href="README.en.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/caob23/editaplot-dsh/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-Apache--2.0-blue" alt="license"></a>
  <a href="https://github.com/caob23/editaplot-dsh"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="python"></a>
  <a href="https://github.com/caob23/editaplot-dsh"><img src="https://img.shields.io/badge/node-%E2%89%A520-green" alt="node"></a>
</p>

---

> **This repository is an Apache-2.0 derivative of [`hang-jin/editaplot`](https://github.com/hang-jin/editaplot).**
> All modifications, repackaging, SaaS deployment, and closed-source distribution allowed by the original Apache-2.0 license are permitted here; upstream copyright and NOTICE are preserved verbatim in `LICENSE` and `NOTICE`.

---

## What this is

`editaplot-dsh` exposes [EditaPlot](https://github.com/hang-jin/editaplot)'s "30+ scientific chart templates + Origin rendering" capability as a set of **MCP (Model Context Protocol) tools** registered inside [DeepSeek Harness (DSH)](https://github.com/deepseek-ai/deepseek-harness). Once installed, any AI agent running on DSH can:

- See and invoke six `mcp__editaplot__*` tools
- After a compatibility probe, feed data to a template and have local Origin render an **editable** `.opju` plus PNG/PDF/TIFF outputs
- Get structured error codes on failure (no Origin hacking, no reinstalls, no host hangs)

In one line: **let the AI draw editable scientific figures, not a bit-packed PNG**.

## Why use it

| Dimension | Letting the LLM call `matplotlib` / `ggplot` directly | This project |
|---|---|---|
| Vector-editable | ❌ tweak one thing → rerun | ✅ Open `.opju` in Origin, keep editing |
| Journal / thesis figures | ❌ styling drifts | ✅ Templates come from published workflows |
| Complex plots (XPS, CV, EIS, FTIR, radar) | ❌ canned code is rare | ✅ 30+ built-in templates |
| Data↔visual consistency | ⚠️ you check | ✅ `visual_contract.md` validates |
| Offline | ✅ | ✅ everything goes through local Origin, data never leaves the box |
| Origin 2025b default look | ⚠️ custom | ✅ 2024b baseline; 2025b visual differences recorded |

## Architecture

```
DSH (DeepSeek Harness) ──► load bundle ──► cordis.patch.yml
                                              │
                                              ├─ mcp-editaplot row
                                              │   └─ spawns editaplot_mcp_server.py (stdio)
                                              │       └─ mcp.server.Server + stdio_server
                                              │           └─ registers 6 tools
                                              │               ├─ mcp__editaplot__compatibility
                                              │               ├─ mcp__editaplot__list_templates
                                              │               ├─ mcp__editaplot__describe_template
                                              │               ├─ mcp__editaplot__validate_template
                                              │               ├─ mcp__editaplot__render_chart
                                              │               └─ mcp__editaplot__export
                                              │
                                              └─ skill-editaplot row
                                                  └─ copies skills/editaplot/SKILL.md into DSH's skills dir
```

Key engineering decisions:

- **MCP bridge, not in-host Python** — keeps DSH's host runtime as Node/Cordis, no extra language runtime baked in. Python is a stand-alone, observable, hot-swappable child.
- **`bundles/<name>/cordis.patch.yml` join** — install-time the patch is layered on top of the current profile; the shared `bundle/base` layer stays clean.
- **`failOnStartupError: false`** — DSH boots even when Origin is missing; tools report at call-time, host never hangs.
- **`originpro==1.1.15` pin** — matches upstream; no silent drift.

## Install

### A) From npm (recommended)

```bash
dsh plugin --profile web add editaplot-dsh
```

Or directly into a profile's `node_modules`:

```bash
cd $DSH_HOME/profiles/web
npm install editaplot-dsh
```

DSH reads `dsh.bundle.patch` during `pnpm install` / `npm install` and applies the patch layer onto the target profile automatically.

### B) From GitHub

```bash
dsh plugin --profile web add github:caob23/editaplot-dsh
```

DSH clones the repo into `$DSH_HOME/profiles/web/node_modules/editaplot-dsh/` and joins the bundle.

### C) Local development link

```bash
git clone https://github.com/caob23/editaplot-dsh.git
cd editaplot-dsh
npm install
npm run prepare
cd $DSH_HOME/profiles/web
pnpm link ../../path/to/editaplot-dsh
```

## Prerequisites

| Dependency | Version | Notes |
|---|---|---|
| Windows | 10 / 11 x64 | Upstream `originpro` uses COM automation — **no** macOS / Linux / WSL / Wine support |
| Origin / OriginPro | 2021b – 2026b | 2025b visual differs from 2024b baseline, see compatibility table |
| CPython | 3.10 / 3.11 / 3.12 | MCP server runs on stdio |
| `originpro` Python pkg | `==1.1.15` | BSD, OriginLab official |
| `mcp` Python pkg | `>=1.0.0` | Anthropic's open-source MCP SDK |

Before starting DSH, populate the Python venv bundled with the bundle:

```bash
cd editaplot-dsh
python -m venv .venv
.venv\Scripts\activate
pip install "mcp>=1.0.0"
```

## Compatibility matrix

| Origin version | Status | Notes |
|---|---|---|
| 2026b (10.27) | `compatible_unverified` | SR1 fixed the readback bug (2026-08-09) |
| 2025b (10.25) | `compatible_unverified` | **default target**; axis / margin / font defaults changed |
| 2024b (10.15) | `verified` | **full baseline**; all templates run here |
| 2023b (10.05) | `compatible_unverified` | |
| 2022b (9.95) | `compatible_unverified` | |
| 2021b (9.85) | `compatible_unverified` | |
| ≤ 2020b | `blocked` | upstream `originpro` 1.1.15 does not support |

Per-template verification status goes in [docs/SMOKE-RESULTS.md](docs/SMOKE-RESULTS.md) (filled in after a real-machine run).

## The six tools exposed to the agent

### `mcp__editaplot__compatibility()`

Returns a structured diagnostic of the current Origin environment — **must be called before any render**.

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

- `verified` — 2024b baseline, all templates run
- `compatible_unverified` — Origin is up but no smoke was run here
- `blocked` — `originpro` rejected (too old, Automation Server disabled, etc.)

### `mcp__editaplot__list_templates()`

Returns metadata for every available template (30+): `name`, `description`, `verified_on`, `domain`, `inputs`.

### `mcp__editaplot__describe_template(name)`

Returns the template's `visual_contract.md` — input fields, required columns, visual contract.

### `mcp__editaplot__validate_template(name, data)`

A "paper simulation" before `render`: checks that the data columns match the template contract, column names align, missing fields are reported.

### `mcp__editaplot__render_chart(input)`

**The core tool**. Parameters:

| field | type | description |
|---|---|---|
| `template` | string | template name, e.g. `xps`, `cv`, `bland_altman` |
| `data` | string \| object | data file path (JSON/CSV/OPJU) or inline data |
| `evidence_role` | enum: `main` / `support` / `verify` | semantic role of the rendered output |
| `output_dir` | string | where to land artifacts |

Returns:

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

On failure:

```json
{
  "ok": false,
  "code": "EDITAPLOT_NOT_FOUND",
  "message": "Origin COM Automation Server not available. Check whether Origin is installed and Automation Server is enabled.",
  "remediation": "Tools → System Variables → check Automation Server"
}
```

### `mcp__editaplot__export(opju, formats)`

Re-export an already-rendered `.opju` to other formats without re-running the template.

## Recommended agent workflow

```text
1. compatibility()                            ← mandatory
2. list_templates() / describe_template(x)    ← pick
3. validate_template(x, data)                ← paper run
4. render_chart({template, data, output})    ← actual render
5. export(opju, formats)                     ← optional, format change
```

System prompt should tell the agent: **no step 4 without step 1**.

## Project layout

```
editaplot-dsh/
├── package.json                    # npm manifest, declares dsh.bundle.patch
├── cordis.patch.yml                # DSH bundle patch (two rows: mcp + skill)
├── editaplot_mcp_server.py         # stdio MCP server (6 tools)
├── pnpm-workspace.yaml             # workspace config DSH expects
├── skills/
│   └── editaplot/
│       └── SKILL.md                # DSH-format skill doc
├── scripts/
│   ├── build-bundle.mjs            # `prepare` hook, writes lib/index.js
│   └── push-with-pat.ps1           # GitHub push helper
├── tests/
│   └── plugin-install.spec.ts      # vitest smoke
├── docs/
│   ├── PAT-申请指南.md             # GitHub PAT instructions
│   ├── SMOKE-TEST.md               # real-machine smoke checklist
│   ├── SMOKE-RESULTS.md            # template: record smoke output
│   └── TROUBLESHOOTING.md          # common problems
├── LICENSE                         # Apache-2.0 full text
├── NOTICE                          # upstream attribution + derivation notes
├── CHANGELOG.md
└── CONTRIBUTING.md
```

## Upstream provenance

- Original: <https://github.com/hang-jin/editaplot>
- Upstream LICENSE: Apache-2.0 (<https://www.apache.org/licenses/LICENSE-2.0>)
- Derivative LICENSE: see `LICENSE` here, copyright `2026 editaplot-dsh contributors`
- Upstream NOTICE content is preserved verbatim

This project does **not** modify, repackage, or redistribute the `originpro` Python package or any OriginLab binary. Origin is a registered trademark of OriginLab Corporation; this project has no official affiliation.

## Develop and test

```bash
git clone https://github.com/caob23/editaplot-dsh.git
cd editaplot-dsh
npm install
npm run prepare
npx vitest run tests/
```

Five smoke checks:

1. `package.json` declares `dsh.bundle.patch`
2. `LICENSE` and `NOTICE` are Apache-2.0 and reference upstream
3. `cordis.patch.yml` has the `mcp-editaplot` row with `transport: stdio` and `failOnStartupError: false`
4. `skills/editaplot/SKILL.md` references `mcp__editaplot__compatibility`
5. `editaplot_mcp_server.py` pins `originpro==1.1.15`

## Troubleshooting

Start with [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md). Common:

| Symptom | Section |
|---|---|
| No `mcp__editaplot__*` tools after DSH boots | "MCP server does not respond" |
| Render fails `EDITAPLOT_NOT_FOUND` | "Origin compatibility failure" |
| 2025b visuals differ from 2024b | "2025b renders but visuals differ" |
| `schannel` error pushing to GitHub | "push fails" |

## Roadmap

- [ ] Real-machine smoke test (full 2024b / 2025b runs)
- [ ] Squash the 18 commits into 1 (optional)
- [ ] Upstream PR to `hang-jin/editaplot` adding the six CLI subcommands (`compat check`, `templates list`, etc.)
- [ ] Post-2026b SR1 compatibility pass
- [ ] Submit to the awesome-dsh-plugin list

## License

Apache-2.0 — see [LICENSE](LICENSE) and [NOTICE](NOTICE).