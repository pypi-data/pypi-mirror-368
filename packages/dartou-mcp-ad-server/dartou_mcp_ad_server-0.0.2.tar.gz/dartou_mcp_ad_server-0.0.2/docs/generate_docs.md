# 📚 API接口文档自动生成指南

本项目提供了基于Pydantic模型和类型注解的API接口文档自动生成功能。

## 🚀 快速开始

### 1. 安装文档依赖

```bash
# 安装文档生成依赖
uv sync --extra docs
```

### 2. 生成API文档

**方法一：使用命令行脚本**
```bash
generate-api-docs
```

**方法二：直接运行Python脚本**
```bash
python scripts/generate_api_docs.py
```

**方法三：在代码中调用**
```python
from scripts.generate_api_docs import APIDocGenerator

generator = APIDocGenerator()
generator.generate_all_docs()
```

### 3. 查看生成的文档

文档将生成到 `docs/api/generated/` 目录：

```
docs/api/generated/
├── README.md           # 主索引文档
├── client.md          # API客户端接口文档
├── config.md          # 配置参数说明
└── models/            # Pydantic模型文档
    ├── requests.md    # 请求模型
    ├── responses.md   # 响应模型
    └── records.md     # 数据记录模型
```

## 📖 文档内容说明

### 🔧 API客户端文档 (client.md)
- BiApiClient类的所有公开方法
- 方法签名、参数说明、返回值类型
- 基于方法docstring的详细说明

### 📊 数据模型文档 (models/)
- **请求模型**: API请求的Pydantic模型和字段说明
- **响应模型**: API响应的结构和方法说明
- **记录模型**: 业务数据记录的字段分类和使用示例

### ⚙️ 配置文档 (config.md)
- 所有配置常量和支持的选项
- 支持的游戏、媒体、投手、状态等枚举值

## 🔄 自动更新机制

文档生成器的特点：
- **实时同步**: 基于当前代码生成，确保文档与代码同步
- **类型安全**: 利用Pydantic的类型信息自动生成字段说明
- **结构化**: 自动解析方法签名、参数、返回值和docstring

## 🎯 进阶使用

### 自定义文档生成

可以继承`APIDocGenerator`类来自定义文档生成逻辑：

```python
from scripts.generate_api_docs import APIDocGenerator

class CustomDocGenerator(APIDocGenerator):
    def _generate_custom_section(self):
        # 添加自定义文档部分
        pass
```

### 集成到CI/CD

可以在CI/CD流程中自动生成和更新文档：

```yaml
# .github/workflows/docs.yml
- name: Generate API Docs
  run: |
    uv sync --extra docs
    generate-api-docs

- name: Deploy Docs
  # 部署到文档站点
```

### 与MkDocs集成

如果想要更美观的文档站点，可以配合MkDocs使用：

```yaml
# mkdocs.yml
site_name: MCP Ad Analytics API
nav:
  - Home: index.md
  - API Reference:
    - Overview: api/generated/README.md
    - Client: api/generated/client.md
    - Models:
      - Requests: api/generated/models/requests.md
      - Responses: api/generated/models/responses.md
      - Records: api/generated/models/records.md
    - Config: api/generated/config.md

theme:
  name: material

plugins:
  - mkdocstrings:
      handlers:
        python:
          options:
            docstring_style: google
```

然后运行：
```bash
mkdocs serve  # 本地预览
mkdocs build  # 构建静态文档
```

## 💡 最佳实践

1. **定期更新**: 在代码变更后及时生成新文档
2. **版本控制**: 将生成的文档纳入版本控制，便于追踪变更
3. **持续集成**: 在CI中自动检查文档是否需要更新
4. **团队协作**: 让团队成员了解文档生成流程

## 🛠️ 故障排除

### 常见问题

**Q: 生成文档时报导入错误**
A: 确保项目依赖已安装：`uv sync --extra docs`

**Q: 生成的文档不完整**
A: 检查类型注解和docstring是否完整

**Q: Pydantic模型解析失败**
A: 确保模型定义正确且可以正常实例化

### 调试模式

可以修改`generate_api_docs.py`脚本，添加调试输出：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📋 TODO

- [ ] 支持生成OpenAPI规范文档
- [ ] 集成Swagger UI
- [ ] 支持多语言文档生成
- [ ] 添加文档版本管理
