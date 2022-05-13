FROM centos:7.8.2003

RUN yum install -y git unzip wget python3 pip3
RUN pip3 install pytest

WORKDIR /pytester
#FROM python:3.7-alpine
#RUN apk add bash vim git build-base libffi-dev openssl-dev python3-dev curl openssh-client

COPY ./ /pytester/

#RUN pip install -r requirements.txt
RUN pip3 install -r pytest.req.txt

CMD ["/bin/bash","/pytester/entrypoint.sh" ]

# docker build --network host -t applcmctrl_test:latest -f Dockerfile.preci ./
# docker run -it e2etester bash
# // into e2etester docker container bash

# bash-5.0 # pytest -m dpagent --ip_address 10.60.6.26 -s -vv --html=/test/2.htm --self-contained-html junit-xml=pytest_r3_e2e.xml
# docker run --network openness_default applcmctrl_test:latest

