# EVG auto-deploy
[![pipeline status](https://git.sysop.bigo.sg/intelligent-content-serving/evg-ml-auto-deploy/badges/master/pipeline.svg)](https://git.sysop.bigo.sg/intelligent-content-serving/evg-ml-auto-deploy/commits/master)

本套框架适用于小流量的,追求快速上线的,短期运行的服务.通过CI/CD,可以快速部署服务.  
使用时有任何问题或建议,请联系柏嘉洛(baijialuo@bigo.sg).

## 版本信息
### master:
1. 启用EFK日志持久化工具,可以在[kibada dashboard](http://164.90.89.157:32279/app/kibana#/discover?_g=())查看日志,并下载.
2. 灰度环境配置了单独的域名, 避免与线上流量冲突.
3. 支持triton-serving的pytorch模型部署.
4. 暂时关闭了CI中stop-gray阶段(技术故障).
5. 申请了新的rancher账号,推荐使用(账号algorithm过多人使用,经常出现无法登录的问题).
### v1.0
1. 启用框架, 第一个正式版本.

## 使用方法
1. 将推理模型打包为docker镜像,打包方法参考[这里](https://git.sysop.bigo.sg/gaoyibin/evg-ml-serving-models/tree/master/examples).
2. 在`master`分支(或标有tag的最新版本)的基础上新建分支(分支建议命名为`deploy/<project_name>`),进行服务的开发.
3. 修改`config.yaml`文件,更新配置.请不要随意增减配置项.
4. 在`server.py`里实现与后台定义好的http服务接口(不要删除其中的`ping`接口), 接口定义参考`example/interface.md`.
5. 在`src`下面实现具体的解决方案.
6. 在对应的gitlab CI/CD里手动创建灰度部署,进行测试.测试无误后,下线灰度部署,手动创建生产部署.
7. 模型或代码的更新请重复以上1,3,5,6步骤.

## 注意事项
1. Master分支不接受任何业务相关的Merge Request. master会有一些bug的修复或者新功能的添加,建议master分支有更新时,merge到本分支.
2. 请不要在gitlab CI/CD下上线或下线他人的服务.
3. 请在`src/requirements.txt`下添加所需的额外的依赖,`docker/base/requirements.txt`可以查看已经安装的依赖.
4. 每个服务(包括模型)的最小replicas推荐设置为2,防止服务不可用时(如宕机,更新服务),服务请求失败.为防止机器资源的浪费,灰度环境下强制设置所有deployment的replicas为1, 生产环境下的replicas与`config.yaml`中的设置一致.
5. 如果有多个模型,推荐将小模型或者调用量不高的模型ensemble,参考这里的[多模型部署](https://git.sysop.bigo.sg/gaoyibin/evg-ml-serving-models/tree/master/examples).这样可以提高gpu的利用率,优化成本.
6. 部署到生产环境之后,推荐将模型进行预热,降低服务初始请求的延时,运行`scripts/benchmark.py`里的`pressure()`即可.注意要修改请求的接口.
7. 切记在灰度环境下测试无误,可以得到正确的结果之后,再部署到生产环境.
8. 在[rancher灰度页面(全局/sean/gray)](https://admin.bigoml.cc/p/c-r89km:p-ltprd/workloads)下可以找到部署在灰度环境的服务(服务名下方的标有`<端口号>/tcp`的链接是可以直接调用测试的).对正式环境的服务有疑问,请联系柏嘉洛.
   - 账号: content
   - 密码: content
   - 注: 该账号仅有只读权限,可以查看pod的log. 但无法进行任何修改, 想要修改请通过push代码的方式.
9. 如果代码结构,耗时等需要优化, 请联系柏嘉洛,高逸斌.

### 常见问题
1. Q: 如何配置模型推理服务?  
   A: 模型是通过环境变量的方式进行配置的.`src/libs/tf_rpc_client.py`是一个tf-serving grpc接口的调用示例.这里调用需要模型的domain和name,domain就是在`src/models_info.py`里配置的,name是在模型打包的时候设置的.
2. Q: rancher上模型的deployment出现`ImagePullBackOff`错误,该怎么办?  
   A: 请检查模型的docker image是否push到根目录为`harbor.bigo.sg/bigo_ai`的路径下, 目前集群仅设置了这一个根目录的凭证.
3. Q: 我的分支需要使用submodule, 但是CI的build阶段Clone出错,该怎么办?  
   A: 首先根据[gitlab-ci submodule文档](https://docs.gitlab.com/ee/ci/git_submodules.html)正确导入submodule, 然后将`.gitlab-ci.yml`中第二行的`GIT_SUBMODULE_STRATEGY`的值修改为`none`, 最后将标有`for submodule`的行取消注释,重新push即可.
4. Q: 我的pod一直在重启,有时候也可以返回正确的结果,是怎么回事?  
   A: 请检查`server.py`文件是否将`"/{}/ping".format(INTERFACE_PREFIX)`这个接口删除,如果删除了请按照原`server.py`的写法将该接口添加上. 该接口是线上服务进行健康检查的接口,必须实现,否则当k8s发现该接口无法访问时就会进行重启.
5. Q: `config.yaml`中的`model["name"]`与模型推理接口(及`models_info.py`)中的`model_name`有什么区别?  
   A: `config.yaml`中配置的`model["name"]`作用域仅限于该文件(主要是作为k8s上相应deployment/service的名称)。而模型推理接口(及`models_info.py`)中的`model_name`用于指定要进行推理的模型，需要与构建docker镜像时设置的`model_name`一致.

## 更多
### Gunicorn
本框架使用Flask + Gunicorn的http服务部署方案.  
使用Gunicorn控制进程&线程的数量，并对请求进行分发.flask是一个十分轻量的web应用框架,这也就导致了本框架在处理http请求时,不具有负载均衡(k8s里具有负载均衡功能,所以就需要根据请求量增减服务的replicas),连接保持等功能.

### 部署
当push代码后, 首先会在CI的Build阶段将本分支的代码打包成一个docker image, 并将commit id作为tag. 然后调用`deploy/generater.py`生成k8s部署的yaml文件, 包括: CGI的deployment/service(本分支的代码, 不分配gpu), 每个模型的deployment/service,以及相应的namspace和ingress. 最后在CI的Gray阶段和Production阶段调用`kubectl apply -f deploy-<phase>.yaml`进行部署, 在CI的Stop_gray阶段调用`kubectl delete -f deploy-gray.yaml`删除灰度部署.

### 代码结构
下图展示了基本的代码调用逻辑:  
![data_flow](example/assets/data_flow.jpg)  
当客户端发起请求时, 首先通过`server.py`解析http请求参数, 从CDN上下载数据并解码; 然后调用`src/engine.py`, 根据参数,调用指定的处理逻辑, 并完成编码等处理;`src/libs`是核心的处理逻辑,主要进行数据的前后处理及模型推理操作.  
推荐使用上述的代码调用逻辑关系编写代码,将代码进行解耦合,方便调试及后续的迭代开发.

### 模型文件
模型文件建议放入`models`,并使用LFS存储文件, 不过由于公司Git LFS的配置，超过300M的文件就无法直接上传，此时建议先对文件进行split操作，然后在打包镜像的时候进行Merge操作.  
使用方法: `git lfs track "models/**"`
模型分割合并方法：
1. 分割模型  
    `split -b 100000000 ${filename} ${filename}- && rm ${filename}`
2. 合并模型  
    `cat ${filename}-* > ${filename} && rm ${filename}-*`

### 告警模块
告警功能使用的是公司的棱镜系统, 自定义告警请点[这里](http://mon.sysop.bigo.sg/metrics_admin.html).  
目前已添加了一个告警策略, 推荐在`server.py`中, 每个接口处添加. 当线上服务出现问题时, 可以第一时间在企业微信"内容生产监控告警"群里收到通知.
