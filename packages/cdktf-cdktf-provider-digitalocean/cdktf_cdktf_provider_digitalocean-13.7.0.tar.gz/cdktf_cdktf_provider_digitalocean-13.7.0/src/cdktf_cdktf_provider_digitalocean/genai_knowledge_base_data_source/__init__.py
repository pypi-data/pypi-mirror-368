r'''
# `digitalocean_genai_knowledge_base_data_source`

Refer to the Terraform Registry for docs: [`digitalocean_genai_knowledge_base_data_source`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source).
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


class GenaiKnowledgeBaseDataSource(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBaseDataSource.GenaiKnowledgeBaseDataSource",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source digitalocean_genai_knowledge_base_data_source}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        knowledge_base_uuid: builtins.str,
        id: typing.Optional[builtins.str] = None,
        spaces_data_source: typing.Optional[typing.Union["GenaiKnowledgeBaseDataSourceSpacesDataSource", typing.Dict[builtins.str, typing.Any]]] = None,
        web_crawler_data_source: typing.Optional[typing.Union["GenaiKnowledgeBaseDataSourceWebCrawlerDataSource", typing.Dict[builtins.str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source digitalocean_genai_knowledge_base_data_source} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param knowledge_base_uuid: UUID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#knowledge_base_uuid GenaiKnowledgeBaseDataSource#knowledge_base_uuid}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#id GenaiKnowledgeBaseDataSource#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param spaces_data_source: spaces_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#spaces_data_source GenaiKnowledgeBaseDataSource#spaces_data_source}
        :param web_crawler_data_source: web_crawler_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#web_crawler_data_source GenaiKnowledgeBaseDataSource#web_crawler_data_source}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__724a69e25d9866da01b58d77af22c9dd77432c0dcc0a9198260547f656c41ad1)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GenaiKnowledgeBaseDataSourceConfig(
            knowledge_base_uuid=knowledge_base_uuid,
            id=id,
            spaces_data_source=spaces_data_source,
            web_crawler_data_source=web_crawler_data_source,
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
        '''Generates CDKTF code for importing a GenaiKnowledgeBaseDataSource resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GenaiKnowledgeBaseDataSource to import.
        :param import_from_id: The id of the existing GenaiKnowledgeBaseDataSource that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GenaiKnowledgeBaseDataSource to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9acb641f21856b4d07242414990ae607cc2163ce19b482ce850364f97ebe4b89)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putSpacesDataSource")
    def put_spaces_data_source(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        item_path: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: The name of the Spaces bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#bucket_name GenaiKnowledgeBaseDataSource#bucket_name}
        :param item_path: The path to the item in the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#item_path GenaiKnowledgeBaseDataSource#item_path}
        :param region: The region of the Spaces bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#region GenaiKnowledgeBaseDataSource#region}
        '''
        value = GenaiKnowledgeBaseDataSourceSpacesDataSource(
            bucket_name=bucket_name, item_path=item_path, region=region
        )

        return typing.cast(None, jsii.invoke(self, "putSpacesDataSource", [value]))

    @jsii.member(jsii_name="putWebCrawlerDataSource")
    def put_web_crawler_data_source(
        self,
        *,
        base_url: typing.Optional[builtins.str] = None,
        crawling_option: typing.Optional[builtins.str] = None,
        embed_media: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param base_url: The base URL to crawl. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#base_url GenaiKnowledgeBaseDataSource#base_url}
        :param crawling_option: Options for specifying how URLs found on pages should be handled. - UNKNOWN: Default unknown value - SCOPED: Only include the base URL. - PATH: Crawl the base URL and linked pages within the URL path. - DOMAIN: Crawl the base URL and linked pages within the same domain. - SUBDOMAINS: Crawl the base URL and linked pages for any subdomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#crawling_option GenaiKnowledgeBaseDataSource#crawling_option}
        :param embed_media: Whether to embed media content. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#embed_media GenaiKnowledgeBaseDataSource#embed_media}
        '''
        value = GenaiKnowledgeBaseDataSourceWebCrawlerDataSource(
            base_url=base_url, crawling_option=crawling_option, embed_media=embed_media
        )

        return typing.cast(None, jsii.invoke(self, "putWebCrawlerDataSource", [value]))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetSpacesDataSource")
    def reset_spaces_data_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpacesDataSource", []))

    @jsii.member(jsii_name="resetWebCrawlerDataSource")
    def reset_web_crawler_data_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebCrawlerDataSource", []))

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
    @jsii.member(jsii_name="spacesDataSource")
    def spaces_data_source(
        self,
    ) -> "GenaiKnowledgeBaseDataSourceSpacesDataSourceOutputReference":
        return typing.cast("GenaiKnowledgeBaseDataSourceSpacesDataSourceOutputReference", jsii.get(self, "spacesDataSource"))

    @builtins.property
    @jsii.member(jsii_name="webCrawlerDataSource")
    def web_crawler_data_source(
        self,
    ) -> "GenaiKnowledgeBaseDataSourceWebCrawlerDataSourceOutputReference":
        return typing.cast("GenaiKnowledgeBaseDataSourceWebCrawlerDataSourceOutputReference", jsii.get(self, "webCrawlerDataSource"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseUuidInput")
    def knowledge_base_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "knowledgeBaseUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="spacesDataSourceInput")
    def spaces_data_source_input(
        self,
    ) -> typing.Optional["GenaiKnowledgeBaseDataSourceSpacesDataSource"]:
        return typing.cast(typing.Optional["GenaiKnowledgeBaseDataSourceSpacesDataSource"], jsii.get(self, "spacesDataSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="webCrawlerDataSourceInput")
    def web_crawler_data_source_input(
        self,
    ) -> typing.Optional["GenaiKnowledgeBaseDataSourceWebCrawlerDataSource"]:
        return typing.cast(typing.Optional["GenaiKnowledgeBaseDataSourceWebCrawlerDataSource"], jsii.get(self, "webCrawlerDataSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__64ac00fba6bc37a6a32d8abb456cf148f252532cbcd5ac81ce558e7563c0db5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseUuid")
    def knowledge_base_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseUuid"))

    @knowledge_base_uuid.setter
    def knowledge_base_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4ad25c1aa4d19919fd49714f78bae9cfe67c2a9ed4068c00c44f5dfc1ac3aee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knowledgeBaseUuid", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBaseDataSource.GenaiKnowledgeBaseDataSourceConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "knowledge_base_uuid": "knowledgeBaseUuid",
        "id": "id",
        "spaces_data_source": "spacesDataSource",
        "web_crawler_data_source": "webCrawlerDataSource",
    },
)
class GenaiKnowledgeBaseDataSourceConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        knowledge_base_uuid: builtins.str,
        id: typing.Optional[builtins.str] = None,
        spaces_data_source: typing.Optional[typing.Union["GenaiKnowledgeBaseDataSourceSpacesDataSource", typing.Dict[builtins.str, typing.Any]]] = None,
        web_crawler_data_source: typing.Optional[typing.Union["GenaiKnowledgeBaseDataSourceWebCrawlerDataSource", typing.Dict[builtins.str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param knowledge_base_uuid: UUID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#knowledge_base_uuid GenaiKnowledgeBaseDataSource#knowledge_base_uuid}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#id GenaiKnowledgeBaseDataSource#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param spaces_data_source: spaces_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#spaces_data_source GenaiKnowledgeBaseDataSource#spaces_data_source}
        :param web_crawler_data_source: web_crawler_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#web_crawler_data_source GenaiKnowledgeBaseDataSource#web_crawler_data_source}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(spaces_data_source, dict):
            spaces_data_source = GenaiKnowledgeBaseDataSourceSpacesDataSource(**spaces_data_source)
        if isinstance(web_crawler_data_source, dict):
            web_crawler_data_source = GenaiKnowledgeBaseDataSourceWebCrawlerDataSource(**web_crawler_data_source)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a64a347b3afe46142333438cac99333b74c4d526cdd606bea85757001f607a9)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument knowledge_base_uuid", value=knowledge_base_uuid, expected_type=type_hints["knowledge_base_uuid"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument spaces_data_source", value=spaces_data_source, expected_type=type_hints["spaces_data_source"])
            check_type(argname="argument web_crawler_data_source", value=web_crawler_data_source, expected_type=type_hints["web_crawler_data_source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "knowledge_base_uuid": knowledge_base_uuid,
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
        if id is not None:
            self._values["id"] = id
        if spaces_data_source is not None:
            self._values["spaces_data_source"] = spaces_data_source
        if web_crawler_data_source is not None:
            self._values["web_crawler_data_source"] = web_crawler_data_source

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
    def knowledge_base_uuid(self) -> builtins.str:
        '''UUID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#knowledge_base_uuid GenaiKnowledgeBaseDataSource#knowledge_base_uuid}
        '''
        result = self._values.get("knowledge_base_uuid")
        assert result is not None, "Required property 'knowledge_base_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#id GenaiKnowledgeBaseDataSource#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def spaces_data_source(
        self,
    ) -> typing.Optional["GenaiKnowledgeBaseDataSourceSpacesDataSource"]:
        '''spaces_data_source block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#spaces_data_source GenaiKnowledgeBaseDataSource#spaces_data_source}
        '''
        result = self._values.get("spaces_data_source")
        return typing.cast(typing.Optional["GenaiKnowledgeBaseDataSourceSpacesDataSource"], result)

    @builtins.property
    def web_crawler_data_source(
        self,
    ) -> typing.Optional["GenaiKnowledgeBaseDataSourceWebCrawlerDataSource"]:
        '''web_crawler_data_source block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#web_crawler_data_source GenaiKnowledgeBaseDataSource#web_crawler_data_source}
        '''
        result = self._values.get("web_crawler_data_source")
        return typing.cast(typing.Optional["GenaiKnowledgeBaseDataSourceWebCrawlerDataSource"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDataSourceConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBaseDataSource.GenaiKnowledgeBaseDataSourceSpacesDataSource",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "item_path": "itemPath",
        "region": "region",
    },
)
class GenaiKnowledgeBaseDataSourceSpacesDataSource:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        item_path: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: The name of the Spaces bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#bucket_name GenaiKnowledgeBaseDataSource#bucket_name}
        :param item_path: The path to the item in the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#item_path GenaiKnowledgeBaseDataSource#item_path}
        :param region: The region of the Spaces bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#region GenaiKnowledgeBaseDataSource#region}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25c6cad0377326b7ed7db52f32f4cb5a682c7b95a68d4022ddd8c54b47586045)
            check_type(argname="argument bucket_name", value=bucket_name, expected_type=type_hints["bucket_name"])
            check_type(argname="argument item_path", value=item_path, expected_type=type_hints["item_path"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if bucket_name is not None:
            self._values["bucket_name"] = bucket_name
        if item_path is not None:
            self._values["item_path"] = item_path
        if region is not None:
            self._values["region"] = region

    @builtins.property
    def bucket_name(self) -> typing.Optional[builtins.str]:
        '''The name of the Spaces bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#bucket_name GenaiKnowledgeBaseDataSource#bucket_name}
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def item_path(self) -> typing.Optional[builtins.str]:
        '''The path to the item in the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#item_path GenaiKnowledgeBaseDataSource#item_path}
        '''
        result = self._values.get("item_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The region of the Spaces bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#region GenaiKnowledgeBaseDataSource#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDataSourceSpacesDataSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseDataSourceSpacesDataSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBaseDataSource.GenaiKnowledgeBaseDataSourceSpacesDataSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa1622c55ec2ee33ede036ac1f7d8d01e5085f444a2dcc7fce4a7096b9c4ece5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBucketName")
    def reset_bucket_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBucketName", []))

    @jsii.member(jsii_name="resetItemPath")
    def reset_item_path(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetItemPath", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @builtins.property
    @jsii.member(jsii_name="bucketNameInput")
    def bucket_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "bucketNameInput"))

    @builtins.property
    @jsii.member(jsii_name="itemPathInput")
    def item_path_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "itemPathInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="bucketName")
    def bucket_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "bucketName"))

    @bucket_name.setter
    def bucket_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9dc912596e09140db7d0b270ba98fcc454e7cb98a108dce44d251b5de1b8cd56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="itemPath")
    def item_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "itemPath"))

    @item_path.setter
    def item_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1feb4b30289131abb25d5408baa9ade4df5780c149e8b994023e9a897a143916)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1ed12d61e648881df7b35463ea8cc0d496a44134a1e6d327f67e0716ce60da8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GenaiKnowledgeBaseDataSourceSpacesDataSource]:
        return typing.cast(typing.Optional[GenaiKnowledgeBaseDataSourceSpacesDataSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GenaiKnowledgeBaseDataSourceSpacesDataSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0543066a70cc67cb7219087e83f3796c0c44702302c17dcb5be78940837f3857)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBaseDataSource.GenaiKnowledgeBaseDataSourceWebCrawlerDataSource",
    jsii_struct_bases=[],
    name_mapping={
        "base_url": "baseUrl",
        "crawling_option": "crawlingOption",
        "embed_media": "embedMedia",
    },
)
class GenaiKnowledgeBaseDataSourceWebCrawlerDataSource:
    def __init__(
        self,
        *,
        base_url: typing.Optional[builtins.str] = None,
        crawling_option: typing.Optional[builtins.str] = None,
        embed_media: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param base_url: The base URL to crawl. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#base_url GenaiKnowledgeBaseDataSource#base_url}
        :param crawling_option: Options for specifying how URLs found on pages should be handled. - UNKNOWN: Default unknown value - SCOPED: Only include the base URL. - PATH: Crawl the base URL and linked pages within the URL path. - DOMAIN: Crawl the base URL and linked pages within the same domain. - SUBDOMAINS: Crawl the base URL and linked pages for any subdomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#crawling_option GenaiKnowledgeBaseDataSource#crawling_option}
        :param embed_media: Whether to embed media content. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#embed_media GenaiKnowledgeBaseDataSource#embed_media}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a9af5e40809339d032359cf681beb246c32c635a8a69a80a41515f3d32c734ac)
            check_type(argname="argument base_url", value=base_url, expected_type=type_hints["base_url"])
            check_type(argname="argument crawling_option", value=crawling_option, expected_type=type_hints["crawling_option"])
            check_type(argname="argument embed_media", value=embed_media, expected_type=type_hints["embed_media"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if base_url is not None:
            self._values["base_url"] = base_url
        if crawling_option is not None:
            self._values["crawling_option"] = crawling_option
        if embed_media is not None:
            self._values["embed_media"] = embed_media

    @builtins.property
    def base_url(self) -> typing.Optional[builtins.str]:
        '''The base URL to crawl.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#base_url GenaiKnowledgeBaseDataSource#base_url}
        '''
        result = self._values.get("base_url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def crawling_option(self) -> typing.Optional[builtins.str]:
        '''Options for specifying how URLs found on pages should be handled.

        - UNKNOWN: Default unknown value
        - SCOPED: Only include the base URL.
        - PATH: Crawl the base URL and linked pages within the URL path.
        - DOMAIN: Crawl the base URL and linked pages within the same domain.
        - SUBDOMAINS: Crawl the base URL and linked pages for any subdomain.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#crawling_option GenaiKnowledgeBaseDataSource#crawling_option}
        '''
        result = self._values.get("crawling_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embed_media(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to embed media content.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base_data_source#embed_media GenaiKnowledgeBaseDataSource#embed_media}
        '''
        result = self._values.get("embed_media")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDataSourceWebCrawlerDataSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseDataSourceWebCrawlerDataSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBaseDataSource.GenaiKnowledgeBaseDataSourceWebCrawlerDataSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da92524f416d9c5a1f3d19f9831e90163587cab1a486d63d451b5170132162cc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetBaseUrl")
    def reset_base_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBaseUrl", []))

    @jsii.member(jsii_name="resetCrawlingOption")
    def reset_crawling_option(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCrawlingOption", []))

    @jsii.member(jsii_name="resetEmbedMedia")
    def reset_embed_media(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbedMedia", []))

    @builtins.property
    @jsii.member(jsii_name="baseUrlInput")
    def base_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "baseUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="crawlingOptionInput")
    def crawling_option_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "crawlingOptionInput"))

    @builtins.property
    @jsii.member(jsii_name="embedMediaInput")
    def embed_media_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "embedMediaInput"))

    @builtins.property
    @jsii.member(jsii_name="baseUrl")
    def base_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "baseUrl"))

    @base_url.setter
    def base_url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c390ffa165cc11ab2ab3ab78ae1244a1b20eb2e72010475389ea1c0c7c533ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crawlingOption")
    def crawling_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crawlingOption"))

    @crawling_option.setter
    def crawling_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e60a16c28ab976eb7cb879ed7b63b94bea8f904caddd2e1a32e2ebefa16fb4a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "crawlingOption", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="embedMedia")
    def embed_media(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "embedMedia"))

    @embed_media.setter
    def embed_media(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b61b6809d1c2cacfc10f7420915de9a9eff8c98fb291d716a4b2ff0107acfc6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embedMedia", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GenaiKnowledgeBaseDataSourceWebCrawlerDataSource]:
        return typing.cast(typing.Optional[GenaiKnowledgeBaseDataSourceWebCrawlerDataSource], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GenaiKnowledgeBaseDataSourceWebCrawlerDataSource],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8d3db244fe5da94b4d9480c892f606954a015c6f8a9f116f74cdb6896b4d1364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GenaiKnowledgeBaseDataSource",
    "GenaiKnowledgeBaseDataSourceConfig",
    "GenaiKnowledgeBaseDataSourceSpacesDataSource",
    "GenaiKnowledgeBaseDataSourceSpacesDataSourceOutputReference",
    "GenaiKnowledgeBaseDataSourceWebCrawlerDataSource",
    "GenaiKnowledgeBaseDataSourceWebCrawlerDataSourceOutputReference",
]

publication.publish()

def _typecheckingstub__724a69e25d9866da01b58d77af22c9dd77432c0dcc0a9198260547f656c41ad1(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    knowledge_base_uuid: builtins.str,
    id: typing.Optional[builtins.str] = None,
    spaces_data_source: typing.Optional[typing.Union[GenaiKnowledgeBaseDataSourceSpacesDataSource, typing.Dict[builtins.str, typing.Any]]] = None,
    web_crawler_data_source: typing.Optional[typing.Union[GenaiKnowledgeBaseDataSourceWebCrawlerDataSource, typing.Dict[builtins.str, typing.Any]]] = None,
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

def _typecheckingstub__9acb641f21856b4d07242414990ae607cc2163ce19b482ce850364f97ebe4b89(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__64ac00fba6bc37a6a32d8abb456cf148f252532cbcd5ac81ce558e7563c0db5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4ad25c1aa4d19919fd49714f78bae9cfe67c2a9ed4068c00c44f5dfc1ac3aee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a64a347b3afe46142333438cac99333b74c4d526cdd606bea85757001f607a9(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    knowledge_base_uuid: builtins.str,
    id: typing.Optional[builtins.str] = None,
    spaces_data_source: typing.Optional[typing.Union[GenaiKnowledgeBaseDataSourceSpacesDataSource, typing.Dict[builtins.str, typing.Any]]] = None,
    web_crawler_data_source: typing.Optional[typing.Union[GenaiKnowledgeBaseDataSourceWebCrawlerDataSource, typing.Dict[builtins.str, typing.Any]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25c6cad0377326b7ed7db52f32f4cb5a682c7b95a68d4022ddd8c54b47586045(
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    item_path: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1622c55ec2ee33ede036ac1f7d8d01e5085f444a2dcc7fce4a7096b9c4ece5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dc912596e09140db7d0b270ba98fcc454e7cb98a108dce44d251b5de1b8cd56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1feb4b30289131abb25d5408baa9ade4df5780c149e8b994023e9a897a143916(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1ed12d61e648881df7b35463ea8cc0d496a44134a1e6d327f67e0716ce60da8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0543066a70cc67cb7219087e83f3796c0c44702302c17dcb5be78940837f3857(
    value: typing.Optional[GenaiKnowledgeBaseDataSourceSpacesDataSource],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a9af5e40809339d032359cf681beb246c32c635a8a69a80a41515f3d32c734ac(
    *,
    base_url: typing.Optional[builtins.str] = None,
    crawling_option: typing.Optional[builtins.str] = None,
    embed_media: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da92524f416d9c5a1f3d19f9831e90163587cab1a486d63d451b5170132162cc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c390ffa165cc11ab2ab3ab78ae1244a1b20eb2e72010475389ea1c0c7c533ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e60a16c28ab976eb7cb879ed7b63b94bea8f904caddd2e1a32e2ebefa16fb4a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b61b6809d1c2cacfc10f7420915de9a9eff8c98fb291d716a4b2ff0107acfc6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8d3db244fe5da94b4d9480c892f606954a015c6f8a9f116f74cdb6896b4d1364(
    value: typing.Optional[GenaiKnowledgeBaseDataSourceWebCrawlerDataSource],
) -> None:
    """Type checking stubs"""
    pass
