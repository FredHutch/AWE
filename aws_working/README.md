# Working on AWS

Current state:

AWS:
1. create aurora serverless DB and call it 'cromwelldb-<username>'
1. create ECS Fargate cluster (done, called `FH-AWE`)
1. create ECS task definition for user and call it `fh-awe-<username>`
1. create ECS service in cluster above for user and call it `fh-awe-svc-<username>`

Local:
1. install requirements.txt
1. [run `export AWS_PROFILE=<profile>` to set profile]
1. run `flask run`
1. run `curl -H "fh-awe-user: bmcgough" http://127.0.0.1:5000`

Notes:

I did test this flask app with zappa and it does deploy and is callable.

The resource names are slightly different for my resources; I didn't want to re-create them all. We should normalize the resources names and change the Flask app accordingly.

I am trying to keep this generic to be able to run other containers on demand. To that end, we will need to parameterize the ECS cluster name as that is not in the user request (task defnintion environment variable?)

I cannot test the proxy as for some reason my task status does not match up with what I am seeing in the console???

Also, the Requirements.txt is probably too big.
