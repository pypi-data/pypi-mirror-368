r'''
# `digitalocean_database_kafka_topic`

Refer to the Terraform Registry for docs: [`digitalocean_database_kafka_topic`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic).
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


class DatabaseKafkaTopic(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaTopic.DatabaseKafkaTopic",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic digitalocean_database_kafka_topic}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        name: builtins.str,
        config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DatabaseKafkaTopicConfigA", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        partition_count: typing.Optional[jsii.Number] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic digitalocean_database_kafka_topic} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#cluster_id DatabaseKafkaTopic#cluster_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#name DatabaseKafkaTopic#name}.
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#config DatabaseKafkaTopic#config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#id DatabaseKafkaTopic#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param partition_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#partition_count DatabaseKafkaTopic#partition_count}.
        :param replication_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#replication_factor DatabaseKafkaTopic#replication_factor}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48af6e99511012ab24131ded5553a2e42dc8f17c8f4b4d3caf94d86ae3d7dc49)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config_ = DatabaseKafkaTopicConfig(
            cluster_id=cluster_id,
            name=name,
            config=config,
            id=id,
            partition_count=partition_count,
            replication_factor=replication_factor,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DatabaseKafkaTopic resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseKafkaTopic to import.
        :param import_from_id: The id of the existing DatabaseKafkaTopic that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseKafkaTopic to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e334db016a4937e582bc20e4f8367dad60dfaa203e1b79c62a9a7a251694c17d)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DatabaseKafkaTopicConfigA", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1c76061f8e14913a5f4794c3e37188f90be087c01337b93354df781b35d0e114)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetPartitionCount")
    def reset_partition_count(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPartitionCount", []))

    @jsii.member(jsii_name="resetReplicationFactor")
    def reset_replication_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetReplicationFactor", []))

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
    @jsii.member(jsii_name="config")
    def config(self) -> "DatabaseKafkaTopicConfigAList":
        return typing.cast("DatabaseKafkaTopicConfigAList", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabaseKafkaTopicConfigA"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabaseKafkaTopicConfigA"]]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="partitionCountInput")
    def partition_count_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "partitionCountInput"))

    @builtins.property
    @jsii.member(jsii_name="replicationFactorInput")
    def replication_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "replicationFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2310fe11a07e00c34db522f8a0fe5a08fdf65f59a6223d373b03a975922ecca3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0260d7898b4fdb25814bddbbc02f2097822ee51f977b095b6c027c0fd8cf33ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__878ddd5ec65713d657e818974db259e02fb30f3691ac96fc14004cd0213969e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="partitionCount")
    def partition_count(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "partitionCount"))

    @partition_count.setter
    def partition_count(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afa0dd3e3bbb4a01f86e6a8caa54a0721c64520258668b9fc9a145d915e4f4f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "partitionCount", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="replicationFactor")
    def replication_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "replicationFactor"))

    @replication_factor.setter
    def replication_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56aed1c94fa298b54c379154449754d6fef4f40b56acdb6ed66f85ecaa6f5df4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "replicationFactor", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaTopic.DatabaseKafkaTopicConfig",
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
        "name": "name",
        "config": "config",
        "id": "id",
        "partition_count": "partitionCount",
        "replication_factor": "replicationFactor",
    },
)
class DatabaseKafkaTopicConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DatabaseKafkaTopicConfigA", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        partition_count: typing.Optional[jsii.Number] = None,
        replication_factor: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#cluster_id DatabaseKafkaTopic#cluster_id}.
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#name DatabaseKafkaTopic#name}.
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#config DatabaseKafkaTopic#config}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#id DatabaseKafkaTopic#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param partition_count: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#partition_count DatabaseKafkaTopic#partition_count}.
        :param replication_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#replication_factor DatabaseKafkaTopic#replication_factor}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10c82bfade98a33bc84fade5fbda677ac9a2b51771df08ace502a0a77bc1ce81)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument partition_count", value=partition_count, expected_type=type_hints["partition_count"])
            check_type(argname="argument replication_factor", value=replication_factor, expected_type=type_hints["replication_factor"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "cluster_id": cluster_id,
            "name": name,
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
        if config is not None:
            self._values["config"] = config
        if id is not None:
            self._values["id"] = id
        if partition_count is not None:
            self._values["partition_count"] = partition_count
        if replication_factor is not None:
            self._values["replication_factor"] = replication_factor

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#cluster_id DatabaseKafkaTopic#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#name DatabaseKafkaTopic#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabaseKafkaTopicConfigA"]]]:
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#config DatabaseKafkaTopic#config}
        '''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabaseKafkaTopicConfigA"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#id DatabaseKafkaTopic#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def partition_count(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#partition_count DatabaseKafkaTopic#partition_count}.'''
        result = self._values.get("partition_count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def replication_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#replication_factor DatabaseKafkaTopic#replication_factor}.'''
        result = self._values.get("replication_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseKafkaTopicConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaTopic.DatabaseKafkaTopicConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "cleanup_policy": "cleanupPolicy",
        "compression_type": "compressionType",
        "delete_retention_ms": "deleteRetentionMs",
        "file_delete_delay_ms": "fileDeleteDelayMs",
        "flush_messages": "flushMessages",
        "flush_ms": "flushMs",
        "index_interval_bytes": "indexIntervalBytes",
        "max_compaction_lag_ms": "maxCompactionLagMs",
        "max_message_bytes": "maxMessageBytes",
        "message_down_conversion_enable": "messageDownConversionEnable",
        "message_format_version": "messageFormatVersion",
        "message_timestamp_difference_max_ms": "messageTimestampDifferenceMaxMs",
        "message_timestamp_type": "messageTimestampType",
        "min_cleanable_dirty_ratio": "minCleanableDirtyRatio",
        "min_compaction_lag_ms": "minCompactionLagMs",
        "min_insync_replicas": "minInsyncReplicas",
        "preallocate": "preallocate",
        "retention_bytes": "retentionBytes",
        "retention_ms": "retentionMs",
        "segment_bytes": "segmentBytes",
        "segment_index_bytes": "segmentIndexBytes",
        "segment_jitter_ms": "segmentJitterMs",
        "segment_ms": "segmentMs",
    },
)
class DatabaseKafkaTopicConfigA:
    def __init__(
        self,
        *,
        cleanup_policy: typing.Optional[builtins.str] = None,
        compression_type: typing.Optional[builtins.str] = None,
        delete_retention_ms: typing.Optional[builtins.str] = None,
        file_delete_delay_ms: typing.Optional[builtins.str] = None,
        flush_messages: typing.Optional[builtins.str] = None,
        flush_ms: typing.Optional[builtins.str] = None,
        index_interval_bytes: typing.Optional[builtins.str] = None,
        max_compaction_lag_ms: typing.Optional[builtins.str] = None,
        max_message_bytes: typing.Optional[builtins.str] = None,
        message_down_conversion_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        message_format_version: typing.Optional[builtins.str] = None,
        message_timestamp_difference_max_ms: typing.Optional[builtins.str] = None,
        message_timestamp_type: typing.Optional[builtins.str] = None,
        min_cleanable_dirty_ratio: typing.Optional[jsii.Number] = None,
        min_compaction_lag_ms: typing.Optional[builtins.str] = None,
        min_insync_replicas: typing.Optional[jsii.Number] = None,
        preallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retention_bytes: typing.Optional[builtins.str] = None,
        retention_ms: typing.Optional[builtins.str] = None,
        segment_bytes: typing.Optional[builtins.str] = None,
        segment_index_bytes: typing.Optional[builtins.str] = None,
        segment_jitter_ms: typing.Optional[builtins.str] = None,
        segment_ms: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cleanup_policy: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#cleanup_policy DatabaseKafkaTopic#cleanup_policy}.
        :param compression_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#compression_type DatabaseKafkaTopic#compression_type}.
        :param delete_retention_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#delete_retention_ms DatabaseKafkaTopic#delete_retention_ms}.
        :param file_delete_delay_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#file_delete_delay_ms DatabaseKafkaTopic#file_delete_delay_ms}.
        :param flush_messages: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#flush_messages DatabaseKafkaTopic#flush_messages}.
        :param flush_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#flush_ms DatabaseKafkaTopic#flush_ms}.
        :param index_interval_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#index_interval_bytes DatabaseKafkaTopic#index_interval_bytes}.
        :param max_compaction_lag_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#max_compaction_lag_ms DatabaseKafkaTopic#max_compaction_lag_ms}.
        :param max_message_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#max_message_bytes DatabaseKafkaTopic#max_message_bytes}.
        :param message_down_conversion_enable: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_down_conversion_enable DatabaseKafkaTopic#message_down_conversion_enable}.
        :param message_format_version: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_format_version DatabaseKafkaTopic#message_format_version}.
        :param message_timestamp_difference_max_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_timestamp_difference_max_ms DatabaseKafkaTopic#message_timestamp_difference_max_ms}.
        :param message_timestamp_type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_timestamp_type DatabaseKafkaTopic#message_timestamp_type}.
        :param min_cleanable_dirty_ratio: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#min_cleanable_dirty_ratio DatabaseKafkaTopic#min_cleanable_dirty_ratio}.
        :param min_compaction_lag_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#min_compaction_lag_ms DatabaseKafkaTopic#min_compaction_lag_ms}.
        :param min_insync_replicas: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#min_insync_replicas DatabaseKafkaTopic#min_insync_replicas}.
        :param preallocate: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#preallocate DatabaseKafkaTopic#preallocate}.
        :param retention_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#retention_bytes DatabaseKafkaTopic#retention_bytes}.
        :param retention_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#retention_ms DatabaseKafkaTopic#retention_ms}.
        :param segment_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_bytes DatabaseKafkaTopic#segment_bytes}.
        :param segment_index_bytes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_index_bytes DatabaseKafkaTopic#segment_index_bytes}.
        :param segment_jitter_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_jitter_ms DatabaseKafkaTopic#segment_jitter_ms}.
        :param segment_ms: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_ms DatabaseKafkaTopic#segment_ms}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc47728514050fe3b4dc0ccc9f98886e142ce89c20ba4b8e0452780f3e736037)
            check_type(argname="argument cleanup_policy", value=cleanup_policy, expected_type=type_hints["cleanup_policy"])
            check_type(argname="argument compression_type", value=compression_type, expected_type=type_hints["compression_type"])
            check_type(argname="argument delete_retention_ms", value=delete_retention_ms, expected_type=type_hints["delete_retention_ms"])
            check_type(argname="argument file_delete_delay_ms", value=file_delete_delay_ms, expected_type=type_hints["file_delete_delay_ms"])
            check_type(argname="argument flush_messages", value=flush_messages, expected_type=type_hints["flush_messages"])
            check_type(argname="argument flush_ms", value=flush_ms, expected_type=type_hints["flush_ms"])
            check_type(argname="argument index_interval_bytes", value=index_interval_bytes, expected_type=type_hints["index_interval_bytes"])
            check_type(argname="argument max_compaction_lag_ms", value=max_compaction_lag_ms, expected_type=type_hints["max_compaction_lag_ms"])
            check_type(argname="argument max_message_bytes", value=max_message_bytes, expected_type=type_hints["max_message_bytes"])
            check_type(argname="argument message_down_conversion_enable", value=message_down_conversion_enable, expected_type=type_hints["message_down_conversion_enable"])
            check_type(argname="argument message_format_version", value=message_format_version, expected_type=type_hints["message_format_version"])
            check_type(argname="argument message_timestamp_difference_max_ms", value=message_timestamp_difference_max_ms, expected_type=type_hints["message_timestamp_difference_max_ms"])
            check_type(argname="argument message_timestamp_type", value=message_timestamp_type, expected_type=type_hints["message_timestamp_type"])
            check_type(argname="argument min_cleanable_dirty_ratio", value=min_cleanable_dirty_ratio, expected_type=type_hints["min_cleanable_dirty_ratio"])
            check_type(argname="argument min_compaction_lag_ms", value=min_compaction_lag_ms, expected_type=type_hints["min_compaction_lag_ms"])
            check_type(argname="argument min_insync_replicas", value=min_insync_replicas, expected_type=type_hints["min_insync_replicas"])
            check_type(argname="argument preallocate", value=preallocate, expected_type=type_hints["preallocate"])
            check_type(argname="argument retention_bytes", value=retention_bytes, expected_type=type_hints["retention_bytes"])
            check_type(argname="argument retention_ms", value=retention_ms, expected_type=type_hints["retention_ms"])
            check_type(argname="argument segment_bytes", value=segment_bytes, expected_type=type_hints["segment_bytes"])
            check_type(argname="argument segment_index_bytes", value=segment_index_bytes, expected_type=type_hints["segment_index_bytes"])
            check_type(argname="argument segment_jitter_ms", value=segment_jitter_ms, expected_type=type_hints["segment_jitter_ms"])
            check_type(argname="argument segment_ms", value=segment_ms, expected_type=type_hints["segment_ms"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cleanup_policy is not None:
            self._values["cleanup_policy"] = cleanup_policy
        if compression_type is not None:
            self._values["compression_type"] = compression_type
        if delete_retention_ms is not None:
            self._values["delete_retention_ms"] = delete_retention_ms
        if file_delete_delay_ms is not None:
            self._values["file_delete_delay_ms"] = file_delete_delay_ms
        if flush_messages is not None:
            self._values["flush_messages"] = flush_messages
        if flush_ms is not None:
            self._values["flush_ms"] = flush_ms
        if index_interval_bytes is not None:
            self._values["index_interval_bytes"] = index_interval_bytes
        if max_compaction_lag_ms is not None:
            self._values["max_compaction_lag_ms"] = max_compaction_lag_ms
        if max_message_bytes is not None:
            self._values["max_message_bytes"] = max_message_bytes
        if message_down_conversion_enable is not None:
            self._values["message_down_conversion_enable"] = message_down_conversion_enable
        if message_format_version is not None:
            self._values["message_format_version"] = message_format_version
        if message_timestamp_difference_max_ms is not None:
            self._values["message_timestamp_difference_max_ms"] = message_timestamp_difference_max_ms
        if message_timestamp_type is not None:
            self._values["message_timestamp_type"] = message_timestamp_type
        if min_cleanable_dirty_ratio is not None:
            self._values["min_cleanable_dirty_ratio"] = min_cleanable_dirty_ratio
        if min_compaction_lag_ms is not None:
            self._values["min_compaction_lag_ms"] = min_compaction_lag_ms
        if min_insync_replicas is not None:
            self._values["min_insync_replicas"] = min_insync_replicas
        if preallocate is not None:
            self._values["preallocate"] = preallocate
        if retention_bytes is not None:
            self._values["retention_bytes"] = retention_bytes
        if retention_ms is not None:
            self._values["retention_ms"] = retention_ms
        if segment_bytes is not None:
            self._values["segment_bytes"] = segment_bytes
        if segment_index_bytes is not None:
            self._values["segment_index_bytes"] = segment_index_bytes
        if segment_jitter_ms is not None:
            self._values["segment_jitter_ms"] = segment_jitter_ms
        if segment_ms is not None:
            self._values["segment_ms"] = segment_ms

    @builtins.property
    def cleanup_policy(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#cleanup_policy DatabaseKafkaTopic#cleanup_policy}.'''
        result = self._values.get("cleanup_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def compression_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#compression_type DatabaseKafkaTopic#compression_type}.'''
        result = self._values.get("compression_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete_retention_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#delete_retention_ms DatabaseKafkaTopic#delete_retention_ms}.'''
        result = self._values.get("delete_retention_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def file_delete_delay_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#file_delete_delay_ms DatabaseKafkaTopic#file_delete_delay_ms}.'''
        result = self._values.get("file_delete_delay_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def flush_messages(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#flush_messages DatabaseKafkaTopic#flush_messages}.'''
        result = self._values.get("flush_messages")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def flush_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#flush_ms DatabaseKafkaTopic#flush_ms}.'''
        result = self._values.get("flush_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def index_interval_bytes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#index_interval_bytes DatabaseKafkaTopic#index_interval_bytes}.'''
        result = self._values.get("index_interval_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_compaction_lag_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#max_compaction_lag_ms DatabaseKafkaTopic#max_compaction_lag_ms}.'''
        result = self._values.get("max_compaction_lag_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def max_message_bytes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#max_message_bytes DatabaseKafkaTopic#max_message_bytes}.'''
        result = self._values.get("max_message_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_down_conversion_enable(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_down_conversion_enable DatabaseKafkaTopic#message_down_conversion_enable}.'''
        result = self._values.get("message_down_conversion_enable")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def message_format_version(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_format_version DatabaseKafkaTopic#message_format_version}.'''
        result = self._values.get("message_format_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_timestamp_difference_max_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_timestamp_difference_max_ms DatabaseKafkaTopic#message_timestamp_difference_max_ms}.'''
        result = self._values.get("message_timestamp_difference_max_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def message_timestamp_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#message_timestamp_type DatabaseKafkaTopic#message_timestamp_type}.'''
        result = self._values.get("message_timestamp_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_cleanable_dirty_ratio(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#min_cleanable_dirty_ratio DatabaseKafkaTopic#min_cleanable_dirty_ratio}.'''
        result = self._values.get("min_cleanable_dirty_ratio")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_compaction_lag_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#min_compaction_lag_ms DatabaseKafkaTopic#min_compaction_lag_ms}.'''
        result = self._values.get("min_compaction_lag_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_insync_replicas(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#min_insync_replicas DatabaseKafkaTopic#min_insync_replicas}.'''
        result = self._values.get("min_insync_replicas")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preallocate(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#preallocate DatabaseKafkaTopic#preallocate}.'''
        result = self._values.get("preallocate")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retention_bytes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#retention_bytes DatabaseKafkaTopic#retention_bytes}.'''
        result = self._values.get("retention_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def retention_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#retention_ms DatabaseKafkaTopic#retention_ms}.'''
        result = self._values.get("retention_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def segment_bytes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_bytes DatabaseKafkaTopic#segment_bytes}.'''
        result = self._values.get("segment_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def segment_index_bytes(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_index_bytes DatabaseKafkaTopic#segment_index_bytes}.'''
        result = self._values.get("segment_index_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def segment_jitter_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_jitter_ms DatabaseKafkaTopic#segment_jitter_ms}.'''
        result = self._values.get("segment_jitter_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def segment_ms(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_kafka_topic#segment_ms DatabaseKafkaTopic#segment_ms}.'''
        result = self._values.get("segment_ms")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseKafkaTopicConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabaseKafkaTopicConfigAList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaTopic.DatabaseKafkaTopicConfigAList",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df28fe0971bae8120dce2345a1e59e0acd30bcddf1f37f77e753ea0ef4f30c1b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "DatabaseKafkaTopicConfigAOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4cc687dc0246a0cdd16d60e91b65c9d27bf953d1eefdca87e60e26c3b5f3b80d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DatabaseKafkaTopicConfigAOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f87bf6d4a57e2d9ec787f3295614968fda73257521294c532313e2696e8434d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> _cdktf_9a9027ec.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(_cdktf_9a9027ec.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: _cdktf_9a9027ec.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ee18e15ba09cbdc2e8dc982c2fdfd123511d2147590e340a8673bf27642ff5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ffbebc3e472e2059332ea4075ceabbadbcb9de85f9322e608597a2f636003630)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabaseKafkaTopicConfigA]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabaseKafkaTopicConfigA]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabaseKafkaTopicConfigA]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00ff22f036cc508a77a896196957faac59dcd59207b1e8e54238cc852c1a9a81)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabaseKafkaTopicConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseKafkaTopic.DatabaseKafkaTopicConfigAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1f00bcf7f415e1b093ca50d67b696add8216dcf7f233b0aa08aebe7933d6cb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCleanupPolicy")
    def reset_cleanup_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCleanupPolicy", []))

    @jsii.member(jsii_name="resetCompressionType")
    def reset_compression_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompressionType", []))

    @jsii.member(jsii_name="resetDeleteRetentionMs")
    def reset_delete_retention_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeleteRetentionMs", []))

    @jsii.member(jsii_name="resetFileDeleteDelayMs")
    def reset_file_delete_delay_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileDeleteDelayMs", []))

    @jsii.member(jsii_name="resetFlushMessages")
    def reset_flush_messages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFlushMessages", []))

    @jsii.member(jsii_name="resetFlushMs")
    def reset_flush_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFlushMs", []))

    @jsii.member(jsii_name="resetIndexIntervalBytes")
    def reset_index_interval_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIndexIntervalBytes", []))

    @jsii.member(jsii_name="resetMaxCompactionLagMs")
    def reset_max_compaction_lag_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxCompactionLagMs", []))

    @jsii.member(jsii_name="resetMaxMessageBytes")
    def reset_max_message_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxMessageBytes", []))

    @jsii.member(jsii_name="resetMessageDownConversionEnable")
    def reset_message_down_conversion_enable(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageDownConversionEnable", []))

    @jsii.member(jsii_name="resetMessageFormatVersion")
    def reset_message_format_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageFormatVersion", []))

    @jsii.member(jsii_name="resetMessageTimestampDifferenceMaxMs")
    def reset_message_timestamp_difference_max_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageTimestampDifferenceMaxMs", []))

    @jsii.member(jsii_name="resetMessageTimestampType")
    def reset_message_timestamp_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMessageTimestampType", []))

    @jsii.member(jsii_name="resetMinCleanableDirtyRatio")
    def reset_min_cleanable_dirty_ratio(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCleanableDirtyRatio", []))

    @jsii.member(jsii_name="resetMinCompactionLagMs")
    def reset_min_compaction_lag_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinCompactionLagMs", []))

    @jsii.member(jsii_name="resetMinInsyncReplicas")
    def reset_min_insync_replicas(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinInsyncReplicas", []))

    @jsii.member(jsii_name="resetPreallocate")
    def reset_preallocate(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreallocate", []))

    @jsii.member(jsii_name="resetRetentionBytes")
    def reset_retention_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionBytes", []))

    @jsii.member(jsii_name="resetRetentionMs")
    def reset_retention_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetentionMs", []))

    @jsii.member(jsii_name="resetSegmentBytes")
    def reset_segment_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentBytes", []))

    @jsii.member(jsii_name="resetSegmentIndexBytes")
    def reset_segment_index_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentIndexBytes", []))

    @jsii.member(jsii_name="resetSegmentJitterMs")
    def reset_segment_jitter_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentJitterMs", []))

    @jsii.member(jsii_name="resetSegmentMs")
    def reset_segment_ms(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSegmentMs", []))

    @builtins.property
    @jsii.member(jsii_name="cleanupPolicyInput")
    def cleanup_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cleanupPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="compressionTypeInput")
    def compression_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "compressionTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteRetentionMsInput")
    def delete_retention_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteRetentionMsInput"))

    @builtins.property
    @jsii.member(jsii_name="fileDeleteDelayMsInput")
    def file_delete_delay_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "fileDeleteDelayMsInput"))

    @builtins.property
    @jsii.member(jsii_name="flushMessagesInput")
    def flush_messages_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "flushMessagesInput"))

    @builtins.property
    @jsii.member(jsii_name="flushMsInput")
    def flush_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "flushMsInput"))

    @builtins.property
    @jsii.member(jsii_name="indexIntervalBytesInput")
    def index_interval_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "indexIntervalBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxCompactionLagMsInput")
    def max_compaction_lag_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxCompactionLagMsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxMessageBytesInput")
    def max_message_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "maxMessageBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="messageDownConversionEnableInput")
    def message_down_conversion_enable_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "messageDownConversionEnableInput"))

    @builtins.property
    @jsii.member(jsii_name="messageFormatVersionInput")
    def message_format_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageFormatVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="messageTimestampDifferenceMaxMsInput")
    def message_timestamp_difference_max_ms_input(
        self,
    ) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageTimestampDifferenceMaxMsInput"))

    @builtins.property
    @jsii.member(jsii_name="messageTimestampTypeInput")
    def message_timestamp_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "messageTimestampTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="minCleanableDirtyRatioInput")
    def min_cleanable_dirty_ratio_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minCleanableDirtyRatioInput"))

    @builtins.property
    @jsii.member(jsii_name="minCompactionLagMsInput")
    def min_compaction_lag_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "minCompactionLagMsInput"))

    @builtins.property
    @jsii.member(jsii_name="minInsyncReplicasInput")
    def min_insync_replicas_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minInsyncReplicasInput"))

    @builtins.property
    @jsii.member(jsii_name="preallocateInput")
    def preallocate_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "preallocateInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionBytesInput")
    def retention_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="retentionMsInput")
    def retention_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retentionMsInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentBytesInput")
    def segment_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "segmentBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentIndexBytesInput")
    def segment_index_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "segmentIndexBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentJitterMsInput")
    def segment_jitter_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "segmentJitterMsInput"))

    @builtins.property
    @jsii.member(jsii_name="segmentMsInput")
    def segment_ms_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "segmentMsInput"))

    @builtins.property
    @jsii.member(jsii_name="cleanupPolicy")
    def cleanup_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cleanupPolicy"))

    @cleanup_policy.setter
    def cleanup_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61600a547c80fa37b5fcd0778693b098d77d182f0cee14875f1a80595a2ba38d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cleanupPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="compressionType")
    def compression_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "compressionType"))

    @compression_type.setter
    def compression_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__790a92289e4c6a7f33a98f7ed8b6b9483125edf516f0a52cb0ce1e5d7d69acf5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "compressionType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deleteRetentionMs")
    def delete_retention_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deleteRetentionMs"))

    @delete_retention_ms.setter
    def delete_retention_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8edf90ff658fd837e08f2df998503ef8642f2d7be97c7a74209f53ad1012683c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deleteRetentionMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="fileDeleteDelayMs")
    def file_delete_delay_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "fileDeleteDelayMs"))

    @file_delete_delay_ms.setter
    def file_delete_delay_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b22f58ba4392798b1e2f09b7fd8a1acab48ab1cc691d46ec81a4d1bfa8950a85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "fileDeleteDelayMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="flushMessages")
    def flush_messages(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "flushMessages"))

    @flush_messages.setter
    def flush_messages(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__937e96ed3c6cacd481a5c2f80492f1f9bd66c72572d5c8b8d6145a31617ebcc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "flushMessages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="flushMs")
    def flush_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "flushMs"))

    @flush_ms.setter
    def flush_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24556124999c5b24ddbe6bb0a83e2c7e8aab55410e4be208b56fa3a3fb762ede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "flushMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="indexIntervalBytes")
    def index_interval_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "indexIntervalBytes"))

    @index_interval_bytes.setter
    def index_interval_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b9f11689177c4f5199c78f4c58252bc4f787e16f36c6331404f002d78d588099)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "indexIntervalBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxCompactionLagMs")
    def max_compaction_lag_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxCompactionLagMs"))

    @max_compaction_lag_ms.setter
    def max_compaction_lag_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68bed8c7e6c99cebf2e0be6a4714c819015623005d55c138af55631782773b91)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxCompactionLagMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxMessageBytes")
    def max_message_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "maxMessageBytes"))

    @max_message_bytes.setter
    def max_message_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2c52a8956a8d73136e6224eae20173fa2fdcc0b56f936a013b70c1210517704)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxMessageBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageDownConversionEnable")
    def message_down_conversion_enable(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "messageDownConversionEnable"))

    @message_down_conversion_enable.setter
    def message_down_conversion_enable(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8b24fb2bd572118518e4dd6aa295ed037f87e2bead6103941a8b5ca133cf110b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageDownConversionEnable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageFormatVersion")
    def message_format_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageFormatVersion"))

    @message_format_version.setter
    def message_format_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bad522dc6aaa6b8fb70219931466476097c7bd2ebdca66d6e0c2a5baa0d0143)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageFormatVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageTimestampDifferenceMaxMs")
    def message_timestamp_difference_max_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageTimestampDifferenceMaxMs"))

    @message_timestamp_difference_max_ms.setter
    def message_timestamp_difference_max_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27c25be26ad86bd2d74c4cd8c3a661b6fb0a63932ff82b06066e3d4734670b86)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageTimestampDifferenceMaxMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="messageTimestampType")
    def message_timestamp_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "messageTimestampType"))

    @message_timestamp_type.setter
    def message_timestamp_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__142922c1209d5955d0b5d149db34ae42eb42f58beee7622a1b80653c14421c74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "messageTimestampType", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCleanableDirtyRatio")
    def min_cleanable_dirty_ratio(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minCleanableDirtyRatio"))

    @min_cleanable_dirty_ratio.setter
    def min_cleanable_dirty_ratio(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f98a92c8c67ff0cf0987c2e663651b4857a880f2281dee03fc3efac78b62cf03)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCleanableDirtyRatio", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minCompactionLagMs")
    def min_compaction_lag_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "minCompactionLagMs"))

    @min_compaction_lag_ms.setter
    def min_compaction_lag_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d98f72ad508e1c45dc2ed5b84d024393f1ab3a2689abb5737d490db2260da78)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minCompactionLagMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInsyncReplicas")
    def min_insync_replicas(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInsyncReplicas"))

    @min_insync_replicas.setter
    def min_insync_replicas(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7aa8ceebadebd0e0e3b73bdca373b3ddc3295b09867854b0a859b556d949621)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInsyncReplicas", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="preallocate")
    def preallocate(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "preallocate"))

    @preallocate.setter
    def preallocate(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d246c6b64837f6e9bf9a92d9f2eb1a788ccfe7973e05f2111947934ee2627e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preallocate", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionBytes")
    def retention_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionBytes"))

    @retention_bytes.setter
    def retention_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5424a985a3f71bb9d26cd3dda66a9bcf1152734581aec845c33d83fa40880581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retentionMs")
    def retention_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retentionMs"))

    @retention_ms.setter
    def retention_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__043cb52dfd986b0a91f942986e5e73f07ca6ac35ba6623d75f459b4c0418d66c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retentionMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentBytes")
    def segment_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "segmentBytes"))

    @segment_bytes.setter
    def segment_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04b42eb917ebceba24fac54f62785dc08fa65ba8f00a9a2576128c974a87e7e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentIndexBytes")
    def segment_index_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "segmentIndexBytes"))

    @segment_index_bytes.setter
    def segment_index_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10aff4497f4e664712888ff279cdd421070d2f4e9b8eb95ac50852bfa0245a17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentIndexBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentJitterMs")
    def segment_jitter_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "segmentJitterMs"))

    @segment_jitter_ms.setter
    def segment_jitter_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb30c438134eafedbb563d9473511e4ec6341a2573786d11928a463d8c2504ec)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentJitterMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="segmentMs")
    def segment_ms(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "segmentMs"))

    @segment_ms.setter
    def segment_ms(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e930331d59c832c3cced2692554a2df6f0df26696581803605040afc27a7692c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "segmentMs", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseKafkaTopicConfigA]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseKafkaTopicConfigA]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseKafkaTopicConfigA]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87c7d5c19d42246135c1a14a5b4fb107e835fd27c4cd0c745eee4bf9a612f3f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DatabaseKafkaTopic",
    "DatabaseKafkaTopicConfig",
    "DatabaseKafkaTopicConfigA",
    "DatabaseKafkaTopicConfigAList",
    "DatabaseKafkaTopicConfigAOutputReference",
]

