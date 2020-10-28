FROM ubuntu:20.04
MAINTAINER sk1.project.org@gmail.com

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Dubai
RUN apt-get update && apt-get install -y tzdata gcc sudo libcairo2-dev liblcms2-dev libmagickwand-dev libpango1.0-dev python2 python2-dev python-cairo-dev python3 python3-dev gettext libcups2-dev && apt-get clean
RUN curl https://bootstrap.pypa.io/get-pip.py --output get-pip.py && python2 get-pip.py

CMD ["/vagrant/bbox.py"]
