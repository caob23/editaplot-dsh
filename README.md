# editaplot-dsh

DeepSeek Harness (DSH) adapter for [hang-jin/editaplot](https://github.com/hang-jin/editaplot).
This is a derivative work of hang-jin/editaplot, distributed under Apache-2.0.

`editaplot-dsh` exposes the upstream EditaPlot runtime as native MCP tools
(`mcp__editaplot__*`) inside a DSH profile, so a DSH-hosted AI session can
read a local CSV, recommend a publication-informed chart, and produce
editable OPJU + PNG/PDF/TIF outputs through a locally installed
Origin/OriginPro 2021–2026b instance.

This plugin is **independent** of OriginLab Corporation. Origin and
OriginPro are trademarks of OriginLab Corporation; their names appear
here only to describe compatibility.

## What this package does

| Layer | Role |
|---|---|
| `cordis.patch.yml` | Inserts an `mcp-editaplot` row into the host DSH patch stack and publishes `skills/editaplot/SKILL.md` into the harness skill directory. |
| `editaplot_mcp_server.py` | stdio MCP server. Translates MCP tool calls into upstream EditaPlot CLI invocations and returns JSON. |
| `skills/editaplot/SKILL.md` | The model-side prompt that explains the workflow, environment expectations, and forbidden behaviours. |
| `LICENSE` / `NOTICE` | Apache-2.0 + the upstream NOTICE verbatim. |

The plugin does **not** modify the upstream EditaPlot runtime, the
`originpro` Python package, or Origin itself.

## Compatibility

| Origin | Status |
|---|---|
| 2024b (10.15) | Fully verified upstream baseline |
| 2021 / 2021b / 2022 / 2022b / 2023 / 2023b / 2024 | Compatibility target — capability-gated |
| 2025 / 2025b | Compatibility target (default) — note that 2025b changed graph defaults |
| 2026 / 2026b | Compatibility target — SR1 readback bug fixed upstream 2026-08-09 |
| 2020b and earlier | Not supported by the upstream `originpro` route |

Always call `mcp__editaplot__compatibility()` first and surface the result
to the user.

## Installation (private fork)

```sh
dsh plugin --profile web add github:caob23/editaplot-dsh
```

The plugin is a pure addition — it never overwrites DSH core configuration
and `failOnStartupError: false` keeps the DSH process bootable when
Origin/OriginPro is not installed.

## Provenance and licensing

This project is a derivative of hang-jin/editaplot. Upstream copyright is
preserved; see `LICENSE` and `NOTICE`.

```
EditaPlot
Copyright 2026 EditaPlot contributors

This product includes software developed by the EditaPlot contributors and distributed under the
Apache License, Version 2.0.
```

## Provenance modifications

- All changes are clearly marked `// editaplot-dsh: …` in the affected
  files. The original file headers are preserved.
- The MCP wrapper layer is original work under Apache-2.0.
- The bundled `SKILL.md` adds an MCP tool surface section while keeping
  the upstream prohibition list intact.

## License

Apache-2.0. See `LICENSE` for the full text.