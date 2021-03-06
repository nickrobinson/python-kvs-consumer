# Python Kinesis Video Streams Consumer

## Setup
### Create a Ramdisk
In order to accelerate the processing of chunks as much as possible, each new chunk is written out to a Ramdisk for processing.

To create a local Ramdisk run ```./ramdisk.sh create 30```

### Install dependencies
```pip install -r requirements.txt```

### Execute Consumer
```python3 consumer.py  --endpoint <KINESIS_VIDEO_ENDPOINT> --stream <STREAM_NAME>```

Note: Your Kinesis Video Endpoint can be retrieved by running ```aws kinesisvideo get-data-endpoint --api-name GET_MEDIA --stream-name <STREAM_NAME>```
