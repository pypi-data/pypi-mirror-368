r'''
# `digitalocean_database_kafka_config`

Refer to the Terraform Registry for docs: [`digitalocean_database_kafka_config`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config).
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


class DatabaseKafkaConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaConfig.DatabaseKafkaConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config digitalocean_database_kafka_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        auto_create_topics_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        group_initial_rebalance_delay_ms: typing.Optional[jsii.Number] = None,
        group_max_session_timeout_ms: typing.Optional[jsii.Number] = None,
        group_min_session_timeout_ms: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        log_cleaner_delete_retention_ms: typing.Optional[jsii.Number] = None,
        log_cleaner_min_compaction_lag_ms: typing.Optional[builtins.str] = None,
        log_flush_interval_ms: typing.Optional[builtins.str] = None,
        log_index_interval_bytes: typing.Optional[jsii.Number] = None,
        log_message_downconversion_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_message_timestamp_difference_max_ms: typing.Optional[builtins.str] = None,
        log_preallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_retention_bytes: typing.Optional[builtins.str] = None,
        log_retention_hours: typing.Optional[jsii.Number] = None,
        log_retention_ms: typing.Optional[builtins.str] = None,
        log_roll_jitter_ms: typing.Optional[builtins.str] = None,
        log_segment_delete_delay_ms: typing.Optional[jsii.Number] = None,
        message_max_bytes: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config digitalocean_database_kafka_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#cluster_id DatabaseKafkaConfig#cluster_id}.
        :param auto_create_topics_enable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#auto_create_topics_enable DatabaseKafkaConfig#auto_create_topics_enable}.
        :param group_initial_rebalance_delay_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_initial_rebalance_delay_ms DatabaseKafkaConfig#group_initial_rebalance_delay_ms}.
        :param group_max_session_timeout_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_max_session_timeout_ms DatabaseKafkaConfig#group_max_session_timeout_ms}.
        :param group_min_session_timeout_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_min_session_timeout_ms DatabaseKafkaConfig#group_min_session_timeout_ms}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#id DatabaseKafkaConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_cleaner_delete_retention_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_cleaner_delete_retention_ms DatabaseKafkaConfig#log_cleaner_delete_retention_ms}.
        :param log_cleaner_min_compaction_lag_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_cleaner_min_compaction_lag_ms DatabaseKafkaConfig#log_cleaner_min_compaction_lag_ms}.
        :param log_flush_interval_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_flush_interval_ms DatabaseKafkaConfig#log_flush_interval_ms}.
        :param log_index_interval_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_index_interval_bytes DatabaseKafkaConfig#log_index_interval_bytes}.
        :param log_message_downconversion_enable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_message_downconversion_enable DatabaseKafkaConfig#log_message_downconversion_enable}.
        :param log_message_timestamp_difference_max_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_message_timestamp_difference_max_ms DatabaseKafkaConfig#log_message_timestamp_difference_max_ms}.
        :param log_preallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_preallocate DatabaseKafkaConfig#log_preallocate}.
        :param log_retention_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_bytes DatabaseKafkaConfig#log_retention_bytes}.
        :param log_retention_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_hours DatabaseKafkaConfig#log_retention_hours}.
        :param log_retention_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_ms DatabaseKafkaConfig#log_retention_ms}.
        :param log_roll_jitter_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_roll_jitter_ms DatabaseKafkaConfig#log_roll_jitter_ms}.
        :param log_segment_delete_delay_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_segment_delete_delay_ms DatabaseKafkaConfig#log_segment_delete_delay_ms}.
        :param message_max_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#message_max_bytes DatabaseKafkaConfig#message_max_bytes}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62f5999c31181c3a938a19174be4045d6df32886db728e5fba07c93404d44029)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabaseKafkaConfigConfig(
            cluster_id=cluster_id,
            auto_create_topics_enable=auto_create_topics_enable,
            group_initial_rebalance_delay_ms=group_initial_rebalance_delay_ms,
            group_max_session_timeout_ms=group_max_session_timeout_ms,
            group_min_session_timeout_ms=group_min_session_timeout_ms,
            id=id,
            log_cleaner_delete_retention_ms=log_cleaner_delete_retention_ms,
            log_cleaner_min_compaction_lag_ms=log_cleaner_min_compaction_lag_ms,
            log_flush_interval_ms=log_flush_interval_ms,
            log_index_interval_bytes=log_index_interval_bytes,
            log_message_downconversion_enable=log_message_downconversion_enable,
            log_message_timestamp_difference_max_ms=log_message_timestamp_difference_max_ms,
            log_preallocate=log_preallocate,
            log_retention_bytes=log_retention_bytes,
            log_retention_hours=log_retention_hours,
            log_retention_ms=log_retention_ms,
            log_roll_jitter_ms=log_roll_jitter_ms,
            log_segment_delete_delay_ms=log_segment_delete_delay_ms,
            message_max_bytes=message_max_bytes,
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
        '''Generates CDKTF code for importing a DatabaseKafkaConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseKafkaConfig to import.
        :param import_from_id: The id of the existing DatabaseKafkaConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseKafkaConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8dd30ecf92dca1b2ce61f310c5aa1877b6633a25f4ee0380cc922a2e4eb8207)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAutoCreateTopicsEnable")
    def reset_auto_create_topics_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutoCreateTopicsEnable", []))

    @jsii.member(jsii_name="resetGroupInitialRebalanceDelayMs")
    def reset_group_initial_rebalance_delay_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupInitialRebalanceDelayMs", []))

    @jsii.member(jsii_name="resetGroupMaxSessionTimeoutMs")
    def reset_group_max_session_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupMaxSessionTimeoutMs", []))

    @jsii.member(jsii_name="resetGroupMinSessionTimeoutMs")
    def reset_group_min_session_timeout_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupMinSessionTimeoutMs", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetLogCleanerDeleteRetentionMs")
    def reset_log_cleaner_delete_retention_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogCleanerDeleteRetentionMs", []))

    @jsii.member(jsii_name="resetLogCleanerMinCompactionLagMs")
    def reset_log_cleaner_min_compaction_lag_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogCleanerMinCompactionLagMs", []))

    @jsii.member(jsii_name="resetLogFlushIntervalMs")
    def reset_log_flush_interval_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogFlushIntervalMs", []))

    @jsii.member(jsii_name="resetLogIndexIntervalBytes")
    def reset_log_index_interval_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogIndexIntervalBytes", []))

    @jsii.member(jsii_name="resetLogMessageDownconversionEnable")
    def reset_log_message_downconversion_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogMessageDownconversionEnable", []))

    @jsii.member(jsii_name="resetLogMessageTimestampDifferenceMaxMs")
    def reset_log_message_timestamp_difference_max_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogMessageTimestampDifferenceMaxMs", []))

    @jsii.member(jsii_name="resetLogPreallocate")
    def reset_log_preallocate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogPreallocate", []))

    @jsii.member(jsii_name="resetLogRetentionBytes")
    def reset_log_retention_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogRetentionBytes", []))

    @jsii.member(jsii_name="resetLogRetentionHours")
    def reset_log_retention_hours(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogRetentionHours", []))

    @jsii.member(jsii_name="resetLogRetentionMs")
    def reset_log_retention_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogRetentionMs", []))

    @jsii.member(jsii_name="resetLogRollJitterMs")
    def reset_log_roll_jitter_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogRollJitterMs", []))

    @jsii.member(jsii_name="resetLogSegmentDeleteDelayMs")
    def reset_log_segment_delete_delay_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogSegmentDeleteDelayMs", []))

    @jsii.member(jsii_name="resetMessageMaxBytes")
    def reset_message_max_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageMaxBytes", []))

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
    @jsii.member(jsii_name="autoCreateTopicsEnableInput")
    def auto_create_topics_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "autoCreateTopicsEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="groupInitialRebalanceDelayMsInput")
    def group_initial_rebalance_delay_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "groupInitialRebalanceDelayMsInput"))

    @builtins.property
    @jsii.member(jsii_name="groupMaxSessionTimeoutMsInput")
    def group_max_session_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "groupMaxSessionTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="groupMinSessionTimeoutMsInput")
    def group_min_session_timeout_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "groupMinSessionTimeoutMsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="logCleanerDeleteRetentionMsInput")
    def log_cleaner_delete_retention_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logCleanerDeleteRetentionMsInput"))

    @builtins.property
    @jsii.member(jsii_name="logCleanerMinCompactionLagMsInput")
    def log_cleaner_min_compaction_lag_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logCleanerMinCompactionLagMsInput"))

    @builtins.property
    @jsii.member(jsii_name="logFlushIntervalMsInput")
    def log_flush_interval_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logFlushIntervalMsInput"))

    @builtins.property
    @jsii.member(jsii_name="logIndexIntervalBytesInput")
    def log_index_interval_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logIndexIntervalBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="logMessageDownconversionEnableInput")
    def log_message_downconversion_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logMessageDownconversionEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="logMessageTimestampDifferenceMaxMsInput")
    def log_message_timestamp_difference_max_ms_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logMessageTimestampDifferenceMaxMsInput"))

    @builtins.property
    @jsii.member(jsii_name="logPreallocateInput")
    def log_preallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "logPreallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="logRetentionBytesInput")
    def log_retention_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logRetentionBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="logRetentionHoursInput")
    def log_retention_hours_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logRetentionHoursInput"))

    @builtins.property
    @jsii.member(jsii_name="logRetentionMsInput")
    def log_retention_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logRetentionMsInput"))

    @builtins.property
    @jsii.member(jsii_name="logRollJitterMsInput")
    def log_roll_jitter_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logRollJitterMsInput"))

    @builtins.property
    @jsii.member(jsii_name="logSegmentDeleteDelayMsInput")
    def log_segment_delete_delay_ms_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logSegmentDeleteDelayMsInput"))

    @builtins.property
    @jsii.member(jsii_name="messageMaxBytesInput")
    def message_max_bytes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "messageMaxBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="autoCreateTopicsEnable")
    def auto_create_topics_enable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "autoCreateTopicsEnable"))

    @auto_create_topics_enable.setter
    def auto_create_topics_enable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74186211b4c0177e80d95eed19301dc35b59cd10fc8785f58067701fb0178b5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autoCreateTopicsEnable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__352f14606db132757a65ba1f5ad9964546ce19b53c842176fe6dc4cfc524b36b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupInitialRebalanceDelayMs")
    def group_initial_rebalance_delay_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "groupInitialRebalanceDelayMs"))

    @group_initial_rebalance_delay_ms.setter
    def group_initial_rebalance_delay_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1c7c0c688e88eb6af79fab7b2d6df2ba47d5c899d93db5ee092b5160c8a5e44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupInitialRebalanceDelayMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupMaxSessionTimeoutMs")
    def group_max_session_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "groupMaxSessionTimeoutMs"))

    @group_max_session_timeout_ms.setter
    def group_max_session_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16e1a6fb53ed81217c5967628dd0dc5ddfe7164d748adebd529e36529b157f94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupMaxSessionTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupMinSessionTimeoutMs")
    def group_min_session_timeout_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "groupMinSessionTimeoutMs"))

    @group_min_session_timeout_ms.setter
    def group_min_session_timeout_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6b70584e491188367091d156689bd432cdb2897b6c51ae25dc63e9a72e382288)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupMinSessionTimeoutMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db230118f4c3bbc90f9b6a408dd487cf8571849ad2310919913f27e4868d6986)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logCleanerDeleteRetentionMs")
    def log_cleaner_delete_retention_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logCleanerDeleteRetentionMs"))

    @log_cleaner_delete_retention_ms.setter
    def log_cleaner_delete_retention_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7609bfc47e1cc6585e59056b79ead46b7be72c1a34df5910fb62d1245018ad98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logCleanerDeleteRetentionMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logCleanerMinCompactionLagMs")
    def log_cleaner_min_compaction_lag_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logCleanerMinCompactionLagMs"))

    @log_cleaner_min_compaction_lag_ms.setter
    def log_cleaner_min_compaction_lag_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fda1e9113cb9b7a4a4e051df78cb4506cc87d9e9b6b540f55c4e62ba1b5d66a7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logCleanerMinCompactionLagMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logFlushIntervalMs")
    def log_flush_interval_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logFlushIntervalMs"))

    @log_flush_interval_ms.setter
    def log_flush_interval_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__710118cec5562928e7f0366ff67b07db53d76bf3c6fe82820e5351cb68d6c2d8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logFlushIntervalMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logIndexIntervalBytes")
    def log_index_interval_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logIndexIntervalBytes"))

    @log_index_interval_bytes.setter
    def log_index_interval_bytes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9d4a322fc5ead5d40c70310c0b14864c81b1f9e372f959c6c62a7f2ac7bf503)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logIndexIntervalBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logMessageDownconversionEnable")
    def log_message_downconversion_enable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logMessageDownconversionEnable"))

    @log_message_downconversion_enable.setter
    def log_message_downconversion_enable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2f7b0ba2f95ddb34a1e918c7afba56b2dc8e8a6d3565f3b1545f1811c88f4ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logMessageDownconversionEnable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logMessageTimestampDifferenceMaxMs")
    def log_message_timestamp_difference_max_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logMessageTimestampDifferenceMaxMs"))

    @log_message_timestamp_difference_max_ms.setter
    def log_message_timestamp_difference_max_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b54880bd447ab18acfcb3ea24a6d04b4a6a0fc5f19c49a994ce3cebe24c8c74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logMessageTimestampDifferenceMaxMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logPreallocate")
    def log_preallocate(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "logPreallocate"))

    @log_preallocate.setter
    def log_preallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee28dbbd753c952bc5d668bdac3f639930882e675c865feaf73824b84f497a28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logPreallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRetentionBytes")
    def log_retention_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logRetentionBytes"))

    @log_retention_bytes.setter
    def log_retention_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff0368ee8bd211cf67a17e2bd1e75053600ae8db6b12112f276b8c49302f39c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRetentionBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRetentionHours")
    def log_retention_hours(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logRetentionHours"))

    @log_retention_hours.setter
    def log_retention_hours(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76f246b4a1c5101b0786c0e55f786809c36f9656c921a26b04811838fae95746)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRetentionHours", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRetentionMs")
    def log_retention_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logRetentionMs"))

    @log_retention_ms.setter
    def log_retention_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3625b480a251c3e6d6000497cde6f6fd5985e1bca2abff5d1a2b80fe147f38a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRetentionMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logRollJitterMs")
    def log_roll_jitter_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logRollJitterMs"))

    @log_roll_jitter_ms.setter
    def log_roll_jitter_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b543b57329a13867e632c54b659339d51802ef9fbe84533ea4364c029b63eb3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logRollJitterMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logSegmentDeleteDelayMs")
    def log_segment_delete_delay_ms(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logSegmentDeleteDelayMs"))

    @log_segment_delete_delay_ms.setter
    def log_segment_delete_delay_ms(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87f30c0e4f298e70d4b32d4a5e1f586dae7c579dab6b2b0772b371d05bb07a9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logSegmentDeleteDelayMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageMaxBytes")
    def message_max_bytes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "messageMaxBytes"))

    @message_max_bytes.setter
    def message_max_bytes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a88bbdfda388501b2a7e4dfdc7e774bbf11ddb3066c8da29f9e8df38f21d0c58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageMaxBytes", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaConfig.DatabaseKafkaConfigConfig",
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
        "auto_create_topics_enable": "autoCreateTopicsEnable",
        "group_initial_rebalance_delay_ms": "groupInitialRebalanceDelayMs",
        "group_max_session_timeout_ms": "groupMaxSessionTimeoutMs",
        "group_min_session_timeout_ms": "groupMinSessionTimeoutMs",
        "id": "id",
        "log_cleaner_delete_retention_ms": "logCleanerDeleteRetentionMs",
        "log_cleaner_min_compaction_lag_ms": "logCleanerMinCompactionLagMs",
        "log_flush_interval_ms": "logFlushIntervalMs",
        "log_index_interval_bytes": "logIndexIntervalBytes",
        "log_message_downconversion_enable": "logMessageDownconversionEnable",
        "log_message_timestamp_difference_max_ms": "logMessageTimestampDifferenceMaxMs",
        "log_preallocate": "logPreallocate",
        "log_retention_bytes": "logRetentionBytes",
        "log_retention_hours": "logRetentionHours",
        "log_retention_ms": "logRetentionMs",
        "log_roll_jitter_ms": "logRollJitterMs",
        "log_segment_delete_delay_ms": "logSegmentDeleteDelayMs",
        "message_max_bytes": "messageMaxBytes",
    },
)
class DatabaseKafkaConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        auto_create_topics_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        group_initial_rebalance_delay_ms: typing.Optional[jsii.Number] = None,
        group_max_session_timeout_ms: typing.Optional[jsii.Number] = None,
        group_min_session_timeout_ms: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        log_cleaner_delete_retention_ms: typing.Optional[jsii.Number] = None,
        log_cleaner_min_compaction_lag_ms: typing.Optional[builtins.str] = None,
        log_flush_interval_ms: typing.Optional[builtins.str] = None,
        log_index_interval_bytes: typing.Optional[jsii.Number] = None,
        log_message_downconversion_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_message_timestamp_difference_max_ms: typing.Optional[builtins.str] = None,
        log_preallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_retention_bytes: typing.Optional[builtins.str] = None,
        log_retention_hours: typing.Optional[jsii.Number] = None,
        log_retention_ms: typing.Optional[builtins.str] = None,
        log_roll_jitter_ms: typing.Optional[builtins.str] = None,
        log_segment_delete_delay_ms: typing.Optional[jsii.Number] = None,
        message_max_bytes: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#cluster_id DatabaseKafkaConfig#cluster_id}.
        :param auto_create_topics_enable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#auto_create_topics_enable DatabaseKafkaConfig#auto_create_topics_enable}.
        :param group_initial_rebalance_delay_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_initial_rebalance_delay_ms DatabaseKafkaConfig#group_initial_rebalance_delay_ms}.
        :param group_max_session_timeout_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_max_session_timeout_ms DatabaseKafkaConfig#group_max_session_timeout_ms}.
        :param group_min_session_timeout_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_min_session_timeout_ms DatabaseKafkaConfig#group_min_session_timeout_ms}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#id DatabaseKafkaConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param log_cleaner_delete_retention_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_cleaner_delete_retention_ms DatabaseKafkaConfig#log_cleaner_delete_retention_ms}.
        :param log_cleaner_min_compaction_lag_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_cleaner_min_compaction_lag_ms DatabaseKafkaConfig#log_cleaner_min_compaction_lag_ms}.
        :param log_flush_interval_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_flush_interval_ms DatabaseKafkaConfig#log_flush_interval_ms}.
        :param log_index_interval_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_index_interval_bytes DatabaseKafkaConfig#log_index_interval_bytes}.
        :param log_message_downconversion_enable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_message_downconversion_enable DatabaseKafkaConfig#log_message_downconversion_enable}.
        :param log_message_timestamp_difference_max_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_message_timestamp_difference_max_ms DatabaseKafkaConfig#log_message_timestamp_difference_max_ms}.
        :param log_preallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_preallocate DatabaseKafkaConfig#log_preallocate}.
        :param log_retention_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_bytes DatabaseKafkaConfig#log_retention_bytes}.
        :param log_retention_hours: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_hours DatabaseKafkaConfig#log_retention_hours}.
        :param log_retention_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_ms DatabaseKafkaConfig#log_retention_ms}.
        :param log_roll_jitter_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_roll_jitter_ms DatabaseKafkaConfig#log_roll_jitter_ms}.
        :param log_segment_delete_delay_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_segment_delete_delay_ms DatabaseKafkaConfig#log_segment_delete_delay_ms}.
        :param message_max_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#message_max_bytes DatabaseKafkaConfig#message_max_bytes}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61586145a2d4f13f6fed6109f4563978564044cefeaff0db391289810f90e25a)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument auto_create_topics_enable", value=auto_create_topics_enable, expected_type=type_hints["auto_create_topics_enable"])
            check_type(argname="argument group_initial_rebalance_delay_ms", value=group_initial_rebalance_delay_ms, expected_type=type_hints["group_initial_rebalance_delay_ms"])
            check_type(argname="argument group_max_session_timeout_ms", value=group_max_session_timeout_ms, expected_type=type_hints["group_max_session_timeout_ms"])
            check_type(argname="argument group_min_session_timeout_ms", value=group_min_session_timeout_ms, expected_type=type_hints["group_min_session_timeout_ms"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument log_cleaner_delete_retention_ms", value=log_cleaner_delete_retention_ms, expected_type=type_hints["log_cleaner_delete_retention_ms"])
            check_type(argname="argument log_cleaner_min_compaction_lag_ms", value=log_cleaner_min_compaction_lag_ms, expected_type=type_hints["log_cleaner_min_compaction_lag_ms"])
            check_type(argname="argument log_flush_interval_ms", value=log_flush_interval_ms, expected_type=type_hints["log_flush_interval_ms"])
            check_type(argname="argument log_index_interval_bytes", value=log_index_interval_bytes, expected_type=type_hints["log_index_interval_bytes"])
            check_type(argname="argument log_message_downconversion_enable", value=log_message_downconversion_enable, expected_type=type_hints["log_message_downconversion_enable"])
            check_type(argname="argument log_message_timestamp_difference_max_ms", value=log_message_timestamp_difference_max_ms, expected_type=type_hints["log_message_timestamp_difference_max_ms"])
            check_type(argname="argument log_preallocate", value=log_preallocate, expected_type=type_hints["log_preallocate"])
            check_type(argname="argument log_retention_bytes", value=log_retention_bytes, expected_type=type_hints["log_retention_bytes"])
            check_type(argname="argument log_retention_hours", value=log_retention_hours, expected_type=type_hints["log_retention_hours"])
            check_type(argname="argument log_retention_ms", value=log_retention_ms, expected_type=type_hints["log_retention_ms"])
            check_type(argname="argument log_roll_jitter_ms", value=log_roll_jitter_ms, expected_type=type_hints["log_roll_jitter_ms"])
            check_type(argname="argument log_segment_delete_delay_ms", value=log_segment_delete_delay_ms, expected_type=type_hints["log_segment_delete_delay_ms"])
            check_type(argname="argument message_max_bytes", value=message_max_bytes, expected_type=type_hints["message_max_bytes"])
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
        if auto_create_topics_enable is not None:
            self._values["auto_create_topics_enable"] = auto_create_topics_enable
        if group_initial_rebalance_delay_ms is not None:
            self._values["group_initial_rebalance_delay_ms"] = group_initial_rebalance_delay_ms
        if group_max_session_timeout_ms is not None:
            self._values["group_max_session_timeout_ms"] = group_max_session_timeout_ms
        if group_min_session_timeout_ms is not None:
            self._values["group_min_session_timeout_ms"] = group_min_session_timeout_ms
        if id is not None:
            self._values["id"] = id
        if log_cleaner_delete_retention_ms is not None:
            self._values["log_cleaner_delete_retention_ms"] = log_cleaner_delete_retention_ms
        if log_cleaner_min_compaction_lag_ms is not None:
            self._values["log_cleaner_min_compaction_lag_ms"] = log_cleaner_min_compaction_lag_ms
        if log_flush_interval_ms is not None:
            self._values["log_flush_interval_ms"] = log_flush_interval_ms
        if log_index_interval_bytes is not None:
            self._values["log_index_interval_bytes"] = log_index_interval_bytes
        if log_message_downconversion_enable is not None:
            self._values["log_message_downconversion_enable"] = log_message_downconversion_enable
        if log_message_timestamp_difference_max_ms is not None:
            self._values["log_message_timestamp_difference_max_ms"] = log_message_timestamp_difference_max_ms
        if log_preallocate is not None:
            self._values["log_preallocate"] = log_preallocate
        if log_retention_bytes is not None:
            self._values["log_retention_bytes"] = log_retention_bytes
        if log_retention_hours is not None:
            self._values["log_retention_hours"] = log_retention_hours
        if log_retention_ms is not None:
            self._values["log_retention_ms"] = log_retention_ms
        if log_roll_jitter_ms is not None:
            self._values["log_roll_jitter_ms"] = log_roll_jitter_ms
        if log_segment_delete_delay_ms is not None:
            self._values["log_segment_delete_delay_ms"] = log_segment_delete_delay_ms
        if message_max_bytes is not None:
            self._values["message_max_bytes"] = message_max_bytes

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#cluster_id DatabaseKafkaConfig#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def auto_create_topics_enable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#auto_create_topics_enable DatabaseKafkaConfig#auto_create_topics_enable}.'''
        result = self._values.get("auto_create_topics_enable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def group_initial_rebalance_delay_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_initial_rebalance_delay_ms DatabaseKafkaConfig#group_initial_rebalance_delay_ms}.'''
        result = self._values.get("group_initial_rebalance_delay_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def group_max_session_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_max_session_timeout_ms DatabaseKafkaConfig#group_max_session_timeout_ms}.'''
        result = self._values.get("group_max_session_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def group_min_session_timeout_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#group_min_session_timeout_ms DatabaseKafkaConfig#group_min_session_timeout_ms}.'''
        result = self._values.get("group_min_session_timeout_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#id DatabaseKafkaConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_cleaner_delete_retention_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_cleaner_delete_retention_ms DatabaseKafkaConfig#log_cleaner_delete_retention_ms}.'''
        result = self._values.get("log_cleaner_delete_retention_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_cleaner_min_compaction_lag_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_cleaner_min_compaction_lag_ms DatabaseKafkaConfig#log_cleaner_min_compaction_lag_ms}.'''
        result = self._values.get("log_cleaner_min_compaction_lag_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_flush_interval_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_flush_interval_ms DatabaseKafkaConfig#log_flush_interval_ms}.'''
        result = self._values.get("log_flush_interval_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_index_interval_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_index_interval_bytes DatabaseKafkaConfig#log_index_interval_bytes}.'''
        result = self._values.get("log_index_interval_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_message_downconversion_enable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_message_downconversion_enable DatabaseKafkaConfig#log_message_downconversion_enable}.'''
        result = self._values.get("log_message_downconversion_enable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_message_timestamp_difference_max_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_message_timestamp_difference_max_ms DatabaseKafkaConfig#log_message_timestamp_difference_max_ms}.'''
        result = self._values.get("log_message_timestamp_difference_max_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_preallocate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_preallocate DatabaseKafkaConfig#log_preallocate}.'''
        result = self._values.get("log_preallocate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_retention_bytes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_bytes DatabaseKafkaConfig#log_retention_bytes}.'''
        result = self._values.get("log_retention_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_retention_hours(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_hours DatabaseKafkaConfig#log_retention_hours}.'''
        result = self._values.get("log_retention_hours")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_retention_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_retention_ms DatabaseKafkaConfig#log_retention_ms}.'''
        result = self._values.get("log_retention_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_roll_jitter_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_roll_jitter_ms DatabaseKafkaConfig#log_roll_jitter_ms}.'''
        result = self._values.get("log_roll_jitter_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_segment_delete_delay_ms(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#log_segment_delete_delay_ms DatabaseKafkaConfig#log_segment_delete_delay_ms}.'''
        result = self._values.get("log_segment_delete_delay_ms")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def message_max_bytes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_config#message_max_bytes DatabaseKafkaConfig#message_max_bytes}.'''
        result = self._values.get("message_max_bytes")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseKafkaConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabaseKafkaConfig",
    "DatabaseKafkaConfigConfig",
]

publication.publish()

def _typecheckingstub__62f5999c31181c3a938a19174be4045d6df32886db728e5fba07c93404d44029(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    auto_create_topics_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    group_initial_rebalance_delay_ms: typing.Optional[jsii.Number] = None,
    group_max_session_timeout_ms: typing.Optional[jsii.Number] = None,
    group_min_session_timeout_ms: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    log_cleaner_delete_retention_ms: typing.Optional[jsii.Number] = None,
    log_cleaner_min_compaction_lag_ms: typing.Optional[builtins.str] = None,
    log_flush_interval_ms: typing.Optional[builtins.str] = None,
    log_index_interval_bytes: typing.Optional[jsii.Number] = None,
    log_message_downconversion_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_message_timestamp_difference_max_ms: typing.Optional[builtins.str] = None,
    log_preallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_retention_bytes: typing.Optional[builtins.str] = None,
    log_retention_hours: typing.Optional[jsii.Number] = None,
    log_retention_ms: typing.Optional[builtins.str] = None,
    log_roll_jitter_ms: typing.Optional[builtins.str] = None,
    log_segment_delete_delay_ms: typing.Optional[jsii.Number] = None,
    message_max_bytes: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__f8dd30ecf92dca1b2ce61f310c5aa1877b6633a25f4ee0380cc922a2e4eb8207(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74186211b4c0177e80d95eed19301dc35b59cd10fc8785f58067701fb0178b5a(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__352f14606db132757a65ba1f5ad9964546ce19b53c842176fe6dc4cfc524b36b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1c7c0c688e88eb6af79fab7b2d6df2ba47d5c899d93db5ee092b5160c8a5e44(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16e1a6fb53ed81217c5967628dd0dc5ddfe7164d748adebd529e36529b157f94(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6b70584e491188367091d156689bd432cdb2897b6c51ae25dc63e9a72e382288(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db230118f4c3bbc90f9b6a408dd487cf8571849ad2310919913f27e4868d6986(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7609bfc47e1cc6585e59056b79ead46b7be72c1a34df5910fb62d1245018ad98(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fda1e9113cb9b7a4a4e051df78cb4506cc87d9e9b6b540f55c4e62ba1b5d66a7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__710118cec5562928e7f0366ff67b07db53d76bf3c6fe82820e5351cb68d6c2d8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9d4a322fc5ead5d40c70310c0b14864c81b1f9e372f959c6c62a7f2ac7bf503(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2f7b0ba2f95ddb34a1e918c7afba56b2dc8e8a6d3565f3b1545f1811c88f4ab(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b54880bd447ab18acfcb3ea24a6d04b4a6a0fc5f19c49a994ce3cebe24c8c74(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee28dbbd753c952bc5d668bdac3f639930882e675c865feaf73824b84f497a28(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff0368ee8bd211cf67a17e2bd1e75053600ae8db6b12112f276b8c49302f39c8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76f246b4a1c5101b0786c0e55f786809c36f9656c921a26b04811838fae95746(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3625b480a251c3e6d6000497cde6f6fd5985e1bca2abff5d1a2b80fe147f38a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b543b57329a13867e632c54b659339d51802ef9fbe84533ea4364c029b63eb3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87f30c0e4f298e70d4b32d4a5e1f586dae7c579dab6b2b0772b371d05bb07a9b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a88bbdfda388501b2a7e4dfdc7e774bbf11ddb3066c8da29f9e8df38f21d0c58(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61586145a2d4f13f6fed6109f4563978564044cefeaff0db391289810f90e25a(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    auto_create_topics_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    group_initial_rebalance_delay_ms: typing.Optional[jsii.Number] = None,
    group_max_session_timeout_ms: typing.Optional[jsii.Number] = None,
    group_min_session_timeout_ms: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    log_cleaner_delete_retention_ms: typing.Optional[jsii.Number] = None,
    log_cleaner_min_compaction_lag_ms: typing.Optional[builtins.str] = None,
    log_flush_interval_ms: typing.Optional[builtins.str] = None,
    log_index_interval_bytes: typing.Optional[jsii.Number] = None,
    log_message_downconversion_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_message_timestamp_difference_max_ms: typing.Optional[builtins.str] = None,
    log_preallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_retention_bytes: typing.Optional[builtins.str] = None,
    log_retention_hours: typing.Optional[jsii.Number] = None,
    log_retention_ms: typing.Optional[builtins.str] = None,
    log_roll_jitter_ms: typing.Optional[builtins.str] = None,
    log_segment_delete_delay_ms: typing.Optional[jsii.Number] = None,
    message_max_bytes: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
