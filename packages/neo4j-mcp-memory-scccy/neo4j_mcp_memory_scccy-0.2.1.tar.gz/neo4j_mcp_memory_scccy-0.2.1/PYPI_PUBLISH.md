# PyPI 打包上传指南

## 环境准备

### 安装必要工具
```bash
# 安装构建工具
pip install build twine

# 或使用uv
uv pip install build twine
```

### 配置PyPI认证
```bash
# 方法1: 创建配置文件 ~/.pypirc
cat > ~/.pypirc << EOF
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = your_pypi_api_token_here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = your_testpypi_api_token_here
EOF

# 方法2: 设置环境变量
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your_pypi_api_token_here
export TWINE_PASSWORD_TEST=your_testpypi_api_token_here
```

## 构建包

### 使用hatchling构建
```bash
# 标准构建
python -m build

# 或指定构建类型
python -m build --wheel
python -m build --sdist
```

### 使用uv构建
```bash
uv build
```

### 检查构建结果
```bash
# 查看dist目录
ls -la dist/

# 应该看到类似文件：
# neo4j-mcp-memory-scccy-0.2.1.tar.gz
# neo4j_mcp_memory_scccy-0.2.1-py3-none-any.whl
```

## 测试包（可选）

### 安装到虚拟环境测试
```bash
# 使用pip
pip install dist/*.whl

# 使用uv
uv pip install dist/*.whl

# 测试导入
python -c "import mcp_neo4j_memory; print('Package imported successfully')"
```

### 卸载测试包
```bash
pip uninstall neo4j-mcp-memory-scccy
```

## 上传到PyPI

### 上传到测试PyPI（推荐首次使用）
```bash
# 使用配置文件
twine upload --repository testpypi dist/*

# 使用环境变量
TWINE_REPOSITORY_URL=https://test.pypi.org/legacy/ twine upload dist/*
```

### 上传到正式PyPI
```bash
# 使用配置文件
twine upload dist/*

# 使用环境变量
twine upload dist/*
```

### 强制上传（覆盖已存在的版本）
```bash
twine upload --skip-existing dist/*
```

## 一键脚本

### 完整构建上传流程
```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info/

# 构建并上传到测试PyPI
python -m build && twine upload --repository testpypi dist/*

# 构建并上传到正式PyPI
python -m build && twine upload dist/*
```

### 使用Makefile（如果项目中有）
```bash
# 构建
make build

# 发布到测试PyPI
make publish-test

# 发布到正式PyPI
make publish
```

## 验证上传结果

### 检查包状态
```bash
# 检查测试PyPI
pip search --index https://test.pypi.org/simple/ neo4j-mcp-memory-scccy

# 检查正式PyPI
pip search neo4j-mcp-memory-scccy
```

### 访问PyPI网站
- 测试PyPI: https://test.pypi.org/project/neo4j-mcp-memory-scccy/
- 正式PyPI: https://pypi.org/project/neo4j-mcp-memory-scccy/

## 版本管理

### 更新版本号
```bash
# 编辑 pyproject.toml 中的 version 字段
# 例如: version = "0.2.1"

# 或者使用工具自动更新
pip install bump2version
bump2version patch  # 0.2.0 -> 0.2.1
bump2version minor  # 0.2.0 -> 0.3.0
bump2version major  # 0.2.0 -> 1.0.0
```

### 创建Git标签
```bash
# 创建版本标签
git tag v0.2.1
git push origin v0.2.1
```

## 故障排除

### 常见错误
```bash
# 认证失败
# 检查 ~/.pypirc 文件或环境变量

# 包已存在
# 使用 --skip-existing 或更新版本号

# 构建失败
# 检查 pyproject.toml 配置和依赖
```

### 清理环境
```bash
# 清理构建文件
rm -rf dist/ build/ *.egg-info/

# 清理缓存
pip cache purge
```

## 最佳实践

1. **首次发布**: 先上传到测试PyPI验证
2. **版本管理**: 每次发布前更新版本号
3. **测试验证**: 上传前确保包能正常安装和导入
4. **文档更新**: 更新CHANGELOG.md记录变更
5. **Git标签**: 为每个发布版本创建Git标签
