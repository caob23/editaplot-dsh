# editaplot-dsh push helper — pushes the local repo to github.com/caob23/editaplot-dsh
# using a short-lived Personal Access Token. Reads the token from $env:GH_TOKEN
# or from Read-Host -AsSecureString (input is hidden on screen).
#
# This script intentionally does NOT install/configure anything; it only runs
# git operations. After a successful push, it clears $env:GH_TOKEN.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File scripts\push-with-pat.ps1
#   $env:GH_TOKEN = '<your-token>'; powershell -ExecutionPolicy Bypass -File scripts\push-with-pat.ps1

[CmdletBinding()]
param(
  [string]$Remote = 'https://github.com/caob23/editaplot-dsh.git',
  [string]$Branch = 'main'
)

$ErrorActionPreference = 'Stop'

function Section($text) { Write-Host ''; Write-Host ('==== ' + $text + ' ====') -ForegroundColor Cyan }

# 1. Resolve token
if (-not $env:GH_TOKEN) {
  Section 'GitHub PAT'
  Write-Host '需要一个 Fine-grained PAT (Contents: Read and write) 或 Classic PAT (public_repo).'
  Write-Host '详细步骤见 docs/PAT-申请指南.md'
  Write-Host ''
  $secure = Read-Host 'Paste your GitHub PAT (输入隐藏)' -AsSecureString
  if (-not $secure) { throw '未提供 token，已退出。' }
  $bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
  try {
    $env:GH_TOKEN = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
  } finally {
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
  }
}

if (-not $env:GH_TOKEN) { throw 'GH_TOKEN is empty' }

# 2. Sanity check token format
if ($env:GH_TOKEN -notmatch '^(github_pat_|ghp_|gho_|ghu_|ghs_)[A-Za-z0-9_]+$') {
  throw 'Token 格式不像合法 GitHub PAT，请确认从 https://github.com/settings/tokens 复制'
}

# 3. Author identity
Section 'Commit author'
if (-not (git config --get user.name))  { git config --global user.name  'caob23' }
if (-not (git config --get user.email)) { git config --global user.email 'caob23@users.noreply.github.com' }
git config --get user.name
git config --get user.email

# 4. Confirm working tree is clean
Section 'Working tree'
$status = git status --porcelain
if ($status) {
  Write-Host '工作区有未提交改动：'
  Write-Host $status
  $answer = Read-Host '继续 push 会包含这些改动吗? (yes/no)'
  if ($answer -ne 'yes') { throw '用户中止' }
}

# 5. Build authenticated remote URL (so we never write the token to git config)
$authUrl = $Remote -replace '^https://', ('https://x-access-token:' + $env:GH_TOKEN + '@')

# 6. Ensure branch
Section 'Branch'
$current = git rev-parse --abbrev-ref HEAD
if ($current -ne $Branch) {
  if (git show-ref --verify --quiet "refs/heads/$Branch") {
    git checkout $Branch
  } else {
    git checkout -b $Branch
  }
}

# 7. Push (with --force-with-lease to handle "remote has unrelated histories")
Section 'Push'
try {
  git push --force-with-lease $authUrl $Branch 2>&1
  if ($LASTEXITCODE -ne 0) {
    # Maybe the remote is empty; try a normal push
    Write-Host 'force-with-lease 失败，尝试普通 push...' -ForegroundColor Yellow
    git push $authUrl $Branch 2>&1
  }
} finally {
  # 8. Wipe the token from memory
  $env:GH_TOKEN = $null
  [System.GC]::Collect()
}

Section 'Done'
Write-Host '推送完成。' -ForegroundColor Green
Write-Host '下一步：在 Windows + Origin 2025b 机器上跑 docs/SMOKE-TEST.md 验证。'
Write-Host '完成验证后请立刻去 https://github.com/settings/tokens 撤销此 PAT。'