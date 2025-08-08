r'''
# CDKTF prebuilt bindings for digitalocean/digitalocean provider version 2.63.0

This repo builds and publishes the [Terraform digitalocean provider](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs) bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-digitalocean](https://www.npmjs.com/package/@cdktf/provider-digitalocean).

`npm install @cdktf/provider-digitalocean`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-digitalocean](https://pypi.org/project/cdktf-cdktf-provider-digitalocean).

`pipenv install cdktf-cdktf-provider-digitalocean`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Digitalocean](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Digitalocean).

`dotnet add package HashiCorp.Cdktf.Providers.Digitalocean`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-digitalocean](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-digitalocean).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-digitalocean</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/cdktf/cdktf-provider-digitalocean-go`](https://github.com/cdktf/cdktf-provider-digitalocean-go) package.

`go get github.com/cdktf/cdktf-provider-digitalocean-go/digitalocean/<version>`

Where `<version>` is the version of the prebuilt provider you would like to use e.g. `v11`. The full module name can be found
within the [go.mod](https://github.com/cdktf/cdktf-provider-digitalocean-go/blob/main/digitalocean/go.mod#L1) file.

## Docs

Find auto-generated docs for this provider here:

* [Typescript](./docs/API.typescript.md)
* [Python](./docs/API.python.md)
* [Java](./docs/API.java.md)
* [C#](./docs/API.csharp.md)
* [Go](./docs/API.go.md)

You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-digitalocean).

## Versioning

This project is explicitly not tracking the Terraform digitalocean provider version 1:1. In fact, it always tracks `latest` of `~> 2.19` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by [generating the provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [CDK for Terraform](https://cdk.tf)
* [Terraform digitalocean provider](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [CDK for Terraform](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### Projen

This is mostly based on [Projen](https://github.com/projen/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on Projen

There's a custom [project builder](https://github.com/cdktf/cdktf-provider-project) which encapsulate the common settings for all `cdktf` prebuilt providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [CDKTF Repository Manager](https://github.com/cdktf/cdktf-repository-manager/).
'''
from pkgutil import extend_path
__path__ = extend_path(__path__, __name__)

import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

import typeguard
from importlib.metadata import version as _metadata_package_version
TYPEGUARD_MAJOR_VERSION = int(_metadata_package_version('typeguard').split('.')[0])

def check_type(argname: str, value: object, expected_type: typing.Any) -> typing.Any:
    if TYPEGUARD_MAJOR_VERSION <= 2:
        return typeguard.check_type(argname=argname, value=value, expected_type=expected_type) # type:ignore
    else:
        if isinstance(value, jsii._reference_map.InterfaceDynamicProxy): # pyright: ignore [reportAttributeAccessIssue]
           pass
        else:
            if TYPEGUARD_MAJOR_VERSION == 3:
                typeguard.config.collection_check_strategy = typeguard.CollectionCheckStrategy.ALL_ITEMS # type:ignore
                typeguard.check_type(value=value, expected_type=expected_type) # type:ignore
            else:
                typeguard.check_type(value=value, expected_type=expected_type, collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS) # type:ignore

from ._jsii import *

__all__ = [
    "app",
    "cdn",
    "certificate",
    "container_registry",
    "container_registry_docker_credentials",
    "custom_image",
    "data_digitalocean_account",
    "data_digitalocean_app",
    "data_digitalocean_certificate",
    "data_digitalocean_container_registry",
    "data_digitalocean_database_ca",
    "data_digitalocean_database_cluster",
    "data_digitalocean_database_connection_pool",
    "data_digitalocean_database_metrics_credentials",
    "data_digitalocean_database_replica",
    "data_digitalocean_database_user",
    "data_digitalocean_domain",
    "data_digitalocean_domains",
    "data_digitalocean_droplet",
    "data_digitalocean_droplet_autoscale",
    "data_digitalocean_droplet_snapshot",
    "data_digitalocean_droplets",
    "data_digitalocean_firewall",
    "data_digitalocean_floating_ip",
    "data_digitalocean_genai_agent",
    "data_digitalocean_genai_agent_versions",
    "data_digitalocean_genai_agents",
    "data_digitalocean_genai_agents_by_openai_api_key",
    "data_digitalocean_genai_knowledge_base",
    "data_digitalocean_genai_knowledge_base_data_sources",
    "data_digitalocean_genai_knowledge_bases",
    "data_digitalocean_genai_openai_api_key",
    "data_digitalocean_genai_openai_api_keys",
    "data_digitalocean_image",
    "data_digitalocean_images",
    "data_digitalocean_kubernetes_cluster",
    "data_digitalocean_kubernetes_versions",
    "data_digitalocean_loadbalancer",
    "data_digitalocean_partner_attachment",
    "data_digitalocean_partner_attachment_service_key",
    "data_digitalocean_project",
    "data_digitalocean_projects",
    "data_digitalocean_record",
    "data_digitalocean_records",
    "data_digitalocean_region",
    "data_digitalocean_regions",
    "data_digitalocean_reserved_ip",
    "data_digitalocean_reserved_ipv6",
    "data_digitalocean_sizes",
    "data_digitalocean_spaces_bucket",
    "data_digitalocean_spaces_bucket_object",
    "data_digitalocean_spaces_bucket_objects",
    "data_digitalocean_spaces_buckets",
    "data_digitalocean_spaces_key",
    "data_digitalocean_ssh_key",
    "data_digitalocean_ssh_keys",
    "data_digitalocean_tag",
    "data_digitalocean_tags",
    "data_digitalocean_volume",
    "data_digitalocean_volume_snapshot",
    "data_digitalocean_vpc",
    "data_digitalocean_vpc_nat_gateway",
    "data_digitalocean_vpc_peering",
    "database_cluster",
    "database_connection_pool",
    "database_db",
    "database_firewall",
    "database_kafka_config",
    "database_kafka_topic",
    "database_mongodb_config",
    "database_mysql_config",
    "database_online_migration",
    "database_opensearch_config",
    "database_postgresql_config",
    "database_redis_config",
    "database_replica",
    "database_user",
    "database_valkey_config",
    "domain",
    "droplet",
    "droplet_autoscale",
    "droplet_snapshot",
    "firewall",
    "floating_ip",
    "floating_ip_assignment",
    "genai_agent",
    "genai_agent_knowledge_base_attachment",
    "genai_agent_route",
    "genai_function",
    "genai_knowledge_base",
    "genai_knowledge_base_data_source",
    "genai_openai_api_key",
    "kubernetes_cluster",
    "kubernetes_node_pool",
    "loadbalancer",
    "monitor_alert",
    "partner_attachment",
    "project",
    "project_resources",
    "provider",
    "record",
    "reserved_ip",
    "reserved_ip_assignment",
    "reserved_ipv6",
    "reserved_ipv6_assignment",
    "spaces_bucket",
    "spaces_bucket_cors_configuration",
    "spaces_bucket_logging",
    "spaces_bucket_object",
    "spaces_bucket_policy",
    "spaces_key",
    "ssh_key",
    "tag",
    "uptime_alert",
    "uptime_check",
    "volume",
    "volume_attachment",
    "volume_snapshot",
    "vpc",
    "vpc_nat_gateway",
    "vpc_peering",
]

