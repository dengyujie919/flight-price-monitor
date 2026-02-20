# 项目清理计划

## 📋 可以安全删除的文件/目录

### 1. IDE配置目录 ⚠️
**目录**: `.vscode/`
- **原因**: VSCode的IDE配置，属于个人开发环境
- **状态**: 已在.gitignore中
- **建议**: 删除或保留（不影响项目）
```bash
# 删除命令
rm -rf .vscode/
```

### 2. Playwright目录 ✅
**目录**: `playwright/`
- **原因**: 空目录，似乎未使用
- **状态**: 未被Git跟踪
- **建议**: 可以安全删除
```bash
# 删除命令
rm -rf playwright/
```

### 3. Logs目录的.gitkeep 🔄
**文件**: `logs/.gitkeep`
- **原因**: logs目录已在.gitignore中，不需要.gitkeep
- **状态**: 未被Git跟踪
- **建议**: 删除.logs/.gitkeep（logs目录会在需要时自动创建）
```bash
# 删除命令
rm -f logs/.gitkeep
```

## ✅ 需要保留的重要文件

- ✅ `.env` - API密钥配置（已在.gitignore）
- ✅ `.gitignore` - Git忽略规则
- ✅ `config.py` - 项目配置
- ✅ `run.py` - 主运行脚本
- ✅ `scheduler.py` - 调度器
- ✅ `src/` - 源代码目录
- ✅ `docs/` - 文档目录
- ✅ `README.md` - 项目说明

## 🚀 推荐清理步骤

### 选项1：自动清理（推荐）
```bash
cd "c:\Users\13032\WPSDrive\1732170715\WPS企业云盘\清华大学\我的企业文档\predict"

# 删除不必要文件
rm -rf playwright/
rm -f logs/.gitkeep
```

### 选项2：保守清理
```bash
# 仅删除空目录
rm -rf playwright/
# 保留.vscode/（个人IDE配置）
# 保留logs/.gitkeep
```

## 📊 清理前后对比

**清理前**:
```
predict/
├── .vscode/          ← IDE配置
├── playwright/       ← 空目录
├── logs/.gitkeep     ← 不需要
└── ...其他重要文件
```

**清理后**:
```
predict/
├── src/              ← 源代码
├── docs/             ← 文档
├── config.py         ← 配置
├── run.py            ← 运行脚本
├── scheduler.py      ← 调度器
└── ...其他重要文件
```

## ⚠️ 注意事项

1. **不要删除以下**:
   - `.env` - 包含API密钥
   - `data/` - 包含数据文件
   - `models/` - 包含训练好的模型
   - `outputs/` - 包含分析结果

2. **Git状态**:
   - 以上文件都不在Git跟踪中
   - 删除它们不会影响Git仓库

3. **建议**:
   - 定期清理临时文件
   - 保持.gitignore更新
   - 使用`git status`检查状态

## 🔧 自动清理脚本

创建 `cleanup.sh` (Linux/Mac) 或 `cleanup.bat` (Windows):

**cleanup.bat**:
```batch
@echo off
echo 开始清理项目...
echo.

echo 删除playwright目录...
if exist playwright rmdir /s /q playwright

echo 删除logs/.gitkeep...
if exist logs\.gitkeep del /q logs\.gitkeep

echo.
echo 清理完成！
pause
```

使用方法:
```bash
cleanup.bat
```
