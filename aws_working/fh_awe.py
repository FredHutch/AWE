from flask import Flask, Response, request
from flask_restful import Resource, Api

import requests
import boto3


app = Flask(__name__)
api = Api(app)


class CromwellProxyServer(Resource):
    def post(self):
        # call me like this:
        # curl -X POST http://localhost:8000/api/workflows/v1 -H "accept: application/json" -H "Content-Type: multipart/form-data"   -F "workflowSource=$(curl --silent https://raw.githubusercontent.com/FredHutch/reproducible-workflows/master/WDL/hello/hello.wdl)"
        github_repo = request.form["githubRepo"]
        workflow_source = request.form["workflowSource"]
        # TODO get (optional) input file and other params
        # TODO get username
        # TODO allow support for (non-master) branches in a TBD way
        workflow_url = _get_github_url(github_repo, workflow_source)
        cromwell_base_url = _get_cromwell_base_url()
        version = _get_version()

        url = "{}/api/workflows/{}".format(cromwell_base_url, version)
        # url = "{}/post".format(cromwell_base_url)
        # FIXME use workflowUrl instead of this (and put in data, not files):
        workflow = requests.get(workflow_url).text

        resp = requests.post(
            url,
            files=[("workflowSource", workflow)],
            # data={"workflowSource": workflow},
            headers={
                "accept": "application/json",
                # "Content-Type": "multipart/form-data",
                # "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        # import IPython

        # IPython.embed()

        return {"status": "ok"}


api.add_resource(CromwellProxyServer, "/")


def _get_version():
    # TODO maybe do something dynamic in future
    return "v1"


def _get_cromwell_base_url():
    # TODO really figure it out
    return "http://localhost:8000"
    # return "http://localhost:9000"  # httpbin


def _slashjoin(args):
    """
    make sure all arguments are joined
    by a single slash, removing leading/trailing
    slashes from args if necessary
    """
    fixed_args = [x.lstrip("/").rstrip("/") for x in args]
    return "/".join(fixed_args)


def _get_github_url(repo, filename):  # TODO accept branch arg
    url = _slashjoin([repo, "master", filename])  # TODO be branch-aware
    return url.replace("github.com", "raw.githubusercontent.com")


def _get_username():
    # validate user
    if "fh-awe-user" in request.headers:
        username = request.headers.get("fh-awe-user")
        print("found username: " + username)
        return username
    return None


def _get_db_status(username):
    # return db status for user
    rds = boto3.client("rds")
    print("checking db status for " + username)
    try:
        db = rds.describe_db_clusters(DBClusterIdentifier="bmcgough-aurora-cluster")
    except:
        return None
    db_status = db["DBClusters"][0]["Status"]
    print("found db_status: " + db_status)
    return db_status


def _get_task_definition_status(username):
    # return status of container task definition for user
    ecs = boto3.client("ecs")
    try:
        task = ecs.describe_task_definition(taskDefinition="fh-awe-" + username)
    except:
        return None
    return task["taskDefinition"]["status"]


def _get_service_status(username):
    # return the status of the user's task service
    ecs = boto3.client("ecs")
    try:
        svc = ecs.describe_services(
            cluster="FH-AWE", services=["fh-awe-" + username + "-svc"]
        )
    except:
        return None
    return svc["services"][0]["status"]


def _get_task_status(username):
    # return the status of the user's task
    ecs = boto3.client("ecs")
    try:
        task_list = ecs.list_tasks(
            cluster="FH-AWE", serviceName="fh-awe-" + username + "svc"
        )
    except:
        return None
    task_arn = task_list["taskArns"][0]
    try:
        task = ecs.describe_tasks(cluster="FH-AWE", tasks=[task_arn])
    except:
        return None
    desired_status = task["tasks"][0]["desiredStatus"]
    last_status = task["tasks"][0]["lastStatus"]
    if desired_status == last_status:
        return last_status
    return None


def _proxy(*args, **kwargs):
    # proxy request to running service container
    resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, "new-domain.com"),
        headers={key: value for (key, value) in request.headers if key != "Host"},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False,
    )

    excluded_headers = [
        "content-encoding",
        "content-length",
        "transfer-encoding",
        "connection",
    ]
    headers = [
        (name, value)
        for (name, value) in resp.raw.headers.items()
        if name.lower() not in excluded_headers
    ]

    response = Response(resp.content, resp.status_code, headers)
    return response


# @app.route("/")
# def main():
#     username = _get_username()
#     if username is None:
#         return "username not found\n"
#     db_status = _get_db_status(username)
#     if db_status is None:
#         return "database for " + username + " does not exist!\n"
#     task_definition_status = _get_task_definition_status(username)
#     if task_definition_status is None:
#         return "container task not defined for " + username + "!\n"
#     service_status = _get_service_status(username)
#     if service_status is None:
#         return "service not defined for " + username + "!\n"
#     task_status = _get_task_status(username)
#     if task_status is None:
#         return "task for " + username + " is not running!\n"
#     # proxy here!

if __name__ == "__main__":
    app.run(debug=True)
