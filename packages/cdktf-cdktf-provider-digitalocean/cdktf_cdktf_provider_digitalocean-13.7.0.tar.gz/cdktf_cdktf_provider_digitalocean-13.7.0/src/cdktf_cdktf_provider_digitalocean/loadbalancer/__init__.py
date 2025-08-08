r'''
# `digitalocean_loadbalancer`

Refer to the Terraform Registry for docs: [`digitalocean_loadbalancer`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer).
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


class Loadbalancer(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.Loadbalancer",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer digitalocean_loadbalancer}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        name: builtins.str,
        algorithm: typing.Optional[builtins.str] = None,
        disable_lets_encrypt_dns_records: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        domains: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerDomains", typing.Dict[builtins.str, typing.Any]]]]] = None,
        droplet_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        droplet_tag: typing.Optional[builtins.str] = None,
        enable_backend_keepalive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_proxy_protocol: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firewall: typing.Optional[typing.Union["LoadbalancerFirewall", typing.Dict[builtins.str, typing.Any]]] = None,
        forwarding_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerForwardingRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
        glb_settings: typing.Optional[typing.Union["LoadbalancerGlbSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        healthcheck: typing.Optional[typing.Union["LoadbalancerHealthcheck", typing.Dict[builtins.str, typing.Any]]] = None,
        http_idle_timeout_seconds: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        network: typing.Optional[builtins.str] = None,
        network_stack: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        redirect_http_to_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        size: typing.Optional[builtins.str] = None,
        size_unit: typing.Optional[jsii.Number] = None,
        sticky_sessions: typing.Optional[typing.Union["LoadbalancerStickySessions", typing.Dict[builtins.str, typing.Any]]] = None,
        target_load_balancer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_cipher_policy: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        vpc_uuid: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer digitalocean_loadbalancer} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#name Loadbalancer#name}.
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#algorithm Loadbalancer#algorithm}.
        :param disable_lets_encrypt_dns_records: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#disable_lets_encrypt_dns_records Loadbalancer#disable_lets_encrypt_dns_records}.
        :param domains: domains block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#domains Loadbalancer#domains}
        :param droplet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#droplet_ids Loadbalancer#droplet_ids}.
        :param droplet_tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#droplet_tag Loadbalancer#droplet_tag}.
        :param enable_backend_keepalive: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#enable_backend_keepalive Loadbalancer#enable_backend_keepalive}.
        :param enable_proxy_protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#enable_proxy_protocol Loadbalancer#enable_proxy_protocol}.
        :param firewall: firewall block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#firewall Loadbalancer#firewall}
        :param forwarding_rule: forwarding_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#forwarding_rule Loadbalancer#forwarding_rule}
        :param glb_settings: glb_settings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#glb_settings Loadbalancer#glb_settings}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#healthcheck Loadbalancer#healthcheck}
        :param http_idle_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#http_idle_timeout_seconds Loadbalancer#http_idle_timeout_seconds}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#id Loadbalancer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network: the type of network the load balancer is accessible from (EXTERNAL or INTERNAL). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#network Loadbalancer#network}
        :param network_stack: The network stack determines the allocation of ipv4/ipv6 addresses to the load balancer. Enum: 'IPV4' 'DUALSTACK'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#network_stack Loadbalancer#network_stack}
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#project_id Loadbalancer#project_id}.
        :param redirect_http_to_https: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#redirect_http_to_https Loadbalancer#redirect_http_to_https}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#region Loadbalancer#region}.
        :param size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#size Loadbalancer#size}.
        :param size_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#size_unit Loadbalancer#size_unit}.
        :param sticky_sessions: sticky_sessions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#sticky_sessions Loadbalancer#sticky_sessions}
        :param target_load_balancer_ids: list of load balancer IDs to put behind a global load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_load_balancer_ids Loadbalancer#target_load_balancer_ids}
        :param tls_cipher_policy: The tls cipher policy to be used for the load balancer. Enum: 'DEFAULT' 'STRONG'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#tls_cipher_policy Loadbalancer#tls_cipher_policy}
        :param type: the type of the load balancer (GLOBAL, REGIONAL, or REGIONAL_NETWORK). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#type Loadbalancer#type}
        :param vpc_uuid: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#vpc_uuid Loadbalancer#vpc_uuid}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0a68ad9900cb6a64cd2e94d623a87378011a58fa274b5c8593ce89ca399087b0)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = LoadbalancerConfig(
            name=name,
            algorithm=algorithm,
            disable_lets_encrypt_dns_records=disable_lets_encrypt_dns_records,
            domains=domains,
            droplet_ids=droplet_ids,
            droplet_tag=droplet_tag,
            enable_backend_keepalive=enable_backend_keepalive,
            enable_proxy_protocol=enable_proxy_protocol,
            firewall=firewall,
            forwarding_rule=forwarding_rule,
            glb_settings=glb_settings,
            healthcheck=healthcheck,
            http_idle_timeout_seconds=http_idle_timeout_seconds,
            id=id,
            network=network,
            network_stack=network_stack,
            project_id=project_id,
            redirect_http_to_https=redirect_http_to_https,
            region=region,
            size=size,
            size_unit=size_unit,
            sticky_sessions=sticky_sessions,
            target_load_balancer_ids=target_load_balancer_ids,
            tls_cipher_policy=tls_cipher_policy,
            type=type,
            vpc_uuid=vpc_uuid,
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
        '''Generates CDKTF code for importing a Loadbalancer resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the Loadbalancer to import.
        :param import_from_id: The id of the existing Loadbalancer that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the Loadbalancer to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18103c127e676f5674e65deb9eb0619505ca972d422311babfeeb398ee66251b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDomains")
    def put_domains(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerDomains", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7f584a2a08db381ebe93a697b28f6c9b3766d081d60780426bb7d2fe978c7fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDomains", [value]))

    @jsii.member(jsii_name="putFirewall")
    def put_firewall(
        self,
        *,
        allow: typing.Optional[typing.Sequence[builtins.str]] = None,
        deny: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allow: the rules for ALLOWING traffic to the LB (strings in the form: 'ip:1.2.3.4' or 'cidr:1.2.0.0/16'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#allow Loadbalancer#allow}
        :param deny: the rules for DENYING traffic to the LB (strings in the form: 'ip:1.2.3.4' or 'cidr:1.2.0.0/16'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#deny Loadbalancer#deny}
        '''
        value = LoadbalancerFirewall(allow=allow, deny=deny)

        return typing.cast(None, jsii.invoke(self, "putFirewall", [value]))

    @jsii.member(jsii_name="putForwardingRule")
    def put_forwarding_rule(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerForwardingRule", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2f95e18a934d365f327f2e279a0a684fede396bcab3da08953fbb9624dde27c8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putForwardingRule", [value]))

    @jsii.member(jsii_name="putGlbSettings")
    def put_glb_settings(
        self,
        *,
        target_port: jsii.Number,
        target_protocol: builtins.str,
        cdn: typing.Optional[typing.Union["LoadbalancerGlbSettingsCdn", typing.Dict[builtins.str, typing.Any]]] = None,
        failover_threshold: typing.Optional[jsii.Number] = None,
        region_priorities: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
    ) -> None:
        '''
        :param target_port: target port rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_port Loadbalancer#target_port}
        :param target_protocol: target protocol rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_protocol Loadbalancer#target_protocol}
        :param cdn: cdn block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cdn Loadbalancer#cdn}
        :param failover_threshold: fail-over threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#failover_threshold Loadbalancer#failover_threshold}
        :param region_priorities: region priority map. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#region_priorities Loadbalancer#region_priorities}
        '''
        value = LoadbalancerGlbSettings(
            target_port=target_port,
            target_protocol=target_protocol,
            cdn=cdn,
            failover_threshold=failover_threshold,
            region_priorities=region_priorities,
        )

        return typing.cast(None, jsii.invoke(self, "putGlbSettings", [value]))

    @jsii.member(jsii_name="putHealthcheck")
    def put_healthcheck(
        self,
        *,
        port: jsii.Number,
        protocol: builtins.str,
        check_interval_seconds: typing.Optional[jsii.Number] = None,
        healthy_threshold: typing.Optional[jsii.Number] = None,
        path: typing.Optional[builtins.str] = None,
        response_timeout_seconds: typing.Optional[jsii.Number] = None,
        unhealthy_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#port Loadbalancer#port}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#protocol Loadbalancer#protocol}.
        :param check_interval_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#check_interval_seconds Loadbalancer#check_interval_seconds}.
        :param healthy_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#healthy_threshold Loadbalancer#healthy_threshold}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#path Loadbalancer#path}.
        :param response_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#response_timeout_seconds Loadbalancer#response_timeout_seconds}.
        :param unhealthy_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#unhealthy_threshold Loadbalancer#unhealthy_threshold}.
        '''
        value = LoadbalancerHealthcheck(
            port=port,
            protocol=protocol,
            check_interval_seconds=check_interval_seconds,
            healthy_threshold=healthy_threshold,
            path=path,
            response_timeout_seconds=response_timeout_seconds,
            unhealthy_threshold=unhealthy_threshold,
        )

        return typing.cast(None, jsii.invoke(self, "putHealthcheck", [value]))

    @jsii.member(jsii_name="putStickySessions")
    def put_sticky_sessions(
        self,
        *,
        cookie_name: typing.Optional[builtins.str] = None,
        cookie_ttl_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cookie_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cookie_name Loadbalancer#cookie_name}.
        :param cookie_ttl_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cookie_ttl_seconds Loadbalancer#cookie_ttl_seconds}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#type Loadbalancer#type}.
        '''
        value = LoadbalancerStickySessions(
            cookie_name=cookie_name, cookie_ttl_seconds=cookie_ttl_seconds, type=type
        )

        return typing.cast(None, jsii.invoke(self, "putStickySessions", [value]))

    @jsii.member(jsii_name="resetAlgorithm")
    def reset_algorithm(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlgorithm", []))

    @jsii.member(jsii_name="resetDisableLetsEncryptDnsRecords")
    def reset_disable_lets_encrypt_dns_records(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableLetsEncryptDnsRecords", []))

    @jsii.member(jsii_name="resetDomains")
    def reset_domains(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDomains", []))

    @jsii.member(jsii_name="resetDropletIds")
    def reset_droplet_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDropletIds", []))

    @jsii.member(jsii_name="resetDropletTag")
    def reset_droplet_tag(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDropletTag", []))

    @jsii.member(jsii_name="resetEnableBackendKeepalive")
    def reset_enable_backend_keepalive(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableBackendKeepalive", []))

    @jsii.member(jsii_name="resetEnableProxyProtocol")
    def reset_enable_proxy_protocol(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEnableProxyProtocol", []))

    @jsii.member(jsii_name="resetFirewall")
    def reset_firewall(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFirewall", []))

    @jsii.member(jsii_name="resetForwardingRule")
    def reset_forwarding_rule(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetForwardingRule", []))

    @jsii.member(jsii_name="resetGlbSettings")
    def reset_glb_settings(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGlbSettings", []))

    @jsii.member(jsii_name="resetHealthcheck")
    def reset_healthcheck(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthcheck", []))

    @jsii.member(jsii_name="resetHttpIdleTimeoutSeconds")
    def reset_http_idle_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpIdleTimeoutSeconds", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetNetwork")
    def reset_network(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetwork", []))

    @jsii.member(jsii_name="resetNetworkStack")
    def reset_network_stack(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetworkStack", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetRedirectHttpToHttps")
    def reset_redirect_http_to_https(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRedirectHttpToHttps", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetSize")
    def reset_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSize", []))

    @jsii.member(jsii_name="resetSizeUnit")
    def reset_size_unit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSizeUnit", []))

    @jsii.member(jsii_name="resetStickySessions")
    def reset_sticky_sessions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStickySessions", []))

    @jsii.member(jsii_name="resetTargetLoadBalancerIds")
    def reset_target_load_balancer_ids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTargetLoadBalancerIds", []))

    @jsii.member(jsii_name="resetTlsCipherPolicy")
    def reset_tls_cipher_policy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsCipherPolicy", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetVpcUuid")
    def reset_vpc_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVpcUuid", []))

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
    @jsii.member(jsii_name="domains")
    def domains(self) -> "LoadbalancerDomainsList":
        return typing.cast("LoadbalancerDomainsList", jsii.get(self, "domains"))

    @builtins.property
    @jsii.member(jsii_name="firewall")
    def firewall(self) -> "LoadbalancerFirewallOutputReference":
        return typing.cast("LoadbalancerFirewallOutputReference", jsii.get(self, "firewall"))

    @builtins.property
    @jsii.member(jsii_name="forwardingRule")
    def forwarding_rule(self) -> "LoadbalancerForwardingRuleList":
        return typing.cast("LoadbalancerForwardingRuleList", jsii.get(self, "forwardingRule"))

    @builtins.property
    @jsii.member(jsii_name="glbSettings")
    def glb_settings(self) -> "LoadbalancerGlbSettingsOutputReference":
        return typing.cast("LoadbalancerGlbSettingsOutputReference", jsii.get(self, "glbSettings"))

    @builtins.property
    @jsii.member(jsii_name="healthcheck")
    def healthcheck(self) -> "LoadbalancerHealthcheckOutputReference":
        return typing.cast("LoadbalancerHealthcheckOutputReference", jsii.get(self, "healthcheck"))

    @builtins.property
    @jsii.member(jsii_name="ip")
    def ip(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ip"))

    @builtins.property
    @jsii.member(jsii_name="ipv6")
    def ipv6(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ipv6"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="stickySessions")
    def sticky_sessions(self) -> "LoadbalancerStickySessionsOutputReference":
        return typing.cast("LoadbalancerStickySessionsOutputReference", jsii.get(self, "stickySessions"))

    @builtins.property
    @jsii.member(jsii_name="urn")
    def urn(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "urn"))

    @builtins.property
    @jsii.member(jsii_name="algorithmInput")
    def algorithm_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "algorithmInput"))

    @builtins.property
    @jsii.member(jsii_name="disableLetsEncryptDnsRecordsInput")
    def disable_lets_encrypt_dns_records_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "disableLetsEncryptDnsRecordsInput"))

    @builtins.property
    @jsii.member(jsii_name="domainsInput")
    def domains_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerDomains"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerDomains"]]], jsii.get(self, "domainsInput"))

    @builtins.property
    @jsii.member(jsii_name="dropletIdsInput")
    def droplet_ids_input(self) -> typing.Optional[typing.List[jsii.Number]]:
        return typing.cast(typing.Optional[typing.List[jsii.Number]], jsii.get(self, "dropletIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="dropletTagInput")
    def droplet_tag_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "dropletTagInput"))

    @builtins.property
    @jsii.member(jsii_name="enableBackendKeepaliveInput")
    def enable_backend_keepalive_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableBackendKeepaliveInput"))

    @builtins.property
    @jsii.member(jsii_name="enableProxyProtocolInput")
    def enable_proxy_protocol_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "enableProxyProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="firewallInput")
    def firewall_input(self) -> typing.Optional["LoadbalancerFirewall"]:
        return typing.cast(typing.Optional["LoadbalancerFirewall"], jsii.get(self, "firewallInput"))

    @builtins.property
    @jsii.member(jsii_name="forwardingRuleInput")
    def forwarding_rule_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerForwardingRule"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerForwardingRule"]]], jsii.get(self, "forwardingRuleInput"))

    @builtins.property
    @jsii.member(jsii_name="glbSettingsInput")
    def glb_settings_input(self) -> typing.Optional["LoadbalancerGlbSettings"]:
        return typing.cast(typing.Optional["LoadbalancerGlbSettings"], jsii.get(self, "glbSettingsInput"))

    @builtins.property
    @jsii.member(jsii_name="healthcheckInput")
    def healthcheck_input(self) -> typing.Optional["LoadbalancerHealthcheck"]:
        return typing.cast(typing.Optional["LoadbalancerHealthcheck"], jsii.get(self, "healthcheckInput"))

    @builtins.property
    @jsii.member(jsii_name="httpIdleTimeoutSecondsInput")
    def http_idle_timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpIdleTimeoutSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="networkInput")
    def network_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkInput"))

    @builtins.property
    @jsii.member(jsii_name="networkStackInput")
    def network_stack_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "networkStackInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="redirectHttpToHttpsInput")
    def redirect_http_to_https_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "redirectHttpToHttpsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInput")
    def size_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeUnitInput")
    def size_unit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sizeUnitInput"))

    @builtins.property
    @jsii.member(jsii_name="stickySessionsInput")
    def sticky_sessions_input(self) -> typing.Optional["LoadbalancerStickySessions"]:
        return typing.cast(typing.Optional["LoadbalancerStickySessions"], jsii.get(self, "stickySessionsInput"))

    @builtins.property
    @jsii.member(jsii_name="targetLoadBalancerIdsInput")
    def target_load_balancer_ids_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "targetLoadBalancerIdsInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsCipherPolicyInput")
    def tls_cipher_policy_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tlsCipherPolicyInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcUuidInput")
    def vpc_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="algorithm")
    def algorithm(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "algorithm"))

    @algorithm.setter
    def algorithm(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9966ccc372df39fcfc3face8dcd57899adaf44a754f8a5c94f2498112d9620af)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "algorithm", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="disableLetsEncryptDnsRecords")
    def disable_lets_encrypt_dns_records(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "disableLetsEncryptDnsRecords"))

    @disable_lets_encrypt_dns_records.setter
    def disable_lets_encrypt_dns_records(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c40def00f24dd55ac74c0523644dad47fb76de56c2d9d3cef0924311df6287c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableLetsEncryptDnsRecords", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dropletIds")
    def droplet_ids(self) -> typing.List[jsii.Number]:
        return typing.cast(typing.List[jsii.Number], jsii.get(self, "dropletIds"))

    @droplet_ids.setter
    def droplet_ids(self, value: typing.List[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f813339c027b0c781281d93e846384d9381af5fe398a176f0e8b00833fafa0c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dropletIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dropletTag")
    def droplet_tag(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "dropletTag"))

    @droplet_tag.setter
    def droplet_tag(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32e535d9b48b5c9c30176ab1ae74399665f9846dce9d13e1966b6a57d3e4fd00)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dropletTag", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableBackendKeepalive")
    def enable_backend_keepalive(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableBackendKeepalive"))

    @enable_backend_keepalive.setter
    def enable_backend_keepalive(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d66dff725f9491e54fbc78147d0a5c5a77f578a549f4f1c283d962f0ec4d71bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableBackendKeepalive", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="enableProxyProtocol")
    def enable_proxy_protocol(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "enableProxyProtocol"))

    @enable_proxy_protocol.setter
    def enable_proxy_protocol(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcd1a4312c984e1590eb072721005cc696abfc7fb3030ce131f10a1ce90622d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "enableProxyProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpIdleTimeoutSeconds")
    def http_idle_timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "httpIdleTimeoutSeconds"))

    @http_idle_timeout_seconds.setter
    def http_idle_timeout_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db331010016ff26ee2e5f504a3df3c2543d3948ead0b32d4d0d1b4b42b3dc81f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpIdleTimeoutSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__54bf8035d8b367590c8b7f7211290cdebe90bb110e7bd5b6225721c8b5af5635)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f52b85e859155069dce00d76a5cffc62e57c2db5a977027c4d4ff6956fe409f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="network")
    def network(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "network"))

    @network.setter
    def network(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e3055178433889f8af99847bb2aa59cf23fc4dacfd801da322060b6815ada67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "network", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="networkStack")
    def network_stack(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "networkStack"))

    @network_stack.setter
    def network_stack(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2fbb837ce1978fa4c9dc966c0dc18c74aef3335517aba0abdb38ab113adbacee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "networkStack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ada167cd1c45f058a88d6148bbf0680f22e5f9b018156d55cb3c57fc2438193)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="redirectHttpToHttps")
    def redirect_http_to_https(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "redirectHttpToHttps"))

    @redirect_http_to_https.setter
    def redirect_http_to_https(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e61138417f7c2534d2568818a4aa56daf20723a8d93ba46553b14e3bb2631b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "redirectHttpToHttps", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e348e7aaf03337b1ec7e56ade38780f7e19e3fb0a3a27c4c76c5336d23a5ba3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="size")
    def size(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "size"))

    @size.setter
    def size(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7836df086f3efcb1a0fa6b26a91722ea517995ed983295cd3b180f85cf85ecb2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "size", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeUnit")
    def size_unit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sizeUnit"))

    @size_unit.setter
    def size_unit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__968e87d7d9b676761740b32d6acde0cdc0581046fa7195d3120c57b7dac6087f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeUnit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetLoadBalancerIds")
    def target_load_balancer_ids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "targetLoadBalancerIds"))

    @target_load_balancer_ids.setter
    def target_load_balancer_ids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d7f7e5c6dd1233afe0373a36181a5fe77c2b15f978e5dd161d8dfd6d665d498)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetLoadBalancerIds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsCipherPolicy")
    def tls_cipher_policy(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "tlsCipherPolicy"))

    @tls_cipher_policy.setter
    def tls_cipher_policy(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eff227d581cc298fb43c6a18711732cf0146facc6e7261c20b9b7f6231b73771)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsCipherPolicy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20522b12d3d98e5c328437536beb68e7d072c57b57e468a82d0f295c63eb09fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcUuid")
    def vpc_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcUuid"))

    @vpc_uuid.setter
    def vpc_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__024a2d70d338b88fcc6856488903be5ee07a728324ab3a88597af939bfabb8ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcUuid", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "name": "name",
        "algorithm": "algorithm",
        "disable_lets_encrypt_dns_records": "disableLetsEncryptDnsRecords",
        "domains": "domains",
        "droplet_ids": "dropletIds",
        "droplet_tag": "dropletTag",
        "enable_backend_keepalive": "enableBackendKeepalive",
        "enable_proxy_protocol": "enableProxyProtocol",
        "firewall": "firewall",
        "forwarding_rule": "forwardingRule",
        "glb_settings": "glbSettings",
        "healthcheck": "healthcheck",
        "http_idle_timeout_seconds": "httpIdleTimeoutSeconds",
        "id": "id",
        "network": "network",
        "network_stack": "networkStack",
        "project_id": "projectId",
        "redirect_http_to_https": "redirectHttpToHttps",
        "region": "region",
        "size": "size",
        "size_unit": "sizeUnit",
        "sticky_sessions": "stickySessions",
        "target_load_balancer_ids": "targetLoadBalancerIds",
        "tls_cipher_policy": "tlsCipherPolicy",
        "type": "type",
        "vpc_uuid": "vpcUuid",
    },
)
class LoadbalancerConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        name: builtins.str,
        algorithm: typing.Optional[builtins.str] = None,
        disable_lets_encrypt_dns_records: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        domains: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerDomains", typing.Dict[builtins.str, typing.Any]]]]] = None,
        droplet_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
        droplet_tag: typing.Optional[builtins.str] = None,
        enable_backend_keepalive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        enable_proxy_protocol: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        firewall: typing.Optional[typing.Union["LoadbalancerFirewall", typing.Dict[builtins.str, typing.Any]]] = None,
        forwarding_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["LoadbalancerForwardingRule", typing.Dict[builtins.str, typing.Any]]]]] = None,
        glb_settings: typing.Optional[typing.Union["LoadbalancerGlbSettings", typing.Dict[builtins.str, typing.Any]]] = None,
        healthcheck: typing.Optional[typing.Union["LoadbalancerHealthcheck", typing.Dict[builtins.str, typing.Any]]] = None,
        http_idle_timeout_seconds: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        network: typing.Optional[builtins.str] = None,
        network_stack: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        redirect_http_to_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        region: typing.Optional[builtins.str] = None,
        size: typing.Optional[builtins.str] = None,
        size_unit: typing.Optional[jsii.Number] = None,
        sticky_sessions: typing.Optional[typing.Union["LoadbalancerStickySessions", typing.Dict[builtins.str, typing.Any]]] = None,
        target_load_balancer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_cipher_policy: typing.Optional[builtins.str] = None,
        type: typing.Optional[builtins.str] = None,
        vpc_uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#name Loadbalancer#name}.
        :param algorithm: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#algorithm Loadbalancer#algorithm}.
        :param disable_lets_encrypt_dns_records: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#disable_lets_encrypt_dns_records Loadbalancer#disable_lets_encrypt_dns_records}.
        :param domains: domains block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#domains Loadbalancer#domains}
        :param droplet_ids: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#droplet_ids Loadbalancer#droplet_ids}.
        :param droplet_tag: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#droplet_tag Loadbalancer#droplet_tag}.
        :param enable_backend_keepalive: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#enable_backend_keepalive Loadbalancer#enable_backend_keepalive}.
        :param enable_proxy_protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#enable_proxy_protocol Loadbalancer#enable_proxy_protocol}.
        :param firewall: firewall block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#firewall Loadbalancer#firewall}
        :param forwarding_rule: forwarding_rule block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#forwarding_rule Loadbalancer#forwarding_rule}
        :param glb_settings: glb_settings block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#glb_settings Loadbalancer#glb_settings}
        :param healthcheck: healthcheck block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#healthcheck Loadbalancer#healthcheck}
        :param http_idle_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#http_idle_timeout_seconds Loadbalancer#http_idle_timeout_seconds}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#id Loadbalancer#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param network: the type of network the load balancer is accessible from (EXTERNAL or INTERNAL). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#network Loadbalancer#network}
        :param network_stack: The network stack determines the allocation of ipv4/ipv6 addresses to the load balancer. Enum: 'IPV4' 'DUALSTACK'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#network_stack Loadbalancer#network_stack}
        :param project_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#project_id Loadbalancer#project_id}.
        :param redirect_http_to_https: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#redirect_http_to_https Loadbalancer#redirect_http_to_https}.
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#region Loadbalancer#region}.
        :param size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#size Loadbalancer#size}.
        :param size_unit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#size_unit Loadbalancer#size_unit}.
        :param sticky_sessions: sticky_sessions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#sticky_sessions Loadbalancer#sticky_sessions}
        :param target_load_balancer_ids: list of load balancer IDs to put behind a global load balancer. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_load_balancer_ids Loadbalancer#target_load_balancer_ids}
        :param tls_cipher_policy: The tls cipher policy to be used for the load balancer. Enum: 'DEFAULT' 'STRONG'. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#tls_cipher_policy Loadbalancer#tls_cipher_policy}
        :param type: the type of the load balancer (GLOBAL, REGIONAL, or REGIONAL_NETWORK). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#type Loadbalancer#type}
        :param vpc_uuid: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#vpc_uuid Loadbalancer#vpc_uuid}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(firewall, dict):
            firewall = LoadbalancerFirewall(**firewall)
        if isinstance(glb_settings, dict):
            glb_settings = LoadbalancerGlbSettings(**glb_settings)
        if isinstance(healthcheck, dict):
            healthcheck = LoadbalancerHealthcheck(**healthcheck)
        if isinstance(sticky_sessions, dict):
            sticky_sessions = LoadbalancerStickySessions(**sticky_sessions)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c7d6955a724c1706f8f894cf17bdba6a044a054671acfbca57cae71a67736ac)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument algorithm", value=algorithm, expected_type=type_hints["algorithm"])
            check_type(argname="argument disable_lets_encrypt_dns_records", value=disable_lets_encrypt_dns_records, expected_type=type_hints["disable_lets_encrypt_dns_records"])
            check_type(argname="argument domains", value=domains, expected_type=type_hints["domains"])
            check_type(argname="argument droplet_ids", value=droplet_ids, expected_type=type_hints["droplet_ids"])
            check_type(argname="argument droplet_tag", value=droplet_tag, expected_type=type_hints["droplet_tag"])
            check_type(argname="argument enable_backend_keepalive", value=enable_backend_keepalive, expected_type=type_hints["enable_backend_keepalive"])
            check_type(argname="argument enable_proxy_protocol", value=enable_proxy_protocol, expected_type=type_hints["enable_proxy_protocol"])
            check_type(argname="argument firewall", value=firewall, expected_type=type_hints["firewall"])
            check_type(argname="argument forwarding_rule", value=forwarding_rule, expected_type=type_hints["forwarding_rule"])
            check_type(argname="argument glb_settings", value=glb_settings, expected_type=type_hints["glb_settings"])
            check_type(argname="argument healthcheck", value=healthcheck, expected_type=type_hints["healthcheck"])
            check_type(argname="argument http_idle_timeout_seconds", value=http_idle_timeout_seconds, expected_type=type_hints["http_idle_timeout_seconds"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument network", value=network, expected_type=type_hints["network"])
            check_type(argname="argument network_stack", value=network_stack, expected_type=type_hints["network_stack"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument redirect_http_to_https", value=redirect_http_to_https, expected_type=type_hints["redirect_http_to_https"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument size", value=size, expected_type=type_hints["size"])
            check_type(argname="argument size_unit", value=size_unit, expected_type=type_hints["size_unit"])
            check_type(argname="argument sticky_sessions", value=sticky_sessions, expected_type=type_hints["sticky_sessions"])
            check_type(argname="argument target_load_balancer_ids", value=target_load_balancer_ids, expected_type=type_hints["target_load_balancer_ids"])
            check_type(argname="argument tls_cipher_policy", value=tls_cipher_policy, expected_type=type_hints["tls_cipher_policy"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument vpc_uuid", value=vpc_uuid, expected_type=type_hints["vpc_uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
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
        if algorithm is not None:
            self._values["algorithm"] = algorithm
        if disable_lets_encrypt_dns_records is not None:
            self._values["disable_lets_encrypt_dns_records"] = disable_lets_encrypt_dns_records
        if domains is not None:
            self._values["domains"] = domains
        if droplet_ids is not None:
            self._values["droplet_ids"] = droplet_ids
        if droplet_tag is not None:
            self._values["droplet_tag"] = droplet_tag
        if enable_backend_keepalive is not None:
            self._values["enable_backend_keepalive"] = enable_backend_keepalive
        if enable_proxy_protocol is not None:
            self._values["enable_proxy_protocol"] = enable_proxy_protocol
        if firewall is not None:
            self._values["firewall"] = firewall
        if forwarding_rule is not None:
            self._values["forwarding_rule"] = forwarding_rule
        if glb_settings is not None:
            self._values["glb_settings"] = glb_settings
        if healthcheck is not None:
            self._values["healthcheck"] = healthcheck
        if http_idle_timeout_seconds is not None:
            self._values["http_idle_timeout_seconds"] = http_idle_timeout_seconds
        if id is not None:
            self._values["id"] = id
        if network is not None:
            self._values["network"] = network
        if network_stack is not None:
            self._values["network_stack"] = network_stack
        if project_id is not None:
            self._values["project_id"] = project_id
        if redirect_http_to_https is not None:
            self._values["redirect_http_to_https"] = redirect_http_to_https
        if region is not None:
            self._values["region"] = region
        if size is not None:
            self._values["size"] = size
        if size_unit is not None:
            self._values["size_unit"] = size_unit
        if sticky_sessions is not None:
            self._values["sticky_sessions"] = sticky_sessions
        if target_load_balancer_ids is not None:
            self._values["target_load_balancer_ids"] = target_load_balancer_ids
        if tls_cipher_policy is not None:
            self._values["tls_cipher_policy"] = tls_cipher_policy
        if type is not None:
            self._values["type"] = type
        if vpc_uuid is not None:
            self._values["vpc_uuid"] = vpc_uuid

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
    def name(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#name Loadbalancer#name}.'''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def algorithm(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#algorithm Loadbalancer#algorithm}.'''
        result = self._values.get("algorithm")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_lets_encrypt_dns_records(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#disable_lets_encrypt_dns_records Loadbalancer#disable_lets_encrypt_dns_records}.'''
        result = self._values.get("disable_lets_encrypt_dns_records")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def domains(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerDomains"]]]:
        '''domains block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#domains Loadbalancer#domains}
        '''
        result = self._values.get("domains")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerDomains"]]], result)

    @builtins.property
    def droplet_ids(self) -> typing.Optional[typing.List[jsii.Number]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#droplet_ids Loadbalancer#droplet_ids}.'''
        result = self._values.get("droplet_ids")
        return typing.cast(typing.Optional[typing.List[jsii.Number]], result)

    @builtins.property
    def droplet_tag(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#droplet_tag Loadbalancer#droplet_tag}.'''
        result = self._values.get("droplet_tag")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def enable_backend_keepalive(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#enable_backend_keepalive Loadbalancer#enable_backend_keepalive}.'''
        result = self._values.get("enable_backend_keepalive")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def enable_proxy_protocol(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#enable_proxy_protocol Loadbalancer#enable_proxy_protocol}.'''
        result = self._values.get("enable_proxy_protocol")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def firewall(self) -> typing.Optional["LoadbalancerFirewall"]:
        '''firewall block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#firewall Loadbalancer#firewall}
        '''
        result = self._values.get("firewall")
        return typing.cast(typing.Optional["LoadbalancerFirewall"], result)

    @builtins.property
    def forwarding_rule(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerForwardingRule"]]]:
        '''forwarding_rule block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#forwarding_rule Loadbalancer#forwarding_rule}
        '''
        result = self._values.get("forwarding_rule")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["LoadbalancerForwardingRule"]]], result)

    @builtins.property
    def glb_settings(self) -> typing.Optional["LoadbalancerGlbSettings"]:
        '''glb_settings block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#glb_settings Loadbalancer#glb_settings}
        '''
        result = self._values.get("glb_settings")
        return typing.cast(typing.Optional["LoadbalancerGlbSettings"], result)

    @builtins.property
    def healthcheck(self) -> typing.Optional["LoadbalancerHealthcheck"]:
        '''healthcheck block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#healthcheck Loadbalancer#healthcheck}
        '''
        result = self._values.get("healthcheck")
        return typing.cast(typing.Optional["LoadbalancerHealthcheck"], result)

    @builtins.property
    def http_idle_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#http_idle_timeout_seconds Loadbalancer#http_idle_timeout_seconds}.'''
        result = self._values.get("http_idle_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#id Loadbalancer#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network(self) -> typing.Optional[builtins.str]:
        '''the type of network the load balancer is accessible from (EXTERNAL or INTERNAL).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#network Loadbalancer#network}
        '''
        result = self._values.get("network")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def network_stack(self) -> typing.Optional[builtins.str]:
        '''The network stack determines the allocation of ipv4/ipv6 addresses to the load balancer. Enum: 'IPV4' 'DUALSTACK'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#network_stack Loadbalancer#network_stack}
        '''
        result = self._values.get("network_stack")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#project_id Loadbalancer#project_id}.'''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def redirect_http_to_https(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#redirect_http_to_https Loadbalancer#redirect_http_to_https}.'''
        result = self._values.get("redirect_http_to_https")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#region Loadbalancer#region}.'''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def size(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#size Loadbalancer#size}.'''
        result = self._values.get("size")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def size_unit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#size_unit Loadbalancer#size_unit}.'''
        result = self._values.get("size_unit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sticky_sessions(self) -> typing.Optional["LoadbalancerStickySessions"]:
        '''sticky_sessions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#sticky_sessions Loadbalancer#sticky_sessions}
        '''
        result = self._values.get("sticky_sessions")
        return typing.cast(typing.Optional["LoadbalancerStickySessions"], result)

    @builtins.property
    def target_load_balancer_ids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''list of load balancer IDs to put behind a global load balancer.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_load_balancer_ids Loadbalancer#target_load_balancer_ids}
        '''
        result = self._values.get("target_load_balancer_ids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tls_cipher_policy(self) -> typing.Optional[builtins.str]:
        '''The tls cipher policy to be used for the load balancer. Enum: 'DEFAULT' 'STRONG'.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#tls_cipher_policy Loadbalancer#tls_cipher_policy}
        '''
        result = self._values.get("tls_cipher_policy")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''the type of the load balancer (GLOBAL, REGIONAL, or REGIONAL_NETWORK).

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#type Loadbalancer#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def vpc_uuid(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#vpc_uuid Loadbalancer#vpc_uuid}.'''
        result = self._values.get("vpc_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerDomains",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "certificate_name": "certificateName",
        "is_managed": "isManaged",
    },
)
class LoadbalancerDomains:
    def __init__(
        self,
        *,
        name: builtins.str,
        certificate_name: typing.Optional[builtins.str] = None,
        is_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param name: domain name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#name Loadbalancer#name}
        :param certificate_name: name of certificate required for TLS handshaking. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#certificate_name Loadbalancer#certificate_name}
        :param is_managed: flag indicating if domain is managed by DigitalOcean. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#is_managed Loadbalancer#is_managed}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0abf9f4c7e1038194cc242bb41d43ca5e540ca3641b62e7ccb0d1df09165f6a9)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument certificate_name", value=certificate_name, expected_type=type_hints["certificate_name"])
            check_type(argname="argument is_managed", value=is_managed, expected_type=type_hints["is_managed"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "name": name,
        }
        if certificate_name is not None:
            self._values["certificate_name"] = certificate_name
        if is_managed is not None:
            self._values["is_managed"] = is_managed

    @builtins.property
    def name(self) -> builtins.str:
        '''domain name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#name Loadbalancer#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_name(self) -> typing.Optional[builtins.str]:
        '''name of certificate required for TLS handshaking.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#certificate_name Loadbalancer#certificate_name}
        '''
        result = self._values.get("certificate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_managed(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''flag indicating if domain is managed by DigitalOcean.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#is_managed Loadbalancer#is_managed}
        '''
        result = self._values.get("is_managed")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerDomains(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerDomainsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerDomainsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b279365cf44bab74fa1e66d6fecb14455b27043d22f831cd7bb4937eab5557e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "LoadbalancerDomainsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__774a822f2d5e6494a87c201ed6939d245561032ace5621fd67e873fc869b216d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("LoadbalancerDomainsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df026e3e0ff19111be3e7c013723a2629cd3e61e2c2147af939c67734361dc7b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6f4922a7a37485f57ac74f32d04ba8eb5b06fce42ebb0aedf61804618b1871e9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__74a68412571b7566921dcb792e6ad00c5ef66f25d9101498585282c015afbbab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerDomains]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerDomains]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerDomains]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b4549053c57ec09e3e471445a31d7a00e1ae84b1e65f8b8f60602f5d5862480)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadbalancerDomainsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerDomainsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__065d13e6d8f09d5ceb7fb414e06a5316b9164ff9a0f29457e1def008225acc6e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCertificateName")
    def reset_certificate_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateName", []))

    @jsii.member(jsii_name="resetIsManaged")
    def reset_is_managed(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsManaged", []))

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @builtins.property
    @jsii.member(jsii_name="sslValidationErrorReasons")
    def ssl_validation_error_reasons(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "sslValidationErrorReasons"))

    @builtins.property
    @jsii.member(jsii_name="verificationErrorReasons")
    def verification_error_reasons(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "verificationErrorReasons"))

    @builtins.property
    @jsii.member(jsii_name="certificateNameInput")
    def certificate_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateNameInput"))

    @builtins.property
    @jsii.member(jsii_name="isManagedInput")
    def is_managed_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isManagedInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateName")
    def certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateName"))

    @certificate_name.setter
    def certificate_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bc6124f1ab1bcc1386155245d29637736ad188d009b86f34887439766c76958)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isManaged")
    def is_managed(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isManaged"))

    @is_managed.setter
    def is_managed(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__731e667bfccbe3d0d4786737c330daeb344e99b39ef76fb733e960af9f7ef2e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isManaged", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0334c77a8ec149f2b249e02cc4f174993479124cf038000763c9e468cc56ab5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerDomains]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerDomains]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerDomains]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8495e5c556d9653f5e0b296612af29fea6079ab2220a8d3d13794c983ff51278)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerFirewall",
    jsii_struct_bases=[],
    name_mapping={"allow": "allow", "deny": "deny"},
)
class LoadbalancerFirewall:
    def __init__(
        self,
        *,
        allow: typing.Optional[typing.Sequence[builtins.str]] = None,
        deny: typing.Optional[typing.Sequence[builtins.str]] = None,
    ) -> None:
        '''
        :param allow: the rules for ALLOWING traffic to the LB (strings in the form: 'ip:1.2.3.4' or 'cidr:1.2.0.0/16'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#allow Loadbalancer#allow}
        :param deny: the rules for DENYING traffic to the LB (strings in the form: 'ip:1.2.3.4' or 'cidr:1.2.0.0/16'). Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#deny Loadbalancer#deny}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74556f15023c7e10cefc949342f8aade1a183a5c632491f50f6f37ef68090bb8)
            check_type(argname="argument allow", value=allow, expected_type=type_hints["allow"])
            check_type(argname="argument deny", value=deny, expected_type=type_hints["deny"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if allow is not None:
            self._values["allow"] = allow
        if deny is not None:
            self._values["deny"] = deny

    @builtins.property
    def allow(self) -> typing.Optional[typing.List[builtins.str]]:
        '''the rules for ALLOWING traffic to the LB (strings in the form: 'ip:1.2.3.4' or 'cidr:1.2.0.0/16').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#allow Loadbalancer#allow}
        '''
        result = self._values.get("allow")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def deny(self) -> typing.Optional[typing.List[builtins.str]]:
        '''the rules for DENYING traffic to the LB (strings in the form: 'ip:1.2.3.4' or 'cidr:1.2.0.0/16').

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#deny Loadbalancer#deny}
        '''
        result = self._values.get("deny")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerFirewall(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerFirewallOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerFirewallOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb447cd868b05f43b39ed7dfb5816b22124ec1ea77de877ce3ba873c34eec7d3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetAllow")
    def reset_allow(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAllow", []))

    @jsii.member(jsii_name="resetDeny")
    def reset_deny(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeny", []))

    @builtins.property
    @jsii.member(jsii_name="allowInput")
    def allow_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "allowInput"))

    @builtins.property
    @jsii.member(jsii_name="denyInput")
    def deny_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "denyInput"))

    @builtins.property
    @jsii.member(jsii_name="allow")
    def allow(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "allow"))

    @allow.setter
    def allow(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed4294fd0dc6fe66fdd51af879a155e116ed577aec8e67250d7bd25ff29b00dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "allow", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deny")
    def deny(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "deny"))

    @deny.setter
    def deny(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__869776600f04ccc3d2cc42f66fa1aaa6a00d73b5c77593af857a2da71aa84a45)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deny", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerFirewall]:
        return typing.cast(typing.Optional[LoadbalancerFirewall], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LoadbalancerFirewall]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dacf05d27bcdaece273ecb6815d90376c887b72ba7cf09264e9ea507422d4f01)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerForwardingRule",
    jsii_struct_bases=[],
    name_mapping={
        "entry_port": "entryPort",
        "entry_protocol": "entryProtocol",
        "target_port": "targetPort",
        "target_protocol": "targetProtocol",
        "certificate_id": "certificateId",
        "certificate_name": "certificateName",
        "tls_passthrough": "tlsPassthrough",
    },
)
class LoadbalancerForwardingRule:
    def __init__(
        self,
        *,
        entry_port: jsii.Number,
        entry_protocol: builtins.str,
        target_port: jsii.Number,
        target_protocol: builtins.str,
        certificate_id: typing.Optional[builtins.str] = None,
        certificate_name: typing.Optional[builtins.str] = None,
        tls_passthrough: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param entry_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#entry_port Loadbalancer#entry_port}.
        :param entry_protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#entry_protocol Loadbalancer#entry_protocol}.
        :param target_port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_port Loadbalancer#target_port}.
        :param target_protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_protocol Loadbalancer#target_protocol}.
        :param certificate_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#certificate_id Loadbalancer#certificate_id}.
        :param certificate_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#certificate_name Loadbalancer#certificate_name}.
        :param tls_passthrough: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#tls_passthrough Loadbalancer#tls_passthrough}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49e35a19dc0c3e738b33e77db7d395ef8e5459346c68d44257824b66358d8e9e)
            check_type(argname="argument entry_port", value=entry_port, expected_type=type_hints["entry_port"])
            check_type(argname="argument entry_protocol", value=entry_protocol, expected_type=type_hints["entry_protocol"])
            check_type(argname="argument target_port", value=target_port, expected_type=type_hints["target_port"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
            check_type(argname="argument certificate_id", value=certificate_id, expected_type=type_hints["certificate_id"])
            check_type(argname="argument certificate_name", value=certificate_name, expected_type=type_hints["certificate_name"])
            check_type(argname="argument tls_passthrough", value=tls_passthrough, expected_type=type_hints["tls_passthrough"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "entry_port": entry_port,
            "entry_protocol": entry_protocol,
            "target_port": target_port,
            "target_protocol": target_protocol,
        }
        if certificate_id is not None:
            self._values["certificate_id"] = certificate_id
        if certificate_name is not None:
            self._values["certificate_name"] = certificate_name
        if tls_passthrough is not None:
            self._values["tls_passthrough"] = tls_passthrough

    @builtins.property
    def entry_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#entry_port Loadbalancer#entry_port}.'''
        result = self._values.get("entry_port")
        assert result is not None, "Required property 'entry_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def entry_protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#entry_protocol Loadbalancer#entry_protocol}.'''
        result = self._values.get("entry_protocol")
        assert result is not None, "Required property 'entry_protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def target_port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_port Loadbalancer#target_port}.'''
        result = self._values.get("target_port")
        assert result is not None, "Required property 'target_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target_protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_protocol Loadbalancer#target_protocol}.'''
        result = self._values.get("target_protocol")
        assert result is not None, "Required property 'target_protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#certificate_id Loadbalancer#certificate_id}.'''
        result = self._values.get("certificate_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#certificate_name Loadbalancer#certificate_name}.'''
        result = self._values.get("certificate_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tls_passthrough(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#tls_passthrough Loadbalancer#tls_passthrough}.'''
        result = self._values.get("tls_passthrough")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerForwardingRule(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerForwardingRuleList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerForwardingRuleList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__25d8cdd225b999e51b58d5f381193583af1a55757a4d0c623b52275330d2ec47)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "LoadbalancerForwardingRuleOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d78aaeffe576f9d1709a67136c84e70fd5b7941e14a4fefcd8d11521657e352)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("LoadbalancerForwardingRuleOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44b79b15bf4546a7a7cbe5973922d6247d3ea0d2869e9adadf7958f4a9fe5e41)
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
            type_hints = typing.get_type_hints(_typecheckingstub__355d28d53d4f2864b520619ca580b5fda6c89dcc0569c308c66be2dde54306a1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__213a780aa93ed8e0c8695f1b84c59cd525e463772ff88bd5f8ad5ef9cdb6acf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerForwardingRule]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerForwardingRule]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerForwardingRule]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be8768d41058600c515d11b69b5cd1ce539948874ddc165dfa8aa10c224e9738)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadbalancerForwardingRuleOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerForwardingRuleOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e55c71eb0d1f929e9c71502635b91156664b494ee450d89590413caa1765b68f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCertificateId")
    def reset_certificate_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateId", []))

    @jsii.member(jsii_name="resetCertificateName")
    def reset_certificate_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateName", []))

    @jsii.member(jsii_name="resetTlsPassthrough")
    def reset_tls_passthrough(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsPassthrough", []))

    @builtins.property
    @jsii.member(jsii_name="certificateIdInput")
    def certificate_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateIdInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateNameInput")
    def certificate_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateNameInput"))

    @builtins.property
    @jsii.member(jsii_name="entryPortInput")
    def entry_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "entryPortInput"))

    @builtins.property
    @jsii.member(jsii_name="entryProtocolInput")
    def entry_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "entryProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="targetPortInput")
    def target_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetPortInput"))

    @builtins.property
    @jsii.member(jsii_name="targetProtocolInput")
    def target_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsPassthroughInput")
    def tls_passthrough_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "tlsPassthroughInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateId")
    def certificate_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateId"))

    @certificate_id.setter
    def certificate_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7f78d3f8b032fa875f0391f6ef9e6d8f8c51e6e3b6045a70ded29036f3fba11e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="certificateName")
    def certificate_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateName"))

    @certificate_name.setter
    def certificate_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa5dc1e1a877f10fa9267a40702fbd7941bab638a295ca74a256b6fa4fb1756d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entryPort")
    def entry_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "entryPort"))

    @entry_port.setter
    def entry_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edf09d3e4ea1c163c6f95c2b2060a70cd8efe3188f928ca46a2719a4ac92c1f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entryPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="entryProtocol")
    def entry_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "entryProtocol"))

    @entry_protocol.setter
    def entry_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93f6fa2ab5fbbe4764ee2fb43a0349e702b30561a9ea050dae2923375d96634e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "entryProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetPort")
    def target_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetPort"))

    @target_port.setter
    def target_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c57bf4916e79bbc11a24dfbef7cb08423bbacaf8bf63399f6735c777ed5a740)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetProtocol")
    def target_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetProtocol"))

    @target_protocol.setter
    def target_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e01b3726fc8cc2a57f6cd9298ddc4f85ad4d400648ad438f899cc2a7a9598a1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tlsPassthrough")
    def tls_passthrough(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "tlsPassthrough"))

    @tls_passthrough.setter
    def tls_passthrough(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f28e31c60b9bdf00593bbc2d085c068e2d606696df020371dd6ea5a4f1e4f9b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tlsPassthrough", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerForwardingRule]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerForwardingRule]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerForwardingRule]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e82995a5e2b2f7c8620c5e0039dea3dc6657fadcb6d6c45f0eddd589715abe1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerGlbSettings",
    jsii_struct_bases=[],
    name_mapping={
        "target_port": "targetPort",
        "target_protocol": "targetProtocol",
        "cdn": "cdn",
        "failover_threshold": "failoverThreshold",
        "region_priorities": "regionPriorities",
    },
)
class LoadbalancerGlbSettings:
    def __init__(
        self,
        *,
        target_port: jsii.Number,
        target_protocol: builtins.str,
        cdn: typing.Optional[typing.Union["LoadbalancerGlbSettingsCdn", typing.Dict[builtins.str, typing.Any]]] = None,
        failover_threshold: typing.Optional[jsii.Number] = None,
        region_priorities: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
    ) -> None:
        '''
        :param target_port: target port rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_port Loadbalancer#target_port}
        :param target_protocol: target protocol rules. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_protocol Loadbalancer#target_protocol}
        :param cdn: cdn block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cdn Loadbalancer#cdn}
        :param failover_threshold: fail-over threshold. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#failover_threshold Loadbalancer#failover_threshold}
        :param region_priorities: region priority map. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#region_priorities Loadbalancer#region_priorities}
        '''
        if isinstance(cdn, dict):
            cdn = LoadbalancerGlbSettingsCdn(**cdn)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96c0de0a950316e351cc38e2ec1c19271d8c1a8e5c70a53fd19e31efaf86c931)
            check_type(argname="argument target_port", value=target_port, expected_type=type_hints["target_port"])
            check_type(argname="argument target_protocol", value=target_protocol, expected_type=type_hints["target_protocol"])
            check_type(argname="argument cdn", value=cdn, expected_type=type_hints["cdn"])
            check_type(argname="argument failover_threshold", value=failover_threshold, expected_type=type_hints["failover_threshold"])
            check_type(argname="argument region_priorities", value=region_priorities, expected_type=type_hints["region_priorities"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "target_port": target_port,
            "target_protocol": target_protocol,
        }
        if cdn is not None:
            self._values["cdn"] = cdn
        if failover_threshold is not None:
            self._values["failover_threshold"] = failover_threshold
        if region_priorities is not None:
            self._values["region_priorities"] = region_priorities

    @builtins.property
    def target_port(self) -> jsii.Number:
        '''target port rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_port Loadbalancer#target_port}
        '''
        result = self._values.get("target_port")
        assert result is not None, "Required property 'target_port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def target_protocol(self) -> builtins.str:
        '''target protocol rules.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#target_protocol Loadbalancer#target_protocol}
        '''
        result = self._values.get("target_protocol")
        assert result is not None, "Required property 'target_protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def cdn(self) -> typing.Optional["LoadbalancerGlbSettingsCdn"]:
        '''cdn block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cdn Loadbalancer#cdn}
        '''
        result = self._values.get("cdn")
        return typing.cast(typing.Optional["LoadbalancerGlbSettingsCdn"], result)

    @builtins.property
    def failover_threshold(self) -> typing.Optional[jsii.Number]:
        '''fail-over threshold.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#failover_threshold Loadbalancer#failover_threshold}
        '''
        result = self._values.get("failover_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def region_priorities(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, jsii.Number]]:
        '''region priority map.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#region_priorities Loadbalancer#region_priorities}
        '''
        result = self._values.get("region_priorities")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, jsii.Number]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerGlbSettings(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerGlbSettingsCdn",
    jsii_struct_bases=[],
    name_mapping={"is_enabled": "isEnabled"},
)
class LoadbalancerGlbSettingsCdn:
    def __init__(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_enabled: cache enable flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#is_enabled Loadbalancer#is_enabled}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dcdde4c59b22af9acf4f402815af3ff18cd78d6eb43778f326f50177ba4fe633)
            check_type(argname="argument is_enabled", value=is_enabled, expected_type=type_hints["is_enabled"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if is_enabled is not None:
            self._values["is_enabled"] = is_enabled

    @builtins.property
    def is_enabled(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''cache enable flag.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#is_enabled Loadbalancer#is_enabled}
        '''
        result = self._values.get("is_enabled")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerGlbSettingsCdn(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerGlbSettingsCdnOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerGlbSettingsCdnOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8eea480e7bcb3b4062e389898f99d683b337423654471889361cdb812b74632)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetIsEnabled")
    def reset_is_enabled(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsEnabled", []))

    @builtins.property
    @jsii.member(jsii_name="isEnabledInput")
    def is_enabled_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isEnabledInput"))

    @builtins.property
    @jsii.member(jsii_name="isEnabled")
    def is_enabled(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isEnabled"))

    @is_enabled.setter
    def is_enabled(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9377da121087f707e694d70f8ad1b4207836801a0775ec5b6879adc0ea2548d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isEnabled", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerGlbSettingsCdn]:
        return typing.cast(typing.Optional[LoadbalancerGlbSettingsCdn], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LoadbalancerGlbSettingsCdn],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ae6b27000a4be9aadd9a4a2c08db63dc46d4a1c59401e49abaaca2fa5294092)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class LoadbalancerGlbSettingsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerGlbSettingsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0ffe254cd53792b16a2ca15b113e8b653eb79cc2db8239a883967e13772270c1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="putCdn")
    def put_cdn(
        self,
        *,
        is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param is_enabled: cache enable flag. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#is_enabled Loadbalancer#is_enabled}
        '''
        value = LoadbalancerGlbSettingsCdn(is_enabled=is_enabled)

        return typing.cast(None, jsii.invoke(self, "putCdn", [value]))

    @jsii.member(jsii_name="resetCdn")
    def reset_cdn(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCdn", []))

    @jsii.member(jsii_name="resetFailoverThreshold")
    def reset_failover_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFailoverThreshold", []))

    @jsii.member(jsii_name="resetRegionPriorities")
    def reset_region_priorities(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegionPriorities", []))

    @builtins.property
    @jsii.member(jsii_name="cdn")
    def cdn(self) -> LoadbalancerGlbSettingsCdnOutputReference:
        return typing.cast(LoadbalancerGlbSettingsCdnOutputReference, jsii.get(self, "cdn"))

    @builtins.property
    @jsii.member(jsii_name="cdnInput")
    def cdn_input(self) -> typing.Optional[LoadbalancerGlbSettingsCdn]:
        return typing.cast(typing.Optional[LoadbalancerGlbSettingsCdn], jsii.get(self, "cdnInput"))

    @builtins.property
    @jsii.member(jsii_name="failoverThresholdInput")
    def failover_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "failoverThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionPrioritiesInput")
    def region_priorities_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, jsii.Number]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, jsii.Number]], jsii.get(self, "regionPrioritiesInput"))

    @builtins.property
    @jsii.member(jsii_name="targetPortInput")
    def target_port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "targetPortInput"))

    @builtins.property
    @jsii.member(jsii_name="targetProtocolInput")
    def target_protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "targetProtocolInput"))

    @builtins.property
    @jsii.member(jsii_name="failoverThreshold")
    def failover_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "failoverThreshold"))

    @failover_threshold.setter
    def failover_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b42309e2a5c4b340fea6232810d6a08f7b9fdc4d4f493974d1e2138fe3a46eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "failoverThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="regionPriorities")
    def region_priorities(self) -> typing.Mapping[builtins.str, jsii.Number]:
        return typing.cast(typing.Mapping[builtins.str, jsii.Number], jsii.get(self, "regionPriorities"))

    @region_priorities.setter
    def region_priorities(
        self,
        value: typing.Mapping[builtins.str, jsii.Number],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d45d88f927dfca636a9f77d56dc257c46146bfbff70bf06b81e49b72dea1e97d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "regionPriorities", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetPort")
    def target_port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "targetPort"))

    @target_port.setter
    def target_port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__953014f5e7b31906a97ff6f3b5e77c73a6d1eb0d42d9a38226384d9dd18067a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetPort", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="targetProtocol")
    def target_protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "targetProtocol"))

    @target_protocol.setter
    def target_protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e7d3a3c1edb0f923005dacdaccea5530d7d4d57365df4164594521a622c4c42c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "targetProtocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerGlbSettings]:
        return typing.cast(typing.Optional[LoadbalancerGlbSettings], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LoadbalancerGlbSettings]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66215f2e02e704e5c2d1c9a53c2862969e085bcbf605498f64014f21797266ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerHealthcheck",
    jsii_struct_bases=[],
    name_mapping={
        "port": "port",
        "protocol": "protocol",
        "check_interval_seconds": "checkIntervalSeconds",
        "healthy_threshold": "healthyThreshold",
        "path": "path",
        "response_timeout_seconds": "responseTimeoutSeconds",
        "unhealthy_threshold": "unhealthyThreshold",
    },
)
class LoadbalancerHealthcheck:
    def __init__(
        self,
        *,
        port: jsii.Number,
        protocol: builtins.str,
        check_interval_seconds: typing.Optional[jsii.Number] = None,
        healthy_threshold: typing.Optional[jsii.Number] = None,
        path: typing.Optional[builtins.str] = None,
        response_timeout_seconds: typing.Optional[jsii.Number] = None,
        unhealthy_threshold: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#port Loadbalancer#port}.
        :param protocol: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#protocol Loadbalancer#protocol}.
        :param check_interval_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#check_interval_seconds Loadbalancer#check_interval_seconds}.
        :param healthy_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#healthy_threshold Loadbalancer#healthy_threshold}.
        :param path: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#path Loadbalancer#path}.
        :param response_timeout_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#response_timeout_seconds Loadbalancer#response_timeout_seconds}.
        :param unhealthy_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#unhealthy_threshold Loadbalancer#unhealthy_threshold}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2351b9081f8720dabeb479589895249b97f67d8d84f6438e072d1397ebb66407)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument protocol", value=protocol, expected_type=type_hints["protocol"])
            check_type(argname="argument check_interval_seconds", value=check_interval_seconds, expected_type=type_hints["check_interval_seconds"])
            check_type(argname="argument healthy_threshold", value=healthy_threshold, expected_type=type_hints["healthy_threshold"])
            check_type(argname="argument path", value=path, expected_type=type_hints["path"])
            check_type(argname="argument response_timeout_seconds", value=response_timeout_seconds, expected_type=type_hints["response_timeout_seconds"])
            check_type(argname="argument unhealthy_threshold", value=unhealthy_threshold, expected_type=type_hints["unhealthy_threshold"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "port": port,
            "protocol": protocol,
        }
        if check_interval_seconds is not None:
            self._values["check_interval_seconds"] = check_interval_seconds
        if healthy_threshold is not None:
            self._values["healthy_threshold"] = healthy_threshold
        if path is not None:
            self._values["path"] = path
        if response_timeout_seconds is not None:
            self._values["response_timeout_seconds"] = response_timeout_seconds
        if unhealthy_threshold is not None:
            self._values["unhealthy_threshold"] = unhealthy_threshold

    @builtins.property
    def port(self) -> jsii.Number:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#port Loadbalancer#port}.'''
        result = self._values.get("port")
        assert result is not None, "Required property 'port' is missing"
        return typing.cast(jsii.Number, result)

    @builtins.property
    def protocol(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#protocol Loadbalancer#protocol}.'''
        result = self._values.get("protocol")
        assert result is not None, "Required property 'protocol' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def check_interval_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#check_interval_seconds Loadbalancer#check_interval_seconds}.'''
        result = self._values.get("check_interval_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def healthy_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#healthy_threshold Loadbalancer#healthy_threshold}.'''
        result = self._values.get("healthy_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def path(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#path Loadbalancer#path}.'''
        result = self._values.get("path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def response_timeout_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#response_timeout_seconds Loadbalancer#response_timeout_seconds}.'''
        result = self._values.get("response_timeout_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def unhealthy_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#unhealthy_threshold Loadbalancer#unhealthy_threshold}.'''
        result = self._values.get("unhealthy_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerHealthcheck(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerHealthcheckOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerHealthcheckOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__70b9ae03c1862c18b31d61fefa7121a55ef73bf2ad008ad41168af0267cb5d52)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCheckIntervalSeconds")
    def reset_check_interval_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCheckIntervalSeconds", []))

    @jsii.member(jsii_name="resetHealthyThreshold")
    def reset_healthy_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHealthyThreshold", []))

    @jsii.member(jsii_name="resetPath")
    def reset_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPath", []))

    @jsii.member(jsii_name="resetResponseTimeoutSeconds")
    def reset_response_timeout_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetResponseTimeoutSeconds", []))

    @jsii.member(jsii_name="resetUnhealthyThreshold")
    def reset_unhealthy_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUnhealthyThreshold", []))

    @builtins.property
    @jsii.member(jsii_name="checkIntervalSecondsInput")
    def check_interval_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "checkIntervalSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="healthyThresholdInput")
    def healthy_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "healthyThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="pathInput")
    def path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pathInput"))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="protocolInput")
    def protocol_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "protocolInput"))

    @builtins.property
    @jsii.member(jsii_name="responseTimeoutSecondsInput")
    def response_timeout_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "responseTimeoutSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="unhealthyThresholdInput")
    def unhealthy_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "unhealthyThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="checkIntervalSeconds")
    def check_interval_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "checkIntervalSeconds"))

    @check_interval_seconds.setter
    def check_interval_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7b5ddcf8ca43767b2a542f3889761bd61e3461d4c479b816fc1cd66f93485f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "checkIntervalSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="healthyThreshold")
    def healthy_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "healthyThreshold"))

    @healthy_threshold.setter
    def healthy_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18935c7e0a8198e6da61a874b6af944ccc0c51d7e16eaa75398bd594184c1dee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "healthyThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="path")
    def path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "path"))

    @path.setter
    def path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eee71844feffa98e0e376d3fd6c7ebdb4dbdc158ca9d0f296ad763f915ebb842)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "path", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e240bdb9d3e29f7348774fd38a0f2b6e970f61bc3a8dba6f5450623d46fecc72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="protocol")
    def protocol(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "protocol"))

    @protocol.setter
    def protocol(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67bf7eac6d2a6522e26186cb0cd04345de7a8e5440bc1ceeb32ff7d150fc8305)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "protocol", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="responseTimeoutSeconds")
    def response_timeout_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "responseTimeoutSeconds"))

    @response_timeout_seconds.setter
    def response_timeout_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be54652c8cd8081a6bd9cdec1e08b409e92f2a63f4f8f67a722187cd41ee4bce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "responseTimeoutSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="unhealthyThreshold")
    def unhealthy_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "unhealthyThreshold"))

    @unhealthy_threshold.setter
    def unhealthy_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__080de2f09cbc6c6441b1b579a4994b922582f02bd9e756f2082a26ac595db69e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "unhealthyThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerHealthcheck]:
        return typing.cast(typing.Optional[LoadbalancerHealthcheck], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[LoadbalancerHealthcheck]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe11ceaf1c61eaf28b28225d8fd95a8738461177a86fe7f8853ae19910282b74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerStickySessions",
    jsii_struct_bases=[],
    name_mapping={
        "cookie_name": "cookieName",
        "cookie_ttl_seconds": "cookieTtlSeconds",
        "type": "type",
    },
)
class LoadbalancerStickySessions:
    def __init__(
        self,
        *,
        cookie_name: typing.Optional[builtins.str] = None,
        cookie_ttl_seconds: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param cookie_name: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cookie_name Loadbalancer#cookie_name}.
        :param cookie_ttl_seconds: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cookie_ttl_seconds Loadbalancer#cookie_ttl_seconds}.
        :param type: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#type Loadbalancer#type}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97387ea797209906ce5636875ca81b265502a5ab4780c5fca259942ffb3e276a)
            check_type(argname="argument cookie_name", value=cookie_name, expected_type=type_hints["cookie_name"])
            check_type(argname="argument cookie_ttl_seconds", value=cookie_ttl_seconds, expected_type=type_hints["cookie_ttl_seconds"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if cookie_name is not None:
            self._values["cookie_name"] = cookie_name
        if cookie_ttl_seconds is not None:
            self._values["cookie_ttl_seconds"] = cookie_ttl_seconds
        if type is not None:
            self._values["type"] = type

    @builtins.property
    def cookie_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cookie_name Loadbalancer#cookie_name}.'''
        result = self._values.get("cookie_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def cookie_ttl_seconds(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#cookie_ttl_seconds Loadbalancer#cookie_ttl_seconds}.'''
        result = self._values.get("cookie_ttl_seconds")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/loadbalancer#type Loadbalancer#type}.'''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "LoadbalancerStickySessions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class LoadbalancerStickySessionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.loadbalancer.LoadbalancerStickySessionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__05ee25301d9f52947a1281f8898337fdbc4d5f9c5f121c9a2374a2ac648a65fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetCookieName")
    def reset_cookie_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookieName", []))

    @jsii.member(jsii_name="resetCookieTtlSeconds")
    def reset_cookie_ttl_seconds(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCookieTtlSeconds", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @builtins.property
    @jsii.member(jsii_name="cookieNameInput")
    def cookie_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "cookieNameInput"))

    @builtins.property
    @jsii.member(jsii_name="cookieTtlSecondsInput")
    def cookie_ttl_seconds_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "cookieTtlSecondsInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="cookieName")
    def cookie_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "cookieName"))

    @cookie_name.setter
    def cookie_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e00b774044adb2f53abcbd27cb69921e7e43cf65b968b0827264b4f1ce2e220f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cookieName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="cookieTtlSeconds")
    def cookie_ttl_seconds(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "cookieTtlSeconds"))

    @cookie_ttl_seconds.setter
    def cookie_ttl_seconds(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__90faff8ad550cc04d3e24c587fd59219e761587c89c9e21412696e8c76f62c04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "cookieTtlSeconds", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3a58a639efed2c9d0237d07fe2f3f1d5b4c09e47819ca816b2b0007f1077b6d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[LoadbalancerStickySessions]:
        return typing.cast(typing.Optional[LoadbalancerStickySessions], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[LoadbalancerStickySessions],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9514aa4fd6ff256c9a0d3c14e1ad06a0c6acaa2f38dd8d3c1a324297ec5d7a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "Loadbalancer",
    "LoadbalancerConfig",
    "LoadbalancerDomains",
    "LoadbalancerDomainsList",
    "LoadbalancerDomainsOutputReference",
    "LoadbalancerFirewall",
    "LoadbalancerFirewallOutputReference",
    "LoadbalancerForwardingRule",
    "LoadbalancerForwardingRuleList",
    "LoadbalancerForwardingRuleOutputReference",
    "LoadbalancerGlbSettings",
    "LoadbalancerGlbSettingsCdn",
    "LoadbalancerGlbSettingsCdnOutputReference",
    "LoadbalancerGlbSettingsOutputReference",
    "LoadbalancerHealthcheck",
    "LoadbalancerHealthcheckOutputReference",
    "LoadbalancerStickySessions",
    "LoadbalancerStickySessionsOutputReference",
]

publication.publish()

def _typecheckingstub__0a68ad9900cb6a64cd2e94d623a87378011a58fa274b5c8593ce89ca399087b0(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    name: builtins.str,
    algorithm: typing.Optional[builtins.str] = None,
    disable_lets_encrypt_dns_records: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    domains: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerDomains, typing.Dict[builtins.str, typing.Any]]]]] = None,
    droplet_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    droplet_tag: typing.Optional[builtins.str] = None,
    enable_backend_keepalive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_proxy_protocol: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firewall: typing.Optional[typing.Union[LoadbalancerFirewall, typing.Dict[builtins.str, typing.Any]]] = None,
    forwarding_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerForwardingRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
    glb_settings: typing.Optional[typing.Union[LoadbalancerGlbSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    healthcheck: typing.Optional[typing.Union[LoadbalancerHealthcheck, typing.Dict[builtins.str, typing.Any]]] = None,
    http_idle_timeout_seconds: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    network: typing.Optional[builtins.str] = None,
    network_stack: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    redirect_http_to_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    size: typing.Optional[builtins.str] = None,
    size_unit: typing.Optional[jsii.Number] = None,
    sticky_sessions: typing.Optional[typing.Union[LoadbalancerStickySessions, typing.Dict[builtins.str, typing.Any]]] = None,
    target_load_balancer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tls_cipher_policy: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
    vpc_uuid: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__18103c127e676f5674e65deb9eb0619505ca972d422311babfeeb398ee66251b(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7f584a2a08db381ebe93a697b28f6c9b3766d081d60780426bb7d2fe978c7fe(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerDomains, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2f95e18a934d365f327f2e279a0a684fede396bcab3da08953fbb9624dde27c8(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerForwardingRule, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9966ccc372df39fcfc3face8dcd57899adaf44a754f8a5c94f2498112d9620af(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c40def00f24dd55ac74c0523644dad47fb76de56c2d9d3cef0924311df6287c5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f813339c027b0c781281d93e846384d9381af5fe398a176f0e8b00833fafa0c7(
    value: typing.List[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32e535d9b48b5c9c30176ab1ae74399665f9846dce9d13e1966b6a57d3e4fd00(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d66dff725f9491e54fbc78147d0a5c5a77f578a549f4f1c283d962f0ec4d71bd(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcd1a4312c984e1590eb072721005cc696abfc7fb3030ce131f10a1ce90622d4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db331010016ff26ee2e5f504a3df3c2543d3948ead0b32d4d0d1b4b42b3dc81f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54bf8035d8b367590c8b7f7211290cdebe90bb110e7bd5b6225721c8b5af5635(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f52b85e859155069dce00d76a5cffc62e57c2db5a977027c4d4ff6956fe409f4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e3055178433889f8af99847bb2aa59cf23fc4dacfd801da322060b6815ada67(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2fbb837ce1978fa4c9dc966c0dc18c74aef3335517aba0abdb38ab113adbacee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ada167cd1c45f058a88d6148bbf0680f22e5f9b018156d55cb3c57fc2438193(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e61138417f7c2534d2568818a4aa56daf20723a8d93ba46553b14e3bb2631b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e348e7aaf03337b1ec7e56ade38780f7e19e3fb0a3a27c4c76c5336d23a5ba3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7836df086f3efcb1a0fa6b26a91722ea517995ed983295cd3b180f85cf85ecb2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__968e87d7d9b676761740b32d6acde0cdc0581046fa7195d3120c57b7dac6087f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d7f7e5c6dd1233afe0373a36181a5fe77c2b15f978e5dd161d8dfd6d665d498(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eff227d581cc298fb43c6a18711732cf0146facc6e7261c20b9b7f6231b73771(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20522b12d3d98e5c328437536beb68e7d072c57b57e468a82d0f295c63eb09fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__024a2d70d338b88fcc6856488903be5ee07a728324ab3a88597af939bfabb8ad(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c7d6955a724c1706f8f894cf17bdba6a044a054671acfbca57cae71a67736ac(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: builtins.str,
    algorithm: typing.Optional[builtins.str] = None,
    disable_lets_encrypt_dns_records: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    domains: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerDomains, typing.Dict[builtins.str, typing.Any]]]]] = None,
    droplet_ids: typing.Optional[typing.Sequence[jsii.Number]] = None,
    droplet_tag: typing.Optional[builtins.str] = None,
    enable_backend_keepalive: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    enable_proxy_protocol: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    firewall: typing.Optional[typing.Union[LoadbalancerFirewall, typing.Dict[builtins.str, typing.Any]]] = None,
    forwarding_rule: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[LoadbalancerForwardingRule, typing.Dict[builtins.str, typing.Any]]]]] = None,
    glb_settings: typing.Optional[typing.Union[LoadbalancerGlbSettings, typing.Dict[builtins.str, typing.Any]]] = None,
    healthcheck: typing.Optional[typing.Union[LoadbalancerHealthcheck, typing.Dict[builtins.str, typing.Any]]] = None,
    http_idle_timeout_seconds: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    network: typing.Optional[builtins.str] = None,
    network_stack: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    redirect_http_to_https: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    region: typing.Optional[builtins.str] = None,
    size: typing.Optional[builtins.str] = None,
    size_unit: typing.Optional[jsii.Number] = None,
    sticky_sessions: typing.Optional[typing.Union[LoadbalancerStickySessions, typing.Dict[builtins.str, typing.Any]]] = None,
    target_load_balancer_ids: typing.Optional[typing.Sequence[builtins.str]] = None,
    tls_cipher_policy: typing.Optional[builtins.str] = None,
    type: typing.Optional[builtins.str] = None,
    vpc_uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0abf9f4c7e1038194cc242bb41d43ca5e540ca3641b62e7ccb0d1df09165f6a9(
    *,
    name: builtins.str,
    certificate_name: typing.Optional[builtins.str] = None,
    is_managed: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b279365cf44bab74fa1e66d6fecb14455b27043d22f831cd7bb4937eab5557e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__774a822f2d5e6494a87c201ed6939d245561032ace5621fd67e873fc869b216d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df026e3e0ff19111be3e7c013723a2629cd3e61e2c2147af939c67734361dc7b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4922a7a37485f57ac74f32d04ba8eb5b06fce42ebb0aedf61804618b1871e9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74a68412571b7566921dcb792e6ad00c5ef66f25d9101498585282c015afbbab(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b4549053c57ec09e3e471445a31d7a00e1ae84b1e65f8b8f60602f5d5862480(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerDomains]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__065d13e6d8f09d5ceb7fb414e06a5316b9164ff9a0f29457e1def008225acc6e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bc6124f1ab1bcc1386155245d29637736ad188d009b86f34887439766c76958(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__731e667bfccbe3d0d4786737c330daeb344e99b39ef76fb733e960af9f7ef2e0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0334c77a8ec149f2b249e02cc4f174993479124cf038000763c9e468cc56ab5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8495e5c556d9653f5e0b296612af29fea6079ab2220a8d3d13794c983ff51278(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerDomains]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74556f15023c7e10cefc949342f8aade1a183a5c632491f50f6f37ef68090bb8(
    *,
    allow: typing.Optional[typing.Sequence[builtins.str]] = None,
    deny: typing.Optional[typing.Sequence[builtins.str]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb447cd868b05f43b39ed7dfb5816b22124ec1ea77de877ce3ba873c34eec7d3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed4294fd0dc6fe66fdd51af879a155e116ed577aec8e67250d7bd25ff29b00dd(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__869776600f04ccc3d2cc42f66fa1aaa6a00d73b5c77593af857a2da71aa84a45(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dacf05d27bcdaece273ecb6815d90376c887b72ba7cf09264e9ea507422d4f01(
    value: typing.Optional[LoadbalancerFirewall],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49e35a19dc0c3e738b33e77db7d395ef8e5459346c68d44257824b66358d8e9e(
    *,
    entry_port: jsii.Number,
    entry_protocol: builtins.str,
    target_port: jsii.Number,
    target_protocol: builtins.str,
    certificate_id: typing.Optional[builtins.str] = None,
    certificate_name: typing.Optional[builtins.str] = None,
    tls_passthrough: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25d8cdd225b999e51b58d5f381193583af1a55757a4d0c623b52275330d2ec47(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d78aaeffe576f9d1709a67136c84e70fd5b7941e14a4fefcd8d11521657e352(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44b79b15bf4546a7a7cbe5973922d6247d3ea0d2869e9adadf7958f4a9fe5e41(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__355d28d53d4f2864b520619ca580b5fda6c89dcc0569c308c66be2dde54306a1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__213a780aa93ed8e0c8695f1b84c59cd525e463772ff88bd5f8ad5ef9cdb6acf6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be8768d41058600c515d11b69b5cd1ce539948874ddc165dfa8aa10c224e9738(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[LoadbalancerForwardingRule]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e55c71eb0d1f929e9c71502635b91156664b494ee450d89590413caa1765b68f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f78d3f8b032fa875f0391f6ef9e6d8f8c51e6e3b6045a70ded29036f3fba11e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa5dc1e1a877f10fa9267a40702fbd7941bab638a295ca74a256b6fa4fb1756d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edf09d3e4ea1c163c6f95c2b2060a70cd8efe3188f928ca46a2719a4ac92c1f3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93f6fa2ab5fbbe4764ee2fb43a0349e702b30561a9ea050dae2923375d96634e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c57bf4916e79bbc11a24dfbef7cb08423bbacaf8bf63399f6735c777ed5a740(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e01b3726fc8cc2a57f6cd9298ddc4f85ad4d400648ad438f899cc2a7a9598a1f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f28e31c60b9bdf00593bbc2d085c068e2d606696df020371dd6ea5a4f1e4f9b9(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e82995a5e2b2f7c8620c5e0039dea3dc6657fadcb6d6c45f0eddd589715abe1c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, LoadbalancerForwardingRule]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96c0de0a950316e351cc38e2ec1c19271d8c1a8e5c70a53fd19e31efaf86c931(
    *,
    target_port: jsii.Number,
    target_protocol: builtins.str,
    cdn: typing.Optional[typing.Union[LoadbalancerGlbSettingsCdn, typing.Dict[builtins.str, typing.Any]]] = None,
    failover_threshold: typing.Optional[jsii.Number] = None,
    region_priorities: typing.Optional[typing.Mapping[builtins.str, jsii.Number]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dcdde4c59b22af9acf4f402815af3ff18cd78d6eb43778f326f50177ba4fe633(
    *,
    is_enabled: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8eea480e7bcb3b4062e389898f99d683b337423654471889361cdb812b74632(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9377da121087f707e694d70f8ad1b4207836801a0775ec5b6879adc0ea2548d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ae6b27000a4be9aadd9a4a2c08db63dc46d4a1c59401e49abaaca2fa5294092(
    value: typing.Optional[LoadbalancerGlbSettingsCdn],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ffe254cd53792b16a2ca15b113e8b653eb79cc2db8239a883967e13772270c1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b42309e2a5c4b340fea6232810d6a08f7b9fdc4d4f493974d1e2138fe3a46eb(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d45d88f927dfca636a9f77d56dc257c46146bfbff70bf06b81e49b72dea1e97d(
    value: typing.Mapping[builtins.str, jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__953014f5e7b31906a97ff6f3b5e77c73a6d1eb0d42d9a38226384d9dd18067a1(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7d3a3c1edb0f923005dacdaccea5530d7d4d57365df4164594521a622c4c42c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66215f2e02e704e5c2d1c9a53c2862969e085bcbf605498f64014f21797266ed(
    value: typing.Optional[LoadbalancerGlbSettings],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2351b9081f8720dabeb479589895249b97f67d8d84f6438e072d1397ebb66407(
    *,
    port: jsii.Number,
    protocol: builtins.str,
    check_interval_seconds: typing.Optional[jsii.Number] = None,
    healthy_threshold: typing.Optional[jsii.Number] = None,
    path: typing.Optional[builtins.str] = None,
    response_timeout_seconds: typing.Optional[jsii.Number] = None,
    unhealthy_threshold: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70b9ae03c1862c18b31d61fefa7121a55ef73bf2ad008ad41168af0267cb5d52(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7b5ddcf8ca43767b2a542f3889761bd61e3461d4c479b816fc1cd66f93485f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18935c7e0a8198e6da61a874b6af944ccc0c51d7e16eaa75398bd594184c1dee(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eee71844feffa98e0e376d3fd6c7ebdb4dbdc158ca9d0f296ad763f915ebb842(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e240bdb9d3e29f7348774fd38a0f2b6e970f61bc3a8dba6f5450623d46fecc72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67bf7eac6d2a6522e26186cb0cd04345de7a8e5440bc1ceeb32ff7d150fc8305(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be54652c8cd8081a6bd9cdec1e08b409e92f2a63f4f8f67a722187cd41ee4bce(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__080de2f09cbc6c6441b1b579a4994b922582f02bd9e756f2082a26ac595db69e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe11ceaf1c61eaf28b28225d8fd95a8738461177a86fe7f8853ae19910282b74(
    value: typing.Optional[LoadbalancerHealthcheck],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97387ea797209906ce5636875ca81b265502a5ab4780c5fca259942ffb3e276a(
    *,
    cookie_name: typing.Optional[builtins.str] = None,
    cookie_ttl_seconds: typing.Optional[jsii.Number] = None,
    type: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05ee25301d9f52947a1281f8898337fdbc4d5f9c5f121c9a2374a2ac648a65fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e00b774044adb2f53abcbd27cb69921e7e43cf65b968b0827264b4f1ce2e220f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90faff8ad550cc04d3e24c587fd59219e761587c89c9e21412696e8c76f62c04(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3a58a639efed2c9d0237d07fe2f3f1d5b4c09e47819ca816b2b0007f1077b6d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9514aa4fd6ff256c9a0d3c14e1ad06a0c6acaa2f38dd8d3c1a324297ec5d7a0(
    value: typing.Optional[LoadbalancerStickySessions],
) -> None:
    """Type checking stubs"""
    pass
