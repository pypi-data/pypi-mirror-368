r'''
# `digitalocean_database_redis_config`

Refer to the Terraform Registry for docs: [`digitalocean_database_redis_config`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config).
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


class DatabaseRedisConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseRedisConfig.DatabaseRedisConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config digitalocean_database_redis_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        acl_channels_default: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        io_threads: typing.Optional[jsii.Number] = None,
        lfu_decay_time: typing.Optional[jsii.Number] = None,
        lfu_log_factor: typing.Optional[jsii.Number] = None,
        maxmemory_policy: typing.Optional[builtins.str] = None,
        notify_keyspace_events: typing.Optional[builtins.str] = None,
        number_of_databases: typing.Optional[jsii.Number] = None,
        persistence: typing.Optional[builtins.str] = None,
        pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeout: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config digitalocean_database_redis_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#cluster_id DatabaseRedisConfig#cluster_id}.
        :param acl_channels_default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#acl_channels_default DatabaseRedisConfig#acl_channels_default}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#id DatabaseRedisConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param io_threads: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#io_threads DatabaseRedisConfig#io_threads}.
        :param lfu_decay_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#lfu_decay_time DatabaseRedisConfig#lfu_decay_time}.
        :param lfu_log_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#lfu_log_factor DatabaseRedisConfig#lfu_log_factor}.
        :param maxmemory_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#maxmemory_policy DatabaseRedisConfig#maxmemory_policy}.
        :param notify_keyspace_events: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#notify_keyspace_events DatabaseRedisConfig#notify_keyspace_events}.
        :param number_of_databases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#number_of_databases DatabaseRedisConfig#number_of_databases}.
        :param persistence: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#persistence DatabaseRedisConfig#persistence}.
        :param pubsub_client_output_buffer_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#pubsub_client_output_buffer_limit DatabaseRedisConfig#pubsub_client_output_buffer_limit}.
        :param ssl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#ssl DatabaseRedisConfig#ssl}.
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#timeout DatabaseRedisConfig#timeout}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77839e0303178a8f31e107e8dd7a70fd309c4e5877fce3fcce068e3f5262d053)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabaseRedisConfigConfig(
            cluster_id=cluster_id,
            acl_channels_default=acl_channels_default,
            id=id,
            io_threads=io_threads,
            lfu_decay_time=lfu_decay_time,
            lfu_log_factor=lfu_log_factor,
            maxmemory_policy=maxmemory_policy,
            notify_keyspace_events=notify_keyspace_events,
            number_of_databases=number_of_databases,
            persistence=persistence,
            pubsub_client_output_buffer_limit=pubsub_client_output_buffer_limit,
            ssl=ssl,
            timeout=timeout,
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
        '''Generates CDKTF code for importing a DatabaseRedisConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseRedisConfig to import.
        :param import_from_id: The id of the existing DatabaseRedisConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseRedisConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__055f5335f0702daa4a7a71ac1a620333bebc3d7216f1c947b487d5295ed8a8ac)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAclChannelsDefault")
    def reset_acl_channels_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAclChannelsDefault", []))

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

    @jsii.member(jsii_name="resetMaxmemoryPolicy")
    def reset_maxmemory_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxmemoryPolicy", []))

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
    @jsii.member(jsii_name="maxmemoryPolicyInput")
    def maxmemory_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxmemoryPolicyInput"))

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
    @jsii.member(jsii_name="aclChannelsDefault")
    def acl_channels_default(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "aclChannelsDefault"))

    @acl_channels_default.setter
    def acl_channels_default(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3927ea96e77d917be7bb5c663854a141e5c75cb9b085201f995117c139881f78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "aclChannelsDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18e92868ce88cee6780869b94602379b268f022cf4ec0e8998668e794b74dee0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c3222f621682ce97e72d2357138b9531a9e0a20a35ccb2d84ed1c6607c78102)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ioThreads")
    def io_threads(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "ioThreads"))

    @io_threads.setter
    def io_threads(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aa0a8d20cee220e0a9850601cd94a610f94b7ebba52b285c3cd57ed84ad7593)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ioThreads", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lfuDecayTime")
    def lfu_decay_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lfuDecayTime"))

    @lfu_decay_time.setter
    def lfu_decay_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__120dacd87cfa13c6a10f96969f09ff5b0fead323fdb2b53c131f050dd992b85e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lfuDecayTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="lfuLogFactor")
    def lfu_log_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "lfuLogFactor"))

    @lfu_log_factor.setter
    def lfu_log_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__853dfd7b13738766e5d589a0d351ec5a86238359552f646c0a21e84ee123ffdb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "lfuLogFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxmemoryPolicy")
    def maxmemory_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxmemoryPolicy"))

    @maxmemory_policy.setter
    def maxmemory_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bac47598d4d404c3a0fa0a9d8b7ffc17f2cea8c6ab4a19b6f61c54f9d1296fa4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxmemoryPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="notifyKeyspaceEvents")
    def notify_keyspace_events(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "notifyKeyspaceEvents"))

    @notify_keyspace_events.setter
    def notify_keyspace_events(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2cb65394ebb836dcce3e66de45f4ab06a4137e8754ca624063f1b669158abfab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "notifyKeyspaceEvents", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="numberOfDatabases")
    def number_of_databases(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "numberOfDatabases"))

    @number_of_databases.setter
    def number_of_databases(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73cc9412778ed296c989fd07442687e85569f6a64ee25181a25f149ff9257272)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "numberOfDatabases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="persistence")
    def persistence(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "persistence"))

    @persistence.setter
    def persistence(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9db4e777b7725cfabab17a2c67445973b44b0823be558bdb190352e370cc9350)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "persistence", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pubsubClientOutputBufferLimit")
    def pubsub_client_output_buffer_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pubsubClientOutputBufferLimit"))

    @pubsub_client_output_buffer_limit.setter
    def pubsub_client_output_buffer_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f5f00a1f31de95f86c59b2c5f3b7514bba25ee6a3ccc4251eb05ce8728acae38)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c84e7143f24e742208cb4cc7060e3b6fcb08e5b4ba568612507075e2ae980904)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ssl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timeout")
    def timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "timeout"))

    @timeout.setter
    def timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f657f93bf3189833e58b3e6888a126bd02c364386fa3f887a538158499e28c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timeout", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseRedisConfig.DatabaseRedisConfigConfig",
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
        "id": "id",
        "io_threads": "ioThreads",
        "lfu_decay_time": "lfuDecayTime",
        "lfu_log_factor": "lfuLogFactor",
        "maxmemory_policy": "maxmemoryPolicy",
        "notify_keyspace_events": "notifyKeyspaceEvents",
        "number_of_databases": "numberOfDatabases",
        "persistence": "persistence",
        "pubsub_client_output_buffer_limit": "pubsubClientOutputBufferLimit",
        "ssl": "ssl",
        "timeout": "timeout",
    },
)
class DatabaseRedisConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        id: typing.Optional[builtins.str] = None,
        io_threads: typing.Optional[jsii.Number] = None,
        lfu_decay_time: typing.Optional[jsii.Number] = None,
        lfu_log_factor: typing.Optional[jsii.Number] = None,
        maxmemory_policy: typing.Optional[builtins.str] = None,
        notify_keyspace_events: typing.Optional[builtins.str] = None,
        number_of_databases: typing.Optional[jsii.Number] = None,
        persistence: typing.Optional[builtins.str] = None,
        pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
        ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#cluster_id DatabaseRedisConfig#cluster_id}.
        :param acl_channels_default: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#acl_channels_default DatabaseRedisConfig#acl_channels_default}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#id DatabaseRedisConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param io_threads: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#io_threads DatabaseRedisConfig#io_threads}.
        :param lfu_decay_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#lfu_decay_time DatabaseRedisConfig#lfu_decay_time}.
        :param lfu_log_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#lfu_log_factor DatabaseRedisConfig#lfu_log_factor}.
        :param maxmemory_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#maxmemory_policy DatabaseRedisConfig#maxmemory_policy}.
        :param notify_keyspace_events: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#notify_keyspace_events DatabaseRedisConfig#notify_keyspace_events}.
        :param number_of_databases: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#number_of_databases DatabaseRedisConfig#number_of_databases}.
        :param persistence: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#persistence DatabaseRedisConfig#persistence}.
        :param pubsub_client_output_buffer_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#pubsub_client_output_buffer_limit DatabaseRedisConfig#pubsub_client_output_buffer_limit}.
        :param ssl: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#ssl DatabaseRedisConfig#ssl}.
        :param timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#timeout DatabaseRedisConfig#timeout}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b563e1fd2c22afe5f4f715dba7736688a4f688abceef728e78aafab59b81530)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument acl_channels_default", value=acl_channels_default, expected_type=type_hints["acl_channels_default"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument io_threads", value=io_threads, expected_type=type_hints["io_threads"])
            check_type(argname="argument lfu_decay_time", value=lfu_decay_time, expected_type=type_hints["lfu_decay_time"])
            check_type(argname="argument lfu_log_factor", value=lfu_log_factor, expected_type=type_hints["lfu_log_factor"])
            check_type(argname="argument maxmemory_policy", value=maxmemory_policy, expected_type=type_hints["maxmemory_policy"])
            check_type(argname="argument notify_keyspace_events", value=notify_keyspace_events, expected_type=type_hints["notify_keyspace_events"])
            check_type(argname="argument number_of_databases", value=number_of_databases, expected_type=type_hints["number_of_databases"])
            check_type(argname="argument persistence", value=persistence, expected_type=type_hints["persistence"])
            check_type(argname="argument pubsub_client_output_buffer_limit", value=pubsub_client_output_buffer_limit, expected_type=type_hints["pubsub_client_output_buffer_limit"])
            check_type(argname="argument ssl", value=ssl, expected_type=type_hints["ssl"])
            check_type(argname="argument timeout", value=timeout, expected_type=type_hints["timeout"])
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
        if id is not None:
            self._values["id"] = id
        if io_threads is not None:
            self._values["io_threads"] = io_threads
        if lfu_decay_time is not None:
            self._values["lfu_decay_time"] = lfu_decay_time
        if lfu_log_factor is not None:
            self._values["lfu_log_factor"] = lfu_log_factor
        if maxmemory_policy is not None:
            self._values["maxmemory_policy"] = maxmemory_policy
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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#cluster_id DatabaseRedisConfig#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def acl_channels_default(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#acl_channels_default DatabaseRedisConfig#acl_channels_default}.'''
        result = self._values.get("acl_channels_default")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#id DatabaseRedisConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def io_threads(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#io_threads DatabaseRedisConfig#io_threads}.'''
        result = self._values.get("io_threads")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lfu_decay_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#lfu_decay_time DatabaseRedisConfig#lfu_decay_time}.'''
        result = self._values.get("lfu_decay_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def lfu_log_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#lfu_log_factor DatabaseRedisConfig#lfu_log_factor}.'''
        result = self._values.get("lfu_log_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def maxmemory_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#maxmemory_policy DatabaseRedisConfig#maxmemory_policy}.'''
        result = self._values.get("maxmemory_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def notify_keyspace_events(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#notify_keyspace_events DatabaseRedisConfig#notify_keyspace_events}.'''
        result = self._values.get("notify_keyspace_events")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def number_of_databases(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#number_of_databases DatabaseRedisConfig#number_of_databases}.'''
        result = self._values.get("number_of_databases")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def persistence(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#persistence DatabaseRedisConfig#persistence}.'''
        result = self._values.get("persistence")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pubsub_client_output_buffer_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#pubsub_client_output_buffer_limit DatabaseRedisConfig#pubsub_client_output_buffer_limit}.'''
        result = self._values.get("pubsub_client_output_buffer_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ssl(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#ssl DatabaseRedisConfig#ssl}.'''
        result = self._values.get("ssl")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_redis_config#timeout DatabaseRedisConfig#timeout}.'''
        result = self._values.get("timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseRedisConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabaseRedisConfig",
    "DatabaseRedisConfigConfig",
]

publication.publish()

def _typecheckingstub__77839e0303178a8f31e107e8dd7a70fd309c4e5877fce3fcce068e3f5262d053(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    acl_channels_default: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    io_threads: typing.Optional[jsii.Number] = None,
    lfu_decay_time: typing.Optional[jsii.Number] = None,
    lfu_log_factor: typing.Optional[jsii.Number] = None,
    maxmemory_policy: typing.Optional[builtins.str] = None,
    notify_keyspace_events: typing.Optional[builtins.str] = None,
    number_of_databases: typing.Optional[jsii.Number] = None,
    persistence: typing.Optional[builtins.str] = None,
    pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeout: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__055f5335f0702daa4a7a71ac1a620333bebc3d7216f1c947b487d5295ed8a8ac(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3927ea96e77d917be7bb5c663854a141e5c75cb9b085201f995117c139881f78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18e92868ce88cee6780869b94602379b268f022cf4ec0e8998668e794b74dee0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c3222f621682ce97e72d2357138b9531a9e0a20a35ccb2d84ed1c6607c78102(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aa0a8d20cee220e0a9850601cd94a610f94b7ebba52b285c3cd57ed84ad7593(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__120dacd87cfa13c6a10f96969f09ff5b0fead323fdb2b53c131f050dd992b85e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__853dfd7b13738766e5d589a0d351ec5a86238359552f646c0a21e84ee123ffdb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bac47598d4d404c3a0fa0a9d8b7ffc17f2cea8c6ab4a19b6f61c54f9d1296fa4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2cb65394ebb836dcce3e66de45f4ab06a4137e8754ca624063f1b669158abfab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73cc9412778ed296c989fd07442687e85569f6a64ee25181a25f149ff9257272(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9db4e777b7725cfabab17a2c67445973b44b0823be558bdb190352e370cc9350(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f5f00a1f31de95f86c59b2c5f3b7514bba25ee6a3ccc4251eb05ce8728acae38(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c84e7143f24e742208cb4cc7060e3b6fcb08e5b4ba568612507075e2ae980904(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f657f93bf3189833e58b3e6888a126bd02c364386fa3f887a538158499e28c6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b563e1fd2c22afe5f4f715dba7736688a4f688abceef728e78aafab59b81530(
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
    id: typing.Optional[builtins.str] = None,
    io_threads: typing.Optional[jsii.Number] = None,
    lfu_decay_time: typing.Optional[jsii.Number] = None,
    lfu_log_factor: typing.Optional[jsii.Number] = None,
    maxmemory_policy: typing.Optional[builtins.str] = None,
    notify_keyspace_events: typing.Optional[builtins.str] = None,
    number_of_databases: typing.Optional[jsii.Number] = None,
    persistence: typing.Optional[builtins.str] = None,
    pubsub_client_output_buffer_limit: typing.Optional[jsii.Number] = None,
    ssl: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
