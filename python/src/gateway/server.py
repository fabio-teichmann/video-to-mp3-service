import os 
import gridfs
import pika 
import json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos" #default mongo db port

# Wrapper to flask
mongo = PyMongo(server)

# Wrapper to mongo db
# GridFS shards data beyond the 16MB file size limit
# that Mongo.db imposes.
fs = gridfs.GridFS(mongo.db)

# reference host for gateway queue
connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    # communicate with auth service to log user in
    # and assign token to user
    token, err = access.login(request)

    if not err:
        return token
    else:
        return err
    

@server.route("/upload", methods=["POST"])
def upload():
    access, err = validate.token(request)
    if err:
        return "invalid credentials", 401

    access = json.loads(access)

    if access["admin"]:
        if len(request.files) != 1:
            return "exactly 1 file required", 400
        
        for _, file in request.files.items():
            err = util.upload(file, fs, channel, access)

            if err:
                return err
            
        return "success", 200
    
    else:
        # user is not authorized
        return "not authorized", 401
    

@server.route("/download", methods=["GET"])
def download():
    pass

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)