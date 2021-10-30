FROM public.ecr.aws/amazonlinux/amazonlinux:2

USER root

ENV LC_ALL=en_US.utf8 LANG=en_US.utf8 PYCURL_SSL_LIBRARY=nss SHELL_PLUS=ipython IPYTHONDIR=/etc/ipython LOGGING_MODE=print

RUN amazon-linux-extras install nginx1 rust1 python3.8 && \
    yum -y update && \
    yum -y install \
        gcc \
        glibc-locale-source \
        glibc-langpack-en \
        git \
        libcurl-devel \
        openssl-devel \
        # Even though we don't always use Apache in these apps, mod_ssl installs certs that we need.
        mod_ssl \
        # We need these mysql packages for python to be able to connect yo mysql, and for `manage.py dbshell` to work.
        mysql-devel \
        mysql \
        # Python3.8 packages necessary for building wheels
        python38-devel \
        python38-wheel \
        # Upgrading SQLite3 to 3.33.0
        sqlite-3.14.2-1.fc25.x86_64.rpm \
        sqlite-devel-3.14.2-1.fc25.x86_64.rpm \
        sqlite-libs-3.14.2-1.fc25.x86_64.rpm \
        # Useful unix utilities that don't come with the base CentOS 7 image.
        hostname \
        procps \
        psmisc \
        procps-ng \
        which \
    # Cleanup for yum, as suggested by yum itself.
    && yum -y clean all && \
    rm -rf /var/cache/yum && \
    # Set up the UTF-8 locale so that shelling into the container won't spam you with locale errors.
    localedef -i en_US -f UTF-8 en_US.UTF-8 && \
    # Install supervisor globally
    pip3.8 install supervisor && \
    # Create the virtualenv. Note that we NEED to use `python3.8`, here, since `python` is currently py2.7. Once we set
    # up the PATH on the next command, `python` becomes py3.8.
    /usr/bin/python3.8 -m venv /ve && \
    # Add the user under which gunicorn will run.
    adduser -r gunicorn && \
    # Set the container's timezone to Los Angeles time.
    rm -rf /etc/localtime && \
    ln -s /usr/share/zoneinfo/America/Los_Angeles /etc/localtime


# Ensure that we run the pip and python that are in the virtualenv, rather than the system copies.
ENV PATH /ve/bin:$PATH

# Install the latest pip and our dependencies into the virtualenv.  We do this before copying the codebase so that minor
# code changes don't force a rebuild of the entire virtualenv.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --upgrade pip wheel && \
    pip install -r /tmp/requirements.txt && \
    # Purge the pip cache, which can save us a good few megabytes in the docker image.
    rm -rf $(pip cache dir)

# Expose the app's communication port.
EXPOSE 8443

# Copy the code into the image. The .dockerignore file determines what gets left out of this operation. This step will
# always invalidate the docker build cache, so it's done as late as possible to make sure the fewest number of steps
# must be repeated on each build of the image.
COPY . /app
WORKDIR /app

# Install our app into the ve, symlink static resources, settings files, certs into place, etc.
RUN pip install -e . && \
    # precompile the sass files
    python manage.py compilescss  --settings=seedling.settings_docker -v0 --skip-checks  && \
    # Run collectstatic to symlink all the static files into /static, which is where the webserver expects them.
    python manage.py collectstatic --settings=seedling.settings_docker --noinput -v0 && \
    chown -R gunicorn:nginx /static && \
    # Uncomment this if your project requires internationalization.
    # python manage.py compilemessages --settings=seedling.settings_docker && \
    # generate the default certs
    /usr/libexec/httpd-ssl-gencerts && \
    # Create an iPython profile and then replace the default config with our own, which enables automatic code reload.
    ipython profile create && \
    ln -fs /app/etc/ipython_config.py /etc/ipython/profile_default/ipython_config.py

CMD ["/usr/local/bin/supervisord", "-c", "/app/etc/supervisord.conf"]
