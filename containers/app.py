#!/usr/bin/env python3

import io
import os
import time

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import psutil


import boto3
import sh
from hammock import Hammock as Cromwell

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()

def create_config_file(user, pi):
    with open("aws.conf.template") as infile:
        template = infile.read()
    pi_bucket = "fh-pi-{}".format(pi.replace("_", "-")) # handle div buckets
    conf = template.replace("%%HOSTNAME%%", os.getenv("HOST")).\
        replace("%%DATABASE_NAME%%", "cromwell_{}".format(user)).\
        replace("%%USERNAME%%", os.getenv("USERNAME")).\
        replace("%%PASSWORD%%", os.getenv("PASSWORD")).\
        replace("%%ACCOUNT_NUMBER%%", os.getenv("ACCOUNT_NUMBER")).\
        replace("%%ROLE_NAME%%", os.getenv("ROLE_NAME")).\
        replace("%%PI_BUCKET%%", pi_bucket).\
        replace("%%QUEUE_NAME%%", os.getenv("QUEUE_NAME"))
    with open("aws.conf", "w") as outfile:
        outfile.write(conf)
    

def create_database(user):
    dbname = "cromwell_{}".format(user)
    # TODO super insecure, fix

    # stupid hack
    with open("tmp.sh", "w") as script:
        script.write("#!/bin/bash\n\n")
        script.write("echo \"create database {}\" | mysql --host={} --password=\"{}\" --user={}\n".format(dbname, os.getenv("HOST"), os.getenv("PASSWORD"), os.getenv("USERNAME")))
    os.chmod("tmp.sh", 0o777)
    cmd = sh.Command("./tmp.sh")
    cmd()
    # FIXME why does this vvv not work?
    # sh.mysql(sh.echo("create database {};".format(dbname)), "--user=username", "--host=somehostname", '--password="fakepw"')
    os.remove("tmp.sh")

def does_database_exist(user):
    dbname = "cromwell_{}".format(user)

    # stupid hack
    with open("tmp2.sh", "w") as script:
        script.write("#!/bin/bash\n\n")
        script.write("echo \"show databases;\" | mysql --host={} --password=\"{}\" --user={}\n".format(os.getenv("HOST"), os.getenv("PASSWORD"), os.getenv("USERNAME")))
    os.chmod("tmp2.sh", 0o777)
    cmd = sh.Command("./tmp2.sh")
    out = io.StringIO()
    cmd(_out=out)
    os.remove("tmp2.sh")
    if dbname in out.getvalue():
        # could be improved about,
        # potential false positives
        return True
    return False


def is_cromwell_running():
    for proc in psutil.process_iter():
        if proc.name() == "java" and "cromwell-36.jar" in proc.cmdline():
            return True
    return False


def start_cromwell():
    sh.java("-Dconfig.file=aws.conf", "-jar", "cromwell-36.jar", "server", _bg=True,
            _out="cromwell.log", _err_to_out=True)
    count = 0
    while True:
        count += 1
        # TODO add timeout
        time.sleep(1)
        with open("cromwell.log") as logfile:
            log = logfile.read()
            if "service started on" in log:
                return
            if count > 120:
                raise ValueError("cromwell not started after 120 seconds")

def start_workflow(user):
    pass


class Test(Resource):
    def get(self):
        return request.path

    def post(self):
        args = parser.parse_args()
        return args
    

class CromwellRequestRouter(Resource):

    def get(self):
        return {'hello': 'world'}

    def post(self, user):
        "run new workflow"
        path = request.path
        segs = path.split("/")
        segs.pop(0) # get rid of username
        path = "/" + "/".join(segs)

        pi = request.headers['PI']
        if not does_database_exist(user):
            create_database(user)
        if not is_cromwell_running():
            create_config_file(user, pi)
            start_cromwell()
        
        # hardcoding....
        cromwell = Cromwell("http://localhost:8000")
        resp = cromwell.api.workflows.v1.POST()





api.add_resource(CromwellRequestRouter, '/<string:user>/api/workflows/v1')
api.add_resource(Test, "/")

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
    # FIXME make it run on port 80
    # app.run(debug=True, host="0.0.0.0", port="80")
