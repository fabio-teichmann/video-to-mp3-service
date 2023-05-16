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

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)