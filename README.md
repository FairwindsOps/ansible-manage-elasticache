Role Name
=========

Manage elasticache clusters in the Omnia framework. Currently memcached only.

Requirements
------------

Any pre-requisites that may not be covered by Ansible itself or the role should be mentioned here. For instance, if the role uses the EC2 module, it may be a good idea to mention in this section that the boto package is required.

Role Variables
--------------

A description of the settable variables for this role should go here, including any variables that are in defaults/main.yml, vars/main.yml, and any variables that can/should be set via parameters to the role. Any variables that are read from other roles and/or the global scope (ie. hostvars, group vars, etc.) should be mentioned here as well.

Dependencies
------------

A list of other roles hosted on Galaxy should go here, plus any details in regards to parameters that may need to be set for other roles, or variables that are used from other roles.

Example Playbook
----------------

```
- name: Ensure elasticache memcached cluster
  hosts: localhost
  connection: local
  gather_facts: False
  vars:
    stack: streetjumpers

  pre_tasks:
    - include_vars: "{{ item }}"
      with_items:
        - ../../../account/vars.yml
        - ../env.yml
      tags: always

    - name: set fact
      set_fact:
        layer_config: "{{ stacks.streetjumpers.layers.memcached }}"

  roles:
    - role: reactiveops.manage-elasticache
      elasticache_manage_cluster_id:              "{{ layer_config.ec_cluster_id }}"
      elasticache_manage_name:                    "{{ layer_config.ec_cluster_name }}"
      elasticache_manage_engine:                  "{{ layer_config.ec_engine }}"
      elasticache_manage_cache_engine_version:    "{{ layer_config.ec_engine_version }}"
      elasticache_manage_node_type:               "{{ layer_config.ec_nodetype }}"
      elasticache_manage_num_nodes:               "{{ layer_config.num_nodes }}"
      elasticache_manage_elb_health_check:        "{{ layer_config.health_check }}"
      elasticache_manage_cache_subnet_group:      "{{ layer_config.cache_subnet_group }}"

```

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
