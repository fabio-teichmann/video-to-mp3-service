import os
import sys
import time

import gridfs
import pika
from convert import to_mp3
from pymongo import MongoClient


def main():
    client = MongoClient("host.minikube.internal", 27017)  # stored locally
    db_videos = client.videos
    db_mp3s = client.mp3s

    # gridfs
    fs_videos = gridfs.GridFS(db_videos)
    fs_mp3s = gridfs.GridFS(db_mp3s)

    # rabbitmq connection
    connection = pika.BlockingConnection(
        pika.ConnectionParamters(host="rabbitmq")  # service name
    )

    channel = connection.channel()

    def callback(channel, method, properties, body):
        err = to_mp3.start(body, fs_videos, fs_mp3s, channel)
        if err:
            # negative acknowledgement
            # keep message in the queue if issue with conversion
            channel.basic_nack(delivery_tag=method.delivery_tag)
        else:
            # positive acknowledgement
            channel.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(
        queue=os.environ.get("VIDEO_QUEUE"), on_message_callback=callback
    )

    print("waiting for messages. To exit press CTRL+C")

    channel.start_consuming()

    if __name__ == "__main__":
        try:
            main()
        except KeyboardInterrupt:
            # graceful shutdown
            print("interrupted")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
