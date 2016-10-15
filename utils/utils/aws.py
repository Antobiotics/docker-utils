import json
import ConfigParser

from executor import execute

import utils.logger as l
import utils.configuration as g_conf

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
        return g_conf.CONFIG.get_aws('credentials')

    @property
    def region(self):
        return g_conf.CONFIG.get_aws('region')

    @property
    def vpc_id(self):
        return g_conf.CONFIG.get_aws('vpc_id')

    @property
    def cluster_prefix(self):
        return g_conf.CONFIG.get('cluster', 'prefix')

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

    def get_instance(self, name):
        instances_data = self.get_instances()
        reservations = instances_data['Reservations']
        for reservation in reservations:
            try:
                instances = reservation['Instances']
                for instance in instances:
                    key_name = instance['KeyName']
                    if key_name == name:
                        return instance
            except KeyError:
                raise RuntimeError('No instance for %s' %(name))
        l.WARN("%s doesn't exist")
        return None

    def get_instance_ip_desc(self, name):
        instance = self.get_instance(name)
        return {
            'private': {
                "dns_name": instance['PrivateDnsName'],
                "ip": instance['PrivateIpAddress'],
            },
            'public': {
                "dns_name": instance['PublicDnsName'],
                "ip": instance['PublicIpAddress'],
            }
        }


class AWSInstance(AWS):
    def __init__(self, name, instance_type='t2.nano'):
        super(AWSInstance, self).__init__()
        self.name = self.cluster_prefix + '-' + name
        self.instance_type = instance_type

    @property
    def driver_options(self):
        options = [
            '-d amazonec2',
            '--amazonec2-access-key {access_key_id}',
            '--amazonec2-region {region}',
            '--amazonec2-secret-key {access_secret_key}',
            '--amazonec2-vpc-id {vpc_id}',
            '--amazonec2-zone b',
            '--amazonec2-security-group=default']
        return (
            ' '.join(options)
            .format(access_key_id=self.aws_access_key_id,
                    access_secret_key=self.aws_secret_access_key,
                    region=self.region,
                    vpc_id=self.vpc_id)
        )

    def exists(self):
        return not self.get_instance(self.name) is None

    def remove(self):
        command = 'docker-machine rm %s' %(self.name)
        return execute(command)

    def create(self, options_string):
        command = [
            'docker-machine create',
            options_string
        ]
        res = execute(' '.join(command))
        l.INFO('Command Exited with result: %s'%(res))

    @property
    def steps_dict(self):
        return {
            'prepare': self.prepare,
            'bootstrap': self.bootstrap,
            'finalise': self.finalise
        }

    def build(self, options):
        if options['reset'] and self.exists():
            res = self.remove()
            if not res:
                raise RuntimeError('Unable to remove instance %s' %(self.name))

        for step in options['steps']:
            l.INFO("Performing: %s" %(step))
            self.steps_dict[step]()

    def prepare(self):
        raise RuntimeError("self.prepare must be implemented for AWSInstance")

    def bootstrap(self):
        raise RuntimeError("self.bootstrap must be implemented for AWSInstance")

    def finalise(self):
        raise RuntimeError("self.finalise must be implemented for AWSInstance")

class AWSGenericInstance(AWSInstance):
    def prepare(self):
        pass

    def bootstrap(self):
        options = [self.driver_options,
                   '--amazonec2-instance-type={instance_type}',
                   self.name]

        options_string = (
            ' '.join(options)
            .format(instance_type=self.instance_type)
        )
        self.create(options_string)

    def finalise(self):
        pass

class KeyStore(AWSGenericInstance):
    def finalise(self):
        command = [
            'eval "$(docker-machine env %s)" &&',
            'docker run',
            '-d -p "8500:8500"',
            '-h "consul" progrium/consul -server -bootstrap'
        ]
        execute(' '.join(command)%(self.name))

class SwarmMaster(AWSGenericInstance):
    def get_key_store(self):
        key_store_desc = (
            self.get_instance_ip_desc(self.cluster_prefix + '-key-store')
        )
        return key_store_desc['public']['ip']

    def bootstrap(self):
        options = [self.driver_options,
                   '--amazonec2-instance-type={instance_type}',
                   '--swarm',
                   '--swarm-master',
                   '--swarm-discovery="consul://{key_store}:8500"',
                   '--engine-opt="cluster-store=consul://{key_store}:8500"',
                   '--engine-opt="cluster-advertise=eth1:2376"',
                   self.name]

        options_string = (
            ' '.join(options)
            .format(instance_type=self.instance_type,
                    key_store=self.get_key_store())
        )
        l.INFO(options_string)
        self.create(options_string)
