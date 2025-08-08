# Python CNB OpenAPI SDK

[![PyPI](https://img.shields.io/pypi/v/python-cnb.svg)](https://pypi.org/project/python-cnb/)
[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
<a href="https://yuanbao.tencent.com"><img src="https://img.shields.io/badge/AI-Code%20Assist-EB9FDA"></a>

CNB OpenAPI的Python SDK，方便与CNB平台进行交互。
> 该 sdk 由 [cnb-sdk-generator](https://cnb.cool/cnb/sdk/cnb-sdk-generator) 生成

## 功能特性

- 完整的API覆盖（用户、仓库、Issue等）
- 基于Pydantic的强类型模型
- 完善的错误处理机制
- 自动重试和超时控制

## 安装

```bash
pip install -e .
```

或通过PyPI安装（已发布）：

```bash
pip install python-cnb
```

## 快速开始

```python
#!/usr/bin/env python

import os
from dotenv import load_dotenv
from cnb import CNBClient
from cnb.exceptions import CNBAPIError
from cnb.models import api

# 加载环境变量
load_dotenv()

def get_user_info():
    # 初始化客户端
    client = CNBClient(
        base_url="https://api.cnb.cool",
        api_key=os.getenv("CNB_TOKEN"),  # 从环境变量获取API Key
        max_retries=3,  # 最大重试次数
        timeout=30,     # 请求超时时间(秒)
    )

    try:
        user_info = client.cnb.users.get_user_info()
        print(f"user_info: {user_info}")

    except CNBAPIError as e:
        print(f"API调用失败: {e}")

def create_issue():
    # 初始化客户端
    client = CNBClient(
        base_url="https://api.cnb.cool",
        api_key=os.getenv("CNB_TOKEN"),  # 从环境变量获取API Key
        max_retries=3,  # 最大重试次数
        timeout=30,     # 请求超时时间(秒)
    )

    try:
        issue = client.cnb.issues.create_issue(
            repo="looc/test-ci", 
            body_params=api.PostIssueForm(
                title="测试 Issue",
                priority="111"
            )
        )
        print(f"issue: {issue}")

    except CNBAPIError as e:
        print(f"API调用失败: {e.errcode}")       

if __name__ == "__main__":
    get_user_info()
    list_issues()

```

## 许可证

MIT License - 详见[LICENSE](LICENSE)文件