from bitstring import BitArray, BitStream
import boto3
import skvideo.io
import tempfile
import os
import cv2
import click

@click.command()
@click.option('--endpoint', prompt='Kinesis Video Endpoint', help='Kinesis Video Endpoint.')
@click.option('--stream', prompt='Kinesis Stream Name', help='Kinesis Stream Name.')

def run(endpoint, stream):
    client = boto3.client('kinesis-video-media', endpoint_url=endpoint)

    response = client.get_media(
        StreamName=stream,
        StartSelector={
            'StartSelectorType': 'NOW'
        }
    )

    stream = response['Payload']

    fd, path = tempfile.mkstemp()

    iterchunks = stream.iter_chunks()
    first_chunk = next(iterchunks)
    chunk = BitArray(first_chunk)

    for i in iterchunks:
        a = BitArray(i)
        pos = a.find('0x1a45dfa3')
        if pos:
            chunk.append(a[:pos[0]])
            with open('myfile.mkv', 'wb') as w:
                w.write(chunk.tobytes())
            videogen = skvideo.io.vreader('myfile.mkv')
            for frame in videogen:
                print(frame.shape)
                mat = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                small_mat = cv2.resize(mat, (0,0), fx=0.5, fy=0.5)
                cv2.imshow('image', small_mat)
                cv2.waitKey(1)
            chunk = a[pos[0]:]
        else:
            chunk.append(a)


if __name__ == '__main__':
    run()