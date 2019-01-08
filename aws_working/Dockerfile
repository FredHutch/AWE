# hmm, they don't have a 'latest'. we'll have to
# remember to update this once in a while.
FROM broadinstitute/cromwell:36


# build me as fredhutch/cromwell:latest

# run me like this locally:

# docker run -p 8000:8000 \
# -v $HOME/.aws:/root/.aws -e AWS_PROFILE=scicomp \ 
# -e CROMWELL_USER=dtenenba \
# --rm -v ~/.aws:/root/.aws fredhutch/cromwell

# (that won't work because we need to be in the vpc to 
# talk to the database)

ENTRYPOINT []

RUN curl --silent --show-error --retry 5 https://bootstrap.pypa.io/get-pip.py | python

RUN pip install awscli

ADD cmd.sh .

CMD "./cmd.sh"


