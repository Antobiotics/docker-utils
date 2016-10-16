import json
import click

import utils.logger as l
import utils.aws as aws
import utils.aws_instance as aws_instances

from utils.configuration import CONFIG

def pretty_json(j):
    return json.dumps(j, sort_keys=True,
                      indent=4, separators=(',', ': '))

PREDEFINED_ROLES = {
    'key-store': aws_instances.KeyStore,
    'swarm-master': aws_instances.SwarmMaster
}

def set_configuration(cfg_file):
    l.INFO('With Configuration file: %s'%(cfg_file))
    CONFIG.read_config(cfg_file)

def bootstrap_member(desc):
    instance = aws_instances.SwarmNode
    role = desc['role']
    if role in PREDEFINED_ROLES.keys():
        instance = PREDEFINED_ROLES[role]

    instance_class = PREDEFINED_ROLES.get(role, instance)
    return instance_class(desc).build()

@click.group()
@click.option('--cfg', default='./cluster.json')
def main(**kwargs):
    set_configuration(kwargs['cfg'])

@main.command()
@click.option('--instances', default='all',
              help="CSV of instance names")
@click.option('--reset', is_flag=True,
              help='Destroy the machine if already exists')
@click.option('--steps', default='prepare,bootstrap,finalise',
              help="CSV <prepare,bootstrap,finalise>")
def bootstrap(instances, reset, steps):
    targeted_members = instances.split(',')
    if instances == 'all':
        targeted_members = sorted(CONFIG.get_members(),
                                  key=lambda k: k.get('priority', 0),
                                  reverse=True)
        targeted_members = [
            m['name'] for m in targeted_members
        ]

    for name in targeted_members:
        member_desc = CONFIG.get_member(name)
        member_desc['reset'] = reset
        member_desc['steps'] = steps.split(',')
        l.INFO("Bootstraping %s" %(member_desc))
        bootstrap_member(member_desc)

@main.command()
@click.option('--instances', default='all',
              help="CSV of instance names")
def takedown(instances):
    targeted_members = instances.split(',')
    if instances == 'all':
        targeted_members = [
            m['name'] for m in CONFIG.get_members()
        ]

    for name in targeted_members:
        member_desc = CONFIG.get_member(name)
        l.INFO("Taking down %s" %(member_desc))
        instance = aws_instances.AWSInstance(member_desc)
        try:
            instance.remove()
        except Exception as e:
            l.ERROR(e)

@main.command()
@click.argument('name')
@click.option('--pretty', is_flag=True)
def describe(name, pretty):
    descriptor = aws.AWS().get_instance_ip_descs(name)
    if pretty:
        l.INFO(pretty_json(descriptor))
    else:
        print descriptor

if __name__ == '__main__':
    main()
