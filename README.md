# docker-utils

## Warnings:

Selfish-ware.
One day and a bottle of wine project.
Docker swarm and AWS helpers. The whole thing is an organised hack.

- Useless for 99.99999% of the people.
- I was sick of struggling with docker for every project I'm starting and I can't remember shit.
- Very specific to my (limited) knowledge of Docker and my uses of it.
- Probably gonna give up maintaining it as soon as a new hipster tech solving the same problem goes out.
- Naive and absolutely not generic.

It basically simplifies the process of using Docker Swarm and
adds helpers to avoid typing long chains of arguments.

- Creates a key store.
- Creates a swarm master.
- Create machines with different roles and configurations.
- Force rebuild if already exist.
- Describe instances.

At the moment, it is not very clever. It just automates some of painful stuffs,
so you still need to get your hands dirty with docker first.

The goal is to have a central command line tool to trigger most
of the actions I perform on a cluster while developing.

## TODO:

- Add `cluster.json` validation.
- Read from `docker-compose.yml`.
- Scale Command.
- Refactor.
- VirtualBox support.
- Security groups.
- Add Kafka/Spark/Zookeeper images to repo.
- Script deployer.

## Requirements:

You need to have installed:

- Docker
- Docker-machine
- AWS CLI tools

You also need to have an AWS credentials somewhere. Look at `cluster.json`
to see how to configure AWS for that project.

## Setup:

```
> make setup
> make setup-dev # for developement
```

## Install:

```
> make install
> which swarm_queen
> swarm_queen --help
```

## Usage:

```
> ./swarm_queen --help
Usage: swarm_queen [OPTIONS] COMMAND [ARGS]...

Options:
  --cfg TEXT  Cluster configuration to use
  --help      Show this message and exit.

Commands:
  bootstrap
  describe
  takedown
```

It all depends (for now) on one single file: `cluster.json` that defines
your cluster.

For example:

```
{
    "name": "dev",
    "aws": {
        "region": "us-east-1",
        "credentials_file": "<home>/.aws/credentials",
        "profile": "default",
        "vpc_id": "vpc-fa8b4e9f"
    },
    "members": [
        {
            "name": "key-store",
            "instance_type": "t2.nano",
            "role": "key-store",
            "priority": 2000
        },
        {
            "name": "swarm-master",
            "instance_type": "t2.nano",
            "role": "swarm-master",
            "priority": 1000
        },
        {
            "name": "dbs",
            "intance_type": "t2.nano",
            "role": "storage",
            "root-size": 20,
            "priority": 100,
            "num_instances": 2
        },
        {
            "name": "app",
            "intance_type": "t2.nano",
            "role": "storage",
            "priority": 100
        }
    ]
}
```

### Launching a cluster:

```
> ./swarm_queen bootstrap --instances all
```

You can specify the instances to launch with a comma separated list.

```
> ./swarm_queen bootstrap --instances key-store,swarm-master
```

If an instance already exists, the simplest way is to use `--reset` flag

Look at `cluster.json` to see how to configure it.


### Examining:

```
> ./swarm_queen describe swarm-master --pretty
```


### Destroying a cluster:

```
> ./swarm_queen takedown --instances all
```

