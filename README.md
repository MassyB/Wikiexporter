# Instalation

Using `docker` you need to build the image and use it as a command line to execute the CLI application

```sh
docker build -t wikiexporter .
```

In order to see what are the inputs expected by the CLI

```
docker run wikiexporter wikiexport --help
```

In order to process data for a single date and save it in tmp

```
docker run -v /tmp:/tmp wikiexporter wikiexport --start-datetime=20201023T01:00:00  --output=/tmp
```

To process data for a date range and save it in any directory and still use the cache (which by default uses /tmp)

```
docker run -v /tmp:/tmp -v /tmp:/user/src/app/wikiexport/export_data \
wikiexporter wikiexport --start-datetime=20201023T01:00:00  --end-datetime=20201023T03:00:00 --output=export_data
```

To save data in S3 for a date range. If the volume is omitted the cache is empty every time because it's in the container (inside /tmp by default)

```
docker run -v /tmp:/tmp -v /tmp:/user/src/app/wikiexport/export_data \
wikiexporter wikiexport --start-datetime=20201023T01:00:00  --end-datetime=20201023T03:00:00 \
--output=s3://datadog-bucket-1234/my-directory --aws-access-key-id=my-key-id --aws-secret-access-key=my-secret-key
```

To run unitests

```
docker run wikiexporter python -m unittests -v
```
# Solution Design:

This application is designed to run on a local machine as a CLI. It revolves around four main components:

* *Wikimedia* which is responsible of downloading pageviews data, computing the top 25 for each domain and sort those remaining pageviews
* *Cache* which is responsible of storing results of previous executions and retrieve them whenever possible in order not to redo work
* *Blacklist* which is responsible of downloading the previous pageviews and load that for a quicker access
* *Writer* which is responsible of writing data either to local storage or to S3

### Wikimedia

##### Top 25 pageview per domain 

The main goal of the Wikimedia class is to compute the top 25 pageview per domain: It does so with the use of min heaps. 
The main data structure is a dictionary where each key represents a domain and each value represents a Min Heap containing the pageviews of that domain.
I decided to go with my own implementation (without the help of external libraries) because it's fairly simple and the data is already pre aggregated up to the 
domain and page title. 

A min heap is a complete binary tree where the value of each node is less than the values of it's children making the minimum value accessible in a very efficient manner in the root.
This data structure (DS) helps us keep the K largest elements of a collection. In our case the value is the number of views
```
Heap

  2
 / \
6   5

new_element = 4

Heap

  4
 / \
6   5
```

The time complexity of this method is O(n log k) where n is the number of elements in the dump file. 
Because we know K The time complexity is O(n).

#### Usage of generators 

In the functions that downloads the dump file and reads a gzipped file I make the choice to use generators instead of loading all the content of the file in memory. This prevents too much memory consumption at the cost of slow disk reads.
Of course this doesn't mean that this application can support a TB size dump file (if all the pageviews are not filtered). 
I'll write about scale in the improvements section

### Cache

Because we don't want to do the same work more than once I use a cache but a very simple version of it which is a file stored in local storage that is loaded when the application starts and its content is saved when the application finishes.
I implemented the cache as an abstract class because it can be backed by a file (for my simple use case, LocalCache) but it can also use more sophisticated solutions that deal with TTL, concurrency ...etc. 

#### Blacklist

There is the `src.model.blacklist` that handles the blacklist of pages and domains. It's downloading when the application starts and loads the file in memory because it's smaller than the dump files.

#### Writer 

Writer is an abstract class that exposes a way to save pageviews in some storage. There are two implementations: `LocalWriter` and `S3Writer`. 
The abstract `Writer` class uses some factory method to chose which class to instantiate based on application's inputs

#### Pageview

This class encodes the data we are dealing with in this application. I decided to go with a proper class instead of manipulating tuples (or named tuples) because I think it's clearer 
and I can take advantage of python's data model by overriding magic methods (`__eq__` and `__hash__` for example) 

## Clean code

I tried to uses typing hints in the signature of the function to give an idea to the reader of the expected input/output
I tried to document all the functions, methods and classes
I used generators when I felt that memory consumptions could be optimized epecially when downloading large dump files
I used used a function decorator in order to keep exception handling and retries in one single place in the code base namely `utils.repeat_if_exception`

## Unit Tests

All the unit tests are under the test directory. I tried to cover as many code paths as I could. In order to do so I used mock objects to mock 
externals services: file IO with `open` built-in or networking with `requests`.

## Improvements 

If we were to execute this application for every hour of the day we can:
* hava a CRON Job to execute the `docker run -v /tmp:/tmp wikieport --start-datetime=20201023T00:00:00`
* If we have an orchestration solution like Apache Airflow we can execute this application as a task in a DAG and use jinja templates for the `--start-datetime` argument

This is intended to be a CLI application that handles small amount of data. If we wanted to scale, implementing the top 25 using python standard library would be challenging instead we can use 
data processing frameworks like (Apache BEAM or Spark) to handle such amount of data. Both frameworks support operations like filtering, grouping and aggregating.

Also in order to handle scale the cache part can be replace by a more robust and feature rich solution like redis/memcache which allows for several users using the application to benefit from all the already executed requests
