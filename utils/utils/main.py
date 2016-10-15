import click

import utils.logger as l

from utils.configuration import CONFIG

def set_configuration(cfg_file):
    l.INFO('With Configuration file: %s'%(cfg_file))
    CONFIG.switch_to(cfg_file)


@click.group()
@click.option('--cfg-file', default='env.cfg')
def main(**kwargs):
    set_configuration(kwargs['cfg_file'])


@main.command()
def run(**kwargs):
    print kwargs


if __name__ == '__main__':
    main()
