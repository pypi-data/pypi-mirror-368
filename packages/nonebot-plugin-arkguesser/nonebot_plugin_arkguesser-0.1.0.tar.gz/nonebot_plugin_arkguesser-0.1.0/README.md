<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://github.com/A-kirami/nonebot-plugin-template/blob/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-arkguesser

_✨ 明日方舟猜干员游戏 - 支持多种游戏模式和题库设置 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/lizhiqi233-rgb/nonebot-plugin-arkguesser.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-arkguesser">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-arkguesser.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="python">

</div>

## 📖 介绍

这是一个基于 NoneBot2 的明日方舟猜干员游戏插件，支持多种游戏模式和题库设置，为群聊和私聊提供有趣的游戏体验。

### 🎮 游戏特色
- **多种星级范围题库**：支持1-6星干员的不同组合
- **大头模式**：适合正常游戏体验，显示干员头像
- **兔头模式**：增加游戏趣味性，显示可爱的兔头头像
- **连战模式**：猜对后自动开始下一轮，享受连续游戏乐趣
- **智能题库管理**：支持群组和个人设置，优先级明确

## 💿 安装

<details open>
<summary>使用 nb-cli 安装</summary>
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装

    nb plugin install nonebot-plugin-arkguesser

</details>

<details>
<summary>使用包管理器安装</summary>
在 nonebot2 项目的插件目录下, 打开命令行, 根据你使用的包管理器, 输入相应的安装命令

<details>
<summary>pip</summary>

    pip install nonebot-plugin-arkguesser
</details>
<details>
<summary>pdm</summary>

    pdm add nonebot-plugin-arkguesser
</details>
<details>
<summary>poetry</summary>

    poetry add nonebot-plugin-arkguesser
</details>
<details>
<summary>conda</summary>

    conda install nonebot-plugin-arkguesser
</details>

打开 nonebot2 项目根目录下的 `pyproject.toml` 文件, 在 `[tool.nonebot]` 部分追加写入

    plugins = ["nonebot_plugin_arkguesser"]

</details>

## ⚙️ 配置

在 nonebot2 项目的`.env`文件中添加下表中的配置项

| 配置项 | 必填 | 默认值 | 说明 |
|:-----:|:----:|:----:|:----:|
| `arkguesser_max_attempts` | 否 | 10 | 最大尝试次数 |
| `arkguesser_default_rarity_range` | 否 | "6" | 默认星级范围 |
| `arkguesser_default_mode` | 否 | "大头" | 默认游戏模式 |

## 🎉 使用

### 指令表
| 指令 | 权限 | 需要@ | 范围 | 说明 |
|:-----:|:----:|:----:|:----:|:----:|
| `arkstart` | 群员 | 否 | 群聊/私聊 | 开始游戏 |
| `结束` | 群员 | 否 | 群聊/私聊 | 结束游戏 |
| 直接输入干员名 | 群员 | 否 | 群聊/私聊 | 开始猜测 |

### 🎮 游戏指令详解

#### 基础游戏
- `arkstart` - 开始游戏
- `结束` - 结束游戏
- 直接输入干员名即可开始猜测

#### 📚 题库设置
- `/arkstart 题库` - 查看题库设置和使用方法
- `/arkstart 题库 6` - 设置题库为6星干员
- `/arkstart 题库 4-6` - 设置题库为4-6星干员
- `/arkstart 题库 查看` - 查看当前题库设置
- `/arkstart 题库 重置` - 重置为默认设置

#### 🎭 模式设置
- `/arkstart 模式` - 查看模式设置和使用方法
- `/arkstart 模式 大头` - 设置为大头模式
- `/arkstart 模式 兔头` - 设置为兔头模式
- `/arkstart 模式 查看` - 查看当前模式设置
- `/arkstart 模式 重置` - 重置为默认模式

#### 🔄 连战模式设置
- `/arkstart 连战` - 查看连战模式设置和使用方法
- `/arkstart 连战 开启` - 开启连战模式
- `/arkstart 连战 关闭` - 关闭连战模式
- `/arkstart 连战 查看` - 查看当前连战模式设置
- `/arkstart 连战 重置` - 重置为默认连战模式设置

### ⚙️ 群组配置说明
- **群聊设置**：对所有群成员生效
- **个人设置**：只在私聊中生效  
- **优先级**：群聊设置 > 个人设置 > 默认设置

### 💡 使用技巧
1. **题库选择**：根据群组水平选择合适的星级范围
2. **模式切换**：大头模式适合正常游戏，兔头模式增加趣味性
3. **连战模式**：适合活跃的群聊，保持游戏连续性
4. **个人设置**：私聊中可以设置个人偏好，不影响群聊

## 🚀 特性

- ✅ 支持多种星级范围题库（1-6星）
- ✅ 大头模式和兔头模式切换
- ✅ 连战模式自动下一轮
- ✅ 群组和个人设置分离
- ✅ 智能优先级管理
- ✅ 完整的指令系统
- ✅ 美观的游戏界面

## 📝 更新日志

### v0.1.0
- 🎉 初始版本发布
- 🎮 基础猜干员游戏功能
- 🎭 大头和兔头模式
- 🔄 连战模式支持
- ⚙️ 题库和模式设置
- 👥 群组和个人配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

本项目采用 [MIT](./LICENSE) 许可证。

## 🙏 致谢

- [NoneBot2](https://github.com/nonebot/nonebot2) - 优秀的机器人框架
- [nonebot-plugin-alconna](https://github.com/ArcletProject/nonebot-plugin-alconna) - 强大的指令解析器
- [nonebot-plugin-htmlrender](https://github.com/kexue-z/nonebot-plugin-htmlrender) - 美观的渲染器
