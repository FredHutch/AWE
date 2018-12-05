# FH-AWE: a Workflow Manager Project for hackathon
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
