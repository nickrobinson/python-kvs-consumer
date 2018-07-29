import click

#from darkflow.net.build import TFNet
# import cv2
from amazon_kvclpy import kvcl

class FrameProcessor(kvcl.FrameProcessorBase):

    def initialize(self, shard_id):
        pass

    def process_frame(self, frame, checkpointer):
        pass

    def shutdown(self, checkpointer, reason):
        pass

@click.command()
@click.option('--endpoint', prompt='Kinesis Video Endpoint', help='Kinesis Video Endpoint.')
@click.option('--stream', prompt='Kinesis Stream Name', help='Kinesis Stream Name.')

def run(endpoint, stream):
    processor = kvcl.KVCLProcess(FrameProcessor(),
        stream,
        endpoint)
    processor.run()

if __name__ == '__main__':
    run()
