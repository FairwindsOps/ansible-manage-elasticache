#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

# Borrowed and heavily modified from: https://github.com/wimnat/ansible-modules/blob/master/elasticache/elasticache_replication_group.py

DOCUMENTATION = '''
---
module: elasticache_replication_group
short_description: Manage AWS Elasticache replication groups
description:
    - Manage AWS Elasticache replication groups
version_added: "2.1"
author: Rob White (@wimnat)
options:
  name:
    auto_minor_version_upgrade:
      - "Whether to automatically perform minor engine upgrades."
    required: false
    default: false
    id:
      - "The replication group identifier."
    required: true
    default: null
  description:
    description:
      - "A user-created description for the replication group."
    required: true
    default: null
  primary_cluster_id:
    description:
      - "The identifier of the cache cluster that will serve as the primary for this replication group. This cache cluster must already exist and have a status of available."
    required: false
    default: null
  failover_enabled:
    description:
      - "Specifies whether a read-only replica will be automaticaly promoted to read/write primary if the existing primary fails. If true, Multi-AZ is enabled for this replication group."
      required: false
      default: false
  region:
    description:
     - "The AWS region to use. If not specified then the value of the EC2_REGION environment variable, if any, is used. See U(http://docs.aws.amazon.com/general/latest/gr/rande.html#ec2_region)."
    required: false
    default: null
  num_of_cache_clusters:
    description:
      - "The number of cache clusters this replication group will have. If Multi-AZ is enabled (see failover_enabled option), this parameter must be at least 2."
      required: false
      default: null
  preferred_cache_cluster_azs:
    description:
      - "A list of EC2 availability zones in which the replication group's cache clusters will be created."
      required: false
      default: null
  cache_node_type:
    description:
      - "The compute and memory capacity of the nodes in the node group."
      required: false
      default: null
  engine:
    description:
      - "The name of the cache engine to be used for the cache clusters in this replication group."
      required: false
      default: redis
  engine_version:
    description:
      - "The version number of the cache engine to be used for the cache clusters in this replication group."
      required: false
      default: null
  cache_parameter_group_name:
    description:
      - "The name of the parameter group to associate with this replication group. If this argument is omitted, the default cache parameter group for the specified engine is used."
      required: false
      default: null
  cache_subnet_group_name:
    description:
      - "The name of the cache subnet group to be used for the replication group."
      required: false
      default: null
  cache_security_group_names:
    description:
      - "A list of cache security group names to associate with this replication group."
      required: false
      default: null
  security_group_ids:
    description:
      - "One or more Amazon VPC security groups associated with this replication group. Use this parameter only when you are creating a replication group in an Amazon Virtual Private Cloud (VPC)."
      required: false
      default: null
  tags:
    description:
      - "A list of cost allocation tags to be added to this resource. A tag is a key-value pair. A tag key must be accompanied by a tag value."
      required: false
      default: null
  snapshot_arn:
    description:
      - "An Amazon Resource Name (ARN) that uniquely identifies a Redis RDB snapshot file stored in Amazon S3. The snapshot file will be used to populate the node group. The Amazon S3 object name in the ARN cannot contain any commas. This parameter is only valid if the Engine parameter is redis."
      required: false
      default: null
  snapshot_name:
    description:
      - "The name of a snapshot from which to restore data into the new node group. The snapshot status changes to restoring while the new node group is being created. This parameter is only valid if the Engine parameter is redis."
      required: false
      default: null
  preferred_maintenance_window:
    description:
      - "Specifies the weekly time range during which maintenance on the cache cluster is performed. It is specified as a range in the format ddd:hh24:mi-ddd:hh24:mi (24H Clock UTC). Example: sun:05:00-sun:09:00. The minimum maintenance window is a 60 minute period."
      required: false
      default: null
  port:
    description:
      - "The port number on which each member of the replication group will accept connections."
      required: false
      default: null
  notification_topic_arn:
    description:
      - "The Amazon Resource Name (ARN) of the Amazon Simple Notification Service (SNS) topic to which notifications will be sent. The Amazon SNS topic owner must be the same as the cache cluster owner."
      required: false
      default: null
  state:
    description:
      - "Create or remove the Elasticache replication group"
    required: false
    default: null
    choices: [ 'present', 'absent' ]
  snapshot_retention_limit:
    description:
      - "The number of days for which ElastiCache will retain automatic snapshots before deleting them. For example, if you set snapshot_retention_limit to 5, then a snapshot that was taken today will be retained for 5 days before being deleted."
    required: false
    default: 0 (backups disabled)
  snapshot_window:
    description:
      - "The daily time range (in UTC) during which ElastiCache will begin taking a daily snapshot of your node group. Example: 05:00-09:00. "
      - "If you do not specify this parameter, then ElastiCache will automatically choose an appropriate time range."
      - "This parameter is only valid if the Engine parameter is redis."
    required: false
    default: null
  retain_primary_cluster:
    description:
      - "When removing a replication group, if set to true, all of the read replicas will be deleted, but the primary node will be retained."
    required: false
    default: null
  final_snapshot_id:
    description:
      - "When removing a replication group, if set, the name of a final node group snapshot."
    required: false
    default: null
  wait:
    description: Wait for the replication group to be in state 'available' before returning
    required: false
    default: no
    choices: [ "yes", "no" ]

extends_documentation_fragment: aws
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

#

'''

