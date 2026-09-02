# Troubleshooting — editaplot-dsh 常见问题

## push 失败

### `403 Permission denied`

- **原因**：token 勾了错 scope，或者勾了错账号
- **修法（fine-grained）**：重新生成时 **Repository access** 选 `Only select repositories` → `caob23/editaplot-dsh`；**Permissions → Repository permissions → Contents** 勾 `Read and write`
- **修法（classic）**：勾 `public_repo`

### `404 Not Found`

- **原因**：仓库没创建、owner 拼错、或 token 没勾对该 repo
- **修法**：浏览器打开 `https://github.com/caob23/editaplot-dsh` 确认仓库存在；fine-grained token 重新选 repo

### `fatal: refusing to merge unrelated histories`

- **原因**：远端已经有 README / LICENSE 等文件，跟你本地的根目录不共享历史
- **修法**：脚本默认走 `--force-with-lease`。如果还失败，浏览器去仓库 Settings → "Allow auto-merge" 关掉，或者手动 `git pull --rebase origin main` 后再 push

### `fatal: could not read Username for 'https://github.com'`

- **原因**：脚本没拿到 PAT，git 退回到交互式认证
- **修法**：确认 `$env:GH_TOKEN` 已设，或者重跑时粘贴 PAT

---

## bundle 装载失败

### `cordis.patch.yml` 解析失败：YAML / `!!js` 报错

`!!js` 块必须是一个**会返回字符串的箭头函数或普通函数表达式**，例如：

```yaml
command: !!js |
  (() => {
    const path = require('node:path')
    return path.join('a', 'b')
  })()
```

**常见错写法**：

- `(function(){...})()` —— 标准 JS 合法，但 cordis-loader 解析 YAML 时 + JS 时容易出兼容问题，建议统一用箭头函数
- 没 `return` —— 函数返回 `undefined`，loader 拒绝
- 用了 `await` —— 同步表达式，不允许

### `id: mcp-editaplot` 跟别的 plugin 冲突

如果别的 DSH bundle（比如 `dsh-origin-plugin`）也声明了 `mcp-editaplot`，需要把它的 `id` 改名，例如：

```yaml
- id: mcp-editaplot-dsh  # ← 唯一
```

### `failOnStartupError: false` 没生效

DSH Loader 早期版本可能不接受 `false`，需要换成 `"false"` 字符串。

---

## MCP server 不响应

### 进程启动后立即退出

- **原因**：找不到上游 `editaplot.cmd`
- **修法**：上游 `hang-jin/editaplot` 必须装在同一 node_modules 下，即：
  ```
  $DSH_HOME/profiles/web/node_modules/
    editaplot-dsh/          # ← 我们
      editaplot_mcp_server.py
    editaplot/              # ← 上游 peer
      editaplot.cmd
  ```
  没有的话，`pip install editaplot` 或 `pnpm install editaplot` 把它装上

### Python `ModuleNotFoundError: mcp`

- **原因**：MCP server 没装 `mcp` Python 包
- **修法**：在 venv 里 `pip install "mcp>=1.0.0"`

### model 看不到 `mcp__editaplot__*` 工具

- **原因**：DSH Loader 启动了 MCP server 但没把工具注册到模型
- **修法**：检查 `cordis.patch.yml` 里 `serverName: editaplot` 是否跟 MCP server 代码里的 `SERVER_NAME = "editaplot"` 一致

---

## Origin 兼容性失败

### `compat check` 返回 `blocked`

可能原因：
1. Origin 版本 ≤ 2020b —— 不支持，提示用户升级
2. `originpro` Python 包没装 —— `pip install originpro==1.1.15`
3. Origin Automation Server 没开 —— 打开 Origin → Tools → System Variables → 检查

### 2025b 渲染出图但视觉与 2024b 不同

这是上游记录的**已知差异**（OriginLab 自己发过说明）：

> "Origin 2025b changed page geometry, margins, text rendering, axis frame, line width, and tick label rotation"

**不要试图修正**——这是 Origin 自身行为，DSH 插件不应该篡改上游输出。如用户要 2024b 视觉，告诉他们装 2024b baseline。

---

## 推送流程里 token 痕迹残留

- `$env:GH_TOKEN` 在脚本 finally 块会被清
- PowerShell 历史 (`Get-History`) **可能**记录粘贴的字符串——运行后跑 `Clear-History`
- 终端截图、屏幕录制、剪贴板同步工具都可能缓存——**用完立即 revoke**

---

## 仍有问题

把下列内容打包到 issue：

```
1. 操作系统 + Python 版本 + Origin 版本
2. 完整命令 + 完整 stdout/stderr
3. docs/SMOKE-RESULTS.md 当前状态
4. `git rev-parse HEAD` 输出
```