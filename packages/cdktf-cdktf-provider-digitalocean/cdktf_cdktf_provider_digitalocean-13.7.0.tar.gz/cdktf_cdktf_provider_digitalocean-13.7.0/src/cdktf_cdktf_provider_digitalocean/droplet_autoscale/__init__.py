r'''
# `digitalocean_droplet_autoscale`

Refer to the Terraform Registry for docs: [`digitalocean_droplet_autoscale`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale).
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


class DropletAutoscale(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscale",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale digitalocean_droplet_autoscale}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        config: typing.Union["DropletAutoscaleConfigA", typing.Dict[builtins.str, typing.Any]],
        droplet_template: typing.Union["DropletAutoscaleDropletTemplate", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale digitalocean_droplet_autoscale} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#config DropletAutoscale#config}
        :param droplet_template: droplet_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#droplet_template DropletAutoscale#droplet_template}
        :param name: Name of the Droplet autoscale pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#name DropletAutoscale#name}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__385d73781b73d62490e64d9d4b5e21e9ca1897f566f31d3b0f8e0f0b397a24f4)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config_ = DropletAutoscaleConfig(
            config=config,
            droplet_template=droplet_template,
            name=name,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config_])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a DropletAutoscale resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DropletAutoscale to import.
        :param import_from_id: The id of the existing DropletAutoscale that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DropletAutoscale to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__69a1ae5ff43ef87fd54d79bca3f70a45b8a2a9554c3b286ef07254273569e2a3)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putConfig")
    def put_config(
        self,
        *,
        cooldown_minutes: typing.Optional[jsii.Number] = None,
        max_instances: typing.Optional[jsii.Number] = None,
        min_instances: typing.Optional[jsii.Number] = None,
        target_cpu_utilization: typing.Optional[jsii.Number] = None,
        target_memory_utilization: typing.Optional[jsii.Number] = None,
        target_number_instances: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cooldown_minutes: Cooldown duration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#cooldown_minutes DropletAutoscale#cooldown_minutes}
        :param max_instances: Max number of members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#max_instances DropletAutoscale#max_instances}
        :param min_instances: Min number of members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#min_instances DropletAutoscale#min_instances}
        :param target_cpu_utilization: CPU target threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_cpu_utilization DropletAutoscale#target_cpu_utilization}
        :param target_memory_utilization: Memory target threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_memory_utilization DropletAutoscale#target_memory_utilization}
        :param target_number_instances: Target number of members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_number_instances DropletAutoscale#target_number_instances}
        '''
        value = DropletAutoscaleConfigA(
            cooldown_minutes=cooldown_minutes,
            max_instances=max_instances,
            min_instances=min_instances,
            target_cpu_utilization=target_cpu_utilization,
            target_memory_utilization=target_memory_utilization,
            target_number_instances=target_number_instances,
        )

        return typing.cast(None, jsii.invoke(self, "putConfig", [value]))

    @jsii.member(jsii_name="putDropletTemplate")
    def put_droplet_template(
        self,
        *,
        image: builtins.str,
        region: builtins.str,
        size: builtins.str,
        ssh_keys: typing.Sequence[builtins.str],
        ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        project_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_data: typing.Optional[builtins.str] = None,
        vpc_uuid: typing.Optional[builtins.str] = None,
        with_droplet_agent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param image: Droplet image. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#image DropletAutoscale#image}
        :param region: Droplet region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#region DropletAutoscale#region}
        :param size: Droplet size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#size DropletAutoscale#size}
        :param ssh_keys: Droplet SSH keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#ssh_keys DropletAutoscale#ssh_keys}
        :param ipv6: Enable droplet IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#ipv6 DropletAutoscale#ipv6}
        :param project_id: Droplet project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#project_id DropletAutoscale#project_id}
        :param tags: Droplet tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#tags DropletAutoscale#tags}
        :param user_data: Droplet user data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#user_data DropletAutoscale#user_data}
        :param vpc_uuid: Droplet VPC UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#vpc_uuid DropletAutoscale#vpc_uuid}
        :param with_droplet_agent: Enable droplet agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#with_droplet_agent DropletAutoscale#with_droplet_agent}
        '''
        value = DropletAutoscaleDropletTemplate(
            image=image,
            region=region,
            size=size,
            ssh_keys=ssh_keys,
            ipv6=ipv6,
            project_id=project_id,
            tags=tags,
            user_data=user_data,
            vpc_uuid=vpc_uuid,
            with_droplet_agent=with_droplet_agent,
        )

        return typing.cast(None, jsii.invoke(self, "putDropletTemplate", [value]))

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
    def config(self) -> "DropletAutoscaleConfigAOutputReference":
        return typing.cast("DropletAutoscaleConfigAOutputReference", jsii.get(self, "config"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="currentUtilization")
    def current_utilization(self) -> "DropletAutoscaleCurrentUtilizationList":
        return typing.cast("DropletAutoscaleCurrentUtilizationList", jsii.get(self, "currentUtilization"))

    @builtins.property
    @jsii.member(jsii_name="dropletTemplate")
    def droplet_template(self) -> "DropletAutoscaleDropletTemplateOutputReference":
        return typing.cast("DropletAutoscaleDropletTemplateOutputReference", jsii.get(self, "dropletTemplate"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(self) -> typing.Optional["DropletAutoscaleConfigA"]:
        return typing.cast(typing.Optional["DropletAutoscaleConfigA"], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="dropletTemplateInput")
    def droplet_template_input(
        self,
    ) -> typing.Optional["DropletAutoscaleDropletTemplate"]:
        return typing.cast(typing.Optional["DropletAutoscaleDropletTemplate"], jsii.get(self, "dropletTemplateInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__68965bbeaea21e376f6aca62eba659ebbd153b287c24923bb2303380057480eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "config": "config",
        "droplet_template": "dropletTemplate",
        "name": "name",
    },
)
class DropletAutoscaleConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        config: typing.Union["DropletAutoscaleConfigA", typing.Dict[builtins.str, typing.Any]],
        droplet_template: typing.Union["DropletAutoscaleDropletTemplate", typing.Dict[builtins.str, typing.Any]],
        name: builtins.str,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param config: config block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#config DropletAutoscale#config}
        :param droplet_template: droplet_template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#droplet_template DropletAutoscale#droplet_template}
        :param name: Name of the Droplet autoscale pool. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#name DropletAutoscale#name}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(config, dict):
            config = DropletAutoscaleConfigA(**config)
        if isinstance(droplet_template, dict):
            droplet_template = DropletAutoscaleDropletTemplate(**droplet_template)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__89ef440cc8bbbc5b2235f3746b1bbeb9b1bdc92dd24a9652f7bfc9b0103065a7)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
            check_type(argname="argument droplet_template", value=droplet_template, expected_type=type_hints["droplet_template"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "config": config,
            "droplet_template": droplet_template,
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
    def config(self) -> "DropletAutoscaleConfigA":
        '''config block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#config DropletAutoscale#config}
        '''
        result = self._values.get("config")
        assert result is not None, "Required property 'config' is missing"
        return typing.cast("DropletAutoscaleConfigA", result)

    @builtins.property
    def droplet_template(self) -> "DropletAutoscaleDropletTemplate":
        '''droplet_template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#droplet_template DropletAutoscale#droplet_template}
        '''
        result = self._values.get("droplet_template")
        assert result is not None, "Required property 'droplet_template' is missing"
        return typing.cast("DropletAutoscaleDropletTemplate", result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Droplet autoscale pool.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#name DropletAutoscale#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DropletAutoscaleConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleConfigA",
    jsii_struct_bases=[],
    name_mapping={
        "cooldown_minutes": "cooldownMinutes",
        "max_instances": "maxInstances",
        "min_instances": "minInstances",
        "target_cpu_utilization": "targetCpuUtilization",
        "target_memory_utilization": "targetMemoryUtilization",
        "target_number_instances": "targetNumberInstances",
    },
)
class DropletAutoscaleConfigA:
    def __init__(
        self,
        *,
        cooldown_minutes: typing.Optional[jsii.Number] = None,
        max_instances: typing.Optional[jsii.Number] = None,
        min_instances: typing.Optional[jsii.Number] = None,
        target_cpu_utilization: typing.Optional[jsii.Number] = None,
        target_memory_utilization: typing.Optional[jsii.Number] = None,
        target_number_instances: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param cooldown_minutes: Cooldown duration. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#cooldown_minutes DropletAutoscale#cooldown_minutes}
        :param max_instances: Max number of members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#max_instances DropletAutoscale#max_instances}
        :param min_instances: Min number of members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#min_instances DropletAutoscale#min_instances}
        :param target_cpu_utilization: CPU target threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_cpu_utilization DropletAutoscale#target_cpu_utilization}
        :param target_memory_utilization: Memory target threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_memory_utilization DropletAutoscale#target_memory_utilization}
        :param target_number_instances: Target number of members. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_number_instances DropletAutoscale#target_number_instances}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44e515df6a3829c319c75030193157f3798ac166d29bf71b686d47b30d2a15c8)
            check_type(argname="argument cooldown_minutes", value=cooldown_minutes, expected_type=type_hints["cooldown_minutes"])
            check_type(argname="argument max_instances", value=max_instances, expected_type=type_hints["max_instances"])
            check_type(argname="argument min_instances", value=min_instances, expected_type=type_hints["min_instances"])
            check_type(argname="argument target_cpu_utilization", value=target_cpu_utilization, expected_type=type_hints["target_cpu_utilization"])
            check_type(argname="argument target_memory_utilization", value=target_memory_utilization, expected_type=type_hints["target_memory_utilization"])
            check_type(argname="argument target_number_instances", value=target_number_instances, expected_type=type_hints["target_number_instances"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cooldown_minutes is not None:
            self._values["cooldown_minutes"] = cooldown_minutes
        if max_instances is not None:
            self._values["max_instances"] = max_instances
        if min_instances is not None:
            self._values["min_instances"] = min_instances
        if target_cpu_utilization is not None:
            self._values["target_cpu_utilization"] = target_cpu_utilization
        if target_memory_utilization is not None:
            self._values["target_memory_utilization"] = target_memory_utilization
        if target_number_instances is not None:
            self._values["target_number_instances"] = target_number_instances

    @builtins.property
    def cooldown_minutes(self) -> typing.Optional[jsii.Number]:
        '''Cooldown duration.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#cooldown_minutes DropletAutoscale#cooldown_minutes}
        '''
        result = self._values.get("cooldown_minutes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_instances(self) -> typing.Optional[jsii.Number]:
        '''Max number of members.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#max_instances DropletAutoscale#max_instances}
        '''
        result = self._values.get("max_instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def min_instances(self) -> typing.Optional[jsii.Number]:
        '''Min number of members.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#min_instances DropletAutoscale#min_instances}
        '''
        result = self._values.get("min_instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_cpu_utilization(self) -> typing.Optional[jsii.Number]:
        '''CPU target threshold.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_cpu_utilization DropletAutoscale#target_cpu_utilization}
        '''
        result = self._values.get("target_cpu_utilization")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_memory_utilization(self) -> typing.Optional[jsii.Number]:
        '''Memory target threshold.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_memory_utilization DropletAutoscale#target_memory_utilization}
        '''
        result = self._values.get("target_memory_utilization")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def target_number_instances(self) -> typing.Optional[jsii.Number]:
        '''Target number of members.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#target_number_instances DropletAutoscale#target_number_instances}
        '''
        result = self._values.get("target_number_instances")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DropletAutoscaleConfigA(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DropletAutoscaleConfigAOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleConfigAOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e3a0303060564682eab203e18418dd1aa8cff4e4f36f7b5835a16d148b56e9cd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCooldownMinutes")
    def reset_cooldown_minutes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCooldownMinutes", []))

    @jsii.member(jsii_name="resetMaxInstances")
    def reset_max_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxInstances", []))

    @jsii.member(jsii_name="resetMinInstances")
    def reset_min_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinInstances", []))

    @jsii.member(jsii_name="resetTargetCpuUtilization")
    def reset_target_cpu_utilization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetCpuUtilization", []))

    @jsii.member(jsii_name="resetTargetMemoryUtilization")
    def reset_target_memory_utilization(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetMemoryUtilization", []))

    @jsii.member(jsii_name="resetTargetNumberInstances")
    def reset_target_number_instances(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetNumberInstances", []))

    @builtins.property
    @jsii.member(jsii_name="cooldownMinutesInput")
    def cooldown_minutes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cooldownMinutesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxInstancesInput")
    def max_instances_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="minInstancesInput")
    def min_instances_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="targetCpuUtilizationInput")
    def target_cpu_utilization_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetCpuUtilizationInput"))

    @builtins.property
    @jsii.member(jsii_name="targetMemoryUtilizationInput")
    def target_memory_utilization_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetMemoryUtilizationInput"))

    @builtins.property
    @jsii.member(jsii_name="targetNumberInstancesInput")
    def target_number_instances_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetNumberInstancesInput"))

    @builtins.property
    @jsii.member(jsii_name="cooldownMinutes")
    def cooldown_minutes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cooldownMinutes"))

    @cooldown_minutes.setter
    def cooldown_minutes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07341e500d77428ff348add48f353029cd6d9280be0dd026767658bf4244f452)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cooldownMinutes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxInstances")
    def max_instances(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxInstances"))

    @max_instances.setter
    def max_instances(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__296ffb83985914dd792587ccdc52f3727cb8984c9beef749ffab0d7084b81ebe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minInstances")
    def min_instances(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minInstances"))

    @min_instances.setter
    def min_instances(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e20364bfa44e2494780dbcd67ba819f9cc37a3b1e1813744cb03d20d16c1fc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetCpuUtilization")
    def target_cpu_utilization(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetCpuUtilization"))

    @target_cpu_utilization.setter
    def target_cpu_utilization(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b675ef9c25cd079a530005013a3f06bcc5fa6dc95e829c3a4b3b6e24946c26c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetCpuUtilization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetMemoryUtilization")
    def target_memory_utilization(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetMemoryUtilization"))

    @target_memory_utilization.setter
    def target_memory_utilization(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c61a3bc5d60f60bf1498936d2042f48beb30ed8c99999594dad813c7e0cdff0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetMemoryUtilization", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetNumberInstances")
    def target_number_instances(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetNumberInstances"))

    @target_number_instances.setter
    def target_number_instances(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f431a0aee1dd983b1e6ea9424c170216497e7af11529c257e5a74852a08138fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetNumberInstances", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DropletAutoscaleConfigA]:
        return typing.cast(typing.Optional[DropletAutoscaleConfigA], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[DropletAutoscaleConfigA]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cd9e03fcb2a9bee616c8abe70a75f2b75a54c31dfaf76530ef459a06cdb1a2d3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleCurrentUtilization",
    jsii_struct_bases=[],
    name_mapping={},
)
class DropletAutoscaleCurrentUtilization:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DropletAutoscaleCurrentUtilization(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DropletAutoscaleCurrentUtilizationList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleCurrentUtilizationList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c9dd170b97748e5f5a219700d49a88b9a9c4e0104e1aaff969bea9ac562c3d9e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DropletAutoscaleCurrentUtilizationOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b3c7cfdda0eced2339d7f3a19c345064986580a52224e0fa2610b5974f90ee4)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DropletAutoscaleCurrentUtilizationOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32f3f76190f75741960b98ab457b26dbec8f14d85566b13be58987594d08a595)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c91d65071a315c83a07a3a572e6ec9b9876555d089f22e851f2b4d9fb2110d4b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f407561011a55d5a621b44972793424ed55949f86abd29e3fb077ca857daab66)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DropletAutoscaleCurrentUtilizationOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleCurrentUtilizationOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81dec228aa7df71229608dfbabfa40d2bc031e8c23670ad42cf6627aa648a1d4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="cpu")
    def cpu(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cpu"))

    @builtins.property
    @jsii.member(jsii_name="memory")
    def memory(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "memory"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DropletAutoscaleCurrentUtilization]:
        return typing.cast(typing.Optional[DropletAutoscaleCurrentUtilization], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DropletAutoscaleCurrentUtilization],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ee02a08ec4ced37e4508b0623a8e91f9d67592514531a036b838d223754db60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleDropletTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "image": "image",
        "region": "region",
        "size": "size",
        "ssh_keys": "sshKeys",
        "ipv6": "ipv6",
        "project_id": "projectId",
        "tags": "tags",
        "user_data": "userData",
        "vpc_uuid": "vpcUuid",
        "with_droplet_agent": "withDropletAgent",
    },
)
class DropletAutoscaleDropletTemplate:
    def __init__(
        self,
        *,
        image: builtins.str,
        region: builtins.str,
        size: builtins.str,
        ssh_keys: typing.Sequence[builtins.str],
        ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        project_id: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_data: typing.Optional[builtins.str] = None,
        vpc_uuid: typing.Optional[builtins.str] = None,
        with_droplet_agent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param image: Droplet image. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#image DropletAutoscale#image}
        :param region: Droplet region. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#region DropletAutoscale#region}
        :param size: Droplet size. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#size DropletAutoscale#size}
        :param ssh_keys: Droplet SSH keys. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#ssh_keys DropletAutoscale#ssh_keys}
        :param ipv6: Enable droplet IPv6. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#ipv6 DropletAutoscale#ipv6}
        :param project_id: Droplet project ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#project_id DropletAutoscale#project_id}
        :param tags: Droplet tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#tags DropletAutoscale#tags}
        :param user_data: Droplet user data. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#user_data DropletAutoscale#user_data}
        :param vpc_uuid: Droplet VPC UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#vpc_uuid DropletAutoscale#vpc_uuid}
        :param with_droplet_agent: Enable droplet agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#with_droplet_agent DropletAutoscale#with_droplet_agent}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f849eb10f4e50a6f6198c2c412c87f42fd261902eb0ba64d473ef578d22314d5)
            check_type(argname="argument image", value=image, expected_type=type_hints["image"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
            check_type(argname="argument ssh_keys", value=ssh_keys, expected_type=type_hints["ssh_keys"])
            check_type(argname="argument ipv6", value=ipv6, expected_type=type_hints["ipv6"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument user_data", value=user_data, expected_type=type_hints["user_data"])
            check_type(argname="argument vpc_uuid", value=vpc_uuid, expected_type=type_hints["vpc_uuid"])
            check_type(argname="argument with_droplet_agent", value=with_droplet_agent, expected_type=type_hints["with_droplet_agent"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "image": image,
            "region": region,
            "size": size,
            "ssh_keys": ssh_keys,
        }
        if ipv6 is not None:
            self._values["ipv6"] = ipv6
        if project_id is not None:
            self._values["project_id"] = project_id
        if tags is not None:
            self._values["tags"] = tags
        if user_data is not None:
            self._values["user_data"] = user_data
        if vpc_uuid is not None:
            self._values["vpc_uuid"] = vpc_uuid
        if with_droplet_agent is not None:
            self._values["with_droplet_agent"] = with_droplet_agent

    @builtins.property
    def image(self) -> builtins.str:
        '''Droplet image.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#image DropletAutoscale#image}
        '''
        result = self._values.get("image")
        assert result is not None, "Required property 'image' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Droplet region.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#region DropletAutoscale#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def size(self) -> builtins.str:
        '''Droplet size.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#size DropletAutoscale#size}
        '''
        result = self._values.get("size")
        assert result is not None, "Required property 'size' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def ssh_keys(self) -> typing.List[builtins.str]:
        '''Droplet SSH keys.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#ssh_keys DropletAutoscale#ssh_keys}
        '''
        result = self._values.get("ssh_keys")
        assert result is not None, "Required property 'ssh_keys' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def ipv6(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable droplet IPv6.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#ipv6 DropletAutoscale#ipv6}
        '''
        result = self._values.get("ipv6")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Droplet project ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#project_id DropletAutoscale#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Droplet tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#tags DropletAutoscale#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_data(self) -> typing.Optional[builtins.str]:
        '''Droplet user data.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#user_data DropletAutoscale#user_data}
        '''
        result = self._values.get("user_data")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_uuid(self) -> typing.Optional[builtins.str]:
        '''Droplet VPC UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#vpc_uuid DropletAutoscale#vpc_uuid}
        '''
        result = self._values.get("vpc_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def with_droplet_agent(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Enable droplet agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/droplet_autoscale#with_droplet_agent DropletAutoscale#with_droplet_agent}
        '''
        result = self._values.get("with_droplet_agent")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DropletAutoscaleDropletTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DropletAutoscaleDropletTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dropletAutoscale.DropletAutoscaleDropletTemplateOutputReference",
):
    def __init__(
        self,
        terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b57ca24b78acd78bb2cb5f497a8b428e1206e7c99fd0472d07d8526e694f9f59)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIpv6")
    def reset_ipv6(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIpv6", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUserData")
    def reset_user_data(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserData", []))

    @jsii.member(jsii_name="resetVpcUuid")
    def reset_vpc_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcUuid", []))

    @jsii.member(jsii_name="resetWithDropletAgent")
    def reset_with_droplet_agent(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWithDropletAgent", []))

    @builtins.property
    @jsii.member(jsii_name="imageInput")
    def image_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "imageInput"))

    @builtins.property
    @jsii.member(jsii_name="ipv6Input")
    def ipv6_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "ipv6Input"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sshKeysInput")
    def ssh_keys_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "sshKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="userDataInput")
    def user_data_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userDataInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcUuidInput")
    def vpc_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="withDropletAgentInput")
    def with_droplet_agent_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "withDropletAgentInput"))

    @builtins.property
    @jsii.member(jsii_name="image")
    def image(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "image"))

    @image.setter
    def image(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ad42872c1f479b83dc59c00770f382bd50fed5ae8f09861c1808dca203af6f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "image", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "ipv6"))

    @ipv6.setter
    def ipv6(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46b633f08a30d45d7b8ca4787199192cec2515c1a25705be3d9f1e2d9ea9ac09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ipv6", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__57b3efaac37c5e22a4620cb34305930613579b27a3e779818597cf9aa37c3a8b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbaab147aaf75e3059d78ca5413f6b3d854724a55d60bad2a0dc914f78b3e944)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "size"))

    @size.setter
    def size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7e4bcf54026cfbd23ff0c68fffbcfcef7fdacea4b8592a8616772d7d7667199)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "size", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sshKeys")
    def ssh_keys(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sshKeys"))

    @ssh_keys.setter
    def ssh_keys(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__018a198538172bd68222c6b714171b69d9fc15cc064a8a193fef7bc237354c7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sshKeys", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fab1f954a7a1f71dcafbe565da930e709c4ad37bdd4b362379cb2d0de84dff55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userData")
    def user_data(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userData"))

    @user_data.setter
    def user_data(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5582f10f38204c4d1df3ba6dd331709aa02cb8fa4afaac41d3ace556f6f27188)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userData", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcUuid")
    def vpc_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcUuid"))

    @vpc_uuid.setter
    def vpc_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d813543c650eb705643fe2ccfe60c7ee0e8c2298a66e8450e9e40c0d07c0bd9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="withDropletAgent")
    def with_droplet_agent(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "withDropletAgent"))

    @with_droplet_agent.setter
    def with_droplet_agent(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ca7031a02ab4d256f0f36b6cf7b5de89a9da6b4751b0170158333742b365bbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "withDropletAgent", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DropletAutoscaleDropletTemplate]:
        return typing.cast(typing.Optional[DropletAutoscaleDropletTemplate], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DropletAutoscaleDropletTemplate],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7588bef1e61a9964f2fc112e0b173f1855c51cfd8e35bca2e709a56fc55d82c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DropletAutoscale",
    "DropletAutoscaleConfig",
    "DropletAutoscaleConfigA",
    "DropletAutoscaleConfigAOutputReference",
    "DropletAutoscaleCurrentUtilization",
    "DropletAutoscaleCurrentUtilizationList",
    "DropletAutoscaleCurrentUtilizationOutputReference",
    "DropletAutoscaleDropletTemplate",
    "DropletAutoscaleDropletTemplateOutputReference",
]

publication.publish()

def _typecheckingstub__385d73781b73d62490e64d9d4b5e21e9ca1897f566f31d3b0f8e0f0b397a24f4(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    config: typing.Union[DropletAutoscaleConfigA, typing.Dict[builtins.str, typing.Any]],
    droplet_template: typing.Union[DropletAutoscaleDropletTemplate, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
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

def _typecheckingstub__69a1ae5ff43ef87fd54d79bca3f70a45b8a2a9554c3b286ef07254273569e2a3(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__68965bbeaea21e376f6aca62eba659ebbd153b287c24923bb2303380057480eb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89ef440cc8bbbc5b2235f3746b1bbeb9b1bdc92dd24a9652f7bfc9b0103065a7(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    config: typing.Union[DropletAutoscaleConfigA, typing.Dict[builtins.str, typing.Any]],
    droplet_template: typing.Union[DropletAutoscaleDropletTemplate, typing.Dict[builtins.str, typing.Any]],
    name: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44e515df6a3829c319c75030193157f3798ac166d29bf71b686d47b30d2a15c8(
    *,
    cooldown_minutes: typing.Optional[jsii.Number] = None,
    max_instances: typing.Optional[jsii.Number] = None,
    min_instances: typing.Optional[jsii.Number] = None,
    target_cpu_utilization: typing.Optional[jsii.Number] = None,
    target_memory_utilization: typing.Optional[jsii.Number] = None,
    target_number_instances: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e3a0303060564682eab203e18418dd1aa8cff4e4f36f7b5835a16d148b56e9cd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07341e500d77428ff348add48f353029cd6d9280be0dd026767658bf4244f452(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__296ffb83985914dd792587ccdc52f3727cb8984c9beef749ffab0d7084b81ebe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e20364bfa44e2494780dbcd67ba819f9cc37a3b1e1813744cb03d20d16c1fc0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b675ef9c25cd079a530005013a3f06bcc5fa6dc95e829c3a4b3b6e24946c26c4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c61a3bc5d60f60bf1498936d2042f48beb30ed8c99999594dad813c7e0cdff0a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f431a0aee1dd983b1e6ea9424c170216497e7af11529c257e5a74852a08138fe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cd9e03fcb2a9bee616c8abe70a75f2b75a54c31dfaf76530ef459a06cdb1a2d3(
    value: typing.Optional[DropletAutoscaleConfigA],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c9dd170b97748e5f5a219700d49a88b9a9c4e0104e1aaff969bea9ac562c3d9e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b3c7cfdda0eced2339d7f3a19c345064986580a52224e0fa2610b5974f90ee4(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32f3f76190f75741960b98ab457b26dbec8f14d85566b13be58987594d08a595(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c91d65071a315c83a07a3a572e6ec9b9876555d089f22e851f2b4d9fb2110d4b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f407561011a55d5a621b44972793424ed55949f86abd29e3fb077ca857daab66(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81dec228aa7df71229608dfbabfa40d2bc031e8c23670ad42cf6627aa648a1d4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ee02a08ec4ced37e4508b0623a8e91f9d67592514531a036b838d223754db60(
    value: typing.Optional[DropletAutoscaleCurrentUtilization],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f849eb10f4e50a6f6198c2c412c87f42fd261902eb0ba64d473ef578d22314d5(
    *,
    image: builtins.str,
    region: builtins.str,
    size: builtins.str,
    ssh_keys: typing.Sequence[builtins.str],
    ipv6: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    project_id: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_data: typing.Optional[builtins.str] = None,
    vpc_uuid: typing.Optional[builtins.str] = None,
    with_droplet_agent: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b57ca24b78acd78bb2cb5f497a8b428e1206e7c99fd0472d07d8526e694f9f59(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ad42872c1f479b83dc59c00770f382bd50fed5ae8f09861c1808dca203af6f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46b633f08a30d45d7b8ca4787199192cec2515c1a25705be3d9f1e2d9ea9ac09(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__57b3efaac37c5e22a4620cb34305930613579b27a3e779818597cf9aa37c3a8b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbaab147aaf75e3059d78ca5413f6b3d854724a55d60bad2a0dc914f78b3e944(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7e4bcf54026cfbd23ff0c68fffbcfcef7fdacea4b8592a8616772d7d7667199(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__018a198538172bd68222c6b714171b69d9fc15cc064a8a193fef7bc237354c7c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fab1f954a7a1f71dcafbe565da930e709c4ad37bdd4b362379cb2d0de84dff55(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5582f10f38204c4d1df3ba6dd331709aa02cb8fa4afaac41d3ace556f6f27188(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d813543c650eb705643fe2ccfe60c7ee0e8c2298a66e8450e9e40c0d07c0bd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ca7031a02ab4d256f0f36b6cf7b5de89a9da6b4751b0170158333742b365bbc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7588bef1e61a9964f2fc112e0b173f1855c51cfd8e35bca2e709a56fc55d82c4(
    value: typing.Optional[DropletAutoscaleDropletTemplate],
) -> None:
    """Type checking stubs"""
    pass
