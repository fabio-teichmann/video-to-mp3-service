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