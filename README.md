# Installation

Using `docker` you need to build the image to execute the CLI application

```
> docker build -t wikiexporter .
```

In order to see what are the inputs expected by the CLI

```
> docker run wikiexporter wikiexport --help
Usage: wikiexport [OPTIONS]

Options:
  --start-datetime [%Y%m%dT%H:00:00]
                                  datetime (truncated to the hour) of the data
                                  to process  [default: (20201029T10:00:00);
                                  required]

  --end-datetime [%Y%m%dT%H:00:00]
                                  end datetime inclusive (truncated to the
                                  hour) of the datetime range to process

  --output TEXT                   output path where to put CSV files. Can be a
                                  directory or an S3 bucket of the form
                                  s3://mybucket/my-folder  [required]

  --aws-access-key-id TEXT        AWS credentials: ACCESS KEY ID
  --aws-secret-access-key TEXT    AWS credentials: SECRET ACCESS KEY ID
  --help                          Show this message and exit.

```

In order to process data for a single date and save it in `/tmp`.
In order to retrieve the final CSV file in the host's `/tmp` you must bind it to the directory specified by the `--output` argument

```
> docker run -v /tmp:/tmp wikiexporter wikiexport --start-datetime=20201023T01:00:00  --output=/tmp
```

To process the default yesterday's datetime data 

```
> docker run -v /tmp:/tmp wikiexporter wikiexport
```

To process data for a date range and save it in any directory and still use the cache (which by default uses `/tmp`)

```
> docker run -v /tmp:/tmp -v /tmp:/user/src/app/wikiexport/export_data \
wikiexporter wikiexport --start-datetime=20201023T01:00:00  --end-datetime=20201023T03:00:00 --output=export_data
```

To save data in S3 for a date range. If the volume is omitted the cache is empty every time because it's in the container (inside `/tmp` by default)

```
> docker run -v /tmp:/tmp -v /tmp:/user/src/app/wikiexport/export_data \
wikiexporter wikiexport --start-datetime=20201023T01:00:00  --end-datetime=20201023T03:00:00 \
--output=s3://datadog-bucket-1234/my-directory --aws-access-key-id=my_key_id --aws-secret-access-key=my_secret_key
```

To run unittests

```
> docker run wikiexporter python -m unittest -v
```


# Design:

This application is designed to run on a local machine as a CLI. It revolves around four main components:

* **Wikimedia** which is responsible of downloading pageviews data, computing the top 25 for each domain and sort those remaining pageviews
* **Cache** which is responsible of storing results of previous executions and retrieve them whenever possible in order not to redo work
* **Blacklist** which is responsible of downloading the previous pageviews and load that for a quicker access
* **Writer** which is responsible of writing data either to local storage or to S3


### Wikimedia


##### Top 25 pageview per domain 

The main goal of the Wikimedia class is to compute the top 25 pageviews per domain: It does so using min heaps. 
The main data structure is a dictionary where each key represents a domain and each value represents a min heap containing the pageviews of that domain.
I decided to go with my own implementation (without the help of external libraries) because it's fairly simple and the data is already pre aggregated up to the 
domain and page title. 

A min heap is a complete binary tree where the value of each node is less than the values of it's children making the minimum value accessible in a very efficient manner in the root.
This data structure helps us keep the K largest elements of a collection. In our case we compare between pageviews using number of views
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
Because we know k equals 25 The time complexity is O(n).


#### Usage of generators 

In the functions that download the dump file and reads a gzipped file I make the choice to use generators instead of loading all the content of the file in memory. This prevents too much memory consumption at the cost of slow disk reads.
Of course this doesn't mean that this application can support a TB size dump file (if all the pageviews are not filtered). 


### Cache

Because we don't want to do the same work more than once I use a cache but a very simple version of it which is a file stored in local storage that is loaded when the application starts and its content is saved when the application finishes.
I implemented the cache as an abstract class because it can be backed by a file (for my simple use case, `LocalCache`) but it can also use more sophisticated solutions that deal with TTL, concurrency ...etc. 


