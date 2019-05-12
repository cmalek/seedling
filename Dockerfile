FROM centos:7

MAINTAINER Chris Malek <cmalek@placodermi.org>

USER root

WORKDIR /etc
RUN rm -rf localtime && ln -s /usr/share/zoneinfo/America/Los_Angeles localtime
ENV LC_ALL en_US.UTF-8

# Install all the system dependencies via yum.
RUN yum -y install epel-release && \
    yum -y install https://centos7.iuscommunity.org/ius-release.rpm && \
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
        ImageMagick-devel \
        httpd \
        mod_ssl \
        mysql \
        mysql-devel \
        supervisor \
        # These python36u packages come from the ius-release repo, which we install above.
        python36u \
        python36u-devel \
        python36u-pip \
        # Useful unix utilities that don't come with the base CentOS 7 image.
        psmisc \
        which \
    && yum -y clean all && \
    # Add symlinks for python3.6/pip3.6 to just python3/pip3. These won't be needed under most circumstances, due to the
    # ENV line that we run next. I added them just to stay consistent with other ADS Dockerfiles.
    ln -s /usr/bin/python3.6 /usr/bin/python3 && \
    ln -s /usr/bin/pip3.6 /usr/bin/pip3 && \
    # Set up the UTF-8 locale so that shelling into the container won't spam you with locale errors.
    localedef -i en_US -f UTF-8 en_US.UTF-8 && \
    # Create the venv for seedling's environment to live it.
    python3 -m venv /seedling-ve && \
    # Add the user under which gunicorn will run.
    adduser -r gunicorn

# Ensure that we run the pip and python that are in the virtualenv, rather than the system copies.
ENV PATH /seedling-ve/bin:$PATH

# Install the latest pip and seedling's dependencies into the virtualenv.
# We do this before copying the codebase so that minor code changes don't force a rebuild of the entire virtualenv.
COPY requirements.txt /tmp/requirements.txt

RUN pip install --upgrade pip && \
    pip install -r /tmp/requirements.txt && \
    rm -rf /tmp/dependencies

# Expose the ports we configure Apache to listen on.
EXPOSE 80 443 

# Copy the code into the image. The .dockerignore file determines what gets left out of this operation.
# This step will always invalidate its cache, so it's done as late as possible to make sure the fewest number of steps
# must be repeated on each build of the image.
COPY . /seedling
WORKDIR /seedling

# Install seedling itself into the virtualenv, along with several other things.
RUN pip install -e . && \
    # Run collectstatic to symlink all the static files into /static, which is where the webserver expects them.
    ./manage.py collectstatic --settings=seedling.settings.docker_build --noinput -v0 -i node_modules --link && \
    # Copy/create/delete various config files and folders.
    cp bin/entrypoint.sh /entrypoint.sh && \
    cp etc/docker/supervisord.conf /etc/supervisord.conf && \
    cp etc/docker/apache/httpd.conf /etc/httpd/conf/httpd.conf && \
    cp etc/docker/apache/ssl.conf /etc/httpd/conf.d/ssl.conf && \
    cp etc/docker/apache/seedling.conf /etc/httpd/conf.d/seedling.conf && \
    cp etc/docker/apache/status.html /var/www/html/status.html && \
    rm /etc/httpd/conf.d/welcome.conf && \
    mkdir /seedling_certs && \
    cp /etc/pki/tls/private/localhost.key /seedling_certs && \
    cp /etc/pki/tls/certs/localhost.crt /seedling_certs && \
    chmod a+r /seedling_certs/*

ENTRYPOINT ["/seedling-ve/bin/deploy", "entrypoint"]
CMD ["/usr/bin/supervisord"]
