## 说明
1. 推荐使用在[这个仓库](https://git.sysop.bigo.sg/baijialuo/evg-ml-serving-interface)提issue的方式来定义接口.
2. 本接口文档适用于master分支的`server.py`,仅供参考

## 接口定义
### 接口1
**请求类型** `POST`  
**请求** `/auto-deploy/gen_image`
```
{
    model_id: <int>
    image_url: <image url>
    template_url: <image url>
}
```
**响应**
```
{
    image_url: <image url>,
    err_code: <int>
}
```

### 错误码
```
SUCCESS = 200
# common
ERR_INVALID_ARGS = 2
ERR_CDN = 3
ERR_SYSTEM = -1
ERR_OVERLOAD = -2
# face related
NO_FACE = 201
FACE_TOO_LARGE = 202
FACE_TOO_SMALL = 203
FACE_NOT_CENTER = 204
# quality related
QUALITY_TOO_LOW = 301
```

### 注释
1. 其中`template_url`为素材模板图片url

### 接口参数解释
#### model_id
```
# only one model by now
default = 0
```