#### Blacklist

There is the `src.model.blacklist` that handles the blacklist of pages and domains. It's downloaded when the application starts and it loads the file in memory because it's smaller than the dump files.


#### Writer 

Writer is an abstract class that exposes a way to save pageviews in some storage. There are two implementations: `LocalWriter` and `S3Writer`. 
The abstract `Writer` class uses some factory method to choose which class to instantiate based on arguments of `wikiexport` CLI


#### Pageview

This class encodes the data we are dealing with in this application. I decided to go with a proper class instead of manipulating tuples (or named tuples) because I think it's clearer 
and I can take advantage of python's data model by overriding magic methods (`__eq__` and `__hash__` for example) 


## Clean code

I tried to uses typing hints in the signature of the function to give an idea to the reader of the expected input/output
I tried to document all the functions, methods and classes
I used generators when I felt that memory consumptions could be optimized epecially when downloading large dump files
I used used a function decorator in order to keep exception handling and retries in one single place in the code base namely `utils.repeat_if_exception`


## Unit Tests

All the unit tests are under the `test` directory. I tried to cover as many code paths as I could. In order to do so I used mock objects to mock 
externals services: file IO with `open` built-in or networking with `requests`.


## Improvements 


**What might change about your solution if this application needed to run automatically for each hour of the day?**

* We can have a CRON Job to execute the `docker run -v /tmp:/tmp wikieport ` and we would modify the default value of `--start-datetime` to be the last hour. This is a simple solution if we don't have any orchestration framework at our disposal.
* If we have an orchestration solution like Apache Airflow we can execute this application as a task (using `BashOperator`) in a DAG and use jinja templates for the `--start-datetime` argument to get the current hour. 
* In Airflow we can use the docker operator to execute `wikiexport` or we can also use the `KubernetesPodOperator` in order to delegate work outside Airflow as much as possible with the benefits of K8s doing the heavy lifting for us


**What additional things would you want to operate this application in a production setting?**

* In a production setting I would aime for 100% code coverage using some mock for the boto3 client
* I would also operate on CI workflow in order to add new code as easily as possible without breaking things (100% code coverage)
* Because it would be an application that a team collaborates on, I would also make reading the code easier by using some tools like `black` for python to have a unified code base
* For continuous deployment I would make sure that the version of the image changes to track the enhancements of the application and to make rollbacks easier
* For security purposes I would not use arguments like `aws-access-key-id` and `aws-secret-access-key`. For authentication, I would rely on IAM roles/users and configuration in `~/.aws` 
* I would also monitor this application and put alerts in order to affect as less as possible downstream jobs in case of a failure
  

**How would you test this application?**

* By covering as much code paths as possible in the unittests.
* By executing some requests on a pre-production environment before executing the application in production


**How you’d improve on this application design?**

This is intended to be a CLI application that handles small amount of data. If we wanted to scale, implementing the top 25 using python standard library would be very challenging. Instead, we can use 
data processing frameworks like (Apache BEAM or Apache Spark) to handle such amount of data. Both frameworks support operations like filtering, grouping, aggregating and writing to several IOs.
For example, using Apache BEAM we can replace the `Wikimedia` class by a pipeline written also in python. This pipeline can run on a Spark/Flink cluster. That way we can handle a lot more data.

Apache Airflow should be used to start execution of those pipelines (Spark/BEAM).

Also in order to handle scale, the cache part can be replace by a more robust and feature rich solution like redis (which will take the data from a database). It will allow for several users using the application to benefit from all the already executed requests

When we handle a date range instead of doing the whole work by one single BEAM/Spark job we can take advantage of the fact that the data is partitioned by hour so we can start as many jobs as hours in our date range.
With that solution we reduce latency and redoing work in case of failure is faster because it's quicker to process an hour worth of data than it's to process a day worth of data.