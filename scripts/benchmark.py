import requests
import time
from threading import Thread
import queue
from func_timeout import func_timeout, func_set_timeout
import random


# params
server_host = 'http://intelligent-content-gray.bigoml.cc'  # gray env
#server_host = 'https://evg-ml.bigo.sg'  # production env
user_image_url = 'http://img.like.video/asia_live/4h5/0KK2hA.jpg'
template_url = 'https://static-web.likeevideo.com/as/likee-static/act-23756/2.png'


def oilpaint_gen_image():
    start_time = time.time()
    url = '{}/auto-deploy/gen_image'.format(server_host)
    params = {
        "image_url":user_image_url,
        "template_url": template_url,
        "model_id":0,
    }
    resp = requests.post(url, json=params)
    print('gen_image cost: {}s'.format(time.time() - start_time))
    print(resp.text)

def pressure():
    def log_func():
        start_time = time.time()
        while not tasks.empty():
            time.sleep(1)
            print('{:3f} req/sec'.format(num_finished / (time.time()-start_time)))

    def worker_func():
        nonlocal num_finished
        nonlocal num_timeout
        while not tasks.empty():
            tasks.get()
            try:
                res = func_timeout(20, oilpaint_gen_image)
            except Exception as err:
                num_timeout += 1
                print('-------------timeout--------------')
            num_finished += 1

    tasks = queue.Queue()
    num_finished = 0
    num_timeout = 0
    num_tasks = 200
    num_workers  = 10

    for _ in range(num_tasks):
        tasks.put(None)
    workers = []
    logger = Thread(target=log_func)
    logger.start()
    for _ in range(num_workers):
        worker = Thread(target=worker_func)
        worker.start()
        workers.append(worker)
    for worker in workers:
        worker.join()
    logger.join()
    print('total:{}, timeout:{}'.format(num_tasks, num_timeout))

#pressure()
oilpaint_gen_image()

