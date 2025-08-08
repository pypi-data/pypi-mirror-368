r'''
# `digitalocean_partner_attachment`

Refer to the Terraform Registry for docs: [`digitalocean_partner_attachment`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment).
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


class PartnerAttachment(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.partnerAttachment.PartnerAttachment",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment digitalocean_partner_attachment}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        connection_bandwidth_in_mbps: jsii.Number,
        naas_provider: builtins.str,
        name: builtins.str,
        region: builtins.str,
        vpc_ids: typing.Sequence[builtins.str],
        bgp: typing.Optional[typing.Union["PartnerAttachmentBgp", typing.Dict[builtins.str, typing.Any]]] = None,
        parent_uuid: typing.Optional[builtins.str] = None,
        redundancy_zone: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["PartnerAttachmentTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment digitalocean_partner_attachment} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param connection_bandwidth_in_mbps: The connection bandwidth in Mbps. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#connection_bandwidth_in_mbps PartnerAttachment#connection_bandwidth_in_mbps}
        :param naas_provider: The NaaS provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#naas_provider PartnerAttachment#naas_provider}
        :param name: The name of the Partner Attachment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#name PartnerAttachment#name}
        :param region: The region where the Partner Attachment will be created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#region PartnerAttachment#region}
        :param vpc_ids: The list of VPC IDs to attach the Partner Attachment to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#vpc_ids PartnerAttachment#vpc_ids}
        :param bgp: bgp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#bgp PartnerAttachment#bgp}
        :param parent_uuid: The UUID of the Parent Partner Attachment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#parent_uuid PartnerAttachment#parent_uuid}
        :param redundancy_zone: The redundancy zone for the NaaS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#redundancy_zone PartnerAttachment#redundancy_zone}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#timeouts PartnerAttachment#timeouts}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a440716fc49276a705f71fd6e17defd5fb40d26a16ddd7aa7f24ec6b7826ee74)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = PartnerAttachmentConfig(
            connection_bandwidth_in_mbps=connection_bandwidth_in_mbps,
            naas_provider=naas_provider,
            name=name,
            region=region,
            vpc_ids=vpc_ids,
            bgp=bgp,
            parent_uuid=parent_uuid,
            redundancy_zone=redundancy_zone,
            timeouts=timeouts,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="generateConfigForImport")
    @builtins.classmethod
    def generate_config_for_import(
        cls,
        scope: _constructs_77d1e7e8.Construct,
        import_to_id: builtins.str,
        import_from_id: builtins.str,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    ) -> _cdktf_9a9027ec.ImportableResource:
        '''Generates CDKTF code for importing a PartnerAttachment resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the PartnerAttachment to import.
        :param import_from_id: The id of the existing PartnerAttachment that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the PartnerAttachment to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__156c740c23b1d5b743a59dcfc1593972244d910910b8084b8f356e98871254ea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putBgp")
    def put_bgp(
        self,
        *,
        auth_key: typing.Optional[builtins.str] = None,
        local_router_ip: typing.Optional[builtins.str] = None,
        peer_router_asn: typing.Optional[jsii.Number] = None,
        peer_router_ip: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#auth_key PartnerAttachment#auth_key}.
        :param local_router_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#local_router_ip PartnerAttachment#local_router_ip}.
        :param peer_router_asn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#peer_router_asn PartnerAttachment#peer_router_asn}.
        :param peer_router_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#peer_router_ip PartnerAttachment#peer_router_ip}.
        '''
        value = PartnerAttachmentBgp(
            auth_key=auth_key,
            local_router_ip=local_router_ip,
            peer_router_asn=peer_router_asn,
            peer_router_ip=peer_router_ip,
        )

        return typing.cast(None, jsii.invoke(self, "putBgp", [value]))

    @jsii.member(jsii_name="putTimeouts")
    def put_timeouts(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#create PartnerAttachment#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#delete PartnerAttachment#delete}.
        '''
        value = PartnerAttachmentTimeouts(create=create, delete=delete)

        return typing.cast(None, jsii.invoke(self, "putTimeouts", [value]))

    @jsii.member(jsii_name="resetBgp")
    def reset_bgp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgp", []))

    @jsii.member(jsii_name="resetParentUuid")
    def reset_parent_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentUuid", []))

    @jsii.member(jsii_name="resetRedundancyZone")
    def reset_redundancy_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedundancyZone", []))

    @jsii.member(jsii_name="resetTimeouts")
    def reset_timeouts(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimeouts", []))

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
    @jsii.member(jsii_name="bgp")
    def bgp(self) -> "PartnerAttachmentBgpOutputReference":
        return typing.cast("PartnerAttachmentBgpOutputReference", jsii.get(self, "bgp"))

    @builtins.property
    @jsii.member(jsii_name="children")
    def children(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "children"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @builtins.property
    @jsii.member(jsii_name="state")
    def state(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "state"))

    @builtins.property
    @jsii.member(jsii_name="timeouts")
    def timeouts(self) -> "PartnerAttachmentTimeoutsOutputReference":
        return typing.cast("PartnerAttachmentTimeoutsOutputReference", jsii.get(self, "timeouts"))

    @builtins.property
    @jsii.member(jsii_name="bgpInput")
    def bgp_input(self) -> typing.Optional["PartnerAttachmentBgp"]:
        return typing.cast(typing.Optional["PartnerAttachmentBgp"], jsii.get(self, "bgpInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionBandwidthInMbpsInput")
    def connection_bandwidth_in_mbps_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectionBandwidthInMbpsInput"))

    @builtins.property
    @jsii.member(jsii_name="naasProviderInput")
    def naas_provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "naasProviderInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parentUuidInput")
    def parent_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="redundancyZoneInput")
    def redundancy_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "redundancyZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="timeoutsInput")
    def timeouts_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PartnerAttachmentTimeouts"]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, "PartnerAttachmentTimeouts"]], jsii.get(self, "timeoutsInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcIdsInput")
    def vpc_ids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "vpcIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="connectionBandwidthInMbps")
    def connection_bandwidth_in_mbps(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectionBandwidthInMbps"))

    @connection_bandwidth_in_mbps.setter
    def connection_bandwidth_in_mbps(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__504717f35d79a49b82a946eff43de366865afa2f28e1408e15dfbb8d56d423f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectionBandwidthInMbps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="naasProvider")
    def naas_provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "naasProvider"))

    @naas_provider.setter
    def naas_provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8160ceaccba028c67e4442a12293a23501827f09a5cafd02bdfe23996a61765)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "naasProvider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c8bb1bb9c2d3bf753b6233ac435fd653faca443b0c936447410b4de4207be5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentUuid")
    def parent_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentUuid"))

    @parent_uuid.setter
    def parent_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0dced98dfcfccc0f0a34f1e2fc3797f3668da6b133f6219911fa654b2df38d10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redundancyZone")
    def redundancy_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "redundancyZone"))

    @redundancy_zone.setter
    def redundancy_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__053e0169ee77c1cc6eff3f51b726444917568cc67da5836355444f661c760ae4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redundancyZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc6d7d26ef6d3b95cef90efd81959ce0b3306fc36e97f3b4ca863a009b5666ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcIds")
    def vpc_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "vpcIds"))

    @vpc_ids.setter
    def vpc_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d98dc3a39a8caba4efae7aca9b029663b24156e044b2ba9b8ca78883798002b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcIds", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.partnerAttachment.PartnerAttachmentBgp",
    jsii_struct_bases=[],
    name_mapping={
        "auth_key": "authKey",
        "local_router_ip": "localRouterIp",
        "peer_router_asn": "peerRouterAsn",
        "peer_router_ip": "peerRouterIp",
    },
)
class PartnerAttachmentBgp:
    def __init__(
        self,
        *,
        auth_key: typing.Optional[builtins.str] = None,
        local_router_ip: typing.Optional[builtins.str] = None,
        peer_router_asn: typing.Optional[jsii.Number] = None,
        peer_router_ip: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param auth_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#auth_key PartnerAttachment#auth_key}.
        :param local_router_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#local_router_ip PartnerAttachment#local_router_ip}.
        :param peer_router_asn: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#peer_router_asn PartnerAttachment#peer_router_asn}.
        :param peer_router_ip: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#peer_router_ip PartnerAttachment#peer_router_ip}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a8befe5052a221a529ceb23dc2b08e95dbdc2d46f1fa277dc64c9569e9caf9d3)
            check_type(argname="argument auth_key", value=auth_key, expected_type=type_hints["auth_key"])
            check_type(argname="argument local_router_ip", value=local_router_ip, expected_type=type_hints["local_router_ip"])
            check_type(argname="argument peer_router_asn", value=peer_router_asn, expected_type=type_hints["peer_router_asn"])
            check_type(argname="argument peer_router_ip", value=peer_router_ip, expected_type=type_hints["peer_router_ip"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if auth_key is not None:
            self._values["auth_key"] = auth_key
        if local_router_ip is not None:
            self._values["local_router_ip"] = local_router_ip
        if peer_router_asn is not None:
            self._values["peer_router_asn"] = peer_router_asn
        if peer_router_ip is not None:
            self._values["peer_router_ip"] = peer_router_ip

    @builtins.property
    def auth_key(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#auth_key PartnerAttachment#auth_key}.'''
        result = self._values.get("auth_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def local_router_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#local_router_ip PartnerAttachment#local_router_ip}.'''
        result = self._values.get("local_router_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def peer_router_asn(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#peer_router_asn PartnerAttachment#peer_router_asn}.'''
        result = self._values.get("peer_router_asn")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def peer_router_ip(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#peer_router_ip PartnerAttachment#peer_router_ip}.'''
        result = self._values.get("peer_router_ip")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PartnerAttachmentBgp(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PartnerAttachmentBgpOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.partnerAttachment.PartnerAttachmentBgpOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70dc3ce00c96e9281bcd03881b96017f994ae1b8e68ee46d4b7ceba4303693fe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAuthKey")
    def reset_auth_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAuthKey", []))

    @jsii.member(jsii_name="resetLocalRouterIp")
    def reset_local_router_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLocalRouterIp", []))

    @jsii.member(jsii_name="resetPeerRouterAsn")
    def reset_peer_router_asn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeerRouterAsn", []))

    @jsii.member(jsii_name="resetPeerRouterIp")
    def reset_peer_router_ip(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPeerRouterIp", []))

    @builtins.property
    @jsii.member(jsii_name="authKeyInput")
    def auth_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "authKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="localRouterIpInput")
    def local_router_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "localRouterIpInput"))

    @builtins.property
    @jsii.member(jsii_name="peerRouterAsnInput")
    def peer_router_asn_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "peerRouterAsnInput"))

    @builtins.property
    @jsii.member(jsii_name="peerRouterIpInput")
    def peer_router_ip_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "peerRouterIpInput"))

    @builtins.property
    @jsii.member(jsii_name="authKey")
    def auth_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "authKey"))

    @auth_key.setter
    def auth_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ccd26d0391d3d987cdfcfa07e13f92a1b0c3108425a38dc5e75ea792a3e3d1d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "authKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="localRouterIp")
    def local_router_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "localRouterIp"))

    @local_router_ip.setter
    def local_router_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b0724c9a59f2ec1551def439f3910efb029c906cf8e653f4c5fd3b5dff4023e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "localRouterIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerRouterAsn")
    def peer_router_asn(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "peerRouterAsn"))

    @peer_router_asn.setter
    def peer_router_asn(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70512f9a22020ac2367cef8c4d2a11377e7b30234b113b639439bbe6f80d03d5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerRouterAsn", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="peerRouterIp")
    def peer_router_ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "peerRouterIp"))

    @peer_router_ip.setter
    def peer_router_ip(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e051742ea93d3e87b1bb09d05fc22ce5c54fa0dc72fdb7aad1e85b9a4ad348e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "peerRouterIp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[PartnerAttachmentBgp]:
        return typing.cast(typing.Optional[PartnerAttachmentBgp], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[PartnerAttachmentBgp]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67c44c731b17e70105e3ab143a35ebcb3ed3dd4272e0a52608305d018fc96ec0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.partnerAttachment.PartnerAttachmentConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "connection_bandwidth_in_mbps": "connectionBandwidthInMbps",
        "naas_provider": "naasProvider",
        "name": "name",
        "region": "region",
        "vpc_ids": "vpcIds",
        "bgp": "bgp",
        "parent_uuid": "parentUuid",
        "redundancy_zone": "redundancyZone",
        "timeouts": "timeouts",
    },
)
class PartnerAttachmentConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        connection_bandwidth_in_mbps: jsii.Number,
        naas_provider: builtins.str,
        name: builtins.str,
        region: builtins.str,
        vpc_ids: typing.Sequence[builtins.str],
        bgp: typing.Optional[typing.Union[PartnerAttachmentBgp, typing.Dict[builtins.str, typing.Any]]] = None,
        parent_uuid: typing.Optional[builtins.str] = None,
        redundancy_zone: typing.Optional[builtins.str] = None,
        timeouts: typing.Optional[typing.Union["PartnerAttachmentTimeouts", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param connection_bandwidth_in_mbps: The connection bandwidth in Mbps. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#connection_bandwidth_in_mbps PartnerAttachment#connection_bandwidth_in_mbps}
        :param naas_provider: The NaaS provider. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#naas_provider PartnerAttachment#naas_provider}
        :param name: The name of the Partner Attachment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#name PartnerAttachment#name}
        :param region: The region where the Partner Attachment will be created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#region PartnerAttachment#region}
        :param vpc_ids: The list of VPC IDs to attach the Partner Attachment to. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#vpc_ids PartnerAttachment#vpc_ids}
        :param bgp: bgp block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#bgp PartnerAttachment#bgp}
        :param parent_uuid: The UUID of the Parent Partner Attachment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#parent_uuid PartnerAttachment#parent_uuid}
        :param redundancy_zone: The redundancy zone for the NaaS. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#redundancy_zone PartnerAttachment#redundancy_zone}
        :param timeouts: timeouts block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#timeouts PartnerAttachment#timeouts}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(bgp, dict):
            bgp = PartnerAttachmentBgp(**bgp)
        if isinstance(timeouts, dict):
            timeouts = PartnerAttachmentTimeouts(**timeouts)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__47e1663a84b3c3a6028c54114e760f46bf510eba055b728d7e189937b3359134)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument connection_bandwidth_in_mbps", value=connection_bandwidth_in_mbps, expected_type=type_hints["connection_bandwidth_in_mbps"])
            check_type(argname="argument naas_provider", value=naas_provider, expected_type=type_hints["naas_provider"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument vpc_ids", value=vpc_ids, expected_type=type_hints["vpc_ids"])
            check_type(argname="argument bgp", value=bgp, expected_type=type_hints["bgp"])
            check_type(argname="argument parent_uuid", value=parent_uuid, expected_type=type_hints["parent_uuid"])
            check_type(argname="argument redundancy_zone", value=redundancy_zone, expected_type=type_hints["redundancy_zone"])
            check_type(argname="argument timeouts", value=timeouts, expected_type=type_hints["timeouts"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "connection_bandwidth_in_mbps": connection_bandwidth_in_mbps,
            "naas_provider": naas_provider,
            "name": name,
            "region": region,
            "vpc_ids": vpc_ids,
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
        if bgp is not None:
            self._values["bgp"] = bgp
        if parent_uuid is not None:
            self._values["parent_uuid"] = parent_uuid
        if redundancy_zone is not None:
            self._values["redundancy_zone"] = redundancy_zone
        if timeouts is not None:
            self._values["timeouts"] = timeouts

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
    def connection_bandwidth_in_mbps(self) -> jsii.Number:
        '''The connection bandwidth in Mbps.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#connection_bandwidth_in_mbps PartnerAttachment#connection_bandwidth_in_mbps}
        '''
        result = self._values.get("connection_bandwidth_in_mbps")
        assert result is not None, "Required property 'connection_bandwidth_in_mbps' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def naas_provider(self) -> builtins.str:
        '''The NaaS provider.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#naas_provider PartnerAttachment#naas_provider}
        '''
        result = self._values.get("naas_provider")
        assert result is not None, "Required property 'naas_provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the Partner Attachment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#name PartnerAttachment#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''The region where the Partner Attachment will be created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#region PartnerAttachment#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def vpc_ids(self) -> typing.List[builtins.str]:
        '''The list of VPC IDs to attach the Partner Attachment to.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#vpc_ids PartnerAttachment#vpc_ids}
        '''
        result = self._values.get("vpc_ids")
        assert result is not None, "Required property 'vpc_ids' is missing"
        return typing.cast(typing.List[builtins.str], result)

    @builtins.property
    def bgp(self) -> typing.Optional[PartnerAttachmentBgp]:
        '''bgp block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#bgp PartnerAttachment#bgp}
        '''
        result = self._values.get("bgp")
        return typing.cast(typing.Optional[PartnerAttachmentBgp], result)

    @builtins.property
    def parent_uuid(self) -> typing.Optional[builtins.str]:
        '''The UUID of the Parent Partner Attachment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#parent_uuid PartnerAttachment#parent_uuid}
        '''
        result = self._values.get("parent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redundancy_zone(self) -> typing.Optional[builtins.str]:
        '''The redundancy zone for the NaaS.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#redundancy_zone PartnerAttachment#redundancy_zone}
        '''
        result = self._values.get("redundancy_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def timeouts(self) -> typing.Optional["PartnerAttachmentTimeouts"]:
        '''timeouts block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#timeouts PartnerAttachment#timeouts}
        '''
        result = self._values.get("timeouts")
        return typing.cast(typing.Optional["PartnerAttachmentTimeouts"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PartnerAttachmentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.partnerAttachment.PartnerAttachmentTimeouts",
    jsii_struct_bases=[],
    name_mapping={"create": "create", "delete": "delete"},
)
class PartnerAttachmentTimeouts:
    def __init__(
        self,
        *,
        create: typing.Optional[builtins.str] = None,
        delete: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param create: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#create PartnerAttachment#create}.
        :param delete: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#delete PartnerAttachment#delete}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4690aa394a70c948412b3ccc7233c1a993d865a12ecbdf230315cc4c2b90cc8b)
            check_type(argname="argument create", value=create, expected_type=type_hints["create"])
            check_type(argname="argument delete", value=delete, expected_type=type_hints["delete"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if create is not None:
            self._values["create"] = create
        if delete is not None:
            self._values["delete"] = delete

    @builtins.property
    def create(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#create PartnerAttachment#create}.'''
        result = self._values.get("create")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def delete(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/partner_attachment#delete PartnerAttachment#delete}.'''
        result = self._values.get("delete")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "PartnerAttachmentTimeouts(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class PartnerAttachmentTimeoutsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.partnerAttachment.PartnerAttachmentTimeoutsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe87fa7c33120970d3abea8cece302d94669b6557d1f565b42315b5a70a92b8d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCreate")
    def reset_create(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreate", []))

    @jsii.member(jsii_name="resetDelete")
    def reset_delete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDelete", []))

    @builtins.property
    @jsii.member(jsii_name="createInput")
    def create_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createInput"))

    @builtins.property
    @jsii.member(jsii_name="deleteInput")
    def delete_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "deleteInput"))

    @builtins.property
    @jsii.member(jsii_name="create")
    def create(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "create"))

    @create.setter
    def create(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc575751825e31c9448b350a32cfd288d263dbe5c2e84e12155c725d2ab39472)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "create", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="delete")
    def delete(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "delete"))

    @delete.setter
    def delete(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1afc769009de441b4cfc7d891c25c06316e7b19b0c16e3a8846c585ab959c4cb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "delete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PartnerAttachmentTimeouts]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PartnerAttachmentTimeouts]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PartnerAttachmentTimeouts]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2de160513950fd788ad328fafab60497062d99b33a62eb85fc5e289eb15138cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "PartnerAttachment",
    "PartnerAttachmentBgp",
    "PartnerAttachmentBgpOutputReference",
    "PartnerAttachmentConfig",
    "PartnerAttachmentTimeouts",
    "PartnerAttachmentTimeoutsOutputReference",
]

publication.publish()

def _typecheckingstub__a440716fc49276a705f71fd6e17defd5fb40d26a16ddd7aa7f24ec6b7826ee74(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    connection_bandwidth_in_mbps: jsii.Number,
    naas_provider: builtins.str,
    name: builtins.str,
    region: builtins.str,
    vpc_ids: typing.Sequence[builtins.str],
    bgp: typing.Optional[typing.Union[PartnerAttachmentBgp, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_uuid: typing.Optional[builtins.str] = None,
    redundancy_zone: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[PartnerAttachmentTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__156c740c23b1d5b743a59dcfc1593972244d910910b8084b8f356e98871254ea(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__504717f35d79a49b82a946eff43de366865afa2f28e1408e15dfbb8d56d423f9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8160ceaccba028c67e4442a12293a23501827f09a5cafd02bdfe23996a61765(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c8bb1bb9c2d3bf753b6233ac435fd653faca443b0c936447410b4de4207be5a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0dced98dfcfccc0f0a34f1e2fc3797f3668da6b133f6219911fa654b2df38d10(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__053e0169ee77c1cc6eff3f51b726444917568cc67da5836355444f661c760ae4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc6d7d26ef6d3b95cef90efd81959ce0b3306fc36e97f3b4ca863a009b5666ff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d98dc3a39a8caba4efae7aca9b029663b24156e044b2ba9b8ca78883798002b3(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8befe5052a221a529ceb23dc2b08e95dbdc2d46f1fa277dc64c9569e9caf9d3(
    *,
    auth_key: typing.Optional[builtins.str] = None,
    local_router_ip: typing.Optional[builtins.str] = None,
    peer_router_asn: typing.Optional[jsii.Number] = None,
    peer_router_ip: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70dc3ce00c96e9281bcd03881b96017f994ae1b8e68ee46d4b7ceba4303693fe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ccd26d0391d3d987cdfcfa07e13f92a1b0c3108425a38dc5e75ea792a3e3d1d7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b0724c9a59f2ec1551def439f3910efb029c906cf8e653f4c5fd3b5dff4023e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70512f9a22020ac2367cef8c4d2a11377e7b30234b113b639439bbe6f80d03d5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e051742ea93d3e87b1bb09d05fc22ce5c54fa0dc72fdb7aad1e85b9a4ad348e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67c44c731b17e70105e3ab143a35ebcb3ed3dd4272e0a52608305d018fc96ec0(
    value: typing.Optional[PartnerAttachmentBgp],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47e1663a84b3c3a6028c54114e760f46bf510eba055b728d7e189937b3359134(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    connection_bandwidth_in_mbps: jsii.Number,
    naas_provider: builtins.str,
    name: builtins.str,
    region: builtins.str,
    vpc_ids: typing.Sequence[builtins.str],
    bgp: typing.Optional[typing.Union[PartnerAttachmentBgp, typing.Dict[builtins.str, typing.Any]]] = None,
    parent_uuid: typing.Optional[builtins.str] = None,
    redundancy_zone: typing.Optional[builtins.str] = None,
    timeouts: typing.Optional[typing.Union[PartnerAttachmentTimeouts, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4690aa394a70c948412b3ccc7233c1a993d865a12ecbdf230315cc4c2b90cc8b(
    *,
    create: typing.Optional[builtins.str] = None,
    delete: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe87fa7c33120970d3abea8cece302d94669b6557d1f565b42315b5a70a92b8d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc575751825e31c9448b350a32cfd288d263dbe5c2e84e12155c725d2ab39472(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1afc769009de441b4cfc7d891c25c06316e7b19b0c16e3a8846c585ab959c4cb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2de160513950fd788ad328fafab60497062d99b33a62eb85fc5e289eb15138cd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, PartnerAttachmentTimeouts]],
) -> None:
    """Type checking stubs"""
    pass
