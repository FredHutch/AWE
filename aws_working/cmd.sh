#!/bin/sh

aws s3 cp "s3://fh-awe-config/$CROMWELL_USER/aws.conf" . 

java  -Dconfig.file=aws.conf -jar /app/cromwell.jar server

