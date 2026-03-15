# Typora-Del Python 版本

Typora Markdown 冗余图片清理工具 - Python 增强版

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行

```bash
python typora_del_unified.py <path>
```

**或者交互模式：**

```bash
python typora_del_unified.py
```

## ✨ 功能特性

- ✅ 智能路径识别（自动判断文件/目录）
- ✅ 统计预览（处理前显示统计信息）
- ✅ 用户确认（避免误操作）
- ✅ 进度条显示
- ✅ 彩色输出
- ✅ 详细操作报告
- ✅ 持久化日志（保存在 `log/` 目录）

## 📖 使用示例

```bash
# 处理单个文件
python typora_del_unified.py article.md

# 处理整个目录
python typora_del_unified.py ./blog/

# 交互模式
python typora_del_unified.py
```

## 📁 文件说明

- `typora_del_unified.py` - 唯一入口文件
- `utils.py` - 核心工具函数
- `logger.py` - 日志模块
- `requirements.txt` - Python 依赖

## 📝 详细文档

查看项目根目录的 [README.md](../README.md) 获取完整使用说明。
