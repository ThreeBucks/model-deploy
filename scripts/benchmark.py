import os
import time
import yaml
import queue
import requests
from threading import Thread


# Global
NUM_TASKS = 200
NUM_WORKERS = 5


# params
server_host = 'http://infer-audit-sg.ingress.ml.bigo.inner:8080'
# server_host = 'http://localhost:5000'  # localhost
user_image_url = 'http://img.like.video/asia_live/4h5/0KK2hA.jpg'
template_url = 'https://static-web.likeevideo.com/as/likee-static/act-23756/2.png'

project_name = yaml.safe_load(open(os.path.join(os.path.dirname(__file__), "../config.yaml"), "r"))["project_name"]


def gen_image(cost_que=None):
    start_time = time.time()
    url = '{}/api/grey/content/{}/gen_image'.format(server_host, project_name)  # grey
    # url = '{}/api/content/{}/gen_image'.format(server_host, project_name)  # production or NodePort
    params = {
        "image_url":user_image_url,
        "template_url": template_url,
        "model_id":0,
    }
    resp = requests.post(url, json=params)
    if cost_que is not None:
        cost_que.put(time.time() - start_time)
    print('gen_image cost: {}s'.format(time.time() - start_time))
    print(resp.text)

def pressure():
    def log_func():
        start_time = time.time()
        while not tasks.empty():
            time.sleep(1)
            qps = num_finished / (time.time()-start_time)
            qps_que.put(qps)
            print('{:3f} req/sec'.format(qps))

    def worker_func():
        nonlocal num_finished
        while not tasks.empty():
            tasks.get()
            res = gen_image(cost_que)
            num_finished += 1

    tasks = queue.Queue()
    cost_que = queue.Queue()
    qps_que = queue.Queue()
    cost_list = []
    qps_list = []
    num_finished = 0

    for _ in range(NUM_TASKS):
        tasks.put(None)
    workers = []
    logger = Thread(target=log_func)
    logger.start()
    for _ in range(NUM_WORKERS):
        worker = Thread(target=worker_func)
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()
    logger.join()
    for _ in range(NUM_TASKS):
        cost_list.append(cost_que.get())
    cost_list = sorted(cost_list)
    while qps_que.qsize() > 0:
        qps_list.append(qps_que.get())
    qps_list = sorted(qps_list)

    print('QPS: max:{:.3f}, recommend:{:.3f}'.format(qps_list[-1], qps_list[int(len(qps_list) * 0.8)]))
    print('total tasks:{}, average cost:{:.3f}s, 50th cost:{:.3f}s, 90th cost:{:.3f}s'.format(
        NUM_TASKS, sum(cost_list) / NUM_TASKS, cost_list[int(NUM_TASKS * 0.5)], cost_list[int(NUM_TASKS * 0.9)]))

# pressure()
gen_image()

