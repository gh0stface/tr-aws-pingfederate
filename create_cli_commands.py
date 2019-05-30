'''
Script notes:
- This script assumes you have multiple cloud-tool profiles set up and that 
they are named matching the deployment regions, example: "us-east-1", 
"eu-west-1", and "ap-southeast-1". If you do not have these profiles or they 
are named differently, you may eitehr change your cloud-tool profiles to match, 
or you may manually update the name of the profiles in the outputted commands 
before running them.
- Static TR/respository-specific values exist in this script. Most of these are 
found in the mappings objects and they should very rarely change.
'''

import sys
import datetime

if sys.version_info.major != 3:
    print ('ERROR: This script requires Python 3.x')
    sys.exit()

if len(sys.argv) != 2:
    print ('ERROR: Exactly 1 argument must be supplied - ENVIRONMENT')
    sys.exit()

environment = sys.argv[1]

if environment not in ['prod', 'qa', 'dev']:
    print ('ERROR: \"' + environment + '\" is not a valid ENVIRONMENT value - valid values are: prod, qa, dev')
    sys.exit()

DATETIMENOW = datetime.datetime.now()
DATETIMENOW_FORMATTED = DATETIMENOW.strftime('%Y%m%dT%H%M')

PFVERSION = '9.2.3'

class CalculatedValues(object):
    def __init__(self, environment, region, noderole):
        self.environment        = environment
        self.region             = region
        self.noderole           = noderole
        self.deployment_regions = environment_mapped_values(environment)['deployment_regions']
        self.aaid               = environment_mapped_values(environment)['aaid']
        self.rds_store          = environment_mapped_values(environment)['rds_store']
        self.aws_acct_id        = environment_mapped_values(environment)['aws_acct_id']
        self.instance_type      = environment_mapped_values(environment)['instance_type']
        self.region_name_full   = region_mapped_values(region)['region_name_full']
        self.clustered_noderole = noderole_mapped_values(noderole, environment, region)['clustered_noderole']
        self.provisioner        = noderole_mapped_values(noderole, environment, region)['provisioner']
        self.environment_label  = noderole_mapped_values(noderole, environment, region)['environment_label']
        self.url_suffix         = noderole_mapped_values(noderole, environment, region)['url_suffix']
        self.pf_header          = noderole_mapped_values(noderole, environment, region)['pf_header']
        self.stack_id           = environment_mapped_values(environment)['stack_ids']

def environment_mapped_values(environment):

    mappings = {
        'prod': {
            'deployment_regions': ['use1', 'euw1', 'apse1'],
            'aaid'              : '205529',
            'rds_store'         : 'PFDefaultDS',
            'aws_acct_id'       : '888888888888',
            'instance_type'     : 'c5.xlarge',
            'url_suffix'        : '',
            'pf_header'         : 'Y29uZmlnZXhwb3J0ZXI6MkZlZGVyYXRlIQ==',
            'stack_ids'         : {
                'use1' : '01626100-ffdd-11e8-8c6a-128a65397f5a',
                'euw1' : '553521b0-ffe1-11e8-97a3-50a686326636',
                'apse1': '???',
            },
        },
        'qa': {
            'deployment_regions': ['use1', 'euw1'],
            'aaid'              : '205485',
            'rds_store'         : 'PFDefaultDS',
            'aws_acct_id'       : '888888888888',
            'instance_type'     : 't3.medium',
            'url_suffix'        : '-qa',
            'pf_header'         : 'Y29uZmlnZXhwb3J0ZXI6MkZlZGVyYXRlIQ==',
            'stack_ids'         : {
                'use1' : '70f25d70-ffb7-11e8-b3b2-12b2af31d434',
                'euw1' : 'd9ee8400-ffb9-11e8-9d9d-503ac9e65ad1',
                'apse1': 'N/A',
            },
        },
        'dev': {
            'deployment_regions': ['use1'],
            'aaid'              : '205466',
            'rds_store'         : 'PFDefaultDS',
            'aws_acct_id'       : '888888888888',
            'instance_type'     : 't2.medium',
            'url_suffix'        : '-dev',
            'pf_header'         : 'Y29uZmlnZXhwb3J0ZXI6MkZlZGVyYXRlIQ==',
            'stack_ids'         : {
                'use1' : '70800720-ff08-11e8-9160-1253a26d999e',
                'euw1' : 'N/A',
                'apse1': 'N/A',
            },
        },
    }

    return mappings[environment]

def region_mapped_values(region):

    mappings = {
        'use1': {
            'region_name_full': 'us-east-1'
        },
        'euw1': {
            'region_name_full': 'eu-west-1'
        },
        'apse1': {
            'region_name_full': 'ap-southeast-1'
        }
    }

    return mappings[region]

