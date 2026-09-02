# Changelog

All notable changes to editaplot-dsh are recorded here.

## Unreleased — initial scaffold

The first public drop is a derivative of `hang-jin/editaplot` exposing the
upstream CLI as six MCP tools inside a DSH profile bundle:

- `mcp-editaplot` host row registered through `cordis.patch.yml`
- `editaplot_mcp_server.py` stdio MCP server with six tools:
  `compatibility`, `list_templates`, `describe_template`,
  `validate_template`, `render_chart`, `export`
- `skills/editaplot/SKILL.md` published into the harness skill directory
- Apache-2.0 LICENSE and NOTICE preserved verbatim from upstream
- `originpro==1.1.15` version pin inherited from upstream
- Default `EDITAPLOT_VERSION_TARGET=2025b`, verified baseline `2024b`

**This scaffold has not been validated on a live Origin installation.**
Run `docs/SMOKE-TEST.md` end-to-end before publishing a release.