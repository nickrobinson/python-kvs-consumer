from bitstring import BitArray, BitStream
import boto3
import skvideo.io
import tempfile
import os
import click
import queue
import threading

from darkflow.net.build import TFNet
import cv2

options = {"model": "cfg/tiny-yolo-voc.cfg", "load": "bin/tiny-yolo-voc.weights", "threshold": 0.3}
tfnet = TFNet(options)

q = queue.Queue()

def worker(endpoint, stream):
    counter = 0
    client = boto3.client('kinesis-video-media', endpoint_url=endpoint)

    response = client.get_media(
        StreamName=stream,
        StartSelector={
            'StartSelectorType': 'NOW'
        }
    )

    fd, path = tempfile.mkstemp()

    iterchunks = response['Payload'].iter_chunks()
    first_chunk = next(iterchunks)
    chunk = BitArray(first_chunk)

    for i in iterchunks:
        a = BitArray(i)
        pos = a.find('0x1a45dfa3')
        if pos:
            chunk.append(a[:pos[0]])
            with open('/Volumes/ramdisk/myfile.mkv', 'wb') as w:
                w.write(chunk.tobytes())
            videogen = skvideo.io.vreader('/Volumes/ramdisk/myfile.mkv')
            for frame in videogen:
                if counter % 20 == 1:
                    q.put(frame)
            chunk = a[pos[0]:]
        else:
            chunk.append(a)
        counter += 1

@click.command()
@click.option('--endpoint', prompt='Kinesis Video Endpoint', help='Kinesis Video Endpoint.')
@click.option('--stream', prompt='Kinesis Stream Name', help='Kinesis Stream Name.')

def run(endpoint, stream):

    t = threading.Thread(target=worker, args=(endpoint, stream))
    t.start()

    while True:
        item = q.get()
        if item is None:
            break
        #print(q.qsize())
        mat = cv2.cvtColor(item, cv2.COLOR_BGR2RGB)
        small_mat = cv2.resize(mat, (0,0), fx=0.4, fy=0.4)
        result = tfnet.return_predict(small_mat)
        print(result)
        #cv2.imshow('image', small_mat)
        #cv2.waitKey(1)
        q.task_done()

if __name__ == '__main__':
    run()
