import pika, json, tempfile, os 
from bson.objectid import ObjectId
import moviepy.editor

def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message)

    # empty temp file
    tf = tempfile.NamedTemporaryFile()
    # video contents
    # get video file from mongodb
    out = fs_videos.get(ObjectId(message["video_file_id"]))
    # add video contents to empty file
    tf.write(out.read())
    # create audio from temp video file
    audio = moviepy.editor.VideoFileClip(tf.name).audio
    tf.close()

    # write audio to file
    tf_path = tempfile.gettempdir() + f"/{message['video_file_id']}.mp3"
    audio.write_audiofile(tf_path)

    # save file to mongodb
    # reopen file
    f = open(tf_path, "rb")
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    # manually remove temporary file
    os.remove(tf_path)

    # update message with fid received from mongodb
    message["mp3_file_id"] = str(fid)

    # put message on mp3-queue
    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTEN_DELIVERY_MODE
            ),
        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to publish message"