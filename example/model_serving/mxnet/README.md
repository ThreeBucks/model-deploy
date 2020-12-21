### 背景
[multi-model-server](https://github.com/awslabs/multi-model-server)（MMS）是mxnet的模型推理框架。可以通过命令行工具或docker部署推理服务，这里仅介绍基于docker的部署。  
由于其仅支持http接口，使用python处理http请求及模型前后处理，会导致推理效率较低，推荐使用tf serving(examples/tensorflow)。  
如果你在使用过程中,遇到并解决了任何问题,请帮助我们完善相关文档(向master分支提交MR).

### 单模型构建
1. 导出模型
    - 参考[官方教程](http://mxnet.incubator.apache.org/api/python/docs/tutorials/)  
    - 保存模型到`models`下，分别为`<xxx>-0000.params`和`<xxx>-symbol.json`  
    注：params文件名中必须是`0000`, `<xxx>`与模型名称一致
2. 安装环境
    - 新建python虚拟环境(conda:`conda create -n mms python=3.6`)，启用环境
    - 安装相关依赖库： `pip install -r requirements.txt`
3. 构建docker镜像
    修改`signature.json`，设置网络输入大小及类型等信息。  
    修改`mxnet_service_template/mxnet_vision_service.py`中的`preprocess`函数和`postprocess`函数为网络所需要的前后处理操作。  
    修改`build.sh`
     - 修改`MODEL_NAME`变量为模型名称
     - 修改`IMAGE_NAME`变量为docker image名称，参考[docker镜像命名规范](http://wiki.bigo.sg:8090/pages/viewpage.action?pageId=179601831)  

    运行脚本:  
    `bash build.sh`
4. 创建docker容器
    - 修改`run.sh`，修改其中的端口映射，gpu，及镜像名称。  
        注：  
        - http接口端口为8080，模型管理端口为8081。
        - 不支持使用环境变量的方式设置gpu，使用`--gpus`参数进行设置(docker daemon API version >= 1.40)。  
    - 运行脚本：  
    `bash run.sh`
5. 接口调用  
   修改`http_client.py`中main函数的`MxHttpClient`的`address`及`client.infer`中的`model_name`进行调用测试。

### 多模型构建
    参考单模型构建.需要为不同模型编写相应的前后处理，然后导出相应的`<model_name>.mar`文件，然后修改`Dockerfile`，将.mar文件COPY到镜像的模型目录下。  
    运行脚本：  
    `bash build.sh`

### 常见问题
1. 安装的mxnet版本要与训练时的版本一致，否则可能会出现不兼容的问题。
2. 运行镜像时出现`MXNetError: Cannot find argument 'layout'`的错误。直接将模型的`<xxx>-symbol.json`中`layout`相关的行删除即可。
