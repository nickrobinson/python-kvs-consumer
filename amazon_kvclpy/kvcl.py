import abc
import tempfile
import boto3
from bitstring import BitArray
import skvideo.io

# RecordProcessor base class
class FrameProcessorBase(object):
    '''
    Base class for implementing a record processor. A RecordProcessor processes frames in a stream.
    Its methods will be called with this pattern:

    - initialize will be called once
    - process_frame will be called zero or more times
    - shutdown will be called if this processor loses its lease
    '''
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def initialize(self, stream_id):
        '''
        Called once by a KCLProcess before any calls to process_frame

        :type stream_id: str
        :param stream_id: The shard id that this processor is going to be working on.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def process_frame(self, frame, checkpointer):
        '''
        Called by a KCLProcess with a list of frames to be processed and a checkpointer which accepts sequence numbers
        from the frames to indicate where in the stream to checkpoint.

        :type frames: list
        :param frames: A list of frames that are to be processed. A record looks like
            {"data":"numpy array","streamName":"someKey","fragmentId":"1234567890"} Note that "data" is a base64
            encoded string. You can use base64.b64decode to decode the data into a string. We currently do not do this decoding for you
            so as to leave it to your discretion whether you need to decode this particular piece of data.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.
        '''
        raise NotImplementedError

    @abc.abstractmethod
    def shutdown(self, checkpointer, reason):
        '''
        Called by a KCLProcess instance to indicate that this record processor should shutdown. After this is called,
        there will be no more calls to any other methods of this record processor.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.

        :type reason: str
        :param reason: The reason this record processor is being shutdown, either TERMINATE or ZOMBIE. If ZOMBIE,
            clients should not checkpoint because there is possibly another record processor which has acquired the lease
            for this shard. If TERMINATE then checkpointer.checkpoint() should be called to checkpoint at the end of the
            shard so that this processor will be shutdown and new processor(s) will be created to for the child(ren) of
            this shard.
        '''
        raise NotImplementedError

    def shutdown_requested(self, checkpointer):
        """
        Called by a KCLProcess instance to indicate that this record processor is about to be be shutdown.  This gives
        the record processor a chance to checkpoint, before the lease is terminated.

        :type checkpointer: amazon_kclpy.kcl.Checkpointer
        :param checkpointer: A checkpointer which accepts a sequence number or no parameters.
        """
        pass

    version = 1

class KVCLProcess(object):
  def __init__(self, frame_processor, stream_name, endpoint):
    self.processor = frame_processor
    self.kvs_client = boto3.client('kinesis-video-media', endpoint_url=endpoint)
    self.stream_name = stream_name

  def run(self):
    counter = 0
    response = self.kvs_client.get_media(
        StreamName=self.stream_name,
        StartSelector={
            'StartSelectorType': 'NOW'
        }
    )

    iterchunks = response['Payload'].iter_chunks()
    first_chunk = next(iterchunks)
    chunk = BitArray(first_chunk)

    for i in iterchunks:
        a = BitArray(i)
        pos = a.find('0x1a45dfa3')
        if pos:
            chunk.append(a[:pos[0]])
            f = tempfile.NamedTemporaryFile(suffix='.mkv')
            print(f.name)
            f.write(chunk.tobytes())
            videogen = skvideo.io.vreader(f.name)
            for frame in videogen:
                if counter % 20 == 1:
                    self.processor.process_frame(frame)
            chunk = a[pos[0]:]
        else:
            chunk.append(a)
        counter += 1