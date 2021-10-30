# Seedling

This access.caltech Django application ...

INSERT REASONABLE DESCRIPTION OF THIS APPLICATION HERE

## Operations

### Working with the AWS infrastructure for Seedling

We're using terraform workspaces, and whatever is the latest version of terraform-0.12.  Here's how you set up to work with
the terraform templates in this repository:

```
cd terraform
chtf __LATEST_VERSION__
terraform init --upgrade
terraform workspace select test
```

Now when you run `terraform plan` and `terraform apply`, you will be working only with the `test` environment.
To work with the prod environment, do

```
terraform workspace select prod
``` 

To list the available environments, do:

```
terraform workspace list
```

### Configs for the cloud

The ADS KeePass has the /etc/context.d .env files needed for running the
`deploy config` commands.  They're named for the service, and are under
"deployfish .env files".

### Logs for the cloud

The logs for the test and prod servers end up of course in the ADS ELK stack:
http://ads-logs.cloud.caltech.edu/_plugin/kibana/.  They will both have the
"application" set to "seedling".  

A good way to search Kibana for those all relevant logs for the test server is:

```
application:"seedling" AND environment:test AND NOT message:HealthChecker
```

A good way to search Kibana for those all relevant logs for the prod server is:

```
application:"seedling" AND environment:prod AND NOT message:HealthChecker
```

These both say "give me the logs from our service but leave out all the spam from
the ALB running its health checks on the service."

## Contributing to the code of Seedling

## Set up your local virtualenv

The Amazon Linux 2 base image we use here has Python 3.7.6, so we'll want that in our virtualenv.

```
git clone git@bitbucket.org:caltech-imss-ads/seedling.git
cd seedling
pyenv virtualenv 3.7.6 seedling
pyenv local seedling
pip install --upgrade pip
pip install -r requirements.txt
```

If you don't have a `pyenv` python 3.7.6 built, build it like so:

```
pyenv install 3.7.6
```

### Prepare the docker environment

Now copy in the Docker environment file to the appropriate place on your Mac:

```
cp etc/environment.txt /etc/context.d/seedling.env
```

Edit `/etc/context.d/seedling.env` and set the following things:

* `AWS_ACCESS_KEY_ID`: set this to your own `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`: set this to your own `AWS_SECRET_ACCESS_KEY`

### Build the Docker image

```
make build
```

### Run the service, and initialize the database

```
make dev-detached
make exec
> ./manage.py migrate
```

### Getting to the service in your browser

Since Seedling is meant to run behind the access.caltech proxy servers, you'll need to supply the
access.caltech HTTP Request headers in order for it to work correctly. You'll need to use something
like Firefox's Modify Headers or Chrome's [ModHeader](https://bewisse.com/modheader/) plugin so that you can set the appropriate HTTP Headers. 

Set the following Request headers:

* `User` to your access.caltech username
* `SM_USER` to your access.caltech username
* `CAPCaltechUID` to your Caltech UID,
* `user_mail` to your e-mail address
* `user_first_name` to your first name
* `user_last_name` to your last name

You should now be able to browse to https://localhost:8443/seedling .
