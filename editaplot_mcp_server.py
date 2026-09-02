#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
editaplot-dsh MCP server — exposes hang-jin/editaplot as MCP tools to DSH.

This is a derivative work of hang-jin/editaplot (Apache License 2.0) adapted
to the Model Context Protocol (MCP). It does not modify the upstream EditaPlot
runtime; it shells out to the upstream `editaplot.cmd` (Windows) or
`editaplot` CLI and translates the arguments/results into MCP tool shapes.

Tool surface (the model sees these as mcp__editaplot__*):

    compatibility()           — probe local Origin/OriginPro, return status
    list_templates()          — enumerate the 30+ verified templates
    describe_template(name)    — return the template's contract (input/output)
    render_chart(input)       — invoke editaplot, return OPJU/PNG/PDF/TIF paths
    export(input)             — re-export an existing OPJU to PNG/PDF/TIF
    validate_template(name, data) — dry-run a template against sample data

The server only calls a locally installed EditaPlot (via the upstream CLI) and
never installs or modifies Origin/OriginPro itself. When Origin is missing,
every tool returns a structured error so the model can fall back gracefully.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

# MCP is the same dependency dsh-origin-plugin relies on.
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import ImageContent, TextContent, Tool
except ImportError as exc:  # pragma: no cover - the launcher surfaces this
    sys.stderr.write(
        "[editaplot-dsh] Python dependency `mcp` not found. "
        "Install with: pip install mcp>=1.0.0\n"
    )
    raise

SERVER_NAME = "editaplot"
VERSION_TARGET = os.environ.get("EDITAPLOT_VERSION_TARGET", "2025b")
VERIFIED_BASELINE = os.environ.get("EDITAPLOT_VERIFIED_BASELINE", "2024b")

# On Windows the upstream ships editaplot.cmd; on POSIX the install matrix
# does not yet support Origin automation (per upstream SKILL.md line 22).
IS_WINDOWS = sys.platform == "win32"
CLI_BASENAME = "editaplot.cmd" if IS_WINDOWS else "editaplot"


def _cli_path() -> str:
    """Locate the upstream editaplot CLI inside the same install tree.

    The DSH plugin manager installs editaplot-dsh under
    <DSH_HOME>/profiles/<profile>/node_modules/editaplot-dsh/. The upstream
    editaplot package is a sibling (peerDep), so its CLI sits at
    node_modules/editaplot/editaplot.cmd. PATH may also carry it.
    """
    here = Path(__file__).resolve().parent
    sibling = here.parent / "editaplot" / CLI_BASENAME
    if sibling.exists():
        return str(sibling)
    from shutil import which

    found = which(CLI_BASENAME.rstrip(".cmd"))
    return found or str(sibling)


def _run_cli(args: list[str], timeout: int = 60) -> dict[str, Any]:
    """Invoke the upstream CLI and capture a structured result."""
    cmd = [_cli_path(), *args, "--output-format", "json"]
    try:
        completed = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError:
        return {
            "ok": False,
            "code": "EDITAPLOT_NOT_FOUND",
            "message": f"Could not locate upstream EditaPlot CLI at {_cli_path()}",
        }
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "code": "EDITAPLOT_TIMEOUT",
            "message": f"EditaPlot CLI exceeded {timeout}s timeout",
        }

    if completed.returncode != 0:
        return {
            "ok": False,
            "code": "EDITAPLOT_NONZERO_EXIT",
            "message": completed.stderr.strip() or completed.stdout.strip(),
            "exit_code": completed.returncode,
        }

    try:
        return {"ok": True, "data": json.loads(completed.stdout)}
    except json.JSONDecodeError:
        return {"ok": True, "data": {"raw": completed.stdout}}


server = Server(SERVER_NAME)