def noderole_mapped_values(noderole, environment, region):

    mappings = {
        'admin': {
            'clustered_noderole': 'CLUSTERED_CONSOLE',
            'environment_label' : environment,
            'url_suffix'        : environment_mapped_values(environment)['url_suffix'],
            'provisioner'       : 'OFF', 
            'pf_header'         : environment_mapped_values(environment)['pf_header']
        },
        'engine': {
            'clustered_noderole': 'CLUSTERED_ENGINE',
            'environment_label' : '',
            'url_suffix'        : '',
            'provisioner'       : 'OFF', 
            'pf_header'         : ''
        },
        'provisioner': {
            'clustered_noderole': 'CLUSTERED_ENGINE',
            'environment_label' : '',
            'url_suffix'        : '',
            'provisioner'       : 'STANDALONE',  
            'pf_header'         : ''
        }
    }

    return mappings[noderole]

def get_ecr_login_string(region):

    region_name_full = region_mapped_values(region)['region_name_full']
    ecr_login_string = f'aws ecr get-login --profile {region_name_full} --no-include-email | bash'

    return ecr_login_string

def get_docker_strings(noderole, environment, region):

    values = CalculatedValues(environment, region, noderole)

    docker_image_file = f'{values.aws_acct_id}.dkr.ecr.{values.region_name_full}.amazonaws.com/a{values.aaid}-pf{values.noderole}-{environment}'

    docker_build_string = f'''docker build \\
    -t {docker_image_file}:latest \\
    -t {docker_image_file}:{DATETIMENOW_FORMATTED} \\
    --build-arg AAID={values.aaid} \\
    --build-arg ENVNAME={values.environment} \\
    --build-arg ENVURLLABEL={values.url_suffix} \\
    --build-arg PFHEADER={values.pf_header} \\
    --build-arg RDSSTORE={values.rds_store} \\
    --build-arg AWSREGION={values.region} \\
    --build-arg NODEROLE={values.clustered_noderole} \\
    --build-arg PROVISIONER={values.provisioner} \\
    --build-arg INSTANCETYPE={values.instance_type} \\
    --build-arg PFVERSION={PFVERSION} \\
    --no-cache ./PingFederate'''

    docker_push_string = f'''docker push {docker_image_file}:latest\ndocker push {docker_image_file}:{DATETIMENOW_FORMATTED}'''

    docker_strings = {
        'docker_build_string' : docker_build_string,
        'docker_push_string'  : docker_push_string
    }

    return docker_strings

def get_create_change_set_string(environment, region):

    values = CalculatedValues(environment, region, 'admin')

    cloudformation_script_location_s3 = f'a{values.aaid}-esso-cftemplates-{environment}/a{values.aaid}-{DATETIMENOW_FORMATTED}-{region}.yaml'

    s3_cp_string = f'''aws s3 cp \\
    --profile {values.region_name_full} \\
    ./a205XXX-esso-fullenv.yaml \\
    s3://{cloudformation_script_location_s3}'''

    create_change_set_string = f'''aws cloudformation create-change-set \\
    --profile {values.region_name_full} \\
    --stack-name arn:aws:cloudformation:{values.region_name_full}:{values.aws_acct_id}:stack/a{values.aaid}-esso-fullenv-{environment}/{values.stack_id[values.region]} \\
    --template-url https://s3.amazonaws.com/{cloudformation_script_location_s3} \\
    --parameters ParameterKey=RDSPassword,UsePreviousValue=true ParameterKey=EnvironmentType,UsePreviousValue=true \\
    --capabilities CAPABILITY_NAMED_IAM \\
    --change-set-name a{values.aaid}-{DATETIMENOW_FORMATTED}'''

    create_change_set_strings = {
        's3_cp_string'             : s3_cp_string,
        'create_change_set_string' : create_change_set_string
    }

    return create_change_set_strings

# just text output here, this logic can be repurposed for build/deployment automation
for region in environment_mapped_values(environment)['deployment_regions']:

    print('\n')
    print(get_ecr_login_string(region) + '\n')

    if region == 'use1':
        docker_strings = get_docker_strings('admin', environment, region)
        print(docker_strings['docker_build_string'] + '\n')
        print(docker_strings['docker_push_string'] + '\n')

    if region == 'use1':
        docker_strings = get_docker_strings('provisioner', environment, region)
        print(docker_strings['docker_build_string'] + '\n')
        print(docker_strings['docker_push_string'] + '\n')

    docker_strings = get_docker_strings('engine', environment, region)
    print(docker_strings['docker_build_string'] + '\n')
    print(docker_strings['docker_push_string'] + '\n')

    create_change_set_strings = get_create_change_set_string(environment, region)
    print(create_change_set_strings['s3_cp_string'] + '\n')
    print(create_change_set_strings['create_change_set_string'] + '\n')