publication.publish()

def _typecheckingstub__48af6e99511012ab24131ded5553a2e42dc8f17c8f4b4d3caf94d86ae3d7dc49(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    name: builtins.str,
    config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DatabaseKafkaTopicConfigA, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    partition_count: typing.Optional[jsii.Number] = None,
    replication_factor: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__e334db016a4937e582bc20e4f8367dad60dfaa203e1b79c62a9a7a251694c17d(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1c76061f8e14913a5f4794c3e37188f90be087c01337b93354df781b35d0e114(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DatabaseKafkaTopicConfigA, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2310fe11a07e00c34db522f8a0fe5a08fdf65f59a6223d373b03a975922ecca3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0260d7898b4fdb25814bddbbc02f2097822ee51f977b095b6c027c0fd8cf33ac(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__878ddd5ec65713d657e818974db259e02fb30f3691ac96fc14004cd0213969e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afa0dd3e3bbb4a01f86e6a8caa54a0721c64520258668b9fc9a145d915e4f4f3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56aed1c94fa298b54c379154449754d6fef4f40b56acdb6ed66f85ecaa6f5df4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10c82bfade98a33bc84fade5fbda677ac9a2b51771df08ace502a0a77bc1ce81(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    name: builtins.str,
    config: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DatabaseKafkaTopicConfigA, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    partition_count: typing.Optional[jsii.Number] = None,
    replication_factor: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc47728514050fe3b4dc0ccc9f98886e142ce89c20ba4b8e0452780f3e736037(
    *,
    cleanup_policy: typing.Optional[builtins.str] = None,
    compression_type: typing.Optional[builtins.str] = None,
    delete_retention_ms: typing.Optional[builtins.str] = None,
    file_delete_delay_ms: typing.Optional[builtins.str] = None,
    flush_messages: typing.Optional[builtins.str] = None,
    flush_ms: typing.Optional[builtins.str] = None,
    index_interval_bytes: typing.Optional[builtins.str] = None,
    max_compaction_lag_ms: typing.Optional[builtins.str] = None,
    max_message_bytes: typing.Optional[builtins.str] = None,
    message_down_conversion_enable: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    message_format_version: typing.Optional[builtins.str] = None,
    message_timestamp_difference_max_ms: typing.Optional[builtins.str] = None,
    message_timestamp_type: typing.Optional[builtins.str] = None,
    min_cleanable_dirty_ratio: typing.Optional[jsii.Number] = None,
    min_compaction_lag_ms: typing.Optional[builtins.str] = None,
    min_insync_replicas: typing.Optional[jsii.Number] = None,
    preallocate: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retention_bytes: typing.Optional[builtins.str] = None,
    retention_ms: typing.Optional[builtins.str] = None,
    segment_bytes: typing.Optional[builtins.str] = None,
    segment_index_bytes: typing.Optional[builtins.str] = None,
    segment_jitter_ms: typing.Optional[builtins.str] = None,
    segment_ms: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df28fe0971bae8120dce2345a1e59e0acd30bcddf1f37f77e753ea0ef4f30c1b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4cc687dc0246a0cdd16d60e91b65c9d27bf953d1eefdca87e60e26c3b5f3b80d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f87bf6d4a57e2d9ec787f3295614968fda73257521294c532313e2696e8434d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ee18e15ba09cbdc2e8dc982c2fdfd123511d2147590e340a8673bf27642ff5e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffbebc3e472e2059332ea4075ceabbadbcb9de85f9322e608597a2f636003630(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00ff22f036cc508a77a896196957faac59dcd59207b1e8e54238cc852c1a9a81(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabaseKafkaTopicConfigA]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1f00bcf7f415e1b093ca50d67b696add8216dcf7f233b0aa08aebe7933d6cb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61600a547c80fa37b5fcd0778693b098d77d182f0cee14875f1a80595a2ba38d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__790a92289e4c6a7f33a98f7ed8b6b9483125edf516f0a52cb0ce1e5d7d69acf5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8edf90ff658fd837e08f2df998503ef8642f2d7be97c7a74209f53ad1012683c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b22f58ba4392798b1e2f09b7fd8a1acab48ab1cc691d46ec81a4d1bfa8950a85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__937e96ed3c6cacd481a5c2f80492f1f9bd66c72572d5c8b8d6145a31617ebcc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24556124999c5b24ddbe6bb0a83e2c7e8aab55410e4be208b56fa3a3fb762ede(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9f11689177c4f5199c78f4c58252bc4f787e16f36c6331404f002d78d588099(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68bed8c7e6c99cebf2e0be6a4714c819015623005d55c138af55631782773b91(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2c52a8956a8d73136e6224eae20173fa2fdcc0b56f936a013b70c1210517704(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8b24fb2bd572118518e4dd6aa295ed037f87e2bead6103941a8b5ca133cf110b(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bad522dc6aaa6b8fb70219931466476097c7bd2ebdca66d6e0c2a5baa0d0143(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27c25be26ad86bd2d74c4cd8c3a661b6fb0a63932ff82b06066e3d4734670b86(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__142922c1209d5955d0b5d149db34ae42eb42f58beee7622a1b80653c14421c74(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f98a92c8c67ff0cf0987c2e663651b4857a880f2281dee03fc3efac78b62cf03(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d98f72ad508e1c45dc2ed5b84d024393f1ab3a2689abb5737d490db2260da78(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7aa8ceebadebd0e0e3b73bdca373b3ddc3295b09867854b0a859b556d949621(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d246c6b64837f6e9bf9a92d9f2eb1a788ccfe7973e05f2111947934ee2627e4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5424a985a3f71bb9d26cd3dda66a9bcf1152734581aec845c33d83fa40880581(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__043cb52dfd986b0a91f942986e5e73f07ca6ac35ba6623d75f459b4c0418d66c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04b42eb917ebceba24fac54f62785dc08fa65ba8f00a9a2576128c974a87e7e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10aff4497f4e664712888ff279cdd421070d2f4e9b8eb95ac50852bfa0245a17(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb30c438134eafedbb563d9473511e4ec6341a2573786d11928a463d8c2504ec(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e930331d59c832c3cced2692554a2df6f0df26696581803605040afc27a7692c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87c7d5c19d42246135c1a14a5b4fb107e835fd27c4cd0c745eee4bf9a612f3f1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabaseKafkaTopicConfigA]],
) -> None:
    """Type checking stubs"""
    pass