@server.list_tools()
async def list_tools() -> list[Tool]:
    """The tools the DSH model will see as mcp__editaplot__*."""
    return [
        Tool(
            name="compatibility",
            description=(
                "Probe the local Origin/OriginPro installation and return a "
                "structured compatibility report (verified | "
                "compatible_unverified | blocked). The fully verified "
                f"baseline is Origin/OriginPro {VERIFIED_BASELINE}. This "
                f"plugin targets the {VERSION_TARGET} range; 2021+ is in scope."
            ),
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        Tool(
            name="list_templates",
            description=(
                "List the 30+ EditaPlot scientific chart templates (bar, "
                "bland_altman, bubble, calibration_curve, circular_network, "
                "confusion_matrix, cv, decision_curve, density_ridgeline3d, "
                "diagnostic_curve, dsc, eis, forest, ftir, grouped_box, "
                "heatmap, histogram, horizontal_bar, line_error, lsv, nmr, "
                "paired_trajectory, percent_stacked_bar, radar, sankey, "
                "scatter_matrix, stacked_bar, subplot_grid, trajectory3d, "
                "violin, xps, xrd, ...). Each entry includes the verified "
                "Origin version it was tested on."
            ),
            inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
        ),
        Tool(
            name="describe_template",
            description=(
                "Return the data contract and origin_acceptance notes for a "
                "single template. The model should call this BEFORE "
                "render_chart so it knows the required columns and the "
                "experimental claims the template supports."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Template name."}
                },
                "required": ["name"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="render_chart",
            description=(
                "Render a chart through EditaPlot and return the produced "
                "OPJU/PNG/PDF/TIF file paths plus an object-readback summary. "
                "The model must have called describe_template first and the "
                "user must have approved the scientific purpose."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "template": {"type": "string"},
                    "data": {"type": "string", "description": "Path to CSV/XLSX input."},
                    "evidence_role": {
                        "type": "string",
                        "enum": ["main", "support", "verify"],
                    },
                    "output_dir": {"type": "string"},
                },
                "required": ["template", "data"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="validate_template",
            description=(
                "Dry-run a template against sample data without producing any "
                "OPJU. Returns the same per-column contract checks the live "
                "route performs, so the model can confirm the data shape "
                "before committing to a render."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "data": {"type": "string"},
                },
                "required": ["name", "data"],
                "additionalProperties": False,
            },
        ),
        Tool(
            name="export",
            description=(
                "Re-export an existing editable OPJU to PNG/PDF/TIF. Useful "
                "when the user edits the OPJU manually and wants updated "
                "raster exports without re-running the whole pipeline."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "opju": {"type": "string"},
                    "formats": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["png", "pdf", "tif"]},
                    },
                },
                "required": ["opju"],
                "additionalProperties": False,
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Dispatch an MCP tool call to the upstream EditaPlot CLI."""
    if name == "compatibility":
        result = _run_cli(["compat", "check"])
    elif name == "list_templates":
        result = _run_cli(["templates", "list"])
    elif name == "describe_template":
        tpl = arguments.get("name", "")
        result = _run_cli(["templates", "describe", tpl])
    elif name == "render_chart":
        args = ["render"]
        if arguments.get("template"):
            args += ["--template", arguments["template"]]
        if arguments.get("data"):
            args += ["--data", arguments["data"]]
        if arguments.get("output_dir"):
            args += ["--output-dir", arguments["output_dir"]]
        if arguments.get("evidence_role"):
            args += ["--evidence-role", arguments["evidence_role"]]
        result = _run_cli(args, timeout=180)
    elif name == "validate_template":
        result = _run_cli(
            ["templates", "validate", arguments["name"], arguments["data"]],
            timeout=60,
        )
    elif name == "export":
        formats = ",".join(arguments.get("formats") or ["png", "pdf", "tif"])
        result = _run_cli(["export", arguments["opju"], "--formats", formats])
    else:
        return [TextContent(type="text", text=json.dumps({
            "ok": False,
            "code": "UNKNOWN_TOOL",
            "message": f"Tool {name} is not registered on editaplot-dsh",
        }))]

    return [TextContent(type="text", text=json.dumps(result, indent=2))]


async def main() -> None:
    """Run the MCP server over stdio (the transport declared in cordis.patch.yml)."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())