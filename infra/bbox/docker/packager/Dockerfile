FROM ubuntu:16.04
MAINTAINER sk1.project.org@gmail.com

RUN apt-get update && apt-get install -y gcc sudo python-dev python-gi \
gir1.2-glib-2.0 gir1.2-libmsi0 gir1.2-libgcab-1.0 python-pip hfsprogs \
genisoimage libxml2-dev libssl-dev && pip install WiX.Py && apt-get clean

COPY utils-src/bomutils/bomutils-0.2.tar.gz bomutils-0.2.tar.gz
RUN tar -xzf bomutils-0.2.tar.gz && \
cd bomutils-0.2 && make && make install && cd .. && rm -rf bomutils-0.2

COPY utils-src/xar/xar-1.5.2.tar.gz xar-1.5.2.tar.gz
RUN tar -xzf xar-1.5.2.tar.gz && cd xar-1.5.2 && \
./configure && make && make install && cd .. && rm -rf xar-1.5.2

CMD ["/vagrant/bbox.py", "packaging"]
