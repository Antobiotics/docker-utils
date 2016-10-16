from executor import execute

import swarm_queen.logger as l
from swarm_queen.aws import AWS
from swarm_queen.configuration import CONFIG

DEFAULT_STEPS = [
    'prepare',
    'bootstrap',
    'finalise'
]

class AWSInstance(AWS):
    def __init__(self, description):
        super(AWSInstance, self).__init__()
        self.description = description

    @property
    def name(self):
        return self.cluster_prefix + '-' + self.description['name']

    @property
    def instance_type(self):
        return self.description.get('instance_type', 't2.nano')

    @property
    def role(self):
        return self.description.get('role', 'node')

    @property
    def is_master(self):
        return False

    @property
    def root_size(self):
        return self.description.get('root-size', 10)

    @property
    def num_instances(self):
        return self.description.get('num_instances', 1)

    @property
    def reset(self):
        return self.description.get('reset', False)

    @property
    def steps(self):
        return self.description.get('steps', DEFAULT_STEPS)

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

    @property
    def instance_options(self):
        options = [
            '--amazonec2-instance-type={instance_type}',
            '--engine-label role={role}',
            '--amazonec2-root-size {storage}'
        ]
        return (
            ' '.join(options)
            .format(instance_type=self.instance_type,
                    role=self.role,
                    storage=self.root_size)
        )

    def exists(self):
        return self.get_instance(self.name) != []

    def remove(self):
        for i in range(self.num_instances):
            name = self.name
            if self.num_instances != 1:
                name = self.name + '-' + str(i)
            command = 'docker-machine rm %s' %(name)
            execute(command)

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

    def build(self):
        for i in range(self.num_instances):
            name = self.name
            if self.num_instances != 1:
                name = self.name + '-' + str(i)
            if self.reset and self.exists():
                res = self.remove()
                if not res:
                    raise RuntimeError('Unable to remove instance %s' %(name))

            for step in self.steps:
                l.INFO("Performing: %s" %(step))
                self.steps_dict[step](name)

    def prepare(self, name):
        raise RuntimeError("self.prepare must be implemented for AWSInstance")

    def bootstrap(self, name):
        raise RuntimeError("self.bootstrap must be implemented for AWSInstance")

    def finalise(self, name):
        raise RuntimeError("self.finalise must be implemented for AWSInstance")

class AWSGenericInstance(AWSInstance):
    def prepare(self, name):
        pass

    def bootstrap(self, name):
        options = [self.driver_options,
                   self.instance_options,
                   name]

        options_string = (
            ' '.join(options)
            .format(instance_type=self.instance_type)
        )
        self.create(options_string)

    def finalise(self, name):
        pass

class KeyStore(AWSGenericInstance):

    @property
    def num_instances(self):
        return 1

    def finalise(self, name):
        command = [
            'eval "$(docker-machine env %s)" &&',
            'docker run',
            '-d -p "8500:8500"',
            '-h "consul" progrium/consul -server -bootstrap'
        ]
        execute(' '.join(command)%(name))

class SwarmNode(AWSGenericInstance):

    def get_key_strore_desc(self):
        return CONFIG.get_member_by_role('key-store')

    def get_key_store(self):
        key_store_name = self.get_key_strore_desc()['name']
        key_store_desc = (
            self.get_instance_ip_descs(key_store_name)
        )
        if len(key_store_desc) != 1:
            raise RuntimeError("""
                               There must be only one key store instance, found: %s
                               """ % (len(key_store_desc)))
        return key_store_desc[0]['public']['ip']

    @property
    def swarm_options(self):
        options = [
            '--swarm-discovery="consul://{key_store}:8500"',
            '--engine-opt="cluster-store=consul://{key_store}:8500"',
            '--engine-opt="cluster-advertise=eth0:2376"',
        ]
        return (
            ' '.join(options)
            .format(key_store=self.get_key_store())
        )

    @property
    def bootstrap_options(self):
        set_master = ''
        if self.is_master:
            l.WARN("Setting up instance as SWARM MASTER")
            set_master = '--swarm-master'
        return [self.driver_options,
                self.instance_options,
                '--swarm',
                set_master,
                self.swarm_options]

    def bootstrap(self, name):
        options = self.bootstrap_options + [name]
        options_string = ' '.join(options)
        self.create(options_string)

class SwarmMaster(SwarmNode):
    @property
    def num_instances(self):
        return 1

    @property
    def is_master(self):
        return True
