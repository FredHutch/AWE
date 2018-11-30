# Workflow Manager Project for hackathon
Workflow here is defined as a series of individual jobs that are part of a single procedure performed on a dataset, which is intended to be subject to the same version control.  The intent is to facilitate reproducible workflow jobs.  

## Assumptions

1. Workflow execution will be done using cromwell and will happen on AWS Batch.
1. All source and reference data will be in S3 Buckets.
1. Each user will have separate AWS child accounts.
1. Workflow and inputs will be in GitHub repos. Allow for those repo's to be private.

## A base user experience for FH-AWE (Fred Hutch Adaptive Workflow Engine)

1. The user creates a workflow definition, defines inputs, and pushes to GitHub.
1. The user starts one workflow job (or an array of them?).  
1. The user gets the status of any of their running or completed workflow jobs.
1. The user cancels a running workflow job.
1. The user receives workflow job failure information and restarts workflow job.  

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

## Cromwell notes
Cromwell can use a MySQL database for job metadata.
Cromwell is single-user.

## Likely AWS Services

* Lambda
* [a persistent state solution - MySQL compatible]
* S3
* AWS Batch

## API
URL structure `/workflow/job/jobid/action`

Return values are HTTP status unless otherwise specified.

* `workflow`
    * this is a name for the workflow
    * `PUT` - add named workflow to persistent state
        * requires URL of workflow git repo
    * `DELETE` - removes named workflow and related job definitions
    * `GET` - returns named workflow metadata
* `job`
    * this is a job definition
    * `PUT` - add named job definition to workflow
        * requires input/output/config
    * `DELETE` - removes named job definition
    * `GET` - returns job definition metadata
* `jobid`
    * this is a specific run or instance of a job definition
    * `PUT` - execute the named job definition, optionally supplying a jobid
        * returns jobid in body
    * `DELETE` - halt the exection of the named jobid
    * `GET` - return the status of the named jobid
        * returns status info in body

Examples:
```
PUT /kallisto '{ "workflow_repo": "http://github.com/FredHutch/workflow-management-hackathon" }'
PUT /kallisto/july2018 '{ <some input/output/config info here>}'
PUT /kallisto/july2018/first_run
GET /kallisto/july2018/first_run
```
