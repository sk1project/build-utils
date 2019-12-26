FROM opensuse/leap:15.1
MAINTAINER sk1.project.org@gmail.com

RUN zypper -n refresh && zypper -n update && zypper -n clean
RUN zypper -n install gcc rpm-build cairo-devel liblcms2-devel ImageMagick-devel pango-devel python-devel python-cairo-devel python3 python3-devel gettext && zypper -n clean
 
CMD ["/vagrant/bbox.py"]
