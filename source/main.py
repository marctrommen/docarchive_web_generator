#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# -----------------------------------------------------------------------------
# file name ..... main.py
# author ........ Marcus Trommen (mailto:marcus.trommen@gmx.net)
# -----------------------------------------------------------------------------
# PURPOSE:
# Generator (build process) for a static WebPage to access documents for 
# download.
# 
# -----------------------------------------------------------------------------

import datetime
import json
import locale
import os
import shutil
import sys
import pathlib
#from pathlib import Path

# -----------------------------------------------------------------------------
# initialize main's data structure
DATA = {}


# -----------------------------------------------------------------------------
# initializes all variables and parameters, which are necessary for the build
# process
def __init():
	sys.stderr.write("__init()\n")

	DATA["CONFIG"] = {}
	__load_config()
	locale.setlocale(locale.LC_ALL, "")
	current_timestamp = datetime.datetime.now()
	DATA["CONFIG"]["GENERATOR_STARTED"] = current_timestamp
	DATA["CONFIG"]["CURRENT_YEAR"] = current_timestamp.strftime('%Y')
	DATA["CONFIG"]["WEB_PAGE_GENERATED"] = current_timestamp.strftime('%Y%m%d %H%M%S')
	DATA["CONFIG"]["WEB_PAGE_GENERATED_HUMAN_READABLE"] = current_timestamp.strftime('%d.%m.%Y %H:%M:%S')
	DATA["CONFIG"]["WEB_PAGE_TITLE"] = "Dokument-Archiv"

	DATA["HTML_TEMPLATES"] = {}
	__load_templates()
	
	DATA["ALL_DOCUMENTS"] = {}
	DATA["ALL_KEYWORDS"] = {}
	DATA["ALL_YEARS"] = {}
	
# -----------------------------------------------------------------------------
# load configuration from file
def __load_config():
	sys.stderr.write("__load_config()\n")
	configPath = os.path.realpath(__file__)
	configPath = os.path.dirname(configPath)
	configPath = os.path.normpath(configPath)
	configPath = os.path.join(configPath, "config.json")

	with open(configPath, "r") as f:
		DATA["CONFIG"] = json.load(f)
		if not DATA["CONFIG"]:
			raise RuntimeError("configuration should not be empty!")

# -----------------------------------------------------------------------------
# load html templates from files
def __load_templates():
	sys.stderr.write("__load_templates()\n")

	fileName = os.path.join(DATA["CONFIG"]["TEMPLATES_DIR"], "page_template.html")
	with open(fileName, 'r') as fileObject:
		DATA["HTML_TEMPLATES"]["WEB_PAGE"] = fileObject.read()

	fileName = os.path.join(DATA["CONFIG"]["TEMPLATES_DIR"], "listpage_template.html")
	with open(fileName, 'r') as fileObject:
		DATA["HTML_TEMPLATES"]["ITEM_LIST"] = fileObject.read()

	fileName = os.path.join(DATA["CONFIG"]["TEMPLATES_DIR"], "simpleitem_template.html")
	with open(fileName, 'r') as fileObject:
		DATA["HTML_TEMPLATES"]["SIMPLE_ITEM"] = fileObject.read()

	fileName = os.path.join(DATA["CONFIG"]["TEMPLATES_DIR"], "pageitem_template.html")
	with open(fileName, 'r') as fileObject:
		DATA["HTML_TEMPLATES"]["DOC_ITEM"] = fileObject.read()

	fileName = os.path.join(DATA["CONFIG"]["TEMPLATES_DIR"], "keyword_template.html")
	with open(fileName, 'r') as fileObject:
		DATA["HTML_TEMPLATES"]["KEYWORD"] = fileObject.read()
	

# -----------------------------------------------------------------------------
# fill the DATA structure with data from JSON files of all documents from the
# document archive
def __fill_data():
	sys.stderr.write("__fill_data()\n")

	# --- search recursively for all *.json files ---
	for json_file in pathlib.Path(DATA["CONFIG"]["DOCUMENT_ARCHIVE_BASE_DIR"]).rglob('*.json'):
		with open(str(json_file), 'r') as fileObject:
			json_data = json.load(fileObject)

		# search 'title' field for criteria
		document_id = json_data['id']
		title = json_data['title']
		storage_location = json_data['storage_location']

		keyword_list = []
		for keyword in json_data['keywords']:
			keyword = keyword.strip()
			keyword = keyword.lower()
			keyword = keyword.replace(" ", "_")
			keyword = keyword.replace("-", "_")
			keyword = keyword.replace("ä", "ae")
			keyword = keyword.replace("ö", "oe")
			keyword = keyword.replace("ü", "ue")
			keyword = keyword.replace("ß", "ss")
			keyword_list.append(keyword)

		__add_document_to_all_documents(document_id, title, storage_location, keyword_list)
		
		__add_document_to_all_years(document_id)
		
		__add_document_to_all_keywords(document_id, keyword_list)


