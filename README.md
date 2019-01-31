# AWE: a Workflow Environment

Goal of project: To build infrastructure on top
of an existing workflow engine ([Cromwell](https://cromwell.readthedocs.io/en/stable/)) to make it simple for researchers to quickly use.

## Background:

Cromwell can be run on the command line or as a RESTful server.
However, it is not meant to be used in a multi-user environment (it has no notion of users and no authentication/authorization). This project would enable multiple users
to use Cromwell.

## Features

* Authenticate with HutchNet ID/Password (against Azure AD).  Status: Not implemented (there are people in HDC who know how to do this)
* Pull workflow source, input json, etc., directly from GitHub. Status: partially implemented
* At the end of a successful workflow, remove intermediate files and place output files in a desired location. Status: not implemented, lower priority.
* CloudFormation or Terraform templates/scripts to set up a new AWS account for use with AWE. Status: not implemented
* CloudFormation or Terraform templates/scripts to onboard a new user to AWE. Status: not implemented, currently doing manual onboarding.
* Different back ends - choose to submit workflow to Slurm. Status: Not implemented, lower priority.

## Requirements

* Ability to identify users (at least at the level of groups/labs) who
  are running AWS Batch jobs, for billing/accounting purposes. Not possible if all users use the same Batch compute environment. (This will be less of an issue when all groups have their own AWS account).
* Users should not be able to do anything in AWE that they
  don't have permission to do as themselves. Data and job output
  should be written to a bucket that users have access to, 
  and user A should not be able to see user B's data or job output.


## Architecture

![Architecture diagram](AWE_diagram.png)


### Components

* Server. Runs in AWS Lambda and is accessible through API Gateway. Recommend using [Zappa](https://github.com/miserlou/Zappa) to develop a  [RESTful](https://flask-restful.readthedocs.io/en/latest/) [Flask](http://flask.pocoo.org/) application in Python which "lives" in Lambda.
* Fleet of Cromwell servers. Since Cromwell can't handle different users, each time a distinct user shows up, we need
to spin up a new Cromwell server for that user (if there isn't one already running). We'd like to respond to the user in a reasonable time so rather than starting the new server in AWS Batch, we thought we would start it in ECS. 
* AWS Batch Compute environment. When a user submits a job
  to Cromwell, Cromwell will run it in AWS Batch. This
  requires that some [CloudFormation stacks](https://docs.opendata.aws/genomics-workflows/aws-batch/configure-aws-batch-cfn/) be run in order to set up the AWS Account beforehand.
* Databases. Each instance of Cromwell (one for each user)
  needs to have its own database (MariaDB-compatible), presumably in RDS. Each time a user logs in who has not
  logged in before, we will need to create a database for them.

### Functionality



### Design goals

* Integration with Active Directory for authentication. 
  Ultimately we would like to hook up to Fred Hutch's
  AD (in Azure) but we can use a "fake" AD server for today.
*   


Workflow here is defined as a series of individual jobs that are part of a single procedure performed on a dataset, which are intended to be subject to the same version control.  The intent is to facilitate reproducible workflow jobs.  

## Assumptions

1. Workflow execution will be done using cromwell[1] and will happen on AWS Batch.
1. Workflow, config, and inputs will be in Git repos; inputs and reference data will be in S3 Buckets.
1. Each user will have separate IAM users in AWS child accounts of the Fred Hutch main AWS account.

## A base user experience for FH-AWE (Fred Hutch Adaptive Workflow Engine)

Pre-config: set up AWS Batch environment for Cromwell

1. The user starts a workflow by specifying the git repo URL of the workflow files.  
1. The user gets the status of any of their running or completed workflows.
1. The user cancels a running workflow.  

## What the backend needs to do

All requests must be authenticated with Active Directory.

* Create workflow
    * persistent store user, name, git repo of workflow
    * persistent store job definition as related to named workflow
* Start workflow job
    * execute cromwell on AWS Batch (probably a cromwell workflow job that then launches the individual jobs?)
    * update persistent state (cromwell may do this)
* Job Status
    * retrieve (workflow?) job metadata from persistent state
* Cancel job
    * retrieve data from persistent state to verify job state
    * halt job in AWS Batch/cromwell

 ## Bonus features!
 1. Search including all named components as well as inputs and outputs.
 1. Self-service configurable notifications.
 1. Job visualizations (from cromwell and above cromwell).
 1. Non-environment AWS credentials for future UI use.

## Cromwell notes
Cromwell can use a MySQL database for job metadata.
Cromwell is single-user.

## Likely AWS Services

* Lambda
* [a persistent state solution - MySQL compatible]
* S3
* AWS Batch

## API

* `POST /<user>/<workflowid>`
   * start user's workflow with label = workflowid
   * formdata includes workflow git repo, additional user-defined labels
   * returns 200 or error if discovered quickly

* `DELETE /<user>/<workflowid>`
   * abort user's workflowid
   * returns cromwell abort return codes
   
* `GET /<user>/<workflowid>/<cromwell API call>`
   * look up cromwell workflowid by label from URL, then proxy API call to user's cromwell instance
   
Examples (yes, the GET example is not AWEsome):
```
POST /bmcgough/kallisto_20181205 '{ "workflow_repo": "http://github.com/FredHutch/AWE-kallisto", "label": "data from bob" }'
DELETE /bmcgough/kallisto_20181205
GET /bmcgough/kallisto_20181205/api/workflows/{version}/kallisto_20181205/status
```

1. *Why Cromwell?*
Their logo for one:

   ![CR0M-w311](https://github.com/broadinstitute/cromwell/raw/develop/docs/jamie_the_cromwell_pig.png)
