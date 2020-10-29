some commands:

to build the image:
* docker build -t wikiexport_container .

to execute the docker:

* docker run wikiexport_container wikiexport --help
* docker run wikiexport_container wikiexport --start-datetime=20201023T01:00:00
* docker run wikiexport_container python -m unitest -v

* docker run -v /tmp:/tmp wikiexport wikiexport --start-datetime=20200901T02:00:00 
* docker run -v /tmp:/usr/src/app/export_data wikiexport wikiexport --start-datetime=20200901T02:00:00 --output=export_data
* docker run -v /tmp:/usr/src/app/export_data -v /tmp:/tmp \
wikiexport wikiexport --start-datetime=20200901T02:00:00 --output=export_data
notes:
* how to add a volume for local storage