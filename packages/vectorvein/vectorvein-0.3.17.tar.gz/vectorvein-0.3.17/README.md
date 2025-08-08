# 向量脉络 API 包

这是一个用于调用向量脉络官方API的Python包装器。它提供了简单易用的接口来访问向量脉络的工作流和VApp功能。

## 安装

```bash
pip install -r requirements.txt
```

## 使用示例

### 初始化客户端

```python
from vectorvein.api import VectorVeinClient

# 创建客户端实例
client = VectorVeinClient(api_key="YOUR_API_KEY")
```

### 运行工作流

```python
from vectorvein.api import WorkflowInputField

# 准备工作流输入字段
input_fields = [
    WorkflowInputField(
        node_id="8fc6eceb-8599-46a7-87fe-58bf7c0b633e",
        field_name="商品名称",
        value="测试商品"
    )
]

# 异步运行工作流
rid = client.run_workflow(
    wid="abcde0985736457aa72cc667f17bfc89",
    input_fields=input_fields,
    wait_for_completion=False
)
print(f"工作流运行ID: {rid}")

# 同步运行工作流
result = client.run_workflow(
    wid="abcde0985736457aa72cc667f17bfc89",
    input_fields=input_fields,
    wait_for_completion=True
)
print(f"工作流运行结果: {result}")
```

### 管理访问密钥

```python
# 创建访问密钥
keys = client.create_access_keys(
    access_key_type="L",  # L: 长期, M: 多次, O: 一次性
    app_id="YOUR_APP_ID",
    count=1,
    max_credits=500,
    description="测试密钥"
)
print(f"创建的访问密钥: {keys}")

# 获取访问密钥信息
keys = client.get_access_keys(["ACCESS_KEY_1", "ACCESS_KEY_2"])
print(f"访问密钥信息: {keys}")

# 列出访问密钥
response = client.list_access_keys(
    page=1,
    page_size=10,
    sort_field="create_time",
    sort_order="descend"
)
print(f"访问密钥列表: {response}")

# 更新访问密钥
client.update_access_keys(
    access_key="ACCESS_KEY",
    description="更新的描述"
)

# 删除访问密钥
client.delete_access_keys(
    app_id="YOUR_APP_ID",
    access_keys=["ACCESS_KEY_1", "ACCESS_KEY_2"]
)
```

### 生成VApp访问链接

```python
url = client.generate_vapp_url(
    app_id="YOUR_APP_ID",
    access_key="YOUR_ACCESS_KEY",
    key_id="YOUR_KEY_ID"
)
print(f"VApp访问链接: {url}")
```

## API文档

### VectorVeinClient

主要的API客户端类，提供以下方法：

- `run_workflow()` - 运行工作流
- `check_workflow_status()` - 检查工作流运行状态
- `get_access_keys()` - 获取访问密钥信息
- `create_access_keys()` - 创建访问密钥
- `list_access_keys()` - 列出访问密钥
- `delete_access_keys()` - 删除访问密钥
- `update_access_keys()` - 更新访问密钥
- `add_apps_to_access_keys()` - 向访问密钥添加应用
- `remove_apps_from_access_keys()` - 从访问密钥移除应用
- `generate_vapp_url()` - 生成VApp访问链接

### 数据模型

- `VApp` - VApp信息
- `AccessKey` - 访问密钥信息
- `WorkflowInputField` - 工作流输入字段
- `WorkflowOutput` - 工作流输出结果
- `WorkflowRunResult` - 工作流运行结果
- `AccessKeyListResponse` - 访问密钥列表响应

### 异常类

- `VectorVeinAPIError` - API基础异常类
- `APIKeyError` - API密钥相关错误
- `WorkflowError` - 工作流相关错误
- `AccessKeyError` - 访问密钥相关错误
- `RequestError` - 请求相关错误
- `TimeoutError` - 超时错误

## 注意事项

1. 请妥善保管您的API密钥，不要将其泄露给他人。
2. API调用有速率限制，每分钟最多60次调用。
3. 建议在生产环境中使用异步方式运行工作流，避免长时间等待。
4. 访问密钥的类型一旦创建就不能更改，请谨慎选择。
5. 生成的VApp访问链接有效期默认为15分钟，请及时使用。
