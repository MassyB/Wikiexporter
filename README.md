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

# Context:

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

## Tests



## Deployment/Packaging

## Improvements 

