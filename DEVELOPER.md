# Developer Information

This project is using Python 2.7 - well tested with 2.7.15

In order to setup your development environment run the following::

    ./gradlew dev

This will create a python virtualenv in the `v` directory.

This project uses gradle, see the `build.gradle.kts` file for details on tasks.

## Deployment

### Tag the release

Before creating a new distribution, a new version and tag should be created:

- Update the ``CHANGES.rst`` file and create the top paragraph for your version
- Commit your changes with a message like "prepare release x.y.z"
- Push to origin
- Create a tag by running ``./gradlew createTag``

### Build the docker image::

```
./gradlew buildDockerImage
```

Push the docker image::

```
./gradlew pushDockerDevImage
```

## Testing

Run all python tests::

    ./gradlew test

During development single tests can be run with::

    ./bin/test -vvt <filepattern>


### Test Setup Dependencies

Our test setup requires some docker services defined in
`src/az/iris/service/docker/docker-compose.yml`.


## Run locally

### System Tweaks

In order to run CrateDb in a docker container the following needs to be set:

```
   sysctl -w vm.max_map_count=262144
```

For details see https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html

### Via Docker

A docker compose stack can be found in the localdev directory. To start it do:

```
    cd localdev
    docker-compose up
```

The API is available at http://localhost:29080
The frontend is available at http://localhost:29081
The admin interface is available at http://localhost:29082
Crate admin can be reached at http://localhost:29042/admin

Note that the dockerized frontend currently takes some time (about 2 minutes)
until it is ready to use.

### Set up sample data

To be able to use localdev environment you need to apply some sample data.

First add the tables in Crate:

```
    ./v/bin/setup_db --setting etc/sql/sql.py --host localhost:29042 etc/sql/sql.sql
```

Then load the sampledata as bulk into Crate:

```
    curl -s -XPOST localhost:29042/_bulk?pretty= --data-binary "@samples/sample.bulk"
```


## API Documentation

When the app is running the API documentation can be found under /docs,
e.g: http://localhost:29080/docs
