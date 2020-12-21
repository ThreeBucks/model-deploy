import os

models_info = {
    0: {
        'gan_name': 'Oilpaint_mmpro',
        'gan_domain': os.environ.get('OILPAINT_TF_SERVING_HOST', 'jja-gpu114.bigoml.cc:8503'),  # 默认配置可用于本地测试
    },
}
