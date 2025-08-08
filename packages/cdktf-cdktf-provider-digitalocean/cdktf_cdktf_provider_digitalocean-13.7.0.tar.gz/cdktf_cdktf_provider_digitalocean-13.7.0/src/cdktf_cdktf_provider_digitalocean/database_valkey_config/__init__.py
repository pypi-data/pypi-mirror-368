r'''
# `digitalocean_database_valkey_config`

Refer to the Terraform Registry for docs: [`digitalocean_database_valkey_config`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config).
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


class DatabaseValkeyConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseValkeyConfig.DatabaseValkeyConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config digitalocean_database_valkey_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        acl_channels_default: typing.Optional[builtins.str] = None,
        frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        io_threads: typing.Optional[jsii.Number] = None,
        lfu_decay_time: typing.Optional[jsii.Number] = None,
        lfu_log_factor: typing.Optional[jsii.Number] = None,
        notify_keyspace_events: typing.Optional[builtins.str] = None,
        number_of_databases: typing.Optional[jsii.Number] = None,
        persistence: typing.Optional[builtins.str] = None,
        pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config digitalocean_database_valkey_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: A unique identifier for the database cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#cluster_id DatabaseValkeyConfig#cluster_id}
        :param acl_channels_default: Determines default pub/sub channels' ACL for new users if ACL is not supplied. When this option is not defined, all_channels is assumed to keep backward compatibility. This option doesn't affect Valkey configuration acl-pubsub-default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#acl_channels_default DatabaseValkeyConfig#acl_channels_default}
        :param frequent_snapshots: Frequent RDB snapshots. When enabled, Valkey will create frequent local RDB snapshots. When disabled, Valkey will only take RDB snapshots when a backup is created, based on the backup schedule. This setting is ignored when valkey_persistence is set to off. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#frequent_snapshots DatabaseValkeyConfig#frequent_snapshots}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#id DatabaseValkeyConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param io_threads: The number of IO threads used by Valkey. Must be between 1 and 32. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#io_threads DatabaseValkeyConfig#io_threads}
        :param lfu_decay_time: The decay time for Valkey's LFU cache eviction. Must be between 1 and 120. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#lfu_decay_time DatabaseValkeyConfig#lfu_decay_time}
        :param lfu_log_factor: The log factor for Valkey's LFU (Least Frequently Used) cache eviction. Must be between 1 and 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#lfu_log_factor DatabaseValkeyConfig#lfu_log_factor}
        :param notify_keyspace_events: Set notify-keyspace-events option. Requires at least K or E and accepts any combination of the following options. Setting the parameter to "" disables notifications. K — Keyspace events E — Keyevent events g — Generic commands (e.g. DEL, EXPIRE, RENAME, ...) $ — String commands l — List commands s — Set commands h — Hash commands z — Sorted set commands t — Stream commands d — Module key type events x — Expired events e — Evicted events m — Key miss events n — New key events A — Alias for "g$lshztxed" Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#notify_keyspace_events DatabaseValkeyConfig#notify_keyspace_events}
        :param number_of_databases: The number of logical databases in the Valkey cluster. Must be between 1 and 128. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#number_of_databases DatabaseValkeyConfig#number_of_databases}
        :param persistence: When persistence is 'rdb', Valkey does RDB dumps each 10 minutes if any key is changed. Also RDB dumps are done according to backup schedule for backup purposes. When persistence is 'off', no RDB dumps and backups are done, so data can be lost at any moment if service is restarted for any reason, or if service is powered off. Also service can't be forked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#persistence DatabaseValkeyConfig#persistence}
        :param pubsub_client_output_buffer_limit: Set output buffer limit for pub / sub clients in MB. The value is the hard limit, the soft limit is 1/4 of the hard limit. When setting the limit, be mindful of the available memory in the selected service plan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#pubsub_client_output_buffer_limit DatabaseValkeyConfig#pubsub_client_output_buffer_limit}
        :param ssl: Whether to enable SSL/TLS for connections to the Valkey cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#ssl DatabaseValkeyConfig#ssl}
        :param timeout: The timeout (in seconds) for Valkey client connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#timeout DatabaseValkeyConfig#timeout}
        :param valkey_active_expire_effort: Active expire effort. Valkey reclaims expired keys both when accessed and in the background. The background process scans for expired keys to free memory. Increasing the active-expire-effort setting (default 1, max 10) uses more CPU to reclaim expired keys faster, reducing memory usage but potentially increasing latency. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#valkey_active_expire_effort DatabaseValkeyConfig#valkey_active_expire_effort}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2a206797af482e75633ad06df29f8d31c7e99cd89deac26c6e165a8813e7007)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabaseValkeyConfigConfig(
            cluster_id=cluster_id,
            acl_channels_default=acl_channels_default,
            frequent_snapshots=frequent_snapshots,
            id=id,
            io_threads=io_threads,
            lfu_decay_time=lfu_decay_time,
            lfu_log_factor=lfu_log_factor,
            notify_keyspace_events=notify_keyspace_events,
            number_of_databases=number_of_databases,
            persistence=persistence,
            pubsub_client_output_buffer_limit=pubsub_client_output_buffer_limit,
            ssl=ssl,
            timeout=timeout,
            valkey_active_expire_effort=valkey_active_expire_effort,
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
        '''Generates CDKTF code for importing a DatabaseValkeyConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseValkeyConfig to import.
        :param import_from_id: The id of the existing DatabaseValkeyConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseValkeyConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e95f0b8944a93d3156ba01a8bdf4a86b9db7cc2fb5d55071750e71ce38dcdb57)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAclChannelsDefault")
    def reset_acl_channels_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAclChannelsDefault", []))

    @jsii.member(jsii_name="resetFrequentSnapshots")
    def reset_frequent_snapshots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFrequentSnapshots", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIoThreads")
    def reset_io_threads(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIoThreads", []))

    @jsii.member(jsii_name="resetLfuDecayTime")
    def reset_lfu_decay_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLfuDecayTime", []))

    @jsii.member(jsii_name="resetLfuLogFactor")
    def reset_lfu_log_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLfuLogFactor", []))

    @jsii.member(jsii_name="resetNotifyKeyspaceEvents")
    def reset_notify_keyspace_events(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNotifyKeyspaceEvents", []))

    @jsii.member(jsii_name="resetNumberOfDatabases")
    def reset_number_of_databases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNumberOfDatabases", []))

    @jsii.member(jsii_name="resetPersistence")
    def reset_persistence(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPersistence", []))

    @jsii.member(jsii_name="resetPubsubClientOutputBufferLimit")
    def reset_pubsub_client_output_buffer_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPubsubClientOutputBufferLimit", []))

    @jsii.member(jsii_name="resetSsl")
    def reset_ssl(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSsl", []))

    @jsii.member(jsii_name="resetTimeout")
    def reset_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeout", []))

    @jsii.member(jsii_name="resetValkeyActiveExpireEffort")
    def reset_valkey_active_expire_effort(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetValkeyActiveExpireEffort", []))

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
    @jsii.member(jsii_name="aclChannelsDefaultInput")
    def acl_channels_default_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aclChannelsDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="frequentSnapshotsInput")
    def frequent_snapshots_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "frequentSnapshotsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ioThreadsInput")
    def io_threads_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "ioThreadsInput"))

    @builtins.property
    @jsii.member(jsii_name="lfuDecayTimeInput")
    def lfu_decay_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lfuDecayTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="lfuLogFactorInput")
    def lfu_log_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "lfuLogFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="notifyKeyspaceEventsInput")
    def notify_keyspace_events_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "notifyKeyspaceEventsInput"))

    @builtins.property
    @jsii.member(jsii_name="numberOfDatabasesInput")
    def number_of_databases_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "numberOfDatabasesInput"))

    @builtins.property
    @jsii.member(jsii_name="persistenceInput")
    def persistence_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "persistenceInput"))

    @builtins.property
    @jsii.member(jsii_name="pubsubClientOutputBufferLimitInput")
    def pubsub_client_output_buffer_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pubsubClientOutputBufferLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="sslInput")
    def ssl_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sslInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutInput")
    def timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "timeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="valkeyActiveExpireEffortInput")
    def valkey_active_expire_effort_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "valkeyActiveExpireEffortInput"))

    @builtins.property
    @jsii.member(jsii_name="aclChannelsDefault")
    def acl_channels_default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclChannelsDefault"))

    @acl_channels_default.setter
    def acl_channels_default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b36da619d81b974181747eb7bc5cdf8b9e37e315a023f75a6cb508a149fc6ef3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aclChannelsDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ae1e65b95d4ffbc9269041b3e30048b38e9f32b6f377a45a9efbb5982316cde)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="frequentSnapshots")
    def frequent_snapshots(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "frequentSnapshots"))

    @frequent_snapshots.setter
    def frequent_snapshots(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1189a8e424eff0da50e64ca62d98ef9486d909067dba5960533e5466d1d004e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "frequentSnapshots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33af5b2b47310a191f42ae5e4571f480efcca2fddffcc2208909b1e914556fca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ioThreads")
    def io_threads(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ioThreads"))

    @io_threads.setter
    def io_threads(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58f2930a27193cd28872db54e24ef83ef92614bfdc193829f9c45bf2bf503a61)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ioThreads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lfuDecayTime")
    def lfu_decay_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lfuDecayTime"))

    @lfu_decay_time.setter
    def lfu_decay_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f7df267d6f3a93e5287f8dcd7e629d67092a2b123701ced737ac9401dacffc60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lfuDecayTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lfuLogFactor")
    def lfu_log_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lfuLogFactor"))

    @lfu_log_factor.setter
    def lfu_log_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfd3298c55669771f4bba2a679ab8dd55e52f45e8052d422fae7276327ee8158)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lfuLogFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notifyKeyspaceEvents")
    def notify_keyspace_events(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notifyKeyspaceEvents"))

    @notify_keyspace_events.setter
    def notify_keyspace_events(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31297c1cea68f256512c2baaf642dcf0f29dc6107dda955639c4304abba16f0f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyKeyspaceEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfDatabases")
    def number_of_databases(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfDatabases"))

    @number_of_databases.setter
    def number_of_databases(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4121a5c4d7ba7cb00f9ae12e939338c75de7e4d4ba7cf1c0a5d8b6264a6ec16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfDatabases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistence")
    def persistence(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "persistence"))

    @persistence.setter
    def persistence(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__62747ab71db01953752b32b0b53abd30180c06d8abc84ae7fe22cea1cfeedf7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pubsubClientOutputBufferLimit")
    def pubsub_client_output_buffer_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pubsubClientOutputBufferLimit"))

    @pubsub_client_output_buffer_limit.setter
    def pubsub_client_output_buffer_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef514f913e75116f101ef286e56a8fc3e7f87c0042ccd6e047cdaad25eb4989a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pubsubClientOutputBufferLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ssl")
    def ssl(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ssl"))

    @ssl.setter
    def ssl(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__560a251a4e6017ee5865b35b76f1824bd68919c9b9fea11685d40308bd41dfbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89c1d4f09da8a44ffccb700f2dc49374c8e1b839b24cc93838499cd43b211fdd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="valkeyActiveExpireEffort")
    def valkey_active_expire_effort(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "valkeyActiveExpireEffort"))

    @valkey_active_expire_effort.setter
    def valkey_active_expire_effort(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e4a95891d4706d044a25b1f1d2c5c0f80b717e139474781348360dc8ccdf416)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "valkeyActiveExpireEffort", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseValkeyConfig.DatabaseValkeyConfigConfig",
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
        "acl_channels_default": "aclChannelsDefault",
        "frequent_snapshots": "frequentSnapshots",
        "id": "id",
        "io_threads": "ioThreads",
        "lfu_decay_time": "lfuDecayTime",
        "lfu_log_factor": "lfuLogFactor",
        "notify_keyspace_events": "notifyKeyspaceEvents",
        "number_of_databases": "numberOfDatabases",
        "persistence": "persistence",
        "pubsub_client_output_buffer_limit": "pubsubClientOutputBufferLimit",
        "ssl": "ssl",
        "timeout": "timeout",
        "valkey_active_expire_effort": "valkeyActiveExpireEffort",
    },
)
class DatabaseValkeyConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        acl_channels_default: typing.Optional[builtins.str] = None,
        frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        id: typing.Optional[builtins.str] = None,
        io_threads: typing.Optional[jsii.Number] = None,
        lfu_decay_time: typing.Optional[jsii.Number] = None,
        lfu_log_factor: typing.Optional[jsii.Number] = None,
        notify_keyspace_events: typing.Optional[builtins.str] = None,
        number_of_databases: typing.Optional[jsii.Number] = None,
        persistence: typing.Optional[builtins.str] = None,
        pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: A unique identifier for the database cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#cluster_id DatabaseValkeyConfig#cluster_id}
        :param acl_channels_default: Determines default pub/sub channels' ACL for new users if ACL is not supplied. When this option is not defined, all_channels is assumed to keep backward compatibility. This option doesn't affect Valkey configuration acl-pubsub-default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#acl_channels_default DatabaseValkeyConfig#acl_channels_default}
        :param frequent_snapshots: Frequent RDB snapshots. When enabled, Valkey will create frequent local RDB snapshots. When disabled, Valkey will only take RDB snapshots when a backup is created, based on the backup schedule. This setting is ignored when valkey_persistence is set to off. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#frequent_snapshots DatabaseValkeyConfig#frequent_snapshots}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#id DatabaseValkeyConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param io_threads: The number of IO threads used by Valkey. Must be between 1 and 32. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#io_threads DatabaseValkeyConfig#io_threads}
        :param lfu_decay_time: The decay time for Valkey's LFU cache eviction. Must be between 1 and 120. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#lfu_decay_time DatabaseValkeyConfig#lfu_decay_time}
        :param lfu_log_factor: The log factor for Valkey's LFU (Least Frequently Used) cache eviction. Must be between 1 and 100. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#lfu_log_factor DatabaseValkeyConfig#lfu_log_factor}
        :param notify_keyspace_events: Set notify-keyspace-events option. Requires at least K or E and accepts any combination of the following options. Setting the parameter to "" disables notifications. K — Keyspace events E — Keyevent events g — Generic commands (e.g. DEL, EXPIRE, RENAME, ...) $ — String commands l — List commands s — Set commands h — Hash commands z — Sorted set commands t — Stream commands d — Module key type events x — Expired events e — Evicted events m — Key miss events n — New key events A — Alias for "g$lshztxed" Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#notify_keyspace_events DatabaseValkeyConfig#notify_keyspace_events}
        :param number_of_databases: The number of logical databases in the Valkey cluster. Must be between 1 and 128. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#number_of_databases DatabaseValkeyConfig#number_of_databases}
        :param persistence: When persistence is 'rdb', Valkey does RDB dumps each 10 minutes if any key is changed. Also RDB dumps are done according to backup schedule for backup purposes. When persistence is 'off', no RDB dumps and backups are done, so data can be lost at any moment if service is restarted for any reason, or if service is powered off. Also service can't be forked. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#persistence DatabaseValkeyConfig#persistence}
        :param pubsub_client_output_buffer_limit: Set output buffer limit for pub / sub clients in MB. The value is the hard limit, the soft limit is 1/4 of the hard limit. When setting the limit, be mindful of the available memory in the selected service plan. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#pubsub_client_output_buffer_limit DatabaseValkeyConfig#pubsub_client_output_buffer_limit}
        :param ssl: Whether to enable SSL/TLS for connections to the Valkey cluster. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#ssl DatabaseValkeyConfig#ssl}
        :param timeout: The timeout (in seconds) for Valkey client connections. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#timeout DatabaseValkeyConfig#timeout}
        :param valkey_active_expire_effort: Active expire effort. Valkey reclaims expired keys both when accessed and in the background. The background process scans for expired keys to free memory. Increasing the active-expire-effort setting (default 1, max 10) uses more CPU to reclaim expired keys faster, reducing memory usage but potentially increasing latency. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#valkey_active_expire_effort DatabaseValkeyConfig#valkey_active_expire_effort}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__893730b3e9ea2c7bb706002a72fd26487b5918366174f201e249f67846601380)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument acl_channels_default", value=acl_channels_default, expected_type=type_hints["acl_channels_default"])
            check_type(argname="argument frequent_snapshots", value=frequent_snapshots, expected_type=type_hints["frequent_snapshots"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument io_threads", value=io_threads, expected_type=type_hints["io_threads"])
            check_type(argname="argument lfu_decay_time", value=lfu_decay_time, expected_type=type_hints["lfu_decay_time"])
            check_type(argname="argument lfu_log_factor", value=lfu_log_factor, expected_type=type_hints["lfu_log_factor"])
            check_type(argname="argument notify_keyspace_events", value=notify_keyspace_events, expected_type=type_hints["notify_keyspace_events"])
            check_type(argname="argument number_of_databases", value=number_of_databases, expected_type=type_hints["number_of_databases"])
            check_type(argname="argument persistence", value=persistence, expected_type=type_hints["persistence"])
            check_type(argname="argument pubsub_client_output_buffer_limit", value=pubsub_client_output_buffer_limit, expected_type=type_hints["pubsub_client_output_buffer_limit"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
            check_type(argname="argument valkey_active_expire_effort", value=valkey_active_expire_effort, expected_type=type_hints["valkey_active_expire_effort"])
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
        if acl_channels_default is not None:
            self._values["acl_channels_default"] = acl_channels_default
        if frequent_snapshots is not None:
            self._values["frequent_snapshots"] = frequent_snapshots
        if id is not None:
            self._values["id"] = id
        if io_threads is not None:
            self._values["io_threads"] = io_threads
        if lfu_decay_time is not None:
            self._values["lfu_decay_time"] = lfu_decay_time
        if lfu_log_factor is not None:
            self._values["lfu_log_factor"] = lfu_log_factor
        if notify_keyspace_events is not None:
            self._values["notify_keyspace_events"] = notify_keyspace_events
        if number_of_databases is not None:
            self._values["number_of_databases"] = number_of_databases
        if persistence is not None:
            self._values["persistence"] = persistence
        if pubsub_client_output_buffer_limit is not None:
            self._values["pubsub_client_output_buffer_limit"] = pubsub_client_output_buffer_limit
        if ssl is not None:
            self._values["ssl"] = ssl
        if timeout is not None:
            self._values["timeout"] = timeout
        if valkey_active_expire_effort is not None:
            self._values["valkey_active_expire_effort"] = valkey_active_expire_effort

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
        '''A unique identifier for the database cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#cluster_id DatabaseValkeyConfig#cluster_id}
        '''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def acl_channels_default(self) -> typing.Optional[builtins.str]:
        '''Determines default pub/sub channels' ACL for new users if ACL is not supplied.

        When this option is not defined, all_channels is assumed to keep backward compatibility. This option doesn't affect Valkey configuration acl-pubsub-default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#acl_channels_default DatabaseValkeyConfig#acl_channels_default}
        '''
        result = self._values.get("acl_channels_default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def frequent_snapshots(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Frequent RDB snapshots.

        When enabled, Valkey will create frequent local RDB snapshots. When disabled, Valkey will only take RDB snapshots when a backup is created, based on the backup schedule. This setting is ignored when valkey_persistence is set to off.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#frequent_snapshots DatabaseValkeyConfig#frequent_snapshots}
        '''
        result = self._values.get("frequent_snapshots")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#id DatabaseValkeyConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def io_threads(self) -> typing.Optional[jsii.Number]:
        '''The number of IO threads used by Valkey. Must be between 1 and 32.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#io_threads DatabaseValkeyConfig#io_threads}
        '''
        result = self._values.get("io_threads")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lfu_decay_time(self) -> typing.Optional[jsii.Number]:
        '''The decay time for Valkey's LFU cache eviction. Must be between 1 and 120.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#lfu_decay_time DatabaseValkeyConfig#lfu_decay_time}
        '''
        result = self._values.get("lfu_decay_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lfu_log_factor(self) -> typing.Optional[jsii.Number]:
        '''The log factor for Valkey's LFU (Least Frequently Used) cache eviction. Must be between 1 and 100.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#lfu_log_factor DatabaseValkeyConfig#lfu_log_factor}
        '''
        result = self._values.get("lfu_log_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def notify_keyspace_events(self) -> typing.Optional[builtins.str]:
        '''Set notify-keyspace-events option.

        Requires at least K or E and accepts any combination of the following options. Setting the parameter to "" disables notifications.

        K — Keyspace events
        E — Keyevent events
        g — Generic commands (e.g. DEL, EXPIRE, RENAME, ...)
        $ — String commands
        l — List commands
        s — Set commands
        h — Hash commands
        z — Sorted set commands
        t — Stream commands
        d — Module key type events
        x — Expired events
        e — Evicted events
        m — Key miss events
        n — New key events
        A — Alias for "g$lshztxed"

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#notify_keyspace_events DatabaseValkeyConfig#notify_keyspace_events}
        '''
        result = self._values.get("notify_keyspace_events")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_databases(self) -> typing.Optional[jsii.Number]:
        '''The number of logical databases in the Valkey cluster. Must be between 1 and 128.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#number_of_databases DatabaseValkeyConfig#number_of_databases}
        '''
        result = self._values.get("number_of_databases")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def persistence(self) -> typing.Optional[builtins.str]:
        '''When persistence is 'rdb', Valkey does RDB dumps each 10 minutes if any key is changed.

        Also RDB dumps are done according to backup schedule for backup purposes. When persistence is 'off', no RDB dumps and backups are done, so data can be lost at any moment if service is restarted for any reason, or if service is powered off. Also service can't be forked.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#persistence DatabaseValkeyConfig#persistence}
        '''
        result = self._values.get("persistence")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pubsub_client_output_buffer_limit(self) -> typing.Optional[jsii.Number]:
        '''Set output buffer limit for pub / sub clients in MB.

        The value is the hard limit, the soft limit is 1/4 of the hard limit. When setting the limit, be mindful of the available memory in the selected service plan.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#pubsub_client_output_buffer_limit DatabaseValkeyConfig#pubsub_client_output_buffer_limit}
        '''
        result = self._values.get("pubsub_client_output_buffer_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to enable SSL/TLS for connections to the Valkey cluster.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#ssl DatabaseValkeyConfig#ssl}
        '''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''The timeout (in seconds) for Valkey client connections.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#timeout DatabaseValkeyConfig#timeout}
        '''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def valkey_active_expire_effort(self) -> typing.Optional[jsii.Number]:
        '''Active expire effort.

        Valkey reclaims expired keys both when accessed and in the background. The background process scans for expired keys to free memory. Increasing the active-expire-effort setting (default 1, max 10) uses more CPU to reclaim expired keys faster, reducing memory usage but potentially increasing latency.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_valkey_config#valkey_active_expire_effort DatabaseValkeyConfig#valkey_active_expire_effort}
        '''
        result = self._values.get("valkey_active_expire_effort")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseValkeyConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabaseValkeyConfig",
    "DatabaseValkeyConfigConfig",
]

publication.publish()

def _typecheckingstub__b2a206797af482e75633ad06df29f8d31c7e99cd89deac26c6e165a8813e7007(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    acl_channels_default: typing.Optional[builtins.str] = None,
    frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    io_threads: typing.Optional[jsii.Number] = None,
    lfu_decay_time: typing.Optional[jsii.Number] = None,
    lfu_log_factor: typing.Optional[jsii.Number] = None,
    notify_keyspace_events: typing.Optional[builtins.str] = None,
    number_of_databases: typing.Optional[jsii.Number] = None,
    persistence: typing.Optional[builtins.str] = None,
    pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeout: typing.Optional[jsii.Number] = None,
    valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__e95f0b8944a93d3156ba01a8bdf4a86b9db7cc2fb5d55071750e71ce38dcdb57(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b36da619d81b974181747eb7bc5cdf8b9e37e315a023f75a6cb508a149fc6ef3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ae1e65b95d4ffbc9269041b3e30048b38e9f32b6f377a45a9efbb5982316cde(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1189a8e424eff0da50e64ca62d98ef9486d909067dba5960533e5466d1d004e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33af5b2b47310a191f42ae5e4571f480efcca2fddffcc2208909b1e914556fca(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58f2930a27193cd28872db54e24ef83ef92614bfdc193829f9c45bf2bf503a61(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f7df267d6f3a93e5287f8dcd7e629d67092a2b123701ced737ac9401dacffc60(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfd3298c55669771f4bba2a679ab8dd55e52f45e8052d422fae7276327ee8158(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31297c1cea68f256512c2baaf642dcf0f29dc6107dda955639c4304abba16f0f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4121a5c4d7ba7cb00f9ae12e939338c75de7e4d4ba7cf1c0a5d8b6264a6ec16(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__62747ab71db01953752b32b0b53abd30180c06d8abc84ae7fe22cea1cfeedf7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef514f913e75116f101ef286e56a8fc3e7f87c0042ccd6e047cdaad25eb4989a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__560a251a4e6017ee5865b35b76f1824bd68919c9b9fea11685d40308bd41dfbc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89c1d4f09da8a44ffccb700f2dc49374c8e1b839b24cc93838499cd43b211fdd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e4a95891d4706d044a25b1f1d2c5c0f80b717e139474781348360dc8ccdf416(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__893730b3e9ea2c7bb706002a72fd26487b5918366174f201e249f67846601380(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    acl_channels_default: typing.Optional[builtins.str] = None,
    frequent_snapshots: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    id: typing.Optional[builtins.str] = None,
    io_threads: typing.Optional[jsii.Number] = None,
    lfu_decay_time: typing.Optional[jsii.Number] = None,
    lfu_log_factor: typing.Optional[jsii.Number] = None,
    notify_keyspace_events: typing.Optional[builtins.str] = None,
    number_of_databases: typing.Optional[jsii.Number] = None,
    persistence: typing.Optional[builtins.str] = None,
    pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeout: typing.Optional[jsii.Number] = None,
    valkey_active_expire_effort: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
