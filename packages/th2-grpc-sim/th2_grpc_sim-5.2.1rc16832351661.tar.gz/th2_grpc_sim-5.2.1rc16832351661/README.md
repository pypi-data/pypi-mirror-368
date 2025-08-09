# th2 gRPC sim library

This library contains proto messages and `Sim` service with RPC methods that are used in [th2 sim](https://github.com/th2-net/th2-sim "th2-sim"). See [sim.proto](src/main/proto/th2_grpc_sim/sim.proto "sim.proto") file for details. <br>
Tool generates code from `.proto` files and uploads built packages (`.proto` files and generated code) to specified repositories.

## How to maintain project
1. Make your changes.
2. Up version of Java package in `gradle.properties` file.
3. Up version of Python package in `package_info.json` file.
4. Commit everything.

## How to run project

### Java
If you wish to manually create and publish package for Java, run these command:
```
gradle --no-daemon clean build publish artifactoryPublish \
       -Pbintray_user=${BINTRAY_USER} \
       -Pbintray_key=${BINTRAY_KEY}
```
`BINTRAY_USER` and `BINTRAY_KEY` are parameters for publishing.

### Python
If you wish to manually create and publish package for Python:
1. Generate services by gradle:
    ```
       gradle --no-daemon clean generateProto
    ```
   You can find the generated files by following path: `src/gen/main/services/python`
2. Generate code from `.proto` files and publish everything:
    ```
    pip install -r requirements.txt
    python setup.py generate
    python setup.py sdist
    twine upload --repository-url ${PYPI_REPOSITORY_URL} --username ${PYPI_USER} --password ${PYPI_PASSWORD} dist/*
    ```
   `PYPI_REPOSITORY_URL`, `PYPI_USER` and `PYPI_PASSWORD` are parameters for publishing.

## Release notes

### 5.2.0

Updated:
* th2 gradle plugin: 0.3.4 (bom: 4.13.1)
* mypy-protobuf ~= `3.6`
* grpcio-tools ~= `1.74.0`

### 5.1.0

+ Update to `th2-bom` version `4.5.0`
+ Update to `th2-grpc-service-genrator` version `3.4.0`
+ Update to `mypy-protobuf` version `3.4`

### 4.2.0

+ Update libraries versions.
+ Vulnerability check pipeline step.

### 4.1.0

+ Add stubs for Python
+ Update `th2-grpc-common` from `3.9.0` to `3.11.1`
+ Update `th2-grpc-service-generator` from `3.1.12` to `3.2.2`

### 4.0.0 
+ New param relation
+ Added new method 'getRelatedRules'

### 3.1.3
+ Update setup.py

### 3.1.2
+ Update libraries versions.