import json
import ConfigParser

from executor import execute

import swarm_queen.logger as l
import swarm_queen.configuration as g_conf

class AWS(object):
    def __init__(self):
        self.config = self.read_aws_config()

    def read_aws_config(self):
        config = ConfigParser.ConfigParser()
        config.read(self.credentials)
        return config

    def get_config(self, key):
        return self.config.get(self.profile, key)

    @property
    def profile(self):
        return g_conf.CONFIG.get_aws('profile')

    @property
    def credentials(self):
        return g_conf.CONFIG.get_aws('credentials_file')

    @property
    def region(self):
        return g_conf.CONFIG.get_aws('region')

    @property
    def vpc_id(self):
        return g_conf.CONFIG.get_aws('vpc_id')

    @property
    def cluster_prefix(self):
        return g_conf.CONFIG.config['name']

    @property
    def aws_access_key_id(self):
        return self.get_config('aws_access_key_id')

    @property
    def aws_secret_access_key(self):
        return self.get_config('aws_secret_access_key')

    def get_instances(self):
        command = [
            'aws ec2 describe-instances',
            '--profile' + ' ' + self.profile,
            '--region' + ' ' + self.region
        ]
        res = execute(' '.join(command), capture=True)
        if res is None:
            l.ERROR("Unable to get instances for (%s, %s)"%(self.profile,
                                                            self.region))
        return json.loads(res)

    def get_instances_matching(self, name, test_func):
        instances_data = self.get_instances()
        reservations = instances_data['Reservations']
        found_instances = []
        for reservation in reservations:
            try:
                instances = reservation['Instances']
                for instance in instances:
                    key_name = instance['KeyName']
                    state = instance['State']['Name']
                    if test_func(key_name, name) and state == 'running':
                        found_instances.append(instance)
            except KeyError:
                raise RuntimeError('No instances for %s' %(name))
        return found_instances

    def get_instance(self, name):
        def is_equal(key_name, name):
            return key_name == name
        matches = self.get_instances_matching(name, is_equal)
        if len(matches) > 0:
            return matches[0]
        return matches


    def get_instances_containing(self, prefix):
        def contains(key_name, name):
            return name in key_name
        return self.get_instances_matching(prefix, contains)

    def get_instance_ip_descs(self, name):
        found_instances = self.get_instances_containing(name)
        return [{
            'name': instance['KeyName'],
            'private': {
                "dns_name": instance['PrivateDnsName'],
                "ip": instance['PrivateIpAddress'],
            },
            'public': {
                "dns_name": instance['PublicDnsName'],
                "ip": instance['PublicIpAddress'],
            }
        } for instance in found_instances]


