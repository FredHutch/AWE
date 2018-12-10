# FH-AWE Lambda function (our glue)

## Calls

* proxy cromwell API call
* get user cromwell state
* set user cromwell state
* create user cromwell
   
## Functions

* get_state(user) - wraps ECS call for "cromwell-username" task state
* set_state(user, desired state) - wraps ECS call to change "cromwell-username" task state
* create(user) - runs get_state then wraps calls to create ECS task definition (and database)
* proxy(user,API URL) - runs get_state then proxies request to "cromwell-username"
