#!/bin/bash

###################################################################
#title         :install_hooks.sh
#description   :Installs a commit-msg, pre-commit hook for git
#author        :essaber
#date          :
#version       :1.0.0
#usage         :bash install_hooks.sh
#notes         :
#bash_version  :
###################################################################

LIB_DIR=submodules
rm -f .git/hooks/commit-msg
ln -s $PWD/githooks/commit-msg.py .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg

rm -rf .git/hooks/${LIB_DIR}
ln -s $PWD/githooks/${LIB_DIR} .git/hooks/${LIB_DIR}
