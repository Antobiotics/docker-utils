# docker-utils

Selfish-ware.
One day and a bottle of wine project.
Docker swarm and AWS helpers.

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

Look at `cluster.json` to see how to configure it.

Examples:

```
> ./env/bin/python utils/main.py bootstrap --instances dbs
> ./env/bin/python utils/main.py bootstrap --instances all
> ./env/bin/python utils/main.py bootstrap --instances dbs,key-store
```

You got it.

