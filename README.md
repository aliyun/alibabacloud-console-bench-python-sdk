<p align="center">
<a href=" https://www.alibabacloud.com"><img src="https://aliyunsdk-pages.alicdn.com/icons/Aliyun.svg"></a>
</p>

<h1 align="center">企业工作台 python sdk</h1>


## 基本原理

在官网 SDK 的基础上，对 Client进行重写，满足企业工作台的调用逻辑，同时完全兼容官网 SDK，这样就形成了 企业工作台定制 Client + 官网 SDK 提供 APIMETA 的模式。


## 环境要求

- 找阿里云企业工作台团队，提供 OpenAPI 访问凭证(consoleKey、consoleSecret)

## SDK 获取与安装

使用 pip 安装(推荐)

```shell
pip install aliyun-console-bench-python-sdk
```

## 快速使用 

企业工作台的业务模式分为 工作台托管、聚石塔自管 两种模式，因此API调用也有针对性区分。


### 工作台托管 SDK 调用示例

```python
from one_sdk.client import OneClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

def test_client_api():
    client = OneClient(${consoleKey}, ${consoleSecret}, ${regionId})
    client.set_endpoint('console-bench.aliyuncs.com')
    client.add_query_param('AliUid', 'xxx')  # OneConsole传递的主账号id
    
    req = DescribeInstancesRequest()
    req.set_VpcId('xxx')

    res = client.do_action_with_exception(req)
    print(res)
```

说明：

- endpoint: 测试环境下需要 host 绑定 114.55.202.134 console-bench.aliyuncs.com


### 聚石塔托管 SDK 调用示例

```python
from one_sdk.client import OneClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest

def test_client_api():
    client = OneClient(${consoleKey}, ${consoleSecret}, ${regionId})
    client.set_endpoint('console-bench.aliyuncs.com')
    client.add_query_param('IdToken', 'xxx')  # Oauth授权后获取的身份信息
    
    req = DescribeInstancesRequest()
    req.set_VpcId('xxx')

    res = client.do_action_with_exception(req)
    print(res)
```

说明：

- endpoint: 测试环境下需要 host 绑定 114.55.202.134 console-bench.aliyuncs.com


