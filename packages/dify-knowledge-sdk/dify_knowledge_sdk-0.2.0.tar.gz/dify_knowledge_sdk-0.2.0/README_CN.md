# Dify 知识库 SDK

一个用于与 Dify 知识库 API 交互的综合 Python SDK。此 SDK 提供了通过 Dify REST API 管理数据集（知识库）、文档、片段和元数据的易用方法。

## 功能特性

- 📚 **完整的 API 覆盖**：支持所有 Dify 知识库 API 端点
- 🔐 **身份验证**：基于 API 密钥的安全身份验证
- 📄 **文档管理**：从文本或文件创建、更新、删除文档
- 🗂️ **数据集操作**：知识库的完整 CRUD 操作
- ✂️ **片段控制**：精细控制文档片段（块）的管理
- 🏷️ **元数据支持**：创建和管理自定义元数据字段
- 🌐 **HTTP 客户端**：基于 httpx 构建，提供可靠快速的 HTTP 通信
- ⚠️ **错误处理**：使用自定义异常进行全面的错误处理
- 📊 **进度监控**：跟踪文档索引进度
- 🔒 **类型安全**：使用 Pydantic 模型提供完整类型提示

## 安装

```bash
pip install dify-sdk
```

## 快速开始

```python
from dify_sdk import DifyDatasetClient

# 初始化客户端
client = DifyDatasetClient(api_key="your-api-key-here")

# 创建新的数据集（知识库）
dataset = client.create_dataset(
    name="我的知识库",
    permission="only_me"
)

# 从文本创建文档
doc_response = client.create_document_by_text(
    dataset_id=dataset.id,
    name="示例文档",
    text="这是知识库的示例文档。",
    indexing_technique="high_quality"
)

# 列出所有文档
documents = client.list_documents(dataset.id)
print(f"文档总数: {documents.total}")

# 关闭客户端
client.close()
```

## 配置

### API 密钥

从 Dify 知识库 API 页面获取您的 API 密钥：

1. 进入您的 Dify 知识库
2. 在左侧边栏导航到 **API** 部分
3. 从 **API 密钥** 部分生成或复制您的 API 密钥

### 基础 URL

默认情况下，SDK 使用 `https://api.dify.ai` 作为基础 URL。您可以自定义：

```python
client = DifyDatasetClient(
    api_key="your-api-key",
    base_url="https://your-custom-dify-instance.com",
    timeout=60.0  # 自定义超时时间（秒）
)
```

## 核心功能

### 数据集管理

```python
# 创建数据集
dataset = client.create_dataset(
    name="技术文档",
    permission="only_me",
    description="内部技术文档"
)

# 分页列出数据集
datasets = client.list_datasets(page=1, limit=20)

# 删除数据集
client.delete_dataset(dataset_id)
```

### 文档操作

#### 从文本创建

```python
# 从文本创建文档
doc_response = client.create_document_by_text(
    dataset_id=dataset_id,
    name="API 文档",
    text="完整的 API 文档内容...",
    indexing_technique="high_quality",
    process_rule_mode="automatic"
)
```

#### 从文件创建

```python
# 从文件创建文档
doc_response = client.create_document_by_file(
    dataset_id=dataset_id,
    file_path="./documentation.pdf",
    indexing_technique="high_quality"
)
```

#### 自定义处理规则

```python
# 自定义处理配置
process_rule_config = {
    "rules": {
        "pre_processing_rules": [
            {"id": "remove_extra_spaces", "enabled": True},
            {"id": "remove_urls_emails", "enabled": True}
        ],
        "segmentation": {
            "separator": "###",
            "max_tokens": 500
        }
    }
}

doc_response = client.create_document_by_file(
    dataset_id=dataset_id,
    file_path="document.txt",
    process_rule_mode="custom",
    process_rule_config=process_rule_config
)
```

### 片段管理

