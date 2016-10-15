import json
import click

import utils.logger as l
import utils.aws as aws

from utils.configuration import CONFIG

def pretty_json(j):
    return json.dumps(j, sort_keys=True,
                      indent=4, separators=(',', ': '))

PREDEFINED_ROLES = {
    'key-store': aws.KeyStore(name='key-store',
                              instance_type='t2.nano'),
}

def set_configuration(cfg_file):
    l.INFO('With Configuration file: %s'%(cfg_file))
    CONFIG.switch_to(cfg_file)

def bootstrap_role(role, reset):
    instance = aws.AWSGenericInstance(role)
    if role in PREDEFINED_ROLES.keys():
        instance = PREDEFINED_ROLES[role]
    return instance.build(reset)

@click.group()
@click.option('--cfg-file', default='env.cfg')
def main(**kwargs):
    set_configuration(kwargs['cfg_file'])


@main.command()
def run(**kwargs):
    print kwargs

@main.command()
@click.argument('role')
@click.option('--reset', is_flag=True)
def bootstrap(role, reset):
    print bootstrap_role(role, reset)

@main.command()
@click.argument('name')
@click.option('--pretty', is_flag=True)
def describe(name, pretty):
    descriptor = aws.AWS().get_instance_ip_desc(name)
    if pretty:
        l.INFO(pretty_json(descriptor))
    else:
        print descriptor

if __name__ == '__main__':
    main()
