r'''
# `provider`

Refer to the Terraform Registry for docs: [`digitalocean`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs).
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


class DigitaloceanProvider(
    _cdktf_9a9027ec.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.provider.DigitaloceanProvider",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs digitalocean}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id: builtins.str,
        *,
        alias: typing.Optional[builtins.str] = None,
        api_endpoint: typing.Optional[builtins.str] = None,
        http_retry_max: typing.Optional[jsii.Number] = None,
        http_retry_wait_max: typing.Optional[jsii.Number] = None,
        http_retry_wait_min: typing.Optional[jsii.Number] = None,
        requests_per_second: typing.Optional[jsii.Number] = None,
        spaces_access_id: typing.Optional[builtins.str] = None,
        spaces_endpoint: typing.Optional[builtins.str] = None,
        spaces_secret_key: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs digitalocean} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#alias DigitaloceanProvider#alias}
        :param api_endpoint: The URL to use for the DigitalOcean API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#api_endpoint DigitaloceanProvider#api_endpoint}
        :param http_retry_max: The maximum number of retries on a failed API request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_max DigitaloceanProvider#http_retry_max}
        :param http_retry_wait_max: The maximum wait time (in seconds) between failed API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_wait_max DigitaloceanProvider#http_retry_wait_max}
        :param http_retry_wait_min: The minimum wait time (in seconds) between failed API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_wait_min DigitaloceanProvider#http_retry_wait_min}
        :param requests_per_second: The rate of requests per second to limit the HTTP client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#requests_per_second DigitaloceanProvider#requests_per_second}
        :param spaces_access_id: The access key ID for Spaces API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_access_id DigitaloceanProvider#spaces_access_id}
        :param spaces_endpoint: The URL to use for the DigitalOcean Spaces API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_endpoint DigitaloceanProvider#spaces_endpoint}
        :param spaces_secret_key: The secret access key for Spaces API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_secret_key DigitaloceanProvider#spaces_secret_key}
        :param token: The token key for API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#token DigitaloceanProvider#token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c953c0b514d83cc89545bd360c7500b98399795af00919868177dace7fa797e6)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = DigitaloceanProviderConfig(
            alias=alias,
            api_endpoint=api_endpoint,
            http_retry_max=http_retry_max,
            http_retry_wait_max=http_retry_wait_max,
            http_retry_wait_min=http_retry_wait_min,
            requests_per_second=requests_per_second,
            spaces_access_id=spaces_access_id,
            spaces_endpoint=spaces_endpoint,
            spaces_secret_key=spaces_secret_key,
            token=token,
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
        '''Generates CDKTF code for importing a DigitaloceanProvider resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DigitaloceanProvider to import.
        :param import_from_id: The id of the existing DigitaloceanProvider that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DigitaloceanProvider to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a95a8226d03f2d357835858d0c10e55353482e69f3b13872b8bb84fae46137e)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="resetApiEndpoint")
    def reset_api_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiEndpoint", []))

    @jsii.member(jsii_name="resetHttpRetryMax")
    def reset_http_retry_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpRetryMax", []))

    @jsii.member(jsii_name="resetHttpRetryWaitMax")
    def reset_http_retry_wait_max(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpRetryWaitMax", []))

    @jsii.member(jsii_name="resetHttpRetryWaitMin")
    def reset_http_retry_wait_min(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpRetryWaitMin", []))

    @jsii.member(jsii_name="resetRequestsPerSecond")
    def reset_requests_per_second(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRequestsPerSecond", []))

    @jsii.member(jsii_name="resetSpacesAccessId")
    def reset_spaces_access_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpacesAccessId", []))

    @jsii.member(jsii_name="resetSpacesEndpoint")
    def reset_spaces_endpoint(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpacesEndpoint", []))

    @jsii.member(jsii_name="resetSpacesSecretKey")
    def reset_spaces_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpacesSecretKey", []))

    @jsii.member(jsii_name="resetToken")
    def reset_token(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetToken", []))

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
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="apiEndpointInput")
    def api_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="httpRetryMaxInput")
    def http_retry_max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpRetryMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="httpRetryWaitMaxInput")
    def http_retry_wait_max_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpRetryWaitMaxInput"))

    @builtins.property
    @jsii.member(jsii_name="httpRetryWaitMinInput")
    def http_retry_wait_min_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpRetryWaitMinInput"))

    @builtins.property
    @jsii.member(jsii_name="requestsPerSecondInput")
    def requests_per_second_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requestsPerSecondInput"))

    @builtins.property
    @jsii.member(jsii_name="spacesAccessIdInput")
    def spaces_access_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spacesAccessIdInput"))

    @builtins.property
    @jsii.member(jsii_name="spacesEndpointInput")
    def spaces_endpoint_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spacesEndpointInput"))

    @builtins.property
    @jsii.member(jsii_name="spacesSecretKeyInput")
    def spaces_secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spacesSecretKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="tokenInput")
    def token_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "tokenInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__99d4121bc828c00437fa59397627030b5f9b54e1f5dd311e414d83e587ad73c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="apiEndpoint")
    def api_endpoint(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiEndpoint"))

    @api_endpoint.setter
    def api_endpoint(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4a9b85c1d0332e3219324f1deed0b6d81a83e6471e110466c2039d2dfaf97eb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpRetryMax")
    def http_retry_max(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpRetryMax"))

    @http_retry_max.setter
    def http_retry_max(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b987fc35dc824d2c605331ac75f003f11bc26e5c43f32c706ebe4e9546890f8f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpRetryMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpRetryWaitMax")
    def http_retry_wait_max(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpRetryWaitMax"))

    @http_retry_wait_max.setter
    def http_retry_wait_max(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f663dfe25625db5538cefb982acac4a2b5f4c04cbedf7b8261f4abbb5c3bed9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpRetryWaitMax", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="httpRetryWaitMin")
    def http_retry_wait_min(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "httpRetryWaitMin"))

    @http_retry_wait_min.setter
    def http_retry_wait_min(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f39b1d8aef7ac70a09f916fbd39c6c4337e2e11c5b066cb8d05a21924d74087)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "httpRetryWaitMin", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="requestsPerSecond")
    def requests_per_second(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "requestsPerSecond"))

    @requests_per_second.setter
    def requests_per_second(self, value: typing.Optional[jsii.Number]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a7652c5482dd4ddb5137cd900c3e383d1b5ebf284556e298d51a5a74a1c131c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "requestsPerSecond", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spacesAccessId")
    def spaces_access_id(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spacesAccessId"))

    @spaces_access_id.setter
    def spaces_access_id(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17b2bbf0364b81d1c2b9490f1b796c274993cfe7db3c9deb1b75289ee8da2189)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spacesAccessId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spacesEndpoint")
    def spaces_endpoint(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spacesEndpoint"))

    @spaces_endpoint.setter
    def spaces_endpoint(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c15d4dca4b52bdd66460a53be92235ce0b0b415a60ac44286ac8757cb331f31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spacesEndpoint", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="spacesSecretKey")
    def spaces_secret_key(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "spacesSecretKey"))

    @spaces_secret_key.setter
    def spaces_secret_key(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8594ba50455e3fbccd4914a753218dfb030dd68bad9c7f02837c4e65e385d136)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "spacesSecretKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="token")
    def token(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "token"))

    @token.setter
    def token(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb7d23926ec36ea0c297ca8492f5ddfb667439579d424d6a4e79602a727a4938)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "token", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.provider.DigitaloceanProviderConfig",
    jsii_struct_bases=[],
    name_mapping={
        "alias": "alias",
        "api_endpoint": "apiEndpoint",
        "http_retry_max": "httpRetryMax",
        "http_retry_wait_max": "httpRetryWaitMax",
        "http_retry_wait_min": "httpRetryWaitMin",
        "requests_per_second": "requestsPerSecond",
        "spaces_access_id": "spacesAccessId",
        "spaces_endpoint": "spacesEndpoint",
        "spaces_secret_key": "spacesSecretKey",
        "token": "token",
    },
)
class DigitaloceanProviderConfig:
    def __init__(
        self,
        *,
        alias: typing.Optional[builtins.str] = None,
        api_endpoint: typing.Optional[builtins.str] = None,
        http_retry_max: typing.Optional[jsii.Number] = None,
        http_retry_wait_max: typing.Optional[jsii.Number] = None,
        http_retry_wait_min: typing.Optional[jsii.Number] = None,
        requests_per_second: typing.Optional[jsii.Number] = None,
        spaces_access_id: typing.Optional[builtins.str] = None,
        spaces_endpoint: typing.Optional[builtins.str] = None,
        spaces_secret_key: typing.Optional[builtins.str] = None,
        token: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param alias: Alias name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#alias DigitaloceanProvider#alias}
        :param api_endpoint: The URL to use for the DigitalOcean API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#api_endpoint DigitaloceanProvider#api_endpoint}
        :param http_retry_max: The maximum number of retries on a failed API request. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_max DigitaloceanProvider#http_retry_max}
        :param http_retry_wait_max: The maximum wait time (in seconds) between failed API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_wait_max DigitaloceanProvider#http_retry_wait_max}
        :param http_retry_wait_min: The minimum wait time (in seconds) between failed API requests. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_wait_min DigitaloceanProvider#http_retry_wait_min}
        :param requests_per_second: The rate of requests per second to limit the HTTP client. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#requests_per_second DigitaloceanProvider#requests_per_second}
        :param spaces_access_id: The access key ID for Spaces API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_access_id DigitaloceanProvider#spaces_access_id}
        :param spaces_endpoint: The URL to use for the DigitalOcean Spaces API. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_endpoint DigitaloceanProvider#spaces_endpoint}
        :param spaces_secret_key: The secret access key for Spaces API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_secret_key DigitaloceanProvider#spaces_secret_key}
        :param token: The token key for API operations. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#token DigitaloceanProvider#token}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6594c2e8b0654c0173e1dfaf92b321088509417e3a14af046aa974b6a957424)
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
            check_type(argname="argument api_endpoint", value=api_endpoint, expected_type=type_hints["api_endpoint"])
            check_type(argname="argument http_retry_max", value=http_retry_max, expected_type=type_hints["http_retry_max"])
            check_type(argname="argument http_retry_wait_max", value=http_retry_wait_max, expected_type=type_hints["http_retry_wait_max"])
            check_type(argname="argument http_retry_wait_min", value=http_retry_wait_min, expected_type=type_hints["http_retry_wait_min"])
            check_type(argname="argument requests_per_second", value=requests_per_second, expected_type=type_hints["requests_per_second"])
            check_type(argname="argument spaces_access_id", value=spaces_access_id, expected_type=type_hints["spaces_access_id"])
            check_type(argname="argument spaces_endpoint", value=spaces_endpoint, expected_type=type_hints["spaces_endpoint"])
            check_type(argname="argument spaces_secret_key", value=spaces_secret_key, expected_type=type_hints["spaces_secret_key"])
            check_type(argname="argument token", value=token, expected_type=type_hints["token"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if alias is not None:
            self._values["alias"] = alias
        if api_endpoint is not None:
            self._values["api_endpoint"] = api_endpoint
        if http_retry_max is not None:
            self._values["http_retry_max"] = http_retry_max
        if http_retry_wait_max is not None:
            self._values["http_retry_wait_max"] = http_retry_wait_max
        if http_retry_wait_min is not None:
            self._values["http_retry_wait_min"] = http_retry_wait_min
        if requests_per_second is not None:
            self._values["requests_per_second"] = requests_per_second
        if spaces_access_id is not None:
            self._values["spaces_access_id"] = spaces_access_id
        if spaces_endpoint is not None:
            self._values["spaces_endpoint"] = spaces_endpoint
        if spaces_secret_key is not None:
            self._values["spaces_secret_key"] = spaces_secret_key
        if token is not None:
            self._values["token"] = token

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#alias DigitaloceanProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_endpoint(self) -> typing.Optional[builtins.str]:
        '''The URL to use for the DigitalOcean API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#api_endpoint DigitaloceanProvider#api_endpoint}
        '''
        result = self._values.get("api_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def http_retry_max(self) -> typing.Optional[jsii.Number]:
        '''The maximum number of retries on a failed API request.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_max DigitaloceanProvider#http_retry_max}
        '''
        result = self._values.get("http_retry_max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_retry_wait_max(self) -> typing.Optional[jsii.Number]:
        '''The maximum wait time (in seconds) between failed API requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_wait_max DigitaloceanProvider#http_retry_wait_max}
        '''
        result = self._values.get("http_retry_wait_max")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def http_retry_wait_min(self) -> typing.Optional[jsii.Number]:
        '''The minimum wait time (in seconds) between failed API requests.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#http_retry_wait_min DigitaloceanProvider#http_retry_wait_min}
        '''
        result = self._values.get("http_retry_wait_min")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def requests_per_second(self) -> typing.Optional[jsii.Number]:
        '''The rate of requests per second to limit the HTTP client.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#requests_per_second DigitaloceanProvider#requests_per_second}
        '''
        result = self._values.get("requests_per_second")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def spaces_access_id(self) -> typing.Optional[builtins.str]:
        '''The access key ID for Spaces API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_access_id DigitaloceanProvider#spaces_access_id}
        '''
        result = self._values.get("spaces_access_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spaces_endpoint(self) -> typing.Optional[builtins.str]:
        '''The URL to use for the DigitalOcean Spaces API.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_endpoint DigitaloceanProvider#spaces_endpoint}
        '''
        result = self._values.get("spaces_endpoint")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spaces_secret_key(self) -> typing.Optional[builtins.str]:
        '''The secret access key for Spaces API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#spaces_secret_key DigitaloceanProvider#spaces_secret_key}
        '''
        result = self._values.get("spaces_secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def token(self) -> typing.Optional[builtins.str]:
        '''The token key for API operations.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs#token DigitaloceanProvider#token}
        '''
        result = self._values.get("token")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DigitaloceanProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DigitaloceanProvider",
    "DigitaloceanProviderConfig",
]

publication.publish()

def _typecheckingstub__c953c0b514d83cc89545bd360c7500b98399795af00919868177dace7fa797e6(
    scope: _constructs_77d1e7e8.Construct,
    id: builtins.str,
    *,
    alias: typing.Optional[builtins.str] = None,
    api_endpoint: typing.Optional[builtins.str] = None,
    http_retry_max: typing.Optional[jsii.Number] = None,
    http_retry_wait_max: typing.Optional[jsii.Number] = None,
    http_retry_wait_min: typing.Optional[jsii.Number] = None,
    requests_per_second: typing.Optional[jsii.Number] = None,
    spaces_access_id: typing.Optional[builtins.str] = None,
    spaces_endpoint: typing.Optional[builtins.str] = None,
    spaces_secret_key: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a95a8226d03f2d357835858d0c10e55353482e69f3b13872b8bb84fae46137e(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99d4121bc828c00437fa59397627030b5f9b54e1f5dd311e414d83e587ad73c6(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4a9b85c1d0332e3219324f1deed0b6d81a83e6471e110466c2039d2dfaf97eb(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b987fc35dc824d2c605331ac75f003f11bc26e5c43f32c706ebe4e9546890f8f(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f663dfe25625db5538cefb982acac4a2b5f4c04cbedf7b8261f4abbb5c3bed9e(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f39b1d8aef7ac70a09f916fbd39c6c4337e2e11c5b066cb8d05a21924d74087(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7652c5482dd4ddb5137cd900c3e383d1b5ebf284556e298d51a5a74a1c131c4(
    value: typing.Optional[jsii.Number],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17b2bbf0364b81d1c2b9490f1b796c274993cfe7db3c9deb1b75289ee8da2189(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c15d4dca4b52bdd66460a53be92235ce0b0b415a60ac44286ac8757cb331f31(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8594ba50455e3fbccd4914a753218dfb030dd68bad9c7f02837c4e65e385d136(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb7d23926ec36ea0c297ca8492f5ddfb667439579d424d6a4e79602a727a4938(
    value: typing.Optional[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6594c2e8b0654c0173e1dfaf92b321088509417e3a14af046aa974b6a957424(
    *,
    alias: typing.Optional[builtins.str] = None,
    api_endpoint: typing.Optional[builtins.str] = None,
    http_retry_max: typing.Optional[jsii.Number] = None,
    http_retry_wait_max: typing.Optional[jsii.Number] = None,
    http_retry_wait_min: typing.Optional[jsii.Number] = None,
    requests_per_second: typing.Optional[jsii.Number] = None,
    spaces_access_id: typing.Optional[builtins.str] = None,
    spaces_endpoint: typing.Optional[builtins.str] = None,
    spaces_secret_key: typing.Optional[builtins.str] = None,
    token: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass
