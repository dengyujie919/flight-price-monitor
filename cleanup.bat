@echo off
chcp 65001 >nul
echo ========================================
echo 项目清理脚本
echo ========================================
echo.

echo 将要清理的文件/目录:
echo   1. playwright/ - 空目录
echo   2. logs\.gitkeep - 不需要
echo   3. .vscode/ - IDE配置（可选）
echo.

set /p confirm="确认清理？(y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消清理
    pause
    exit /b 0
)

echo.
echo 开始清理...
echo.

echo [1/3] 删除 playwright 目录...
if exist playwright (
    rmdir /s /q playwright
    echo ✓ playwright 目录已删除
) else (
    echo - playwright 目录不存在
)

echo [2/3] 删除 logs\.gitkeep...
if exist logs\.gitkeep (
    del /q logs\.gitkeep
    echo ✓ logs\.gitkeep 已删除
) else (
    echo - logs\.gitkeep 不存在
)

echo [3/3] .vscode 目录保留（IDE配置）
echo - .vscode 保留

echo.
echo ========================================
echo 清理完成！
echo ========================================
echo.

echo 当前项目文件:
dir /b /a-d

pause
