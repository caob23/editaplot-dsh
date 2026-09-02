#!/usr/bin/env node
/**
 * editaplot-dsh prepare hook — emits a built `lib/` for DSH's host loader and
 * makes sure the MCP server script is executable on POSIX hosts. The DSH
 * host loader resolves `package.json#exports["."]` to `lib/index.js`, so
 * even an empty entry stub keeps the installable contract intact.
 *
 * Mirrors the precedent set by @deepseek-ai/dsh-base/lib/index.js.
 */
import { mkdirSync, writeFileSync, chmodSync, existsSync } from 'node:fs'
import { resolve } from 'node:path'

const root = resolve(new URL('..', import.meta.url).pathname)
const libDir = resolve(root, 'lib')

if (!existsSync(libDir)) mkdirSync(libDir, { recursive: true })

// lib/index.js — empty CommonJS module so DSH's host loader can import it.
writeFileSync(
  resolve(libDir, 'index.js'),
  '// editaplot-dsh: host-runtime entry point.\n' +
  '// The substantive work runs in the bundled MCP server (editaplot_mcp_server.py)\n' +
  '// which the cordis.patch.yml row launches as a stdio subprocess.\n' +
  'export {}\n'
)

// lib/index.d.ts — typed export surface.
writeFileSync(
  resolve(libDir, 'index.d.ts'),
  '// editaplot-dsh: host-runtime types.\n' +
  'export type EditaplotDshPackage = {\n' +
  '  readonly name: "editaplot-dsh"\n' +
  '  readonly version: string\n' +
  '  readonly upstream: "hang-jin/editaplot@Apache-2.0"\n' +
  '}\n' +
  'export const EDITAPLOT_DSH: EditaplotDshPackage = {\n' +
  '  name: "editaplot-dsh",\n' +
  '  version: "0.1.0",\n' +
  '  upstream: "hang-jin/editaplot@Apache-2.0",\n' +
  '}\n'
)

// Make the Python server executable on POSIX hosts.
const py = resolve(root, 'editaplot_mcp_server.py')
if (existsSync(py)) {
  try { chmodSync(py, 0o755) } catch { /* Windows ignores this */ }
}

console.log('editaplot-dsh: built lib/index.js + lib/index.d.ts')