# -----------------------------------------------------------------------------
# add a document by it's document_id to the documents list
def __add_document_to_all_documents(document_id, title, storage_location, keyword_list):
	sys.stderr.write("__add_document_to_all_documents()\n")
	
	html_content_as_list = []
	for keyword in keyword_list:
		snippetParameters = dict(
			KEYWORD = keyword
		)
		html_content_as_list.append(DATA["HTML_TEMPLATES"]["KEYWORD"].format(**snippetParameters))

	keywords_html_snippet = " | ".join(html_content_as_list)
	
	snippetParameters = dict(
		DOCUMENTID = document_id,
		DOCUMENTTITLE = title,
		DOCUMENTSTORAGELOCATION = storage_location, 
		DOCUMENTKEYWORDS = keywords_html_snippet
	)
	
	DATA["ALL_DOCUMENTS"][document_id]=DATA["HTML_TEMPLATES"]["DOC_ITEM"].format(**snippetParameters)
	
	

# -----------------------------------------------------------------------------
# add a document by it's document_id to the year's list
# in case the year's list does not exist yet, it gets created
def __add_document_to_all_years(document_id):
	sys.stderr.write("__add_document_to_all_years()\n")
	
	year = document_id[0:4]
	
	if not year in DATA["ALL_YEARS"]:
		DATA["ALL_YEARS"][year] = []
	
	DATA["ALL_YEARS"][year].append(document_id)


# -----------------------------------------------------------------------------
# add a document by it's document_id to the keyword's list
# as a document might be related to more than one keyword, the document gets
# added to the list of each keyword
# in case the keyword's list does not exist yet, it gets created
def __add_document_to_all_keywords(document_id, keyword_list):
	sys.stderr.write("__add_document_to_all_keywords()\n")

	for key in keyword_list:
		if not key in DATA["ALL_KEYWORDS"]:
			DATA["ALL_KEYWORDS"][key] = []
	
		DATA["ALL_KEYWORDS"][key].append(document_id)


# -----------------------------------------------------------------------------
# build process for the whole web page for the document archive
# 1) clean up old build directory
# 2) copy static content (css files) to target directory
# 3) create all_years.html
# 4) create for each year a year_<year>.html
# 5) create all_keywords.html
# 6) create for each keyword a keyword_<keyword>.html
# 7) create alias link from index.html to year_<current_year>.html
# 8) create alias link from documents subdirectory to the document_archive_base 
#    directory
def __build_web_page():
	sys.stderr.write("__build_web_page()\n")
	
	# 1) clean up old build directory
	if os.path.exists(DATA["CONFIG"]["BUILD_TARGET_DIR"]):
		if not os.path.isdir(DATA["CONFIG"]["BUILD_TARGET_DIR"]):
			raise RuntimeError(DATA["CONFIG"]["BUILD_TARGET_DIR"], "should be a directory!")

		shutil.rmtree(DATA["CONFIG"]["BUILD_TARGET_DIR"])
	

	# 2) copy static content (css files) to target directory
	shutil.copytree(DATA["CONFIG"]["STATIC_CONTENT_DIR"], DATA["CONFIG"]["BUILD_TARGET_DIR"])

	# 3) create all_years.html
	year_list = list(DATA["ALL_YEARS"].keys())
	year_list.sort()
	year_list.reverse()
	
	__create_all_years_page(year_list)
	
	# 4) create for each year a year_<year>.html
	__create_every_year_page(year_list)
	
	# 5) create all_keywords.html
	keyword_list = list(DATA["ALL_KEYWORDS"].keys())
	keyword_list.sort()
	
	__create_all_keywords_page(keyword_list)

	# 6) create for each keyword a keyword_<keyword>.html
	__create_every_keyword_page(keyword_list)

	# 7) create alias link from index.html to year_<latest_year>.html
	__create_symlink_for_index_page()
	
	# 8) create alias link from documents subdirectory to the 
	#    document_archive_base directory
	link_name = os.path.join(DATA["CONFIG"]["BUILD_TARGET_DIR"], "documents")
	destination_file = os.path.join(DATA["CONFIG"]["DOCUMENT_ARCHIVE_BASE_DIR"], "")
	os.symlink(destination_file, link_name)
	