```python
# 创建片段
segments_data = [
    {
        "content": "第一个片段内容",
        "answer": "第一个片段的答案",
        "keywords": ["关键词1", "关键词2"]
    },
    {
        "content": "第二个片段内容",
        "answer": "第二个片段的答案",
        "keywords": ["关键词3", "关键词4"]
    }
]

segments = client.create_segments(dataset_id, document_id, segments_data)

# 列出片段
segments = client.list_segments(dataset_id, document_id)

# 更新片段
client.update_segment(
    dataset_id=dataset_id,
    document_id=document_id,
    segment_id=segment_id,
    segment_data={
        "content": "更新的内容",
        "keywords": ["更新", "关键词"],
        "enabled": True
    }
)

# 删除片段
client.delete_segment(dataset_id, document_id, segment_id)
```

### 元数据管理

```python
# 创建元数据字段
category_field = client.create_metadata_field(
    dataset_id=dataset_id,
    field_type="string",
    name="category"
)

priority_field = client.create_metadata_field(
    dataset_id=dataset_id,
    field_type="number",
    name="priority"
)

# 更新文档元数据
metadata_operations = [
    {
        "document_id": document_id,
        "metadata_list": [
            {
                "id": category_field.id,
                "value": "technical",
                "name": "category"
            },
            {
                "id": priority_field.id,
                "value": "5",
                "name": "priority"
            }
        ]
    }
]

client.update_document_metadata(dataset_id, metadata_operations)
```

### 进度监控

```python
# 监控文档索引进度
status = client.get_document_indexing_status(dataset_id, batch_id)

if status.data:
    indexing_info = status.data[0]
    print(f"状态: {indexing_info.indexing_status}")
    print(f"进度: {indexing_info.completed_segments}/{indexing_info.total_segments}")
```

## 错误处理

SDK 提供了具有特定异常类型的全面错误处理：

```python
from dify_sdk.exceptions import (
    DifyAPIError,
    DifyAuthenticationError,
    DifyValidationError,
    DifyNotFoundError,
    DifyConflictError,
    DifyServerError,
    DifyConnectionError,
    DifyTimeoutError
)

try:
    dataset = client.create_dataset(name="测试数据集")
except DifyAuthenticationError:
    print("无效的 API 密钥")
except DifyValidationError as e:
    print(f"验证错误: {e}")
except DifyConflictError as e:
    print(f"冲突: {e}")  # 例如，重复的数据集名称
except DifyAPIError as e:
    print(f"API 错误: {e}")
    print(f"状态码: {e.status_code}")
    print(f"错误码: {e.error_code}")
```

## 高级用法

对于更高级的场景，请查看 [examples](./examples/) 目录：

- [基础用法](./examples/basic_usage.py) - 简单操作和入门
- [高级用法](./examples/advanced_usage.py) - 复杂工作流、批量操作和监控

## API 参考

### 客户端配置

```python
DifyDatasetClient(
    api_key: str,           # 必需：您的 Dify API 密钥
    base_url: str,          # 可选：API 基础 URL（默认："https://api.dify.ai"）
    timeout: float          # 可选：请求超时时间秒数（默认：30.0）
)
```

### 支持的文件类型

SDK 支持上传以下文件类型：

- `txt` - 纯文本文件
- `md`, `markdown` - Markdown 文件
- `pdf` - PDF 文档
- `html` - HTML 文件
- `xlsx` - Excel 电子表格
- `docx` - Word 文档
- `csv` - CSV 文件

### 速率限制

请遵守 Dify 的 API 速率限制。SDK 包含对速率限制响应的自动错误处理。

## 开发

### 设置

```bash
# 克隆仓库
git clone https://github.com/dify/dify-sdk-python.git
cd dify-sdk-python

# 安装依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black dify_sdk/
isort dify_sdk/
```

## 贡献

欢迎贡献！请随时提交 Pull Request。

## 许可证

此项目根据 MIT 许可证授权 - 有关详细信息，请参阅 [LICENSE](LICENSE) 文件。

## 支持

- 📖 [Dify 文档](https://docs.dify.ai/)
- 🐛 [问题跟踪器](https://github.com/dify/dify-sdk-python/issues)
- 💬 [社区讨论](https://github.com/dify/dify/discussions)

## 更新日志

### v0.1.0

- 初始发布
- 完整的 Dify 知识库 API 支持
- 数据集、文档、片段和元数据的完整 CRUD 操作
- 全面的错误处理
- 使用 Pydantic 的类型安全模型
- 文件上传支持
- 进度监控
- 示例和文档
