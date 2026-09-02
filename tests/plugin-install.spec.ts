/**
 * editaplot-dsh smoke tests — the minimum that the DSH host loader and the
 * MCP server agree on. Runs without a live Origin installation so it can
 * execute in CI on any Windows / macOS / Linux agent.
 *
 * Usage:
 *   pnpm install
 *   pnpm dlx vitest run tests/plugin-install.spec.ts
 */
import { describe, it, expect } from 'vitest'
import { readFileSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'

const root = resolve(new URL('..', import.meta.url).pathname)

describe('editaplot-dsh bundle surface', () => {
  it('declares a dsh.bundle patch and points it at cordis.patch.yml', () => {
    const pkg = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'))
    expect(pkg.dsh?.bundle?.patch).toBe('./cordis.patch.yml')
  })

  it('preserves Apache-2.0 and ships an attribution NOTICE', () => {
    const pkg = JSON.parse(readFileSync(resolve(root, 'package.json'), 'utf8'))
    expect(pkg.license).toBe('Apache-2.0')
    expect(existsSync(resolve(root, 'NOTICE'))).toBe(true)
    expect(existsSync(resolve(root, 'LICENSE'))).toBe(true)
    const notice = readFileSync(resolve(root, 'NOTICE'), 'utf8')
    expect(notice).toMatch(/hang-jin\/editaplot/)
  })

  it('exposes an MCP row with stdio transport and failOnStartupError: false', () => {
    const patch = readFileSync(resolve(root, 'cordis.patch.yml'), 'utf8')
    expect(patch).toMatch(/id:\s*mcp-editaplot/)
    expect(patch).toMatch(/transport:\s*stdio/)
    expect(patch).toMatch(/failOnStartupError:\s*false/)
  })

  it('publishes the SKILL.md so DSH auto-loads it on startup', () => {
    const skill = readFileSync(resolve(root, 'skills/editaplot/SKILL.md'), 'utf8')
    expect(skill).toMatch(/name:\s*editaplot/)
    expect(skill).toMatch(/mcp__editaplot__compatibility/)
  })

  it('pins the upstream originpro version to 1.1.15', () => {
    const py = readFileSync(resolve(root, 'editaplot_mcp_server.py'), 'utf8')
    expect(py).toMatch(/originpro==1\.1\.15/)
  })
})