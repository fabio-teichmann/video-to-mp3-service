import pika, json

def upload(file, fs, channel, access):
    """This functions fulfills the following tasks:
    
    1. upload file to Mongo DB
    2. put message on RabbitMQ so that downstream services get notified and can process
    3. create asynchronous gateway service between user upload and response
    """
    try:
        file_id = fs.put(file)
    except:
        return "internal server error", 500
    
    message = {
        "video_file_id": str(file_id),
        "mp3_file_id": None, # set downstream
        "username": access["username"]
    }

    try:
        channel.basic.publish(
            exchange="", # default exchange
            routing_key="video", # name of the queue
            body=json.dumps(message),
            properties=pika.BaseicProperties(
                # Make sure that messages are persistet (conserved)
                # in case a pod crashes and needs to restart. Makes
                # messages durable.
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),
        )
    except:
        # delete file in Mondo DB
        fs.delete(file_id)
        return "internal server error", 500