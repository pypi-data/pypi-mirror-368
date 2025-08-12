# 发布检查清单 v0.1.2

## ✅ 版本更新检查
- [x] pyproject.toml 版本号：0.1.2
- [x] CHANGELOG.md 版本号：0.1.2
- [x] README.md 版本号：v0.1.2

## ✅ 文件清理检查
- [x] 删除 setup.py（已被pyproject.toml替代）
- [x] 删除 Makefile（不是必需的）
- [x] 删除 CONTRIBUTING.md（简化项目结构）
- [x] 删除 .github/ 目录（简化部署）
- [x] 更新 MANIFEST.in（包含pyproject.toml）

## ✅ 核心文件检查
- [x] __init__.py - 插件主文件
- [x] game.py - 游戏核心逻辑
- [x] pool_manager.py - 题库管理
- [x] mode_manager.py - 模式管理
- [x] continuous_manager.py - 连战管理
- [x] render.py - 渲染引擎
- [x] config.py - 配置管理
- [x] resources/ - 资源文件目录

## ✅ 配置文件检查
- [x] pyproject.toml - 项目配置
- [x] requirements.txt - 依赖列表
- [x] MANIFEST.in - 打包配置
- [x] .gitignore - Git忽略文件
- [x] LICENSE - MIT许可证

## ✅ 文档文件检查
- [x] README.md - 项目说明
- [x] CHANGELOG.md - 更新日志
- [x] RELEASE.md - 发布说明
- [x] CHECKLIST.md - 检查清单

## 🚀 发布前最终检查
- [ ] 测试插件加载：`python -c "import nonebot_plugin_arkguesser"`
- [ ] 验证资源文件完整性
- [ ] 检查依赖版本兼容性
- [ ] 确认所有文件编码为UTF-8

## 📦 发布步骤
1. 提交所有更改到Git
2. 创建Git标签 v0.1.2
3. 推送到GitHub
4. 构建分发包：`python -m build`
5. 上传到PyPI：`python -m twine upload dist/*`
6. 在GitHub上创建Release

## 🔍 发布后验证
- [ ] 检查PyPI页面
- [ ] 测试安装：`pip install nonebot-plugin-arkguesser==0.1.2`
- [ ] 验证插件功能正常
- [ ] 更新GitHub Release说明
