## 关于OSS的OpenAPI调用

因为 oss 是数据类型的 OpenAPI，因此我们对其进行了特殊处理，调用方式跟官网SDK存在一些差别

## 获取所有bucket

```python
from one_sdk.client import OneClient
from aliyunsdkcore.request import RpcRequest

def test_oss_api():
    client = OneClient(
        ${consoleKey},
        ${consoleSecret},
        ${regionId}
    )
    client.set_endpoint('work-cn-hangzhou.aliyuncs.com')
    client.add_query_param('AliUid', 'xxx')
    
    req = RpcRequest('oss', '', 'GetService')
    

    res = client.do_action_with_exception(req)
    print(res)    
```