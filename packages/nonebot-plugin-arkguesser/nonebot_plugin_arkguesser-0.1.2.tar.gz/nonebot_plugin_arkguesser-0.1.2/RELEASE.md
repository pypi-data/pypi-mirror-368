# 发布说明

## 发布到GitHub

1. 提交所有更改：
   ```bash
   git add .
   git commit -m "Release v0.1.2"
   git tag v0.1.2
   git push origin main
   git push origin v0.1.2
   ```

2. 在GitHub上创建Release，包含：
   - 版本标签：v0.1.2
   - 发布标题：v0.1.2 - 明日方舟猜干员游戏插件
   - 发布说明：从CHANGELOG.md复制

## 发布到PyPI

1. 构建分发包：
   ```bash
   python -m build
   ```

2. 上传到PyPI：
   ```bash
   python -m twine upload dist/*
   ```

## 验证发布

1. 检查PyPI页面：https://pypi.org/project/nonebot-plugin-arkguesser/
2. 测试安装：`pip install nonebot-plugin-arkguesser==0.1.2`
3. 验证功能正常

## 注意事项

- 确保所有依赖版本兼容
- 测试插件在NoneBot2环境中的加载
- 验证资源文件正确打包
