import os
import cv2
import numpy as np
import tensorflow as tf

# import you network
from net import Net

def export_model(checkpoint_path, save_path):
    net_input_shape = [256, 256]  # optional
    
    net = Net()  # modify to your network class name

    if not os.path.exists(checkpoint_path):
        print('There are no checkpoint in {}'.format(checkpoint_path))
    save_dir = os.path.dirname(save_path)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # create input/output tensor, type string is recommended
    input_str = tf.placeholder(tf.string, name='input_str')
    output_str = tf.placeholder(tf.string, name='output_str')
    
    # decode input str and preprocess
    input_img = tf.image.decode_png(input_str, channels=3)
    # input_img = tf.image.resize_images(input_img, net_input_shape)
    input_img = tf.expand_dims(tf.cast(input_img, tf.float32), 0)
    input_img = (input_img - 127.5) / 128.

    # net infer
    pred_img = net(input_img)
    pred_img = tf.identity(pred_img, name='predict')
    
    # postprocess and encode output str
    output_img = tf.cast(pred_img*128. + 127.5, tf.uint8)
    output_str = tf.image.encode_png(output_img[0])
    output_str = tf.stack([output_str], 0)
    
    # load checkpoint
    sess = tf.Session()
    saver = tf.train.Saver(max_to_keep=20)
    ckpt = tf.train.get_checkpoint_state(checkpoint_path)
    if ckpt and ckpt.model_checkpoint_path:
        saver.restore(sess, checkpoint_path)
        print('Load model succeed!')
    else:
        print('Load model failed!, Please check model in {}'.format(checkpoint_path))
        return

    # export saved model
    tf.saved_model.simple_save(
        sess,
        saved_path,
        inputs={'input_str': input_str},
            outputs={'output_str': output_str})
    
    print('Export model succeed!, model saved in {}'.format(saved_path))

if __name__ == "__main__":
    export_model('<checkpoint_path>', '<save_path>')
