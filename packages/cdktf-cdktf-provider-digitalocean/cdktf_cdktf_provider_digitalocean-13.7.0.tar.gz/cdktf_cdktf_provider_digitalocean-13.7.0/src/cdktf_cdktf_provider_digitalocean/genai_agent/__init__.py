r'''
# `digitalocean_genai_agent`

Refer to the Terraform Registry for docs: [`digitalocean_genai_agent`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent).
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


class GenaiAgent(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgent",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent digitalocean_genai_agent}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        instruction: builtins.str,
        model_uuid: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        region: builtins.str,
        agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentAgentGuardrail", typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentAnthropicApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_key_uuid: typing.Optional[builtins.str] = None,
        api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentApiKeyInfos", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentApiKeys", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChatbot", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChatbotIdentifiers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        child_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgents", typing.Dict[builtins.str, typing.Any]]]]] = None,
        created_at: typing.Optional[builtins.str] = None,
        deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentDeployment", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentFunctions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        if_case: typing.Optional[builtins.str] = None,
        k: typing.Optional[jsii.Number] = None,
        knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        knowledge_base_uuid: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_tokens: typing.Optional[jsii.Number] = None,
        model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentOpenAiApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        open_ai_key_uuid: typing.Optional[builtins.str] = None,
        parent_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgents", typing.Dict[builtins.str, typing.Any]]]]] = None,
        provide_citations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrieval_method: typing.Optional[builtins.str] = None,
        route_created_by: typing.Optional[builtins.str] = None,
        route_name: typing.Optional[builtins.str] = None,
        route_uuid: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        temperature: typing.Optional[jsii.Number] = None,
        template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplate", typing.Dict[builtins.str, typing.Any]]]]] = None,
        top_p: typing.Optional[jsii.Number] = None,
        url: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent digitalocean_genai_agent} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param instruction: Instruction for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        :param model_uuid: Model UUID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        :param name: Name of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param project_id: Project ID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        :param region: Region where the Agent is deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        :param agent_guardrail: agent_guardrail block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agent_guardrail GenaiAgent#agent_guardrail}
        :param anthropic_api_key: anthropic_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        :param anthropic_key_uuid: Optional Anthropic API key ID to use with Anthropic models. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_key_uuid GenaiAgent#anthropic_key_uuid}
        :param api_key_infos: api_key_infos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        :param api_keys: api_keys block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        :param chatbot: chatbot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        :param chatbot_identifiers: chatbot_identifiers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        :param child_agents: child_agents block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#child_agents GenaiAgent#child_agents}
        :param created_at: Timestamp when the Agent was created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_at GenaiAgent#created_at}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        :param description: Description for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param functions: functions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#functions GenaiAgent#functions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#id GenaiAgent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param if_case: If case condition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#if_case GenaiAgent#if_case}
        :param k: K value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#k GenaiAgent#k}
        :param knowledge_bases: knowledge_bases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_bases GenaiAgent#knowledge_bases}
        :param knowledge_base_uuid: Ids of the knowledge base(s) to attach to the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_base_uuid GenaiAgent#knowledge_base_uuid}
        :param max_tokens: Maximum tokens allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#max_tokens GenaiAgent#max_tokens}
        :param model: model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model GenaiAgent#model}
        :param open_ai_api_key: open_ai_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#open_ai_api_key GenaiAgent#open_ai_api_key}
        :param open_ai_key_uuid: Optional OpenAI API key ID to use with OpenAI models. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#open_ai_key_uuid GenaiAgent#open_ai_key_uuid}
        :param parent_agents: parent_agents block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_agents GenaiAgent#parent_agents}
        :param provide_citations: Indicates if the agent should provide citations in responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provide_citations GenaiAgent#provide_citations}
        :param retrieval_method: Retrieval method used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#retrieval_method GenaiAgent#retrieval_method}
        :param route_created_by: User who created the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_created_by GenaiAgent#route_created_by}
        :param route_name: Route name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_name GenaiAgent#route_name}
        :param route_uuid: Route UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_uuid GenaiAgent#route_uuid}
        :param tags: List of Tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        :param temperature: Agent temperature setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#temperature GenaiAgent#temperature}
        :param template: template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#template GenaiAgent#template}
        :param top_p: Top P sampling parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#top_p GenaiAgent#top_p}
        :param url: URL for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param user_id: User ID linked with the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8ad15c6eed73b0e5f68e4e306d1928365102a6f7a62128ec0c97e04c1cd828b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = GenaiAgentConfig(
            instruction=instruction,
            model_uuid=model_uuid,
            name=name,
            project_id=project_id,
            region=region,
            agent_guardrail=agent_guardrail,
            anthropic_api_key=anthropic_api_key,
            anthropic_key_uuid=anthropic_key_uuid,
            api_key_infos=api_key_infos,
            api_keys=api_keys,
            chatbot=chatbot,
            chatbot_identifiers=chatbot_identifiers,
            child_agents=child_agents,
            created_at=created_at,
            deployment=deployment,
            description=description,
            functions=functions,
            id=id,
            if_case=if_case,
            k=k,
            knowledge_bases=knowledge_bases,
            knowledge_base_uuid=knowledge_base_uuid,
            max_tokens=max_tokens,
            model=model,
            open_ai_api_key=open_ai_api_key,
            open_ai_key_uuid=open_ai_key_uuid,
            parent_agents=parent_agents,
            provide_citations=provide_citations,
            retrieval_method=retrieval_method,
            route_created_by=route_created_by,
            route_name=route_name,
            route_uuid=route_uuid,
            tags=tags,
            temperature=temperature,
            template=template,
            top_p=top_p,
            url=url,
            user_id=user_id,
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
        '''Generates CDKTF code for importing a GenaiAgent resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the GenaiAgent to import.
        :param import_from_id: The id of the existing GenaiAgent that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the GenaiAgent to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6b2b05818d707f1696237ccee85341c07300b06a592cbb004db693cf7771f03)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAgentGuardrail")
    def put_agent_guardrail(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentAgentGuardrail", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb4dd3c7de22ca49dfa2a1804b444eb491344e3afb3a40fa18f1d261975f9daf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAgentGuardrail", [value]))

    @jsii.member(jsii_name="putAnthropicApiKey")
    def put_anthropic_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentAnthropicApiKey", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2c4c185c6505e127ae3a374b0da82e8cf2c671263abbe1cbe0e7f6c6eff5914)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnthropicApiKey", [value]))

    @jsii.member(jsii_name="putApiKeyInfos")
    def put_api_key_infos(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentApiKeyInfos", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__267b3ca15e3360e1f10dbe222f262d3ada1115cd68d913360f8eadf9ce7d60ad)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeyInfos", [value]))

    @jsii.member(jsii_name="putApiKeys")
    def put_api_keys(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentApiKeys", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c57e52ff4a00c6e8fc8db158fc1ce3b6535d8a7132941c5cef4b76afa3daa64d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeys", [value]))

    @jsii.member(jsii_name="putChatbot")
    def put_chatbot(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChatbot", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__582ad8e5c4a1f4b8d6674c8cb50523d6bd432b93b5b33fe5b497795cb68b147f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbot", [value]))

    @jsii.member(jsii_name="putChatbotIdentifiers")
    def put_chatbot_identifiers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChatbotIdentifiers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6d225646d51ace5b98ed4bc6cf34e07d2f3a38e8bc553cd157cb020b798ea25)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbotIdentifiers", [value]))

    @jsii.member(jsii_name="putChildAgents")
    def put_child_agents(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgents", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a08d93585900228b9646464bc701a8548d334f14b802062aa07e1d5193ed4249)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChildAgents", [value]))

    @jsii.member(jsii_name="putDeployment")
    def put_deployment(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentDeployment", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06b10067569d609ea09022a43e3390833a28da96a9c45790ee47e88a20c500b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDeployment", [value]))

    @jsii.member(jsii_name="putFunctions")
    def put_functions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentFunctions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f479d01a6e12f1207fe5a357551cb135b1525f2bf0ed1d441afbd914e30ccb0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFunctions", [value]))

    @jsii.member(jsii_name="putKnowledgeBases")
    def put_knowledge_bases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c62d9b4eb8ef54ae7667ddef9002557c59e95ba4466ab89a12c147ec087a0f13)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKnowledgeBases", [value]))

    @jsii.member(jsii_name="putModel")
    def put_model(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentModel", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__611c6b7ae39f2ff17759633d795165d59f8513a272a9da0fe866f7672bf82412)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putModel", [value]))

    @jsii.member(jsii_name="putOpenAiApiKey")
    def put_open_ai_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentOpenAiApiKey", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1eee1f4491176fb38d55103c37d2b577f3ce5a9ea5e7f87a43fa213d2f93640)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOpenAiApiKey", [value]))

    @jsii.member(jsii_name="putParentAgents")
    def put_parent_agents(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgents", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9a0d413e1a8740fcc213096bdb04008272d5f21ebd582d0f8678e1b6c46abee1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putParentAgents", [value]))

    @jsii.member(jsii_name="putTemplate")
    def put_template(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplate", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3914d50054b5984ec44d21896ce99ce613cb8864df461155444d87de0ee0f220)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTemplate", [value]))

    @jsii.member(jsii_name="resetAgentGuardrail")
    def reset_agent_guardrail(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentGuardrail", []))

    @jsii.member(jsii_name="resetAnthropicApiKey")
    def reset_anthropic_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicApiKey", []))

    @jsii.member(jsii_name="resetAnthropicKeyUuid")
    def reset_anthropic_key_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicKeyUuid", []))

    @jsii.member(jsii_name="resetApiKeyInfos")
    def reset_api_key_infos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeyInfos", []))

    @jsii.member(jsii_name="resetApiKeys")
    def reset_api_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeys", []))

    @jsii.member(jsii_name="resetChatbot")
    def reset_chatbot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbot", []))

    @jsii.member(jsii_name="resetChatbotIdentifiers")
    def reset_chatbot_identifiers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbotIdentifiers", []))

    @jsii.member(jsii_name="resetChildAgents")
    def reset_child_agents(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChildAgents", []))

    @jsii.member(jsii_name="resetCreatedAt")
    def reset_created_at(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedAt", []))

    @jsii.member(jsii_name="resetDeployment")
    def reset_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeployment", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFunctions")
    def reset_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFunctions", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIfCase")
    def reset_if_case(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIfCase", []))

    @jsii.member(jsii_name="resetK")
    def reset_k(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK", []))

    @jsii.member(jsii_name="resetKnowledgeBases")
    def reset_knowledge_bases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnowledgeBases", []))

    @jsii.member(jsii_name="resetKnowledgeBaseUuid")
    def reset_knowledge_base_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnowledgeBaseUuid", []))

    @jsii.member(jsii_name="resetMaxTokens")
    def reset_max_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTokens", []))

    @jsii.member(jsii_name="resetModel")
    def reset_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModel", []))

    @jsii.member(jsii_name="resetOpenAiApiKey")
    def reset_open_ai_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenAiApiKey", []))

    @jsii.member(jsii_name="resetOpenAiKeyUuid")
    def reset_open_ai_key_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenAiKeyUuid", []))

    @jsii.member(jsii_name="resetParentAgents")
    def reset_parent_agents(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentAgents", []))

    @jsii.member(jsii_name="resetProvideCitations")
    def reset_provide_citations(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvideCitations", []))

    @jsii.member(jsii_name="resetRetrievalMethod")
    def reset_retrieval_method(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRetrievalMethod", []))

    @jsii.member(jsii_name="resetRouteCreatedBy")
    def reset_route_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteCreatedBy", []))

    @jsii.member(jsii_name="resetRouteName")
    def reset_route_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteName", []))

    @jsii.member(jsii_name="resetRouteUuid")
    def reset_route_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRouteUuid", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetTemperature")
    def reset_temperature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemperature", []))

    @jsii.member(jsii_name="resetTemplate")
    def reset_template(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemplate", []))

    @jsii.member(jsii_name="resetTopP")
    def reset_top_p(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopP", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

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
    @jsii.member(jsii_name="agentGuardrail")
    def agent_guardrail(self) -> "GenaiAgentAgentGuardrailList":
        return typing.cast("GenaiAgentAgentGuardrailList", jsii.get(self, "agentGuardrail"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(self) -> "GenaiAgentAnthropicApiKeyList":
        return typing.cast("GenaiAgentAnthropicApiKeyList", jsii.get(self, "anthropicApiKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfos")
    def api_key_infos(self) -> "GenaiAgentApiKeyInfosList":
        return typing.cast("GenaiAgentApiKeyInfosList", jsii.get(self, "apiKeyInfos"))

    @builtins.property
    @jsii.member(jsii_name="apiKeys")
    def api_keys(self) -> "GenaiAgentApiKeysList":
        return typing.cast("GenaiAgentApiKeysList", jsii.get(self, "apiKeys"))

    @builtins.property
    @jsii.member(jsii_name="chatbot")
    def chatbot(self) -> "GenaiAgentChatbotList":
        return typing.cast("GenaiAgentChatbotList", jsii.get(self, "chatbot"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiers")
    def chatbot_identifiers(self) -> "GenaiAgentChatbotIdentifiersList":
        return typing.cast("GenaiAgentChatbotIdentifiersList", jsii.get(self, "chatbotIdentifiers"))

    @builtins.property
    @jsii.member(jsii_name="childAgents")
    def child_agents(self) -> "GenaiAgentChildAgentsList":
        return typing.cast("GenaiAgentChildAgentsList", jsii.get(self, "childAgents"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> "GenaiAgentDeploymentList":
        return typing.cast("GenaiAgentDeploymentList", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="functions")
    def functions(self) -> "GenaiAgentFunctionsList":
        return typing.cast("GenaiAgentFunctionsList", jsii.get(self, "functions"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBases")
    def knowledge_bases(self) -> "GenaiAgentKnowledgeBasesList":
        return typing.cast("GenaiAgentKnowledgeBasesList", jsii.get(self, "knowledgeBases"))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> "GenaiAgentModelList":
        return typing.cast("GenaiAgentModelList", jsii.get(self, "model"))

    @builtins.property
    @jsii.member(jsii_name="openAiApiKey")
    def open_ai_api_key(self) -> "GenaiAgentOpenAiApiKeyList":
        return typing.cast("GenaiAgentOpenAiApiKeyList", jsii.get(self, "openAiApiKey"))

    @builtins.property
    @jsii.member(jsii_name="parentAgents")
    def parent_agents(self) -> "GenaiAgentParentAgentsList":
        return typing.cast("GenaiAgentParentAgentsList", jsii.get(self, "parentAgents"))

    @builtins.property
    @jsii.member(jsii_name="routeCreatedAt")
    def route_created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeCreatedAt"))

    @builtins.property
    @jsii.member(jsii_name="template")
    def template(self) -> "GenaiAgentTemplateList":
        return typing.cast("GenaiAgentTemplateList", jsii.get(self, "template"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="agentGuardrailInput")
    def agent_guardrail_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentAgentGuardrail"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentAgentGuardrail"]]], jsii.get(self, "agentGuardrailInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyInput")
    def anthropic_api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentAnthropicApiKey"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentAnthropicApiKey"]]], jsii.get(self, "anthropicApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicKeyUuidInput")
    def anthropic_key_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "anthropicKeyUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfosInput")
    def api_key_infos_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentApiKeyInfos"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentApiKeyInfos"]]], jsii.get(self, "apiKeyInfosInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeysInput")
    def api_keys_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentApiKeys"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentApiKeys"]]], jsii.get(self, "apiKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiersInput")
    def chatbot_identifiers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChatbotIdentifiers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChatbotIdentifiers"]]], jsii.get(self, "chatbotIdentifiersInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotInput")
    def chatbot_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChatbot"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChatbot"]]], jsii.get(self, "chatbotInput"))

    @builtins.property
    @jsii.member(jsii_name="childAgentsInput")
    def child_agents_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgents"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgents"]]], jsii.get(self, "childAgentsInput"))

    @builtins.property
    @jsii.member(jsii_name="createdAtInput")
    def created_at_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdAtInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentDeployment"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentDeployment"]]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="functionsInput")
    def functions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentFunctions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentFunctions"]]], jsii.get(self, "functionsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ifCaseInput")
    def if_case_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ifCaseInput"))

    @builtins.property
    @jsii.member(jsii_name="instructionInput")
    def instruction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instructionInput"))

    @builtins.property
    @jsii.member(jsii_name="kInput")
    def k_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "kInput"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBasesInput")
    def knowledge_bases_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentKnowledgeBases"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentKnowledgeBases"]]], jsii.get(self, "knowledgeBasesInput"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseUuidInput")
    def knowledge_base_uuid_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "knowledgeBaseUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTokensInput")
    def max_tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTokensInput"))

    @builtins.property
    @jsii.member(jsii_name="modelInput")
    def model_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModel"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModel"]]], jsii.get(self, "modelInput"))

    @builtins.property
    @jsii.member(jsii_name="modelUuidInput")
    def model_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="openAiApiKeyInput")
    def open_ai_api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentOpenAiApiKey"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentOpenAiApiKey"]]], jsii.get(self, "openAiApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="openAiKeyUuidInput")
    def open_ai_key_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "openAiKeyUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="parentAgentsInput")
    def parent_agents_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgents"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgents"]]], jsii.get(self, "parentAgentsInput"))

    @builtins.property
    @jsii.member(jsii_name="projectIdInput")
    def project_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "projectIdInput"))

    @builtins.property
    @jsii.member(jsii_name="provideCitationsInput")
    def provide_citations_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "provideCitationsInput"))

    @builtins.property
    @jsii.member(jsii_name="regionInput")
    def region_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "regionInput"))

    @builtins.property
    @jsii.member(jsii_name="retrievalMethodInput")
    def retrieval_method_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "retrievalMethodInput"))

    @builtins.property
    @jsii.member(jsii_name="routeCreatedByInput")
    def route_created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeCreatedByInput"))

    @builtins.property
    @jsii.member(jsii_name="routeNameInput")
    def route_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeNameInput"))

    @builtins.property
    @jsii.member(jsii_name="routeUuidInput")
    def route_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "routeUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="tagsInput")
    def tags_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "tagsInput"))

    @builtins.property
    @jsii.member(jsii_name="temperatureInput")
    def temperature_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "temperatureInput"))

    @builtins.property
    @jsii.member(jsii_name="templateInput")
    def template_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplate"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplate"]]], jsii.get(self, "templateInput"))

    @builtins.property
    @jsii.member(jsii_name="topPInput")
    def top_p_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "topPInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicKeyUuid")
    def anthropic_key_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "anthropicKeyUuid"))

    @anthropic_key_uuid.setter
    def anthropic_key_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d81873a26223ec29313f6e2cd8172a1a41336384c90e451fb32aac3cf2709cce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "anthropicKeyUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @created_at.setter
    def created_at(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85adbc481545966c67a7847450287c72ab790543c5cb45777926b251e4d61fb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdAt", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a87bee0f257f12077898aea21e027fba170f43f1ba07bfa8e89f06a391ad490f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9b2c3fb6380cb6ab5f750b7811264a1118d31280a78a0c100b68619fef6754e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ifCase")
    def if_case(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ifCase"))

    @if_case.setter
    def if_case(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d4affd44a3a101d74e4031f1631bbe61431da9713a9edbf720d2926a54fc51e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ifCase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @instruction.setter
    def instruction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__29ddc31bd6028f28962f457930a28d75b89b2af569634898507338a5279f1922)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instruction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="k")
    def k(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "k"))

    @k.setter
    def k(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da8d2ea0e14ff5d8ef91f32be837e9cc98d745c57399fdad8bb393347c45400e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="knowledgeBaseUuid")
    def knowledge_base_uuid(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "knowledgeBaseUuid"))

    @knowledge_base_uuid.setter
    def knowledge_base_uuid(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ec0435b6f09cd28d46fe0a8e91f2e6ed8d0ddea75766e97a6b14fbcb0e0944a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "knowledgeBaseUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTokens")
    def max_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTokens"))

    @max_tokens.setter
    def max_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8428a7d1976ef3b7a8f6ecda84d281ee5f2455827827276b7ee6f0cb6e1e9417)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelUuid")
    def model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelUuid"))

    @model_uuid.setter
    def model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0a73155e6964184cf67dc542ad4865febc5666d5790b9473cbbaba6edd13091)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3259b1cf1f998bd0017a11db3fd2cb7ea4575fa5e9bef5231b49a4feb7b4fc39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="openAiKeyUuid")
    def open_ai_key_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "openAiKeyUuid"))

    @open_ai_key_uuid.setter
    def open_ai_key_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d8f2ec288a4e624527323ef46d7c067e9e781f290e52c31f99da489ddad0d0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "openAiKeyUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44c0edc416b656c709073b1904f62c20b1eab3efb55401f75e35269242cc58cc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provideCitations")
    def provide_citations(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "provideCitations"))

    @provide_citations.setter
    def provide_citations(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__072aad9e4f2c84953f9380adee092a97950cd8dc1fd57a54f9b4cd0876979cbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provideCitations", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c82923fcf2aed497acb9cf7a246bb6608b70e87bb038920d6c3063b33b7defe4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retrievalMethod")
    def retrieval_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retrievalMethod"))

    @retrieval_method.setter
    def retrieval_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c27a700463125fad4b177e60ba50e6effe845b208410826323857340c4b7b33a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retrievalMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeCreatedBy")
    def route_created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeCreatedBy"))

    @route_created_by.setter
    def route_created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20ff53d503102e9800ab44dbca8588eb455f9f96d86ceb0e56821d5a6eb8745b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeCreatedBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeName"))

    @route_name.setter
    def route_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3afa1e02b7f113706360fc391ff4f7388a7a6f68228e23d963bc22c743acdbda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeUuid")
    def route_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeUuid"))

    @route_uuid.setter
    def route_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__282f84dd62a95e6eb5a04933ddb5cb39594bd1928b5a0e459a9c6d12bf62e6f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9b94564e0f17d631b2fdd5803fb2de9cd45cf242924013a7a1cca50f9d1fca10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="temperature")
    def temperature(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "temperature"))

    @temperature.setter
    def temperature(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3b2472b53437b3cb11f8c24b980eac788a3fa21d753c2360f97242c0e16065f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "temperature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topP")
    def top_p(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topP"))

    @top_p.setter
    def top_p(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__184867ca0a917fc7a63d7f0f6bb2cbaddf5f13cb8a2d22bcbf7c0e7c834d6b37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topP", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4aab4b94873f2bbde16985eaf79130aade0a123482b50e076f3f377c79d8649f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b9f1a9aa0da7b6272423849a340b9fac4b5040c097dcf612830d0fcec87117c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentAgentGuardrail",
    jsii_struct_bases=[],
    name_mapping={
        "agent_uuid": "agentUuid",
        "default_response": "defaultResponse",
        "description": "description",
        "guardrail_uuid": "guardrailUuid",
        "is_default": "isDefault",
        "name": "name",
        "priority": "priority",
        "type": "type",
        "uuid": "uuid",
    },
)
class GenaiAgentAgentGuardrail:
    def __init__(
        self,
        *,
        agent_uuid: typing.Optional[builtins.str] = None,
        default_response: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        guardrail_uuid: typing.Optional[builtins.str] = None,
        is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        priority: typing.Optional[jsii.Number] = None,
        type: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param agent_uuid: Agent UUID for the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agent_uuid GenaiAgent#agent_uuid}
        :param default_response: Default response for the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#default_response GenaiAgent#default_response}
        :param description: Description of the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param guardrail_uuid: Guardrail UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#guardrail_uuid GenaiAgent#guardrail_uuid}
        :param is_default: Indicates if the Guardrail is default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_default GenaiAgent#is_default}
        :param name: Name of Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param priority: Priority of the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#priority GenaiAgent#priority}
        :param type: Type of the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#type GenaiAgent#type}
        :param uuid: Guardrail UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7566d41e587e4385181babbdf0ffc04a44a671a453e355436da33cdae5967c3)
            check_type(argname="argument agent_uuid", value=agent_uuid, expected_type=type_hints["agent_uuid"])
            check_type(argname="argument default_response", value=default_response, expected_type=type_hints["default_response"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument guardrail_uuid", value=guardrail_uuid, expected_type=type_hints["guardrail_uuid"])
            check_type(argname="argument is_default", value=is_default, expected_type=type_hints["is_default"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument priority", value=priority, expected_type=type_hints["priority"])
            check_type(argname="argument type", value=type, expected_type=type_hints["type"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if agent_uuid is not None:
            self._values["agent_uuid"] = agent_uuid
        if default_response is not None:
            self._values["default_response"] = default_response
        if description is not None:
            self._values["description"] = description
        if guardrail_uuid is not None:
            self._values["guardrail_uuid"] = guardrail_uuid
        if is_default is not None:
            self._values["is_default"] = is_default
        if name is not None:
            self._values["name"] = name
        if priority is not None:
            self._values["priority"] = priority
        if type is not None:
            self._values["type"] = type
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def agent_uuid(self) -> typing.Optional[builtins.str]:
        '''Agent UUID for the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agent_uuid GenaiAgent#agent_uuid}
        '''
        result = self._values.get("agent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_response(self) -> typing.Optional[builtins.str]:
        '''Default response for the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#default_response GenaiAgent#default_response}
        '''
        result = self._values.get("default_response")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guardrail_uuid(self) -> typing.Optional[builtins.str]:
        '''Guardrail UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#guardrail_uuid GenaiAgent#guardrail_uuid}
        '''
        result = self._values.get("guardrail_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Guardrail is default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_default GenaiAgent#is_default}
        '''
        result = self._values.get("is_default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Priority of the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#priority GenaiAgent#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Type of the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#type GenaiAgent#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''Guardrail UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentAgentGuardrail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentAgentGuardrailList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentAgentGuardrailList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a75119a431736970e588cc4563ac784afca97c2471c3c51717754f7e024c3e5e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentAgentGuardrailOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4f8b58ea3dd89e1bca8800f27118aaa360fce8503dabd96b49846182c1bc873)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentAgentGuardrailOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fad4a93114092bd64f78efc131128335d4dbc8197730a65dbbf94970f625022)
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
            type_hints = typing.get_type_hints(_typecheckingstub__165d385bae5a3a65407f74e9dcd9d1878e2c39a6948cbabc61fccc036a32c689)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa601f9c31d9d5dc606bc54d852da68e316769a12f766173bc73283eaca0f09b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAgentGuardrail]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAgentGuardrail]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAgentGuardrail]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6d0647809526fa1dd3ca9afbea21b45698c1d6a34475e99567bb2bbec738a8dd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentAgentGuardrailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentAgentGuardrailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b8e17bb6c72913753d3cbd0e0b0b29eb29ba2a9589b7854dca5df1df23982381)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAgentUuid")
    def reset_agent_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentUuid", []))

    @jsii.member(jsii_name="resetDefaultResponse")
    def reset_default_response(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultResponse", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetGuardrailUuid")
    def reset_guardrail_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuardrailUuid", []))

    @jsii.member(jsii_name="resetIsDefault")
    def reset_is_default(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsDefault", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPriority")
    def reset_priority(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPriority", []))

    @jsii.member(jsii_name="resetType")
    def reset_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetType", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="isAttached")
    def is_attached(self) -> _cdktf_9a9027ec.IResolvable:
        return typing.cast(_cdktf_9a9027ec.IResolvable, jsii.get(self, "isAttached"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="agentUuidInput")
    def agent_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultResponseInput")
    def default_response_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultResponseInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="guardrailUuidInput")
    def guardrail_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guardrailUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="isDefaultInput")
    def is_default_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isDefaultInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="priorityInput")
    def priority_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "priorityInput"))

    @builtins.property
    @jsii.member(jsii_name="typeInput")
    def type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "typeInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="agentUuid")
    def agent_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentUuid"))

    @agent_uuid.setter
    def agent_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd25aefa5b6a673e5bc604d700b005a465cc4ad70fc5279592389d458ec548a1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultResponse")
    def default_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultResponse"))

    @default_response.setter
    def default_response(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e785edc77fe9c2954d1dd88a133cdcd37b6be06b4920daac7e86159eb02d96f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultResponse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__272bcbc6975a05d19b0cda338cb4460370f5f319c58ede08806d9f17aaf07d89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="guardrailUuid")
    def guardrail_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guardrailUuid"))

    @guardrail_uuid.setter
    def guardrail_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de8553a6bceda9cefc5535f27519c4059f1ec26cc81b12d6b095191d0cdb8fe7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "guardrailUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isDefault")
    def is_default(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isDefault"))

    @is_default.setter
    def is_default(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f398074e61625562ab1dacbaf045374a6d00e2788af813bc7c1f9138dd5f9aa3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94b496795cae80d022f9cb135effcce376c45233f86002f6e70df1ea2bf881ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c90a1e97eadee6fabdb34d2761140b9d02830477791bc2d7a850e05f7ef6e7a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96bdacd29d6d0acc5502ee406a48eb86d8d42d158e845291d56211c47575f893)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__917dde05c244c4d09700034e14a35ce1acd8f36c68005e934412ddd3926e20f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAgentGuardrail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAgentGuardrail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAgentGuardrail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ac2569e10820d99fe8ffe1aba8ae58da126f83c6abd69f69b19ad8a12f488ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentAnthropicApiKey",
    jsii_struct_bases=[],
    name_mapping={"created_by": "createdBy", "name": "name", "uuid": "uuid"},
)
class GenaiAgentAnthropicApiKey:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4ef67f53293eef1562e17b21fba05e809d571c92dd5ae9b94cb3ea5a3f008762)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentAnthropicApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentAnthropicApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentAnthropicApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__db1b227fe49c8b6f2fd264298c7e500ca3eb3f4d76e45bc152b0a292f8b0634a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentAnthropicApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__817eb7a0173601d4f72f2a57731cb34d9efa695bbfd3da42029a90cb5627cae7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentAnthropicApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a4483b1f5caa2ebdfdafbf2e4fab138ee683f2c467332cd794374cf6e1a5eccb)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a39abb13df042687c08e068ad1bf9aa0f455a6d459b5cbfda812e3258f7db260)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec1ed65b5d0b241cbffac16071d8aec71e5b9ecc56249142444b0b6e0f1324e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAnthropicApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAnthropicApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAnthropicApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f950606dff36d70a94a78c3da74ea0ecf5eb9db7bd4b9402508bb6aaef8ba706)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentAnthropicApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentAnthropicApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__040e784819e33147aaad2d4b6637a267a66f4d0d495510405a24c8affecdfd44)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c6cd9d09006e7edbe1ad748e99af49060ab0608d571b7a4b54b0e502eb8c649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83c89015fa71628179ae0225194e02eeef03699b26a08262dc0246886fce8fa7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c1cfa1c7ee7327efbbdef0b43450f7ee2a23a714161c9c512d4128094316df04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAnthropicApiKey]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAnthropicApiKey]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAnthropicApiKey]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88006a8aaf9ffc0fd27f2c96b47e2a0fa78db205f88a17a1152887ee1b835493)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentApiKeyInfos",
    jsii_struct_bases=[],
    name_mapping={
        "created_by": "createdBy",
        "name": "name",
        "secret_key": "secretKey",
        "uuid": "uuid",
    },
)
class GenaiAgentApiKeyInfos:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        secret_key: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param secret_key: Updated At timestamp for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secret_key GenaiAgent#secret_key}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__564aa1ceae6821db77edf4e07e7588f64d5ed57588fce3ed3d50b096fc854590)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        '''Updated At timestamp for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secret_key GenaiAgent#secret_key}
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentApiKeyInfos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentApiKeyInfosList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentApiKeyInfosList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5f4bb46e3ebcba97a519cd637e5ac42d6e14f495c0b179a676953ced33d540ef)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentApiKeyInfosOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c2fe0973f3dfed0d9a7440c31e53ea69210880a8071de18893b45f892919517e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentApiKeyInfosOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3473f287c971b9134606161db7c6535b68c9d947bbbc56d41604b0441b1e6e0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__840d9b113286ad19a28cd0261e5217b949ec6a11789e979443d0d44efb0b9127)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8590f9a0c388f6604aa99a9da1b7bfced112580df3fb73785d412c4938f0176b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeyInfos]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeyInfos]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeyInfos]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e1ff5f3c56af29c33d14c1f248118eaa150fd94dde44682fe1f3977003e958b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentApiKeyInfosOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentApiKeyInfosOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2c1473e387216405441b30885a29625ca05c88439fa3fe912b095d0114826e50)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSecretKey")
    def reset_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretKey", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretKeyInput")
    def secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4f4212e2ae5c256dc3896d2faa19844152b7054052cc168337e1622beb2f035)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf9b7a3d6688f7dad46bab71230e2f919a4171c4e6d23ebc1f859b3d1c454712)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef234978c8673dfcc1f65fe5870d0e5fa9191c9057af26a1d9ca8051bebcb185)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97bbb21e465882710c57e004d532ef7f06e2767d936a472df0d71a07f28c7e19)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeyInfos]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeyInfos]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeyInfos]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__87aa100e823140284901fa8fb8e9db4bdcc6ad4e3cdc024a98b0a3f43995d9fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentApiKeys",
    jsii_struct_bases=[],
    name_mapping={"api_key": "apiKey"},
)
class GenaiAgentApiKeys:
    def __init__(self, *, api_key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param api_key: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de90b9f1f47cb988a825c9912fda0764ac837e28cb6cf35d787b0cf63b1f7acb)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentApiKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentApiKeysList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentApiKeysList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9ebdf5ff47ae1ec8f216fc92545a4d93336807f2873130b531e1aaffb78f3b48)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentApiKeysOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a74e7484c3cf2340a45b20835a1f98fac07ef1dbca2ff913c47046df287de830)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentApiKeysOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__010c19c8909bdd022e3046eb43bffd478a882c9298f600736d0c62308cc1bd30)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f2be1ca12047418c7a62e0b92d2b0ab0aa03d569d2ce76ef099c4de23bc8d85)
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
            type_hints = typing.get_type_hints(_typecheckingstub__11cc274db16b194eccfe4c64edd34984c46f6bbe88c132cfa211461f76cd8e92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeys]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeys]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeys]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8811cb85c6fe74b5c61dbc160dc36b2e3f46ee1dcf65154bab8969f20e708a94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentApiKeysOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentApiKeysOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a7226514e2c816731a0105123c0e90c2f7c335c09a5d5d85e3ac51ffd785350d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d4e31555e008a358d2fee013ff51d619bc2024d85e7f6c36e8d0717f1f0cde1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeys]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeys]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeys]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31171dfe0f06118da6e1d918a5736ef2c5b4d3864f10e4074499bd7404533432)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChatbot",
    jsii_struct_bases=[],
    name_mapping={
        "button_background_color": "buttonBackgroundColor",
        "logo": "logo",
        "name": "name",
        "primary_color": "primaryColor",
        "secondary_color": "secondaryColor",
        "starting_message": "startingMessage",
    },
)
class GenaiAgentChatbot:
    def __init__(
        self,
        *,
        button_background_color: typing.Optional[builtins.str] = None,
        logo: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        primary_color: typing.Optional[builtins.str] = None,
        secondary_color: typing.Optional[builtins.str] = None,
        starting_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param button_background_color: Background color for the chatbot button. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#button_background_color GenaiAgent#button_background_color}
        :param logo: Logo for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#logo GenaiAgent#logo}
        :param name: Name of the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param primary_color: Primary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#primary_color GenaiAgent#primary_color}
        :param secondary_color: Secondary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secondary_color GenaiAgent#secondary_color}
        :param starting_message: Starting message for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#starting_message GenaiAgent#starting_message}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3b48fa6c77125752b88c1d965b4db4cda3ea1ec45b9b531d39b3f62c09540212)
            check_type(argname="argument button_background_color", value=button_background_color, expected_type=type_hints["button_background_color"])
            check_type(argname="argument logo", value=logo, expected_type=type_hints["logo"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument primary_color", value=primary_color, expected_type=type_hints["primary_color"])
            check_type(argname="argument secondary_color", value=secondary_color, expected_type=type_hints["secondary_color"])
            check_type(argname="argument starting_message", value=starting_message, expected_type=type_hints["starting_message"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if button_background_color is not None:
            self._values["button_background_color"] = button_background_color
        if logo is not None:
            self._values["logo"] = logo
        if name is not None:
            self._values["name"] = name
        if primary_color is not None:
            self._values["primary_color"] = primary_color
        if secondary_color is not None:
            self._values["secondary_color"] = secondary_color
        if starting_message is not None:
            self._values["starting_message"] = starting_message

    @builtins.property
    def button_background_color(self) -> typing.Optional[builtins.str]:
        '''Background color for the chatbot button.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#button_background_color GenaiAgent#button_background_color}
        '''
        result = self._values.get("button_background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logo(self) -> typing.Optional[builtins.str]:
        '''Logo for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#logo GenaiAgent#logo}
        '''
        result = self._values.get("logo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def primary_color(self) -> typing.Optional[builtins.str]:
        '''Primary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#primary_color GenaiAgent#primary_color}
        '''
        result = self._values.get("primary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_color(self) -> typing.Optional[builtins.str]:
        '''Secondary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secondary_color GenaiAgent#secondary_color}
        '''
        result = self._values.get("secondary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def starting_message(self) -> typing.Optional[builtins.str]:
        '''Starting message for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#starting_message GenaiAgent#starting_message}
        '''
        result = self._values.get("starting_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChatbot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChatbotIdentifiers",
    jsii_struct_bases=[],
    name_mapping={},
)
class GenaiAgentChatbotIdentifiers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChatbotIdentifiers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentChatbotIdentifiersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChatbotIdentifiersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__79a3e4b4982d214d08a98760d1adf11d6e716b1dadc772be1feacaa5458e50da)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentChatbotIdentifiersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__878cd1295cb9dd82b920782afe229c5b7abb9689d2cb277b36f7e1e52f316a72)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChatbotIdentifiersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9efd013260f178227e8648103bbee6cb1da5b0de1e36c1b39c677fa1dbe23ddc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7094cd1e00d3bfbdc75a0775ecf67e09c00b58217b26960b67674a94d7868d81)
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
            type_hints = typing.get_type_hints(_typecheckingstub__53a6a7d1d1686adea8435dfc11472b94cf1fec8ac4b661b2a100c85ff75dfa72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbotIdentifiers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbotIdentifiers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbotIdentifiers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31a85f1e7405bc8139ec95d92546215c14ae20425f6d871b66b54a4b661eb62a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChatbotIdentifiersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChatbotIdentifiersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__69b9d8485efbd2078d9f24472df6766b263446c1d32e6578de65d496f664660d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="chatbotId")
    def chatbot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "chatbotId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbotIdentifiers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbotIdentifiers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbotIdentifiers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__670f3f44520e259bf7fda9522c7bce1b8bfce22af66426c4a4f05463080c76e3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChatbotList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChatbotList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9dcd7f16911284d3108d6d5b7cc735e1cd80ab131d35ec0fcd0397274d1352d5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentChatbotOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__278af6605a5e395c67ff045739d60c5e68e682798df17351099a18e929f388ba)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChatbotOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca65b6855b3bb4033b22111bb0382b966ae559aa8dc90bf20646769ce0c8c6e8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d6e7f64c9970bad09e605e5eaebf457d80fceed035cbe014958f239023989b2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8603ec3cc1f5dd254fb39692576430548c418fa2b7fcf8a86b784f53eff938a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbot]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbot]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbot]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6abfea6b9d3ec416f930b9a6adefaf7dd4f668c59a51d9ecdf3ea558266d11b1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChatbotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChatbotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2edb9c2a6754f5471756a30e7324d6eb1e8fb66c92487e41603b49eb8c9068f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetButtonBackgroundColor")
    def reset_button_background_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetButtonBackgroundColor", []))

    @jsii.member(jsii_name="resetLogo")
    def reset_logo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogo", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPrimaryColor")
    def reset_primary_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryColor", []))

    @jsii.member(jsii_name="resetSecondaryColor")
    def reset_secondary_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryColor", []))

    @jsii.member(jsii_name="resetStartingMessage")
    def reset_starting_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartingMessage", []))

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColorInput")
    def button_background_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buttonBackgroundColorInput"))

    @builtins.property
    @jsii.member(jsii_name="logoInput")
    def logo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logoInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryColorInput")
    def primary_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "primaryColorInput"))

    @builtins.property
    @jsii.member(jsii_name="secondaryColorInput")
    def secondary_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secondaryColorInput"))

    @builtins.property
    @jsii.member(jsii_name="startingMessageInput")
    def starting_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startingMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColor")
    def button_background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonBackgroundColor"))

    @button_background_color.setter
    def button_background_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37db94d1dd160f7626c106a076442422afbe4739b1ef14033aaa11112ce1564b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buttonBackgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logo")
    def logo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logo"))

    @logo.setter
    def logo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b61825ccd4a8d0addf4c359f720bf19d9d589c2ec90345106cb0eaffaa5e806d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f69014e8c02b8e4be236c3e0c0c66d778341f826ea1c58b0902ac1d56e93ddd7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryColor")
    def primary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryColor"))

    @primary_color.setter
    def primary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32691138c06f220ac2bd16cb920b75dbf4e20d4ef4d25531297541235e566e06)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryColor")
    def secondary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryColor"))

    @secondary_color.setter
    def secondary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab8677e3ec56f36f8dde1a834a595381a493b2a9c68eadc515c9e09272e67361)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startingMessage")
    def starting_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingMessage"))

    @starting_message.setter
    def starting_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3f62f7688600d178b3910aad332f3e2ae21fcd37aa753c313dc97b933b1c0a3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startingMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbot]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbot]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbot]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8551be7c8cf1a817d498b669c45c55a210254bc9490a7bd8d35dcaeb75e9dfd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgents",
    jsii_struct_bases=[],
    name_mapping={
        "instruction": "instruction",
        "model_uuid": "modelUuid",
        "name": "name",
        "project_id": "projectId",
        "region": "region",
        "anthropic_api_key": "anthropicApiKey",
        "api_key_infos": "apiKeyInfos",
        "api_keys": "apiKeys",
        "chatbot": "chatbot",
        "chatbot_identifiers": "chatbotIdentifiers",
        "deployment": "deployment",
        "description": "description",
    },
)
class GenaiAgentChildAgents:
    def __init__(
        self,
        *,
        instruction: builtins.str,
        model_uuid: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        region: builtins.str,
        anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgentsAnthropicApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgentsApiKeyInfos", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgentsApiKeys", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgentsChatbot", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgentsChatbotIdentifiers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentChildAgentsDeployment", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instruction: Instruction for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        :param model_uuid: Model UUID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        :param name: Name of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param project_id: Project ID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        :param region: Region where the Agent is deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        :param anthropic_api_key: anthropic_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        :param api_key_infos: api_key_infos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        :param api_keys: api_keys block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        :param chatbot: chatbot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        :param chatbot_identifiers: chatbot_identifiers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        :param description: Description for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d169eafe552bfd7016793638009c7609e1d40d95cb64d80062aa23a223899afe)
            check_type(argname="argument instruction", value=instruction, expected_type=type_hints["instruction"])
            check_type(argname="argument model_uuid", value=model_uuid, expected_type=type_hints["model_uuid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
            check_type(argname="argument api_key_infos", value=api_key_infos, expected_type=type_hints["api_key_infos"])
            check_type(argname="argument api_keys", value=api_keys, expected_type=type_hints["api_keys"])
            check_type(argname="argument chatbot", value=chatbot, expected_type=type_hints["chatbot"])
            check_type(argname="argument chatbot_identifiers", value=chatbot_identifiers, expected_type=type_hints["chatbot_identifiers"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instruction": instruction,
            "model_uuid": model_uuid,
            "name": name,
            "project_id": project_id,
            "region": region,
        }
        if anthropic_api_key is not None:
            self._values["anthropic_api_key"] = anthropic_api_key
        if api_key_infos is not None:
            self._values["api_key_infos"] = api_key_infos
        if api_keys is not None:
            self._values["api_keys"] = api_keys
        if chatbot is not None:
            self._values["chatbot"] = chatbot
        if chatbot_identifiers is not None:
            self._values["chatbot_identifiers"] = chatbot_identifiers
        if deployment is not None:
            self._values["deployment"] = deployment
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def instruction(self) -> builtins.str:
        '''Instruction for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        '''
        result = self._values.get("instruction")
        assert result is not None, "Required property 'instruction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_uuid(self) -> builtins.str:
        '''Model UUID of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        '''
        result = self._values.get("model_uuid")
        assert result is not None, "Required property 'model_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Project ID of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Region where the Agent is deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def anthropic_api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsAnthropicApiKey"]]]:
        '''anthropic_api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        '''
        result = self._values.get("anthropic_api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsAnthropicApiKey"]]], result)

    @builtins.property
    def api_key_infos(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsApiKeyInfos"]]]:
        '''api_key_infos block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        '''
        result = self._values.get("api_key_infos")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsApiKeyInfos"]]], result)

    @builtins.property
    def api_keys(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsApiKeys"]]]:
        '''api_keys block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        '''
        result = self._values.get("api_keys")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsApiKeys"]]], result)

    @builtins.property
    def chatbot(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsChatbot"]]]:
        '''chatbot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        '''
        result = self._values.get("chatbot")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsChatbot"]]], result)

    @builtins.property
    def chatbot_identifiers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsChatbotIdentifiers"]]]:
        '''chatbot_identifiers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        '''
        result = self._values.get("chatbot_identifiers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsChatbotIdentifiers"]]], result)

    @builtins.property
    def deployment(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsDeployment"]]]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentChildAgentsDeployment"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsAnthropicApiKey",
    jsii_struct_bases=[],
    name_mapping={"created_by": "createdBy", "name": "name", "uuid": "uuid"},
)
class GenaiAgentChildAgentsAnthropicApiKey:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6acfe5f6e27ccfca6297ec8173fe1059b38d96408909b0cb5bf883d26b99155f)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgentsAnthropicApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentChildAgentsAnthropicApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsAnthropicApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cb9267c90514737f12e1397127a69829bfc6d2bd218f56a68a4de015ff95de51)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentChildAgentsAnthropicApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cded6037ccef18815ab5719e983307101497530187273f287ae1768e76fe4561)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsAnthropicApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae39f4f92959cfd503eada386dd225bf5257a437edeb5c243a10e0e03e8f5c21)
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
            type_hints = typing.get_type_hints(_typecheckingstub__34eb3e1ec536fb7bfc1693e59e72d4eb9d1e19d2253f85d8f57de0a5e660c340)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6ddf7768830c9b8f65113f566ec1cc791c61e71322c9e3d67c75cd3bf868d2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsAnthropicApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsAnthropicApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsAnthropicApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b83ad80bfa648285d19348b4f748359799d4df8d62fe88f4028232c939e100bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsAnthropicApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsAnthropicApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8b6d32b8aedc625c0508f195fef4700424bd932bb0c0a90b5a75f0424ef2566)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bf9a7e880dc95cb7d3bf349a144c85f93c018f6ce9c62ccb8db5f816eba073e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7140732a3bac55f95bd331a786e75ce40cf76e1b6beca2b49aedbc125332b22f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7302504f664d23f8c0230ade6752d5fa3430049fee86db0c7a69e3e6c76f99d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsAnthropicApiKey]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsAnthropicApiKey]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsAnthropicApiKey]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eb4f8869a22459022299210c13594b609204e72661b2cb769b5af9237126933e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsApiKeyInfos",
    jsii_struct_bases=[],
    name_mapping={
        "created_by": "createdBy",
        "name": "name",
        "secret_key": "secretKey",
        "uuid": "uuid",
    },
)
class GenaiAgentChildAgentsApiKeyInfos:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        secret_key: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param secret_key: Updated At timestamp for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secret_key GenaiAgent#secret_key}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bed0ddfebdd50fb65a71698cb95aa81b09001b83be36f6f5b00c7925a636448f)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        '''Updated At timestamp for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secret_key GenaiAgent#secret_key}
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgentsApiKeyInfos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentChildAgentsApiKeyInfosList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsApiKeyInfosList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9f9b3f2ddcd671f6a311f893398dbe62f497255bab90e571da286ee6322d20f7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentChildAgentsApiKeyInfosOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1cbe40d4139f3092bb78b6fdb7b839c995774f5511ebf11a327e22d155939e2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsApiKeyInfosOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3493419117b3f54aca4e10e56b102afdee6d2c9bb71b27d3b11a5c0415ec83a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1e66b0aef97f1e0e4df91f79a901708e0d3cccc7fda5c203f3f44004a1f221d9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__14f54bb025d5dc0b8a33cbc1a1e7b8cbd74597af87432278717764cf74cdb945)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeyInfos]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeyInfos]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeyInfos]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__367424808c3740dad43f442e56252acd46d663a6e92b27a07a9749ad63be516a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsApiKeyInfosOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsApiKeyInfosOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f79d8212d77cbe6b80caea0dbb10b679989e3750ad1f40baa97e455d536f701f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSecretKey")
    def reset_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretKey", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretKeyInput")
    def secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c666545537de88d4b4996fd735678d2bd44418a0933638cae657b0ec672979c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1afe18f79a6364baec4849e611a5a0f7dd7a5b1dbf5a6a9048f83cb02a2c57ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d3b5e63d28b3651f66250ee8ea60c149660ebfb569c59f3f3435bc4e4f2fc16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fbfeff4c1c9f254317fae1a57822d68e88cb17cbdf4482d839555cc2329a9ee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeyInfos]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeyInfos]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeyInfos]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d919775cf4ecae36ce709bc27496f7a427bf215b6520870326da6ff5d58e3b1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsApiKeys",
    jsii_struct_bases=[],
    name_mapping={"api_key": "apiKey"},
)
class GenaiAgentChildAgentsApiKeys:
    def __init__(self, *, api_key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param api_key: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e063fe8ad92a99ba5c03752d4b1a10e4f2d40789415379364ce5f3fcdfeda90f)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgentsApiKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentChildAgentsApiKeysList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsApiKeysList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8389dd8819f287be73bfacd0f3c5ea3be013c4f48339310b7c164a71c213ea77)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentChildAgentsApiKeysOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed4888a77679a2d545324334ea71bf14d349289d4fd8274febd5039e37e8fb39)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsApiKeysOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a996e8bb136b90428108fe3c6ff7e836039b8ef983af68f1d4d4bbc97131ec8f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__639efeb4e7ff2ea271bed3bd93ba676e41bde704f7255e9f3028e50f381f0a86)
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
            type_hints = typing.get_type_hints(_typecheckingstub__505e67ec0ee06cfe043db42b0df95ac4237f81ad644240e599bbfbcb0fa55f85)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeys]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeys]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeys]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab02b0465a4604ba93dc507ef950d2e0584e2f0078cc302c9d8c2c8caf17345e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsApiKeysOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsApiKeysOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c28ef3b34805456e9d87fab89c63cafdccd9988990b5cb3ba212e7497aaa8c20)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6f4574c7ca06f316b86ac9c159ea4c8eb39811c542b4ccdead1093740e3e96e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeys]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeys]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeys]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4065a00b0edc0467ab34b019d33ccd4ee3f9f8d984c6219f6dafe92bbc9f217c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsChatbot",
    jsii_struct_bases=[],
    name_mapping={
        "button_background_color": "buttonBackgroundColor",
        "logo": "logo",
        "name": "name",
        "primary_color": "primaryColor",
        "secondary_color": "secondaryColor",
        "starting_message": "startingMessage",
    },
)
class GenaiAgentChildAgentsChatbot:
    def __init__(
        self,
        *,
        button_background_color: typing.Optional[builtins.str] = None,
        logo: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        primary_color: typing.Optional[builtins.str] = None,
        secondary_color: typing.Optional[builtins.str] = None,
        starting_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param button_background_color: Background color for the chatbot button. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#button_background_color GenaiAgent#button_background_color}
        :param logo: Logo for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#logo GenaiAgent#logo}
        :param name: Name of the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param primary_color: Primary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#primary_color GenaiAgent#primary_color}
        :param secondary_color: Secondary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secondary_color GenaiAgent#secondary_color}
        :param starting_message: Starting message for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#starting_message GenaiAgent#starting_message}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__74d855fc08af425a2e2044b6337850c97a4ccd2cd1065c028ddbaf28542e1c67)
            check_type(argname="argument button_background_color", value=button_background_color, expected_type=type_hints["button_background_color"])
            check_type(argname="argument logo", value=logo, expected_type=type_hints["logo"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument primary_color", value=primary_color, expected_type=type_hints["primary_color"])
            check_type(argname="argument secondary_color", value=secondary_color, expected_type=type_hints["secondary_color"])
            check_type(argname="argument starting_message", value=starting_message, expected_type=type_hints["starting_message"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if button_background_color is not None:
            self._values["button_background_color"] = button_background_color
        if logo is not None:
            self._values["logo"] = logo
        if name is not None:
            self._values["name"] = name
        if primary_color is not None:
            self._values["primary_color"] = primary_color
        if secondary_color is not None:
            self._values["secondary_color"] = secondary_color
        if starting_message is not None:
            self._values["starting_message"] = starting_message

    @builtins.property
    def button_background_color(self) -> typing.Optional[builtins.str]:
        '''Background color for the chatbot button.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#button_background_color GenaiAgent#button_background_color}
        '''
        result = self._values.get("button_background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logo(self) -> typing.Optional[builtins.str]:
        '''Logo for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#logo GenaiAgent#logo}
        '''
        result = self._values.get("logo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def primary_color(self) -> typing.Optional[builtins.str]:
        '''Primary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#primary_color GenaiAgent#primary_color}
        '''
        result = self._values.get("primary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_color(self) -> typing.Optional[builtins.str]:
        '''Secondary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secondary_color GenaiAgent#secondary_color}
        '''
        result = self._values.get("secondary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def starting_message(self) -> typing.Optional[builtins.str]:
        '''Starting message for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#starting_message GenaiAgent#starting_message}
        '''
        result = self._values.get("starting_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgentsChatbot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsChatbotIdentifiers",
    jsii_struct_bases=[],
    name_mapping={},
)
class GenaiAgentChildAgentsChatbotIdentifiers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgentsChatbotIdentifiers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentChildAgentsChatbotIdentifiersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsChatbotIdentifiersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__038649f18bab9dc8ff641c3ad57c3a2600241ed30c8fb3f45a249613944ed46c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentChildAgentsChatbotIdentifiersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ac2676bd377f3e04f485381aaa4e727edf5939597fe4aad879abe537ec3cc22)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsChatbotIdentifiersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61bf6a093a09658244b59d774faf565360e218e105625ebe5a128359c5f8092b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b9161d2cf3738df24c62882a04d76092afe7b2f90b37c2a947e15ec79327fe4f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__daa7e557bbedb38d86a444e77b1d6011cdd6ec4b208ab1b6cb3c085173267d2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbotIdentifiers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbotIdentifiers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbotIdentifiers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea1b115019572f92a67b414bd9a32b8d6b50cd8bc2af68fb658682fafd07856a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsChatbotIdentifiersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsChatbotIdentifiersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e0f5e8e9b05754c50d10de53ec0c39986321dd0cc0bb75d29cb4478fa34a7dcb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="chatbotId")
    def chatbot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "chatbotId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbotIdentifiers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbotIdentifiers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbotIdentifiers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__246a472d3987106133763cb60c64b88cd5d7b97dfacc14661ee73ad0eb0d5286)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsChatbotList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsChatbotList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b1da78e0e8361326c458684e7d19a717df5267c56d8b89d881265e434f86f183)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentChildAgentsChatbotOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b05bb5c69c639378c5cef533630543b6e137936f1e7699e49c66478773d0fd5f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsChatbotOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0bb3a36987f259568b9efaad3fe073243098e240e6dfefa92d5adecfdacad5e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3cd5997c56ada02dcf3681715de2d206b9244239d5726c17c037e003b18ceb43)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a35d17e44c72000ae52f1fcdcc642165153e530d1c7c331a36e99ebad8308c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbot]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbot]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbot]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b8d842cdb744bb82da098d03b446e945d02dd80b6d5f22983e583e824b8f5620)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsChatbotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsChatbotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__10a8f087250402fe6771d299d1a55e4e2125c908a15a7bb03cb7e41533401642)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetButtonBackgroundColor")
    def reset_button_background_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetButtonBackgroundColor", []))

    @jsii.member(jsii_name="resetLogo")
    def reset_logo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogo", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPrimaryColor")
    def reset_primary_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryColor", []))

    @jsii.member(jsii_name="resetSecondaryColor")
    def reset_secondary_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryColor", []))

    @jsii.member(jsii_name="resetStartingMessage")
    def reset_starting_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartingMessage", []))

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColorInput")
    def button_background_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buttonBackgroundColorInput"))

    @builtins.property
    @jsii.member(jsii_name="logoInput")
    def logo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logoInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryColorInput")
    def primary_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "primaryColorInput"))

    @builtins.property
    @jsii.member(jsii_name="secondaryColorInput")
    def secondary_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secondaryColorInput"))

    @builtins.property
    @jsii.member(jsii_name="startingMessageInput")
    def starting_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startingMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColor")
    def button_background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonBackgroundColor"))

    @button_background_color.setter
    def button_background_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__330b609f80b8bcd331f9f6055f2a24940ebde40e0c5508322f5de4f5cb06b382)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buttonBackgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logo")
    def logo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logo"))

    @logo.setter
    def logo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86266f03beeb10239e8d5cc949f35b1e74e493c6e317e07358fc6879094defa8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97d7a9325890cb2214b83c101b6d9ffcebf66d6cd857095ebbda90bee0479298)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryColor")
    def primary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryColor"))

    @primary_color.setter
    def primary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae532fd14f4a8bf0e4d44e6d2e9cd5832a814bcf910dbe12105cd1ae0c13d3cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryColor")
    def secondary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryColor"))

    @secondary_color.setter
    def secondary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48e066cc04a0ba1242a70d31a74bc5e52a6e0665b948965c12df8d64336f2532)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startingMessage")
    def starting_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingMessage"))

    @starting_message.setter
    def starting_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f8d0fa1e832b93d7e102f96bf1d4f5d45ed45c5d8884a82e82fffcfb0299723a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startingMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbot]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbot]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbot]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49185662c13695ff29f5d310caaa7110c4a8b9977a66e80b29641570304beb7f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "status": "status",
        "url": "url",
        "uuid": "uuid",
        "visibility": "visibility",
    },
)
class GenaiAgentChildAgentsDeployment:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        visibility: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param status: Status of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#status GenaiAgent#status}
        :param url: Url of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        :param visibility: Visibility of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#visibility GenaiAgent#visibility}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d54e4276bf728eccce57cd78723f2a0fcfcccef573ef5a9f67e65fa0949ad78)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument visibility", value=visibility, expected_type=type_hints["visibility"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if status is not None:
            self._values["status"] = status
        if url is not None:
            self._values["url"] = url
        if uuid is not None:
            self._values["uuid"] = uuid
        if visibility is not None:
            self._values["visibility"] = visibility

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Status of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#status GenaiAgent#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Url of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Visibility of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#visibility GenaiAgent#visibility}
        '''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentChildAgentsDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentChildAgentsDeploymentList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsDeploymentList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f40c556fe5bf0c32c16d5b70e15697b8e86cee80d0c698d7c0abcb59e4d83a70)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentChildAgentsDeploymentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa1d008119ea0dfbc0466ba8a5e645dcc8b3870d7b8cc94242e18bbf38ceb8e7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsDeploymentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24645c3758a82d9470f7f8fc49b5a9e9475d5a98157b7e2d112e5cd3fea5ac4c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2050b2b6f8981ddf2fe4e4d0ee7432e4f9a4812b3bfae4ef6147adb6c1cc3f2e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__66fb1dda78e3b331d678a0727b5d170c20ef912a13cffe7bded95cd9e63584b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsDeployment]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsDeployment]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsDeployment]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__716111a5d6724aab55b14ad363591a75b72e3306521f1f6c7deb6b7d83702508)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b75d0c8d09d2a432b2fb8c74f48ea0dea1b49d350f66b95acca210b6fc29dbbf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @jsii.member(jsii_name="resetVisibility")
    def reset_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibility", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="visibilityInput")
    def visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "visibilityInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dc9d3cf945ac666fb6124d1b0cbb148bd51a8eb81b35166bf5fdc075a3a08050)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__896eb5bea0e9680e80aa117d4ccec768b04a4b6e66d26ca093e5092375d12c22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a7219ad383438d8e06252d5dd16517005732fa5852db083f145b93bc4cf021b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b900d68e9b4412d1a22a93989a378edfc79487fa0855c9afe6a3ae1d41626f69)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63f4d1bb22ba00ee6fc41df2a9b1c64ca4f485402c4236f3f860c76d21645162)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibility", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsDeployment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsDeployment]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsDeployment]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9fee7866719b70d243235ea851982c2b1f7f2868720971626bd132b039d526d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e966efa6581b6658a0db60d74a233db1276bd72c9e312d7c041a73082da7b91a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentChildAgentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf6e8e0edc46614dbdc2e7cfa6e02ee3c71eeb439d4b3639bf0bcd85f8495c33)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentChildAgentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__58f03c8a2b64457b5b886b27d4d1c2d0f47b02376f21a2d2c2f2c862f5450216)
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
            type_hints = typing.get_type_hints(_typecheckingstub__979b6318e18a2fdc0cde5b9f930fb0676c1d9ae2d84eea9a3554aa905757bb09)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6818b677db392015ac0628e8fe1a6d0d5602900c9b2fd9eccfbd0f5b7776330a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgents]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgents]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgents]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16930b1a4d4dbbdc501f9f46df4bb38bce681567a5ddf31e85667b3246b89660)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentChildAgentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentChildAgentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0f96413c57fd4ae3e03a4e6ccb0beae2cc4d27bf8ce9d9e1025fed609195ca1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnthropicApiKey")
    def put_anthropic_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__864335562f30fff6b6fc3783227380885842056f2f933470e29648bec6cf3744)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnthropicApiKey", [value]))

    @jsii.member(jsii_name="putApiKeyInfos")
    def put_api_key_infos(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b1713ace72f234d0821f69f25a46769376b2ab576fc3876f29f22de558f38b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeyInfos", [value]))

    @jsii.member(jsii_name="putApiKeys")
    def put_api_keys(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsApiKeys, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__42d5e6e2ac60061c5d29b06651379a79b8041f188c826434f8043cc7972903fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeys", [value]))

    @jsii.member(jsii_name="putChatbot")
    def put_chatbot(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsChatbot, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ad4a0897549c768cbcf42053a90bcf9d98fe2fd61e8f06590fb5e2bf3658fb22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbot", [value]))

    @jsii.member(jsii_name="putChatbotIdentifiers")
    def put_chatbot_identifiers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__474c2df064be6fa22b3664034aa7f8872949ad6ac99cc2d9ef1f0ceffc2aaa2c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbotIdentifiers", [value]))

    @jsii.member(jsii_name="putDeployment")
    def put_deployment(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsDeployment, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ac4b81016355056b89953707395eeb3362c6dace92f88a1558b809044cee888)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDeployment", [value]))

    @jsii.member(jsii_name="resetAnthropicApiKey")
    def reset_anthropic_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicApiKey", []))

    @jsii.member(jsii_name="resetApiKeyInfos")
    def reset_api_key_infos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeyInfos", []))

    @jsii.member(jsii_name="resetApiKeys")
    def reset_api_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeys", []))

    @jsii.member(jsii_name="resetChatbot")
    def reset_chatbot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbot", []))

    @jsii.member(jsii_name="resetChatbotIdentifiers")
    def reset_chatbot_identifiers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbotIdentifiers", []))

    @jsii.member(jsii_name="resetDeployment")
    def reset_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeployment", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @builtins.property
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentId"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(self) -> GenaiAgentChildAgentsAnthropicApiKeyList:
        return typing.cast(GenaiAgentChildAgentsAnthropicApiKeyList, jsii.get(self, "anthropicApiKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfos")
    def api_key_infos(self) -> GenaiAgentChildAgentsApiKeyInfosList:
        return typing.cast(GenaiAgentChildAgentsApiKeyInfosList, jsii.get(self, "apiKeyInfos"))

    @builtins.property
    @jsii.member(jsii_name="apiKeys")
    def api_keys(self) -> GenaiAgentChildAgentsApiKeysList:
        return typing.cast(GenaiAgentChildAgentsApiKeysList, jsii.get(self, "apiKeys"))

    @builtins.property
    @jsii.member(jsii_name="chatbot")
    def chatbot(self) -> GenaiAgentChildAgentsChatbotList:
        return typing.cast(GenaiAgentChildAgentsChatbotList, jsii.get(self, "chatbot"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiers")
    def chatbot_identifiers(self) -> GenaiAgentChildAgentsChatbotIdentifiersList:
        return typing.cast(GenaiAgentChildAgentsChatbotIdentifiersList, jsii.get(self, "chatbotIdentifiers"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> GenaiAgentChildAgentsDeploymentList:
        return typing.cast(GenaiAgentChildAgentsDeploymentList, jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyInput")
    def anthropic_api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsAnthropicApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsAnthropicApiKey]]], jsii.get(self, "anthropicApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfosInput")
    def api_key_infos_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeyInfos]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeyInfos]]], jsii.get(self, "apiKeyInfosInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeysInput")
    def api_keys_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeys]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeys]]], jsii.get(self, "apiKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiersInput")
    def chatbot_identifiers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbotIdentifiers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbotIdentifiers]]], jsii.get(self, "chatbotIdentifiersInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotInput")
    def chatbot_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbot]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbot]]], jsii.get(self, "chatbotInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsDeployment]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsDeployment]]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="instructionInput")
    def instruction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instructionInput"))

    @builtins.property
    @jsii.member(jsii_name="modelUuidInput")
    def model_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelUuidInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd0d902c2cda4500ba557b0389bed9f6f1bc2ec93b2d9677090b03124ac055ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @instruction.setter
    def instruction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8cafd360c4eeaa08e33721e6e7a2a7bc58e126e0b6f229a52db2333e38ccc625)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instruction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelUuid")
    def model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelUuid"))

    @model_uuid.setter
    def model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__27356f093cfd5973b5109da874f7ae6de416cae1a35f3938073a77cdf7352498)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f496df4e6d5e9a2a2516e8d92cb3567be356db52f8b54ce8e62ac610dcae877)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6ccb279c0d3d24e814a29e4bdbcdb81514a84d68404066e428ef5f38656805b6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73c8f9fdeb4957426d148a770457cd2e7a4d472b8a8daed828cdde4be4658862)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgents]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgents]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgents]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__32d7110dddaa9870a7fa5baa37e297f72cbad4ea467836e8bc9d3eb60caebbc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "instruction": "instruction",
        "model_uuid": "modelUuid",
        "name": "name",
        "project_id": "projectId",
        "region": "region",
        "agent_guardrail": "agentGuardrail",
        "anthropic_api_key": "anthropicApiKey",
        "anthropic_key_uuid": "anthropicKeyUuid",
        "api_key_infos": "apiKeyInfos",
        "api_keys": "apiKeys",
        "chatbot": "chatbot",
        "chatbot_identifiers": "chatbotIdentifiers",
        "child_agents": "childAgents",
        "created_at": "createdAt",
        "deployment": "deployment",
        "description": "description",
        "functions": "functions",
        "id": "id",
        "if_case": "ifCase",
        "k": "k",
        "knowledge_bases": "knowledgeBases",
        "knowledge_base_uuid": "knowledgeBaseUuid",
        "max_tokens": "maxTokens",
        "model": "model",
        "open_ai_api_key": "openAiApiKey",
        "open_ai_key_uuid": "openAiKeyUuid",
        "parent_agents": "parentAgents",
        "provide_citations": "provideCitations",
        "retrieval_method": "retrievalMethod",
        "route_created_by": "routeCreatedBy",
        "route_name": "routeName",
        "route_uuid": "routeUuid",
        "tags": "tags",
        "temperature": "temperature",
        "template": "template",
        "top_p": "topP",
        "url": "url",
        "user_id": "userId",
    },
)
class GenaiAgentConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        instruction: builtins.str,
        model_uuid: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        region: builtins.str,
        agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_key_uuid: typing.Optional[builtins.str] = None,
        api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
        child_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgents, typing.Dict[builtins.str, typing.Any]]]]] = None,
        created_at: typing.Optional[builtins.str] = None,
        deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentDeployment", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentFunctions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        if_case: typing.Optional[builtins.str] = None,
        k: typing.Optional[jsii.Number] = None,
        knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        knowledge_base_uuid: typing.Optional[typing.Sequence[builtins.str]] = None,
        max_tokens: typing.Optional[jsii.Number] = None,
        model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentOpenAiApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        open_ai_key_uuid: typing.Optional[builtins.str] = None,
        parent_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgents", typing.Dict[builtins.str, typing.Any]]]]] = None,
        provide_citations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        retrieval_method: typing.Optional[builtins.str] = None,
        route_created_by: typing.Optional[builtins.str] = None,
        route_name: typing.Optional[builtins.str] = None,
        route_uuid: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        temperature: typing.Optional[jsii.Number] = None,
        template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplate", typing.Dict[builtins.str, typing.Any]]]]] = None,
        top_p: typing.Optional[jsii.Number] = None,
        url: typing.Optional[builtins.str] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param instruction: Instruction for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        :param model_uuid: Model UUID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        :param name: Name of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param project_id: Project ID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        :param region: Region where the Agent is deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        :param agent_guardrail: agent_guardrail block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agent_guardrail GenaiAgent#agent_guardrail}
        :param anthropic_api_key: anthropic_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        :param anthropic_key_uuid: Optional Anthropic API key ID to use with Anthropic models. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_key_uuid GenaiAgent#anthropic_key_uuid}
        :param api_key_infos: api_key_infos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        :param api_keys: api_keys block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        :param chatbot: chatbot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        :param chatbot_identifiers: chatbot_identifiers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        :param child_agents: child_agents block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#child_agents GenaiAgent#child_agents}
        :param created_at: Timestamp when the Agent was created. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_at GenaiAgent#created_at}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        :param description: Description for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param functions: functions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#functions GenaiAgent#functions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#id GenaiAgent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param if_case: If case condition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#if_case GenaiAgent#if_case}
        :param k: K value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#k GenaiAgent#k}
        :param knowledge_bases: knowledge_bases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_bases GenaiAgent#knowledge_bases}
        :param knowledge_base_uuid: Ids of the knowledge base(s) to attach to the agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_base_uuid GenaiAgent#knowledge_base_uuid}
        :param max_tokens: Maximum tokens allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#max_tokens GenaiAgent#max_tokens}
        :param model: model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model GenaiAgent#model}
        :param open_ai_api_key: open_ai_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#open_ai_api_key GenaiAgent#open_ai_api_key}
        :param open_ai_key_uuid: Optional OpenAI API key ID to use with OpenAI models. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#open_ai_key_uuid GenaiAgent#open_ai_key_uuid}
        :param parent_agents: parent_agents block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_agents GenaiAgent#parent_agents}
        :param provide_citations: Indicates if the agent should provide citations in responses. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provide_citations GenaiAgent#provide_citations}
        :param retrieval_method: Retrieval method used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#retrieval_method GenaiAgent#retrieval_method}
        :param route_created_by: User who created the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_created_by GenaiAgent#route_created_by}
        :param route_name: Route name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_name GenaiAgent#route_name}
        :param route_uuid: Route UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_uuid GenaiAgent#route_uuid}
        :param tags: List of Tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        :param temperature: Agent temperature setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#temperature GenaiAgent#temperature}
        :param template: template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#template GenaiAgent#template}
        :param top_p: Top P sampling parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#top_p GenaiAgent#top_p}
        :param url: URL for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param user_id: User ID linked with the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53b789a8f0aeb7446f6a9eb27d8409f1dd3be1708387d6fb2a1b10a316cb94ea)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument instruction", value=instruction, expected_type=type_hints["instruction"])
            check_type(argname="argument model_uuid", value=model_uuid, expected_type=type_hints["model_uuid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument agent_guardrail", value=agent_guardrail, expected_type=type_hints["agent_guardrail"])
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
            check_type(argname="argument anthropic_key_uuid", value=anthropic_key_uuid, expected_type=type_hints["anthropic_key_uuid"])
            check_type(argname="argument api_key_infos", value=api_key_infos, expected_type=type_hints["api_key_infos"])
            check_type(argname="argument api_keys", value=api_keys, expected_type=type_hints["api_keys"])
            check_type(argname="argument chatbot", value=chatbot, expected_type=type_hints["chatbot"])
            check_type(argname="argument chatbot_identifiers", value=chatbot_identifiers, expected_type=type_hints["chatbot_identifiers"])
            check_type(argname="argument child_agents", value=child_agents, expected_type=type_hints["child_agents"])
            check_type(argname="argument created_at", value=created_at, expected_type=type_hints["created_at"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument functions", value=functions, expected_type=type_hints["functions"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument if_case", value=if_case, expected_type=type_hints["if_case"])
            check_type(argname="argument k", value=k, expected_type=type_hints["k"])
            check_type(argname="argument knowledge_bases", value=knowledge_bases, expected_type=type_hints["knowledge_bases"])
            check_type(argname="argument knowledge_base_uuid", value=knowledge_base_uuid, expected_type=type_hints["knowledge_base_uuid"])
            check_type(argname="argument max_tokens", value=max_tokens, expected_type=type_hints["max_tokens"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument open_ai_api_key", value=open_ai_api_key, expected_type=type_hints["open_ai_api_key"])
            check_type(argname="argument open_ai_key_uuid", value=open_ai_key_uuid, expected_type=type_hints["open_ai_key_uuid"])
            check_type(argname="argument parent_agents", value=parent_agents, expected_type=type_hints["parent_agents"])
            check_type(argname="argument provide_citations", value=provide_citations, expected_type=type_hints["provide_citations"])
            check_type(argname="argument retrieval_method", value=retrieval_method, expected_type=type_hints["retrieval_method"])
            check_type(argname="argument route_created_by", value=route_created_by, expected_type=type_hints["route_created_by"])
            check_type(argname="argument route_name", value=route_name, expected_type=type_hints["route_name"])
            check_type(argname="argument route_uuid", value=route_uuid, expected_type=type_hints["route_uuid"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument temperature", value=temperature, expected_type=type_hints["temperature"])
            check_type(argname="argument template", value=template, expected_type=type_hints["template"])
            check_type(argname="argument top_p", value=top_p, expected_type=type_hints["top_p"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instruction": instruction,
            "model_uuid": model_uuid,
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
        if agent_guardrail is not None:
            self._values["agent_guardrail"] = agent_guardrail
        if anthropic_api_key is not None:
            self._values["anthropic_api_key"] = anthropic_api_key
        if anthropic_key_uuid is not None:
            self._values["anthropic_key_uuid"] = anthropic_key_uuid
        if api_key_infos is not None:
            self._values["api_key_infos"] = api_key_infos
        if api_keys is not None:
            self._values["api_keys"] = api_keys
        if chatbot is not None:
            self._values["chatbot"] = chatbot
        if chatbot_identifiers is not None:
            self._values["chatbot_identifiers"] = chatbot_identifiers
        if child_agents is not None:
            self._values["child_agents"] = child_agents
        if created_at is not None:
            self._values["created_at"] = created_at
        if deployment is not None:
            self._values["deployment"] = deployment
        if description is not None:
            self._values["description"] = description
        if functions is not None:
            self._values["functions"] = functions
        if id is not None:
            self._values["id"] = id
        if if_case is not None:
            self._values["if_case"] = if_case
        if k is not None:
            self._values["k"] = k
        if knowledge_bases is not None:
            self._values["knowledge_bases"] = knowledge_bases
        if knowledge_base_uuid is not None:
            self._values["knowledge_base_uuid"] = knowledge_base_uuid
        if max_tokens is not None:
            self._values["max_tokens"] = max_tokens
        if model is not None:
            self._values["model"] = model
        if open_ai_api_key is not None:
            self._values["open_ai_api_key"] = open_ai_api_key
        if open_ai_key_uuid is not None:
            self._values["open_ai_key_uuid"] = open_ai_key_uuid
        if parent_agents is not None:
            self._values["parent_agents"] = parent_agents
        if provide_citations is not None:
            self._values["provide_citations"] = provide_citations
        if retrieval_method is not None:
            self._values["retrieval_method"] = retrieval_method
        if route_created_by is not None:
            self._values["route_created_by"] = route_created_by
        if route_name is not None:
            self._values["route_name"] = route_name
        if route_uuid is not None:
            self._values["route_uuid"] = route_uuid
        if tags is not None:
            self._values["tags"] = tags
        if temperature is not None:
            self._values["temperature"] = temperature
        if template is not None:
            self._values["template"] = template
        if top_p is not None:
            self._values["top_p"] = top_p
        if url is not None:
            self._values["url"] = url
        if user_id is not None:
            self._values["user_id"] = user_id

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
    def instruction(self) -> builtins.str:
        '''Instruction for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        '''
        result = self._values.get("instruction")
        assert result is not None, "Required property 'instruction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_uuid(self) -> builtins.str:
        '''Model UUID of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        '''
        result = self._values.get("model_uuid")
        assert result is not None, "Required property 'model_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Project ID of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Region where the Agent is deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_guardrail(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAgentGuardrail]]]:
        '''agent_guardrail block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agent_guardrail GenaiAgent#agent_guardrail}
        '''
        result = self._values.get("agent_guardrail")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAgentGuardrail]]], result)

    @builtins.property
    def anthropic_api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAnthropicApiKey]]]:
        '''anthropic_api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        '''
        result = self._values.get("anthropic_api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAnthropicApiKey]]], result)

    @builtins.property
    def anthropic_key_uuid(self) -> typing.Optional[builtins.str]:
        '''Optional Anthropic API key ID to use with Anthropic models.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_key_uuid GenaiAgent#anthropic_key_uuid}
        '''
        result = self._values.get("anthropic_key_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def api_key_infos(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeyInfos]]]:
        '''api_key_infos block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        '''
        result = self._values.get("api_key_infos")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeyInfos]]], result)

    @builtins.property
    def api_keys(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeys]]]:
        '''api_keys block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        '''
        result = self._values.get("api_keys")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeys]]], result)

    @builtins.property
    def chatbot(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbot]]]:
        '''chatbot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        '''
        result = self._values.get("chatbot")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbot]]], result)

    @builtins.property
    def chatbot_identifiers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbotIdentifiers]]]:
        '''chatbot_identifiers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        '''
        result = self._values.get("chatbot_identifiers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbotIdentifiers]]], result)

    @builtins.property
    def child_agents(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgents]]]:
        '''child_agents block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#child_agents GenaiAgent#child_agents}
        '''
        result = self._values.get("child_agents")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgents]]], result)

    @builtins.property
    def created_at(self) -> typing.Optional[builtins.str]:
        '''Timestamp when the Agent was created.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_at GenaiAgent#created_at}
        '''
        result = self._values.get("created_at")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def deployment(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentDeployment"]]]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentDeployment"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def functions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentFunctions"]]]:
        '''functions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#functions GenaiAgent#functions}
        '''
        result = self._values.get("functions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentFunctions"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#id GenaiAgent#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def if_case(self) -> typing.Optional[builtins.str]:
        '''If case condition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#if_case GenaiAgent#if_case}
        '''
        result = self._values.get("if_case")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k(self) -> typing.Optional[jsii.Number]:
        '''K value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#k GenaiAgent#k}
        '''
        result = self._values.get("k")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def knowledge_bases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentKnowledgeBases"]]]:
        '''knowledge_bases block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_bases GenaiAgent#knowledge_bases}
        '''
        result = self._values.get("knowledge_bases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentKnowledgeBases"]]], result)

    @builtins.property
    def knowledge_base_uuid(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Ids of the knowledge base(s) to attach to the agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_base_uuid GenaiAgent#knowledge_base_uuid}
        '''
        result = self._values.get("knowledge_base_uuid")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def max_tokens(self) -> typing.Optional[jsii.Number]:
        '''Maximum tokens allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#max_tokens GenaiAgent#max_tokens}
        '''
        result = self._values.get("max_tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def model(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModel"]]]:
        '''model block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model GenaiAgent#model}
        '''
        result = self._values.get("model")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModel"]]], result)

    @builtins.property
    def open_ai_api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentOpenAiApiKey"]]]:
        '''open_ai_api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#open_ai_api_key GenaiAgent#open_ai_api_key}
        '''
        result = self._values.get("open_ai_api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentOpenAiApiKey"]]], result)

    @builtins.property
    def open_ai_key_uuid(self) -> typing.Optional[builtins.str]:
        '''Optional OpenAI API key ID to use with OpenAI models.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#open_ai_key_uuid GenaiAgent#open_ai_key_uuid}
        '''
        result = self._values.get("open_ai_key_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_agents(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgents"]]]:
        '''parent_agents block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_agents GenaiAgent#parent_agents}
        '''
        result = self._values.get("parent_agents")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgents"]]], result)

    @builtins.property
    def provide_citations(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the agent should provide citations in responses.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provide_citations GenaiAgent#provide_citations}
        '''
        result = self._values.get("provide_citations")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def retrieval_method(self) -> typing.Optional[builtins.str]:
        '''Retrieval method used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#retrieval_method GenaiAgent#retrieval_method}
        '''
        result = self._values.get("retrieval_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_created_by(self) -> typing.Optional[builtins.str]:
        '''User who created the route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_created_by GenaiAgent#route_created_by}
        '''
        result = self._values.get("route_created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_name(self) -> typing.Optional[builtins.str]:
        '''Route name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_name GenaiAgent#route_name}
        '''
        result = self._values.get("route_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_uuid(self) -> typing.Optional[builtins.str]:
        '''Route UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#route_uuid GenaiAgent#route_uuid}
        '''
        result = self._values.get("route_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def temperature(self) -> typing.Optional[jsii.Number]:
        '''Agent temperature setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#temperature GenaiAgent#temperature}
        '''
        result = self._values.get("temperature")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def template(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplate"]]]:
        '''template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#template GenaiAgent#template}
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplate"]]], result)

    @builtins.property
    def top_p(self) -> typing.Optional[jsii.Number]:
        '''Top P sampling parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#top_p GenaiAgent#top_p}
        '''
        result = self._values.get("top_p")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''User ID linked with the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "status": "status",
        "url": "url",
        "uuid": "uuid",
        "visibility": "visibility",
    },
)
class GenaiAgentDeployment:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        visibility: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param status: Status of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#status GenaiAgent#status}
        :param url: Url of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        :param visibility: Visibility of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#visibility GenaiAgent#visibility}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4534a93bd1883fad37e18129490a8f6a482ec69784870cc66c2db63115446bd0)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument visibility", value=visibility, expected_type=type_hints["visibility"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if status is not None:
            self._values["status"] = status
        if url is not None:
            self._values["url"] = url
        if uuid is not None:
            self._values["uuid"] = uuid
        if visibility is not None:
            self._values["visibility"] = visibility

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Status of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#status GenaiAgent#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Url of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Visibility of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#visibility GenaiAgent#visibility}
        '''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentDeploymentList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentDeploymentList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1ccf37bf2e374148d5ff17f5b90be9e7b2958eaefb5395b0a77b285ddb9381f6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentDeploymentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa5daa144ec32688b63376d3c4e24bdb74524fdb0cd06ad6510a560711a7fa53)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentDeploymentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a51690f4d4c74c55c257bd3e84206e9bcc643a65cd6b9f9e939d4cff1328265)
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
            type_hints = typing.get_type_hints(_typecheckingstub__56b2b03af9c50ef3493f202ff7e4d0b21e2bc54ad187b9dff9cc6ef3302bfa5a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4701bfead870635c21ede6e6eeeb823745230c26c447881bddd08950db08531b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentDeployment]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentDeployment]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentDeployment]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6772cf8418ddf7ebc764376ded46e0ba2ee500f2d632467884e04fb1a38c1b5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f19778e44b1ecc1ff14982484cf2b029ca017e5da9e0a7bc5130e8a6ba991f58)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @jsii.member(jsii_name="resetVisibility")
    def reset_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibility", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="visibilityInput")
    def visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "visibilityInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bfaf6dee0dcf8dc63c51600d72791daab3e109321afa58ec989a98536027d937)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d5951fa0acdba6659c9a0315e1e6debed83aaedb9823082f3f9d29681e0586e4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30d13aec77f1e4e2ce93b3f5f434987b39ee3b823db3badf23ff932d87d76f82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__302555f5d94b41d595cf80efd7f7dfec960bf5effd1e4b22eb9bb0cb4c1167ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3c19995c48b7fba58cf03f3b7c9c8428fa695eef5808dd9e3abb1c568b08dae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibility", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentDeployment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentDeployment]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentDeployment]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6638ae5b766ff7ab0ef80c40cc2d5923c7c50428b513690083fe28c9d697c2a0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentFunctions",
    jsii_struct_bases=[],
    name_mapping={
        "api_key": "apiKey",
        "description": "description",
        "faasname": "faasname",
        "faasnamespace": "faasnamespace",
        "guardrail_uuid": "guardrailUuid",
        "name": "name",
        "url": "url",
        "uuid": "uuid",
    },
)
class GenaiAgentFunctions:
    def __init__(
        self,
        *,
        api_key: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        faasname: typing.Optional[builtins.str] = None,
        faasnamespace: typing.Optional[builtins.str] = None,
        guardrail_uuid: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param api_key: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        :param description: Description of the Function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param faasname: Name of function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#faasname GenaiAgent#faasname}
        :param faasnamespace: Namespace of function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#faasnamespace GenaiAgent#faasnamespace}
        :param guardrail_uuid: Guardrail UUID for the Function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#guardrail_uuid GenaiAgent#guardrail_uuid}
        :param name: Name of function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param url: Url of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dbfcfd2a2996c9eada4a7d788821cb591d1786e672de2b6a440cefbeb2d3ce3e)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument faasname", value=faasname, expected_type=type_hints["faasname"])
            check_type(argname="argument faasnamespace", value=faasnamespace, expected_type=type_hints["faasnamespace"])
            check_type(argname="argument guardrail_uuid", value=guardrail_uuid, expected_type=type_hints["guardrail_uuid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key
        if description is not None:
            self._values["description"] = description
        if faasname is not None:
            self._values["faasname"] = faasname
        if faasnamespace is not None:
            self._values["faasnamespace"] = faasnamespace
        if guardrail_uuid is not None:
            self._values["guardrail_uuid"] = guardrail_uuid
        if name is not None:
            self._values["name"] = name
        if url is not None:
            self._values["url"] = url
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the Function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def faasname(self) -> typing.Optional[builtins.str]:
        '''Name of function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#faasname GenaiAgent#faasname}
        '''
        result = self._values.get("faasname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def faasnamespace(self) -> typing.Optional[builtins.str]:
        '''Namespace of function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#faasnamespace GenaiAgent#faasnamespace}
        '''
        result = self._values.get("faasnamespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guardrail_uuid(self) -> typing.Optional[builtins.str]:
        '''Guardrail UUID for the Function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#guardrail_uuid GenaiAgent#guardrail_uuid}
        '''
        result = self._values.get("guardrail_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Url of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentFunctions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentFunctionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentFunctionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fd0818d57073a88788115c8781e5151507a0775f84855b8ebf75e863c07e04c2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentFunctionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b3d24a461e32235fc804885051a76dd47b217239c7955e403e8988600f017ace)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentFunctionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9f79cd1ad43bb7c88276258cfdc07760ea5bb6ae5c4398880edfc78cf6a44292)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1563663579c3f929a18d3a9ca945169b1c67aa58bc66454cc6bf00c07f27ecea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__18f77ad921b45c43606e2392a1d83f58c0d3a67fb6d8e97ee7a09449af844d2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentFunctions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentFunctions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentFunctions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__524a02b78aed2308c777f5538ca85866820a7cf8fc18e5e77d125014f2f0e34c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentFunctionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentFunctionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ea2bbf35f2a2b22e6d091692999b7a93aea57ed6aa3492a51f05e981ba2c813d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetFaasname")
    def reset_faasname(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaasname", []))

    @jsii.member(jsii_name="resetFaasnamespace")
    def reset_faasnamespace(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetFaasnamespace", []))

    @jsii.member(jsii_name="resetGuardrailUuid")
    def reset_guardrail_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGuardrailUuid", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="faasnameInput")
    def faasname_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "faasnameInput"))

    @builtins.property
    @jsii.member(jsii_name="faasnamespaceInput")
    def faasnamespace_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "faasnamespaceInput"))

    @builtins.property
    @jsii.member(jsii_name="guardrailUuidInput")
    def guardrail_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "guardrailUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7932744349f3e12b2ece04e13115176c6a9d5d4f197f039fde48a3ef5edb302)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1bdba6bb495cae705181e9349cd6aa57d3fae75466c17c976be5461857db6e9e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faasname")
    def faasname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "faasname"))

    @faasname.setter
    def faasname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b25f4392461ace2a2a8a81ff3bbe8d327aee212c1040836014157cf87b984bae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faasname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faasnamespace")
    def faasnamespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "faasnamespace"))

    @faasnamespace.setter
    def faasnamespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7ce2a957d8dc69ca9169131050edad4ef2d8092b1047a79f33fcf3aac5af357)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faasnamespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="guardrailUuid")
    def guardrail_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guardrailUuid"))

    @guardrail_uuid.setter
    def guardrail_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__367f132e9d97a6dcb1164f750d4b993f0d11d6a7ab8e56a7caa2f0fffb780551)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "guardrailUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee9e5fb6d77a0b62c672db1efd9c33b1220ecc257f7c85c6bc8b1c6056d10742)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c334b9379436094648935e3b58af73d7ca7630abb5fc16f861ce7da18f65c2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1b53ed50b5745ee09feb370b261ee8318e7ae9f4c6a9d313e7b22ed0a8473e43)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentFunctions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentFunctions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentFunctions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ec933f92dd2310b007039aef534911a870e5751bee779d7a124afb93c259b1d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentKnowledgeBases",
    jsii_struct_bases=[],
    name_mapping={
        "database_id": "databaseId",
        "embedding_model_uuid": "embeddingModelUuid",
        "is_public": "isPublic",
        "last_indexing_job": "lastIndexingJob",
        "name": "name",
        "project_id": "projectId",
        "region": "region",
        "tags": "tags",
        "user_id": "userId",
    },
)
class GenaiAgentKnowledgeBases:
    def __init__(
        self,
        *,
        database_id: typing.Optional[builtins.str] = None,
        embedding_model_uuid: typing.Optional[builtins.str] = None,
        is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_indexing_job: typing.Optional[typing.Union["GenaiAgentKnowledgeBasesLastIndexingJob", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database_id: Database ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#database_id GenaiAgent#database_id}
        :param embedding_model_uuid: Embedding model UUID for the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#embedding_model_uuid GenaiAgent#embedding_model_uuid}
        :param is_public: Indicates if the Knowledge Base is public. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_public GenaiAgent#is_public}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#last_indexing_job GenaiAgent#last_indexing_job}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param project_id: Project ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        :param region: Region of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        :param tags: List of tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        :param user_id: User ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        '''
        if isinstance(last_indexing_job, dict):
            last_indexing_job = GenaiAgentKnowledgeBasesLastIndexingJob(**last_indexing_job)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f104ea7dd1a4b9da28ee10fcf1b2a070c12dc5eca3f061e993e39544ebc0542)
            check_type(argname="argument database_id", value=database_id, expected_type=type_hints["database_id"])
            check_type(argname="argument embedding_model_uuid", value=embedding_model_uuid, expected_type=type_hints["embedding_model_uuid"])
            check_type(argname="argument is_public", value=is_public, expected_type=type_hints["is_public"])
            check_type(argname="argument last_indexing_job", value=last_indexing_job, expected_type=type_hints["last_indexing_job"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if database_id is not None:
            self._values["database_id"] = database_id
        if embedding_model_uuid is not None:
            self._values["embedding_model_uuid"] = embedding_model_uuid
        if is_public is not None:
            self._values["is_public"] = is_public
        if last_indexing_job is not None:
            self._values["last_indexing_job"] = last_indexing_job
        if name is not None:
            self._values["name"] = name
        if project_id is not None:
            self._values["project_id"] = project_id
        if region is not None:
            self._values["region"] = region
        if tags is not None:
            self._values["tags"] = tags
        if user_id is not None:
            self._values["user_id"] = user_id

    @builtins.property
    def database_id(self) -> typing.Optional[builtins.str]:
        '''Database ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#database_id GenaiAgent#database_id}
        '''
        result = self._values.get("database_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embedding_model_uuid(self) -> typing.Optional[builtins.str]:
        '''Embedding model UUID for the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#embedding_model_uuid GenaiAgent#embedding_model_uuid}
        '''
        result = self._values.get("embedding_model_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Knowledge Base is public.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_public GenaiAgent#is_public}
        '''
        result = self._values.get("is_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def last_indexing_job(
        self,
    ) -> typing.Optional["GenaiAgentKnowledgeBasesLastIndexingJob"]:
        '''last_indexing_job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#last_indexing_job GenaiAgent#last_indexing_job}
        '''
        result = self._values.get("last_indexing_job")
        return typing.cast(typing.Optional["GenaiAgentKnowledgeBasesLastIndexingJob"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Project ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''User ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentKnowledgeBases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentKnowledgeBasesLastIndexingJob",
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
class GenaiAgentKnowledgeBasesLastIndexingJob:
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#completed_datasources GenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#data_source_uuids GenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#phase GenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tokens GenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#total_datasources GenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20ea345c0209a78b82908ab2704935c9b1a71b1dacee2d6c6acc8bb5b2b2fb88)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#completed_datasources GenaiAgent#completed_datasources}
        '''
        result = self._values.get("completed_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_source_uuids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Datasource UUIDs for the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#data_source_uuids GenaiAgent#data_source_uuids}
        '''
        result = self._values.get("data_source_uuids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase(self) -> typing.Optional[builtins.str]:
        '''Phase of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#phase GenaiAgent#phase}
        '''
        result = self._values.get("phase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Number of tokens processed in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tokens GenaiAgent#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_datasources(self) -> typing.Optional[jsii.Number]:
        '''Total number of datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#total_datasources GenaiAgent#total_datasources}
        '''
        result = self._values.get("total_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID  of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentKnowledgeBasesLastIndexingJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentKnowledgeBasesLastIndexingJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentKnowledgeBasesLastIndexingJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__15870b7353242831376610056d9da8be394ac0606d2dbdcbd8387b3b7493dfdf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__5d0c705433b2a1cf3f15ab8fdc25ba08ce1c72e5ad41756e328d27bc4d51ee3d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuids")
    def data_source_uuids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataSourceUuids"))

    @data_source_uuids.setter
    def data_source_uuids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eefc82971f06bc5c8072a911be81d8da4ce45d398163171614f0790924177beb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceUuids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase")
    def phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phase"))

    @phase.setter
    def phase(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53da46ae24f659e9b7334e6017fe5afaae8f44864d31bf28bf3d58b49c7cce8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f487ab31de406121d7517b0e655db6b4e8d5bc6ee4d49534fb496ac1665ce2f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDatasources")
    def total_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalDatasources"))

    @total_datasources.setter
    def total_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c10b42d5af39f46586ce30f0ae68e5825a0b99c339cb848f90e38c58c2a89748)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26117a7044da85243efd3340190d8e0e0713006ae835857ac03c8947537fbcf6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GenaiAgentKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[GenaiAgentKnowledgeBasesLastIndexingJob], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GenaiAgentKnowledgeBasesLastIndexingJob],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01bf184937a40e1e071c8601e7175b438671d340c41355653e10f73784b95f75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentKnowledgeBasesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentKnowledgeBasesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7e4b07e893eebe8cca5125ce6c02f6db965b201fb21b3d749006669c601b1632)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentKnowledgeBasesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__49612fb261f22d8469ae826365c67c73edf35c97953dc5dfbb2d2e97778105cf)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentKnowledgeBasesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca7a3a04c25d35c76cf181fbdb2544277d403d69fbbbf9ac8a718ad3f66c45ef)
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
            type_hints = typing.get_type_hints(_typecheckingstub__efdd847f5d9beadd48e2140f592f678f37b488ebf48c6dcb3cfa9c8e7564c3de)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e2abc005a381e21bf92e93e6af344684ba65b4992a4b34348a1513655deadf0b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentKnowledgeBases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentKnowledgeBases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentKnowledgeBases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__100d625fca3ee25a446ad2843b2fbd4f2d400c3c48f01448781f4a2fdb79d72a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentKnowledgeBasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentKnowledgeBasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4bed10bf3e42715e094e6d9c7b89608d575eec41bbe58ffbec141b9b52d3c469)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putLastIndexingJob")
    def put_last_indexing_job(
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#completed_datasources GenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#data_source_uuids GenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#phase GenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tokens GenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#total_datasources GenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        value = GenaiAgentKnowledgeBasesLastIndexingJob(
            completed_datasources=completed_datasources,
            data_source_uuids=data_source_uuids,
            phase=phase,
            tokens=tokens,
            total_datasources=total_datasources,
            uuid=uuid,
        )

        return typing.cast(None, jsii.invoke(self, "putLastIndexingJob", [value]))

    @jsii.member(jsii_name="resetDatabaseId")
    def reset_database_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseId", []))

    @jsii.member(jsii_name="resetEmbeddingModelUuid")
    def reset_embedding_model_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingModelUuid", []))

    @jsii.member(jsii_name="resetIsPublic")
    def reset_is_public(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsPublic", []))

    @jsii.member(jsii_name="resetLastIndexingJob")
    def reset_last_indexing_job(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastIndexingJob", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

    @builtins.property
    @jsii.member(jsii_name="addedToAgentAt")
    def added_to_agent_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addedToAgentAt"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastIndexingJob")
    def last_indexing_job(
        self,
    ) -> GenaiAgentKnowledgeBasesLastIndexingJobOutputReference:
        return typing.cast(GenaiAgentKnowledgeBasesLastIndexingJobOutputReference, jsii.get(self, "lastIndexingJob"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="databaseIdInput")
    def database_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuidInput")
    def embedding_model_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "embeddingModelUuidInput"))

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
    ) -> typing.Optional[GenaiAgentKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[GenaiAgentKnowledgeBasesLastIndexingJob], jsii.get(self, "lastIndexingJobInput"))

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
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseId")
    def database_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseId"))

    @database_id.setter
    def database_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__763828d3e9be167181c171fea63ba8fb6d51fa91b188fa4d20fe232945ffd24c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuid")
    def embedding_model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelUuid"))

    @embedding_model_uuid.setter
    def embedding_model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae8c1e36997011a31b88f51d6883001890f2d12acc5cae1c17b44e715edcbe6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingModelUuid", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__3f56266b576489e8d3d6e7ecb644b5a242a8faf1e646e09901c4e0dfbb7163b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPublic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__352a806a15b205a0f45e54b252ce26064529652be0285e8305c2321871c80c71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2c26eaf0270aea3a9b14f1fed92fa614c9de8c18b5269cdcb6209df4b9e7c40e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fcdc929c0998a21b62323487f6fadd44d573c520c17d9a56f967ea8919e99671)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1064f0dd01f8524a86d9de13ead77260995d21bb0a66ea3add54e0c52fe6ae1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e07eedf07e0d7d55e9f71210dfefe8e21c69551812b4eca9b03fbb882e809f22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentKnowledgeBases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentKnowledgeBases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentKnowledgeBases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ba868de226c4bb677b96089eae3f515fba8a81cc7aa909235707d43d19b79ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModel",
    jsii_struct_bases=[],
    name_mapping={
        "agreement": "agreement",
        "inference_name": "inferenceName",
        "inference_version": "inferenceVersion",
        "is_foundational": "isFoundational",
        "name": "name",
        "parent_uuid": "parentUuid",
        "provider": "provider",
        "upload_complete": "uploadComplete",
        "url": "url",
        "usecases": "usecases",
        "versions": "versions",
    },
)
class GenaiAgentModel:
    def __init__(
        self,
        *,
        agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentModelAgreement", typing.Dict[builtins.str, typing.Any]]]]] = None,
        inference_name: typing.Optional[builtins.str] = None,
        inference_version: typing.Optional[builtins.str] = None,
        is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        parent_uuid: typing.Optional[builtins.str] = None,
        provider: typing.Optional[builtins.str] = None,
        upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
        versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentModelVersions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param agreement: agreement block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agreement GenaiAgent#agreement}
        :param inference_name: Inference name of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_name GenaiAgent#inference_name}
        :param inference_version: Infernce version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_version GenaiAgent#inference_version}
        :param is_foundational: Indicates if the Model Base is foundational. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_foundational GenaiAgent#is_foundational}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param parent_uuid: Parent UUID of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_uuid GenaiAgent#parent_uuid}
        :param provider: Provider of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provider GenaiAgent#provider}
        :param upload_complete: Indicates if the Model upload is complete. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#upload_complete GenaiAgent#upload_complete}
        :param url: URL of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param usecases: List of Usecases for the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#usecases GenaiAgent#usecases}
        :param versions: versions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#versions GenaiAgent#versions}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6e47edd42853d4de182a42fb135765f8bb629a176512349488e9e158369a5af)
            check_type(argname="argument agreement", value=agreement, expected_type=type_hints["agreement"])
            check_type(argname="argument inference_name", value=inference_name, expected_type=type_hints["inference_name"])
            check_type(argname="argument inference_version", value=inference_version, expected_type=type_hints["inference_version"])
            check_type(argname="argument is_foundational", value=is_foundational, expected_type=type_hints["is_foundational"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parent_uuid", value=parent_uuid, expected_type=type_hints["parent_uuid"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument upload_complete", value=upload_complete, expected_type=type_hints["upload_complete"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument usecases", value=usecases, expected_type=type_hints["usecases"])
            check_type(argname="argument versions", value=versions, expected_type=type_hints["versions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if agreement is not None:
            self._values["agreement"] = agreement
        if inference_name is not None:
            self._values["inference_name"] = inference_name
        if inference_version is not None:
            self._values["inference_version"] = inference_version
        if is_foundational is not None:
            self._values["is_foundational"] = is_foundational
        if name is not None:
            self._values["name"] = name
        if parent_uuid is not None:
            self._values["parent_uuid"] = parent_uuid
        if provider is not None:
            self._values["provider"] = provider
        if upload_complete is not None:
            self._values["upload_complete"] = upload_complete
        if url is not None:
            self._values["url"] = url
        if usecases is not None:
            self._values["usecases"] = usecases
        if versions is not None:
            self._values["versions"] = versions

    @builtins.property
    def agreement(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModelAgreement"]]]:
        '''agreement block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agreement GenaiAgent#agreement}
        '''
        result = self._values.get("agreement")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModelAgreement"]]], result)

    @builtins.property
    def inference_name(self) -> typing.Optional[builtins.str]:
        '''Inference name of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_name GenaiAgent#inference_name}
        '''
        result = self._values.get("inference_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_version(self) -> typing.Optional[builtins.str]:
        '''Infernce version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_version GenaiAgent#inference_version}
        '''
        result = self._values.get("inference_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_foundational(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model Base is foundational.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_foundational GenaiAgent#is_foundational}
        '''
        result = self._values.get("is_foundational")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_uuid(self) -> typing.Optional[builtins.str]:
        '''Parent UUID of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_uuid GenaiAgent#parent_uuid}
        '''
        result = self._values.get("parent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider(self) -> typing.Optional[builtins.str]:
        '''Provider of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provider GenaiAgent#provider}
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upload_complete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model upload is complete.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#upload_complete GenaiAgent#upload_complete}
        '''
        result = self._values.get("upload_complete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usecases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Usecases for the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#usecases GenaiAgent#usecases}
        '''
        result = self._values.get("usecases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def versions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModelVersions"]]]:
        '''versions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#versions GenaiAgent#versions}
        '''
        result = self._values.get("versions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModelVersions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelAgreement",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "name": "name",
        "url": "url",
        "uuid": "uuid",
    },
)
class GenaiAgentModelAgreement:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Description of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param name: Name of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param url: URL of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param uuid: UUID of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1cc462f05e9b14e2706e2e085ab409aa67899376da6decb2cc946a363800358d)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if url is not None:
            self._values["url"] = url
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentModelAgreement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentModelAgreementList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelAgreementList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7db2478a274205e94bcb28a52822afb0eb6c27f507d1fd4ac1c068b885cc89e3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentModelAgreementOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2f867a94f45a00a8c59222181b17d49c8ab85f4f3bb82ea80ed97352d3796c7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentModelAgreementOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a32f690ab03e8f8033dcfde7f92214e2c26c57e08fccf42091c9684f069aaa8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c5ae04bcb60858976a33632721dc4ef133b2f3f1599916b97975627c9efabcea)
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
            type_hints = typing.get_type_hints(_typecheckingstub__65bef8fac330ef4c5400bd02261a1d1f045ff0edbbc8c3981459f019861bddd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelAgreement]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelAgreement]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__12b517c3d5f01accac95ff5a4b4733b2c1de9c012ff22b4176eb941de2a088d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentModelAgreementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelAgreementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c7cac094c6359347af3dfc765cad6dbfb3d973b8c381d27c4c2635025bd41bed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ab1e9f8a4863062749cabfcdd605aa974e8a3febe2efa0ec97f00b97784ca2e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e9cc67b628e3bfa640fbda456f7f454bfac4f6beb7012e1874cc9834440ae1c0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d89be89f7e6d328675d35ec2e876995e1f904eac69bfa5b510695657c4b3f0b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ea2218ab95df7e5512c9f7663f6e4a4fae50af8416ccfea69316d3664501fc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelAgreement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelAgreement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelAgreement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ef4dacbc004a584194ca14a4b37b466357cc830758a55bb621681a81bfdd769)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentModelList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cce42ac4ee35fe1f59159e4714b81385879a149936f71face5b4a4f6c3580987)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentModelOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d705e1aad0dacb2175f43b2ad65908645368e211053e7624260efceb2327da42)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentModelOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__09131d242c7b59dab22e0ef3dedcb9afb2dea6da9f01d2ac87af5709da6f4cce)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf2616fc2c1a8bcddf0b7aa07c4b670836aa25547898c292feb594acbcc09b1a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1bf65b12942c09cecd4c27d661d1fcdd3f890347e6116ff379f8f7c70d1aa7ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModel]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModel]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__224dc52745e874700e6ce2d1c931c84abdf98f7166c69e11e815c06ba25cad5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8ca2b61d384c5504eba5ff96d09bf069e6fc3fb691376dda92e9b0146bad158b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAgreement")
    def put_agreement(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25ef58bf3d615b50371336ffb971954ee30bd2ebee6eb269d6cbc05de0e59cd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAgreement", [value]))

    @jsii.member(jsii_name="putVersions")
    def put_versions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentModelVersions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e2d6b64722f95f0cebf65434ec7e2debf1c63ba4cf48c5e471cadb8e48d0d97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVersions", [value]))

    @jsii.member(jsii_name="resetAgreement")
    def reset_agreement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgreement", []))

    @jsii.member(jsii_name="resetInferenceName")
    def reset_inference_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInferenceName", []))

    @jsii.member(jsii_name="resetInferenceVersion")
    def reset_inference_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInferenceVersion", []))

    @jsii.member(jsii_name="resetIsFoundational")
    def reset_is_foundational(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsFoundational", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetParentUuid")
    def reset_parent_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentUuid", []))

    @jsii.member(jsii_name="resetProvider")
    def reset_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvider", []))

    @jsii.member(jsii_name="resetUploadComplete")
    def reset_upload_complete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUploadComplete", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUsecases")
    def reset_usecases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsecases", []))

    @jsii.member(jsii_name="resetVersions")
    def reset_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersions", []))

    @builtins.property
    @jsii.member(jsii_name="agreement")
    def agreement(self) -> GenaiAgentModelAgreementList:
        return typing.cast(GenaiAgentModelAgreementList, jsii.get(self, "agreement"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="versions")
    def versions(self) -> "GenaiAgentModelVersionsList":
        return typing.cast("GenaiAgentModelVersionsList", jsii.get(self, "versions"))

    @builtins.property
    @jsii.member(jsii_name="agreementInput")
    def agreement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelAgreement]]], jsii.get(self, "agreementInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceNameInput")
    def inference_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inferenceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceVersionInput")
    def inference_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inferenceVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="isFoundationalInput")
    def is_foundational_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isFoundationalInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parentUuidInput")
    def parent_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="uploadCompleteInput")
    def upload_complete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "uploadCompleteInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="usecasesInput")
    def usecases_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usecasesInput"))

    @builtins.property
    @jsii.member(jsii_name="versionsInput")
    def versions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModelVersions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentModelVersions"]]], jsii.get(self, "versionsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceName")
    def inference_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceName"))

    @inference_name.setter
    def inference_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae8292ed235e59d88fae98cb0fa84aafbe7e64ce67532a51bb3a0d1dc109d5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inferenceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inferenceVersion")
    def inference_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceVersion"))

    @inference_version.setter
    def inference_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e4d7b5f7193a40ca1e574f55f3753b3021b6d50a5c78ff84864b3bffb6317ea8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inferenceVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isFoundational")
    def is_foundational(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isFoundational"))

    @is_foundational.setter
    def is_foundational(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1890a2b29e586c458115c750f4f949e12273165fe0d64b2fb70485b9a86473f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isFoundational", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2d204088719a22ec3c291eb7350f440f8dda1da549d419fcaeef7dc1b602ff6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentUuid")
    def parent_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentUuid"))

    @parent_uuid.setter
    def parent_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3b39ff07d51c04af916eda781c79f409fb6fab2116c2aec7b03a229ecc673db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2f19891a0a800a4cdd69e0f62c45acc9e10965d716a750d11b5edeb46967203)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uploadComplete")
    def upload_complete(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "uploadComplete"))

    @upload_complete.setter
    def upload_complete(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38703376ecdcaf3a328504a6ef360ea796e765f3b32ed2f24b6d9cc0c4d10749)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uploadComplete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6c9016e9949d788b8e235c0ea53f11cf200a7c402a95b8f9d76b395f4f7e155)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usecases")
    def usecases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usecases"))

    @usecases.setter
    def usecases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5dbcfc65584dd3e4ee5c7600deda3ed71b164a1297718e9b8bf673cd03ac1e63)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usecases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModel]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModel]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModel]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__def57ccac82925119db92e4abb0ca319089745494bad4b5523241d840fa0d1da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelVersions",
    jsii_struct_bases=[],
    name_mapping={"major": "major", "minor": "minor", "patch": "patch"},
)
class GenaiAgentModelVersions:
    def __init__(
        self,
        *,
        major: typing.Optional[jsii.Number] = None,
        minor: typing.Optional[jsii.Number] = None,
        patch: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param major: Major version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#major GenaiAgent#major}
        :param minor: Minor version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#minor GenaiAgent#minor}
        :param patch: Patch version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#patch GenaiAgent#patch}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b6abbf842cd0deb97daf8c409e498e7ba0a42826e05c8b58c8c6108483522827)
            check_type(argname="argument major", value=major, expected_type=type_hints["major"])
            check_type(argname="argument minor", value=minor, expected_type=type_hints["minor"])
            check_type(argname="argument patch", value=patch, expected_type=type_hints["patch"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if major is not None:
            self._values["major"] = major
        if minor is not None:
            self._values["minor"] = minor
        if patch is not None:
            self._values["patch"] = patch

    @builtins.property
    def major(self) -> typing.Optional[jsii.Number]:
        '''Major version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#major GenaiAgent#major}
        '''
        result = self._values.get("major")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minor(self) -> typing.Optional[jsii.Number]:
        '''Minor version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#minor GenaiAgent#minor}
        '''
        result = self._values.get("minor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def patch(self) -> typing.Optional[jsii.Number]:
        '''Patch version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#patch GenaiAgent#patch}
        '''
        result = self._values.get("patch")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentModelVersions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentModelVersionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelVersionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__da6bf6b63608dc002e6eda34611592a697bf4c8aae6481edb523cbcd024abaac)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentModelVersionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1eb3b6bfc26bf84eeae8f349843083a9aab64e0d29a587a55b3b7ffa7a401abc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentModelVersionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__beb97504308b89f4001a24472a2c775f897ee2cb2826ddc74d3f4a3d5bc41dd9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e9473fc3dac6fa81bc0fd22a682a966ba3cfbda216e1f8a65ae59740d52ffd3b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3599e4d80de18fca8ff117bca0f7d16a5ebda1e2b424eb3c7bf3e9870488cc92)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelVersions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelVersions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelVersions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfebeba4d8804cb038d3c84478335000176c1f019f943323c8b2aa8b0e832ba4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentModelVersionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentModelVersionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6c2a7b8e420c0de20dd20dabec7e9978899a6f4493307f3b0ad68f22b9370c6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMajor")
    def reset_major(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMajor", []))

    @jsii.member(jsii_name="resetMinor")
    def reset_minor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinor", []))

    @jsii.member(jsii_name="resetPatch")
    def reset_patch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPatch", []))

    @builtins.property
    @jsii.member(jsii_name="majorInput")
    def major_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "majorInput"))

    @builtins.property
    @jsii.member(jsii_name="minorInput")
    def minor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minorInput"))

    @builtins.property
    @jsii.member(jsii_name="patchInput")
    def patch_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "patchInput"))

    @builtins.property
    @jsii.member(jsii_name="major")
    def major(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "major"))

    @major.setter
    def major(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56c82ff64e22b3828cd1c3f6c0dc84c4c7beadf32db04b4b303f337183cac290)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "major", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minor")
    def minor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minor"))

    @minor.setter
    def minor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__192c71c15e7ffffb8ed131666841ecd2e3963a11d638a57d38f92e4c38280c2f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="patch")
    def patch(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "patch"))

    @patch.setter
    def patch(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b2b797191372e70a61370682da0a466cc70120ff3bcff1558fb1e26726a745e8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "patch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelVersions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelVersions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelVersions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d60fdf0f8637d66d76ba30d0a496332561cb29ec03fd9c9599d5514600315bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentOpenAiApiKey",
    jsii_struct_bases=[],
    name_mapping={"created_by": "createdBy", "name": "name", "uuid": "uuid"},
)
class GenaiAgentOpenAiApiKey:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b17037d79416a5bb12451e8d0daa5369731dafa244d5d6cc34601ddb802503)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentOpenAiApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentOpenAiApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentOpenAiApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__beb8816a3fb792b2505959ed1b77c99fafbd1e6d1c93c42c8acbc97db6c954b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentOpenAiApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2be3c704fd2ff495777f77942724f8db372aa33672370c98af9c7ccee67086d5)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentOpenAiApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d12e6d56bbfa288399bab3b12482f71d21f44eb39cd6532528f8741b12de0806)
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
            type_hints = typing.get_type_hints(_typecheckingstub__16bb0fc3804f347ad75f62ed5cc2b351ccea1bebead99a94a85a15f8e447b2bc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__638d1f61e26a8b199abd090796707e797b1e8bdb86ac7cbc663b02cc20362172)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentOpenAiApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentOpenAiApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentOpenAiApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__993d212c156cf5c432cd8c77583556c89c1850c52368cffbd8b6e8357a245e22)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentOpenAiApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentOpenAiApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d371df9bfb43840cc762d1c8681ace6a7b0074b3bbf077dc911ef2e8cd5ce8ab)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__666bb1198b0ca0353fa822dd006a2f390b526dc067e1bfa423328b47f27d15cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a65050229e763f80d1a73d991bf97740f9229ff9f89b14bd45014705b240bff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96d85b65729b176b92f990a7f6b9a06564f743999aec3ad337818f373ec11a75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentOpenAiApiKey]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentOpenAiApiKey]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentOpenAiApiKey]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af4538463b204357667f0d7ced9a9f994f0f524a2de2865dfc9d2900cadfa3f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgents",
    jsii_struct_bases=[],
    name_mapping={
        "instruction": "instruction",
        "model_uuid": "modelUuid",
        "name": "name",
        "project_id": "projectId",
        "region": "region",
        "anthropic_api_key": "anthropicApiKey",
        "api_key_infos": "apiKeyInfos",
        "api_keys": "apiKeys",
        "chatbot": "chatbot",
        "chatbot_identifiers": "chatbotIdentifiers",
        "deployment": "deployment",
        "description": "description",
    },
)
class GenaiAgentParentAgents:
    def __init__(
        self,
        *,
        instruction: builtins.str,
        model_uuid: builtins.str,
        name: builtins.str,
        project_id: builtins.str,
        region: builtins.str,
        anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgentsAnthropicApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgentsApiKeyInfos", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgentsApiKeys", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgentsChatbot", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgentsChatbotIdentifiers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentParentAgentsDeployment", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param instruction: Instruction for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        :param model_uuid: Model UUID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        :param name: Name of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param project_id: Project ID of the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        :param region: Region where the Agent is deployed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        :param anthropic_api_key: anthropic_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        :param api_key_infos: api_key_infos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        :param api_keys: api_keys block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        :param chatbot: chatbot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        :param chatbot_identifiers: chatbot_identifiers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        :param description: Description for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a4cb1bb1df81627670e832d776aa3cac71c5ce21903508bb02cbd2e735f4e7a)
            check_type(argname="argument instruction", value=instruction, expected_type=type_hints["instruction"])
            check_type(argname="argument model_uuid", value=model_uuid, expected_type=type_hints["model_uuid"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
            check_type(argname="argument api_key_infos", value=api_key_infos, expected_type=type_hints["api_key_infos"])
            check_type(argname="argument api_keys", value=api_keys, expected_type=type_hints["api_keys"])
            check_type(argname="argument chatbot", value=chatbot, expected_type=type_hints["chatbot"])
            check_type(argname="argument chatbot_identifiers", value=chatbot_identifiers, expected_type=type_hints["chatbot_identifiers"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
        self._values: typing.Dict[builtins.str, typing.Any] = {
            "instruction": instruction,
            "model_uuid": model_uuid,
            "name": name,
            "project_id": project_id,
            "region": region,
        }
        if anthropic_api_key is not None:
            self._values["anthropic_api_key"] = anthropic_api_key
        if api_key_infos is not None:
            self._values["api_key_infos"] = api_key_infos
        if api_keys is not None:
            self._values["api_keys"] = api_keys
        if chatbot is not None:
            self._values["chatbot"] = chatbot
        if chatbot_identifiers is not None:
            self._values["chatbot_identifiers"] = chatbot_identifiers
        if deployment is not None:
            self._values["deployment"] = deployment
        if description is not None:
            self._values["description"] = description

    @builtins.property
    def instruction(self) -> builtins.str:
        '''Instruction for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        '''
        result = self._values.get("instruction")
        assert result is not None, "Required property 'instruction' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def model_uuid(self) -> builtins.str:
        '''Model UUID of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model_uuid GenaiAgent#model_uuid}
        '''
        result = self._values.get("model_uuid")
        assert result is not None, "Required property 'model_uuid' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def name(self) -> builtins.str:
        '''Name of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def project_id(self) -> builtins.str:
        '''Project ID of the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        assert result is not None, "Required property 'project_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def region(self) -> builtins.str:
        '''Region where the Agent is deployed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        '''
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def anthropic_api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsAnthropicApiKey"]]]:
        '''anthropic_api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#anthropic_api_key GenaiAgent#anthropic_api_key}
        '''
        result = self._values.get("anthropic_api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsAnthropicApiKey"]]], result)

    @builtins.property
    def api_key_infos(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsApiKeyInfos"]]]:
        '''api_key_infos block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key_infos GenaiAgent#api_key_infos}
        '''
        result = self._values.get("api_key_infos")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsApiKeyInfos"]]], result)

    @builtins.property
    def api_keys(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsApiKeys"]]]:
        '''api_keys block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_keys GenaiAgent#api_keys}
        '''
        result = self._values.get("api_keys")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsApiKeys"]]], result)

    @builtins.property
    def chatbot(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsChatbot"]]]:
        '''chatbot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot GenaiAgent#chatbot}
        '''
        result = self._values.get("chatbot")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsChatbot"]]], result)

    @builtins.property
    def chatbot_identifiers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsChatbotIdentifiers"]]]:
        '''chatbot_identifiers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#chatbot_identifiers GenaiAgent#chatbot_identifiers}
        '''
        result = self._values.get("chatbot_identifiers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsChatbotIdentifiers"]]], result)

    @builtins.property
    def deployment(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsDeployment"]]]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#deployment GenaiAgent#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentParentAgentsDeployment"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsAnthropicApiKey",
    jsii_struct_bases=[],
    name_mapping={"created_by": "createdBy", "name": "name", "uuid": "uuid"},
)
class GenaiAgentParentAgentsAnthropicApiKey:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__da7d206c4078d1f816e0926929a709cc630cf005382db8035768be451646d0bf)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgentsAnthropicApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentParentAgentsAnthropicApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsAnthropicApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c32aecec02e468c468eca75ff644ce4197208e2bdccd1be7db1fc828f8a6ede0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentParentAgentsAnthropicApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e795046eae5510a7c4751aa0f16c25df4d5e063c9cff40dcc1c45062efef844)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsAnthropicApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf7717c97bb9ad1ca50d92d3f55d2f7dc50a73f1997dafdfd6e80681426efa48)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6cd54103770f77d95b049fed7a497fce1072c4702901c7cf6f49b7bf85342fb0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__102565eecf84e6717db89af1ccbde6a3f7d631e84af71ac0a2fca9dd99fe09c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsAnthropicApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsAnthropicApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsAnthropicApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2a726d14060f596c925b749cc73de5642ba0d62c10e8c8697f934a8696dc3b8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsAnthropicApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsAnthropicApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__706e9bddbf60625e72b4934fe5710522605820fc4cf4f74d9dd558e35c39376d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__228b3b2c8d8b69c0a886c89f6137e2d97d36829c6ffa9f8c6a82d9334f82ee3f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e0bdc8795cd08d1016ad6aa36881834713b323be60774cf7e7bf6e59505e7d2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__deebcd8afad83101e977f53a31fb3eea0196ef6742c4db1826b240c18a753600)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsAnthropicApiKey]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsAnthropicApiKey]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsAnthropicApiKey]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96f863017740847c5b8343cbe315a4b8efebba642f6f8b49147088caf0843d1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsApiKeyInfos",
    jsii_struct_bases=[],
    name_mapping={
        "created_by": "createdBy",
        "name": "name",
        "secret_key": "secretKey",
        "uuid": "uuid",
    },
)
class GenaiAgentParentAgentsApiKeyInfos:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        secret_key: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param secret_key: Updated At timestamp for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secret_key GenaiAgent#secret_key}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0228f52b306b2c621461b92c945283400ca3946be1609441a3bc304e391bcdb2)
            check_type(argname="argument created_by", value=created_by, expected_type=type_hints["created_by"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument secret_key", value=secret_key, expected_type=type_hints["secret_key"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if created_by is not None:
            self._values["created_by"] = created_by
        if name is not None:
            self._values["name"] = name
        if secret_key is not None:
            self._values["secret_key"] = secret_key
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def created_by(self) -> typing.Optional[builtins.str]:
        '''Created By user ID for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#created_by GenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        '''Updated At timestamp for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secret_key GenaiAgent#secret_key}
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgentsApiKeyInfos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentParentAgentsApiKeyInfosList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsApiKeyInfosList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__873592535e27cad3217c05eab1c60832f08daf83906290ac18b7695a67703687)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentParentAgentsApiKeyInfosOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fee7aa422a87f135a76a686487340cf026ab245b4993546041088d736363a212)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsApiKeyInfosOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10d69457aa98d69d02a9804dfdc421ad788d5a69d0811b5360d7593ef3751b5f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__38e4f6e07d40aea3e93abf3ab9d039e9a031c83fd5e68b3c31eb9c24b42cf5c9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f557d3bf0833884fb23df262797341828d682a04b5288fd4149d165f38af0b23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeyInfos]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeyInfos]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeyInfos]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__46e1f282cbedd43f4c142ebd7e94d329f4ab7fdb6f53a3b0209b5b77e3e2e4c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsApiKeyInfosOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsApiKeyInfosOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__91bc3bcc624da29dc2d9870c324880c7ab944ebd1684ddac57296f1f0e50e272)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetCreatedBy")
    def reset_created_by(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCreatedBy", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetSecretKey")
    def reset_secret_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecretKey", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="createdByInput")
    def created_by_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "createdByInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="secretKeyInput")
    def secret_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secretKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @created_by.setter
    def created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__daf45a8eae7c4fe8ae53ea465f505fe148efce11e20e84ef7ebb97ccc89aadef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4378718d00942459f0846dfaf4debe66cb18841ee2bbfbd4df64bc6644ede15)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca733ea68d5026470b923db3b1d8295aa64427ad34bc7e5af85c84d06acd9d6e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fea499ee56b89bf3594cb44e7c3f3798763459f8198eb95035b8592888be77df)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeyInfos]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeyInfos]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeyInfos]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__499bc238ca8f68b31ee54176f005309527f29c98b230ccc08c89e7fcee407cdc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsApiKeys",
    jsii_struct_bases=[],
    name_mapping={"api_key": "apiKey"},
)
class GenaiAgentParentAgentsApiKeys:
    def __init__(self, *, api_key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param api_key: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__96d2c0852b7657ef162ce41817485ce8a7c2aa71d975d4addeb1ebf3f07c3006)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#api_key GenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgentsApiKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentParentAgentsApiKeysList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsApiKeysList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__96e434aedb0a8826dccbc212c5427b3e3bb27bef902459d51976143fe23003b5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentParentAgentsApiKeysOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6240ee923a5b6e572ba141fc20b3910d647da6487533d76a6e945f3b9f8568f6)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsApiKeysOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38affec753090f5a6cf9e8226357d4a67e902c655d4a2166a09cfc8467dc271d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5cc6c13484e26c19454905d05681e8db6fe3e2d66355429c547495a120e68e07)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb55489121fc23cd4777751bf4ceb102e3029d7ab6a3a6ca2c4b34ecc1323b17)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeys]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeys]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeys]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bb08b26b0543248837421d64639dd73c9a16fa8c012db417df1c77ba03847b54)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsApiKeysOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsApiKeysOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a1f91eed9cb616394545b40a911ee9266c0a50848bfc2c46a01504b3e005805f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetApiKey")
    def reset_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKey", []))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInput")
    def api_key_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "apiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @api_key.setter
    def api_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d7b3f8ec68a13e88764c081d58510417ebafa2bd9eafbdc2f1f9197448c53acd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeys]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeys]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeys]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af375e62476ef531baf469c953d29ac5a74c03776a5d65e14b430f1b92804516)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsChatbot",
    jsii_struct_bases=[],
    name_mapping={
        "button_background_color": "buttonBackgroundColor",
        "logo": "logo",
        "name": "name",
        "primary_color": "primaryColor",
        "secondary_color": "secondaryColor",
        "starting_message": "startingMessage",
    },
)
class GenaiAgentParentAgentsChatbot:
    def __init__(
        self,
        *,
        button_background_color: typing.Optional[builtins.str] = None,
        logo: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        primary_color: typing.Optional[builtins.str] = None,
        secondary_color: typing.Optional[builtins.str] = None,
        starting_message: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param button_background_color: Background color for the chatbot button. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#button_background_color GenaiAgent#button_background_color}
        :param logo: Logo for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#logo GenaiAgent#logo}
        :param name: Name of the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param primary_color: Primary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#primary_color GenaiAgent#primary_color}
        :param secondary_color: Secondary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secondary_color GenaiAgent#secondary_color}
        :param starting_message: Starting message for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#starting_message GenaiAgent#starting_message}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7505e05497ba47c2f29c82e6beb3de9af7bf6cd184e5af42201bf50ff2a00b03)
            check_type(argname="argument button_background_color", value=button_background_color, expected_type=type_hints["button_background_color"])
            check_type(argname="argument logo", value=logo, expected_type=type_hints["logo"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument primary_color", value=primary_color, expected_type=type_hints["primary_color"])
            check_type(argname="argument secondary_color", value=secondary_color, expected_type=type_hints["secondary_color"])
            check_type(argname="argument starting_message", value=starting_message, expected_type=type_hints["starting_message"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if button_background_color is not None:
            self._values["button_background_color"] = button_background_color
        if logo is not None:
            self._values["logo"] = logo
        if name is not None:
            self._values["name"] = name
        if primary_color is not None:
            self._values["primary_color"] = primary_color
        if secondary_color is not None:
            self._values["secondary_color"] = secondary_color
        if starting_message is not None:
            self._values["starting_message"] = starting_message

    @builtins.property
    def button_background_color(self) -> typing.Optional[builtins.str]:
        '''Background color for the chatbot button.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#button_background_color GenaiAgent#button_background_color}
        '''
        result = self._values.get("button_background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logo(self) -> typing.Optional[builtins.str]:
        '''Logo for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#logo GenaiAgent#logo}
        '''
        result = self._values.get("logo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def primary_color(self) -> typing.Optional[builtins.str]:
        '''Primary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#primary_color GenaiAgent#primary_color}
        '''
        result = self._values.get("primary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_color(self) -> typing.Optional[builtins.str]:
        '''Secondary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#secondary_color GenaiAgent#secondary_color}
        '''
        result = self._values.get("secondary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def starting_message(self) -> typing.Optional[builtins.str]:
        '''Starting message for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#starting_message GenaiAgent#starting_message}
        '''
        result = self._values.get("starting_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgentsChatbot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsChatbotIdentifiers",
    jsii_struct_bases=[],
    name_mapping={},
)
class GenaiAgentParentAgentsChatbotIdentifiers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgentsChatbotIdentifiers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentParentAgentsChatbotIdentifiersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsChatbotIdentifiersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8ac54d6c08f0c74b705878da023d44da4393465776219785d295cf072176462)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentParentAgentsChatbotIdentifiersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__696e4f3eee9e1c8b90ce1a7b33af3f13c51fd26dff85ec184c40c5ec8fda9890)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsChatbotIdentifiersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0cd93bb6651fc4d77bb0302c4c4f62346c187dda09f44b097a1ea9e4d511d59)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5baad42878aa6b1fed7fdc2742d086515b951150192cfbbbe7fc1e81908ec216)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c74ce4ebe78441cdccc8572ddb0c72b7cf750e2678e66f06f37446d0777788a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbotIdentifiers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbotIdentifiers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbotIdentifiers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e28feabbc22a0e37cc1ec60fd25621877256b5407ecda8e57d358981f50f00a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsChatbotIdentifiersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsChatbotIdentifiersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5eda7db18673405c5c305709a5ca2b819c410b0fd9ded1ff84bc164639c0eddd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="chatbotId")
    def chatbot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "chatbotId"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbotIdentifiers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbotIdentifiers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbotIdentifiers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb1dc072b2bf8eaf7a200ec3f3bb4200f8a68fc1e091e14dc3b0fa2d11143962)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsChatbotList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsChatbotList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__562521664e385ef0a15e7b915cdbeee234da619eef886ecaa7d9e8075c297663)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentParentAgentsChatbotOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17da8a4497f8ef6021cd7766b628b7e538f8df3518e14e63394f2c68339cf70f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsChatbotOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__958c43440c9a35de155816ac64586c1f44114d79dbd0f0b8497821faa338f47a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__5b00c4615cfdc2e3522c1450b32072fa5f21a7a07ff0a0d4042b36a64d26b73d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9d91ef114953b689f624720947a76435e28bcd4caa81edec61f558881342850e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbot]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbot]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbot]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d6699d12f1d5382970e4587c24f738491a97c019dea87cfcaad9231d4b32a10)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsChatbotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsChatbotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e91000e1d0c6e0f43b29e538525ebb0925220d1c534f91749e8cce545210ec78)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetButtonBackgroundColor")
    def reset_button_background_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetButtonBackgroundColor", []))

    @jsii.member(jsii_name="resetLogo")
    def reset_logo(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogo", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetPrimaryColor")
    def reset_primary_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPrimaryColor", []))

    @jsii.member(jsii_name="resetSecondaryColor")
    def reset_secondary_color(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSecondaryColor", []))

    @jsii.member(jsii_name="resetStartingMessage")
    def reset_starting_message(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStartingMessage", []))

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColorInput")
    def button_background_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "buttonBackgroundColorInput"))

    @builtins.property
    @jsii.member(jsii_name="logoInput")
    def logo_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logoInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="primaryColorInput")
    def primary_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "primaryColorInput"))

    @builtins.property
    @jsii.member(jsii_name="secondaryColorInput")
    def secondary_color_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "secondaryColorInput"))

    @builtins.property
    @jsii.member(jsii_name="startingMessageInput")
    def starting_message_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "startingMessageInput"))

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColor")
    def button_background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonBackgroundColor"))

    @button_background_color.setter
    def button_background_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c50c9dc508e183702fc3b7b54236e2b5b320e9064dbe54def4afc40abdfe8b83)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buttonBackgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logo")
    def logo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logo"))

    @logo.setter
    def logo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__714c176383027cd6e555de74712aa57ed7d7494a48cef77e73fbe0da2ea926a5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9bc9754a9c157ff51329ff6cd96c927e5c27c3f92461947858771d3239a09bef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryColor")
    def primary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryColor"))

    @primary_color.setter
    def primary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8166b7958d47fdf3465e054738ae359c29bfd0d31fbbf5635d1d85c4be1e97b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryColor")
    def secondary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryColor"))

    @secondary_color.setter
    def secondary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__edb1a4c858f15b0b865cb06a319bf26562388fc08dd15d9f9ef400c91569948b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startingMessage")
    def starting_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingMessage"))

    @starting_message.setter
    def starting_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0548ed64ebc9fe952877816de2c989eb6f039e3dee885bb1f1eb94f5727abd7c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startingMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbot]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbot]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbot]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5db27f4d954f5827e62f50a34b25820ee20ebdb3cd775dc7ea35340784e53827)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "status": "status",
        "url": "url",
        "uuid": "uuid",
        "visibility": "visibility",
    },
)
class GenaiAgentParentAgentsDeployment:
    def __init__(
        self,
        *,
        name: typing.Optional[builtins.str] = None,
        status: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
        visibility: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param status: Status of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#status GenaiAgent#status}
        :param url: Url of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        :param visibility: Visibility of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#visibility GenaiAgent#visibility}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3377902e32c12490ecfb8f207169caa4b8974fd0b1bb23bf10b33446b4e4f99b)
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument status", value=status, expected_type=type_hints["status"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
            check_type(argname="argument visibility", value=visibility, expected_type=type_hints["visibility"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if name is not None:
            self._values["name"] = name
        if status is not None:
            self._values["status"] = status
        if url is not None:
            self._values["url"] = url
        if uuid is not None:
            self._values["uuid"] = uuid
        if visibility is not None:
            self._values["visibility"] = visibility

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Status of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#status GenaiAgent#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Url of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Visibility of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#visibility GenaiAgent#visibility}
        '''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentParentAgentsDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentParentAgentsDeploymentList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsDeploymentList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1aa3db2750d05d3b1a57dcebf5d78c50176206d9f29ac4b277717f9a9ac1e4a7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentParentAgentsDeploymentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ede2d37927ceffdaffb86c648e41af1e421d5355c9882ade29b8958b96a3bd38)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsDeploymentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a51c740d09dbcff2bc4704ba76b8c2bff0e3be6cf06962940b35ae7897b9c57d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9b1635d7d1c022581b839db4c1890542d22228a76e93cc54a0f1865edb37250)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db2628545d2bf2556e0c65ba7f12465b5b3deb6156a2a6941d117e2f9381d1bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsDeployment]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsDeployment]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsDeployment]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e990f3ed922e15841f2f17dd69e0975a659308dac4cb474cfede304d70eaea23)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7348822a8644e44d1059940704f799c7023df38ee8931cc26631289099ac1c51)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetStatus")
    def reset_status(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetStatus", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @jsii.member(jsii_name="resetVisibility")
    def reset_visibility(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVisibility", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="statusInput")
    def status_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "statusInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="visibilityInput")
    def visibility_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "visibilityInput"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__16a1a0a908b0c69869b578f84d8a3a7a25422fc14a71fcc689eff639f9f2d072)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fae802b88d443efa27ebae1ca20d24f236e40d3208f61160d6ed16260c3ad930)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e49ca5d7c7b100d74565758cacda6eaa387fcb99703813d4191cebc782986094)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e3ca0c3df18764132db3db6366faf91a1cfb2e1f21d4400db26bea6dcc5a895)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__605177106d0f964c4af52bbbf730e34027a8c909d610b01eaf596ea22337a713)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibility", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsDeployment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsDeployment]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsDeployment]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa422f83223a30098da6a85beb3fbaab0c600d8428416ed0ea89f87c46f3816f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__63e30ec309b14ce88a6534fd72889ec13cae0ba4d1acd145e87e099dc62068f9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentParentAgentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ce6bd36d9ff82090b4c7e880ea75e7973e0fe89b6002a128b7849e9ac5c8091)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentParentAgentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bac695629cf420350ea6535a0df41bff7f4de4859130ac98024d161e98d5b7de)
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
            type_hints = typing.get_type_hints(_typecheckingstub__350e16b7d51e91bdadb5f8592e62eb97a1079885c95a100a9041493587743999)
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
            type_hints = typing.get_type_hints(_typecheckingstub__87bfdff6a019d9afd88254a5ef329841e3573e130d1b8ded4c42ce09bb72fc99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgents]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgents]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgents]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b426cd159acab4e9b23f9ac8d3cf8a4e6d355b1c6b0715a8d78505c837517cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentParentAgentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentParentAgentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b35c653b566d8abc86758a9ac02800f87e34ca6d4af10f5ad72001ecc74b1b37)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAnthropicApiKey")
    def put_anthropic_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d28e200a8424688143f528464e7b06f8bcfb1f18219ca981a7db305418978692)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnthropicApiKey", [value]))

    @jsii.member(jsii_name="putApiKeyInfos")
    def put_api_key_infos(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4d38882d287037360f87d4abb6ca4cde7985e86ad601072d53d39cc6fb10659)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeyInfos", [value]))

    @jsii.member(jsii_name="putApiKeys")
    def put_api_keys(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsApiKeys, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6fdcade5d979c3d078fca0bc98985821fe3d018a0f687050e3f8f256d5c26eb7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeys", [value]))

    @jsii.member(jsii_name="putChatbot")
    def put_chatbot(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsChatbot, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2da3b94e570c01194ca4797778e1bef0de2792fb652e36553e09eec94fee62e6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbot", [value]))

    @jsii.member(jsii_name="putChatbotIdentifiers")
    def put_chatbot_identifiers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa667603bf6d9c10c10ee4a17d36ea8c1079f6c028a7346a598a667b7f253ac9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbotIdentifiers", [value]))

    @jsii.member(jsii_name="putDeployment")
    def put_deployment(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsDeployment, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9960210e0162cdb95d7d65cdabfc8eb103f0bdc20aadb84f09ab8deeecdf95d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDeployment", [value]))

    @jsii.member(jsii_name="resetAnthropicApiKey")
    def reset_anthropic_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAnthropicApiKey", []))

    @jsii.member(jsii_name="resetApiKeyInfos")
    def reset_api_key_infos(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeyInfos", []))

    @jsii.member(jsii_name="resetApiKeys")
    def reset_api_keys(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetApiKeys", []))

    @jsii.member(jsii_name="resetChatbot")
    def reset_chatbot(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbot", []))

    @jsii.member(jsii_name="resetChatbotIdentifiers")
    def reset_chatbot_identifiers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbotIdentifiers", []))

    @jsii.member(jsii_name="resetDeployment")
    def reset_deployment(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeployment", []))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @builtins.property
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentId"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(self) -> GenaiAgentParentAgentsAnthropicApiKeyList:
        return typing.cast(GenaiAgentParentAgentsAnthropicApiKeyList, jsii.get(self, "anthropicApiKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfos")
    def api_key_infos(self) -> GenaiAgentParentAgentsApiKeyInfosList:
        return typing.cast(GenaiAgentParentAgentsApiKeyInfosList, jsii.get(self, "apiKeyInfos"))

    @builtins.property
    @jsii.member(jsii_name="apiKeys")
    def api_keys(self) -> GenaiAgentParentAgentsApiKeysList:
        return typing.cast(GenaiAgentParentAgentsApiKeysList, jsii.get(self, "apiKeys"))

    @builtins.property
    @jsii.member(jsii_name="chatbot")
    def chatbot(self) -> GenaiAgentParentAgentsChatbotList:
        return typing.cast(GenaiAgentParentAgentsChatbotList, jsii.get(self, "chatbot"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiers")
    def chatbot_identifiers(self) -> GenaiAgentParentAgentsChatbotIdentifiersList:
        return typing.cast(GenaiAgentParentAgentsChatbotIdentifiersList, jsii.get(self, "chatbotIdentifiers"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> GenaiAgentParentAgentsDeploymentList:
        return typing.cast(GenaiAgentParentAgentsDeploymentList, jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyInput")
    def anthropic_api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsAnthropicApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsAnthropicApiKey]]], jsii.get(self, "anthropicApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfosInput")
    def api_key_infos_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeyInfos]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeyInfos]]], jsii.get(self, "apiKeyInfosInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeysInput")
    def api_keys_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeys]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeys]]], jsii.get(self, "apiKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiersInput")
    def chatbot_identifiers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbotIdentifiers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbotIdentifiers]]], jsii.get(self, "chatbotIdentifiersInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotInput")
    def chatbot_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbot]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbot]]], jsii.get(self, "chatbotInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsDeployment]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsDeployment]]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="instructionInput")
    def instruction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instructionInput"))

    @builtins.property
    @jsii.member(jsii_name="modelUuidInput")
    def model_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "modelUuidInput"))

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
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6220425d0a7787f8f2fd9f44104e1fe4ce76a1a9ba18ccbb14c85276be3adabb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @instruction.setter
    def instruction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__674258837b2e17e079d977d474ac40d039a62644d6817831528d596885702f05)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instruction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="modelUuid")
    def model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelUuid"))

    @model_uuid.setter
    def model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e258dd1c99f75b548d75bda994f40ef520be8400d926aa64b645304216fbf6f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "modelUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b46a392fdeed5d11dd89dd9506c327a380a677da2b7b71eb7e7f8bcf602f72da)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5257bd70bc8e3c6ce7bb23733377b9505df61ef9e922761a994bf73eab3aeb71)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba7ece4e553bf30f71b1ab43a5f3886a1918ec671c2d0fba071b7747ea43708d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgents]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgents]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgents]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4acf480f4f31acecb641b1225593ec7825facc5800894e0838baac8cbdf1f36)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplate",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "instruction": "instruction",
        "k": "k",
        "knowledge_bases": "knowledgeBases",
        "max_tokens": "maxTokens",
        "model": "model",
        "name": "name",
        "temperature": "temperature",
        "top_p": "topP",
        "uuid": "uuid",
    },
)
class GenaiAgentTemplate:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        instruction: typing.Optional[builtins.str] = None,
        k: typing.Optional[jsii.Number] = None,
        knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplateKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_tokens: typing.Optional[jsii.Number] = None,
        model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplateModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        temperature: typing.Optional[jsii.Number] = None,
        top_p: typing.Optional[jsii.Number] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Description of the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param instruction: Instruction for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        :param k: K value for the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#k GenaiAgent#k}
        :param knowledge_bases: knowledge_bases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_bases GenaiAgent#knowledge_bases}
        :param max_tokens: Maximum tokens allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#max_tokens GenaiAgent#max_tokens}
        :param model: model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model GenaiAgent#model}
        :param name: Name of the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param temperature: Agent temperature setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#temperature GenaiAgent#temperature}
        :param top_p: Top P sampling parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#top_p GenaiAgent#top_p}
        :param uuid: uuid of the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e2de23e2c8f609ba50d1502866322493e465551c415788b27bc5a995d3756306)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument instruction", value=instruction, expected_type=type_hints["instruction"])
            check_type(argname="argument k", value=k, expected_type=type_hints["k"])
            check_type(argname="argument knowledge_bases", value=knowledge_bases, expected_type=type_hints["knowledge_bases"])
            check_type(argname="argument max_tokens", value=max_tokens, expected_type=type_hints["max_tokens"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument temperature", value=temperature, expected_type=type_hints["temperature"])
            check_type(argname="argument top_p", value=top_p, expected_type=type_hints["top_p"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if instruction is not None:
            self._values["instruction"] = instruction
        if k is not None:
            self._values["k"] = k
        if knowledge_bases is not None:
            self._values["knowledge_bases"] = knowledge_bases
        if max_tokens is not None:
            self._values["max_tokens"] = max_tokens
        if model is not None:
            self._values["model"] = model
        if name is not None:
            self._values["name"] = name
        if temperature is not None:
            self._values["temperature"] = temperature
        if top_p is not None:
            self._values["top_p"] = top_p
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instruction(self) -> typing.Optional[builtins.str]:
        '''Instruction for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#instruction GenaiAgent#instruction}
        '''
        result = self._values.get("instruction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k(self) -> typing.Optional[jsii.Number]:
        '''K value for the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#k GenaiAgent#k}
        '''
        result = self._values.get("k")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def knowledge_bases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateKnowledgeBases"]]]:
        '''knowledge_bases block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#knowledge_bases GenaiAgent#knowledge_bases}
        '''
        result = self._values.get("knowledge_bases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateKnowledgeBases"]]], result)

    @builtins.property
    def max_tokens(self) -> typing.Optional[jsii.Number]:
        '''Maximum tokens allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#max_tokens GenaiAgent#max_tokens}
        '''
        result = self._values.get("max_tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def model(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModel"]]]:
        '''model block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#model GenaiAgent#model}
        '''
        result = self._values.get("model")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModel"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def temperature(self) -> typing.Optional[jsii.Number]:
        '''Agent temperature setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#temperature GenaiAgent#temperature}
        '''
        result = self._values.get("temperature")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def top_p(self) -> typing.Optional[jsii.Number]:
        '''Top P sampling parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#top_p GenaiAgent#top_p}
        '''
        result = self._values.get("top_p")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''uuid of the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateKnowledgeBases",
    jsii_struct_bases=[],
    name_mapping={
        "database_id": "databaseId",
        "embedding_model_uuid": "embeddingModelUuid",
        "is_public": "isPublic",
        "last_indexing_job": "lastIndexingJob",
        "name": "name",
        "project_id": "projectId",
        "region": "region",
        "tags": "tags",
        "user_id": "userId",
    },
)
class GenaiAgentTemplateKnowledgeBases:
    def __init__(
        self,
        *,
        database_id: typing.Optional[builtins.str] = None,
        embedding_model_uuid: typing.Optional[builtins.str] = None,
        is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_indexing_job: typing.Optional[typing.Union["GenaiAgentTemplateKnowledgeBasesLastIndexingJob", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database_id: Database ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#database_id GenaiAgent#database_id}
        :param embedding_model_uuid: Embedding model UUID for the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#embedding_model_uuid GenaiAgent#embedding_model_uuid}
        :param is_public: Indicates if the Knowledge Base is public. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_public GenaiAgent#is_public}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#last_indexing_job GenaiAgent#last_indexing_job}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param project_id: Project ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        :param region: Region of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        :param tags: List of tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        :param user_id: User ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        '''
        if isinstance(last_indexing_job, dict):
            last_indexing_job = GenaiAgentTemplateKnowledgeBasesLastIndexingJob(**last_indexing_job)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f93999fc9072de6748f56f7419170b7a2fe7e488decef22ac20ab10c45a46d)
            check_type(argname="argument database_id", value=database_id, expected_type=type_hints["database_id"])
            check_type(argname="argument embedding_model_uuid", value=embedding_model_uuid, expected_type=type_hints["embedding_model_uuid"])
            check_type(argname="argument is_public", value=is_public, expected_type=type_hints["is_public"])
            check_type(argname="argument last_indexing_job", value=last_indexing_job, expected_type=type_hints["last_indexing_job"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument project_id", value=project_id, expected_type=type_hints["project_id"])
            check_type(argname="argument region", value=region, expected_type=type_hints["region"])
            check_type(argname="argument tags", value=tags, expected_type=type_hints["tags"])
            check_type(argname="argument user_id", value=user_id, expected_type=type_hints["user_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if database_id is not None:
            self._values["database_id"] = database_id
        if embedding_model_uuid is not None:
            self._values["embedding_model_uuid"] = embedding_model_uuid
        if is_public is not None:
            self._values["is_public"] = is_public
        if last_indexing_job is not None:
            self._values["last_indexing_job"] = last_indexing_job
        if name is not None:
            self._values["name"] = name
        if project_id is not None:
            self._values["project_id"] = project_id
        if region is not None:
            self._values["region"] = region
        if tags is not None:
            self._values["tags"] = tags
        if user_id is not None:
            self._values["user_id"] = user_id

    @builtins.property
    def database_id(self) -> typing.Optional[builtins.str]:
        '''Database ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#database_id GenaiAgent#database_id}
        '''
        result = self._values.get("database_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embedding_model_uuid(self) -> typing.Optional[builtins.str]:
        '''Embedding model UUID for the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#embedding_model_uuid GenaiAgent#embedding_model_uuid}
        '''
        result = self._values.get("embedding_model_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Knowledge Base is public.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_public GenaiAgent#is_public}
        '''
        result = self._values.get("is_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def last_indexing_job(
        self,
    ) -> typing.Optional["GenaiAgentTemplateKnowledgeBasesLastIndexingJob"]:
        '''last_indexing_job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#last_indexing_job GenaiAgent#last_indexing_job}
        '''
        result = self._values.get("last_indexing_job")
        return typing.cast(typing.Optional["GenaiAgentTemplateKnowledgeBasesLastIndexingJob"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Project ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#project_id GenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#region GenaiAgent#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tags GenaiAgent#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''User ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#user_id GenaiAgent#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentTemplateKnowledgeBases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateKnowledgeBasesLastIndexingJob",
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
class GenaiAgentTemplateKnowledgeBasesLastIndexingJob:
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#completed_datasources GenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#data_source_uuids GenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#phase GenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tokens GenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#total_datasources GenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f88c53534c6f5ace235d9da6bbd88f9c27ecf4867181d81ba43e3acf5328a515)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#completed_datasources GenaiAgent#completed_datasources}
        '''
        result = self._values.get("completed_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_source_uuids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Datasource UUIDs for the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#data_source_uuids GenaiAgent#data_source_uuids}
        '''
        result = self._values.get("data_source_uuids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase(self) -> typing.Optional[builtins.str]:
        '''Phase of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#phase GenaiAgent#phase}
        '''
        result = self._values.get("phase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Number of tokens processed in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tokens GenaiAgent#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_datasources(self) -> typing.Optional[jsii.Number]:
        '''Total number of datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#total_datasources GenaiAgent#total_datasources}
        '''
        result = self._values.get("total_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID  of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentTemplateKnowledgeBasesLastIndexingJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d2e2b3f4b07ac081d4cb0268539c7fdd1f6baa3c265e62b399dd9813348d1bf7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

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
            type_hints = typing.get_type_hints(_typecheckingstub__aa9dc305bb5b5d88f6b4829c77a91995e1c82c7c53304a53d48fb9b3e8ceba2d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuids")
    def data_source_uuids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataSourceUuids"))

    @data_source_uuids.setter
    def data_source_uuids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75d6652210ce38b837b159e2d580b96475485608c95e6f741da91cb8ed3a6d74)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceUuids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase")
    def phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phase"))

    @phase.setter
    def phase(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15948c9f70bb5c06a39b5a4db6b2a84a2298900d29e171add6f987876d3637b5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73cb0d1365f22a71b6b9c3ab333e10c57f1022e7ee8a72fb1b6d6dfed0310a41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDatasources")
    def total_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalDatasources"))

    @total_datasources.setter
    def total_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__031876788574d91956e1592978b5821477b4d3116419c2b03c695cf0144933ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5020e38c4275218b985a8beaf67b464f428346cca700970d2287c095da7e2e2b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[GenaiAgentTemplateKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[GenaiAgentTemplateKnowledgeBasesLastIndexingJob], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[GenaiAgentTemplateKnowledgeBasesLastIndexingJob],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45fd45f19894821e6bf1b41fbb141523e998803aef10f9faa8f4aef55105e900)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateKnowledgeBasesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateKnowledgeBasesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5efc14f3aa9e193b79e0663a9731dd0322087eaa7c35e489373c9f88ede9bcc0)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentTemplateKnowledgeBasesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f4c65f5649aa11cf74e5bb8115a94b793a176355dfa5d2d12a36b7582c839ea)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentTemplateKnowledgeBasesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e33323219da2e771de75556efd2d5a89ea88d2bb9cc7d6ff642ab20f645024f7)
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
            type_hints = typing.get_type_hints(_typecheckingstub__eb350fdeb52ea8d940362009a040a218bff3c2e3f7c4d6308e0a89b24eb57be1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fde936b05e03d6db7ffe6712ceac6321c2bb91d46b4d23ad9bdbb813d5e641b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateKnowledgeBases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateKnowledgeBases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateKnowledgeBases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a49a4ef05c59e3cb34d42ca844bc7d95ddf54062dbb542ec0a2ff08548e0b551)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateKnowledgeBasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateKnowledgeBasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c65dad30fd1390ee8e4c0a20d312708e5a6feb37fe74413a26e262e4cc61521e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putLastIndexingJob")
    def put_last_indexing_job(
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#completed_datasources GenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#data_source_uuids GenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#phase GenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#tokens GenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#total_datasources GenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        value = GenaiAgentTemplateKnowledgeBasesLastIndexingJob(
            completed_datasources=completed_datasources,
            data_source_uuids=data_source_uuids,
            phase=phase,
            tokens=tokens,
            total_datasources=total_datasources,
            uuid=uuid,
        )

        return typing.cast(None, jsii.invoke(self, "putLastIndexingJob", [value]))

    @jsii.member(jsii_name="resetDatabaseId")
    def reset_database_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDatabaseId", []))

    @jsii.member(jsii_name="resetEmbeddingModelUuid")
    def reset_embedding_model_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetEmbeddingModelUuid", []))

    @jsii.member(jsii_name="resetIsPublic")
    def reset_is_public(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsPublic", []))

    @jsii.member(jsii_name="resetLastIndexingJob")
    def reset_last_indexing_job(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLastIndexingJob", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetProjectId")
    def reset_project_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProjectId", []))

    @jsii.member(jsii_name="resetRegion")
    def reset_region(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRegion", []))

    @jsii.member(jsii_name="resetTags")
    def reset_tags(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTags", []))

    @jsii.member(jsii_name="resetUserId")
    def reset_user_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUserId", []))

    @builtins.property
    @jsii.member(jsii_name="addedToAgentAt")
    def added_to_agent_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "addedToAgentAt"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="lastIndexingJob")
    def last_indexing_job(
        self,
    ) -> GenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference:
        return typing.cast(GenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference, jsii.get(self, "lastIndexingJob"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="databaseIdInput")
    def database_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "databaseIdInput"))

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuidInput")
    def embedding_model_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "embeddingModelUuidInput"))

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
    ) -> typing.Optional[GenaiAgentTemplateKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[GenaiAgentTemplateKnowledgeBasesLastIndexingJob], jsii.get(self, "lastIndexingJobInput"))

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
    @jsii.member(jsii_name="userIdInput")
    def user_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "userIdInput"))

    @builtins.property
    @jsii.member(jsii_name="databaseId")
    def database_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "databaseId"))

    @database_id.setter
    def database_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ac8651d567250ab5a9bcef3ed833fed0334015e3d533db236c134b1d2885f14b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuid")
    def embedding_model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelUuid"))

    @embedding_model_uuid.setter
    def embedding_model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c49fe0e6eee567db3f1b8c4058f3289a538d59c80d0cfd20c998c6ea61a54040)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "embeddingModelUuid", value) # pyright: ignore[reportArgumentType]

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
            type_hints = typing.get_type_hints(_typecheckingstub__76b3fc076fbb054cfd5f23d89fb729cff8c07b1a05c0e0559b4e3b7a9e137cd0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPublic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4707dcc7ee3fffbd1c850e36cadd4a4d3ae22f6b719ccdc57f1053ec327dce72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97b1d58888b980b34104f4d5fd72704838e6433491adc64636475d6d41f47a0a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__37394db5be1308c77f0c53565ededf7e65d9687511d3817beaa5ff285428e9ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92952c0dfa9885cd65f0dcabfb30328db507acc59f15e2fd41780b699d3fdda8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3b75985056e1a5f44a7d8257a5430c7ec07388d820639c98f5c0f7e79a362a8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateKnowledgeBases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateKnowledgeBases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateKnowledgeBases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__462b435a3ab307608f118b57d44837d35401c64a694f8b2ac4f377d92b1970f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9091daef6d41400f8071b94d4e2e004e8d9511771ef7f8433e88ac2baeccafc7)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentTemplateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13b0ea0bd2a01cdd1cb66c83717b2db60f728076c33abe53c57ca934f9522048)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentTemplateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bee8ba3e2e8017a88122a1b269ab2bc546b2537af74b9c9d33cafd4efe39dc8f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6d2b2afe0bebb637d9b41b9069b12e00b24225539e7aff79a65befed4006e16c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bb3d4621b75e7cad63fd431d1ea9def11c005450b8805fd5c300e0883c266a39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplate]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplate]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplate]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c7d059024c4735ecbae9db886bef5a6e7fb065b93bc818cbde0d57434b7b1253)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModel",
    jsii_struct_bases=[],
    name_mapping={
        "agreement": "agreement",
        "inference_name": "inferenceName",
        "inference_version": "inferenceVersion",
        "is_foundational": "isFoundational",
        "name": "name",
        "parent_uuid": "parentUuid",
        "provider": "provider",
        "upload_complete": "uploadComplete",
        "url": "url",
        "usecases": "usecases",
        "versions": "versions",
    },
)
class GenaiAgentTemplateModel:
    def __init__(
        self,
        *,
        agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplateModelAgreement", typing.Dict[builtins.str, typing.Any]]]]] = None,
        inference_name: typing.Optional[builtins.str] = None,
        inference_version: typing.Optional[builtins.str] = None,
        is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        parent_uuid: typing.Optional[builtins.str] = None,
        provider: typing.Optional[builtins.str] = None,
        upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
        versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplateModelVersions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param agreement: agreement block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agreement GenaiAgent#agreement}
        :param inference_name: Inference name of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_name GenaiAgent#inference_name}
        :param inference_version: Infernce version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_version GenaiAgent#inference_version}
        :param is_foundational: Indicates if the Model Base is foundational. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_foundational GenaiAgent#is_foundational}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param parent_uuid: Parent UUID of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_uuid GenaiAgent#parent_uuid}
        :param provider: Provider of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provider GenaiAgent#provider}
        :param upload_complete: Indicates if the Model upload is complete. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#upload_complete GenaiAgent#upload_complete}
        :param url: URL of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param usecases: List of Usecases for the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#usecases GenaiAgent#usecases}
        :param versions: versions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#versions GenaiAgent#versions}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5d43f4c13789a41db8f25a4c6623430fb7c907f84e5fb66b5ab1e8e4d1934c7c)
            check_type(argname="argument agreement", value=agreement, expected_type=type_hints["agreement"])
            check_type(argname="argument inference_name", value=inference_name, expected_type=type_hints["inference_name"])
            check_type(argname="argument inference_version", value=inference_version, expected_type=type_hints["inference_version"])
            check_type(argname="argument is_foundational", value=is_foundational, expected_type=type_hints["is_foundational"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument parent_uuid", value=parent_uuid, expected_type=type_hints["parent_uuid"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument upload_complete", value=upload_complete, expected_type=type_hints["upload_complete"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument usecases", value=usecases, expected_type=type_hints["usecases"])
            check_type(argname="argument versions", value=versions, expected_type=type_hints["versions"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if agreement is not None:
            self._values["agreement"] = agreement
        if inference_name is not None:
            self._values["inference_name"] = inference_name
        if inference_version is not None:
            self._values["inference_version"] = inference_version
        if is_foundational is not None:
            self._values["is_foundational"] = is_foundational
        if name is not None:
            self._values["name"] = name
        if parent_uuid is not None:
            self._values["parent_uuid"] = parent_uuid
        if provider is not None:
            self._values["provider"] = provider
        if upload_complete is not None:
            self._values["upload_complete"] = upload_complete
        if url is not None:
            self._values["url"] = url
        if usecases is not None:
            self._values["usecases"] = usecases
        if versions is not None:
            self._values["versions"] = versions

    @builtins.property
    def agreement(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModelAgreement"]]]:
        '''agreement block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#agreement GenaiAgent#agreement}
        '''
        result = self._values.get("agreement")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModelAgreement"]]], result)

    @builtins.property
    def inference_name(self) -> typing.Optional[builtins.str]:
        '''Inference name of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_name GenaiAgent#inference_name}
        '''
        result = self._values.get("inference_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_version(self) -> typing.Optional[builtins.str]:
        '''Infernce version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#inference_version GenaiAgent#inference_version}
        '''
        result = self._values.get("inference_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_foundational(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model Base is foundational.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#is_foundational GenaiAgent#is_foundational}
        '''
        result = self._values.get("is_foundational")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_uuid(self) -> typing.Optional[builtins.str]:
        '''Parent UUID of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#parent_uuid GenaiAgent#parent_uuid}
        '''
        result = self._values.get("parent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider(self) -> typing.Optional[builtins.str]:
        '''Provider of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#provider GenaiAgent#provider}
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upload_complete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model upload is complete.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#upload_complete GenaiAgent#upload_complete}
        '''
        result = self._values.get("upload_complete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usecases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Usecases for the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#usecases GenaiAgent#usecases}
        '''
        result = self._values.get("usecases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def versions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModelVersions"]]]:
        '''versions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#versions GenaiAgent#versions}
        '''
        result = self._values.get("versions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModelVersions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentTemplateModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelAgreement",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "name": "name",
        "url": "url",
        "uuid": "uuid",
    },
)
class GenaiAgentTemplateModelAgreement:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Description of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        :param name: Name of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        :param url: URL of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        :param uuid: UUID of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2043af57abebc4ae573e76bbf6432067914c0fe373bbdfb814dfcc36c78a72ec)
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument name", value=name, expected_type=type_hints["name"])
            check_type(argname="argument url", value=url, expected_type=type_hints["url"])
            check_type(argname="argument uuid", value=uuid, expected_type=type_hints["uuid"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if description is not None:
            self._values["description"] = description
        if name is not None:
            self._values["name"] = name
        if url is not None:
            self._values["url"] = url
        if uuid is not None:
            self._values["uuid"] = uuid

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#description GenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#name GenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#url GenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#uuid GenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentTemplateModelAgreement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentTemplateModelAgreementList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelAgreementList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__63081977d05ea88a008672b904ec80eebabfab3f022f86500256f0916766958e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentTemplateModelAgreementOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06e9c43703a453754a2f2769ea9eb1aeb7d545ed44a378a3c5ca6046f1437ba1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentTemplateModelAgreementOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c5ab5bb8a586e6d7a093f10dbc097832992a7e2485a0f99db69725daa180b56)
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
            type_hints = typing.get_type_hints(_typecheckingstub__acf5dc8666b80d93dc7e7d5f17d91184797a03d6bc238de3f693f654fd220c11)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ae0dd261b3f0638eb3f4f61a930328912dd6d89701bae851f0a2c4ab2218b8bd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelAgreement]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelAgreement]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__60f4388d4850a48c87ef8f0086951a35ad67342a6f935a734896a7c946e1b5e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateModelAgreementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelAgreementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6fce60935f3b461298bae7d2e44bac910a3060b63a9907386ce44a31f3b11c1e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e2d915d98d6e76219e3f4464ab0e6ce0bc44c1a8a071540a19be2691c25a8dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d08bae95bf3a9f5635a5fe40f06b39689775d2ba6c719278803f1dcf7e555024)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51ce5f3d5b3cda5a08b2d300607d10af577e002455d949f1649bff54c6f9ecd3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88cfec1867140394cc44039cb3d637abc2271f883d7bbd6b43a8d14f6a0e0ea4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelAgreement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelAgreement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelAgreement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a35e74d38f92590144058111d9007bfd24d1d46c3c10fdf66a963086eef7e666)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateModelList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__410305e0301f6f48ea8b8e1bedfe977f89da45df36889940cbb7ba8af6e42028)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "GenaiAgentTemplateModelOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4fb80cdc74964fae0d2a3a6e39de421bf5a20f3541c0c139a70cb1ae0bc565cc)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentTemplateModelOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e0a54284d6c536440607cc76132b54aaf5346e0d8c6c9ac25f031f7a2091f88)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f8e7fc175a31fc042c2cfd4fe08b906b9cbeddf9efa0627ced7eb7e45c861505)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6b880252e515027efc6ae25199db2f8ef78a0e6aa9d3763950145d147ce18f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModel]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModel]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__921185faae11d535e344cccd22192684ab724bce7412b6373f5ea661d5f3530b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__167ce27a002fee3ac9c80098534b14c827893686f902684c563555b19d0e15a3)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAgreement")
    def put_agreement(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20c79269de84885d72662f20beeb8ed2197ced6cf603f339c2886b9fa49c58d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAgreement", [value]))

    @jsii.member(jsii_name="putVersions")
    def put_versions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["GenaiAgentTemplateModelVersions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3e5ecf7aaa3bbdc1a6a6b545d8dadc9ddfc23263946e44b31833a0ce11726e97)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putVersions", [value]))

    @jsii.member(jsii_name="resetAgreement")
    def reset_agreement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgreement", []))

    @jsii.member(jsii_name="resetInferenceName")
    def reset_inference_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInferenceName", []))

    @jsii.member(jsii_name="resetInferenceVersion")
    def reset_inference_version(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInferenceVersion", []))

    @jsii.member(jsii_name="resetIsFoundational")
    def reset_is_foundational(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIsFoundational", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetParentUuid")
    def reset_parent_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetParentUuid", []))

    @jsii.member(jsii_name="resetProvider")
    def reset_provider(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProvider", []))

    @jsii.member(jsii_name="resetUploadComplete")
    def reset_upload_complete(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUploadComplete", []))

    @jsii.member(jsii_name="resetUrl")
    def reset_url(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUrl", []))

    @jsii.member(jsii_name="resetUsecases")
    def reset_usecases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUsecases", []))

    @jsii.member(jsii_name="resetVersions")
    def reset_versions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetVersions", []))

    @builtins.property
    @jsii.member(jsii_name="agreement")
    def agreement(self) -> GenaiAgentTemplateModelAgreementList:
        return typing.cast(GenaiAgentTemplateModelAgreementList, jsii.get(self, "agreement"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="versions")
    def versions(self) -> "GenaiAgentTemplateModelVersionsList":
        return typing.cast("GenaiAgentTemplateModelVersionsList", jsii.get(self, "versions"))

    @builtins.property
    @jsii.member(jsii_name="agreementInput")
    def agreement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelAgreement]]], jsii.get(self, "agreementInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceNameInput")
    def inference_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inferenceNameInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceVersionInput")
    def inference_version_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "inferenceVersionInput"))

    @builtins.property
    @jsii.member(jsii_name="isFoundationalInput")
    def is_foundational_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "isFoundationalInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="parentUuidInput")
    def parent_uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "parentUuidInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="uploadCompleteInput")
    def upload_complete_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "uploadCompleteInput"))

    @builtins.property
    @jsii.member(jsii_name="urlInput")
    def url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "urlInput"))

    @builtins.property
    @jsii.member(jsii_name="usecasesInput")
    def usecases_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "usecasesInput"))

    @builtins.property
    @jsii.member(jsii_name="versionsInput")
    def versions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModelVersions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["GenaiAgentTemplateModelVersions"]]], jsii.get(self, "versionsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceName")
    def inference_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceName"))

    @inference_name.setter
    def inference_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6e1328057bce3f72771548a40fcab8cf852b615a68b16387002cbedf23ed659a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inferenceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inferenceVersion")
    def inference_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceVersion"))

    @inference_version.setter
    def inference_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d706b30a489a7ace18b383a09de6b5101996e613d94f36dbc1d838fe566bd7c3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inferenceVersion", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="isFoundational")
    def is_foundational(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "isFoundational"))

    @is_foundational.setter
    def is_foundational(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9f708c4daaa68b0469eb150a87b57dd5ab47d2d9d7bb114f28d06e5960c8d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isFoundational", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__394a22b4ad9a89c753f84e01ef5997980aaa3375ac747de66aa0b0ac5fba2c88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentUuid")
    def parent_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentUuid"))

    @parent_uuid.setter
    def parent_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__575ca64554af927c0344296431d099ac4511760b69039efe79056b4ec5742083)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1381d1b5bdf30efd6359bcbccd5c162d25ff29c1007b64d17e77ac2ebef39847)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uploadComplete")
    def upload_complete(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "uploadComplete"))

    @upload_complete.setter
    def upload_complete(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77be8241849ae894b7cc1ab178ba2dca5c0e73b9b9d576548bb6479797c1bee8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uploadComplete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ea57d5496f2b629581b61735a90b69f144d1491565a9a4fa95f509d3f793485c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usecases")
    def usecases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usecases"))

    @usecases.setter
    def usecases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cc343c2046c23aeb06fcc6ecf67d9b775bbb2e0b19ebf5ea3c2f6f4ea9ac892a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usecases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModel]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModel]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModel]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__649ebe59d7dbc1e843efb970036d57c3b519f86c4864069007ce4345aab82efa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelVersions",
    jsii_struct_bases=[],
    name_mapping={"major": "major", "minor": "minor", "patch": "patch"},
)
class GenaiAgentTemplateModelVersions:
    def __init__(
        self,
        *,
        major: typing.Optional[jsii.Number] = None,
        minor: typing.Optional[jsii.Number] = None,
        patch: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param major: Major version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#major GenaiAgent#major}
        :param minor: Minor version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#minor GenaiAgent#minor}
        :param patch: Patch version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#patch GenaiAgent#patch}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ea162ec38f272aae133bd22200eff1c090d39bcc206ec6b350edbe8743763ae)
            check_type(argname="argument major", value=major, expected_type=type_hints["major"])
            check_type(argname="argument minor", value=minor, expected_type=type_hints["minor"])
            check_type(argname="argument patch", value=patch, expected_type=type_hints["patch"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if major is not None:
            self._values["major"] = major
        if minor is not None:
            self._values["minor"] = minor
        if patch is not None:
            self._values["patch"] = patch

    @builtins.property
    def major(self) -> typing.Optional[jsii.Number]:
        '''Major version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#major GenaiAgent#major}
        '''
        result = self._values.get("major")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minor(self) -> typing.Optional[jsii.Number]:
        '''Minor version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#minor GenaiAgent#minor}
        '''
        result = self._values.get("minor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def patch(self) -> typing.Optional[jsii.Number]:
        '''Patch version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/genai_agent#patch GenaiAgent#patch}
        '''
        result = self._values.get("patch")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GenaiAgentTemplateModelVersions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GenaiAgentTemplateModelVersionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelVersionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1894a51500ac8da38a07b2224fb6d17001e61da902a08700effae98f32c223bf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "GenaiAgentTemplateModelVersionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f9152a3ee97a269204c141fc11c16c1a564a2afdb4f92820aa728d5c478a737e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("GenaiAgentTemplateModelVersionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__66f16bdb496c4ed016c37635f01e98f38995272eff86c1b60c078eb1a08fd249)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dce064bb2ca67922cd2122a825764a14e9b3c08072aa6295c48640ddeea503fd)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a830c218b6208b4fcfee7903fb9df462455612b2746e84dcb35fa5088bdc4801)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelVersions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelVersions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelVersions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f165bec7df9ba90805f383736eb9151586452118ad84be535850b196d9bd4f34)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateModelVersionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateModelVersionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c47a1e7fd1e1f6165e9a33962e0e3f67b6fae4a9c1d6e050e4f0f4e3800da98)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetMajor")
    def reset_major(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMajor", []))

    @jsii.member(jsii_name="resetMinor")
    def reset_minor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinor", []))

    @jsii.member(jsii_name="resetPatch")
    def reset_patch(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPatch", []))

    @builtins.property
    @jsii.member(jsii_name="majorInput")
    def major_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "majorInput"))

    @builtins.property
    @jsii.member(jsii_name="minorInput")
    def minor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minorInput"))

    @builtins.property
    @jsii.member(jsii_name="patchInput")
    def patch_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "patchInput"))

    @builtins.property
    @jsii.member(jsii_name="major")
    def major(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "major"))

    @major.setter
    def major(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a18cb78c6ea7abc06b08f7b7da42eafdffadddceafc8b5298403b87d89c44dfe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "major", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minor")
    def minor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minor"))

    @minor.setter
    def minor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e082722e681cdc927b845000cd0cccfd18a2489938ce3761f63c9b284a218d77)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="patch")
    def patch(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "patch"))

    @patch.setter
    def patch(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40c25888d1ff1d6673163243f7a02af9f7adcac932383604927e17f54aa8a232)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "patch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelVersions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelVersions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelVersions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f3947145a408fcd052d33fac0595af121730a498846cafdc27eceebb74a751fb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class GenaiAgentTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.genaiAgent.GenaiAgentTemplateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9b9c2dec03c83822452696b7fcbd8ca8dbb899cdee546f5abb75ded638689127)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putKnowledgeBases")
    def put_knowledge_bases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cbd7d60c1ade6cb58a99cb283cd38108c4d43df794db2e86d58d6c358e898066)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKnowledgeBases", [value]))

    @jsii.member(jsii_name="putModel")
    def put_model(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModel, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02691845375443bf4a19fe1de384030cf9f68201841c98ed0059cda3fdd8114a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putModel", [value]))

    @jsii.member(jsii_name="resetDescription")
    def reset_description(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDescription", []))

    @jsii.member(jsii_name="resetInstruction")
    def reset_instruction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInstruction", []))

    @jsii.member(jsii_name="resetK")
    def reset_k(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetK", []))

    @jsii.member(jsii_name="resetKnowledgeBases")
    def reset_knowledge_bases(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKnowledgeBases", []))

    @jsii.member(jsii_name="resetMaxTokens")
    def reset_max_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTokens", []))

    @jsii.member(jsii_name="resetModel")
    def reset_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModel", []))

    @jsii.member(jsii_name="resetName")
    def reset_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetName", []))

    @jsii.member(jsii_name="resetTemperature")
    def reset_temperature(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTemperature", []))

    @jsii.member(jsii_name="resetTopP")
    def reset_top_p(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTopP", []))

    @jsii.member(jsii_name="resetUuid")
    def reset_uuid(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetUuid", []))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBases")
    def knowledge_bases(self) -> GenaiAgentTemplateKnowledgeBasesList:
        return typing.cast(GenaiAgentTemplateKnowledgeBasesList, jsii.get(self, "knowledgeBases"))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> GenaiAgentTemplateModelList:
        return typing.cast(GenaiAgentTemplateModelList, jsii.get(self, "model"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="instructionInput")
    def instruction_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "instructionInput"))

    @builtins.property
    @jsii.member(jsii_name="kInput")
    def k_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "kInput"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBasesInput")
    def knowledge_bases_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateKnowledgeBases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateKnowledgeBases]]], jsii.get(self, "knowledgeBasesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTokensInput")
    def max_tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTokensInput"))

    @builtins.property
    @jsii.member(jsii_name="modelInput")
    def model_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModel]]], jsii.get(self, "modelInput"))

    @builtins.property
    @jsii.member(jsii_name="nameInput")
    def name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "nameInput"))

    @builtins.property
    @jsii.member(jsii_name="temperatureInput")
    def temperature_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "temperatureInput"))

    @builtins.property
    @jsii.member(jsii_name="topPInput")
    def top_p_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "topPInput"))

    @builtins.property
    @jsii.member(jsii_name="uuidInput")
    def uuid_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "uuidInput"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb46def812359337a27e9e806ab21cb7bb21714c26378661c65bc6b9d926ed5b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @instruction.setter
    def instruction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04434eca95169dcc0ecd5d079b8d99984a7312e3745b4566648c7c90c0c29d5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instruction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="k")
    def k(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "k"))

    @k.setter
    def k(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20adae04337994db7df9b0997a624cde1b6a3451e1c59935aacf7411434fc710)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTokens")
    def max_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTokens"))

    @max_tokens.setter
    def max_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3769b0ea5875e1195228e3daaad5fda93bd227331680a6e7d924e95dc9770bf4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8bcb972db6f83865fa87d8cebc60172f1dcce9bde3e096416925ea7b3e44bd12)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="temperature")
    def temperature(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "temperature"))

    @temperature.setter
    def temperature(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3a9e08455a8d7693ccb64a01abdf76091de5e0ca8b2b275c68d4b4ac79a44eb6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "temperature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topP")
    def top_p(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topP"))

    @top_p.setter
    def top_p(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23fced514a94feb605b8ba48330164d64766119c661020afaaae42d058a42b8d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topP", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d430c77aede2f60cc8793f70a74484992b654af8300ee7c177b950bfd161810a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__04732ca6c5cf19846f22af8a411b2a34ccaeeb33373fea73a8972637acbfa101)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "GenaiAgent",
    "GenaiAgentAgentGuardrail",
    "GenaiAgentAgentGuardrailList",
    "GenaiAgentAgentGuardrailOutputReference",
    "GenaiAgentAnthropicApiKey",
    "GenaiAgentAnthropicApiKeyList",
    "GenaiAgentAnthropicApiKeyOutputReference",
    "GenaiAgentApiKeyInfos",
    "GenaiAgentApiKeyInfosList",
    "GenaiAgentApiKeyInfosOutputReference",
    "GenaiAgentApiKeys",
    "GenaiAgentApiKeysList",
    "GenaiAgentApiKeysOutputReference",
    "GenaiAgentChatbot",
    "GenaiAgentChatbotIdentifiers",
    "GenaiAgentChatbotIdentifiersList",
    "GenaiAgentChatbotIdentifiersOutputReference",
    "GenaiAgentChatbotList",
    "GenaiAgentChatbotOutputReference",
    "GenaiAgentChildAgents",
    "GenaiAgentChildAgentsAnthropicApiKey",
    "GenaiAgentChildAgentsAnthropicApiKeyList",
    "GenaiAgentChildAgentsAnthropicApiKeyOutputReference",
    "GenaiAgentChildAgentsApiKeyInfos",
    "GenaiAgentChildAgentsApiKeyInfosList",
    "GenaiAgentChildAgentsApiKeyInfosOutputReference",
    "GenaiAgentChildAgentsApiKeys",
    "GenaiAgentChildAgentsApiKeysList",
    "GenaiAgentChildAgentsApiKeysOutputReference",
    "GenaiAgentChildAgentsChatbot",
    "GenaiAgentChildAgentsChatbotIdentifiers",
    "GenaiAgentChildAgentsChatbotIdentifiersList",
    "GenaiAgentChildAgentsChatbotIdentifiersOutputReference",
    "GenaiAgentChildAgentsChatbotList",
    "GenaiAgentChildAgentsChatbotOutputReference",
    "GenaiAgentChildAgentsDeployment",
    "GenaiAgentChildAgentsDeploymentList",
    "GenaiAgentChildAgentsDeploymentOutputReference",
    "GenaiAgentChildAgentsList",
    "GenaiAgentChildAgentsOutputReference",
    "GenaiAgentConfig",
    "GenaiAgentDeployment",
    "GenaiAgentDeploymentList",
    "GenaiAgentDeploymentOutputReference",
    "GenaiAgentFunctions",
    "GenaiAgentFunctionsList",
    "GenaiAgentFunctionsOutputReference",
    "GenaiAgentKnowledgeBases",
    "GenaiAgentKnowledgeBasesLastIndexingJob",
    "GenaiAgentKnowledgeBasesLastIndexingJobOutputReference",
    "GenaiAgentKnowledgeBasesList",
    "GenaiAgentKnowledgeBasesOutputReference",
    "GenaiAgentModel",
    "GenaiAgentModelAgreement",
    "GenaiAgentModelAgreementList",
    "GenaiAgentModelAgreementOutputReference",
    "GenaiAgentModelList",
    "GenaiAgentModelOutputReference",
    "GenaiAgentModelVersions",
    "GenaiAgentModelVersionsList",
    "GenaiAgentModelVersionsOutputReference",
    "GenaiAgentOpenAiApiKey",
    "GenaiAgentOpenAiApiKeyList",
    "GenaiAgentOpenAiApiKeyOutputReference",
    "GenaiAgentParentAgents",
    "GenaiAgentParentAgentsAnthropicApiKey",
    "GenaiAgentParentAgentsAnthropicApiKeyList",
    "GenaiAgentParentAgentsAnthropicApiKeyOutputReference",
    "GenaiAgentParentAgentsApiKeyInfos",
    "GenaiAgentParentAgentsApiKeyInfosList",
    "GenaiAgentParentAgentsApiKeyInfosOutputReference",
    "GenaiAgentParentAgentsApiKeys",
    "GenaiAgentParentAgentsApiKeysList",
    "GenaiAgentParentAgentsApiKeysOutputReference",
    "GenaiAgentParentAgentsChatbot",
    "GenaiAgentParentAgentsChatbotIdentifiers",
    "GenaiAgentParentAgentsChatbotIdentifiersList",
    "GenaiAgentParentAgentsChatbotIdentifiersOutputReference",
    "GenaiAgentParentAgentsChatbotList",
    "GenaiAgentParentAgentsChatbotOutputReference",
    "GenaiAgentParentAgentsDeployment",
    "GenaiAgentParentAgentsDeploymentList",
    "GenaiAgentParentAgentsDeploymentOutputReference",
    "GenaiAgentParentAgentsList",
    "GenaiAgentParentAgentsOutputReference",
    "GenaiAgentTemplate",
    "GenaiAgentTemplateKnowledgeBases",
    "GenaiAgentTemplateKnowledgeBasesLastIndexingJob",
    "GenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference",
    "GenaiAgentTemplateKnowledgeBasesList",
    "GenaiAgentTemplateKnowledgeBasesOutputReference",
    "GenaiAgentTemplateList",
    "GenaiAgentTemplateModel",
    "GenaiAgentTemplateModelAgreement",
    "GenaiAgentTemplateModelAgreementList",
    "GenaiAgentTemplateModelAgreementOutputReference",
    "GenaiAgentTemplateModelList",
    "GenaiAgentTemplateModelOutputReference",
    "GenaiAgentTemplateModelVersions",
    "GenaiAgentTemplateModelVersionsList",
    "GenaiAgentTemplateModelVersionsOutputReference",
    "GenaiAgentTemplateOutputReference",
]

publication.publish()

def _typecheckingstub__d8ad15c6eed73b0e5f68e4e306d1928365102a6f7a62128ec0c97e04c1cd828b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    instruction: builtins.str,
    model_uuid: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    region: builtins.str,
    agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_key_uuid: typing.Optional[builtins.str] = None,
    api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    child_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgents, typing.Dict[builtins.str, typing.Any]]]]] = None,
    created_at: typing.Optional[builtins.str] = None,
    deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentDeployment, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentFunctions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    if_case: typing.Optional[builtins.str] = None,
    k: typing.Optional[jsii.Number] = None,
    knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    knowledge_base_uuid: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_tokens: typing.Optional[jsii.Number] = None,
    model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentOpenAiApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    open_ai_key_uuid: typing.Optional[builtins.str] = None,
    parent_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgents, typing.Dict[builtins.str, typing.Any]]]]] = None,
    provide_citations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retrieval_method: typing.Optional[builtins.str] = None,
    route_created_by: typing.Optional[builtins.str] = None,
    route_name: typing.Optional[builtins.str] = None,
    route_uuid: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    temperature: typing.Optional[jsii.Number] = None,
    template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplate, typing.Dict[builtins.str, typing.Any]]]]] = None,
    top_p: typing.Optional[jsii.Number] = None,
    url: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
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

def _typecheckingstub__e6b2b05818d707f1696237ccee85341c07300b06a592cbb004db693cf7771f03(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb4dd3c7de22ca49dfa2a1804b444eb491344e3afb3a40fa18f1d261975f9daf(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2c4c185c6505e127ae3a374b0da82e8cf2c671263abbe1cbe0e7f6c6eff5914(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__267b3ca15e3360e1f10dbe222f262d3ada1115cd68d913360f8eadf9ce7d60ad(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c57e52ff4a00c6e8fc8db158fc1ce3b6535d8a7132941c5cef4b76afa3daa64d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__582ad8e5c4a1f4b8d6674c8cb50523d6bd432b93b5b33fe5b497795cb68b147f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6d225646d51ace5b98ed4bc6cf34e07d2f3a38e8bc553cd157cb020b798ea25(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a08d93585900228b9646464bc701a8548d334f14b802062aa07e1d5193ed4249(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgents, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06b10067569d609ea09022a43e3390833a28da96a9c45790ee47e88a20c500b4(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentDeployment, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f479d01a6e12f1207fe5a357551cb135b1525f2bf0ed1d441afbd914e30ccb0(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentFunctions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c62d9b4eb8ef54ae7667ddef9002557c59e95ba4466ab89a12c147ec087a0f13(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__611c6b7ae39f2ff17759633d795165d59f8513a272a9da0fe866f7672bf82412(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModel, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1eee1f4491176fb38d55103c37d2b577f3ce5a9ea5e7f87a43fa213d2f93640(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentOpenAiApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9a0d413e1a8740fcc213096bdb04008272d5f21ebd582d0f8678e1b6c46abee1(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgents, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3914d50054b5984ec44d21896ce99ce613cb8864df461155444d87de0ee0f220(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplate, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d81873a26223ec29313f6e2cd8172a1a41336384c90e451fb32aac3cf2709cce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85adbc481545966c67a7847450287c72ab790543c5cb45777926b251e4d61fb6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a87bee0f257f12077898aea21e027fba170f43f1ba07bfa8e89f06a391ad490f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9b2c3fb6380cb6ab5f750b7811264a1118d31280a78a0c100b68619fef6754e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d4affd44a3a101d74e4031f1631bbe61431da9713a9edbf720d2926a54fc51e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__29ddc31bd6028f28962f457930a28d75b89b2af569634898507338a5279f1922(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da8d2ea0e14ff5d8ef91f32be837e9cc98d745c57399fdad8bb393347c45400e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ec0435b6f09cd28d46fe0a8e91f2e6ed8d0ddea75766e97a6b14fbcb0e0944a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8428a7d1976ef3b7a8f6ecda84d281ee5f2455827827276b7ee6f0cb6e1e9417(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0a73155e6964184cf67dc542ad4865febc5666d5790b9473cbbaba6edd13091(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3259b1cf1f998bd0017a11db3fd2cb7ea4575fa5e9bef5231b49a4feb7b4fc39(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d8f2ec288a4e624527323ef46d7c067e9e781f290e52c31f99da489ddad0d0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44c0edc416b656c709073b1904f62c20b1eab3efb55401f75e35269242cc58cc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__072aad9e4f2c84953f9380adee092a97950cd8dc1fd57a54f9b4cd0876979cbc(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c82923fcf2aed497acb9cf7a246bb6608b70e87bb038920d6c3063b33b7defe4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c27a700463125fad4b177e60ba50e6effe845b208410826323857340c4b7b33a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ff53d503102e9800ab44dbca8588eb455f9f96d86ceb0e56821d5a6eb8745b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3afa1e02b7f113706360fc391ff4f7388a7a6f68228e23d963bc22c743acdbda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__282f84dd62a95e6eb5a04933ddb5cb39594bd1928b5a0e459a9c6d12bf62e6f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b94564e0f17d631b2fdd5803fb2de9cd45cf242924013a7a1cca50f9d1fca10(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3b2472b53437b3cb11f8c24b980eac788a3fa21d753c2360f97242c0e16065f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__184867ca0a917fc7a63d7f0f6bb2cbaddf5f13cb8a2d22bcbf7c0e7c834d6b37(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4aab4b94873f2bbde16985eaf79130aade0a123482b50e076f3f377c79d8649f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b9f1a9aa0da7b6272423849a340b9fac4b5040c097dcf612830d0fcec87117c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7566d41e587e4385181babbdf0ffc04a44a671a453e355436da33cdae5967c3(
    *,
    agent_uuid: typing.Optional[builtins.str] = None,
    default_response: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    guardrail_uuid: typing.Optional[builtins.str] = None,
    is_default: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    priority: typing.Optional[jsii.Number] = None,
    type: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a75119a431736970e588cc4563ac784afca97c2471c3c51717754f7e024c3e5e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4f8b58ea3dd89e1bca8800f27118aaa360fce8503dabd96b49846182c1bc873(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fad4a93114092bd64f78efc131128335d4dbc8197730a65dbbf94970f625022(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__165d385bae5a3a65407f74e9dcd9d1878e2c39a6948cbabc61fccc036a32c689(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa601f9c31d9d5dc606bc54d852da68e316769a12f766173bc73283eaca0f09b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d0647809526fa1dd3ca9afbea21b45698c1d6a34475e99567bb2bbec738a8dd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAgentGuardrail]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8e17bb6c72913753d3cbd0e0b0b29eb29ba2a9589b7854dca5df1df23982381(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd25aefa5b6a673e5bc604d700b005a465cc4ad70fc5279592389d458ec548a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e785edc77fe9c2954d1dd88a133cdcd37b6be06b4920daac7e86159eb02d96f1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__272bcbc6975a05d19b0cda338cb4460370f5f319c58ede08806d9f17aaf07d89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de8553a6bceda9cefc5535f27519c4059f1ec26cc81b12d6b095191d0cdb8fe7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f398074e61625562ab1dacbaf045374a6d00e2788af813bc7c1f9138dd5f9aa3(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94b496795cae80d022f9cb135effcce376c45233f86002f6e70df1ea2bf881ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c90a1e97eadee6fabdb34d2761140b9d02830477791bc2d7a850e05f7ef6e7a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96bdacd29d6d0acc5502ee406a48eb86d8d42d158e845291d56211c47575f893(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__917dde05c244c4d09700034e14a35ce1acd8f36c68005e934412ddd3926e20f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ac2569e10820d99fe8ffe1aba8ae58da126f83c6abd69f69b19ad8a12f488ff(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAgentGuardrail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4ef67f53293eef1562e17b21fba05e809d571c92dd5ae9b94cb3ea5a3f008762(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db1b227fe49c8b6f2fd264298c7e500ca3eb3f4d76e45bc152b0a292f8b0634a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__817eb7a0173601d4f72f2a57731cb34d9efa695bbfd3da42029a90cb5627cae7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a4483b1f5caa2ebdfdafbf2e4fab138ee683f2c467332cd794374cf6e1a5eccb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a39abb13df042687c08e068ad1bf9aa0f455a6d459b5cbfda812e3258f7db260(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec1ed65b5d0b241cbffac16071d8aec71e5b9ecc56249142444b0b6e0f1324e6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f950606dff36d70a94a78c3da74ea0ecf5eb9db7bd4b9402508bb6aaef8ba706(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentAnthropicApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__040e784819e33147aaad2d4b6637a267a66f4d0d495510405a24c8affecdfd44(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c6cd9d09006e7edbe1ad748e99af49060ab0608d571b7a4b54b0e502eb8c649(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83c89015fa71628179ae0225194e02eeef03699b26a08262dc0246886fce8fa7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c1cfa1c7ee7327efbbdef0b43450f7ee2a23a714161c9c512d4128094316df04(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88006a8aaf9ffc0fd27f2c96b47e2a0fa78db205f88a17a1152887ee1b835493(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentAnthropicApiKey]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__564aa1ceae6821db77edf4e07e7588f64d5ed57588fce3ed3d50b096fc854590(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    secret_key: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f4bb46e3ebcba97a519cd637e5ac42d6e14f495c0b179a676953ced33d540ef(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c2fe0973f3dfed0d9a7440c31e53ea69210880a8071de18893b45f892919517e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3473f287c971b9134606161db7c6535b68c9d947bbbc56d41604b0441b1e6e0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__840d9b113286ad19a28cd0261e5217b949ec6a11789e979443d0d44efb0b9127(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8590f9a0c388f6604aa99a9da1b7bfced112580df3fb73785d412c4938f0176b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e1ff5f3c56af29c33d14c1f248118eaa150fd94dde44682fe1f3977003e958b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeyInfos]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c1473e387216405441b30885a29625ca05c88439fa3fe912b095d0114826e50(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4f4212e2ae5c256dc3896d2faa19844152b7054052cc168337e1622beb2f035(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf9b7a3d6688f7dad46bab71230e2f919a4171c4e6d23ebc1f859b3d1c454712(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef234978c8673dfcc1f65fe5870d0e5fa9191c9057af26a1d9ca8051bebcb185(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97bbb21e465882710c57e004d532ef7f06e2767d936a472df0d71a07f28c7e19(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87aa100e823140284901fa8fb8e9db4bdcc6ad4e3cdc024a98b0a3f43995d9fc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeyInfos]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de90b9f1f47cb988a825c9912fda0764ac837e28cb6cf35d787b0cf63b1f7acb(
    *,
    api_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ebdf5ff47ae1ec8f216fc92545a4d93336807f2873130b531e1aaffb78f3b48(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a74e7484c3cf2340a45b20835a1f98fac07ef1dbca2ff913c47046df287de830(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__010c19c8909bdd022e3046eb43bffd478a882c9298f600736d0c62308cc1bd30(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f2be1ca12047418c7a62e0b92d2b0ab0aa03d569d2ce76ef099c4de23bc8d85(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11cc274db16b194eccfe4c64edd34984c46f6bbe88c132cfa211461f76cd8e92(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8811cb85c6fe74b5c61dbc160dc36b2e3f46ee1dcf65154bab8969f20e708a94(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentApiKeys]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a7226514e2c816731a0105123c0e90c2f7c335c09a5d5d85e3ac51ffd785350d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d4e31555e008a358d2fee013ff51d619bc2024d85e7f6c36e8d0717f1f0cde1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31171dfe0f06118da6e1d918a5736ef2c5b4d3864f10e4074499bd7404533432(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentApiKeys]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3b48fa6c77125752b88c1d965b4db4cda3ea1ec45b9b531d39b3f62c09540212(
    *,
    button_background_color: typing.Optional[builtins.str] = None,
    logo: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    primary_color: typing.Optional[builtins.str] = None,
    secondary_color: typing.Optional[builtins.str] = None,
    starting_message: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__79a3e4b4982d214d08a98760d1adf11d6e716b1dadc772be1feacaa5458e50da(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__878cd1295cb9dd82b920782afe229c5b7abb9689d2cb277b36f7e1e52f316a72(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9efd013260f178227e8648103bbee6cb1da5b0de1e36c1b39c677fa1dbe23ddc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7094cd1e00d3bfbdc75a0775ecf67e09c00b58217b26960b67674a94d7868d81(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53a6a7d1d1686adea8435dfc11472b94cf1fec8ac4b661b2a100c85ff75dfa72(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31a85f1e7405bc8139ec95d92546215c14ae20425f6d871b66b54a4b661eb62a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbotIdentifiers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__69b9d8485efbd2078d9f24472df6766b263446c1d32e6578de65d496f664660d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__670f3f44520e259bf7fda9522c7bce1b8bfce22af66426c4a4f05463080c76e3(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbotIdentifiers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9dcd7f16911284d3108d6d5b7cc735e1cd80ab131d35ec0fcd0397274d1352d5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__278af6605a5e395c67ff045739d60c5e68e682798df17351099a18e929f388ba(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca65b6855b3bb4033b22111bb0382b966ae559aa8dc90bf20646769ce0c8c6e8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6e7f64c9970bad09e605e5eaebf457d80fceed035cbe014958f239023989b2c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8603ec3cc1f5dd254fb39692576430548c418fa2b7fcf8a86b784f53eff938a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6abfea6b9d3ec416f930b9a6adefaf7dd4f668c59a51d9ecdf3ea558266d11b1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChatbot]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2edb9c2a6754f5471756a30e7324d6eb1e8fb66c92487e41603b49eb8c9068f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37db94d1dd160f7626c106a076442422afbe4739b1ef14033aaa11112ce1564b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b61825ccd4a8d0addf4c359f720bf19d9d589c2ec90345106cb0eaffaa5e806d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f69014e8c02b8e4be236c3e0c0c66d778341f826ea1c58b0902ac1d56e93ddd7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32691138c06f220ac2bd16cb920b75dbf4e20d4ef4d25531297541235e566e06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab8677e3ec56f36f8dde1a834a595381a493b2a9c68eadc515c9e09272e67361(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3f62f7688600d178b3910aad332f3e2ae21fcd37aa753c313dc97b933b1c0a3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8551be7c8cf1a817d498b669c45c55a210254bc9490a7bd8d35dcaeb75e9dfd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChatbot]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d169eafe552bfd7016793638009c7609e1d40d95cb64d80062aa23a223899afe(
    *,
    instruction: builtins.str,
    model_uuid: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    region: builtins.str,
    anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsDeployment, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6acfe5f6e27ccfca6297ec8173fe1059b38d96408909b0cb5bf883d26b99155f(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb9267c90514737f12e1397127a69829bfc6d2bd218f56a68a4de015ff95de51(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cded6037ccef18815ab5719e983307101497530187273f287ae1768e76fe4561(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae39f4f92959cfd503eada386dd225bf5257a437edeb5c243a10e0e03e8f5c21(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34eb3e1ec536fb7bfc1693e59e72d4eb9d1e19d2253f85d8f57de0a5e660c340(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6ddf7768830c9b8f65113f566ec1cc791c61e71322c9e3d67c75cd3bf868d2f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b83ad80bfa648285d19348b4f748359799d4df8d62fe88f4028232c939e100bd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsAnthropicApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8b6d32b8aedc625c0508f195fef4700424bd932bb0c0a90b5a75f0424ef2566(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bf9a7e880dc95cb7d3bf349a144c85f93c018f6ce9c62ccb8db5f816eba073e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7140732a3bac55f95bd331a786e75ce40cf76e1b6beca2b49aedbc125332b22f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7302504f664d23f8c0230ade6752d5fa3430049fee86db0c7a69e3e6c76f99d0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb4f8869a22459022299210c13594b609204e72661b2cb769b5af9237126933e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsAnthropicApiKey]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bed0ddfebdd50fb65a71698cb95aa81b09001b83be36f6f5b00c7925a636448f(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    secret_key: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f9b3f2ddcd671f6a311f893398dbe62f497255bab90e571da286ee6322d20f7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1cbe40d4139f3092bb78b6fdb7b839c995774f5511ebf11a327e22d155939e2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3493419117b3f54aca4e10e56b102afdee6d2c9bb71b27d3b11a5c0415ec83a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e66b0aef97f1e0e4df91f79a901708e0d3cccc7fda5c203f3f44004a1f221d9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__14f54bb025d5dc0b8a33cbc1a1e7b8cbd74597af87432278717764cf74cdb945(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__367424808c3740dad43f442e56252acd46d663a6e92b27a07a9749ad63be516a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeyInfos]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f79d8212d77cbe6b80caea0dbb10b679989e3750ad1f40baa97e455d536f701f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c666545537de88d4b4996fd735678d2bd44418a0933638cae657b0ec672979c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1afe18f79a6364baec4849e611a5a0f7dd7a5b1dbf5a6a9048f83cb02a2c57ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d3b5e63d28b3651f66250ee8ea60c149660ebfb569c59f3f3435bc4e4f2fc16(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fbfeff4c1c9f254317fae1a57822d68e88cb17cbdf4482d839555cc2329a9ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d919775cf4ecae36ce709bc27496f7a427bf215b6520870326da6ff5d58e3b1a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeyInfos]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e063fe8ad92a99ba5c03752d4b1a10e4f2d40789415379364ce5f3fcdfeda90f(
    *,
    api_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8389dd8819f287be73bfacd0f3c5ea3be013c4f48339310b7c164a71c213ea77(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed4888a77679a2d545324334ea71bf14d349289d4fd8274febd5039e37e8fb39(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a996e8bb136b90428108fe3c6ff7e836039b8ef983af68f1d4d4bbc97131ec8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__639efeb4e7ff2ea271bed3bd93ba676e41bde704f7255e9f3028e50f381f0a86(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__505e67ec0ee06cfe043db42b0df95ac4237f81ad644240e599bbfbcb0fa55f85(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab02b0465a4604ba93dc507ef950d2e0584e2f0078cc302c9d8c2c8caf17345e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsApiKeys]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c28ef3b34805456e9d87fab89c63cafdccd9988990b5cb3ba212e7497aaa8c20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6f4574c7ca06f316b86ac9c159ea4c8eb39811c542b4ccdead1093740e3e96e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4065a00b0edc0467ab34b019d33ccd4ee3f9f8d984c6219f6dafe92bbc9f217c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsApiKeys]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74d855fc08af425a2e2044b6337850c97a4ccd2cd1065c028ddbaf28542e1c67(
    *,
    button_background_color: typing.Optional[builtins.str] = None,
    logo: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    primary_color: typing.Optional[builtins.str] = None,
    secondary_color: typing.Optional[builtins.str] = None,
    starting_message: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__038649f18bab9dc8ff641c3ad57c3a2600241ed30c8fb3f45a249613944ed46c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ac2676bd377f3e04f485381aaa4e727edf5939597fe4aad879abe537ec3cc22(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61bf6a093a09658244b59d774faf565360e218e105625ebe5a128359c5f8092b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b9161d2cf3738df24c62882a04d76092afe7b2f90b37c2a947e15ec79327fe4f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daa7e557bbedb38d86a444e77b1d6011cdd6ec4b208ab1b6cb3c085173267d2c(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea1b115019572f92a67b414bd9a32b8d6b50cd8bc2af68fb658682fafd07856a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbotIdentifiers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0f5e8e9b05754c50d10de53ec0c39986321dd0cc0bb75d29cb4478fa34a7dcb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__246a472d3987106133763cb60c64b88cd5d7b97dfacc14661ee73ad0eb0d5286(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbotIdentifiers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1da78e0e8361326c458684e7d19a717df5267c56d8b89d881265e434f86f183(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b05bb5c69c639378c5cef533630543b6e137936f1e7699e49c66478773d0fd5f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0bb3a36987f259568b9efaad3fe073243098e240e6dfefa92d5adecfdacad5e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3cd5997c56ada02dcf3681715de2d206b9244239d5726c17c037e003b18ceb43(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a35d17e44c72000ae52f1fcdcc642165153e530d1c7c331a36e99ebad8308c0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b8d842cdb744bb82da098d03b446e945d02dd80b6d5f22983e583e824b8f5620(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsChatbot]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10a8f087250402fe6771d299d1a55e4e2125c908a15a7bb03cb7e41533401642(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__330b609f80b8bcd331f9f6055f2a24940ebde40e0c5508322f5de4f5cb06b382(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86266f03beeb10239e8d5cc949f35b1e74e493c6e317e07358fc6879094defa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97d7a9325890cb2214b83c101b6d9ffcebf66d6cd857095ebbda90bee0479298(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae532fd14f4a8bf0e4d44e6d2e9cd5832a814bcf910dbe12105cd1ae0c13d3cf(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48e066cc04a0ba1242a70d31a74bc5e52a6e0665b948965c12df8d64336f2532(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8d0fa1e832b93d7e102f96bf1d4f5d45ed45c5d8884a82e82fffcfb0299723a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49185662c13695ff29f5d310caaa7110c4a8b9977a66e80b29641570304beb7f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsChatbot]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d54e4276bf728eccce57cd78723f2a0fcfcccef573ef5a9f67e65fa0949ad78(
    *,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    visibility: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f40c556fe5bf0c32c16d5b70e15697b8e86cee80d0c698d7c0abcb59e4d83a70(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa1d008119ea0dfbc0466ba8a5e645dcc8b3870d7b8cc94242e18bbf38ceb8e7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24645c3758a82d9470f7f8fc49b5a9e9475d5a98157b7e2d112e5cd3fea5ac4c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2050b2b6f8981ddf2fe4e4d0ee7432e4f9a4812b3bfae4ef6147adb6c1cc3f2e(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66fb1dda78e3b331d678a0727b5d170c20ef912a13cffe7bded95cd9e63584b9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__716111a5d6724aab55b14ad363591a75b72e3306521f1f6c7deb6b7d83702508(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgentsDeployment]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b75d0c8d09d2a432b2fb8c74f48ea0dea1b49d350f66b95acca210b6fc29dbbf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc9d3cf945ac666fb6124d1b0cbb148bd51a8eb81b35166bf5fdc075a3a08050(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__896eb5bea0e9680e80aa117d4ccec768b04a4b6e66d26ca093e5092375d12c22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a7219ad383438d8e06252d5dd16517005732fa5852db083f145b93bc4cf021b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b900d68e9b4412d1a22a93989a378edfc79487fa0855c9afe6a3ae1d41626f69(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63f4d1bb22ba00ee6fc41df2a9b1c64ca4f485402c4236f3f860c76d21645162(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9fee7866719b70d243235ea851982c2b1f7f2868720971626bd132b039d526d2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgentsDeployment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e966efa6581b6658a0db60d74a233db1276bd72c9e312d7c041a73082da7b91a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf6e8e0edc46614dbdc2e7cfa6e02ee3c71eeb439d4b3639bf0bcd85f8495c33(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58f03c8a2b64457b5b886b27d4d1c2d0f47b02376f21a2d2c2f2c862f5450216(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__979b6318e18a2fdc0cde5b9f930fb0676c1d9ae2d84eea9a3554aa905757bb09(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6818b677db392015ac0628e8fe1a6d0d5602900c9b2fd9eccfbd0f5b7776330a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16930b1a4d4dbbdc501f9f46df4bb38bce681567a5ddf31e85667b3246b89660(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentChildAgents]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0f96413c57fd4ae3e03a4e6ccb0beae2cc4d27bf8ce9d9e1025fed609195ca1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__864335562f30fff6b6fc3783227380885842056f2f933470e29648bec6cf3744(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b1713ace72f234d0821f69f25a46769376b2ab576fc3876f29f22de558f38b7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__42d5e6e2ac60061c5d29b06651379a79b8041f188c826434f8043cc7972903fd(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsApiKeys, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ad4a0897549c768cbcf42053a90bcf9d98fe2fd61e8f06590fb5e2bf3658fb22(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsChatbot, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__474c2df064be6fa22b3664034aa7f8872949ad6ac99cc2d9ef1f0ceffc2aaa2c(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ac4b81016355056b89953707395eeb3362c6dace92f88a1558b809044cee888(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgentsDeployment, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd0d902c2cda4500ba557b0389bed9f6f1bc2ec93b2d9677090b03124ac055ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8cafd360c4eeaa08e33721e6e7a2a7bc58e126e0b6f229a52db2333e38ccc625(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__27356f093cfd5973b5109da874f7ae6de416cae1a35f3938073a77cdf7352498(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f496df4e6d5e9a2a2516e8d92cb3567be356db52f8b54ce8e62ac610dcae877(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ccb279c0d3d24e814a29e4bdbcdb81514a84d68404066e428ef5f38656805b6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73c8f9fdeb4957426d148a770457cd2e7a4d472b8a8daed828cdde4be4658862(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32d7110dddaa9870a7fa5baa37e297f72cbad4ea467836e8bc9d3eb60caebbc0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentChildAgents]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53b789a8f0aeb7446f6a9eb27d8409f1dd3be1708387d6fb2a1b10a316cb94ea(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    instruction: builtins.str,
    model_uuid: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    region: builtins.str,
    agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_key_uuid: typing.Optional[builtins.str] = None,
    api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    child_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentChildAgents, typing.Dict[builtins.str, typing.Any]]]]] = None,
    created_at: typing.Optional[builtins.str] = None,
    deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentDeployment, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentFunctions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    if_case: typing.Optional[builtins.str] = None,
    k: typing.Optional[jsii.Number] = None,
    knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    knowledge_base_uuid: typing.Optional[typing.Sequence[builtins.str]] = None,
    max_tokens: typing.Optional[jsii.Number] = None,
    model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentOpenAiApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    open_ai_key_uuid: typing.Optional[builtins.str] = None,
    parent_agents: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgents, typing.Dict[builtins.str, typing.Any]]]]] = None,
    provide_citations: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    retrieval_method: typing.Optional[builtins.str] = None,
    route_created_by: typing.Optional[builtins.str] = None,
    route_name: typing.Optional[builtins.str] = None,
    route_uuid: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    temperature: typing.Optional[jsii.Number] = None,
    template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplate, typing.Dict[builtins.str, typing.Any]]]]] = None,
    top_p: typing.Optional[jsii.Number] = None,
    url: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4534a93bd1883fad37e18129490a8f6a482ec69784870cc66c2db63115446bd0(
    *,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    visibility: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ccf37bf2e374148d5ff17f5b90be9e7b2958eaefb5395b0a77b285ddb9381f6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa5daa144ec32688b63376d3c4e24bdb74524fdb0cd06ad6510a560711a7fa53(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a51690f4d4c74c55c257bd3e84206e9bcc643a65cd6b9f9e939d4cff1328265(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b2b03af9c50ef3493f202ff7e4d0b21e2bc54ad187b9dff9cc6ef3302bfa5a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4701bfead870635c21ede6e6eeeb823745230c26c447881bddd08950db08531b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6772cf8418ddf7ebc764376ded46e0ba2ee500f2d632467884e04fb1a38c1b5a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentDeployment]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f19778e44b1ecc1ff14982484cf2b029ca017e5da9e0a7bc5130e8a6ba991f58(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfaf6dee0dcf8dc63c51600d72791daab3e109321afa58ec989a98536027d937(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5951fa0acdba6659c9a0315e1e6debed83aaedb9823082f3f9d29681e0586e4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30d13aec77f1e4e2ce93b3f5f434987b39ee3b823db3badf23ff932d87d76f82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__302555f5d94b41d595cf80efd7f7dfec960bf5effd1e4b22eb9bb0cb4c1167ab(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3c19995c48b7fba58cf03f3b7c9c8428fa695eef5808dd9e3abb1c568b08dae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6638ae5b766ff7ab0ef80c40cc2d5923c7c50428b513690083fe28c9d697c2a0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentDeployment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dbfcfd2a2996c9eada4a7d788821cb591d1786e672de2b6a440cefbeb2d3ce3e(
    *,
    api_key: typing.Optional[builtins.str] = None,
    description: typing.Optional[builtins.str] = None,
    faasname: typing.Optional[builtins.str] = None,
    faasnamespace: typing.Optional[builtins.str] = None,
    guardrail_uuid: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd0818d57073a88788115c8781e5151507a0775f84855b8ebf75e863c07e04c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b3d24a461e32235fc804885051a76dd47b217239c7955e403e8988600f017ace(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9f79cd1ad43bb7c88276258cfdc07760ea5bb6ae5c4398880edfc78cf6a44292(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1563663579c3f929a18d3a9ca945169b1c67aa58bc66454cc6bf00c07f27ecea(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18f77ad921b45c43606e2392a1d83f58c0d3a67fb6d8e97ee7a09449af844d2a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__524a02b78aed2308c777f5538ca85866820a7cf8fc18e5e77d125014f2f0e34c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentFunctions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea2bbf35f2a2b22e6d091692999b7a93aea57ed6aa3492a51f05e981ba2c813d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7932744349f3e12b2ece04e13115176c6a9d5d4f197f039fde48a3ef5edb302(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bdba6bb495cae705181e9349cd6aa57d3fae75466c17c976be5461857db6e9e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b25f4392461ace2a2a8a81ff3bbe8d327aee212c1040836014157cf87b984bae(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7ce2a957d8dc69ca9169131050edad4ef2d8092b1047a79f33fcf3aac5af357(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__367f132e9d97a6dcb1164f750d4b993f0d11d6a7ab8e56a7caa2f0fffb780551(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee9e5fb6d77a0b62c672db1efd9c33b1220ecc257f7c85c6bc8b1c6056d10742(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c334b9379436094648935e3b58af73d7ca7630abb5fc16f861ce7da18f65c2f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1b53ed50b5745ee09feb370b261ee8318e7ae9f4c6a9d313e7b22ed0a8473e43(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec933f92dd2310b007039aef534911a870e5751bee779d7a124afb93c259b1d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentFunctions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f104ea7dd1a4b9da28ee10fcf1b2a070c12dc5eca3f061e993e39544ebc0542(
    *,
    database_id: typing.Optional[builtins.str] = None,
    embedding_model_uuid: typing.Optional[builtins.str] = None,
    is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_indexing_job: typing.Optional[typing.Union[GenaiAgentKnowledgeBasesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20ea345c0209a78b82908ab2704935c9b1a71b1dacee2d6c6acc8bb5b2b2fb88(
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

def _typecheckingstub__15870b7353242831376610056d9da8be394ac0606d2dbdcbd8387b3b7493dfdf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d0c705433b2a1cf3f15ab8fdc25ba08ce1c72e5ad41756e328d27bc4d51ee3d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eefc82971f06bc5c8072a911be81d8da4ce45d398163171614f0790924177beb(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53da46ae24f659e9b7334e6017fe5afaae8f44864d31bf28bf3d58b49c7cce8d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f487ab31de406121d7517b0e655db6b4e8d5bc6ee4d49534fb496ac1665ce2f6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c10b42d5af39f46586ce30f0ae68e5825a0b99c339cb848f90e38c58c2a89748(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26117a7044da85243efd3340190d8e0e0713006ae835857ac03c8947537fbcf6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01bf184937a40e1e071c8601e7175b438671d340c41355653e10f73784b95f75(
    value: typing.Optional[GenaiAgentKnowledgeBasesLastIndexingJob],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7e4b07e893eebe8cca5125ce6c02f6db965b201fb21b3d749006669c601b1632(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__49612fb261f22d8469ae826365c67c73edf35c97953dc5dfbb2d2e97778105cf(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca7a3a04c25d35c76cf181fbdb2544277d403d69fbbbf9ac8a718ad3f66c45ef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__efdd847f5d9beadd48e2140f592f678f37b488ebf48c6dcb3cfa9c8e7564c3de(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2abc005a381e21bf92e93e6af344684ba65b4992a4b34348a1513655deadf0b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__100d625fca3ee25a446ad2843b2fbd4f2d400c3c48f01448781f4a2fdb79d72a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentKnowledgeBases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4bed10bf3e42715e094e6d9c7b89608d575eec41bbe58ffbec141b9b52d3c469(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__763828d3e9be167181c171fea63ba8fb6d51fa91b188fa4d20fe232945ffd24c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae8c1e36997011a31b88f51d6883001890f2d12acc5cae1c17b44e715edcbe6a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f56266b576489e8d3d6e7ecb644b5a242a8faf1e646e09901c4e0dfbb7163b4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__352a806a15b205a0f45e54b252ce26064529652be0285e8305c2321871c80c71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c26eaf0270aea3a9b14f1fed92fa614c9de8c18b5269cdcb6209df4b9e7c40e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fcdc929c0998a21b62323487f6fadd44d573c520c17d9a56f967ea8919e99671(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1064f0dd01f8524a86d9de13ead77260995d21bb0a66ea3add54e0c52fe6ae1f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e07eedf07e0d7d55e9f71210dfefe8e21c69551812b4eca9b03fbb882e809f22(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ba868de226c4bb677b96089eae3f515fba8a81cc7aa909235707d43d19b79ba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentKnowledgeBases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6e47edd42853d4de182a42fb135765f8bb629a176512349488e9e158369a5af(
    *,
    agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModelAgreement, typing.Dict[builtins.str, typing.Any]]]]] = None,
    inference_name: typing.Optional[builtins.str] = None,
    inference_version: typing.Optional[builtins.str] = None,
    is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    parent_uuid: typing.Optional[builtins.str] = None,
    provider: typing.Optional[builtins.str] = None,
    upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
    versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModelVersions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1cc462f05e9b14e2706e2e085ab409aa67899376da6decb2cc946a363800358d(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7db2478a274205e94bcb28a52822afb0eb6c27f507d1fd4ac1c068b885cc89e3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2f867a94f45a00a8c59222181b17d49c8ab85f4f3bb82ea80ed97352d3796c7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a32f690ab03e8f8033dcfde7f92214e2c26c57e08fccf42091c9684f069aaa8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5ae04bcb60858976a33632721dc4ef133b2f3f1599916b97975627c9efabcea(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__65bef8fac330ef4c5400bd02261a1d1f045ff0edbbc8c3981459f019861bddd3(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12b517c3d5f01accac95ff5a4b4733b2c1de9c012ff22b4176eb941de2a088d7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelAgreement]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7cac094c6359347af3dfc765cad6dbfb3d973b8c381d27c4c2635025bd41bed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ab1e9f8a4863062749cabfcdd605aa974e8a3febe2efa0ec97f00b97784ca2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9cc67b628e3bfa640fbda456f7f454bfac4f6beb7012e1874cc9834440ae1c0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d89be89f7e6d328675d35ec2e876995e1f904eac69bfa5b510695657c4b3f0b3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ea2218ab95df7e5512c9f7663f6e4a4fae50af8416ccfea69316d3664501fc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ef4dacbc004a584194ca14a4b37b466357cc830758a55bb621681a81bfdd769(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelAgreement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cce42ac4ee35fe1f59159e4714b81385879a149936f71face5b4a4f6c3580987(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d705e1aad0dacb2175f43b2ad65908645368e211053e7624260efceb2327da42(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__09131d242c7b59dab22e0ef3dedcb9afb2dea6da9f01d2ac87af5709da6f4cce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf2616fc2c1a8bcddf0b7aa07c4b670836aa25547898c292feb594acbcc09b1a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1bf65b12942c09cecd4c27d661d1fcdd3f890347e6116ff379f8f7c70d1aa7ed(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__224dc52745e874700e6ce2d1c931c84abdf98f7166c69e11e815c06ba25cad5b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModel]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca2b61d384c5504eba5ff96d09bf069e6fc3fb691376dda92e9b0146bad158b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25ef58bf3d615b50371336ffb971954ee30bd2ebee6eb269d6cbc05de0e59cd2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e2d6b64722f95f0cebf65434ec7e2debf1c63ba4cf48c5e471cadb8e48d0d97(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentModelVersions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae8292ed235e59d88fae98cb0fa84aafbe7e64ce67532a51bb3a0d1dc109d5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e4d7b5f7193a40ca1e574f55f3753b3021b6d50a5c78ff84864b3bffb6317ea8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1890a2b29e586c458115c750f4f949e12273165fe0d64b2fb70485b9a86473f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2d204088719a22ec3c291eb7350f440f8dda1da549d419fcaeef7dc1b602ff6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3b39ff07d51c04af916eda781c79f409fb6fab2116c2aec7b03a229ecc673db(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2f19891a0a800a4cdd69e0f62c45acc9e10965d716a750d11b5edeb46967203(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38703376ecdcaf3a328504a6ef360ea796e765f3b32ed2f24b6d9cc0c4d10749(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6c9016e9949d788b8e235c0ea53f11cf200a7c402a95b8f9d76b395f4f7e155(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5dbcfc65584dd3e4ee5c7600deda3ed71b164a1297718e9b8bf673cd03ac1e63(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__def57ccac82925119db92e4abb0ca319089745494bad4b5523241d840fa0d1da(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModel]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b6abbf842cd0deb97daf8c409e498e7ba0a42826e05c8b58c8c6108483522827(
    *,
    major: typing.Optional[jsii.Number] = None,
    minor: typing.Optional[jsii.Number] = None,
    patch: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da6bf6b63608dc002e6eda34611592a697bf4c8aae6481edb523cbcd024abaac(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1eb3b6bfc26bf84eeae8f349843083a9aab64e0d29a587a55b3b7ffa7a401abc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb97504308b89f4001a24472a2c775f897ee2cb2826ddc74d3f4a3d5bc41dd9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e9473fc3dac6fa81bc0fd22a682a966ba3cfbda216e1f8a65ae59740d52ffd3b(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3599e4d80de18fca8ff117bca0f7d16a5ebda1e2b424eb3c7bf3e9870488cc92(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfebeba4d8804cb038d3c84478335000176c1f019f943323c8b2aa8b0e832ba4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentModelVersions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6c2a7b8e420c0de20dd20dabec7e9978899a6f4493307f3b0ad68f22b9370c6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56c82ff64e22b3828cd1c3f6c0dc84c4c7beadf32db04b4b303f337183cac290(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__192c71c15e7ffffb8ed131666841ecd2e3963a11d638a57d38f92e4c38280c2f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2b797191372e70a61370682da0a466cc70120ff3bcff1558fb1e26726a745e8(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d60fdf0f8637d66d76ba30d0a496332561cb29ec03fd9c9599d5514600315bd(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentModelVersions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b17037d79416a5bb12451e8d0daa5369731dafa244d5d6cc34601ddb802503(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__beb8816a3fb792b2505959ed1b77c99fafbd1e6d1c93c42c8acbc97db6c954b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be3c704fd2ff495777f77942724f8db372aa33672370c98af9c7ccee67086d5(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d12e6d56bbfa288399bab3b12482f71d21f44eb39cd6532528f8741b12de0806(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16bb0fc3804f347ad75f62ed5cc2b351ccea1bebead99a94a85a15f8e447b2bc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__638d1f61e26a8b199abd090796707e797b1e8bdb86ac7cbc663b02cc20362172(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__993d212c156cf5c432cd8c77583556c89c1850c52368cffbd8b6e8357a245e22(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentOpenAiApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d371df9bfb43840cc762d1c8681ace6a7b0074b3bbf077dc911ef2e8cd5ce8ab(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__666bb1198b0ca0353fa822dd006a2f390b526dc067e1bfa423328b47f27d15cd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a65050229e763f80d1a73d991bf97740f9229ff9f89b14bd45014705b240bff(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96d85b65729b176b92f990a7f6b9a06564f743999aec3ad337818f373ec11a75(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af4538463b204357667f0d7ced9a9f994f0f524a2de2865dfc9d2900cadfa3f2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentOpenAiApiKey]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a4cb1bb1df81627670e832d776aa3cac71c5ce21903508bb02cbd2e735f4e7a(
    *,
    instruction: builtins.str,
    model_uuid: builtins.str,
    name: builtins.str,
    project_id: builtins.str,
    region: builtins.str,
    anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsDeployment, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da7d206c4078d1f816e0926929a709cc630cf005382db8035768be451646d0bf(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c32aecec02e468c468eca75ff644ce4197208e2bdccd1be7db1fc828f8a6ede0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e795046eae5510a7c4751aa0f16c25df4d5e063c9cff40dcc1c45062efef844(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf7717c97bb9ad1ca50d92d3f55d2f7dc50a73f1997dafdfd6e80681426efa48(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cd54103770f77d95b049fed7a497fce1072c4702901c7cf6f49b7bf85342fb0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__102565eecf84e6717db89af1ccbde6a3f7d631e84af71ac0a2fca9dd99fe09c4(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2a726d14060f596c925b749cc73de5642ba0d62c10e8c8697f934a8696dc3b8(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsAnthropicApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__706e9bddbf60625e72b4934fe5710522605820fc4cf4f74d9dd558e35c39376d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__228b3b2c8d8b69c0a886c89f6137e2d97d36829c6ffa9f8c6a82d9334f82ee3f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e0bdc8795cd08d1016ad6aa36881834713b323be60774cf7e7bf6e59505e7d2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__deebcd8afad83101e977f53a31fb3eea0196ef6742c4db1826b240c18a753600(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96f863017740847c5b8343cbe315a4b8efebba642f6f8b49147088caf0843d1c(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsAnthropicApiKey]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0228f52b306b2c621461b92c945283400ca3946be1609441a3bc304e391bcdb2(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    secret_key: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__873592535e27cad3217c05eab1c60832f08daf83906290ac18b7695a67703687(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fee7aa422a87f135a76a686487340cf026ab245b4993546041088d736363a212(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10d69457aa98d69d02a9804dfdc421ad788d5a69d0811b5360d7593ef3751b5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38e4f6e07d40aea3e93abf3ab9d039e9a031c83fd5e68b3c31eb9c24b42cf5c9(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f557d3bf0833884fb23df262797341828d682a04b5288fd4149d165f38af0b23(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__46e1f282cbedd43f4c142ebd7e94d329f4ab7fdb6f53a3b0209b5b77e3e2e4c7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeyInfos]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__91bc3bcc624da29dc2d9870c324880c7ab944ebd1684ddac57296f1f0e50e272(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__daf45a8eae7c4fe8ae53ea465f505fe148efce11e20e84ef7ebb97ccc89aadef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4378718d00942459f0846dfaf4debe66cb18841ee2bbfbd4df64bc6644ede15(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca733ea68d5026470b923db3b1d8295aa64427ad34bc7e5af85c84d06acd9d6e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fea499ee56b89bf3594cb44e7c3f3798763459f8198eb95035b8592888be77df(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__499bc238ca8f68b31ee54176f005309527f29c98b230ccc08c89e7fcee407cdc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeyInfos]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96d2c0852b7657ef162ce41817485ce8a7c2aa71d975d4addeb1ebf3f07c3006(
    *,
    api_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__96e434aedb0a8826dccbc212c5427b3e3bb27bef902459d51976143fe23003b5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6240ee923a5b6e572ba141fc20b3910d647da6487533d76a6e945f3b9f8568f6(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38affec753090f5a6cf9e8226357d4a67e902c655d4a2166a09cfc8467dc271d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5cc6c13484e26c19454905d05681e8db6fe3e2d66355429c547495a120e68e07(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb55489121fc23cd4777751bf4ceb102e3029d7ab6a3a6ca2c4b34ecc1323b17(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb08b26b0543248837421d64639dd73c9a16fa8c012db417df1c77ba03847b54(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsApiKeys]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1f91eed9cb616394545b40a911ee9266c0a50848bfc2c46a01504b3e005805f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d7b3f8ec68a13e88764c081d58510417ebafa2bd9eafbdc2f1f9197448c53acd(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af375e62476ef531baf469c953d29ac5a74c03776a5d65e14b430f1b92804516(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsApiKeys]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7505e05497ba47c2f29c82e6beb3de9af7bf6cd184e5af42201bf50ff2a00b03(
    *,
    button_background_color: typing.Optional[builtins.str] = None,
    logo: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    primary_color: typing.Optional[builtins.str] = None,
    secondary_color: typing.Optional[builtins.str] = None,
    starting_message: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8ac54d6c08f0c74b705878da023d44da4393465776219785d295cf072176462(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__696e4f3eee9e1c8b90ce1a7b33af3f13c51fd26dff85ec184c40c5ec8fda9890(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0cd93bb6651fc4d77bb0302c4c4f62346c187dda09f44b097a1ea9e4d511d59(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5baad42878aa6b1fed7fdc2742d086515b951150192cfbbbe7fc1e81908ec216(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c74ce4ebe78441cdccc8572ddb0c72b7cf750e2678e66f06f37446d0777788a9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e28feabbc22a0e37cc1ec60fd25621877256b5407ecda8e57d358981f50f00a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbotIdentifiers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5eda7db18673405c5c305709a5ca2b819c410b0fd9ded1ff84bc164639c0eddd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb1dc072b2bf8eaf7a200ec3f3bb4200f8a68fc1e091e14dc3b0fa2d11143962(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbotIdentifiers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__562521664e385ef0a15e7b915cdbeee234da619eef886ecaa7d9e8075c297663(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17da8a4497f8ef6021cd7766b628b7e538f8df3518e14e63394f2c68339cf70f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__958c43440c9a35de155816ac64586c1f44114d79dbd0f0b8497821faa338f47a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b00c4615cfdc2e3522c1450b32072fa5f21a7a07ff0a0d4042b36a64d26b73d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d91ef114953b689f624720947a76435e28bcd4caa81edec61f558881342850e(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d6699d12f1d5382970e4587c24f738491a97c019dea87cfcaad9231d4b32a10(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsChatbot]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e91000e1d0c6e0f43b29e538525ebb0925220d1c534f91749e8cce545210ec78(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c50c9dc508e183702fc3b7b54236e2b5b320e9064dbe54def4afc40abdfe8b83(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__714c176383027cd6e555de74712aa57ed7d7494a48cef77e73fbe0da2ea926a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9bc9754a9c157ff51329ff6cd96c927e5c27c3f92461947858771d3239a09bef(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8166b7958d47fdf3465e054738ae359c29bfd0d31fbbf5635d1d85c4be1e97b4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__edb1a4c858f15b0b865cb06a319bf26562388fc08dd15d9f9ef400c91569948b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0548ed64ebc9fe952877816de2c989eb6f039e3dee885bb1f1eb94f5727abd7c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5db27f4d954f5827e62f50a34b25820ee20ebdb3cd775dc7ea35340784e53827(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsChatbot]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3377902e32c12490ecfb8f207169caa4b8974fd0b1bb23bf10b33446b4e4f99b(
    *,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    visibility: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1aa3db2750d05d3b1a57dcebf5d78c50176206d9f29ac4b277717f9a9ac1e4a7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ede2d37927ceffdaffb86c648e41af1e421d5355c9882ade29b8958b96a3bd38(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a51c740d09dbcff2bc4704ba76b8c2bff0e3be6cf06962940b35ae7897b9c57d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9b1635d7d1c022581b839db4c1890542d22228a76e93cc54a0f1865edb37250(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db2628545d2bf2556e0c65ba7f12465b5b3deb6156a2a6941d117e2f9381d1bd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e990f3ed922e15841f2f17dd69e0975a659308dac4cb474cfede304d70eaea23(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgentsDeployment]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7348822a8644e44d1059940704f799c7023df38ee8931cc26631289099ac1c51(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__16a1a0a908b0c69869b578f84d8a3a7a25422fc14a71fcc689eff639f9f2d072(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fae802b88d443efa27ebae1ca20d24f236e40d3208f61160d6ed16260c3ad930(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e49ca5d7c7b100d74565758cacda6eaa387fcb99703813d4191cebc782986094(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e3ca0c3df18764132db3db6366faf91a1cfb2e1f21d4400db26bea6dcc5a895(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__605177106d0f964c4af52bbbf730e34027a8c909d610b01eaf596ea22337a713(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa422f83223a30098da6a85beb3fbaab0c600d8428416ed0ea89f87c46f3816f(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgentsDeployment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63e30ec309b14ce88a6534fd72889ec13cae0ba4d1acd145e87e099dc62068f9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ce6bd36d9ff82090b4c7e880ea75e7973e0fe89b6002a128b7849e9ac5c8091(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bac695629cf420350ea6535a0df41bff7f4de4859130ac98024d161e98d5b7de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350e16b7d51e91bdadb5f8592e62eb97a1079885c95a100a9041493587743999(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__87bfdff6a019d9afd88254a5ef329841e3573e130d1b8ded4c42ce09bb72fc99(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b426cd159acab4e9b23f9ac8d3cf8a4e6d355b1c6b0715a8d78505c837517cf(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentParentAgents]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b35c653b566d8abc86758a9ac02800f87e34ca6d4af10f5ad72001ecc74b1b37(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28e200a8424688143f528464e7b06f8bcfb1f18219ca981a7db305418978692(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4d38882d287037360f87d4abb6ca4cde7985e86ad601072d53d39cc6fb10659(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fdcade5d979c3d078fca0bc98985821fe3d018a0f687050e3f8f256d5c26eb7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsApiKeys, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2da3b94e570c01194ca4797778e1bef0de2792fb652e36553e09eec94fee62e6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsChatbot, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa667603bf6d9c10c10ee4a17d36ea8c1079f6c028a7346a598a667b7f253ac9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9960210e0162cdb95d7d65cdabfc8eb103f0bdc20aadb84f09ab8deeecdf95d6(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentParentAgentsDeployment, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6220425d0a7787f8f2fd9f44104e1fe4ce76a1a9ba18ccbb14c85276be3adabb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__674258837b2e17e079d977d474ac40d039a62644d6817831528d596885702f05(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e258dd1c99f75b548d75bda994f40ef520be8400d926aa64b645304216fbf6f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b46a392fdeed5d11dd89dd9506c327a380a677da2b7b71eb7e7f8bcf602f72da(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5257bd70bc8e3c6ce7bb23733377b9505df61ef9e922761a994bf73eab3aeb71(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7ece4e553bf30f71b1ab43a5f3886a1918ec671c2d0fba071b7747ea43708d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4acf480f4f31acecb641b1225593ec7825facc5800894e0838baac8cbdf1f36(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentParentAgents]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e2de23e2c8f609ba50d1502866322493e465551c415788b27bc5a995d3756306(
    *,
    description: typing.Optional[builtins.str] = None,
    instruction: typing.Optional[builtins.str] = None,
    k: typing.Optional[jsii.Number] = None,
    knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_tokens: typing.Optional[jsii.Number] = None,
    model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    temperature: typing.Optional[jsii.Number] = None,
    top_p: typing.Optional[jsii.Number] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f93999fc9072de6748f56f7419170b7a2fe7e488decef22ac20ab10c45a46d(
    *,
    database_id: typing.Optional[builtins.str] = None,
    embedding_model_uuid: typing.Optional[builtins.str] = None,
    is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_indexing_job: typing.Optional[typing.Union[GenaiAgentTemplateKnowledgeBasesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f88c53534c6f5ace235d9da6bbd88f9c27ecf4867181d81ba43e3acf5328a515(
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

def _typecheckingstub__d2e2b3f4b07ac081d4cb0268539c7fdd1f6baa3c265e62b399dd9813348d1bf7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa9dc305bb5b5d88f6b4829c77a91995e1c82c7c53304a53d48fb9b3e8ceba2d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75d6652210ce38b837b159e2d580b96475485608c95e6f741da91cb8ed3a6d74(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15948c9f70bb5c06a39b5a4db6b2a84a2298900d29e171add6f987876d3637b5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73cb0d1365f22a71b6b9c3ab333e10c57f1022e7ee8a72fb1b6d6dfed0310a41(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__031876788574d91956e1592978b5821477b4d3116419c2b03c695cf0144933ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5020e38c4275218b985a8beaf67b464f428346cca700970d2287c095da7e2e2b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45fd45f19894821e6bf1b41fbb141523e998803aef10f9faa8f4aef55105e900(
    value: typing.Optional[GenaiAgentTemplateKnowledgeBasesLastIndexingJob],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5efc14f3aa9e193b79e0663a9731dd0322087eaa7c35e489373c9f88ede9bcc0(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f4c65f5649aa11cf74e5bb8115a94b793a176355dfa5d2d12a36b7582c839ea(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e33323219da2e771de75556efd2d5a89ea88d2bb9cc7d6ff642ab20f645024f7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eb350fdeb52ea8d940362009a040a218bff3c2e3f7c4d6308e0a89b24eb57be1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fde936b05e03d6db7ffe6712ceac6321c2bb91d46b4d23ad9bdbb813d5e641b0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a49a4ef05c59e3cb34d42ca844bc7d95ddf54062dbb542ec0a2ff08548e0b551(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateKnowledgeBases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c65dad30fd1390ee8e4c0a20d312708e5a6feb37fe74413a26e262e4cc61521e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ac8651d567250ab5a9bcef3ed833fed0334015e3d533db236c134b1d2885f14b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c49fe0e6eee567db3f1b8c4058f3289a538d59c80d0cfd20c998c6ea61a54040(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76b3fc076fbb054cfd5f23d89fb729cff8c07b1a05c0e0559b4e3b7a9e137cd0(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4707dcc7ee3fffbd1c850e36cadd4a4d3ae22f6b719ccdc57f1053ec327dce72(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97b1d58888b980b34104f4d5fd72704838e6433491adc64636475d6d41f47a0a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__37394db5be1308c77f0c53565ededf7e65d9687511d3817beaa5ff285428e9ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92952c0dfa9885cd65f0dcabfb30328db507acc59f15e2fd41780b699d3fdda8(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3b75985056e1a5f44a7d8257a5430c7ec07388d820639c98f5c0f7e79a362a8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__462b435a3ab307608f118b57d44837d35401c64a694f8b2ac4f377d92b1970f1(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateKnowledgeBases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9091daef6d41400f8071b94d4e2e004e8d9511771ef7f8433e88ac2baeccafc7(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13b0ea0bd2a01cdd1cb66c83717b2db60f728076c33abe53c57ca934f9522048(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bee8ba3e2e8017a88122a1b269ab2bc546b2537af74b9c9d33cafd4efe39dc8f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6d2b2afe0bebb637d9b41b9069b12e00b24225539e7aff79a65befed4006e16c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bb3d4621b75e7cad63fd431d1ea9def11c005450b8805fd5c300e0883c266a39(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c7d059024c4735ecbae9db886bef5a6e7fb065b93bc818cbde0d57434b7b1253(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplate]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d43f4c13789a41db8f25a4c6623430fb7c907f84e5fb66b5ab1e8e4d1934c7c(
    *,
    agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModelAgreement, typing.Dict[builtins.str, typing.Any]]]]] = None,
    inference_name: typing.Optional[builtins.str] = None,
    inference_version: typing.Optional[builtins.str] = None,
    is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    parent_uuid: typing.Optional[builtins.str] = None,
    provider: typing.Optional[builtins.str] = None,
    upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
    versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModelVersions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2043af57abebc4ae573e76bbf6432067914c0fe373bbdfb814dfcc36c78a72ec(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63081977d05ea88a008672b904ec80eebabfab3f022f86500256f0916766958e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06e9c43703a453754a2f2769ea9eb1aeb7d545ed44a378a3c5ca6046f1437ba1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c5ab5bb8a586e6d7a093f10dbc097832992a7e2485a0f99db69725daa180b56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__acf5dc8666b80d93dc7e7d5f17d91184797a03d6bc238de3f693f654fd220c11(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae0dd261b3f0638eb3f4f61a930328912dd6d89701bae851f0a2c4ab2218b8bd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__60f4388d4850a48c87ef8f0086951a35ad67342a6f935a734896a7c946e1b5e7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelAgreement]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6fce60935f3b461298bae7d2e44bac910a3060b63a9907386ce44a31f3b11c1e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e2d915d98d6e76219e3f4464ab0e6ce0bc44c1a8a071540a19be2691c25a8dc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d08bae95bf3a9f5635a5fe40f06b39689775d2ba6c719278803f1dcf7e555024(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51ce5f3d5b3cda5a08b2d300607d10af577e002455d949f1649bff54c6f9ecd3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88cfec1867140394cc44039cb3d637abc2271f883d7bbd6b43a8d14f6a0e0ea4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a35e74d38f92590144058111d9007bfd24d1d46c3c10fdf66a963086eef7e666(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelAgreement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__410305e0301f6f48ea8b8e1bedfe977f89da45df36889940cbb7ba8af6e42028(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb80cdc74964fae0d2a3a6e39de421bf5a20f3541c0c139a70cb1ae0bc565cc(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e0a54284d6c536440607cc76132b54aaf5346e0d8c6c9ac25f031f7a2091f88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f8e7fc175a31fc042c2cfd4fe08b906b9cbeddf9efa0627ced7eb7e45c861505(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6b880252e515027efc6ae25199db2f8ef78a0e6aa9d3763950145d147ce18f1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__921185faae11d535e344cccd22192684ab724bce7412b6373f5ea661d5f3530b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModel]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167ce27a002fee3ac9c80098534b14c827893686f902684c563555b19d0e15a3(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20c79269de84885d72662f20beeb8ed2197ced6cf603f339c2886b9fa49c58d9(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3e5ecf7aaa3bbdc1a6a6b545d8dadc9ddfc23263946e44b31833a0ce11726e97(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModelVersions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6e1328057bce3f72771548a40fcab8cf852b615a68b16387002cbedf23ed659a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d706b30a489a7ace18b383a09de6b5101996e613d94f36dbc1d838fe566bd7c3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9f708c4daaa68b0469eb150a87b57dd5ab47d2d9d7bb114f28d06e5960c8d7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__394a22b4ad9a89c753f84e01ef5997980aaa3375ac747de66aa0b0ac5fba2c88(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__575ca64554af927c0344296431d099ac4511760b69039efe79056b4ec5742083(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1381d1b5bdf30efd6359bcbccd5c162d25ff29c1007b64d17e77ac2ebef39847(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77be8241849ae894b7cc1ab178ba2dca5c0e73b9b9d576548bb6479797c1bee8(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ea57d5496f2b629581b61735a90b69f144d1491565a9a4fa95f509d3f793485c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cc343c2046c23aeb06fcc6ecf67d9b775bbb2e0b19ebf5ea3c2f6f4ea9ac892a(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__649ebe59d7dbc1e843efb970036d57c3b519f86c4864069007ce4345aab82efa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModel]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ea162ec38f272aae133bd22200eff1c090d39bcc206ec6b350edbe8743763ae(
    *,
    major: typing.Optional[jsii.Number] = None,
    minor: typing.Optional[jsii.Number] = None,
    patch: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1894a51500ac8da38a07b2224fb6d17001e61da902a08700effae98f32c223bf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f9152a3ee97a269204c141fc11c16c1a564a2afdb4f92820aa728d5c478a737e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66f16bdb496c4ed016c37635f01e98f38995272eff86c1b60c078eb1a08fd249(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dce064bb2ca67922cd2122a825764a14e9b3c08072aa6295c48640ddeea503fd(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a830c218b6208b4fcfee7903fb9df462455612b2746e84dcb35fa5088bdc4801(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f165bec7df9ba90805f383736eb9151586452118ad84be535850b196d9bd4f34(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[GenaiAgentTemplateModelVersions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c47a1e7fd1e1f6165e9a33962e0e3f67b6fae4a9c1d6e050e4f0f4e3800da98(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a18cb78c6ea7abc06b08f7b7da42eafdffadddceafc8b5298403b87d89c44dfe(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e082722e681cdc927b845000cd0cccfd18a2489938ce3761f63c9b284a218d77(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40c25888d1ff1d6673163243f7a02af9f7adcac932383604927e17f54aa8a232(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3947145a408fcd052d33fac0595af121730a498846cafdc27eceebb74a751fb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplateModelVersions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9b9c2dec03c83822452696b7fcbd8ca8dbb899cdee546f5abb75ded638689127(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbd7d60c1ade6cb58a99cb283cd38108c4d43df794db2e86d58d6c358e898066(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02691845375443bf4a19fe1de384030cf9f68201841c98ed0059cda3fdd8114a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[GenaiAgentTemplateModel, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb46def812359337a27e9e806ab21cb7bb21714c26378661c65bc6b9d926ed5b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04434eca95169dcc0ecd5d079b8d99984a7312e3745b4566648c7c90c0c29d5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20adae04337994db7df9b0997a624cde1b6a3451e1c59935aacf7411434fc710(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3769b0ea5875e1195228e3daaad5fda93bd227331680a6e7d924e95dc9770bf4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8bcb972db6f83865fa87d8cebc60172f1dcce9bde3e096416925ea7b3e44bd12(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a9e08455a8d7693ccb64a01abdf76091de5e0ca8b2b275c68d4b4ac79a44eb6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23fced514a94feb605b8ba48330164d64766119c661020afaaae42d058a42b8d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d430c77aede2f60cc8793f70a74484992b654af8300ee7c177b950bfd161810a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__04732ca6c5cf19846f22af8a411b2a34ccaeeb33373fea73a8972637acbfa101(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, GenaiAgentTemplate]],
) -> None:
    """Type checking stubs"""
    pass
