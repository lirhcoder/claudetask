# Claude Code Safe Wrapper for Windows
# 防止 Ctrl+Z 导致的崩溃

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

Write-Host "========================================"
Write-Host "Claude Code Safe Mode"
Write-Host "========================================"
Write-Host ""
Write-Host "提示:"
Write-Host "- 使用 Ctrl+C 安全退出"
Write-Host "- 避免使用 Ctrl+Z (会导致程序崩溃)"
Write-Host ""
Write-Host "----------------------------------------"

# 设置控制台处理程序
[Console]::TreatControlCAsInput = $false

# 捕获 Ctrl+Z 并忽略
[Console]::CancelKeyPress += {
    param($sender, $e)
    if ($e.SpecialKey -eq [ConsoleSpecialKey]::ControlZ) {
        Write-Host "`n警告: Ctrl+Z 在 Windows 上不受支持，已忽略"
        $e.Cancel = $true
    }
}

try {
    # 执行 Claude Code
    & claude $Arguments
    $exitCode = $LASTEXITCODE
    
    if ($exitCode -ne 0) {
        Write-Host ""
        Write-Host "Claude Code 退出代码: $exitCode"
    }
} catch {
    Write-Host "错误: $_"
    exit 1
}

exit $exitCode