# 推送 editaplot-dsh 到 GitHub — 完整流程

> 本仓库是 Apache-2.0 衍生作品。先在本地完成 `git init` + 首次 commit，再用下面的步骤推到 `github.com/caob23/editaplot-dsh`。

## 步骤 0：你只需要做一次的事

### 0.1 创建空仓库

1. 打开浏览器，登录 `caob23` 这个 GitHub 账号
2. 访问 `https://github.com/new`
3. 填写：

| 字段 | 值 |
|---|---|
| Owner | `caob23` |
| Repository name | `editaplot-dsh` |
| Description | `DSH adapter for hang-jin/editaplot — AI-guided editable scientific figures through local Origin/OriginPro 2021–2026b` |
| Visibility | Public |
| Initialize this repository with | **全部留空**（不要勾 Add README / .gitignore / license —— 我们本地已经有） |

4. 点 **Create repository**

### 0.2 生成 Personal Access Token (PAT)

1. 打开浏览器，访问：`https://github.com/settings/tokens?type=beta`

   > ⚠️ GitHub 现在默认推 Fine-grained PAT（推荐）。点 "Generate new token" → 选 **Fine-grained token**。
   > 
   > 也可以用 Classic PAT（在 `https://github.com/settings/tokens` 选 "Generate new token (classic)"）。下面给两种写完。

#### Fine-grained（推荐）

| 字段 | 值 |
|---|---|
| Token name | `editaplot-dsh-push-2026` |
| Expiration | **7 days**（用完立刻失效，最安全） |
| Resource owner | `caob23` |
| Repository access | **Only select repositories** → 勾 `editaplot-dsh` |
| Permissions → Repository permissions | **Contents: Read and write** |

   其它都不要勾。点 **Generate token**。

#### Classic（备选）

| 字段 | 值 |
|---|---|
| Note | `editaplot-dsh-push` |
| Expiration | **7 days** |
| Scopes | 勾 `public_repo` |

   其它不要勾。点 **Generate token**。

### 0.3 复制 token

页面跳转后会**一次性显示**完整 token，例如：

```
github_pat_11ABCDEFG0_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**只有这一次能看到**，复制下来保存到本地密码管理器。页面关闭后不能再次查看。

---

## 步骤 1：本地 git init + commit

把仓库内容先 commit 到本地。这步我（DSH agent）会代你做，不需要任何凭据。

---

## 步骤 2：推送（你来做）

打开 **PowerShell**（管理员或普通都行），`cd` 到 `C:\Users\GZX\Desktop\mc\editaplot-dsh`。

**方法 A：交互式推送（最安全）**

```powershell
powershell -ExecutionPolicy Bypass -File scripts\push-with-pat.ps1
```

脚本会：
1. 询问你的 PAT（**输入时隐藏**，不会留在屏幕）
2. 询问 commit 作者邮箱（默认 `caob23@users.noreply.github.com`）
3. 询问 commit 作者名（默认 `caob23`）
4. 推送一次到 `https://github.com/caob23/editaplot-dsh.git`
5. 完成后**立刻清除**控制台历史中可能残留的 PAT 痕迹

**方法 B：一次性粘贴**

```powershell
$env:GH_TOKEN = 'github_pat_你的token'
powershell -ExecutionPolicy Bypass -File scripts\push-with-pat.ps1
Remove-Item Env:GH_TOKEN
```

---

## 步骤 3：用完 token 后立刻 revoke

无论 push 成不成功，**7 天到期**前你都应该去：

`https://github.com/settings/tokens`

把 `editaplot-dsh-push-2026` 这个 token 手动 **Delete**。这样即使代码库/脚本里意外泄露了 PAT，过期+手动撤销让它彻底作废。

---

## 步骤 4：第一次 push 后，把 token 也写进 .gitignore

我们已经在 `.gitignore` 里加了 `*.token` 和 `.gh-token`。脚本运行时也会自动确认本地没有 token 落盘。

---

## 步骤 5：发布到 awesome-dsh-plugin.com（**先不要做**）

等真机 smoke 测试通过后再做。现在发等于给用户挖坑。

---

## 如果 push 失败

最常见的 3 个错误：

| 错误 | 原因 | 修法 |
|---|---|---|
| `403 Permission denied` | Token 选了错 scope 或错账号 | 重新生成勾 `public_repo` (classic) 或 `Contents: Read and write` (fine-grained) |
| `404 Not Found` | 仓库没创建或 owner 拼错 | 去 `https://github.com/caob23/editaplot-dsh` 确认仓库存在 |
| `fatal: refusing to merge unrelated histories` | 远端已有 README 等内容 | 在脚本里我们走 `git push -u origin main --force-with-lease`（已经在脚本里加了确认） |

详细排查见 `docs/TROUBLESHOOTING.md`。