import time

try:
    import boto
    HAS_BOTO = True
except ImportError:
    HAS_BOTO = False

try:
    import botocore
    import boto3
    HAS_BOTO3 = True
except ImportError:
    HAS_BOTO3 = False

def format_tags(tags):
  tag_list= []
  for tag in tags:
    tag_list += [{"Key": tag, "Value": tags[tag]}]
  return tag_list

def check_for_rep_group(module, connection):

    params = dict()

    params['ReplicationGroupId'] = module.params.get('id')

    try:
        result = connection.describe_replication_groups(**params)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'ReplicationGroupNotFoundFault':
            return False
        else:
            module.fail_json(msg=e.message)

    return result


def create_rep_group(module, connection):

    params = dict()

    params['ReplicationGroupId'] = module.params.get('id')
    params['ReplicationGroupDescription'] = module.params.get('description')
    params['PrimaryClusterId'] = module.params.get('primary_cluster_id')
    params['AutomaticFailoverEnabled'] = module.params.get('failover_enabled')
    params['NumCacheClusters'] = module.params.get('num_of_cache_clusters')
    params['PreferredCacheClusterAZs'] = module.params.get('preferred_cache_cluster_azs')
    params['CacheNodeType'] = module.params.get('cache_node_type')
    params['Engine'] = module.params.get('engine')
    params['EngineVersion'] = module.params.get('engine_version')
    params['CacheParameterGroupName'] = module.params.get('cache_parameter_group_name')
    params['CacheSubnetGroupName'] = module.params.get('cache_subnet_group_name')
    params['CacheSecurityGroupNames'] = module.params.get('cache_security_group_names')
    params['SecurityGroupIds'] = module.params.get('security_group_ids')
    params['Tags'] = format_tags(module.params.get('tags'))
    params['SnapshotArns'] = module.params.get('snapshot_arn')
    params['PreferredMaintenanceWindow'] = module.params.get('preferred_maintenance_window')
    params['Port'] = module.params.get('port')
    params['NotificationTopicArn'] = module.params.get('notification_topic_arn')
    params['AutoMinorVersionUpgrade'] = module.params.get('auto_minor_version_upgrade')
    params['SnapshotRetentionLimit'] = module.params.get('snapshot_retention_limit')
    params['SnapshotWindow'] = module.params.get('snapshot_window')

    # Remove any items with a value of None
    for k, v in list(params.items()):
        if v is None:
            del params[k]

    try:
        response = connection.create_replication_group(**params)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=e.message)

    wait = module.params.get('wait')

    if wait:
        waiter = connection.get_waiter('replication_group_available')
        waiter.wait(ReplicationGroupId=params['ReplicationGroupId'])
        rep_group = connection.describe_replication_groups({'ReplicationGroupId': params['ReplicationGroupId']})
        module.exit_json(changed=True, **rep_group['ReplicationGroups'][0])
    else:
        module.exit_json(changed=True, **response)


