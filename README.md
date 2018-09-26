# s3-fuzzer

## Installation
s3-fuzzer can be installed using:

```
python setup.py install
```

Or run from a docker container:

```
docker pull zenko/s3-fuzzer
docker run -it zenko/s3-fuzzer
```

## Usage

s3-fuzzer can be configured using a yaml file or environment variables.
s3-fuzzer will search for a `config.yaml` file in the following directories:
* Directory specified by the `S3_FUZZER_CONF_DIR` environment variable
* `~/.s3fuzzer/`
* The current directory

An example config:
```yaml
objects:
  count:
    start: 5000
    stop: 10000
  prefix:
    min: 0
    max: 25
  versions:
    min: 0
    max: 1000
transform:
  min: 10
  max: 100
zenko:
  host: http://zenko.example.com:8080
  access_key: <MY_ACCESS_KEY>
  secret_key: <MY_SECRET_KEY>
  bucket: my-zenko-bucket
aws:
  access_key: <MY_ACCESS_KEY>
  secret_key: <MY_SECRET_KEY>
  bucket: my-aws-bucket
```

s3-fuzzer can also be configured using environment variables. Variable names are determined by flattening the config structure, upper casing, and seprating levels with an `_`.
ie:

```yaml
objects:
  count:
    start: 5000
```
becomes `OBJECTS_COUNT_START`
