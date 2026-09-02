# Contributing

Thank you for helping improve editaplot-dsh.

## Provenance and license

editaplot-dsh is an Apache-2.0 derivative of hang-jin/editaplot. Upstream
copyright is preserved in NOTICE. By submitting a contribution you agree
to license your work under Apache-2.0 (the same terms).

## Before opening a pull request

1. Open an issue first when introducing a new MCP tool, a new Origin
   template wrapper, or a change to `cordis.patch.yml`.
2. Keep `cordis.patch.yml` lean. If a row is not strictly required to
   ship EditaPlot to DSH, leave it out.
3. Test on Windows 11 + Origin 2025b. Fill in `docs/SMOKE-RESULTS.md`.
4. Never modify the upstream `hang-jin/editaplot` runtime, the
   `originpro` Python package version, or Origin itself.
5. Never cite reference images, journal covers, or OriginLab artwork.

## Code style

- TypeScript: project-inherited config. Run `pnpm lint` before pushing.
- Python: keep `editaplot_mcp_server.py` self-contained — no implicit
  imports outside the standard library plus `mcp`.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/).

Examples:

```
feat(mcp): add validate_template tool
fix(patch): resolve path anchoring to profile node_modules
docs(readme): note Origin 2025b default
```