r'''
# `digitalocean_genai_knowledge_base`

Refer to the Terraform Registry for docs: [`digitalocean_genai_knowledge_base`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base).
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


class GenaiKnowledgeBase(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBase",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base digitalocean_genai_knowledge_base}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        datasources: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasources", typing.Dict[builtins.str, typing.Any]]]],
        embedding_model_uuid: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        region: builtins.str,
        added_to_agent_at: typing.Optional[builtins.str] = None,
        database_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_indexing_job: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseLastIndexingJob", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        vpc_uuid: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base digitalocean_genai_knowledge_base} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param datasources: datasources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#datasources GenaiKnowledgeBase#datasources}
        :param embedding_model_uuid: The unique identifier of the embedding model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#embedding_model_uuid GenaiKnowledgeBase#embedding_model_uuid}
        :param name: The name of the knowledge base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#name GenaiKnowledgeBase#name}
        :param project_id: The unique identifier of the project to which the knowledge base belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#project_id GenaiKnowledgeBase#project_id}
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#region GenaiKnowledgeBase#region}.
        :param added_to_agent_at: The time when the knowledge base was added to the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#added_to_agent_at GenaiKnowledgeBase#added_to_agent_at}
        :param database_id: The unique identifier of the DigitalOcean OpenSearch database this knowledge base will use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#database_id GenaiKnowledgeBase#database_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#id GenaiKnowledgeBase#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_public: Indicates whether the knowledge base is public or private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#is_public GenaiKnowledgeBase#is_public}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#last_indexing_job GenaiKnowledgeBase#last_indexing_job}
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tags GenaiKnowledgeBase#tags}.
        :param vpc_uuid: The unique identifier of the VPC to which the knowledge base belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#vpc_uuid GenaiKnowledgeBase#vpc_uuid}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f632334af9bbb652f8e52d508c9d3e515d10bef60910b5ae2be4dbc31065c239)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GenaiKnowledgeBaseConfig(
            datasources=datasources,
            embedding_model_uuid=embedding_model_uuid,
            name=name,
            project_id=project_id,
            region=region,
            added_to_agent_at=added_to_agent_at,
            database_id=database_id,
            id=id,
            is_public=is_public,
            last_indexing_job=last_indexing_job,
            tags=tags,
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
        '''Generates CDKTF code for importing a GenaiKnowledgeBase resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GenaiKnowledgeBase to import.
        :param import_from_id: The id of the existing GenaiKnowledgeBase that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GenaiKnowledgeBase to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5258743cafc4cadb7222f195ef1d2832f8fec389076ee8d47c944d96fd29d1be)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putDatasources")
    def put_datasources(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasources", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d09191dbb4f4f8a572fed1cd89e46f6cffb4225a07250a86e1bc27343cf47ae4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDatasources", [value]))

    @jsii.member(jsii_name="putLastIndexingJob")
    def put_last_indexing_job(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseLastIndexingJob", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52eadacba87603f53e347e6fa9f9568d67501700e453c2050b8669e75c751d7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLastIndexingJob", [value]))

    @jsii.member(jsii_name="resetAddedToAgentAt")
    def reset_added_to_agent_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAddedToAgentAt", []))

    @jsii.member(jsii_name="resetDatabaseId")
    def reset_database_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseId", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIsPublic")
    def reset_is_public(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsPublic", []))

    @jsii.member(jsii_name="resetLastIndexingJob")
    def reset_last_indexing_job(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastIndexingJob", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

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
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="datasources")
    def datasources(self) -> "GenaiKnowledgeBaseDatasourcesList":
        return typing.cast("GenaiKnowledgeBaseDatasourcesList", jsii.get(self, "datasources"))

    @builtins.property
    @jsii.member(jsii_name="lastIndexingJob")
    def last_indexing_job(self) -> "GenaiKnowledgeBaseLastIndexingJobList":
        return typing.cast("GenaiKnowledgeBaseLastIndexingJobList", jsii.get(self, "lastIndexingJob"))

    @builtins.property
    @jsii.member(jsii_name="addedToAgentAtInput")
    def added_to_agent_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "addedToAgentAtInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseIdInput")
    def database_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="datasourcesInput")
    def datasources_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasources"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasources"]]], jsii.get(self, "datasourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuidInput")
    def embedding_model_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "embeddingModelUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="isPublicInput")
    def is_public_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isPublicInput"))

    @builtins.property
    @jsii.member(jsii_name="lastIndexingJobInput")
    def last_indexing_job_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseLastIndexingJob"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseLastIndexingJob"]]], jsii.get(self, "lastIndexingJobInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="vpcUuidInput")
    def vpc_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "vpcUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="addedToAgentAt")
    def added_to_agent_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addedToAgentAt"))

    @added_to_agent_at.setter
    def added_to_agent_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7943a409758fb4355ee6100242da4fe5553e02ddb7adbf21402c7514863b9c6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "addedToAgentAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="databaseId")
    def database_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseId"))

    @database_id.setter
    def database_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55aabbacf6fdac9738cb049de9a2583f38fe9112bbdd16e5eae2bde83a4ed12b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuid")
    def embedding_model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelUuid"))

    @embedding_model_uuid.setter
    def embedding_model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f26c8e7332c1dd10dbe9da309690a54c57aaf9cfbb0ebfdcf09d7ecc0ac52503)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingModelUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e31c980b5b916fc5277bf7352feb5892597c6c852bcf1a40cb62ed6fb628637b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isPublic")
    def is_public(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isPublic"))

    @is_public.setter
    def is_public(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3802576b0fadc1c9b4c1c97a5cbb58a003402ad0f9e9ee168405044e850c436)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPublic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__044ae117534fc73e143c4bf6f0da21113f9c4232b29b7cd53756779b1cda8716)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0a64747ce3e0be219f13aa203521481f20eac7eb5dff427d1c02a70154b5263)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0709e8e3857dd70798447936b884327c06b3b3866a2f9ed2bc558d0f4e4b5e75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__feb3619432a8ee9c14515481309fb393e3eabd3af0ea91e4b2a76ea121c7fe43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="vpcUuid")
    def vpc_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "vpcUuid"))

    @vpc_uuid.setter
    def vpc_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a6f97b8ec9f162979bef581bbca51c759f53dfcb8a682b5cf1e6c7f23b8f700b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "vpcUuid", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "datasources": "datasources",
        "embedding_model_uuid": "embeddingModelUuid",
        "name": "name",
        "project_id": "projectId",
        "region": "region",
        "added_to_agent_at": "addedToAgentAt",
        "database_id": "databaseId",
        "id": "id",
        "is_public": "isPublic",
        "last_indexing_job": "lastIndexingJob",
        "tags": "tags",
        "vpc_uuid": "vpcUuid",
    },
)
class GenaiKnowledgeBaseConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        datasources: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasources", typing.Dict[builtins.str, typing.Any]]]],
        embedding_model_uuid: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        region: builtins.str,
        added_to_agent_at: typing.Optional[builtins.str] = None,
        database_id: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_indexing_job: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseLastIndexingJob", typing.Dict[builtins.str, typing.Any]]]]] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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
        :param datasources: datasources block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#datasources GenaiKnowledgeBase#datasources}
        :param embedding_model_uuid: The unique identifier of the embedding model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#embedding_model_uuid GenaiKnowledgeBase#embedding_model_uuid}
        :param name: The name of the knowledge base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#name GenaiKnowledgeBase#name}
        :param project_id: The unique identifier of the project to which the knowledge base belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#project_id GenaiKnowledgeBase#project_id}
        :param region: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#region GenaiKnowledgeBase#region}.
        :param added_to_agent_at: The time when the knowledge base was added to the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#added_to_agent_at GenaiKnowledgeBase#added_to_agent_at}
        :param database_id: The unique identifier of the DigitalOcean OpenSearch database this knowledge base will use. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#database_id GenaiKnowledgeBase#database_id}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#id GenaiKnowledgeBase#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param is_public: Indicates whether the knowledge base is public or private. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#is_public GenaiKnowledgeBase#is_public}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#last_indexing_job GenaiKnowledgeBase#last_indexing_job}
        :param tags: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tags GenaiKnowledgeBase#tags}.
        :param vpc_uuid: The unique identifier of the VPC to which the knowledge base belongs. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#vpc_uuid GenaiKnowledgeBase#vpc_uuid}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3fcbd577e624422b294bee89a99a34dd12493122f70a99bc0c7f07e0fb56d72)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument datasources", value=datasources, expected_type=type_hints["datasources"])
            check_type(argname="argument embedding_model_uuid", value=embedding_model_uuid, expected_type=type_hints["embedding_model_uuid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument added_to_agent_at", value=added_to_agent_at, expected_type=type_hints["added_to_agent_at"])
            check_type(argname="argument database_id", value=database_id, expected_type=type_hints["database_id"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument is_public", value=is_public, expected_type=type_hints["is_public"])
            check_type(argname="argument last_indexing_job", value=last_indexing_job, expected_type=type_hints["last_indexing_job"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument vpc_uuid", value=vpc_uuid, expected_type=type_hints["vpc_uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "datasources": datasources,
            "embedding_model_uuid": embedding_model_uuid,
            "name": name,
            "project_id": project_id,
            "region": region,
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
        if added_to_agent_at is not None:
            self._values["added_to_agent_at"] = added_to_agent_at
        if database_id is not None:
            self._values["database_id"] = database_id
        if id is not None:
            self._values["id"] = id
        if is_public is not None:
            self._values["is_public"] = is_public
        if last_indexing_job is not None:
            self._values["last_indexing_job"] = last_indexing_job
        if tags is not None:
            self._values["tags"] = tags
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
    def datasources(
        self,
    ) -> typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasources"]]:
        '''datasources block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#datasources GenaiKnowledgeBase#datasources}
        '''
        result = self._values.get("datasources")
        assert result is not None, "Required property 'datasources' is missing"
        return typing.cast(typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasources"]], result)

    @builtins.property
    def embedding_model_uuid(self) -> builtins.str:
        '''The unique identifier of the embedding model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#embedding_model_uuid GenaiKnowledgeBase#embedding_model_uuid}
        '''
        result = self._values.get("embedding_model_uuid")
        assert result is not None, "Required property 'embedding_model_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''The name of the knowledge base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#name GenaiKnowledgeBase#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''The unique identifier of the project to which the knowledge base belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#project_id GenaiKnowledgeBase#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#region GenaiKnowledgeBase#region}.'''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def added_to_agent_at(self) -> typing.Optional[builtins.str]:
        '''The time when the knowledge base was added to the agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#added_to_agent_at GenaiKnowledgeBase#added_to_agent_at}
        '''
        result = self._values.get("added_to_agent_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def database_id(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of the DigitalOcean OpenSearch database this knowledge base will use.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#database_id GenaiKnowledgeBase#database_id}
        '''
        result = self._values.get("database_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#id GenaiKnowledgeBase#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates whether the knowledge base is public or private.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#is_public GenaiKnowledgeBase#is_public}
        '''
        result = self._values.get("is_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def last_indexing_job(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseLastIndexingJob"]]]:
        '''last_indexing_job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#last_indexing_job GenaiKnowledgeBase#last_indexing_job}
        '''
        result = self._values.get("last_indexing_job")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseLastIndexingJob"]]], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tags GenaiKnowledgeBase#tags}.'''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def vpc_uuid(self) -> typing.Optional[builtins.str]:
        '''The unique identifier of the VPC to which the knowledge base belongs.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#vpc_uuid GenaiKnowledgeBase#vpc_uuid}
        '''
        result = self._values.get("vpc_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasources",
    jsii_struct_bases=[],
    name_mapping={
        "file_upload_data_source": "fileUploadDataSource",
        "last_indexing_job": "lastIndexingJob",
        "spaces_data_source": "spacesDataSource",
        "uuid": "uuid",
        "web_crawler_data_source": "webCrawlerDataSource",
    },
)
class GenaiKnowledgeBaseDatasources:
    def __init__(
        self,
        *,
        file_upload_data_source: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasourcesFileUploadDataSource", typing.Dict[builtins.str, typing.Any]]]]] = None,
        last_indexing_job: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasourcesLastIndexingJob", typing.Dict[builtins.str, typing.Any]]]]] = None,
        spaces_data_source: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasourcesSpacesDataSource", typing.Dict[builtins.str, typing.Any]]]]] = None,
        uuid: typing.Optional[builtins.str] = None,
        web_crawler_data_source: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param file_upload_data_source: file_upload_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#file_upload_data_source GenaiKnowledgeBase#file_upload_data_source}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#last_indexing_job GenaiKnowledgeBase#last_indexing_job}
        :param spaces_data_source: spaces_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#spaces_data_source GenaiKnowledgeBase#spaces_data_source}
        :param uuid: UUID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#uuid GenaiKnowledgeBase#uuid}
        :param web_crawler_data_source: web_crawler_data_source block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#web_crawler_data_source GenaiKnowledgeBase#web_crawler_data_source}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__031d1b5bbf00f73165daea5016941fff16d093bad24645cb4b972a27cbbe0c5b)
            check_type(argname="argument file_upload_data_source", value=file_upload_data_source, expected_type=type_hints["file_upload_data_source"])
            check_type(argname="argument last_indexing_job", value=last_indexing_job, expected_type=type_hints["last_indexing_job"])
            check_type(argname="argument spaces_data_source", value=spaces_data_source, expected_type=type_hints["spaces_data_source"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument web_crawler_data_source", value=web_crawler_data_source, expected_type=type_hints["web_crawler_data_source"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if file_upload_data_source is not None:
            self._values["file_upload_data_source"] = file_upload_data_source
        if last_indexing_job is not None:
            self._values["last_indexing_job"] = last_indexing_job
        if spaces_data_source is not None:
            self._values["spaces_data_source"] = spaces_data_source
        if uuid is not None:
            self._values["uuid"] = uuid
        if web_crawler_data_source is not None:
            self._values["web_crawler_data_source"] = web_crawler_data_source

    @builtins.property
    def file_upload_data_source(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesFileUploadDataSource"]]]:
        '''file_upload_data_source block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#file_upload_data_source GenaiKnowledgeBase#file_upload_data_source}
        '''
        result = self._values.get("file_upload_data_source")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesFileUploadDataSource"]]], result)

    @builtins.property
    def last_indexing_job(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesLastIndexingJob"]]]:
        '''last_indexing_job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#last_indexing_job GenaiKnowledgeBase#last_indexing_job}
        '''
        result = self._values.get("last_indexing_job")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesLastIndexingJob"]]], result)

    @builtins.property
    def spaces_data_source(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesSpacesDataSource"]]]:
        '''spaces_data_source block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#spaces_data_source GenaiKnowledgeBase#spaces_data_source}
        '''
        result = self._values.get("spaces_data_source")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesSpacesDataSource"]]], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#uuid GenaiKnowledgeBase#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def web_crawler_data_source(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource"]]]:
        '''web_crawler_data_source block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#web_crawler_data_source GenaiKnowledgeBase#web_crawler_data_source}
        '''
        result = self._values.get("web_crawler_data_source")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDatasources(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesFileUploadDataSource",
    jsii_struct_bases=[],
    name_mapping={
        "original_file_name": "originalFileName",
        "size_in_bytes": "sizeInBytes",
        "stored_object_key": "storedObjectKey",
    },
)
class GenaiKnowledgeBaseDatasourcesFileUploadDataSource:
    def __init__(
        self,
        *,
        original_file_name: typing.Optional[builtins.str] = None,
        size_in_bytes: typing.Optional[builtins.str] = None,
        stored_object_key: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param original_file_name: The original name of the uploaded file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#original_file_name GenaiKnowledgeBase#original_file_name}
        :param size_in_bytes: The size of the file in bytes. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#size_in_bytes GenaiKnowledgeBase#size_in_bytes}
        :param stored_object_key: The stored object key for the file. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#stored_object_key GenaiKnowledgeBase#stored_object_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e21b8753a9c51e185ee1cf9a1a69565a4ce01230cf004ce438bfd08a78f06637)
            check_type(argname="argument original_file_name", value=original_file_name, expected_type=type_hints["original_file_name"])
            check_type(argname="argument size_in_bytes", value=size_in_bytes, expected_type=type_hints["size_in_bytes"])
            check_type(argname="argument stored_object_key", value=stored_object_key, expected_type=type_hints["stored_object_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if original_file_name is not None:
            self._values["original_file_name"] = original_file_name
        if size_in_bytes is not None:
            self._values["size_in_bytes"] = size_in_bytes
        if stored_object_key is not None:
            self._values["stored_object_key"] = stored_object_key

    @builtins.property
    def original_file_name(self) -> typing.Optional[builtins.str]:
        '''The original name of the uploaded file.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#original_file_name GenaiKnowledgeBase#original_file_name}
        '''
        result = self._values.get("original_file_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def size_in_bytes(self) -> typing.Optional[builtins.str]:
        '''The size of the file in bytes.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#size_in_bytes GenaiKnowledgeBase#size_in_bytes}
        '''
        result = self._values.get("size_in_bytes")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def stored_object_key(self) -> typing.Optional[builtins.str]:
        '''The stored object key for the file.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#stored_object_key GenaiKnowledgeBase#stored_object_key}
        '''
        result = self._values.get("stored_object_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDatasourcesFileUploadDataSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseDatasourcesFileUploadDataSourceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesFileUploadDataSourceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__844d44a9b8be9c1b312e001dd894aff17a64408617bce4121cfdde9f03f21bad)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiKnowledgeBaseDatasourcesFileUploadDataSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70e3fa41ef747f454551ab5fefbc1dab94414f9aa7d99f86ff0902204ce1fa1d)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiKnowledgeBaseDatasourcesFileUploadDataSourceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e30c68a9d105073d3f9b20a2e2390845b4d191c0d7aca31814fc0fed71e053b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__47cfa21e7c6f96a07dc7f9a1c1d3ab24411830a750eaf59e0663fb2cc5031b5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0255eb0457be8629d47056eb82e274f56b01b623da36cac45a4e5ce9bbf8b5a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecdf9eae3627f767b62228d00c2f0426c2be2ad0d6ff426289802b9c8cad4135)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseDatasourcesFileUploadDataSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesFileUploadDataSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__094592e0f1b6e61de612badbb04bd82727d8f5f87c7540f44d0eec20946e5e0f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetOriginalFileName")
    def reset_original_file_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOriginalFileName", []))

    @jsii.member(jsii_name="resetSizeInBytes")
    def reset_size_in_bytes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSizeInBytes", []))

    @jsii.member(jsii_name="resetStoredObjectKey")
    def reset_stored_object_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStoredObjectKey", []))

    @builtins.property
    @jsii.member(jsii_name="originalFileNameInput")
    def original_file_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "originalFileNameInput"))

    @builtins.property
    @jsii.member(jsii_name="sizeInBytesInput")
    def size_in_bytes_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sizeInBytesInput"))

    @builtins.property
    @jsii.member(jsii_name="storedObjectKeyInput")
    def stored_object_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "storedObjectKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="originalFileName")
    def original_file_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "originalFileName"))

    @original_file_name.setter
    def original_file_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71862c2dee45a52a8da9d6e94e85c3d577d012e465e952555d7bd379ac693db9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "originalFileName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sizeInBytes")
    def size_in_bytes(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sizeInBytes"))

    @size_in_bytes.setter
    def size_in_bytes(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cf8a5f0de75d4837b3673fd7a0901e5121be52cd145649d598c068534d995fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sizeInBytes", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="storedObjectKey")
    def stored_object_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "storedObjectKey"))

    @stored_object_key.setter
    def stored_object_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad5cc9b600c161ae2f7f9d50dd6fb0380b08da1a1c8ec477574ee5e12b87311e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "storedObjectKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesFileUploadDataSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesFileUploadDataSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66b46c92cef4017eba6fdd7299136ece574f31901fe22cc61858a04e3c335e1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesLastIndexingJob",
    jsii_struct_bases=[],
    name_mapping={
        "completed_datasources": "completedDatasources",
        "data_source_uuids": "dataSourceUuids",
        "phase": "phase",
        "tokens": "tokens",
        "total_datasources": "totalDatasources",
        "uuid": "uuid",
    },
)
class GenaiKnowledgeBaseDatasourcesLastIndexingJob:
    def __init__(
        self,
        *,
        completed_datasources: typing.Optional[jsii.Number] = None,
        data_source_uuids: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase: typing.Optional[builtins.str] = None,
        tokens: typing.Optional[jsii.Number] = None,
        total_datasources: typing.Optional[jsii.Number] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#completed_datasources GenaiKnowledgeBase#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#data_source_uuids GenaiKnowledgeBase#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#phase GenaiKnowledgeBase#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tokens GenaiKnowledgeBase#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#total_datasources GenaiKnowledgeBase#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#uuid GenaiKnowledgeBase#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8105cbd69e07bd94eb6aab60adb58073d16bba6b8dd49c71629f6df892ad31a)
            check_type(argname="argument completed_datasources", value=completed_datasources, expected_type=type_hints["completed_datasources"])
            check_type(argname="argument data_source_uuids", value=data_source_uuids, expected_type=type_hints["data_source_uuids"])
            check_type(argname="argument phase", value=phase, expected_type=type_hints["phase"])
            check_type(argname="argument tokens", value=tokens, expected_type=type_hints["tokens"])
            check_type(argname="argument total_datasources", value=total_datasources, expected_type=type_hints["total_datasources"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if completed_datasources is not None:
            self._values["completed_datasources"] = completed_datasources
        if data_source_uuids is not None:
            self._values["data_source_uuids"] = data_source_uuids
        if phase is not None:
            self._values["phase"] = phase
        if tokens is not None:
            self._values["tokens"] = tokens
        if total_datasources is not None:
            self._values["total_datasources"] = total_datasources
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def completed_datasources(self) -> typing.Optional[jsii.Number]:
        '''Number of completed datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#completed_datasources GenaiKnowledgeBase#completed_datasources}
        '''
        result = self._values.get("completed_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_source_uuids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Datasource UUIDs for the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#data_source_uuids GenaiKnowledgeBase#data_source_uuids}
        '''
        result = self._values.get("data_source_uuids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase(self) -> typing.Optional[builtins.str]:
        '''Phase of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#phase GenaiKnowledgeBase#phase}
        '''
        result = self._values.get("phase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Number of tokens processed in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tokens GenaiKnowledgeBase#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_datasources(self) -> typing.Optional[jsii.Number]:
        '''Total number of datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#total_datasources GenaiKnowledgeBase#total_datasources}
        '''
        result = self._values.get("total_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID  of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#uuid GenaiKnowledgeBase#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDatasourcesLastIndexingJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseDatasourcesLastIndexingJobList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesLastIndexingJobList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4d96bb5db1ce6c1299c5845a638a99d005b232a99c070ea4c664787fed70c546)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiKnowledgeBaseDatasourcesLastIndexingJobOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c466dc6662c7dd8aa433994575ddb2a36804f877755a9809177148ce0e2aed18)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiKnowledgeBaseDatasourcesLastIndexingJobOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9db6061aa26d87b8acef8513ff99621bb2de6962a07a82bf5041b4dcfee44037)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d73eb68582efd0037cd4a8166815715df5f1447d13239b0002660876937e0b0f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__293af08205b5e996bd546f7c9dd9068579e14fbfb68970957223174bf1280a82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesLastIndexingJob]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesLastIndexingJob]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesLastIndexingJob]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27b19dcd9e292e95ab6f2f5dd90784fddf3f0ff445e0d2cf0745200d242c49a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseDatasourcesLastIndexingJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesLastIndexingJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7434b6735941c2931059c7ee7b3f3fcabc82afb75a3fdb07df9ca6faea15bb3f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCompletedDatasources")
    def reset_completed_datasources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompletedDatasources", []))

    @jsii.member(jsii_name="resetDataSourceUuids")
    def reset_data_source_uuids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceUuids", []))

    @jsii.member(jsii_name="resetPhase")
    def reset_phase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase", []))

    @jsii.member(jsii_name="resetTokens")
    def reset_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokens", []))

    @jsii.member(jsii_name="resetTotalDatasources")
    def reset_total_datasources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalDatasources", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="finishedAt")
    def finished_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finishedAt"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseUuid")
    def knowledge_base_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseUuid"))

    @builtins.property
    @jsii.member(jsii_name="startedAt")
    def started_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="completedDatasourcesInput")
    def completed_datasources_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "completedDatasourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuidsInput")
    def data_source_uuids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataSourceUuidsInput"))

    @builtins.property
    @jsii.member(jsii_name="phaseInput")
    def phase_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "phaseInput"))

    @builtins.property
    @jsii.member(jsii_name="tokensInput")
    def tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokensInput"))

    @builtins.property
    @jsii.member(jsii_name="totalDatasourcesInput")
    def total_datasources_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalDatasourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="completedDatasources")
    def completed_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "completedDatasources"))

    @completed_datasources.setter
    def completed_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__67e67d29b0ef95a179245dcedccd420728112968770cb910ed4d6d66cfc0b3db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuids")
    def data_source_uuids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataSourceUuids"))

    @data_source_uuids.setter
    def data_source_uuids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b7364d82e8cd3c949f92993b9e2560808ce9fde42cb5a22b5e40cf803ba1ac2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceUuids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase")
    def phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phase"))

    @phase.setter
    def phase(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca13642c678c12c69201fd880b9da8633a8e80d0eedb7924b35b8c4585110982)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04a83c34a43e9aa8d4cbfcc7bd93dc01e167e9c228cbbdc2344359ef61af7249)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDatasources")
    def total_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalDatasources"))

    @total_datasources.setter
    def total_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b8b664fcd0201cfa537bf5a5ba5e1e31232510ee8ad9175b5a4dc77c45e0648)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f38802cd75731a4a2281a69e27145260cba7a9b60a3e51ba53f5594e74da71a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesLastIndexingJob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesLastIndexingJob]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesLastIndexingJob]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32ad3ccb255670c059ddbc6b4748cb1abf001cd89bed5bea2e112a1e26945b44)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseDatasourcesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72908b977bbfe2d49017de819d1207c070c7170c7e4758b14556e6dc50f6ffc5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiKnowledgeBaseDatasourcesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a3ff0ab11f143ff195cc4cc2e5ecb30e09c5a3d876c4330901422c3a0fe12f0)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiKnowledgeBaseDatasourcesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f84df635bc1d15ac3010dcb6004dfb85dff6a5012583694480daef797304deea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f975f81abd5da7b1da28f74f1d444b7055aca26ada8782387f088f89df5dca47)
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
            type_hints = typing.get_type_hints(_typecheckingstub__084df66d9e717ad2d7780fd7cc5ac053f3af240170e257d782e2f5554f977b06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasources]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasources]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasources]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__afac679ab6ba8ecb3c947bfa9ed55211d2387468739011bb1bfb1794b0d9afca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseDatasourcesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ee64a6d75c8abc92610f4d0b94b71079e66a21979cc480ca82c860a2f6416551)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putFileUploadDataSource")
    def put_file_upload_data_source(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesFileUploadDataSource, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13fd1fa7bb2226e5319dfc2527bddebd2dbc618cdc731090a5ad9ea3942ae100)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFileUploadDataSource", [value]))

    @jsii.member(jsii_name="putLastIndexingJob")
    def put_last_indexing_job(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a6d56552a3223a3b5b9dfc126e6dfe0218fd5ca9f23fc8792f08b23e30a022a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putLastIndexingJob", [value]))

    @jsii.member(jsii_name="putSpacesDataSource")
    def put_spaces_data_source(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasourcesSpacesDataSource", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__21691ad4b16ce659e354de3da46f32698e1cf3cd99968928623ddfb9044c99e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putSpacesDataSource", [value]))

    @jsii.member(jsii_name="putWebCrawlerDataSource")
    def put_web_crawler_data_source(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6076a1108d1f529f3d3fabbfbb0f59f75519c6165278d977b012a0cf5503c05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putWebCrawlerDataSource", [value]))

    @jsii.member(jsii_name="resetFileUploadDataSource")
    def reset_file_upload_data_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFileUploadDataSource", []))

    @jsii.member(jsii_name="resetLastIndexingJob")
    def reset_last_indexing_job(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastIndexingJob", []))

    @jsii.member(jsii_name="resetSpacesDataSource")
    def reset_spaces_data_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSpacesDataSource", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @jsii.member(jsii_name="resetWebCrawlerDataSource")
    def reset_web_crawler_data_source(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWebCrawlerDataSource", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="fileUploadDataSource")
    def file_upload_data_source(
        self,
    ) -> GenaiKnowledgeBaseDatasourcesFileUploadDataSourceList:
        return typing.cast(GenaiKnowledgeBaseDatasourcesFileUploadDataSourceList, jsii.get(self, "fileUploadDataSource"))

    @builtins.property
    @jsii.member(jsii_name="lastIndexingJob")
    def last_indexing_job(self) -> GenaiKnowledgeBaseDatasourcesLastIndexingJobList:
        return typing.cast(GenaiKnowledgeBaseDatasourcesLastIndexingJobList, jsii.get(self, "lastIndexingJob"))

    @builtins.property
    @jsii.member(jsii_name="spacesDataSource")
    def spaces_data_source(self) -> "GenaiKnowledgeBaseDatasourcesSpacesDataSourceList":
        return typing.cast("GenaiKnowledgeBaseDatasourcesSpacesDataSourceList", jsii.get(self, "spacesDataSource"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="webCrawlerDataSource")
    def web_crawler_data_source(
        self,
    ) -> "GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceList":
        return typing.cast("GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceList", jsii.get(self, "webCrawlerDataSource"))

    @builtins.property
    @jsii.member(jsii_name="fileUploadDataSourceInput")
    def file_upload_data_source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]], jsii.get(self, "fileUploadDataSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="lastIndexingJobInput")
    def last_indexing_job_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesLastIndexingJob]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesLastIndexingJob]]], jsii.get(self, "lastIndexingJobInput"))

    @builtins.property
    @jsii.member(jsii_name="spacesDataSourceInput")
    def spaces_data_source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesSpacesDataSource"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesSpacesDataSource"]]], jsii.get(self, "spacesDataSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="webCrawlerDataSourceInput")
    def web_crawler_data_source_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource"]]], jsii.get(self, "webCrawlerDataSourceInput"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22d60634bca820b7c25cdb82a420d477b34c821d33a4e3e404000263d5327700)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasources]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasources]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasources]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__323af9ba27142f0afd700b2ede546ee851a49a193b9040d75236426c591501b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesSpacesDataSource",
    jsii_struct_bases=[],
    name_mapping={
        "bucket_name": "bucketName",
        "item_path": "itemPath",
        "region": "region",
    },
)
class GenaiKnowledgeBaseDatasourcesSpacesDataSource:
    def __init__(
        self,
        *,
        bucket_name: typing.Optional[builtins.str] = None,
        item_path: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param bucket_name: The name of the Spaces bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#bucket_name GenaiKnowledgeBase#bucket_name}
        :param item_path: The path to the item in the bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#item_path GenaiKnowledgeBase#item_path}
        :param region: The region of the Spaces bucket. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#region GenaiKnowledgeBase#region}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6f8ff6b9f3e491a2aafeb70fb14a4ed5ba525f545c0a0b1fd96d5f093848a72)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#bucket_name GenaiKnowledgeBase#bucket_name}
        '''
        result = self._values.get("bucket_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def item_path(self) -> typing.Optional[builtins.str]:
        '''The path to the item in the bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#item_path GenaiKnowledgeBase#item_path}
        '''
        result = self._values.get("item_path")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''The region of the Spaces bucket.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#region GenaiKnowledgeBase#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDatasourcesSpacesDataSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseDatasourcesSpacesDataSourceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesSpacesDataSourceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ee620cf00778a6d979e5d66e130c44f68a89311d95fdd7dee286eb8fee4fc98)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiKnowledgeBaseDatasourcesSpacesDataSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__665865587d3309d793899f96384db1f4c3e3f820bd2ebb85312a9be74a6d8c61)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiKnowledgeBaseDatasourcesSpacesDataSourceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__528efea3138abc85795818e74ae02cc3a1159a28ed6a18ec805b7055c0bc9694)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ecd8cd6a93f2f4b47362b3776b162f16ddf4913b3fe287d3a6c25672233065bd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__490db655b761a3b687a80d54bc9274dae9d8362c143c65dd36509b445ec98356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesSpacesDataSource]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesSpacesDataSource]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesSpacesDataSource]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d064a60686cf43607dd3218a80bc6d9ffe8c138b007d6456e2f8c1812472f9c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseDatasourcesSpacesDataSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesSpacesDataSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__dd6b089ac4725fe1e66345a05c26cef3009d6a8d6dd8a7469bd694a580d33749)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__95663de7ce750f8b29aaf0c0935cb587384e5f783e3bd1c6886797e48f00f9b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bucketName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="itemPath")
    def item_path(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "itemPath"))

    @item_path.setter
    def item_path(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50461b2a7f577a2dbe974f79203311f56bb63265fbcac7dbc2b6855904aa0730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "itemPath", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74fb9f54c5bd7b3a7eeb495d7d12a913dd5e97396f6bef82298915dfe09a3bd8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesSpacesDataSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesSpacesDataSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesSpacesDataSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2de04e485ef365be3c46a556218b96c790d249bda97cf1cf395b9968e4cd87aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource",
    jsii_struct_bases=[],
    name_mapping={
        "base_url": "baseUrl",
        "crawling_option": "crawlingOption",
        "embed_media": "embedMedia",
    },
)
class GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource:
    def __init__(
        self,
        *,
        base_url: typing.Optional[builtins.str] = None,
        crawling_option: typing.Optional[builtins.str] = None,
        embed_media: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param base_url: The base URL to crawl. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#base_url GenaiKnowledgeBase#base_url}
        :param crawling_option: Options for specifying how URLs found on pages should be handled. - UNKNOWN: Default unknown value - SCOPED: Only include the base URL. - PATH: Crawl the base URL and linked pages within the URL path. - DOMAIN: Crawl the base URL and linked pages within the same domain. - SUBDOMAINS: Crawl the base URL and linked pages for any subdomain. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#crawling_option GenaiKnowledgeBase#crawling_option}
        :param embed_media: Whether to embed media content. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#embed_media GenaiKnowledgeBase#embed_media}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e42415897ddf555b418e6a53089c6eb1005a8522d095ff10a1b985af4593799)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#base_url GenaiKnowledgeBase#base_url}
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#crawling_option GenaiKnowledgeBase#crawling_option}
        '''
        result = self._values.get("crawling_option")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embed_media(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Whether to embed media content.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#embed_media GenaiKnowledgeBase#embed_media}
        '''
        result = self._values.get("embed_media")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__111e41475bfe3e7f5e4d5c1f5451dae6c00a3415c7b3e46d2f27983d7f64b3ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e99743d28fbbf034c563c60118f5c7c7ac9d0500fa5de8937f30df1a773601bd)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daf1360be7fb4ff9595e71e0b27f48e4442854d3e53c91e087d11c0820930f7f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__450108f159d400c23c3eab896a8a42bc02401402158fdb55f85f4649e9764bec)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7760ea254b6d7845793d249628ee5a5fbf8d9dd12a32f9659f652dd95b6a4ead)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7de9781980684818b250f545a3926f1b9cbbc14989619ce08fa18ae2789acd09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b54fa986eda62a2bc77fab0a47a9a0da0e3a8a92e1fab441c4f5c422232d11c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

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
            type_hints = typing.get_type_hints(_typecheckingstub__b6c123853ab4b689e7b54d9455357f42046ea2f4ae3d3daee744ef28d22bee58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "baseUrl", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="crawlingOption")
    def crawling_option(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "crawlingOption"))

    @crawling_option.setter
    def crawling_option(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__39d8d93db5ac54e4ab69167e34aba2203195d03384b818f557c6df20271dfba4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5152c5e911a4f47f2cd7edcabc19b4f4f0f131aa7d1e431c1cf33e0cdf4fdb7e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embedMedia", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8385ea90f6ae73cf2e3cfc39a22a0daca2dbe2b96e832cce69531c9d2d1ead68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseLastIndexingJob",
    jsii_struct_bases=[],
    name_mapping={
        "completed_datasources": "completedDatasources",
        "data_source_uuids": "dataSourceUuids",
        "phase": "phase",
        "tokens": "tokens",
        "total_datasources": "totalDatasources",
        "uuid": "uuid",
    },
)
class GenaiKnowledgeBaseLastIndexingJob:
    def __init__(
        self,
        *,
        completed_datasources: typing.Optional[jsii.Number] = None,
        data_source_uuids: typing.Optional[typing.Sequence[builtins.str]] = None,
        phase: typing.Optional[builtins.str] = None,
        tokens: typing.Optional[jsii.Number] = None,
        total_datasources: typing.Optional[jsii.Number] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#completed_datasources GenaiKnowledgeBase#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#data_source_uuids GenaiKnowledgeBase#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#phase GenaiKnowledgeBase#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tokens GenaiKnowledgeBase#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#total_datasources GenaiKnowledgeBase#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#uuid GenaiKnowledgeBase#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7e7d6f6a706e09d4287db8b207060fff58d0570de48f785cfc8ef86d26574975)
            check_type(argname="argument completed_datasources", value=completed_datasources, expected_type=type_hints["completed_datasources"])
            check_type(argname="argument data_source_uuids", value=data_source_uuids, expected_type=type_hints["data_source_uuids"])
            check_type(argname="argument phase", value=phase, expected_type=type_hints["phase"])
            check_type(argname="argument tokens", value=tokens, expected_type=type_hints["tokens"])
            check_type(argname="argument total_datasources", value=total_datasources, expected_type=type_hints["total_datasources"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if completed_datasources is not None:
            self._values["completed_datasources"] = completed_datasources
        if data_source_uuids is not None:
            self._values["data_source_uuids"] = data_source_uuids
        if phase is not None:
            self._values["phase"] = phase
        if tokens is not None:
            self._values["tokens"] = tokens
        if total_datasources is not None:
            self._values["total_datasources"] = total_datasources
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def completed_datasources(self) -> typing.Optional[jsii.Number]:
        '''Number of completed datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#completed_datasources GenaiKnowledgeBase#completed_datasources}
        '''
        result = self._values.get("completed_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_source_uuids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Datasource UUIDs for the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#data_source_uuids GenaiKnowledgeBase#data_source_uuids}
        '''
        result = self._values.get("data_source_uuids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase(self) -> typing.Optional[builtins.str]:
        '''Phase of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#phase GenaiKnowledgeBase#phase}
        '''
        result = self._values.get("phase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Number of tokens processed in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#tokens GenaiKnowledgeBase#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_datasources(self) -> typing.Optional[jsii.Number]:
        '''Total number of datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#total_datasources GenaiKnowledgeBase#total_datasources}
        '''
        result = self._values.get("total_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID  of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_knowledge_base#uuid GenaiKnowledgeBase#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiKnowledgeBaseLastIndexingJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiKnowledgeBaseLastIndexingJobList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseLastIndexingJobList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e30dada4b79a02ba0e5f4a75b3b1b477ab0ac6790861f96e62018d0156a57f69)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiKnowledgeBaseLastIndexingJobOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2873f7d605621f66134415c90f6ffd24c33306922aefb4ee27dd355845ed424e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiKnowledgeBaseLastIndexingJobOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10b4938497f23131abbe868814e5fcf1cbde2bea6929524399244be8c0d27af2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__078be8b8cf2c466892ae9656bbd485ec3dda567da1702461791220a003d45b37)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d32d34ca954afb6ed43b4a2c1a9402512c1b8c98b0906540637145f04199f56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseLastIndexingJob]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseLastIndexingJob]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseLastIndexingJob]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e5f8b3c320eca2400207961fbb00c4907674754c7db2e582dc2942da4ba22f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiKnowledgeBaseLastIndexingJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiKnowledgeBase.GenaiKnowledgeBaseLastIndexingJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__158309ad4cb58e350afaccb1eb8b2e8c4da4034421961bd610a0169f6a559244)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCompletedDatasources")
    def reset_completed_datasources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCompletedDatasources", []))

    @jsii.member(jsii_name="resetDataSourceUuids")
    def reset_data_source_uuids(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDataSourceUuids", []))

    @jsii.member(jsii_name="resetPhase")
    def reset_phase(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPhase", []))

    @jsii.member(jsii_name="resetTokens")
    def reset_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTokens", []))

    @jsii.member(jsii_name="resetTotalDatasources")
    def reset_total_datasources(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTotalDatasources", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="finishedAt")
    def finished_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "finishedAt"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseUuid")
    def knowledge_base_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "knowledgeBaseUuid"))

    @builtins.property
    @jsii.member(jsii_name="startedAt")
    def started_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="completedDatasourcesInput")
    def completed_datasources_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "completedDatasourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuidsInput")
    def data_source_uuids_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "dataSourceUuidsInput"))

    @builtins.property
    @jsii.member(jsii_name="phaseInput")
    def phase_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "phaseInput"))

    @builtins.property
    @jsii.member(jsii_name="tokensInput")
    def tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tokensInput"))

    @builtins.property
    @jsii.member(jsii_name="totalDatasourcesInput")
    def total_datasources_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "totalDatasourcesInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="completedDatasources")
    def completed_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "completedDatasources"))

    @completed_datasources.setter
    def completed_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aaf783bc7b443e61bdfd85be6dbfc49f144b159150ab948970b12680e22e83b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuids")
    def data_source_uuids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataSourceUuids"))

    @data_source_uuids.setter
    def data_source_uuids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50783a9c1436d62dc3555d8a063e613606441fa596214c36e82e654c83481fa5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceUuids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase")
    def phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phase"))

    @phase.setter
    def phase(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04ecb71b4ee9278d79912e07c32c0d8e91f70a2787765891a060ac2ef9ad1b73)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82ad46d3cd69366e145140ed79940687b78541b4caf67105469f6bde0e326009)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDatasources")
    def total_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalDatasources"))

    @total_datasources.setter
    def total_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c348f8dc794b05f855b6a3fb2bfb5f9dcafd99c263c24474f51d820cca6b436c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__045485a725371d9633349a204ce330bf1d80f026eac7bfb1fc7381ac9410724b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseLastIndexingJob]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseLastIndexingJob]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseLastIndexingJob]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1da87bffbc13872ae23773e86e056b559162f8602fd7b03657cf870fa4990057)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GenaiKnowledgeBase",
    "GenaiKnowledgeBaseConfig",
    "GenaiKnowledgeBaseDatasources",
    "GenaiKnowledgeBaseDatasourcesFileUploadDataSource",
    "GenaiKnowledgeBaseDatasourcesFileUploadDataSourceList",
    "GenaiKnowledgeBaseDatasourcesFileUploadDataSourceOutputReference",
    "GenaiKnowledgeBaseDatasourcesLastIndexingJob",
    "GenaiKnowledgeBaseDatasourcesLastIndexingJobList",
    "GenaiKnowledgeBaseDatasourcesLastIndexingJobOutputReference",
    "GenaiKnowledgeBaseDatasourcesList",
    "GenaiKnowledgeBaseDatasourcesOutputReference",
    "GenaiKnowledgeBaseDatasourcesSpacesDataSource",
    "GenaiKnowledgeBaseDatasourcesSpacesDataSourceList",
    "GenaiKnowledgeBaseDatasourcesSpacesDataSourceOutputReference",
    "GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource",
    "GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceList",
    "GenaiKnowledgeBaseDatasourcesWebCrawlerDataSourceOutputReference",
    "GenaiKnowledgeBaseLastIndexingJob",
    "GenaiKnowledgeBaseLastIndexingJobList",
    "GenaiKnowledgeBaseLastIndexingJobOutputReference",
]

publication.publish()

def _typecheckingstub__f632334af9bbb652f8e52d508c9d3e515d10bef60910b5ae2be4dbc31065c239(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    datasources: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasources, typing.Dict[builtins.str, typing.Any]]]],
    embedding_model_uuid: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    region: builtins.str,
    added_to_agent_at: typing.Optional[builtins.str] = None,
    database_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_indexing_job: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseLastIndexingJob, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
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

def _typecheckingstub__5258743cafc4cadb7222f195ef1d2832f8fec389076ee8d47c944d96fd29d1be(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d09191dbb4f4f8a572fed1cd89e46f6cffb4225a07250a86e1bc27343cf47ae4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasources, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52eadacba87603f53e347e6fa9f9568d67501700e453c2050b8669e75c751d7b(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseLastIndexingJob, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7943a409758fb4355ee6100242da4fe5553e02ddb7adbf21402c7514863b9c6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55aabbacf6fdac9738cb049de9a2583f38fe9112bbdd16e5eae2bde83a4ed12b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f26c8e7332c1dd10dbe9da309690a54c57aaf9cfbb0ebfdcf09d7ecc0ac52503(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e31c980b5b916fc5277bf7352feb5892597c6c852bcf1a40cb62ed6fb628637b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3802576b0fadc1c9b4c1c97a5cbb58a003402ad0f9e9ee168405044e850c436(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__044ae117534fc73e143c4bf6f0da21113f9c4232b29b7cd53756779b1cda8716(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0a64747ce3e0be219f13aa203521481f20eac7eb5dff427d1c02a70154b5263(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0709e8e3857dd70798447936b884327c06b3b3866a2f9ed2bc558d0f4e4b5e75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__feb3619432a8ee9c14515481309fb393e3eabd3af0ea91e4b2a76ea121c7fe43(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6f97b8ec9f162979bef581bbca51c759f53dfcb8a682b5cf1e6c7f23b8f700b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3fcbd577e624422b294bee89a99a34dd12493122f70a99bc0c7f07e0fb56d72(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    datasources: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasources, typing.Dict[builtins.str, typing.Any]]]],
    embedding_model_uuid: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    region: builtins.str,
    added_to_agent_at: typing.Optional[builtins.str] = None,
    database_id: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_indexing_job: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseLastIndexingJob, typing.Dict[builtins.str, typing.Any]]]]] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    vpc_uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__031d1b5bbf00f73165daea5016941fff16d093bad24645cb4b972a27cbbe0c5b(
    *,
    file_upload_data_source: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesFileUploadDataSource, typing.Dict[builtins.str, typing.Any]]]]] = None,
    last_indexing_job: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]]]] = None,
    spaces_data_source: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesSpacesDataSource, typing.Dict[builtins.str, typing.Any]]]]] = None,
    uuid: typing.Optional[builtins.str] = None,
    web_crawler_data_source: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e21b8753a9c51e185ee1cf9a1a69565a4ce01230cf004ce438bfd08a78f06637(
    *,
    original_file_name: typing.Optional[builtins.str] = None,
    size_in_bytes: typing.Optional[builtins.str] = None,
    stored_object_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__844d44a9b8be9c1b312e001dd894aff17a64408617bce4121cfdde9f03f21bad(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70e3fa41ef747f454551ab5fefbc1dab94414f9aa7d99f86ff0902204ce1fa1d(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e30c68a9d105073d3f9b20a2e2390845b4d191c0d7aca31814fc0fed71e053b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__47cfa21e7c6f96a07dc7f9a1c1d3ab24411830a750eaf59e0663fb2cc5031b5f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0255eb0457be8629d47056eb82e274f56b01b623da36cac45a4e5ce9bbf8b5a6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecdf9eae3627f767b62228d00c2f0426c2be2ad0d6ff426289802b9c8cad4135(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesFileUploadDataSource]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__094592e0f1b6e61de612badbb04bd82727d8f5f87c7540f44d0eec20946e5e0f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71862c2dee45a52a8da9d6e94e85c3d577d012e465e952555d7bd379ac693db9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cf8a5f0de75d4837b3673fd7a0901e5121be52cd145649d598c068534d995fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad5cc9b600c161ae2f7f9d50dd6fb0380b08da1a1c8ec477574ee5e12b87311e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66b46c92cef4017eba6fdd7299136ece574f31901fe22cc61858a04e3c335e1f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesFileUploadDataSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8105cbd69e07bd94eb6aab60adb58073d16bba6b8dd49c71629f6df892ad31a(
    *,
    completed_datasources: typing.Optional[jsii.Number] = None,
    data_source_uuids: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[jsii.Number] = None,
    total_datasources: typing.Optional[jsii.Number] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d96bb5db1ce6c1299c5845a638a99d005b232a99c070ea4c664787fed70c546(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c466dc6662c7dd8aa433994575ddb2a36804f877755a9809177148ce0e2aed18(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9db6061aa26d87b8acef8513ff99621bb2de6962a07a82bf5041b4dcfee44037(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d73eb68582efd0037cd4a8166815715df5f1447d13239b0002660876937e0b0f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__293af08205b5e996bd546f7c9dd9068579e14fbfb68970957223174bf1280a82(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27b19dcd9e292e95ab6f2f5dd90784fddf3f0ff445e0d2cf0745200d242c49a1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesLastIndexingJob]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7434b6735941c2931059c7ee7b3f3fcabc82afb75a3fdb07df9ca6faea15bb3f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__67e67d29b0ef95a179245dcedccd420728112968770cb910ed4d6d66cfc0b3db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b7364d82e8cd3c949f92993b9e2560808ce9fde42cb5a22b5e40cf803ba1ac2(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca13642c678c12c69201fd880b9da8633a8e80d0eedb7924b35b8c4585110982(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04a83c34a43e9aa8d4cbfcc7bd93dc01e167e9c228cbbdc2344359ef61af7249(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b8b664fcd0201cfa537bf5a5ba5e1e31232510ee8ad9175b5a4dc77c45e0648(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f38802cd75731a4a2281a69e27145260cba7a9b60a3e51ba53f5594e74da71a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32ad3ccb255670c059ddbc6b4748cb1abf001cd89bed5bea2e112a1e26945b44(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesLastIndexingJob]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__72908b977bbfe2d49017de819d1207c070c7170c7e4758b14556e6dc50f6ffc5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a3ff0ab11f143ff195cc4cc2e5ecb30e09c5a3d876c4330901422c3a0fe12f0(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f84df635bc1d15ac3010dcb6004dfb85dff6a5012583694480daef797304deea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f975f81abd5da7b1da28f74f1d444b7055aca26ada8782387f088f89df5dca47(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__084df66d9e717ad2d7780fd7cc5ac053f3af240170e257d782e2f5554f977b06(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__afac679ab6ba8ecb3c947bfa9ed55211d2387468739011bb1bfb1794b0d9afca(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasources]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee64a6d75c8abc92610f4d0b94b71079e66a21979cc480ca82c860a2f6416551(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13fd1fa7bb2226e5319dfc2527bddebd2dbc618cdc731090a5ad9ea3942ae100(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesFileUploadDataSource, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6d56552a3223a3b5b9dfc126e6dfe0218fd5ca9f23fc8792f08b23e30a022a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21691ad4b16ce659e354de3da46f32698e1cf3cd99968928623ddfb9044c99e7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesSpacesDataSource, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6076a1108d1f529f3d3fabbfbb0f59f75519c6165278d977b012a0cf5503c05(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22d60634bca820b7c25cdb82a420d477b34c821d33a4e3e404000263d5327700(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__323af9ba27142f0afd700b2ede546ee851a49a193b9040d75236426c591501b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasources]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6f8ff6b9f3e491a2aafeb70fb14a4ed5ba525f545c0a0b1fd96d5f093848a72(
    *,
    bucket_name: typing.Optional[builtins.str] = None,
    item_path: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ee620cf00778a6d979e5d66e130c44f68a89311d95fdd7dee286eb8fee4fc98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__665865587d3309d793899f96384db1f4c3e3f820bd2ebb85312a9be74a6d8c61(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__528efea3138abc85795818e74ae02cc3a1159a28ed6a18ec805b7055c0bc9694(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecd8cd6a93f2f4b47362b3776b162f16ddf4913b3fe287d3a6c25672233065bd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__490db655b761a3b687a80d54bc9274dae9d8362c143c65dd36509b445ec98356(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d064a60686cf43607dd3218a80bc6d9ffe8c138b007d6456e2f8c1812472f9c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesSpacesDataSource]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dd6b089ac4725fe1e66345a05c26cef3009d6a8d6dd8a7469bd694a580d33749(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95663de7ce750f8b29aaf0c0935cb587384e5f783e3bd1c6886797e48f00f9b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50461b2a7f577a2dbe974f79203311f56bb63265fbcac7dbc2b6855904aa0730(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74fb9f54c5bd7b3a7eeb495d7d12a913dd5e97396f6bef82298915dfe09a3bd8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2de04e485ef365be3c46a556218b96c790d249bda97cf1cf395b9968e4cd87aa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesSpacesDataSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e42415897ddf555b418e6a53089c6eb1005a8522d095ff10a1b985af4593799(
    *,
    base_url: typing.Optional[builtins.str] = None,
    crawling_option: typing.Optional[builtins.str] = None,
    embed_media: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__111e41475bfe3e7f5e4d5c1f5451dae6c00a3415c7b3e46d2f27983d7f64b3ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e99743d28fbbf034c563c60118f5c7c7ac9d0500fa5de8937f30df1a773601bd(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daf1360be7fb4ff9595e71e0b27f48e4442854d3e53c91e087d11c0820930f7f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__450108f159d400c23c3eab896a8a42bc02401402158fdb55f85f4649e9764bec(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7760ea254b6d7845793d249628ee5a5fbf8d9dd12a32f9659f652dd95b6a4ead(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7de9781980684818b250f545a3926f1b9cbbc14989619ce08fa18ae2789acd09(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b54fa986eda62a2bc77fab0a47a9a0da0e3a8a92e1fab441c4f5c422232d11c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c123853ab4b689e7b54d9455357f42046ea2f4ae3d3daee744ef28d22bee58(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__39d8d93db5ac54e4ab69167e34aba2203195d03384b818f557c6df20271dfba4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5152c5e911a4f47f2cd7edcabc19b4f4f0f131aa7d1e431c1cf33e0cdf4fdb7e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8385ea90f6ae73cf2e3cfc39a22a0daca2dbe2b96e832cce69531c9d2d1ead68(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseDatasourcesWebCrawlerDataSource]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e7d6f6a706e09d4287db8b207060fff58d0570de48f785cfc8ef86d26574975(
    *,
    completed_datasources: typing.Optional[jsii.Number] = None,
    data_source_uuids: typing.Optional[typing.Sequence[builtins.str]] = None,
    phase: typing.Optional[builtins.str] = None,
    tokens: typing.Optional[jsii.Number] = None,
    total_datasources: typing.Optional[jsii.Number] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e30dada4b79a02ba0e5f4a75b3b1b477ab0ac6790861f96e62018d0156a57f69(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2873f7d605621f66134415c90f6ffd24c33306922aefb4ee27dd355845ed424e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10b4938497f23131abbe868814e5fcf1cbde2bea6929524399244be8c0d27af2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__078be8b8cf2c466892ae9656bbd485ec3dda567da1702461791220a003d45b37(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d32d34ca954afb6ed43b4a2c1a9402512c1b8c98b0906540637145f04199f56(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e5f8b3c320eca2400207961fbb00c4907674754c7db2e582dc2942da4ba22f9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiKnowledgeBaseLastIndexingJob]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__158309ad4cb58e350afaccb1eb8b2e8c4da4034421961bd610a0169f6a559244(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aaf783bc7b443e61bdfd85be6dbfc49f144b159150ab948970b12680e22e83b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50783a9c1436d62dc3555d8a063e613606441fa596214c36e82e654c83481fa5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04ecb71b4ee9278d79912e07c32c0d8e91f70a2787765891a060ac2ef9ad1b73(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82ad46d3cd69366e145140ed79940687b78541b4caf67105469f6bde0e326009(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c348f8dc794b05f855b6a3fb2bfb5f9dcafd99c263c24474f51d820cca6b436c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__045485a725371d9633349a204ce330bf1d80f026eac7bfb1fc7381ac9410724b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1da87bffbc13872ae23773e86e056b559162f8602fd7b03657cf870fa4990057(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiKnowledgeBaseLastIndexingJob]],
) -> None:
    """Type checking stubs"""
    pass
