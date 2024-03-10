#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# file name ..... config_template.py
# -----------------------------------------------------------------------------
# PURPOSE:
# this script offers a documented version for your developmet or execution 
# environment. In fact you can use it for configuring different environments,
# e.g. development, staging, production, testing, etc.
# just copy this script into an other script (e.g. 'config_dev.py') before you 
# do any changes to it. Then do your changes into the new created script.
# As all copies of this script will allways write their configuration into
# a file named 'config.json' you need to run the dedicated script for your
# environment from command line ...
# 
# $> python3 config_dev.py 
# 
# HINTS:
# *   you can put some defaults into the config_template.py as a kind of help
# *   do not forget to put the file names of 'config.json' and all your local
#     copies derived from 'config_template.py' to your '.gitignore' file.
#     Just do not put them under GIT's version control.
#     $> touch .gitignore
#     $> echo "config.ini" >> .gitignore
#     $> echo "config_dev.py" >> .gitignore
# -----------------------------------------------------------------------------

import json
import os

USAGE="""
# importing the application configuration into your application code, just
# use the following code snippet
# HINT:
# 
# do not forget to put the written config.json file into your local '.gitignore'
# file.

import json

config = {}
with open('config.json', 'r') as f:
	config = json.load(f)
"""

# start configuration here
config = {}

# set here the path to the document archive base directory. In subdirectories
# all PDF document files and their assotiated JSON files are located.
# The JSON files hold the meta data of all these documents and need to be read
# recursively!
config["DOCUMENT_ARCHIVE_BASE_DIR"] = "/home/marco/scratch/docarchive"


aPath = os.path.realpath(__file__)
aPath = os.path.dirname(aPath)
configPath = os.path.normpath(aPath)
aPath = os.path.join(aPath, "..")
aPath = os.path.normpath(aPath)
config["PROJECT_ROOT_DIR"] = aPath
config["BUILD_TARGET_DIR"] = os.path.join( config["PROJECT_ROOT_DIR"], "_site" )
config["STATIC_CONTENT_DIR"] = os.path.join( config["PROJECT_ROOT_DIR"], "static" )
config["TEMPLATES_DIR"] = os.path.join( config["PROJECT_ROOT_DIR"], "templates" )

if __name__ == '__main__':
	configPath = aPath = os.path.join(configPath, 'config.json')
	
	with open(configPath, 'w') as f:
		json.dump(config, f)
	
	print("configuration file was written successfully!")
	print(USAGE)
	
	exit(0)