publication.publish()

# Loading modules to ensure their types are registered with the jsii runtime library
from . import app
from . import cdn
from . import certificate
from . import container_registry
from . import container_registry_docker_credentials
from . import custom_image
from . import data_digitalocean_account
from . import data_digitalocean_app
from . import data_digitalocean_certificate
from . import data_digitalocean_container_registry
from . import data_digitalocean_database_ca
from . import data_digitalocean_database_cluster
from . import data_digitalocean_database_connection_pool
from . import data_digitalocean_database_metrics_credentials
from . import data_digitalocean_database_replica
from . import data_digitalocean_database_user
from . import data_digitalocean_domain
from . import data_digitalocean_domains
from . import data_digitalocean_droplet
from . import data_digitalocean_droplet_autoscale
from . import data_digitalocean_droplet_snapshot
from . import data_digitalocean_droplets
from . import data_digitalocean_firewall
from . import data_digitalocean_floating_ip
from . import data_digitalocean_genai_agent
from . import data_digitalocean_genai_agent_versions
from . import data_digitalocean_genai_agents
from . import data_digitalocean_genai_agents_by_openai_api_key
from . import data_digitalocean_genai_knowledge_base
from . import data_digitalocean_genai_knowledge_base_data_sources
from . import data_digitalocean_genai_knowledge_bases
from . import data_digitalocean_genai_openai_api_key
from . import data_digitalocean_genai_openai_api_keys
from . import data_digitalocean_image
from . import data_digitalocean_images
from . import data_digitalocean_kubernetes_cluster
from . import data_digitalocean_kubernetes_versions
from . import data_digitalocean_loadbalancer
from . import data_digitalocean_partner_attachment
from . import data_digitalocean_partner_attachment_service_key
from . import data_digitalocean_project
from . import data_digitalocean_projects
from . import data_digitalocean_record
from . import data_digitalocean_records
from . import data_digitalocean_region
from . import data_digitalocean_regions
from . import data_digitalocean_reserved_ip
from . import data_digitalocean_reserved_ipv6
from . import data_digitalocean_sizes
from . import data_digitalocean_spaces_bucket
from . import data_digitalocean_spaces_bucket_object
from . import data_digitalocean_spaces_bucket_objects
from . import data_digitalocean_spaces_buckets
from . import data_digitalocean_spaces_key
from . import data_digitalocean_ssh_key
from . import data_digitalocean_ssh_keys
from . import data_digitalocean_tag
from . import data_digitalocean_tags
from . import data_digitalocean_volume
from . import data_digitalocean_volume_snapshot
from . import data_digitalocean_vpc
from . import data_digitalocean_vpc_nat_gateway
from . import data_digitalocean_vpc_peering
from . import database_cluster
from . import database_connection_pool
from . import database_db
from . import database_firewall
from . import database_kafka_config
from . import database_kafka_topic
from . import database_mongodb_config
from . import database_mysql_config
from . import database_online_migration
from . import database_opensearch_config
from . import database_postgresql_config
from . import database_redis_config
from . import database_replica
from . import database_user
from . import database_valkey_config
from . import domain
from . import droplet
from . import droplet_autoscale
from . import droplet_snapshot
from . import firewall
from . import floating_ip
from . import floating_ip_assignment
from . import genai_agent
from . import genai_agent_knowledge_base_attachment
from . import genai_agent_route
from . import genai_function
from . import genai_knowledge_base
from . import genai_knowledge_base_data_source
from . import genai_openai_api_key
from . import kubernetes_cluster
from . import kubernetes_node_pool
from . import loadbalancer
from . import monitor_alert
from . import partner_attachment
from . import project
from . import project_resources
from . import provider
from . import record
from . import reserved_ip
from . import reserved_ip_assignment
from . import reserved_ipv6
from . import reserved_ipv6_assignment
from . import spaces_bucket
from . import spaces_bucket_cors_configuration
from . import spaces_bucket_logging
from . import spaces_bucket_object
from . import spaces_bucket_policy
from . import spaces_key
from . import ssh_key
from . import tag
from . import uptime_alert
from . import uptime_check
from . import volume
from . import volume_attachment
from . import volume_snapshot
from . import vpc
from . import vpc_nat_gateway
from . import vpc_peering
