import click

#from darkflow.net.build import TFNet
import cv2
from amazon_kvclpy import kvcl

class FrameProcessor(kvcl.FrameProcessorBase):

    def initialize(self, shard_id):
        pass

    def process_frame(self, frame, checkpointer):
        small = cv2.resize(frame, (0,0), fx=0.25, fy=0.25) 
        img = cv2.cvtColor(small, cv2.COLOR_RGB2BGR)
        # Display the resulting frame
        cv2.imshow('frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            exit()

    def shutdown(self, checkpointer, reason):
        cv2.destroyAllWindows()
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
