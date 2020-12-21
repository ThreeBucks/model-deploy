import binascii
import json
import logging

import cv2
import numpy as np
import requests

VIDEO_UPLOAD_URL = 'http://video-fs.like.video/upload_video.php'
IMAGE_UPLOAD_URL = 'http://img-fs.like.video/FileuploadDownload/upload_img.php'

logger = logging.getLogger(__name__)


def upload_video(video_bytes):
    files = {
        'file': video_bytes
    }

    try:
        resp = requests.post(VIDEO_UPLOAD_URL, files=files)
        if resp.status_code == 200:
            url = json.loads(resp.text)['url']
            crc = binascii.crc32(video_bytes)
            url = '{}?crc={}&type=5'.format(url, crc)
            return url
        else:
            return None
    except Exception as err:
        logger.error('upload_video failed, error info {}'.format(err))
        return None


def upload_image(image_bytes, req_name='default', ext='.jpg'):
    files = {
        'file': ('image{}'.format(ext), image_bytes)
    }

    try:
        if req_name == 'bigo_live':
            resp = requests.post('http://snapshot.calldev.bigo.sg/upload_file.php', files=files)
        else:
            resp = requests.post(IMAGE_UPLOAD_URL, files=files)

        if resp.status_code == 200:
            return json.loads(resp.text)['url']
        else:
            return None
    except Exception as err:
        logger.error('upload_image failed, error info {}'.format(err))
        return None


def download_video(video_url):
    try:
        resp = requests.get(video_url)
    except Exception as err:
        logger.error('download_video failed, video_url {}, error info {}'.format(video_url, err))
        return None

    if resp.status_code != 200 or not resp.content:
        logger.error('download_video failed, video_url {}'.format(video_url))
        return None

    video_bytes = resp.content

    if video_bytes is None:
        logger.error('download_video failed, empty video, video_url {}'.format(video_url))
        return None

    return video_bytes


def download_image(image_url, decode=False, to_rgb=False):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0'
    }

    try:
        resp = requests.get(image_url, headers=headers)
    except Exception as err:
        logger.error('download_image failed, image_url {}, error info {}'.format(image_url, err))
        return None

    if resp.status_code != 200 or not resp.content:
        logger.error('download_image failed, image_url {}'.format(image_url))
        return None

    image_bytes = resp.content
    image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), cv2.IMREAD_COLOR)

    if image is None:
        logger.error('download_image failed, empty image, image_url {}'.format(image_url))
        return None

    if decode and to_rgb:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    return image if decode else image_bytes


if __name__ == '__main__':
    image_bytes = requests.get('http://img.like.video/asia_live/4h6/1Jgvll.jpg').content
    image_url = upload_image(image_bytes)
    print(image_url)

    video_bytes = requests.get(
        'http://video.like.video/asia_live/7h4/M0B/C9/D7/bvsbAF37MUGEev_7AAAAAGsyOC8464.mp4').content
    video_url = upload_video(video_bytes)
    print(video_url)

    img = download_image('http://img.like.video/asia_live/4h6/1Jgvll.jpg', decode=True)
    print(img.shape)
