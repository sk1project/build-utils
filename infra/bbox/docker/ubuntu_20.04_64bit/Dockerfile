FROM ubuntu:20.04
MAINTAINER sk1.project.org@gmail.com

RUN apt-get update && apt-get install -y gcc sudo libcairo2-dev liblcms2-dev libmagickwand-dev libpango1.0-dev python2 python2-dev python-cairo-dev python3 python3-dev gettext libcups2-dev && apt-get clean

CMD ["/vagrant/bbox.py"]
