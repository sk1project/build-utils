FROM centos:8
MAINTAINER sk1.project.org@gmail.com

RUN yum -y update && yum clean all
RUN yum -y install gcc rpmdevtools lcms2-devel python3 python3-devel gettext && yum clean all

CMD ["/vagrant/bbox.py"]