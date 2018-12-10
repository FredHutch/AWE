# Rethinking architecture...

Goals:

1. All state in cromwell database and object names/tags/labels.
1. No always-running products.

Cloud pieces for each user:

* cromwell database - database used by cromwell server (Aurora Serverless)
* cromwell container instance - runs cromwell server (Fargate)

Cloud pieces shared:

* AWS Batch compute environment (AWS Batch)
* cromwell container
* microservices (Lambda)

States of user's cromwell line up with AWS ECS states - RUNNING, STOPPED, PENDING
  
Client actions:

* send cromwell API call
* get user cromwell state (+details?)
* set user cromwell state (let users shut themselves down?)

The basic client flow:

  * for cromwell API requests:
    ```
    while user cromwell state is not RUNNING:
      send request to set state to RUNNING
    proxy request to cromwell
    ```
  * for non-cromwell API requests:
    ```
    return from lambda directly
    ```
    
Microservice approach:

* API Gateway to map/proxy client requests
* Lambda function `get_state` returns state for cromwell user derived from examining deterministic database and cromwell container
* Lambda function `set_state` returns success/fail of immediate call (not confirmation of state change)
* CloudWatch schedule to run lamda `get_state` and shut down user cromwell if applicable
