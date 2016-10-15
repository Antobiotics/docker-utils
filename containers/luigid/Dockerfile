FROM ubuntu:trusty

RUN apt-get update && apt-get install -y \
    libffi6 \
    libmysqlclient-dev \
    openssl \
    build-essential \
    pypy \
    python \
    python-dev \
    python-pip \
    python-virtualenv \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV LUIGI_HOME /opt/luigi

# Setup luigi's virtualenvironment
RUN virtualenv $LUIGI_HOME
RUN . $LUIGI_HOME/bin/activate; pip install pip==6.0.8

# Install luigis dependencies
RUN $LUIGI_HOME/bin/pip install luigi
RUN $LUIGI_HOME/bin/pip install SQLAlchemy==0.9.8
RUN $LUIGI_HOME/bin/pip install MySQL-python==1.2.5

RUN mkdir -p /opt/luigi
ADD client.cfg /opt/luigi/client.cfg

RUN mkdir -p /var/log/luigid
ADD logrotate.cfg /etc/logrotate.d/luigid
VOLUME /var/log/luigid

CMD $LUIGI_HOME/bin/luigid
EXPOSE 8082

