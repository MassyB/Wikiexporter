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
-----------------------------------------
final notes on the design
Context:

This application is designed to run on a local machine as a CLI. It revolves around four main components:

* Wikimedia which is responsible of downloading pageviews data, computing the top 25 for each domain and sort those remaining pageviews
* Cache which is responsible of storing results of previous executions and retrieve them whenever possible in order not to redo work
* Blacklist which is responsible of downloading the previous pageviews and load that for a quicker access
* Writer which is responsible of writing data either to local storage or to S3

Some deep dive:
