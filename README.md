# krawen

`krawen` is a library for convenient crawling, mirroring.
Primarily, it consists of `KrawenCrawler`, `KrawenMirrorServer`, and `KrawenCrawlerRunner`.

# installation
TODO pypi distribution (but it can install easily!)

```shell
pip install git+https://github.com/ityeri/krawen
```


# features

## `KrawenCrawler`
it's a central crawling feature.
It provides features to download the full response of a specific endpoint,
simulate a page network request, and retrieve the sub-redirection links of a page.
Finally, it saves all data to the ingested `EndpointStore`

## `KrawenMirrorServer`
it's a mirroring server.
It hosts the crawled data as a web

## `KrawenCrawlerRunner`
it's a recursive crawling runner.
From the seed endpoint path, it's crawling recursively forever


# runs

