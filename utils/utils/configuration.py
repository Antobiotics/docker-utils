import ConfigParser

class Configuration(object):
    def __init__(self, cfg_file='env.cfg'):
        self.config = ConfigParser.ConfigParser()
        self.config.read(cfg_file)

    def switch_to(self, cfg_file):
        self.config.read(cfg_file)

    def get_aws(self, key):
        return self.config.get('aws', key)

    def get_cluster(self, key):
        return self.config.get('cluster', key)

CONFIG = Configuration()
