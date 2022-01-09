# Document Management As Static Website With Keyword Search

Take full control of your static website/blog generation by writing your
own simple, lightweight, and magic-free static site generator in
Python.

This generator is specialized for organizing your scanned documents 
with some meta information about the documents into linked web pages.
The documents are grouped by their meta information into:

*   creation year (sorted by it's creation date)
*   keyword (sorted by it's creation date)

As documents could get assigned to more than one keyword, they could
also be listed in referenced by different keyword lists.

The advantage is, that the whole generated static webpage can reside
on a portable device (e.g. USB stick, Solid State Drive SSD) and you 
have access to your whole document archive just with a web browser
(e.g. Google Chrome, Mozilla Firefox).

Together with a Raspberry Pi you can locally host it with a web-server
(e.g. NGINX, Apache) so you can access it locally from your LAN or WLAN.
And thanks to the simple and responsive web design you can even browse
the documents with your mobile devices (e.g. Smartphone, Tablet, Notebook).

[![MIT License][LICENSE-BADGE]](LICENSE)
![Python 3.x][PYTHON-BADGE]
![HTML 5][HTML5-BADGE]
![CSS 3][CSS3-BADGE]

[LICENSE-BADGE]: https://img.shields.io/badge/license-MIT-blue.svg
[PYTHON-BADGE]: https://img.shields.io/badge/Python-3.x-blue.svg
[HTML5-BADGE]: https://img.shields.io/badge/HTML-5-blue.svg
[CSS3-BADGE]: https://img.shields.io/badge/CSS-3-blue.svg


## Content

*   [Feature List](#feature-list)
*   [SiteMap of Website](#sitemap-of-website)
*   [SiteMap of Build](#sitemap-of-build)
*   [Process of Build](#process-of-build)


## Feature List

*   eigenes, simples Template System
*   responsive WebDesign mit "mobile first"
*   statische Web-Seiten
*   kommt ohne JavaScript im Frontend aus
*   so wenige Abhängigkeiten wie möglich
*   alle Dokumente über Schlagwort-Katalog und Jahres-Katalog 
    vorsortiert, so dass keine dynamische Suche im Frontend erforderlich ist
*   Generierung entspricht einem Build-Prozess, inkl. Initialisierung, CleanUp, usw.


## SiteMap of Website

Grobe SiteMap des Static-Blog sieht wie folgt aus:

```
web_root
├── index.html (Dukumente des aktuellen Jahres)
├── all_keywords.html (Liste aller Schlagworte)
├── all_years.html (Liste aller Jahresarchive)
├── keyword_<xxx>.html (Liste aller Dokumente die diesem 
│   Schlagwort <xxx> zugeordnet sind)
├── year_<YYYY>.html (Liste aller Dokumente die diesem 
│   Jahr <YYYY> zugeordnet sind)
├── docarchive (Verzeichnis)
│   ├── <yyyymmdd_xx> (Verzeichnis)
│   │   └── <yyyymmdd_xx>.pdf (PDF-Dokument)
│   └── <yyyymmdd_xx> (Verzeichnis)
│       └── <yyyymmdd_xx>.pdf (PDF-Dokument)
└── css (Verzeichnis)
```	


## SiteMap of Document Archive

```
archive_root
├── <yyyymmdd_xx>
│   ├── <yyyymmdd_xx>.json (JSON formated meta information about the document)
│   └── <yyyymmdd_xx>.pdf  (pdf document)
└── <yyyymmdd_xx>
    ├── <yyyymmdd_xx>.json (JSON formated meta information about the document)
    └── <yyyymmdd_xx>.pdf  (pdf document)
```


## SiteMap of Build

Grobe SiteMap der Build-Umgebung des Generators sieht wie folgt aus:

```
project_root
├── source
│   ├── config_template.py
│   └── main.py
├── templates
│   ├── keyword_template.html
│   ├── listpage_template.html
│   ├── pageitem_template.html
│   ├── page_template.html
│   └── simpleitem_template.html
└── static
    └── css (Verzeichnis)
        ├── listpage.css
        ├── page.css
        └── simplepage.css
```	


## Process of Build

Grober Ablauf des Build-Prozesses:

*   Initialisierung
*   CleanUp des letzten Builds (Verzeichnisbaum `_site` löschen)
*   Zielverzeichnisse erstellen
*   Metadaten zu den Dokumenten aus allen JSON-Dateien des 
    Dokumentarchivs rekursiv von `archive_root` aus
    laden und intern struktiert und sortiert in Datenstrukturen
    ablegen
*   aus den Metadaten die statischen HTML-Dokumente erstellen
    und in die Zielstruktur ablegen
*   PDF-Dateien des Dokumentarchivs in die Zielstruktur kopieren

