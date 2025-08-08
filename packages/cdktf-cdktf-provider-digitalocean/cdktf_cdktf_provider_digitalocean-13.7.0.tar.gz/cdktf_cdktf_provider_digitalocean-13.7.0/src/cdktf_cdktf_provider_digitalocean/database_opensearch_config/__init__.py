r'''
# `digitalocean_database_opensearch_config`

Refer to the Terraform Registry for docs: [`digitalocean_database_opensearch_config`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config).
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

from .._jsii import *

import cdktf as _cdktf_9a9027ec
import constructs as _constructs_77d1e7e8


class DatabaseOpensearchConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseOpensearchConfig.DatabaseOpensearchConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config digitalocean_database_opensearch_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
        cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
        enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_max_content_length_bytes: typing.Optional[jsii.Number] = None,
        http_max_header_size_bytes: typing.Optional[jsii.Number] = None,
        http_max_initial_line_length_bytes: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        indices_fielddata_cache_size_percentage: typing.Optional[jsii.Number] = None,
        indices_memory_index_buffer_size_percentage: typing.Optional[jsii.Number] = None,
        indices_memory_max_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
        indices_memory_min_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
        indices_queries_cache_size_percentage: typing.Optional[jsii.Number] = None,
        indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
        indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
        indices_recovery_max_mb_per_sec: typing.Optional[jsii.Number] = None,
        ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_max_age_hours: typing.Optional[jsii.Number] = None,
        ism_history_max_docs: typing.Optional[jsii.Number] = None,
        ism_history_rollover_check_period_hours: typing.Optional[jsii.Number] = None,
        ism_history_rollover_retention_period_days: typing.Optional[jsii.Number] = None,
        override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        plugins_alerting_filter_by_backend_roles_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        script_max_compilations_rate: typing.Optional[builtins.str] = None,
        search_max_buckets: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
        thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_size: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config digitalocean_database_opensearch_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_id DatabaseOpensearchConfig#cluster_id}.
        :param action_auto_create_index_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#action_auto_create_index_enabled DatabaseOpensearchConfig#action_auto_create_index_enabled}.
        :param action_destructive_requires_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#action_destructive_requires_name DatabaseOpensearchConfig#action_destructive_requires_name}.
        :param cluster_max_shards_per_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_max_shards_per_node DatabaseOpensearchConfig#cluster_max_shards_per_node}.
        :param cluster_routing_allocation_node_concurrent_recoveries: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_routing_allocation_node_concurrent_recoveries DatabaseOpensearchConfig#cluster_routing_allocation_node_concurrent_recoveries}.
        :param enable_security_audit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#enable_security_audit DatabaseOpensearchConfig#enable_security_audit}.
        :param http_max_content_length_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_content_length_bytes DatabaseOpensearchConfig#http_max_content_length_bytes}.
        :param http_max_header_size_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_header_size_bytes DatabaseOpensearchConfig#http_max_header_size_bytes}.
        :param http_max_initial_line_length_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_initial_line_length_bytes DatabaseOpensearchConfig#http_max_initial_line_length_bytes}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#id DatabaseOpensearchConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param indices_fielddata_cache_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_fielddata_cache_size_percentage DatabaseOpensearchConfig#indices_fielddata_cache_size_percentage}.
        :param indices_memory_index_buffer_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_index_buffer_size_percentage DatabaseOpensearchConfig#indices_memory_index_buffer_size_percentage}.
        :param indices_memory_max_index_buffer_size_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_max_index_buffer_size_mb DatabaseOpensearchConfig#indices_memory_max_index_buffer_size_mb}.
        :param indices_memory_min_index_buffer_size_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_min_index_buffer_size_mb DatabaseOpensearchConfig#indices_memory_min_index_buffer_size_mb}.
        :param indices_queries_cache_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_queries_cache_size_percentage DatabaseOpensearchConfig#indices_queries_cache_size_percentage}.
        :param indices_query_bool_max_clause_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_query_bool_max_clause_count DatabaseOpensearchConfig#indices_query_bool_max_clause_count}.
        :param indices_recovery_max_concurrent_file_chunks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_recovery_max_concurrent_file_chunks DatabaseOpensearchConfig#indices_recovery_max_concurrent_file_chunks}.
        :param indices_recovery_max_mb_per_sec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_recovery_max_mb_per_sec DatabaseOpensearchConfig#indices_recovery_max_mb_per_sec}.
        :param ism_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_enabled DatabaseOpensearchConfig#ism_enabled}.
        :param ism_history_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_enabled DatabaseOpensearchConfig#ism_history_enabled}.
        :param ism_history_max_age_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_max_age_hours DatabaseOpensearchConfig#ism_history_max_age_hours}.
        :param ism_history_max_docs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_max_docs DatabaseOpensearchConfig#ism_history_max_docs}.
        :param ism_history_rollover_check_period_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_rollover_check_period_hours DatabaseOpensearchConfig#ism_history_rollover_check_period_hours}.
        :param ism_history_rollover_retention_period_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_rollover_retention_period_days DatabaseOpensearchConfig#ism_history_rollover_retention_period_days}.
        :param override_main_response_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#override_main_response_version DatabaseOpensearchConfig#override_main_response_version}.
        :param plugins_alerting_filter_by_backend_roles_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#plugins_alerting_filter_by_backend_roles_enabled DatabaseOpensearchConfig#plugins_alerting_filter_by_backend_roles_enabled}.
        :param reindex_remote_whitelist: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#reindex_remote_whitelist DatabaseOpensearchConfig#reindex_remote_whitelist}.
        :param script_max_compilations_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#script_max_compilations_rate DatabaseOpensearchConfig#script_max_compilations_rate}.
        :param search_max_buckets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#search_max_buckets DatabaseOpensearchConfig#search_max_buckets}.
        :param thread_pool_analyze_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_analyze_queue_size DatabaseOpensearchConfig#thread_pool_analyze_queue_size}.
        :param thread_pool_analyze_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_analyze_size DatabaseOpensearchConfig#thread_pool_analyze_size}.
        :param thread_pool_force_merge_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_force_merge_size DatabaseOpensearchConfig#thread_pool_force_merge_size}.
        :param thread_pool_get_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_get_queue_size DatabaseOpensearchConfig#thread_pool_get_queue_size}.
        :param thread_pool_get_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_get_size DatabaseOpensearchConfig#thread_pool_get_size}.
        :param thread_pool_search_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_queue_size DatabaseOpensearchConfig#thread_pool_search_queue_size}.
        :param thread_pool_search_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_size DatabaseOpensearchConfig#thread_pool_search_size}.
        :param thread_pool_search_throttled_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_throttled_queue_size DatabaseOpensearchConfig#thread_pool_search_throttled_queue_size}.
        :param thread_pool_search_throttled_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_throttled_size DatabaseOpensearchConfig#thread_pool_search_throttled_size}.
        :param thread_pool_write_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_write_queue_size DatabaseOpensearchConfig#thread_pool_write_queue_size}.
        :param thread_pool_write_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_write_size DatabaseOpensearchConfig#thread_pool_write_size}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c924a1b6e565523254849e1f0b78bc26d3f7dd88f726992c3e5dea55194492d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabaseOpensearchConfigConfig(
            cluster_id=cluster_id,
            action_auto_create_index_enabled=action_auto_create_index_enabled,
            action_destructive_requires_name=action_destructive_requires_name,
            cluster_max_shards_per_node=cluster_max_shards_per_node,
            cluster_routing_allocation_node_concurrent_recoveries=cluster_routing_allocation_node_concurrent_recoveries,
            enable_security_audit=enable_security_audit,
            http_max_content_length_bytes=http_max_content_length_bytes,
            http_max_header_size_bytes=http_max_header_size_bytes,
            http_max_initial_line_length_bytes=http_max_initial_line_length_bytes,
            id=id,
            indices_fielddata_cache_size_percentage=indices_fielddata_cache_size_percentage,
            indices_memory_index_buffer_size_percentage=indices_memory_index_buffer_size_percentage,
            indices_memory_max_index_buffer_size_mb=indices_memory_max_index_buffer_size_mb,
            indices_memory_min_index_buffer_size_mb=indices_memory_min_index_buffer_size_mb,
            indices_queries_cache_size_percentage=indices_queries_cache_size_percentage,
            indices_query_bool_max_clause_count=indices_query_bool_max_clause_count,
            indices_recovery_max_concurrent_file_chunks=indices_recovery_max_concurrent_file_chunks,
            indices_recovery_max_mb_per_sec=indices_recovery_max_mb_per_sec,
            ism_enabled=ism_enabled,
            ism_history_enabled=ism_history_enabled,
            ism_history_max_age_hours=ism_history_max_age_hours,
            ism_history_max_docs=ism_history_max_docs,
            ism_history_rollover_check_period_hours=ism_history_rollover_check_period_hours,
            ism_history_rollover_retention_period_days=ism_history_rollover_retention_period_days,
            override_main_response_version=override_main_response_version,
            plugins_alerting_filter_by_backend_roles_enabled=plugins_alerting_filter_by_backend_roles_enabled,
            reindex_remote_whitelist=reindex_remote_whitelist,
            script_max_compilations_rate=script_max_compilations_rate,
            search_max_buckets=search_max_buckets,
            thread_pool_analyze_queue_size=thread_pool_analyze_queue_size,
            thread_pool_analyze_size=thread_pool_analyze_size,
            thread_pool_force_merge_size=thread_pool_force_merge_size,
            thread_pool_get_queue_size=thread_pool_get_queue_size,
            thread_pool_get_size=thread_pool_get_size,
            thread_pool_search_queue_size=thread_pool_search_queue_size,
            thread_pool_search_size=thread_pool_search_size,
            thread_pool_search_throttled_queue_size=thread_pool_search_throttled_queue_size,
            thread_pool_search_throttled_size=thread_pool_search_throttled_size,
            thread_pool_write_queue_size=thread_pool_write_queue_size,
            thread_pool_write_size=thread_pool_write_size,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DatabaseOpensearchConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseOpensearchConfig to import.
        :param import_from_id: The id of the existing DatabaseOpensearchConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseOpensearchConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1d4f045519f5f167aca47752b083f16ea3952e0a56e2f3cea970dc37890e0a07)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetActionAutoCreateIndexEnabled")
    def reset_action_auto_create_index_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionAutoCreateIndexEnabled", []))

    @jsii.member(jsii_name="resetActionDestructiveRequiresName")
    def reset_action_destructive_requires_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetActionDestructiveRequiresName", []))

    @jsii.member(jsii_name="resetClusterMaxShardsPerNode")
    def reset_cluster_max_shards_per_node(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterMaxShardsPerNode", []))

    @jsii.member(jsii_name="resetClusterRoutingAllocationNodeConcurrentRecoveries")
    def reset_cluster_routing_allocation_node_concurrent_recoveries(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetClusterRoutingAllocationNodeConcurrentRecoveries", []))

    @jsii.member(jsii_name="resetEnableSecurityAudit")
    def reset_enable_security_audit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableSecurityAudit", []))

    @jsii.member(jsii_name="resetHttpMaxContentLengthBytes")
    def reset_http_max_content_length_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxContentLengthBytes", []))

    @jsii.member(jsii_name="resetHttpMaxHeaderSizeBytes")
    def reset_http_max_header_size_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxHeaderSizeBytes", []))

    @jsii.member(jsii_name="resetHttpMaxInitialLineLengthBytes")
    def reset_http_max_initial_line_length_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMaxInitialLineLengthBytes", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIndicesFielddataCacheSizePercentage")
    def reset_indices_fielddata_cache_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesFielddataCacheSizePercentage", []))

    @jsii.member(jsii_name="resetIndicesMemoryIndexBufferSizePercentage")
    def reset_indices_memory_index_buffer_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryIndexBufferSizePercentage", []))

    @jsii.member(jsii_name="resetIndicesMemoryMaxIndexBufferSizeMb")
    def reset_indices_memory_max_index_buffer_size_mb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryMaxIndexBufferSizeMb", []))

    @jsii.member(jsii_name="resetIndicesMemoryMinIndexBufferSizeMb")
    def reset_indices_memory_min_index_buffer_size_mb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesMemoryMinIndexBufferSizeMb", []))

    @jsii.member(jsii_name="resetIndicesQueriesCacheSizePercentage")
    def reset_indices_queries_cache_size_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesQueriesCacheSizePercentage", []))

    @jsii.member(jsii_name="resetIndicesQueryBoolMaxClauseCount")
    def reset_indices_query_bool_max_clause_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesQueryBoolMaxClauseCount", []))

    @jsii.member(jsii_name="resetIndicesRecoveryMaxConcurrentFileChunks")
    def reset_indices_recovery_max_concurrent_file_chunks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesRecoveryMaxConcurrentFileChunks", []))

    @jsii.member(jsii_name="resetIndicesRecoveryMaxMbPerSec")
    def reset_indices_recovery_max_mb_per_sec(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndicesRecoveryMaxMbPerSec", []))

    @jsii.member(jsii_name="resetIsmEnabled")
    def reset_ism_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmEnabled", []))

    @jsii.member(jsii_name="resetIsmHistoryEnabled")
    def reset_ism_history_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryEnabled", []))

    @jsii.member(jsii_name="resetIsmHistoryMaxAgeHours")
    def reset_ism_history_max_age_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryMaxAgeHours", []))

    @jsii.member(jsii_name="resetIsmHistoryMaxDocs")
    def reset_ism_history_max_docs(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryMaxDocs", []))

    @jsii.member(jsii_name="resetIsmHistoryRolloverCheckPeriodHours")
    def reset_ism_history_rollover_check_period_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryRolloverCheckPeriodHours", []))

    @jsii.member(jsii_name="resetIsmHistoryRolloverRetentionPeriodDays")
    def reset_ism_history_rollover_retention_period_days(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsmHistoryRolloverRetentionPeriodDays", []))

    @jsii.member(jsii_name="resetOverrideMainResponseVersion")
    def reset_override_main_response_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOverrideMainResponseVersion", []))

    @jsii.member(jsii_name="resetPluginsAlertingFilterByBackendRolesEnabled")
    def reset_plugins_alerting_filter_by_backend_roles_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPluginsAlertingFilterByBackendRolesEnabled", []))

    @jsii.member(jsii_name="resetReindexRemoteWhitelist")
    def reset_reindex_remote_whitelist(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReindexRemoteWhitelist", []))

    @jsii.member(jsii_name="resetScriptMaxCompilationsRate")
    def reset_script_max_compilations_rate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetScriptMaxCompilationsRate", []))

    @jsii.member(jsii_name="resetSearchMaxBuckets")
    def reset_search_max_buckets(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSearchMaxBuckets", []))

    @jsii.member(jsii_name="resetThreadPoolAnalyzeQueueSize")
    def reset_thread_pool_analyze_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolAnalyzeQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolAnalyzeSize")
    def reset_thread_pool_analyze_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolAnalyzeSize", []))

    @jsii.member(jsii_name="resetThreadPoolForceMergeSize")
    def reset_thread_pool_force_merge_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolForceMergeSize", []))

    @jsii.member(jsii_name="resetThreadPoolGetQueueSize")
    def reset_thread_pool_get_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolGetQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolGetSize")
    def reset_thread_pool_get_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolGetSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchQueueSize")
    def reset_thread_pool_search_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchSize")
    def reset_thread_pool_search_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchThrottledQueueSize")
    def reset_thread_pool_search_throttled_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchThrottledQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolSearchThrottledSize")
    def reset_thread_pool_search_throttled_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolSearchThrottledSize", []))

    @jsii.member(jsii_name="resetThreadPoolWriteQueueSize")
    def reset_thread_pool_write_queue_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolWriteQueueSize", []))

    @jsii.member(jsii_name="resetThreadPoolWriteSize")
    def reset_thread_pool_write_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetThreadPoolWriteSize", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.member(jsii_name="synthesizeHclAttributes")
    def _synthesize_hcl_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeHclAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="actionAutoCreateIndexEnabledInput")
    def action_auto_create_index_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "actionAutoCreateIndexEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="actionDestructiveRequiresNameInput")
    def action_destructive_requires_name_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "actionDestructiveRequiresNameInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterMaxShardsPerNodeInput")
    def cluster_max_shards_per_node_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterMaxShardsPerNodeInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationNodeConcurrentRecoveriesInput")
    def cluster_routing_allocation_node_concurrent_recoveries_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "clusterRoutingAllocationNodeConcurrentRecoveriesInput"))

    @builtins.property
    @jsii.member(jsii_name="enableSecurityAuditInput")
    def enable_security_audit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableSecurityAuditInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxContentLengthBytesInput")
    def http_max_content_length_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxContentLengthBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxHeaderSizeBytesInput")
    def http_max_header_size_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxHeaderSizeBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMaxInitialLineLengthBytesInput")
    def http_max_initial_line_length_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpMaxInitialLineLengthBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesFielddataCacheSizePercentageInput")
    def indices_fielddata_cache_size_percentage_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesFielddataCacheSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryIndexBufferSizePercentageInput")
    def indices_memory_index_buffer_size_percentage_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryIndexBufferSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMaxIndexBufferSizeMbInput")
    def indices_memory_max_index_buffer_size_mb_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryMaxIndexBufferSizeMbInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMinIndexBufferSizeMbInput")
    def indices_memory_min_index_buffer_size_mb_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesMemoryMinIndexBufferSizeMbInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesQueriesCacheSizePercentageInput")
    def indices_queries_cache_size_percentage_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesQueriesCacheSizePercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesQueryBoolMaxClauseCountInput")
    def indices_query_bool_max_clause_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesQueryBoolMaxClauseCountInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxConcurrentFileChunksInput")
    def indices_recovery_max_concurrent_file_chunks_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesRecoveryMaxConcurrentFileChunksInput"))

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxMbPerSecInput")
    def indices_recovery_max_mb_per_sec_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "indicesRecoveryMaxMbPerSecInput"))

    @builtins.property
    @jsii.member(jsii_name="ismEnabledInput")
    def ism_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ismEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryEnabledInput")
    def ism_history_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ismHistoryEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxAgeHoursInput")
    def ism_history_max_age_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryMaxAgeHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxDocsInput")
    def ism_history_max_docs_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryMaxDocsInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverCheckPeriodHoursInput")
    def ism_history_rollover_check_period_hours_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryRolloverCheckPeriodHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverRetentionPeriodDaysInput")
    def ism_history_rollover_retention_period_days_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ismHistoryRolloverRetentionPeriodDaysInput"))

    @builtins.property
    @jsii.member(jsii_name="overrideMainResponseVersionInput")
    def override_main_response_version_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "overrideMainResponseVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="pluginsAlertingFilterByBackendRolesEnabledInput")
    def plugins_alerting_filter_by_backend_roles_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "pluginsAlertingFilterByBackendRolesEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="reindexRemoteWhitelistInput")
    def reindex_remote_whitelist_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "reindexRemoteWhitelistInput"))

    @builtins.property
    @jsii.member(jsii_name="scriptMaxCompilationsRateInput")
    def script_max_compilations_rate_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "scriptMaxCompilationsRateInput"))

    @builtins.property
    @jsii.member(jsii_name="searchMaxBucketsInput")
    def search_max_buckets_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "searchMaxBucketsInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeQueueSizeInput")
    def thread_pool_analyze_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolAnalyzeQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeSizeInput")
    def thread_pool_analyze_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolAnalyzeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolForceMergeSizeInput")
    def thread_pool_force_merge_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolForceMergeSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetQueueSizeInput")
    def thread_pool_get_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolGetQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetSizeInput")
    def thread_pool_get_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolGetSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchQueueSizeInput")
    def thread_pool_search_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchSizeInput")
    def thread_pool_search_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledQueueSizeInput")
    def thread_pool_search_throttled_queue_size_input(
        self,
    ) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchThrottledQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledSizeInput")
    def thread_pool_search_throttled_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolSearchThrottledSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteQueueSizeInput")
    def thread_pool_write_queue_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolWriteQueueSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteSizeInput")
    def thread_pool_write_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "threadPoolWriteSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="actionAutoCreateIndexEnabled")
    def action_auto_create_index_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "actionAutoCreateIndexEnabled"))

    @action_auto_create_index_enabled.setter
    def action_auto_create_index_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__793bd87f76bb64c65c3518d19916fadddf7c05914444ab9d63c8b8b52e7440b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionAutoCreateIndexEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="actionDestructiveRequiresName")
    def action_destructive_requires_name(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "actionDestructiveRequiresName"))

    @action_destructive_requires_name.setter
    def action_destructive_requires_name(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f654b96f9444d7028748355ef4402ba97ef5abeade48455d5f88cff514df7cca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "actionDestructiveRequiresName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6bac83d9b7f21f8105ade0b6b6bfb8f396e33f88118566e2f994ba6686421a0d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterMaxShardsPerNode")
    def cluster_max_shards_per_node(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterMaxShardsPerNode"))

    @cluster_max_shards_per_node.setter
    def cluster_max_shards_per_node(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d11dfbfd7ac566772e54358ba7c077012fdfcdadfa50f7d38c4212292ed67bcb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterMaxShardsPerNode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterRoutingAllocationNodeConcurrentRecoveries")
    def cluster_routing_allocation_node_concurrent_recoveries(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "clusterRoutingAllocationNodeConcurrentRecoveries"))

    @cluster_routing_allocation_node_concurrent_recoveries.setter
    def cluster_routing_allocation_node_concurrent_recoveries(
        self,
        value: jsii.Number,
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7179a5b2d4a0197d89b5f1daa6bee9b03f4b138984da6ab9c852c0f1de3aad7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterRoutingAllocationNodeConcurrentRecoveries", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableSecurityAudit")
    def enable_security_audit(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableSecurityAudit"))

    @enable_security_audit.setter
    def enable_security_audit(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2fbaf80968215f381b4657bf2965514c1c021e487054ad3c96a2b3c24218976)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableSecurityAudit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMaxContentLengthBytes")
    def http_max_content_length_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxContentLengthBytes"))

    @http_max_content_length_bytes.setter
    def http_max_content_length_bytes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f61bd14ce728920ecf9c3674c64ee23806dacd7af5590dc48ff1c599a262b05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxContentLengthBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMaxHeaderSizeBytes")
    def http_max_header_size_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxHeaderSizeBytes"))

    @http_max_header_size_bytes.setter
    def http_max_header_size_bytes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__111504209914657846de86f85d407ca8f8667242eca5942ec7f8d2da6c3a3b1b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxHeaderSizeBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpMaxInitialLineLengthBytes")
    def http_max_initial_line_length_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpMaxInitialLineLengthBytes"))

    @http_max_initial_line_length_bytes.setter
    def http_max_initial_line_length_bytes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24a7c183e62b69dfb06af5e3d9185ddacbc7b1aaa5062d4feac3e830af524bfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpMaxInitialLineLengthBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d06e273669a1430a1c26e4b8c9aec313cd16a599a3e9f34d9358a78892cc447)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesFielddataCacheSizePercentage")
    def indices_fielddata_cache_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesFielddataCacheSizePercentage"))

    @indices_fielddata_cache_size_percentage.setter
    def indices_fielddata_cache_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30a677d9e9b58fd935a13f875723d7c0bf46d005a53bd1eba1f949da65563469)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesFielddataCacheSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryIndexBufferSizePercentage")
    def indices_memory_index_buffer_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryIndexBufferSizePercentage"))

    @indices_memory_index_buffer_size_percentage.setter
    def indices_memory_index_buffer_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c1310a6ed747183a70b43d5f952b4c5f666215a0fd5f1557c951b94cb875660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryIndexBufferSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMaxIndexBufferSizeMb")
    def indices_memory_max_index_buffer_size_mb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryMaxIndexBufferSizeMb"))

    @indices_memory_max_index_buffer_size_mb.setter
    def indices_memory_max_index_buffer_size_mb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__acddd5257856888f8fc96f7d940b5b019196af7b828d3dc19bf0f57054bfaea4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryMaxIndexBufferSizeMb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesMemoryMinIndexBufferSizeMb")
    def indices_memory_min_index_buffer_size_mb(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesMemoryMinIndexBufferSizeMb"))

    @indices_memory_min_index_buffer_size_mb.setter
    def indices_memory_min_index_buffer_size_mb(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e70434500784890c6112c2c2f759920d746c020e53e3e13a65d70ca2b106ffb8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesMemoryMinIndexBufferSizeMb", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesQueriesCacheSizePercentage")
    def indices_queries_cache_size_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesQueriesCacheSizePercentage"))

    @indices_queries_cache_size_percentage.setter
    def indices_queries_cache_size_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83f7adb4743b36359b3cc5bc881e14d89f48d854232703963c556405a0351ae7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesQueriesCacheSizePercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesQueryBoolMaxClauseCount")
    def indices_query_bool_max_clause_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesQueryBoolMaxClauseCount"))

    @indices_query_bool_max_clause_count.setter
    def indices_query_bool_max_clause_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__764b5afb878deca4d824f5f07e6776159a5043c71f605c7ba208f8732b1b03a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesQueryBoolMaxClauseCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxConcurrentFileChunks")
    def indices_recovery_max_concurrent_file_chunks(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesRecoveryMaxConcurrentFileChunks"))

    @indices_recovery_max_concurrent_file_chunks.setter
    def indices_recovery_max_concurrent_file_chunks(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a336628701a9f9cbb8b70f8ae61f170274e49c8e5033a8d5a522b935400aadee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesRecoveryMaxConcurrentFileChunks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indicesRecoveryMaxMbPerSec")
    def indices_recovery_max_mb_per_sec(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "indicesRecoveryMaxMbPerSec"))

    @indices_recovery_max_mb_per_sec.setter
    def indices_recovery_max_mb_per_sec(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e2d02085777d2bfdbddfcddd6e5257386389df68fe3c4ff72ee5bf9f093633d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indicesRecoveryMaxMbPerSec", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismEnabled")
    def ism_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ismEnabled"))

    @ism_enabled.setter
    def ism_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a639894e660ca035ae5bec6ccf38442bb630ed602da78c4dcc536ed910fdd69e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryEnabled")
    def ism_history_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ismHistoryEnabled"))

    @ism_history_enabled.setter
    def ism_history_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46aec146c1f65a1f3b28d1e792f17f6162198f070aead65ee1521b3a5339858d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxAgeHours")
    def ism_history_max_age_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryMaxAgeHours"))

    @ism_history_max_age_hours.setter
    def ism_history_max_age_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__882090ca7423435a4b6cd232c8d4bfba5798e5490acd0b28daf74a70aa6189a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryMaxAgeHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryMaxDocs")
    def ism_history_max_docs(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryMaxDocs"))

    @ism_history_max_docs.setter
    def ism_history_max_docs(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9d1d1bdbfd17a90a784a71f87facfa6f5c4e6cde9dda3ec0bbb88b29ca799f5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryMaxDocs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverCheckPeriodHours")
    def ism_history_rollover_check_period_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryRolloverCheckPeriodHours"))

    @ism_history_rollover_check_period_hours.setter
    def ism_history_rollover_check_period_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab69a57f9b8b35e8563da09146efb3647129c9c230c26cbad387ffe49face61a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryRolloverCheckPeriodHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ismHistoryRolloverRetentionPeriodDays")
    def ism_history_rollover_retention_period_days(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ismHistoryRolloverRetentionPeriodDays"))

    @ism_history_rollover_retention_period_days.setter
    def ism_history_rollover_retention_period_days(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be6bfab662ff248259ff30889ca3cf5ce42f38cfe77ceae639e9000f977cb92e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ismHistoryRolloverRetentionPeriodDays", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="overrideMainResponseVersion")
    def override_main_response_version(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "overrideMainResponseVersion"))

    @override_main_response_version.setter
    def override_main_response_version(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e947b0e992991975eae56dbb6055174b41cf7d0b3bbc475a280c6be7f9e20085)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "overrideMainResponseVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pluginsAlertingFilterByBackendRolesEnabled")
    def plugins_alerting_filter_by_backend_roles_enabled(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "pluginsAlertingFilterByBackendRolesEnabled"))

    @plugins_alerting_filter_by_backend_roles_enabled.setter
    def plugins_alerting_filter_by_backend_roles_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96b24ca458194e389fb6002c24350a520e151f3ce99930fb07ca0820590d4f99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pluginsAlertingFilterByBackendRolesEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="reindexRemoteWhitelist")
    def reindex_remote_whitelist(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "reindexRemoteWhitelist"))

    @reindex_remote_whitelist.setter
    def reindex_remote_whitelist(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d97f1c6f72e25014d6068e83cf048e9336e303555c339209022c9d4b92f5961b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "reindexRemoteWhitelist", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="scriptMaxCompilationsRate")
    def script_max_compilations_rate(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "scriptMaxCompilationsRate"))

    @script_max_compilations_rate.setter
    def script_max_compilations_rate(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__41a3003eb94507101597c4515a81c6ec3d265e2160e2ff747723f12302b2e9fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "scriptMaxCompilationsRate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="searchMaxBuckets")
    def search_max_buckets(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "searchMaxBuckets"))

    @search_max_buckets.setter
    def search_max_buckets(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15ccff43299751eb6c1ade9f9943efcf62e1ff11d8c383242797b65e211a5edb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "searchMaxBuckets", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeQueueSize")
    def thread_pool_analyze_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolAnalyzeQueueSize"))

    @thread_pool_analyze_queue_size.setter
    def thread_pool_analyze_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70bfa2003f9c204a034b7ab10832acc2401937175437c1731b806315de5fde27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolAnalyzeQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolAnalyzeSize")
    def thread_pool_analyze_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolAnalyzeSize"))

    @thread_pool_analyze_size.setter
    def thread_pool_analyze_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6b1334515fc3a50540115e5a60c3cc2825a645dafdf5a9c5251223963ba2dd1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolAnalyzeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolForceMergeSize")
    def thread_pool_force_merge_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolForceMergeSize"))

    @thread_pool_force_merge_size.setter
    def thread_pool_force_merge_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e27e43384edf708f234de11e89fd231cbe17df1c520fd24b72126b7fccb03558)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolForceMergeSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetQueueSize")
    def thread_pool_get_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolGetQueueSize"))

    @thread_pool_get_queue_size.setter
    def thread_pool_get_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5873dea08d265502dcf3cbba72f783b6dfc500b65ec7038d07d45d2eb732675)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolGetQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolGetSize")
    def thread_pool_get_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolGetSize"))

    @thread_pool_get_size.setter
    def thread_pool_get_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0d1cf80e6503197b5f6be9ff56455d78cfb80f1942795061d1de2e92d39ff36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolGetSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchQueueSize")
    def thread_pool_search_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchQueueSize"))

    @thread_pool_search_queue_size.setter
    def thread_pool_search_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34ebe8e9e072887f12d86580526d8ac16373c5aab6fc4191f7cd3046e4bdaf73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchSize")
    def thread_pool_search_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchSize"))

    @thread_pool_search_size.setter
    def thread_pool_search_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25b5a83bba7756ff01419878048c5ab3a753831d3f79ffec1dbe1d3f2c9ea4db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledQueueSize")
    def thread_pool_search_throttled_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchThrottledQueueSize"))

    @thread_pool_search_throttled_queue_size.setter
    def thread_pool_search_throttled_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bed451550dec41a2da732974cd1923cfbba4bbe589d3c3345362430b5cffa659)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchThrottledQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolSearchThrottledSize")
    def thread_pool_search_throttled_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolSearchThrottledSize"))

    @thread_pool_search_throttled_size.setter
    def thread_pool_search_throttled_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1438055b511e40e99d4b382c18b9a7045a4fcf590f6108bd9f77c24f1652b81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolSearchThrottledSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteQueueSize")
    def thread_pool_write_queue_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolWriteQueueSize"))

    @thread_pool_write_queue_size.setter
    def thread_pool_write_queue_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ddeb333a1db523915e0aa6e17437ae9bc063e33990a896c43b0ef152e492a69d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolWriteQueueSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="threadPoolWriteSize")
    def thread_pool_write_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "threadPoolWriteSize"))

    @thread_pool_write_size.setter
    def thread_pool_write_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09937a2e29b01ae2a44bea884ccbec6263e7a778146a313c6341904db84497cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "threadPoolWriteSize", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseOpensearchConfig.DatabaseOpensearchConfigConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "cluster_id": "clusterId",
        "action_auto_create_index_enabled": "actionAutoCreateIndexEnabled",
        "action_destructive_requires_name": "actionDestructiveRequiresName",
        "cluster_max_shards_per_node": "clusterMaxShardsPerNode",
        "cluster_routing_allocation_node_concurrent_recoveries": "clusterRoutingAllocationNodeConcurrentRecoveries",
        "enable_security_audit": "enableSecurityAudit",
        "http_max_content_length_bytes": "httpMaxContentLengthBytes",
        "http_max_header_size_bytes": "httpMaxHeaderSizeBytes",
        "http_max_initial_line_length_bytes": "httpMaxInitialLineLengthBytes",
        "id": "id",
        "indices_fielddata_cache_size_percentage": "indicesFielddataCacheSizePercentage",
        "indices_memory_index_buffer_size_percentage": "indicesMemoryIndexBufferSizePercentage",
        "indices_memory_max_index_buffer_size_mb": "indicesMemoryMaxIndexBufferSizeMb",
        "indices_memory_min_index_buffer_size_mb": "indicesMemoryMinIndexBufferSizeMb",
        "indices_queries_cache_size_percentage": "indicesQueriesCacheSizePercentage",
        "indices_query_bool_max_clause_count": "indicesQueryBoolMaxClauseCount",
        "indices_recovery_max_concurrent_file_chunks": "indicesRecoveryMaxConcurrentFileChunks",
        "indices_recovery_max_mb_per_sec": "indicesRecoveryMaxMbPerSec",
        "ism_enabled": "ismEnabled",
        "ism_history_enabled": "ismHistoryEnabled",
        "ism_history_max_age_hours": "ismHistoryMaxAgeHours",
        "ism_history_max_docs": "ismHistoryMaxDocs",
        "ism_history_rollover_check_period_hours": "ismHistoryRolloverCheckPeriodHours",
        "ism_history_rollover_retention_period_days": "ismHistoryRolloverRetentionPeriodDays",
        "override_main_response_version": "overrideMainResponseVersion",
        "plugins_alerting_filter_by_backend_roles_enabled": "pluginsAlertingFilterByBackendRolesEnabled",
        "reindex_remote_whitelist": "reindexRemoteWhitelist",
        "script_max_compilations_rate": "scriptMaxCompilationsRate",
        "search_max_buckets": "searchMaxBuckets",
        "thread_pool_analyze_queue_size": "threadPoolAnalyzeQueueSize",
        "thread_pool_analyze_size": "threadPoolAnalyzeSize",
        "thread_pool_force_merge_size": "threadPoolForceMergeSize",
        "thread_pool_get_queue_size": "threadPoolGetQueueSize",
        "thread_pool_get_size": "threadPoolGetSize",
        "thread_pool_search_queue_size": "threadPoolSearchQueueSize",
        "thread_pool_search_size": "threadPoolSearchSize",
        "thread_pool_search_throttled_queue_size": "threadPoolSearchThrottledQueueSize",
        "thread_pool_search_throttled_size": "threadPoolSearchThrottledSize",
        "thread_pool_write_queue_size": "threadPoolWriteQueueSize",
        "thread_pool_write_size": "threadPoolWriteSize",
    },
)
class DatabaseOpensearchConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
        cluster_id: builtins.str,
        action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
        cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
        enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        http_max_content_length_bytes: typing.Optional[jsii.Number] = None,
        http_max_header_size_bytes: typing.Optional[jsii.Number] = None,
        http_max_initial_line_length_bytes: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        indices_fielddata_cache_size_percentage: typing.Optional[jsii.Number] = None,
        indices_memory_index_buffer_size_percentage: typing.Optional[jsii.Number] = None,
        indices_memory_max_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
        indices_memory_min_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
        indices_queries_cache_size_percentage: typing.Optional[jsii.Number] = None,
        indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
        indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
        indices_recovery_max_mb_per_sec: typing.Optional[jsii.Number] = None,
        ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        ism_history_max_age_hours: typing.Optional[jsii.Number] = None,
        ism_history_max_docs: typing.Optional[jsii.Number] = None,
        ism_history_rollover_check_period_hours: typing.Optional[jsii.Number] = None,
        ism_history_rollover_retention_period_days: typing.Optional[jsii.Number] = None,
        override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        plugins_alerting_filter_by_backend_roles_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
        script_max_compilations_rate: typing.Optional[builtins.str] = None,
        search_max_buckets: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
        thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_get_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
        thread_pool_write_size: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_id DatabaseOpensearchConfig#cluster_id}.
        :param action_auto_create_index_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#action_auto_create_index_enabled DatabaseOpensearchConfig#action_auto_create_index_enabled}.
        :param action_destructive_requires_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#action_destructive_requires_name DatabaseOpensearchConfig#action_destructive_requires_name}.
        :param cluster_max_shards_per_node: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_max_shards_per_node DatabaseOpensearchConfig#cluster_max_shards_per_node}.
        :param cluster_routing_allocation_node_concurrent_recoveries: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_routing_allocation_node_concurrent_recoveries DatabaseOpensearchConfig#cluster_routing_allocation_node_concurrent_recoveries}.
        :param enable_security_audit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#enable_security_audit DatabaseOpensearchConfig#enable_security_audit}.
        :param http_max_content_length_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_content_length_bytes DatabaseOpensearchConfig#http_max_content_length_bytes}.
        :param http_max_header_size_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_header_size_bytes DatabaseOpensearchConfig#http_max_header_size_bytes}.
        :param http_max_initial_line_length_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_initial_line_length_bytes DatabaseOpensearchConfig#http_max_initial_line_length_bytes}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#id DatabaseOpensearchConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param indices_fielddata_cache_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_fielddata_cache_size_percentage DatabaseOpensearchConfig#indices_fielddata_cache_size_percentage}.
        :param indices_memory_index_buffer_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_index_buffer_size_percentage DatabaseOpensearchConfig#indices_memory_index_buffer_size_percentage}.
        :param indices_memory_max_index_buffer_size_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_max_index_buffer_size_mb DatabaseOpensearchConfig#indices_memory_max_index_buffer_size_mb}.
        :param indices_memory_min_index_buffer_size_mb: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_min_index_buffer_size_mb DatabaseOpensearchConfig#indices_memory_min_index_buffer_size_mb}.
        :param indices_queries_cache_size_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_queries_cache_size_percentage DatabaseOpensearchConfig#indices_queries_cache_size_percentage}.
        :param indices_query_bool_max_clause_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_query_bool_max_clause_count DatabaseOpensearchConfig#indices_query_bool_max_clause_count}.
        :param indices_recovery_max_concurrent_file_chunks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_recovery_max_concurrent_file_chunks DatabaseOpensearchConfig#indices_recovery_max_concurrent_file_chunks}.
        :param indices_recovery_max_mb_per_sec: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_recovery_max_mb_per_sec DatabaseOpensearchConfig#indices_recovery_max_mb_per_sec}.
        :param ism_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_enabled DatabaseOpensearchConfig#ism_enabled}.
        :param ism_history_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_enabled DatabaseOpensearchConfig#ism_history_enabled}.
        :param ism_history_max_age_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_max_age_hours DatabaseOpensearchConfig#ism_history_max_age_hours}.
        :param ism_history_max_docs: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_max_docs DatabaseOpensearchConfig#ism_history_max_docs}.
        :param ism_history_rollover_check_period_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_rollover_check_period_hours DatabaseOpensearchConfig#ism_history_rollover_check_period_hours}.
        :param ism_history_rollover_retention_period_days: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_rollover_retention_period_days DatabaseOpensearchConfig#ism_history_rollover_retention_period_days}.
        :param override_main_response_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#override_main_response_version DatabaseOpensearchConfig#override_main_response_version}.
        :param plugins_alerting_filter_by_backend_roles_enabled: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#plugins_alerting_filter_by_backend_roles_enabled DatabaseOpensearchConfig#plugins_alerting_filter_by_backend_roles_enabled}.
        :param reindex_remote_whitelist: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#reindex_remote_whitelist DatabaseOpensearchConfig#reindex_remote_whitelist}.
        :param script_max_compilations_rate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#script_max_compilations_rate DatabaseOpensearchConfig#script_max_compilations_rate}.
        :param search_max_buckets: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#search_max_buckets DatabaseOpensearchConfig#search_max_buckets}.
        :param thread_pool_analyze_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_analyze_queue_size DatabaseOpensearchConfig#thread_pool_analyze_queue_size}.
        :param thread_pool_analyze_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_analyze_size DatabaseOpensearchConfig#thread_pool_analyze_size}.
        :param thread_pool_force_merge_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_force_merge_size DatabaseOpensearchConfig#thread_pool_force_merge_size}.
        :param thread_pool_get_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_get_queue_size DatabaseOpensearchConfig#thread_pool_get_queue_size}.
        :param thread_pool_get_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_get_size DatabaseOpensearchConfig#thread_pool_get_size}.
        :param thread_pool_search_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_queue_size DatabaseOpensearchConfig#thread_pool_search_queue_size}.
        :param thread_pool_search_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_size DatabaseOpensearchConfig#thread_pool_search_size}.
        :param thread_pool_search_throttled_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_throttled_queue_size DatabaseOpensearchConfig#thread_pool_search_throttled_queue_size}.
        :param thread_pool_search_throttled_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_throttled_size DatabaseOpensearchConfig#thread_pool_search_throttled_size}.
        :param thread_pool_write_queue_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_write_queue_size DatabaseOpensearchConfig#thread_pool_write_queue_size}.
        :param thread_pool_write_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_write_size DatabaseOpensearchConfig#thread_pool_write_size}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7f2aff8afd0d60ec53f7422a2b76a53c70cb6144a8858099191fb9e2f4de991)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument action_auto_create_index_enabled", value=action_auto_create_index_enabled, expected_type=type_hints["action_auto_create_index_enabled"])
            check_type(argname="argument action_destructive_requires_name", value=action_destructive_requires_name, expected_type=type_hints["action_destructive_requires_name"])
            check_type(argname="argument cluster_max_shards_per_node", value=cluster_max_shards_per_node, expected_type=type_hints["cluster_max_shards_per_node"])
            check_type(argname="argument cluster_routing_allocation_node_concurrent_recoveries", value=cluster_routing_allocation_node_concurrent_recoveries, expected_type=type_hints["cluster_routing_allocation_node_concurrent_recoveries"])
            check_type(argname="argument enable_security_audit", value=enable_security_audit, expected_type=type_hints["enable_security_audit"])
            check_type(argname="argument http_max_content_length_bytes", value=http_max_content_length_bytes, expected_type=type_hints["http_max_content_length_bytes"])
            check_type(argname="argument http_max_header_size_bytes", value=http_max_header_size_bytes, expected_type=type_hints["http_max_header_size_bytes"])
            check_type(argname="argument http_max_initial_line_length_bytes", value=http_max_initial_line_length_bytes, expected_type=type_hints["http_max_initial_line_length_bytes"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument indices_fielddata_cache_size_percentage", value=indices_fielddata_cache_size_percentage, expected_type=type_hints["indices_fielddata_cache_size_percentage"])
            check_type(argname="argument indices_memory_index_buffer_size_percentage", value=indices_memory_index_buffer_size_percentage, expected_type=type_hints["indices_memory_index_buffer_size_percentage"])
            check_type(argname="argument indices_memory_max_index_buffer_size_mb", value=indices_memory_max_index_buffer_size_mb, expected_type=type_hints["indices_memory_max_index_buffer_size_mb"])
            check_type(argname="argument indices_memory_min_index_buffer_size_mb", value=indices_memory_min_index_buffer_size_mb, expected_type=type_hints["indices_memory_min_index_buffer_size_mb"])
            check_type(argname="argument indices_queries_cache_size_percentage", value=indices_queries_cache_size_percentage, expected_type=type_hints["indices_queries_cache_size_percentage"])
            check_type(argname="argument indices_query_bool_max_clause_count", value=indices_query_bool_max_clause_count, expected_type=type_hints["indices_query_bool_max_clause_count"])
            check_type(argname="argument indices_recovery_max_concurrent_file_chunks", value=indices_recovery_max_concurrent_file_chunks, expected_type=type_hints["indices_recovery_max_concurrent_file_chunks"])
            check_type(argname="argument indices_recovery_max_mb_per_sec", value=indices_recovery_max_mb_per_sec, expected_type=type_hints["indices_recovery_max_mb_per_sec"])
            check_type(argname="argument ism_enabled", value=ism_enabled, expected_type=type_hints["ism_enabled"])
            check_type(argname="argument ism_history_enabled", value=ism_history_enabled, expected_type=type_hints["ism_history_enabled"])
            check_type(argname="argument ism_history_max_age_hours", value=ism_history_max_age_hours, expected_type=type_hints["ism_history_max_age_hours"])
            check_type(argname="argument ism_history_max_docs", value=ism_history_max_docs, expected_type=type_hints["ism_history_max_docs"])
            check_type(argname="argument ism_history_rollover_check_period_hours", value=ism_history_rollover_check_period_hours, expected_type=type_hints["ism_history_rollover_check_period_hours"])
            check_type(argname="argument ism_history_rollover_retention_period_days", value=ism_history_rollover_retention_period_days, expected_type=type_hints["ism_history_rollover_retention_period_days"])
            check_type(argname="argument override_main_response_version", value=override_main_response_version, expected_type=type_hints["override_main_response_version"])
            check_type(argname="argument plugins_alerting_filter_by_backend_roles_enabled", value=plugins_alerting_filter_by_backend_roles_enabled, expected_type=type_hints["plugins_alerting_filter_by_backend_roles_enabled"])
            check_type(argname="argument reindex_remote_whitelist", value=reindex_remote_whitelist, expected_type=type_hints["reindex_remote_whitelist"])
            check_type(argname="argument script_max_compilations_rate", value=script_max_compilations_rate, expected_type=type_hints["script_max_compilations_rate"])
            check_type(argname="argument search_max_buckets", value=search_max_buckets, expected_type=type_hints["search_max_buckets"])
            check_type(argname="argument thread_pool_analyze_queue_size", value=thread_pool_analyze_queue_size, expected_type=type_hints["thread_pool_analyze_queue_size"])
            check_type(argname="argument thread_pool_analyze_size", value=thread_pool_analyze_size, expected_type=type_hints["thread_pool_analyze_size"])
            check_type(argname="argument thread_pool_force_merge_size", value=thread_pool_force_merge_size, expected_type=type_hints["thread_pool_force_merge_size"])
            check_type(argname="argument thread_pool_get_queue_size", value=thread_pool_get_queue_size, expected_type=type_hints["thread_pool_get_queue_size"])
            check_type(argname="argument thread_pool_get_size", value=thread_pool_get_size, expected_type=type_hints["thread_pool_get_size"])
            check_type(argname="argument thread_pool_search_queue_size", value=thread_pool_search_queue_size, expected_type=type_hints["thread_pool_search_queue_size"])
            check_type(argname="argument thread_pool_search_size", value=thread_pool_search_size, expected_type=type_hints["thread_pool_search_size"])
            check_type(argname="argument thread_pool_search_throttled_queue_size", value=thread_pool_search_throttled_queue_size, expected_type=type_hints["thread_pool_search_throttled_queue_size"])
            check_type(argname="argument thread_pool_search_throttled_size", value=thread_pool_search_throttled_size, expected_type=type_hints["thread_pool_search_throttled_size"])
            check_type(argname="argument thread_pool_write_queue_size", value=thread_pool_write_queue_size, expected_type=type_hints["thread_pool_write_queue_size"])
            check_type(argname="argument thread_pool_write_size", value=thread_pool_write_size, expected_type=type_hints["thread_pool_write_size"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_id": cluster_id,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if action_auto_create_index_enabled is not None:
            self._values["action_auto_create_index_enabled"] = action_auto_create_index_enabled
        if action_destructive_requires_name is not None:
            self._values["action_destructive_requires_name"] = action_destructive_requires_name
        if cluster_max_shards_per_node is not None:
            self._values["cluster_max_shards_per_node"] = cluster_max_shards_per_node
        if cluster_routing_allocation_node_concurrent_recoveries is not None:
            self._values["cluster_routing_allocation_node_concurrent_recoveries"] = cluster_routing_allocation_node_concurrent_recoveries
        if enable_security_audit is not None:
            self._values["enable_security_audit"] = enable_security_audit
        if http_max_content_length_bytes is not None:
            self._values["http_max_content_length_bytes"] = http_max_content_length_bytes
        if http_max_header_size_bytes is not None:
            self._values["http_max_header_size_bytes"] = http_max_header_size_bytes
        if http_max_initial_line_length_bytes is not None:
            self._values["http_max_initial_line_length_bytes"] = http_max_initial_line_length_bytes
        if id is not None:
            self._values["id"] = id
        if indices_fielddata_cache_size_percentage is not None:
            self._values["indices_fielddata_cache_size_percentage"] = indices_fielddata_cache_size_percentage
        if indices_memory_index_buffer_size_percentage is not None:
            self._values["indices_memory_index_buffer_size_percentage"] = indices_memory_index_buffer_size_percentage
        if indices_memory_max_index_buffer_size_mb is not None:
            self._values["indices_memory_max_index_buffer_size_mb"] = indices_memory_max_index_buffer_size_mb
        if indices_memory_min_index_buffer_size_mb is not None:
            self._values["indices_memory_min_index_buffer_size_mb"] = indices_memory_min_index_buffer_size_mb
        if indices_queries_cache_size_percentage is not None:
            self._values["indices_queries_cache_size_percentage"] = indices_queries_cache_size_percentage
        if indices_query_bool_max_clause_count is not None:
            self._values["indices_query_bool_max_clause_count"] = indices_query_bool_max_clause_count
        if indices_recovery_max_concurrent_file_chunks is not None:
            self._values["indices_recovery_max_concurrent_file_chunks"] = indices_recovery_max_concurrent_file_chunks
        if indices_recovery_max_mb_per_sec is not None:
            self._values["indices_recovery_max_mb_per_sec"] = indices_recovery_max_mb_per_sec
        if ism_enabled is not None:
            self._values["ism_enabled"] = ism_enabled
        if ism_history_enabled is not None:
            self._values["ism_history_enabled"] = ism_history_enabled
        if ism_history_max_age_hours is not None:
            self._values["ism_history_max_age_hours"] = ism_history_max_age_hours
        if ism_history_max_docs is not None:
            self._values["ism_history_max_docs"] = ism_history_max_docs
        if ism_history_rollover_check_period_hours is not None:
            self._values["ism_history_rollover_check_period_hours"] = ism_history_rollover_check_period_hours
        if ism_history_rollover_retention_period_days is not None:
            self._values["ism_history_rollover_retention_period_days"] = ism_history_rollover_retention_period_days
        if override_main_response_version is not None:
            self._values["override_main_response_version"] = override_main_response_version
        if plugins_alerting_filter_by_backend_roles_enabled is not None:
            self._values["plugins_alerting_filter_by_backend_roles_enabled"] = plugins_alerting_filter_by_backend_roles_enabled
        if reindex_remote_whitelist is not None:
            self._values["reindex_remote_whitelist"] = reindex_remote_whitelist
        if script_max_compilations_rate is not None:
            self._values["script_max_compilations_rate"] = script_max_compilations_rate
        if search_max_buckets is not None:
            self._values["search_max_buckets"] = search_max_buckets
        if thread_pool_analyze_queue_size is not None:
            self._values["thread_pool_analyze_queue_size"] = thread_pool_analyze_queue_size
        if thread_pool_analyze_size is not None:
            self._values["thread_pool_analyze_size"] = thread_pool_analyze_size
        if thread_pool_force_merge_size is not None:
            self._values["thread_pool_force_merge_size"] = thread_pool_force_merge_size
        if thread_pool_get_queue_size is not None:
            self._values["thread_pool_get_queue_size"] = thread_pool_get_queue_size
        if thread_pool_get_size is not None:
            self._values["thread_pool_get_size"] = thread_pool_get_size
        if thread_pool_search_queue_size is not None:
            self._values["thread_pool_search_queue_size"] = thread_pool_search_queue_size
        if thread_pool_search_size is not None:
            self._values["thread_pool_search_size"] = thread_pool_search_size
        if thread_pool_search_throttled_queue_size is not None:
            self._values["thread_pool_search_throttled_queue_size"] = thread_pool_search_throttled_queue_size
        if thread_pool_search_throttled_size is not None:
            self._values["thread_pool_search_throttled_size"] = thread_pool_search_throttled_size
        if thread_pool_write_queue_size is not None:
            self._values["thread_pool_write_queue_size"] = thread_pool_write_queue_size
        if thread_pool_write_size is not None:
            self._values["thread_pool_write_size"] = thread_pool_write_size

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, _cdktf_9a9027ec.WinrmProvisionerConnection]], result)

    @builtins.property
    def count(
        self,
    ) -> typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]], result)

    @builtins.property
    def depends_on(
        self,
    ) -> typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[_cdktf_9a9027ec.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[_cdktf_9a9027ec.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[_cdktf_9a9027ec.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[_cdktf_9a9027ec.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[_cdktf_9a9027ec.FileProvisioner, _cdktf_9a9027ec.LocalExecProvisioner, _cdktf_9a9027ec.RemoteExecProvisioner]]], result)

    @builtins.property
    def cluster_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_id DatabaseOpensearchConfig#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def action_auto_create_index_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#action_auto_create_index_enabled DatabaseOpensearchConfig#action_auto_create_index_enabled}.'''
        result = self._values.get("action_auto_create_index_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def action_destructive_requires_name(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#action_destructive_requires_name DatabaseOpensearchConfig#action_destructive_requires_name}.'''
        result = self._values.get("action_destructive_requires_name")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def cluster_max_shards_per_node(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_max_shards_per_node DatabaseOpensearchConfig#cluster_max_shards_per_node}.'''
        result = self._values.get("cluster_max_shards_per_node")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def cluster_routing_allocation_node_concurrent_recoveries(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#cluster_routing_allocation_node_concurrent_recoveries DatabaseOpensearchConfig#cluster_routing_allocation_node_concurrent_recoveries}.'''
        result = self._values.get("cluster_routing_allocation_node_concurrent_recoveries")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def enable_security_audit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#enable_security_audit DatabaseOpensearchConfig#enable_security_audit}.'''
        result = self._values.get("enable_security_audit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def http_max_content_length_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_content_length_bytes DatabaseOpensearchConfig#http_max_content_length_bytes}.'''
        result = self._values.get("http_max_content_length_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_max_header_size_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_header_size_bytes DatabaseOpensearchConfig#http_max_header_size_bytes}.'''
        result = self._values.get("http_max_header_size_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_max_initial_line_length_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#http_max_initial_line_length_bytes DatabaseOpensearchConfig#http_max_initial_line_length_bytes}.'''
        result = self._values.get("http_max_initial_line_length_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#id DatabaseOpensearchConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def indices_fielddata_cache_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_fielddata_cache_size_percentage DatabaseOpensearchConfig#indices_fielddata_cache_size_percentage}.'''
        result = self._values.get("indices_fielddata_cache_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_index_buffer_size_percentage(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_index_buffer_size_percentage DatabaseOpensearchConfig#indices_memory_index_buffer_size_percentage}.'''
        result = self._values.get("indices_memory_index_buffer_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_max_index_buffer_size_mb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_max_index_buffer_size_mb DatabaseOpensearchConfig#indices_memory_max_index_buffer_size_mb}.'''
        result = self._values.get("indices_memory_max_index_buffer_size_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_memory_min_index_buffer_size_mb(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_memory_min_index_buffer_size_mb DatabaseOpensearchConfig#indices_memory_min_index_buffer_size_mb}.'''
        result = self._values.get("indices_memory_min_index_buffer_size_mb")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_queries_cache_size_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_queries_cache_size_percentage DatabaseOpensearchConfig#indices_queries_cache_size_percentage}.'''
        result = self._values.get("indices_queries_cache_size_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_query_bool_max_clause_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_query_bool_max_clause_count DatabaseOpensearchConfig#indices_query_bool_max_clause_count}.'''
        result = self._values.get("indices_query_bool_max_clause_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_recovery_max_concurrent_file_chunks(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_recovery_max_concurrent_file_chunks DatabaseOpensearchConfig#indices_recovery_max_concurrent_file_chunks}.'''
        result = self._values.get("indices_recovery_max_concurrent_file_chunks")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def indices_recovery_max_mb_per_sec(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#indices_recovery_max_mb_per_sec DatabaseOpensearchConfig#indices_recovery_max_mb_per_sec}.'''
        result = self._values.get("indices_recovery_max_mb_per_sec")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_enabled DatabaseOpensearchConfig#ism_enabled}.'''
        result = self._values.get("ism_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ism_history_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_enabled DatabaseOpensearchConfig#ism_history_enabled}.'''
        result = self._values.get("ism_history_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def ism_history_max_age_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_max_age_hours DatabaseOpensearchConfig#ism_history_max_age_hours}.'''
        result = self._values.get("ism_history_max_age_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_max_docs(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_max_docs DatabaseOpensearchConfig#ism_history_max_docs}.'''
        result = self._values.get("ism_history_max_docs")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_rollover_check_period_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_rollover_check_period_hours DatabaseOpensearchConfig#ism_history_rollover_check_period_hours}.'''
        result = self._values.get("ism_history_rollover_check_period_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ism_history_rollover_retention_period_days(
        self,
    ) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#ism_history_rollover_retention_period_days DatabaseOpensearchConfig#ism_history_rollover_retention_period_days}.'''
        result = self._values.get("ism_history_rollover_retention_period_days")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def override_main_response_version(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#override_main_response_version DatabaseOpensearchConfig#override_main_response_version}.'''
        result = self._values.get("override_main_response_version")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def plugins_alerting_filter_by_backend_roles_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#plugins_alerting_filter_by_backend_roles_enabled DatabaseOpensearchConfig#plugins_alerting_filter_by_backend_roles_enabled}.'''
        result = self._values.get("plugins_alerting_filter_by_backend_roles_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def reindex_remote_whitelist(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#reindex_remote_whitelist DatabaseOpensearchConfig#reindex_remote_whitelist}.'''
        result = self._values.get("reindex_remote_whitelist")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def script_max_compilations_rate(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#script_max_compilations_rate DatabaseOpensearchConfig#script_max_compilations_rate}.'''
        result = self._values.get("script_max_compilations_rate")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def search_max_buckets(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#search_max_buckets DatabaseOpensearchConfig#search_max_buckets}.'''
        result = self._values.get("search_max_buckets")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_analyze_queue_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_analyze_queue_size DatabaseOpensearchConfig#thread_pool_analyze_queue_size}.'''
        result = self._values.get("thread_pool_analyze_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_analyze_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_analyze_size DatabaseOpensearchConfig#thread_pool_analyze_size}.'''
        result = self._values.get("thread_pool_analyze_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_force_merge_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_force_merge_size DatabaseOpensearchConfig#thread_pool_force_merge_size}.'''
        result = self._values.get("thread_pool_force_merge_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_get_queue_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_get_queue_size DatabaseOpensearchConfig#thread_pool_get_queue_size}.'''
        result = self._values.get("thread_pool_get_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_get_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_get_size DatabaseOpensearchConfig#thread_pool_get_size}.'''
        result = self._values.get("thread_pool_get_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_queue_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_queue_size DatabaseOpensearchConfig#thread_pool_search_queue_size}.'''
        result = self._values.get("thread_pool_search_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_size DatabaseOpensearchConfig#thread_pool_search_size}.'''
        result = self._values.get("thread_pool_search_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_throttled_queue_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_throttled_queue_size DatabaseOpensearchConfig#thread_pool_search_throttled_queue_size}.'''
        result = self._values.get("thread_pool_search_throttled_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_search_throttled_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_search_throttled_size DatabaseOpensearchConfig#thread_pool_search_throttled_size}.'''
        result = self._values.get("thread_pool_search_throttled_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_write_queue_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_write_queue_size DatabaseOpensearchConfig#thread_pool_write_queue_size}.'''
        result = self._values.get("thread_pool_write_queue_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def thread_pool_write_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_opensearch_config#thread_pool_write_size DatabaseOpensearchConfig#thread_pool_write_size}.'''
        result = self._values.get("thread_pool_write_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseOpensearchConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabaseOpensearchConfig",
    "DatabaseOpensearchConfigConfig",
]

publication.publish()

def _typecheckingstub__8c924a1b6e565523254849e1f0b78bc26d3f7dd88f726992c3e5dea55194492d(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
    cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
    enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http_max_content_length_bytes: typing.Optional[jsii.Number] = None,
    http_max_header_size_bytes: typing.Optional[jsii.Number] = None,
    http_max_initial_line_length_bytes: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    indices_fielddata_cache_size_percentage: typing.Optional[jsii.Number] = None,
    indices_memory_index_buffer_size_percentage: typing.Optional[jsii.Number] = None,
    indices_memory_max_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
    indices_memory_min_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
    indices_queries_cache_size_percentage: typing.Optional[jsii.Number] = None,
    indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
    indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
    indices_recovery_max_mb_per_sec: typing.Optional[jsii.Number] = None,
    ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_max_age_hours: typing.Optional[jsii.Number] = None,
    ism_history_max_docs: typing.Optional[jsii.Number] = None,
    ism_history_rollover_check_period_hours: typing.Optional[jsii.Number] = None,
    ism_history_rollover_retention_period_days: typing.Optional[jsii.Number] = None,
    override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    plugins_alerting_filter_by_backend_roles_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
    script_max_compilations_rate: typing.Optional[builtins.str] = None,
    search_max_buckets: typing.Optional[jsii.Number] = None,
    thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
    thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_size: typing.Optional[jsii.Number] = None,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d4f045519f5f167aca47752b083f16ea3952e0a56e2f3cea970dc37890e0a07(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__793bd87f76bb64c65c3518d19916fadddf7c05914444ab9d63c8b8b52e7440b4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f654b96f9444d7028748355ef4402ba97ef5abeade48455d5f88cff514df7cca(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6bac83d9b7f21f8105ade0b6b6bfb8f396e33f88118566e2f994ba6686421a0d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d11dfbfd7ac566772e54358ba7c077012fdfcdadfa50f7d38c4212292ed67bcb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7179a5b2d4a0197d89b5f1daa6bee9b03f4b138984da6ab9c852c0f1de3aad7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2fbaf80968215f381b4657bf2965514c1c021e487054ad3c96a2b3c24218976(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f61bd14ce728920ecf9c3674c64ee23806dacd7af5590dc48ff1c599a262b05(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__111504209914657846de86f85d407ca8f8667242eca5942ec7f8d2da6c3a3b1b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24a7c183e62b69dfb06af5e3d9185ddacbc7b1aaa5062d4feac3e830af524bfa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d06e273669a1430a1c26e4b8c9aec313cd16a599a3e9f34d9358a78892cc447(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30a677d9e9b58fd935a13f875723d7c0bf46d005a53bd1eba1f949da65563469(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c1310a6ed747183a70b43d5f952b4c5f666215a0fd5f1557c951b94cb875660(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acddd5257856888f8fc96f7d940b5b019196af7b828d3dc19bf0f57054bfaea4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e70434500784890c6112c2c2f759920d746c020e53e3e13a65d70ca2b106ffb8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83f7adb4743b36359b3cc5bc881e14d89f48d854232703963c556405a0351ae7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__764b5afb878deca4d824f5f07e6776159a5043c71f605c7ba208f8732b1b03a3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a336628701a9f9cbb8b70f8ae61f170274e49c8e5033a8d5a522b935400aadee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e2d02085777d2bfdbddfcddd6e5257386389df68fe3c4ff72ee5bf9f093633d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a639894e660ca035ae5bec6ccf38442bb630ed602da78c4dcc536ed910fdd69e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46aec146c1f65a1f3b28d1e792f17f6162198f070aead65ee1521b3a5339858d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__882090ca7423435a4b6cd232c8d4bfba5798e5490acd0b28daf74a70aa6189a4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9d1d1bdbfd17a90a784a71f87facfa6f5c4e6cde9dda3ec0bbb88b29ca799f5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab69a57f9b8b35e8563da09146efb3647129c9c230c26cbad387ffe49face61a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be6bfab662ff248259ff30889ca3cf5ce42f38cfe77ceae639e9000f977cb92e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e947b0e992991975eae56dbb6055174b41cf7d0b3bbc475a280c6be7f9e20085(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96b24ca458194e389fb6002c24350a520e151f3ce99930fb07ca0820590d4f99(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d97f1c6f72e25014d6068e83cf048e9336e303555c339209022c9d4b92f5961b(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__41a3003eb94507101597c4515a81c6ec3d265e2160e2ff747723f12302b2e9fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15ccff43299751eb6c1ade9f9943efcf62e1ff11d8c383242797b65e211a5edb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70bfa2003f9c204a034b7ab10832acc2401937175437c1731b806315de5fde27(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6b1334515fc3a50540115e5a60c3cc2825a645dafdf5a9c5251223963ba2dd1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e27e43384edf708f234de11e89fd231cbe17df1c520fd24b72126b7fccb03558(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5873dea08d265502dcf3cbba72f783b6dfc500b65ec7038d07d45d2eb732675(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0d1cf80e6503197b5f6be9ff56455d78cfb80f1942795061d1de2e92d39ff36(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34ebe8e9e072887f12d86580526d8ac16373c5aab6fc4191f7cd3046e4bdaf73(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25b5a83bba7756ff01419878048c5ab3a753831d3f79ffec1dbe1d3f2c9ea4db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bed451550dec41a2da732974cd1923cfbba4bbe589d3c3345362430b5cffa659(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1438055b511e40e99d4b382c18b9a7045a4fcf590f6108bd9f77c24f1652b81(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ddeb333a1db523915e0aa6e17437ae9bc063e33990a896c43b0ef152e492a69d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09937a2e29b01ae2a44bea884ccbec6263e7a778146a313c6341904db84497cb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7f2aff8afd0d60ec53f7422a2b76a53c70cb6144a8858099191fb9e2f4de991(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    action_auto_create_index_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    action_destructive_requires_name: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    cluster_max_shards_per_node: typing.Optional[jsii.Number] = None,
    cluster_routing_allocation_node_concurrent_recoveries: typing.Optional[jsii.Number] = None,
    enable_security_audit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    http_max_content_length_bytes: typing.Optional[jsii.Number] = None,
    http_max_header_size_bytes: typing.Optional[jsii.Number] = None,
    http_max_initial_line_length_bytes: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    indices_fielddata_cache_size_percentage: typing.Optional[jsii.Number] = None,
    indices_memory_index_buffer_size_percentage: typing.Optional[jsii.Number] = None,
    indices_memory_max_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
    indices_memory_min_index_buffer_size_mb: typing.Optional[jsii.Number] = None,
    indices_queries_cache_size_percentage: typing.Optional[jsii.Number] = None,
    indices_query_bool_max_clause_count: typing.Optional[jsii.Number] = None,
    indices_recovery_max_concurrent_file_chunks: typing.Optional[jsii.Number] = None,
    indices_recovery_max_mb_per_sec: typing.Optional[jsii.Number] = None,
    ism_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ism_history_max_age_hours: typing.Optional[jsii.Number] = None,
    ism_history_max_docs: typing.Optional[jsii.Number] = None,
    ism_history_rollover_check_period_hours: typing.Optional[jsii.Number] = None,
    ism_history_rollover_retention_period_days: typing.Optional[jsii.Number] = None,
    override_main_response_version: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    plugins_alerting_filter_by_backend_roles_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    reindex_remote_whitelist: typing.Optional[typing.Sequence[builtins.str]] = None,
    script_max_compilations_rate: typing.Optional[builtins.str] = None,
    search_max_buckets: typing.Optional[jsii.Number] = None,
    thread_pool_analyze_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_analyze_size: typing.Optional[jsii.Number] = None,
    thread_pool_force_merge_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_get_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_search_throttled_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_queue_size: typing.Optional[jsii.Number] = None,
    thread_pool_write_size: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