def destroy_rep_group(module, connection):

    params = dict()

    params['ReplicationGroupId'] = module.params.get('id')
    params['RetainPrimaryCluster'] = module.params.get('retain_primary_cluster')
    params['FinalSnapshotIdentifier'] = module.params.get('final_snapshot_id')

    # Remove any items with a value of None
    for k, v in list(params.items()):
        if v is None:
            del params[k]

    try:
        result = connection.delete_replication_groups(**params)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=e.message)

    print result


def modify_rep_group(module, connection, rep_cluster):

    changed = False
    result = {}
    if (rep_cluster['Status']) == 'available':

        params = dict()
        params['ReplicationGroupId'] = module.params.get('id')
        params['ReplicationGroupDescription'] = module.params.get('description', None)
        params['SnapshotWindow'] = module.params.get('snapshot_window', None)
        params['CacheNodeType'] = module.params.get('cache_node_type', None)
        params['SecurityGroupIds'] = module.params.get('security_group_ids', None)
        params['EngineVersion'] = module.params.get('engine_version', None)
        params['PreferredMaintenanceWindow'] = module.params.get('preferred_maintenance_window', None)
        params['AutoMinorVersionUpgrade'] = module.params.get('auto_minor_version_upgrade', None)
        params['PrimaryClusterId'] = module.params.get('primary_cluster_id', None)
        params['CacheSecurityGroupNames'] = module.params.get('cache_security_group_names', None)
        params['CacheParameterGroupName'] = module.params.get('cache_parameter_group_name', None)

        # Remove any items with a value of None
        for k, v in list(params.items()):
            if v is None:
                del params[k]

        result = connection.modify_replication_group(**params)

        if result['ReplicationGroup']['PendingModifiedValues']:
            changed = True

    module.exit_json(changed=changed, **result)


def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            auto_minor_version_upgrade=dict(default=False, required=False, type='bool'),
            id=dict(default=None, required=True, type='str'),
            description=dict(default=None, required=True, type='str'),
            primary_cluster_id=dict(default=None, required=False, type='str'),
            failover_enabled=dict(default=False, required=False, type='bool'),
            num_of_cache_clusters=dict(default=None, required=False, type='int'),
            preferred_cache_cluster_azs=dict(default=None, required=False, type='list'),
            cache_node_type=dict(default=None, required=False, type='str'),
            engine=dict(default='redis', required=False, type='str', choices=['redis']),
            engine_version=dict(default=None, required=False, type='str'),
            cache_parameter_group_name=dict(default=None, required=False, type='str'),
            cache_subnet_group_name=dict(default=None, required=False, type='str'),
            cache_security_group_names=dict(default=None, required=False, type='list'),
            security_group_ids=dict(default=None, required=False, type='list'),
            tags=dict(default=None, required=False, type='dict'),
            snapshot_arn=dict(default=None, required=False, type='str'),
            snapshot_name=dict(default=None, required=False, type='str'),
            preferred_maintenance_window=dict(default=None, required=False, type='str'),
            port=dict(default=None, required=False, type='int'),
            notification_topic_arn=dict(default=None, required=False, type='str'),
            state=dict(default=None, choices=['present', 'absent']),
            snapshot_retention_limit=dict(default=0, required=False, type='int'),
            snapshot_window=dict(default=None, required=False, type='str'),
            retain_primary_cluster=dict(default=False, required=False, type='bool'),
            final_snapshot_id=dict(default=None, required=False, type='str'),
            wait=dict(default=False, required=False, type='bool'),
        )
    )

    module = AnsibleModule(argument_spec=argument_spec, required_one_of=[['primary_cluster_id', 'num_of_cache_clusters']],)

    if not HAS_BOTO:
        module.fail_json(msg='boto required for this module')

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        connection = boto3_conn(module, conn_type='client', resource='elasticache', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except boto.exception.NoAuthHandlerFound, e:
        module.fail_json(msg=str(e))

    state = module.params.get('state')
    if state == "present":
        rep_group = check_for_rep_group(module, connection)
        if rep_group is False:
            create_rep_group(module, connection)
        else:
            rep_cluster = rep_group.get('ReplicationGroups', [{}])[0]
            modify_rep_group(module, connection, rep_cluster)
    elif state == "absent":
        rep_group = check_for_rep_group(module, connection)
        if rep_group is False:
            module.exit_json(changed=False)
        else:
            destroy_rep_group(module, connection)



# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.ec2 import *

if __name__ == '__main__':
    main()