#!/bin/bash

# This script has various configuration flags for tcapy which need to be set
# It is unlikely you'll need to change many of these (except possibly the folder where tcapy resides)

echo "Setting environment variables for tcapy for current script (recommended to add these globally to /etc/environment)"

## Python environment settings #########################################################################################

# Folder where tcapy is (note: if you will need to change this in tcapy/conf/mongo.conf too)
export TCAPY_CUEMACRO=/home/$USER/cuemacro/tcapy

# Is the Python environment either "conda" or "virtualenv"?
export TCAPY_PYTHON_ENV_TYPE="conda"
# export TCAPY_PYTHON_ENV=/home/$USER/py36tca/ # virtualenv folder or conda name
export TCAPY_PYTHON_ENV=py36tca # virtualenv folder or conda name
export TCAPY_PYTHON_ENV_BIN=$TCAPY_PYTHON_ENV/bin/
export TCAPY_PYTHON_VERSION=3 # Only Python 3 is now supported

export CONDA_ACTIVATE=/home/tcapyuser/anaconda3/bin/activate

export TCAPY_USER=$USER # which user to run tcapy

# Add Anaconda to the path (you might need to change this)
# export PATH=~/anaconda3/bin:$PATH

## Web server settings #################################################################################################

# Can use gunicorn with either apache or nginx (mod_wsgi can only be used with apache and is depreciated)
# recommended to use gunicorn with nginx
export TCAPY_PYTHON_STARTER='gunicorn' # 'gunicorn' ('mod_wsgi' is deprecated)
export TCAPY_WEB_SERVER="nginx" # apache or nginx

# Start other web interfaces? (we always start the default tcapy web interface server)
# but we can also add other interfaces if we want
export START_TCAPY_API=1        # Start Gunicorn RESTful API
export START_TCAPY_BOARD=1      # Start Gunicorn tcapyboard web front-end

## Get Linux distribution ##############################################################################################

# Determine OS distribution
case "`/usr/bin/lsb_release -si`" in
  Ubuntu) export DISTRO="ubuntu" ;;
       *) export DISTRO="redhat"
esac

