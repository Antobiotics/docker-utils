import json

class Configuration(object):
    def __init__(self, cfg='./cluster.json'):
        self.read_config(cfg)

    def read_config(self, cfg):
        print cfg
        with open(cfg, 'r') as cfg_file:
            self.config = json.load(cfg_file)

    def get_config(self):
        return self.config

    def get_aws(self, key):
        return self.config['aws'][key]

    def get_members(self):
        return self.config['members']

    def get_member(self, name):
        members = self.get_members()
        for member in members:
            if member['name'] == name:
                return member
        raise RuntimeError('Member not found %s' %(name))

    def get_member_by_role(self, role):
        members = self.get_members()
        for member in members:
            if member['role'] == role:
                return member
        raise RuntimeError('Member not found with role: %s' %(role))


CONFIG = Configuration()