# -----------------------------------------------------------------------------
# create alias link from index.html to year_<latest_year>.html
# <latest_year> is the first element in the reverse sorted list of all
# 'year_*.html' files
def __create_symlink_for_index_page():
	sys.stderr.write("__create_symlink_for_index_page()\n")

	year_index_list = list(pathlib.Path(DATA["CONFIG"]["BUILD_TARGET_DIR"]).glob('year_*.html'))
	year_index_list.sort()
	year_index_list.reverse()
	destination_file = year_index_list[0]

	link_name = os.path.join(DATA["CONFIG"]["BUILD_TARGET_DIR"], "index.html")

	os.symlink(destination_file, link_name)


# -----------------------------------------------------------------------------
def __create_all_years_page(year_list):
	sys.stderr.write("__create_all_years_page()\n")
	
	item_html_as_list = []
	for year in year_list:
		number_items = len(DATA["ALL_YEARS"][year])
		
		snippetParameters = dict(
			ITEMID = year,
			ITEMFILENAME = "year_" + year + ".html",
			ITEMTITLE = year,
			NUMBERITEMS = str(number_items)
		)
		
		item_html_as_list.append(DATA["HTML_TEMPLATES"]["SIMPLE_ITEM"].format(**snippetParameters))
	
	snippetParameters = dict(
		PAGETITLE_ID = "jahresuebersicht",
		PAGETITLE = "Jahresübersicht",
		PAGECONTENT = "\n".join(item_html_as_list)
	)
	html_list_content = DATA["HTML_TEMPLATES"]["ITEM_LIST"].format(**snippetParameters)
	

	snippetParameters = dict(
		TITLE = DATA["CONFIG"]["WEB_PAGE_TITLE"],
		PAGESTYLE = "simplepage.css",
		CURRENT_YEAR = DATA["CONFIG"]["CURRENT_YEAR"],
		WEB_PAGE_GENERATED = DATA["CONFIG"]["WEB_PAGE_GENERATED"],
		WEB_PAGE_GENERATED_HUMAN_READABLE = DATA["CONFIG"]["WEB_PAGE_GENERATED_HUMAN_READABLE"],
		CONTENT = html_list_content
	)
	html_page_content = DATA["HTML_TEMPLATES"]["WEB_PAGE"].format(**snippetParameters)
	
	
	html_file = os.path.join(DATA["CONFIG"]["BUILD_TARGET_DIR"], "all_years.html")
	with open(html_file, 'w') as fileObject:
		fileObject.write(html_page_content)


# -----------------------------------------------------------------------------
def __create_all_keywords_page(keyword_list):
	sys.stderr.write("__create_all_keywords_page()\n")

	item_html_as_list = []
	for keyword in keyword_list:
		number_items = len(DATA["ALL_KEYWORDS"][keyword])
		
		snippetParameters = dict(
			ITEMID = keyword,
			ITEMFILENAME = "keyword_" + keyword + ".html",
			ITEMTITLE = keyword,
			NUMBERITEMS = str(number_items)
		)
		
		item_html_as_list.append(DATA["HTML_TEMPLATES"]["SIMPLE_ITEM"].format(**snippetParameters))

	snippetParameters = dict(
		PAGETITLE_ID = "schlagwortuebersicht",
		PAGETITLE = "Schlagwortübersicht",
		PAGECONTENT = "\n".join(item_html_as_list)
	)
	html_list_content = DATA["HTML_TEMPLATES"]["ITEM_LIST"].format(**snippetParameters)

	snippetParameters = dict(
		TITLE = DATA["CONFIG"]["WEB_PAGE_TITLE"],
		PAGESTYLE = "simplepage.css",
		CURRENT_YEAR = DATA["CONFIG"]["CURRENT_YEAR"],
		WEB_PAGE_GENERATED = DATA["CONFIG"]["WEB_PAGE_GENERATED"],
		WEB_PAGE_GENERATED_HUMAN_READABLE = DATA["CONFIG"]["WEB_PAGE_GENERATED_HUMAN_READABLE"],
		CONTENT = html_list_content
	)
	html_page_content = DATA["HTML_TEMPLATES"]["WEB_PAGE"].format(**snippetParameters)
	
	
	html_file = os.path.join(DATA["CONFIG"]["BUILD_TARGET_DIR"], "all_keywords.html")
	with open(html_file, 'w') as fileObject:
		fileObject.write(html_page_content)


