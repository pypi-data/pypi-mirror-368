Rastless-CLI
=================

##### A cli for managing data and user access for the cloud application rastless

## Table of Content

- [Installation](#installation)
- [Running the CLI](#running-the-cli)
- [Commands Overview](#commands-overview)
- [Accomplishing a running system](#accomplishing-a-running-system)
- [Publish and Release](#publish-and-release)

## Installation

Requires: Python >=3.8, <4.0

```bash
$ pip install rastless-cli
```

RastLess has to be configured before you can check if everything works. Make sure that your aws account is configured
and has access to DynamoDb and S3.

You can check if everything works correctly by running:

```bash
$ rastless check-aws-connection
```

If it is not working, make sure to configure the aws connection by configuring the aws cli. You need an Access ID and a
Secret ID from aws to configure. Please check
the [official instructions](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html) for further
help.

##### Developer Installation

```bash
$ pip install poetry
$ git clone https://github.com/EomapCompany/rastless-cli
$ cd rastless-cli
$ poetry install
```

Run tests

```bash
poetry run pytest tests/ -v
```

## Running the CLI

After installation you can run the ClI by using:

```bash
$ rastless --help
```

You can decide if you want to upload data to the production, development or test environment.
By using the "dev" flag you upload it to development environment. By using the "test" flag you upload it to the test
environment and without a flag you upload it to the production environment.

```bash
# Example development
$ rastless --dev list-layers

# Example test
$ rastless --test list-layers

# Example production
$ rastless list-layers
```

## Commands Overview

| Commands              |                                                       |
|-----------------------|-------------------------------------------------------|
| add-mpl-colormap      | Add a custom colormap based on matplotlib colormaps   |
| add-discrete-colormap | Add a discrete colormap based on matplotlib colormaps |
| add-sld-colormap      | Add a SLD file                                        |
| add-permission        | Add a role to one or multiple layers                  |
| check-aws-connection  | Check if cli can connect to aws                       |
| create-layer          | Create layer                                          |
| create-timestep       | Create timestep entry and upload layer to S3 bucket   |
| delete-colormap       | Remove a SLD file                                     |
| delete-layer          | Delete a layer with all timestep entries              |
| delete-permission     | Delete one or multiple permissions                    |
| delete-layer-timestep | Delete one or multiple layer timesteps                |
| delete-cache          | Deletes cache                                         |
| list-layers           | List all layers                                       |
| list-colormaps        | List all colormaps                                    |
| layer-exists          | Check if layer id exists                              |

## Accomplishing a running system

#### 1. Check if you have access to the system

```bash
$ rastless check-aws-connection
```

#### 2. Create a new layer

- All inputs are strings. You have to take care, that the element exists in the database e.g. the colormap name.
- Multiple permissions can be set by using multiple -pe flags

```bash
$ rastless create-layer -cl hypos -pr tur -t Turbidity -cm log75_C2S8_32bit -u FTU -b <rgb uuid> -d "Some description" -r 1 -pe user#marcel -pe role#hypos:full-access
```

It will return a new uuid which you need to store, in order to upload timesteps to the particular layer

#### 3. Upload Timesteps for layer

```bash
$ rastless create-timestep -d 2020-01-01T15:00:00 -s SENT2 -l <layer uuid> -t daily -p deflate
```

## Breaking changes

### Version 0.3

The command "create-timestep" changed. Files need to be set as flag instead of normal input

- Now it is possible to set multiple files per timestep by setting multiple file flags -f
- To override a timestep which already exists you have to set the flag -o, otherwise you will be asked during uploading
  if you really want to override it
- To append new files to an existing timestep you have to set the flag -a
- **Attention:** If you append a file to an existing timestep and the filename already exists, it will be automatically
  overridden
  without further action

### Version 1.0.0

Small naming changes:

- fixing naming differences timestamp => timestep  
  `delete_layer_timestamps` command changed to => `delete_layer_timestep`
- permission parameter in all cli commands `-p`  
  change affected `create_layer` command (before: -pe)
- singular and plural inconsistencies (all create/ delete commands named singular)  
  `delete_layer_timesteps` => `delete_layer_timestep`

```shell
# Before. Filepath without flag
rastless create-timestep file1.tif -d 2020-01-01T15:00:00 -s Sent2 -layer-id 1234 -t daily -p deflate

# Now: Single file. Flag: -f
rastless create-timestep -f file1.tif -d 2020-01-01T15:00:00 -s Sent2 -layer-id 1234 -t daily -p deflate

# Now: Multi file. Flag: -f <file1> -f <file1>
rastless create-timestep -f file1.tif -f file2.tif -d 2020-01-01T15:00:00 -s Sent2 -layer-id 1234 -t daily -p deflate

# Now: Override existing timestep. Flag: -o
rastless create-timestep -f file1.tif -f file2.tif -d 2020-01-01T15:00:00 -s Sent2 -layer-id 1234 -t daily -p deflate -o

# Now: Append file to existing timestep. Flag: -a
rastless create-timestep -f file2.tif -d 2020-01-01T15:00:00 -layer-id 1234 -p deflate -a
```

### Version 1.7.0
- Add new endoints to delete layer cache in s3 bucket and dynamodb
- List-layer now has filter options for region_id, client and product

## Publish and Release

When releasing we use [semantic versioning](https://semver.org/) to define the new version tag.

When pushing to master any commit message that includes #major, #minor, #patch will add a tag to the commit
with the respective version bump. If #none is contained in the merge commit message, it will skip the version bump.
When none of the above types is provided the default version bump (minor) is triggered. After the tagging a package
built and release to Pypi is triggered. If all steps were successfully a new GitHub release is created.
