import click


@click.group()
def run():
    pass


@run.command()
@click.argument('name')  # add the name argument
def hello(**kwargs):
    print 'Hello, {0}!'.format(kwargs['name'])


if __name__ == '__main__':
    run()