# -----------------------------------------------------------------------------
def __create_every_year_page(year_list):
	sys.stderr.write("__create_every_year_page()\n")

	for year in year_list:
		document_list = list(DATA["ALL_YEARS"][year])
		document_list.sort()
		document_list.reverse()
		
		item_html_as_list = []
		for document_id in document_list:
			item_html_as_list.append(DATA["ALL_DOCUMENTS"][document_id])

		snippetParameters = dict(
			PAGETITLE_ID = "jahr_" + year,
			PAGETITLE = "Jahr " + year,
			PAGECONTENT = "\n".join(item_html_as_list)
		)
		html_list_content = DATA["HTML_TEMPLATES"]["ITEM_LIST"].format(**snippetParameters)

		snippetParameters = dict(
			TITLE = DATA["CONFIG"]["WEB_PAGE_TITLE"],
			PAGESTYLE = "listpage.css",
			CURRENT_YEAR = DATA["CONFIG"]["CURRENT_YEAR"],
			WEB_PAGE_GENERATED = DATA["CONFIG"]["WEB_PAGE_GENERATED"],
			WEB_PAGE_GENERATED_HUMAN_READABLE = DATA["CONFIG"]["WEB_PAGE_GENERATED_HUMAN_READABLE"],
			CONTENT = html_list_content
		)
		html_page_content = DATA["HTML_TEMPLATES"]["WEB_PAGE"].format(**snippetParameters)
		
		html_file = os.path.join(DATA["CONFIG"]["BUILD_TARGET_DIR"], "year_" + year + ".html")
		with open(html_file, 'w') as fileObject:
			fileObject.write(html_page_content)


# -----------------------------------------------------------------------------
def __create_every_keyword_page(keyword_list):
	sys.stderr.write("__create_every_keyword_page()\n")

	for keyword in keyword_list:
		document_list = list(DATA["ALL_KEYWORDS"][keyword])
		document_list.sort()
		document_list.reverse()

		item_html_as_list = []
		for document_id in document_list:
			item_html_as_list.append(DATA["ALL_DOCUMENTS"][document_id])

		snippetParameters = dict(
			PAGETITLE_ID = "schlagwort_" + keyword,
			PAGETITLE = "Schlagwort " + keyword,
			PAGECONTENT = "\n".join(item_html_as_list)
		)
		html_list_content = DATA["HTML_TEMPLATES"]["ITEM_LIST"].format(**snippetParameters)

		snippetParameters = dict(
			TITLE = DATA["CONFIG"]["WEB_PAGE_TITLE"],
			PAGESTYLE = "listpage.css",
			CURRENT_YEAR = DATA["CONFIG"]["CURRENT_YEAR"],
			WEB_PAGE_GENERATED = DATA["CONFIG"]["WEB_PAGE_GENERATED"],
			WEB_PAGE_GENERATED_HUMAN_READABLE = DATA["CONFIG"]["WEB_PAGE_GENERATED_HUMAN_READABLE"],
			CONTENT = html_list_content
		)
		html_page_content = DATA["HTML_TEMPLATES"]["WEB_PAGE"].format(**snippetParameters)
		
		html_file = os.path.join(DATA["CONFIG"]["BUILD_TARGET_DIR"], "keyword_" + keyword + ".html")
		with open(html_file, 'w') as fileObject:
			fileObject.write(html_page_content)

# -----------------------------------------------------------------------------
# do the build process
if __name__ == '__main__':
	sys.stderr.write("main() start\n")

	__init()
	
	# check for semaphore
	semaphore = os.path.join(DATA["CONFIG"]["DOCUMENT_ARCHIVE_BASE_DIR"], "semaphore")
	if os.path.exists(semaphore):
	
		__fill_data()
		__build_web_page()
	
		sys.stderr.write(DATA["CONFIG"]["WEB_PAGE_GENERATED"])
	
		# delete semaphore
		os.remove(semaphore)
	else:
		sys.stderr.write("nothing to do\n")

	sys.stderr.write("main() done\n")

	exit(0)
