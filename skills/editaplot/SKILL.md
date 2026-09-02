---
name: editaplot
description: Analyze local scientific CSV, TXT, XLS, or XLSX data; recommend publication-informed charts and Chinese scientific palettes; freeze a reproducible plan; and automate editable figures through a callable local Origin/OriginPro installation on physical Windows 10/11 x64. Use for beginner "drop in a file and draw it" requests; XPS, XRD, XAS, PL/TRPL, DSC, NMR, FTIR/IR, UV-Vis, electrochemistry, medical/AI evidence, distribution, relationship, error-bar, bar, stacked, pie, Sankey, radar, heatmap, or verified 3D workflows; project-local Python setup; palette selection; and OPJU/PNG/PDF/TIF verification. Do not use on macOS, Linux, WSL, Wine/CrossOver, Parallels, or other VMs; to install or modify Origin; to redistribute reference images; or to claim an unverified Origin route.
---

# EditaPlot via DSH (editaplot-dsh)

This skill is the DSH adapter for hang-jin/editaplot. The DSH plugin
`@editaplot-dsh` ships it alongside an MCP bridge that exposes six tools:

- `mcp__editaplot__compatibility()` — probe the local Origin/OriginPro
- `mcp__editaplot__list_templates()` — enumerate the 30+ templates
- `mcp__editaplot__describe_template(name)` — read the data contract
- `mcp__editaplot__validate_template(name, data)` — dry-run before rendering
- `mcp__editaplot__render_chart(input)` — produce OPJU + PNG/PDF/TIF
- `mcp__editaplot__export(opju, formats)` — re-export an OPJU

## Environment expectations (inherited from hang-jin/editaplot)

- Physical Windows 10/11 x64 with CPython 3.10–3.12
- Origin/OriginPro installed locally; the compatibility target is the
  **2021–2026b** matrix. Origin 2020b and earlier are explicitly
  unsupported.
- The fully verified live baseline is **Origin 2024b / 10.15**. This
  plugin's default `EDITAPLOT_VERSION_TARGET` is `2025b`; smoke results
  may report `compatible_unverified` for non-baseline hosts and the
  model must not relabel them as verified.
- The bridge calls `originpro==1.1.15` (BSD, OriginLab) for Automation.
  Do not attempt to install or modify Origin itself.

## Required workflow (never shortcut)

1. Call `mcp__editaplot__compatibility()` and surface the report to the
   user. If the status is `blocked`, stop and ask the user to fix the
   Origin installation. If `compatible_unverified`, continue but flag the
   template-by-template acceptance file path so the user can audit.
2. Read the user's data shape. List the columns and propose a role for
   each (main / support / verify / unused). Never guess on unknown
   columns — ask.
3. Propose the recommended chart and the rationale. Show the
   per-column usage table. Wait for the user's confirmation of the
   scientific purpose and the element list.
4. Call `mcp__editaplot__describe_template(template)` and
   `mcp__editaplot__validate_template(template, data)`. Surface any
   contract mismatch to the user before proceeding.
5. Call `mcp__editaplot__render_chart({template, data, output_dir,
   evidence_role})`. Show the resulting OPJU + PNG/PDF/TIF paths.
6. Verify each artifact: OPJU opens, PNG/PDF/TIF match, axes legible,
   legend unambiguous, no overlapping labels, color print-readable.

## Forbidden behaviours

- Installing or modifying Origin/OriginPro, the upstream `originpro`
  package version, or any DSH settings the user has not authorized.
- Citing reference images, journal covers, or OriginLab artwork.
- Claiming journal endorsement, fabricated measurements, or hidden
  normalization.
- Renaming this skill or claiming authorship over hang-jin/editaplot.

## Provenance

This file is auto-published by the editaplot-dsh DSH bundle on startup.
It bundles the upstream `hang-jin/editaplot` SKILL.md verbatim and adds
the MCP tool surface. Both works are licensed under Apache-2.0; see
LICENSE and NOTICE in the upstream repository for attribution.