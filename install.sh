#!/usr/bin/env bash
which -s brew
if [[ $? != 0 ]] ; then
    # Install Homebrew
    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
fi

brew install python
brew install mpg123
brew install mongodb

sudo easy_install pip

[ -d /data/db ] || sudo mkdir -p /data/db
sudo chmod -R 777 /data

sudo pip install virtualenv
virtualenv captain_env
virtualenv -p /usr/bin/python2.7 captain_env
source captain_env/bin/activate
pip install -r requirements.txt
deactivate

