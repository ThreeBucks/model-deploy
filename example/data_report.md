## 数据上报
### 背景
目前集群提供了数据上报功能,可以将请求信息,响应信息及自定义的信息上传到公司大数据平台.  
数据过期时间为30天, 请根据需要决定是否需要上报.   
提供了两种方式查询下载上报的数据,分别是Hive查表和python脚本.
### 是否上报
如果你有以下需求,请选择开启数据上报:
1. 将用户上传的图片用于训练
2. 分析用户上传的图片

如果你的服务没有以上需求,则无需(尽量不要)上报.  
如果你只是想看看生成的结果, 通过rancher查看log即可.
### 如何上报
在`server.py`中将全局变量`DATA_REPORT`设置为`True`, 然后调用`data_reporter.get_instance().process()`.  
其中: 
1. `submodule`为子模块名,主要是用于区分同一个服务下不同的模块(如漫画化服务下有popart, oilpaint, prettycute等模块).
2. `req_params/resp_params`分别是请求参数(包含了用户上传图片的url等信息),返回参数(包含了生成结果等信息).
3. `cost_ms`为请求耗时(可选), 单位为毫秒. 默认为0.
4. `remarks`为备注信息(可选), 用于自定义一些上报项.

### 如何查询
#### Hive查表
1. 登录[Hive平台](http://bi4.bigo.sg/hue/editor/?type=hive), 如果没有权限,请先申请.
2. 使用方法
    1. 一个简单的SQL示例: `select rtime,cost_ms, message  from vlog.likee_evg_content where  day >= "${START_DAY}" and "${END_DAY}" >= day and project_name = "${PROJECT_NAME}"`
    2. 输入要查询的起始日期,终止日期及`project_name`
    3. 点击查询
    4. 下载

    注: Hive可以直接下载<20w条数据, 如果想下载更多比较麻烦,见[使用指南](http://wiki.bigo.sg:8090/pages/viewpage.action?pageId=198706662#HUE%E3%80%81Ooize%E4%BD%BF%E7%94%A8%E6%8C%87%E5%8D%97-Q3%EF%BC%9A%E4%B8%8B%E8%BD%BD%E7%9B%B8%E5%85%B3)
3. 图例
![how_to_use_hive](assets/how_to_use_hive.png)
#### python脚本
[`scripts/extract_report_data.py`](../scripts/extract_report_data.py)为拉取上报数据的python脚本. 填入`START_DAY`, `END_DAY`, `PROJECT_NAME`即可查询.使用相对简单方便.
注: `query`方法会把所有数据(没测试过>20w的情况)一次性拉取下来,用一个列表进行存放(可能会因为数据过多占满内存,而且耗时较高), 推荐使用`query_yield`方法.