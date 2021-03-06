FROM centos:7

MAINTAINER Chris Malek <cmalek@placodermi.org>

USER root

WORKDIR /etc
RUN rm -rf localtime && ln -s /usr/share/zoneinfo/America/Los_Angeles localtime
ENV LC_ALL=en_US.utf8 LANG=en_US.utf8 PYCURL_SSL_LIBRARY=nss
ENV PYTHONUNBUFFERED 1

# Install all the system dependencies via yum.
RUN yum -y install epel-release && \
    yum -y makecache fast && \
    yum -y update && \
    yum -y install \
        gcc \
        git \
        libjpeg-turbo-devel \
        openssl-devel \
        libffi-devel \
        libxslt-devel \
        libxml2-devel \
        httpd \
        mod_ssl \
        mysql \
        mysql-devel \
        supervisor \
        # Python 3.6 comes in CentOS 7's standard yum repo, now.
        python3 \
        python3-devel \
        python3-pip \
        # Useful unix utilities that don't come with the base CentOS 7 image.
        psmisc \
        which \
    && yum -y clean all && \
    # Set up the UTF-8 locale so that shelling into the container won't spam you with locale errors.
    localedef -i en_US -f UTF-8 en_US.UTF-8 && \
    # Create the venv for the app's environment to live it.
    python3 -m venv /ve && \
    # Add the user under which gunicorn will run.
    adduser -r gunicorn

# Ensure that we run the pip and python that are in the virtualenv, rather than the system copies.
ENV PATH /ve/bin:$PATH

# Install the latest pip and our dependencies into the virtualenv.  We do this before copying the codebase so that minor
# code changes don't force a rebuild of the entire virtualenv.
COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt

# Expose the ports we configure Apache to listen on.
EXPOSE 80 443 

# Copy the code into the image. The .dockerignore file determines what gets left out of this operation.
# This step will always invalidate its cache, so it's done as late as possible to make sure the fewest number of steps
# must be repeated on each build of the image.
COPY . /app
WORKDIR /app

# Install the app itself into the virtualenv, along with several other things.
RUN pip install -e . && \
    mkdir /static && \
    # Run collectstatic to symlink all the static files into /static, which is where the webserver expects them.
    ./manage.py collectstatic --settings=config.settings_docker --noinput -v0 -i node_modules --link && \
    # Copy/create/delete various config files and folders.
    cp etc/supervisord.conf /etc/supervisord.conf && \
    cp etc/apache/httpd.conf /etc/httpd/conf/httpd.conf && \
    cp etc/apache/ssl.conf /etc/httpd/conf.d/ssl.conf && \
    cp etc/apache/app.conf /etc/httpd/conf.d/app.conf && \
    cp etc/apache/status.html /var/www/html/status.html && \
    rm /etc/httpd/conf.d/welcome.conf && \
    mkdir /certs && \
    cp /etc/pki/tls/private/localhost.key /certs && \
    cp /etc/pki/tls/certs/localhost.crt /certs && \
    chmod a+r /certs/*

CMD ["/usr/bin/supervisord"]
