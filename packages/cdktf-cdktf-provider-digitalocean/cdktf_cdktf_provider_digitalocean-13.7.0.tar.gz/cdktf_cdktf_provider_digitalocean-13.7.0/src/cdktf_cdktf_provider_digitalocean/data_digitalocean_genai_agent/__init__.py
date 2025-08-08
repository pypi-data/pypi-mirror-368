r'''
# `data_digitalocean_genai_agent`

Refer to the Terraform Registry for docs: [`data_digitalocean_genai_agent`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent).
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


class DataDigitaloceanGenaiAgent(
    _cdktf_9a9027ec.TerraformDataSource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgent",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent digitalocean_genai_agent}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        agent_id: builtins.str,
        agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentAgentGuardrail", typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentAnthropicApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentApiKeyInfos", typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentApiKeys", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentChatbot", typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentChatbotIdentifiers", typing.Dict[builtins.str, typing.Any]]]]] = None,
        deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentDeployment", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentFunctions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        if_case: typing.Optional[builtins.str] = None,
        k: typing.Optional[jsii.Number] = None,
        knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_tokens: typing.Optional[jsii.Number] = None,
        model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentOpenAiApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        retrieval_method: typing.Optional[builtins.str] = None,
        route_created_by: typing.Optional[builtins.str] = None,
        route_name: typing.Optional[builtins.str] = None,
        route_uuid: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        temperature: typing.Optional[jsii.Number] = None,
        template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplate", typing.Dict[builtins.str, typing.Any]]]]] = None,
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
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent digitalocean_genai_agent} Data Source.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param agent_id: ID of the Agent to retrieve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_id DataDigitaloceanGenaiAgent#agent_id}
        :param agent_guardrail: agent_guardrail block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_guardrail DataDigitaloceanGenaiAgent#agent_guardrail}
        :param anthropic_api_key: anthropic_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#anthropic_api_key DataDigitaloceanGenaiAgent#anthropic_api_key}
        :param api_key_infos: api_key_infos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key_infos DataDigitaloceanGenaiAgent#api_key_infos}
        :param api_keys: api_keys block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_keys DataDigitaloceanGenaiAgent#api_keys}
        :param chatbot: chatbot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot DataDigitaloceanGenaiAgent#chatbot}
        :param chatbot_identifiers: chatbot_identifiers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot_identifiers DataDigitaloceanGenaiAgent#chatbot_identifiers}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#deployment DataDigitaloceanGenaiAgent#deployment}
        :param description: Description for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param functions: functions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#functions DataDigitaloceanGenaiAgent#functions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#id DataDigitaloceanGenaiAgent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param if_case: If case condition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#if_case DataDigitaloceanGenaiAgent#if_case}
        :param k: K value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#k DataDigitaloceanGenaiAgent#k}
        :param knowledge_bases: knowledge_bases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#knowledge_bases DataDigitaloceanGenaiAgent#knowledge_bases}
        :param max_tokens: Maximum tokens allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#max_tokens DataDigitaloceanGenaiAgent#max_tokens}
        :param model: model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#model DataDigitaloceanGenaiAgent#model}
        :param open_ai_api_key: open_ai_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#open_ai_api_key DataDigitaloceanGenaiAgent#open_ai_api_key}
        :param retrieval_method: Retrieval method used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#retrieval_method DataDigitaloceanGenaiAgent#retrieval_method}
        :param route_created_by: User who created the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_created_by DataDigitaloceanGenaiAgent#route_created_by}
        :param route_name: Route name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_name DataDigitaloceanGenaiAgent#route_name}
        :param route_uuid: Route UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_uuid DataDigitaloceanGenaiAgent#route_uuid}
        :param tags: List of Tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        :param temperature: Agent temperature setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#temperature DataDigitaloceanGenaiAgent#temperature}
        :param template: template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#template DataDigitaloceanGenaiAgent#template}
        :param top_p: Top P sampling parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#top_p DataDigitaloceanGenaiAgent#top_p}
        :param url: URL for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param user_id: User ID linked with the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55a53b6a78cf146a503d1f19eeacdb1d3829fa2fafbef56283577fa93da8975c)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DataDigitaloceanGenaiAgentConfig(
            agent_id=agent_id,
            agent_guardrail=agent_guardrail,
            anthropic_api_key=anthropic_api_key,
            api_key_infos=api_key_infos,
            api_keys=api_keys,
            chatbot=chatbot,
            chatbot_identifiers=chatbot_identifiers,
            deployment=deployment,
            description=description,
            functions=functions,
            id=id,
            if_case=if_case,
            k=k,
            knowledge_bases=knowledge_bases,
            max_tokens=max_tokens,
            model=model,
            open_ai_api_key=open_ai_api_key,
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
        '''Generates CDKTF code for importing a DataDigitaloceanGenaiAgent resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DataDigitaloceanGenaiAgent to import.
        :param import_from_id: The id of the existing DataDigitaloceanGenaiAgent that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DataDigitaloceanGenaiAgent to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d0ea88a78b21f3689f9c2d6dc92be5df8c3d1d47ebb2490a6dc8c0fc147c3ea)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putAgentGuardrail")
    def put_agent_guardrail(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentAgentGuardrail", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__83ebe970b72f3f3507ffd7bf46c3baea1d28babf1a59ad1fc173ec899caa1e6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAgentGuardrail", [value]))

    @jsii.member(jsii_name="putAnthropicApiKey")
    def put_anthropic_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentAnthropicApiKey", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e79a33d4b6b880a00f4d6916aea21270073298be868e7d52c688a2711cb78064)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAnthropicApiKey", [value]))

    @jsii.member(jsii_name="putApiKeyInfos")
    def put_api_key_infos(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentApiKeyInfos", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__05fb131661efa2909f749221537be395c716aa3cec768599c701983be533dc31)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeyInfos", [value]))

    @jsii.member(jsii_name="putApiKeys")
    def put_api_keys(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentApiKeys", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0223298a6d9b679d34db380be80aea15e1e59388b8fcf40ffe8c93454192d72a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putApiKeys", [value]))

    @jsii.member(jsii_name="putChatbot")
    def put_chatbot(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentChatbot", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d83d40b5c2219bc36fd5f0dbb99bf3f3e91c0fdde1032990c6a77056857fa3fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbot", [value]))

    @jsii.member(jsii_name="putChatbotIdentifiers")
    def put_chatbot_identifiers(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentChatbotIdentifiers", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c5405a40453f1f0c806eca5afc875fe44bde16621e977f3ded8843b891854732)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putChatbotIdentifiers", [value]))

    @jsii.member(jsii_name="putDeployment")
    def put_deployment(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentDeployment", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8a32ee71b08dedf3f4bbb780220d1ca9db3db0cc596d8c99ea0dcc254fd8e9e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDeployment", [value]))

    @jsii.member(jsii_name="putFunctions")
    def put_functions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentFunctions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26ffccf1d181d1bb6631a6053efc568eb95b35e9ccd7612d83bce9c678db8ab7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putFunctions", [value]))

    @jsii.member(jsii_name="putKnowledgeBases")
    def put_knowledge_bases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0642f7b338f25553492f65e75ee8a0ca4c1a931e555961d17213e700188b2527)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKnowledgeBases", [value]))

    @jsii.member(jsii_name="putModel")
    def put_model(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentModel", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab3bcada87c193b273a20cc6cf63002e45790e78b16eb381a594c2599059d889)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putModel", [value]))

    @jsii.member(jsii_name="putOpenAiApiKey")
    def put_open_ai_api_key(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentOpenAiApiKey", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5ea59a705a4575409367998196a1fb967cc56584d1ddefb978319f8b7a9ae5d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putOpenAiApiKey", [value]))

    @jsii.member(jsii_name="putTemplate")
    def put_template(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplate", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__86c229ef9e907b3f91f0fb85265294c9029c545e718032cb2edb873ed956bea2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putTemplate", [value]))

    @jsii.member(jsii_name="resetAgentGuardrail")
    def reset_agent_guardrail(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAgentGuardrail", []))

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

    @jsii.member(jsii_name="resetMaxTokens")
    def reset_max_tokens(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxTokens", []))

    @jsii.member(jsii_name="resetModel")
    def reset_model(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetModel", []))

    @jsii.member(jsii_name="resetOpenAiApiKey")
    def reset_open_ai_api_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetOpenAiApiKey", []))

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
    def agent_guardrail(self) -> "DataDigitaloceanGenaiAgentAgentGuardrailList":
        return typing.cast("DataDigitaloceanGenaiAgentAgentGuardrailList", jsii.get(self, "agentGuardrail"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(self) -> "DataDigitaloceanGenaiAgentAnthropicApiKeyList":
        return typing.cast("DataDigitaloceanGenaiAgentAnthropicApiKeyList", jsii.get(self, "anthropicApiKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfos")
    def api_key_infos(self) -> "DataDigitaloceanGenaiAgentApiKeyInfosList":
        return typing.cast("DataDigitaloceanGenaiAgentApiKeyInfosList", jsii.get(self, "apiKeyInfos"))

    @builtins.property
    @jsii.member(jsii_name="apiKeys")
    def api_keys(self) -> "DataDigitaloceanGenaiAgentApiKeysList":
        return typing.cast("DataDigitaloceanGenaiAgentApiKeysList", jsii.get(self, "apiKeys"))

    @builtins.property
    @jsii.member(jsii_name="chatbot")
    def chatbot(self) -> "DataDigitaloceanGenaiAgentChatbotList":
        return typing.cast("DataDigitaloceanGenaiAgentChatbotList", jsii.get(self, "chatbot"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiers")
    def chatbot_identifiers(self) -> "DataDigitaloceanGenaiAgentChatbotIdentifiersList":
        return typing.cast("DataDigitaloceanGenaiAgentChatbotIdentifiersList", jsii.get(self, "chatbotIdentifiers"))

    @builtins.property
    @jsii.member(jsii_name="childAgents")
    def child_agents(self) -> "DataDigitaloceanGenaiAgentChildAgentsList":
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsList", jsii.get(self, "childAgents"))

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> "DataDigitaloceanGenaiAgentDeploymentList":
        return typing.cast("DataDigitaloceanGenaiAgentDeploymentList", jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="functions")
    def functions(self) -> "DataDigitaloceanGenaiAgentFunctionsList":
        return typing.cast("DataDigitaloceanGenaiAgentFunctionsList", jsii.get(self, "functions"))

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBases")
    def knowledge_bases(self) -> "DataDigitaloceanGenaiAgentKnowledgeBasesList":
        return typing.cast("DataDigitaloceanGenaiAgentKnowledgeBasesList", jsii.get(self, "knowledgeBases"))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> "DataDigitaloceanGenaiAgentModelList":
        return typing.cast("DataDigitaloceanGenaiAgentModelList", jsii.get(self, "model"))

    @builtins.property
    @jsii.member(jsii_name="modelUuid")
    def model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelUuid"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="openAiApiKey")
    def open_ai_api_key(self) -> "DataDigitaloceanGenaiAgentOpenAiApiKeyList":
        return typing.cast("DataDigitaloceanGenaiAgentOpenAiApiKeyList", jsii.get(self, "openAiApiKey"))

    @builtins.property
    @jsii.member(jsii_name="parentAgents")
    def parent_agents(self) -> "DataDigitaloceanGenaiAgentParentAgentsList":
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsList", jsii.get(self, "parentAgents"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="routeCreatedAt")
    def route_created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeCreatedAt"))

    @builtins.property
    @jsii.member(jsii_name="template")
    def template(self) -> "DataDigitaloceanGenaiAgentTemplateList":
        return typing.cast("DataDigitaloceanGenaiAgentTemplateList", jsii.get(self, "template"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="agentGuardrailInput")
    def agent_guardrail_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentAgentGuardrail"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentAgentGuardrail"]]], jsii.get(self, "agentGuardrailInput"))

    @builtins.property
    @jsii.member(jsii_name="agentIdInput")
    def agent_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "agentIdInput"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKeyInput")
    def anthropic_api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentAnthropicApiKey"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentAnthropicApiKey"]]], jsii.get(self, "anthropicApiKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfosInput")
    def api_key_infos_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentApiKeyInfos"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentApiKeyInfos"]]], jsii.get(self, "apiKeyInfosInput"))

    @builtins.property
    @jsii.member(jsii_name="apiKeysInput")
    def api_keys_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentApiKeys"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentApiKeys"]]], jsii.get(self, "apiKeysInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiersInput")
    def chatbot_identifiers_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentChatbotIdentifiers"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentChatbotIdentifiers"]]], jsii.get(self, "chatbotIdentifiersInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotInput")
    def chatbot_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentChatbot"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentChatbot"]]], jsii.get(self, "chatbotInput"))

    @builtins.property
    @jsii.member(jsii_name="deploymentInput")
    def deployment_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentDeployment"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentDeployment"]]], jsii.get(self, "deploymentInput"))

    @builtins.property
    @jsii.member(jsii_name="descriptionInput")
    def description_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "descriptionInput"))

    @builtins.property
    @jsii.member(jsii_name="functionsInput")
    def functions_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentFunctions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentFunctions"]]], jsii.get(self, "functionsInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="ifCaseInput")
    def if_case_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "ifCaseInput"))

    @builtins.property
    @jsii.member(jsii_name="kInput")
    def k_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "kInput"))

    @builtins.property
    @jsii.member(jsii_name="knowledgeBasesInput")
    def knowledge_bases_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentKnowledgeBases"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentKnowledgeBases"]]], jsii.get(self, "knowledgeBasesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTokensInput")
    def max_tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTokensInput"))

    @builtins.property
    @jsii.member(jsii_name="modelInput")
    def model_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModel"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModel"]]], jsii.get(self, "modelInput"))

    @builtins.property
    @jsii.member(jsii_name="openAiApiKeyInput")
    def open_ai_api_key_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentOpenAiApiKey"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentOpenAiApiKey"]]], jsii.get(self, "openAiApiKeyInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplate"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplate"]]], jsii.get(self, "templateInput"))

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
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentId"))

    @agent_id.setter
    def agent_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ff6b7dd50277f86b47fd2fd9c2adaacba0110df7228a3e3b74ae5be100a0598d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f97d41549aced3c3893a7b8e162e707f5b71df7f82c86129230c24c30ed5f048)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__63c949afb24261cc7d6d50b7aba0fb0b69c01acb84194db76067bc2871bfa551)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ifCase")
    def if_case(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "ifCase"))

    @if_case.setter
    def if_case(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f1acf113bd572bfc94ce0879c41e78f265964b6607f655934431df7741e28423)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ifCase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="k")
    def k(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "k"))

    @k.setter
    def k(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__018d5534e38a17e97649d086a0d1b3c1cb7b3e446d60d9ef67dffe2838cf7a27)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTokens")
    def max_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTokens"))

    @max_tokens.setter
    def max_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e5479d15015d0f0789650daeee3bb882def748b90e1ff84050d953b3f7fc0db)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="retrievalMethod")
    def retrieval_method(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "retrievalMethod"))

    @retrieval_method.setter
    def retrieval_method(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__869d1d4671d116f16ac0840c0f58be0edb1a043befaf7bcf875f8303becb15f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "retrievalMethod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeCreatedBy")
    def route_created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeCreatedBy"))

    @route_created_by.setter
    def route_created_by(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfe8aa441cbe5b41474573c690b6a2ceacdfe1d41d90a0c796aeeac603c11692)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeCreatedBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeName")
    def route_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeName"))

    @route_name.setter
    def route_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__652917699e2f5b3b0b249f8e0ff49ce62a0574d6ba69098490b1d6934597ce5f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="routeUuid")
    def route_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "routeUuid"))

    @route_uuid.setter
    def route_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a02cd1f4846b330dd0975b6e6912d7e9be13da88915c2c4428d4a20263be56f8)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "routeUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee275474486d9f205f335c8b245c93c9a86dadd10b25a140eca5e2f4ad14c52f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="temperature")
    def temperature(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "temperature"))

    @temperature.setter
    def temperature(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bdb5af2fc0f4080b32f9e68becbac63e64f5cd3239c36972a73a9c0e69b6dbd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "temperature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topP")
    def top_p(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topP"))

    @top_p.setter
    def top_p(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__40570ba5c536e8d647b6e6f74f55c709ad808c5c42aff78f47f19232694d1f55)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topP", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2d95f67e3a6c970c914525fd2a5abf563701cae72c5ad92d85c2016e56d4747e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bef3e214677f39675f8631610863824c9cd41ea85807228b2edba9713a024d8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentAgentGuardrail",
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
class DataDigitaloceanGenaiAgentAgentGuardrail:
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
        :param agent_uuid: Agent UUID for the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_uuid DataDigitaloceanGenaiAgent#agent_uuid}
        :param default_response: Default response for the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#default_response DataDigitaloceanGenaiAgent#default_response}
        :param description: Description of the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param guardrail_uuid: Guardrail UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#guardrail_uuid DataDigitaloceanGenaiAgent#guardrail_uuid}
        :param is_default: Indicates if the Guardrail is default. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_default DataDigitaloceanGenaiAgent#is_default}
        :param name: Name of Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param priority: Priority of the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#priority DataDigitaloceanGenaiAgent#priority}
        :param type: Type of the Guardrail. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#type DataDigitaloceanGenaiAgent#type}
        :param uuid: Guardrail UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4148f22b82dc0c264e0e38e77896c1a463570d0ef5ac43ebba13e6577f31bd84)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_uuid DataDigitaloceanGenaiAgent#agent_uuid}
        '''
        result = self._values.get("agent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def default_response(self) -> typing.Optional[builtins.str]:
        '''Default response for the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#default_response DataDigitaloceanGenaiAgent#default_response}
        '''
        result = self._values.get("default_response")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guardrail_uuid(self) -> typing.Optional[builtins.str]:
        '''Guardrail UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#guardrail_uuid DataDigitaloceanGenaiAgent#guardrail_uuid}
        '''
        result = self._values.get("guardrail_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_default(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Guardrail is default.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_default DataDigitaloceanGenaiAgent#is_default}
        '''
        result = self._values.get("is_default")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def priority(self) -> typing.Optional[jsii.Number]:
        '''Priority of the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#priority DataDigitaloceanGenaiAgent#priority}
        '''
        result = self._values.get("priority")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def type(self) -> typing.Optional[builtins.str]:
        '''Type of the Guardrail.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#type DataDigitaloceanGenaiAgent#type}
        '''
        result = self._values.get("type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''Guardrail UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentAgentGuardrail(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentAgentGuardrailList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentAgentGuardrailList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__aa7263551e1aeb2f478bac6741389c2caba2fff9ce811afc4408dc13b4ea4531)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentAgentGuardrailOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e448793233dd0ef3e84e9692fb955ae6516e0b9d023582c498ba1851bf4bc793)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentAgentGuardrailOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fb59843b8f891d1b7def5da857c25594f09babfc2c4790c8230ee236fa10a882)
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
            type_hints = typing.get_type_hints(_typecheckingstub__58489b7a027b431b61bb48c0b6205a40901e94467726a2d0c096bea5961861e4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__aef5eb324a58ee4b3e25d26871ec3edc1b8afc9e80136bb34bd7f241b03e0b9b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAgentGuardrail]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAgentGuardrail]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAgentGuardrail]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e08bcc1be3f5d44283a4abb47aa5ec125162c414e5dd26444e6892443faa251)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentAgentGuardrailOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentAgentGuardrailOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__78db844d77fecc4bed90929c162d4475fd0198df8e2cdfbce6278fe03a3d9d82)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0129369d281022db08e214df971b5bf6a60718f44f79697e3e64e9455c870fc0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "agentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultResponse")
    def default_response(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultResponse"))

    @default_response.setter
    def default_response(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__52b385fe47a9eca35f45b73528cd3a9232f6ab132faa380def02b8343c5ae56c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultResponse", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4eb55537f234204dec96d4b2a5678d5fdd9120f4a8ce1d903360fedddfc10f2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="guardrailUuid")
    def guardrail_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guardrailUuid"))

    @guardrail_uuid.setter
    def guardrail_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__de41e48f7dd100a6d0274344bf19dd70cf78721105f7b2f51efe6ddd876a3ba3)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1dbb4145e467f653d16449a0ad1f7b9f2edbec6245c43dd5666de58a456e576f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isDefault", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__792aed5a3a790d38f45cc3a7d314bf744be7a7ce4dec374435f20afa00b9f825)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="priority")
    def priority(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "priority"))

    @priority.setter
    def priority(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3bb417d2696ddab0c653c1d72bfe701abc4072dfb48158376ca668dd906000f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "priority", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="type")
    def type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "type"))

    @type.setter
    def type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__138b64edd90747b7cad76e04e0448d21d08e5eb1f67568848dd95bbb009d7eda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "type", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d2a5249e10c6429a98c998cfa3ccdadc7d265bebaa998217a7d76ddbf418956)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAgentGuardrail]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAgentGuardrail]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAgentGuardrail]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24ef6572b3afb385dc55607b380d7d81e76d1b27b1c423aebce05e04ba5c96ab)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentAnthropicApiKey",
    jsii_struct_bases=[],
    name_mapping={"created_by": "createdBy", "name": "name", "uuid": "uuid"},
)
class DataDigitaloceanGenaiAgentAnthropicApiKey:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#created_by DataDigitaloceanGenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__38ba73ee3aed1a5541136e25472d14a34994b3bab9ab9c89626bc0ce055d14d1)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#created_by DataDigitaloceanGenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentAnthropicApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentAnthropicApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentAnthropicApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fb5a1ba2f9c6104cb59e57e8237cf2a3ae2f2e48c3870c90a8e17b846073f39)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentAnthropicApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__119028dbc7bd05564ae2c2a63b0e0dfdecd7cb6205da7391f37a7fe16c5c774a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentAnthropicApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82b50c3d1427a55c94b91cfb8d6aed6d2e1642ec4708e780d77c3e51941c3790)
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
            type_hints = typing.get_type_hints(_typecheckingstub__70da977f9f2b266b8e693bf2932b149e02d99f57e76c8765819abf8393026d96)
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
            type_hints = typing.get_type_hints(_typecheckingstub__99ca7b616cb7b17333407d3c353d0f5055d75e2619345ff42efe3e5b880cf676)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAnthropicApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAnthropicApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAnthropicApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c6faa1830c09a76442b2269a35b8b21157444ce12c6fdee262e17f7cb0b3f2d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentAnthropicApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentAnthropicApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3ffb4b6f99a74dfef8210f4f7039a5bccb8748fe2b0e774cfe2a952d2276c915)
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
            type_hints = typing.get_type_hints(_typecheckingstub__90503be41741dac6fd234e7dde2161fd5f0244d989460eb5dc0756e4b970c2c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a958250a0f8a1a6c1aa9b8103afada041df126a27c38f5f2f149c3c5b5b948b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33d53c97e12edb62681f234b378143447824310b005a8e8c37c48a532364dd82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAnthropicApiKey]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAnthropicApiKey]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAnthropicApiKey]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bcf120e586acfedafd0a65ca9bf80a3414562cd2f1df972e6df586ba91a43b60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentApiKeyInfos",
    jsii_struct_bases=[],
    name_mapping={
        "created_by": "createdBy",
        "name": "name",
        "secret_key": "secretKey",
        "uuid": "uuid",
    },
)
class DataDigitaloceanGenaiAgentApiKeyInfos:
    def __init__(
        self,
        *,
        created_by: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        secret_key: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param created_by: Created By user ID for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#created_by DataDigitaloceanGenaiAgent#created_by}
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param secret_key: Updated At timestamp for the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#secret_key DataDigitaloceanGenaiAgent#secret_key}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7ded080fd3cbd2a0cdb2cf1520aa26c5b4833b0d24838c43a9b7268a02a38a25)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#created_by DataDigitaloceanGenaiAgent#created_by}
        '''
        result = self._values.get("created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secret_key(self) -> typing.Optional[builtins.str]:
        '''Updated At timestamp for the API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#secret_key DataDigitaloceanGenaiAgent#secret_key}
        '''
        result = self._values.get("secret_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentApiKeyInfos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentApiKeyInfosList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentApiKeyInfosList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5314bb0f238e14f39b077cb662f3c1e4463af572c70e721578bcf9fbaf66f1c9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentApiKeyInfosOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd833d8316094b6ba27e4b71f6c230dd66ca9c3320d1d29e69a3ab3ede736e1e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentApiKeyInfosOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a2520213b1201facf67ca5ac31bafcbdf6d4aa9789b214a7e449e5f2f398a79f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed832516552aec6c833e8df19c544880f559ac7af531b83a8b02b8f1d9a45a2c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__082cf98e664d0c6ef18dd3472084c1140b4fea009f306cb0e015e4a9a5be0be6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeyInfos]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeyInfos]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeyInfos]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bab423fa1795455e9621709e48e64d37da77f4724ab9559e3ffd62dd1ec63cd4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentApiKeyInfosOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentApiKeyInfosOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b52fb1c8420130756683a8f75e05df7c66e8beec36a958728f9766fd74e66da4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__01976ef1bcdf60c93a6d292ecb210a7b34d5b0b02ec994c1bb47657c5aade9a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "createdBy", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1fa2149927547db68cda42b44b457919bbf7b6d040acded5b6c659729dd6ce2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @secret_key.setter
    def secret_key(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bd7ac3a561d6062b3f75c287950fb77d2e689a7ae9bdd8327b5841d7d7613312)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secretKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dddef34524f58ce8130ecf8ca8f378b5225953ab2a65722053ddf4ba590a3515)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeyInfos]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeyInfos]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeyInfos]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__71f185330fcaaaf0857296aa570b49bd25f8d96e59191256055a100fcadf8eaa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentApiKeys",
    jsii_struct_bases=[],
    name_mapping={"api_key": "apiKey"},
)
class DataDigitaloceanGenaiAgentApiKeys:
    def __init__(self, *, api_key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param api_key: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key DataDigitaloceanGenaiAgent#api_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e4e893f7d8048996e26c829a945691e54aec9390f47188440d53963a5609936)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key DataDigitaloceanGenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentApiKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentApiKeysList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentApiKeysList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a0f1b60ace4890ddbcba8023cd78d86a88f76b8041e23da5ce769f4a1abbddb)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentApiKeysOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bc571d90441f71d1e99484e055c4f83b8f38ee69ef9fab660325cd742bd2003)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentApiKeysOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73102bd0ba435498276f1d0a5ac792ed2ffbf9ab8abaca03e4792c89b8501d2e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2be27a0085ee7ac546fb0ddd2ae0348b51002ddae1bacadc0113ef0da29fe568)
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
            type_hints = typing.get_type_hints(_typecheckingstub__89144df563a2cf5401f2fa579fe27dd3da9d97d268088dda303e7fd83d00bf04)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeys]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeys]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeys]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__55e9b8cb776445857224cc63c1a17059540f7c28da53f0ffabc8b587be5e2ab2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentApiKeysOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentApiKeysOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c516f2a14a0911deb46f096762085c6067d896bcb2e83fe4d1e72d54da37e08)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e3023831f55efcfa27402d530cf25bcab42072114938c39bd9ba42f7f696c82)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeys]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeys]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeys]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c89ad2582a44fc6367b02734ef25c48b1508b01995925ab1376e4298ffebdc32)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChatbot",
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
class DataDigitaloceanGenaiAgentChatbot:
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
        :param button_background_color: Background color for the chatbot button. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#button_background_color DataDigitaloceanGenaiAgent#button_background_color}
        :param logo: Logo for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#logo DataDigitaloceanGenaiAgent#logo}
        :param name: Name of the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param primary_color: Primary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#primary_color DataDigitaloceanGenaiAgent#primary_color}
        :param secondary_color: Secondary color for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#secondary_color DataDigitaloceanGenaiAgent#secondary_color}
        :param starting_message: Starting message for the chatbot. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#starting_message DataDigitaloceanGenaiAgent#starting_message}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d9e190799d3fca7427295789b2c609454e7abd8b9eafd5d6b6f2c01f58081950)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#button_background_color DataDigitaloceanGenaiAgent#button_background_color}
        '''
        result = self._values.get("button_background_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def logo(self) -> typing.Optional[builtins.str]:
        '''Logo for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#logo DataDigitaloceanGenaiAgent#logo}
        '''
        result = self._values.get("logo")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def primary_color(self) -> typing.Optional[builtins.str]:
        '''Primary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#primary_color DataDigitaloceanGenaiAgent#primary_color}
        '''
        result = self._values.get("primary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def secondary_color(self) -> typing.Optional[builtins.str]:
        '''Secondary color for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#secondary_color DataDigitaloceanGenaiAgent#secondary_color}
        '''
        result = self._values.get("secondary_color")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def starting_message(self) -> typing.Optional[builtins.str]:
        '''Starting message for the chatbot.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#starting_message DataDigitaloceanGenaiAgent#starting_message}
        '''
        result = self._values.get("starting_message")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChatbot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChatbotIdentifiers",
    jsii_struct_bases=[],
    name_mapping={"chatbot_id": "chatbotId"},
)
class DataDigitaloceanGenaiAgentChatbotIdentifiers:
    def __init__(self, *, chatbot_id: typing.Optional[builtins.str] = None) -> None:
        '''
        :param chatbot_id: Chatbot ID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot_id DataDigitaloceanGenaiAgent#chatbot_id}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3dce3a0093de50f0e3841a61c0a6fd63c8d62237a428bb4e2d2fe0bc9b8b3da1)
            check_type(argname="argument chatbot_id", value=chatbot_id, expected_type=type_hints["chatbot_id"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if chatbot_id is not None:
            self._values["chatbot_id"] = chatbot_id

    @builtins.property
    def chatbot_id(self) -> typing.Optional[builtins.str]:
        '''Chatbot ID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot_id DataDigitaloceanGenaiAgent#chatbot_id}
        '''
        result = self._values.get("chatbot_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChatbotIdentifiers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentChatbotIdentifiersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChatbotIdentifiersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebaf60d63d2c369f06fe62cc515f41f96db79f93f02f1ed6e73b2510361d4076)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChatbotIdentifiersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecae4e947eb3984b272722ddeb2de2eb1cd61c6c5c2217d1fb8005eff7da593f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChatbotIdentifiersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ae7be4bb027905d5dcd1ffcfbbbc8b3228e7cd59a1ed8ed05118cbcc84fcc0ee)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fe46fa384d1b72946ba37d4385f968ca68863d5b850f2165333743daeb2e6115)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ebba11235b740876849de8ac6448649706015a2adbdffa0c5fc4b6e265cbaffd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbotIdentifiers]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbotIdentifiers]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbotIdentifiers]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f51094a0a11a40722a68c0cb4f77c4f3df29988dc26fcba7ad948667ed53a7aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChatbotIdentifiersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChatbotIdentifiersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6c69dbca9cd4acd395674e7a27fc4983b6c48693b3a93e14ebfb04d9904cd169)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetChatbotId")
    def reset_chatbot_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetChatbotId", []))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdInput")
    def chatbot_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "chatbotIdInput"))

    @builtins.property
    @jsii.member(jsii_name="chatbotId")
    def chatbot_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "chatbotId"))

    @chatbot_id.setter
    def chatbot_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__509eae7c7528137a2d343a2f2fa87d0fe8483b63f1a714c97d73b6404d49121d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "chatbotId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbotIdentifiers]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbotIdentifiers]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbotIdentifiers]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0fb4b46f7a63be64635251d08fe95de61ec8c1e20da0756aef142e714d59bcce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChatbotList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChatbotList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef7fa39cfd6efd16751015a80fb39453d30ccfc6eab39aef904661b75390943e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChatbotOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9df83f1f2ec5b81cb8c11127a5b23e36c9adc2322b5e378f48b17491124d4811)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChatbotOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c888f775f3dfaa6cecb0d0397b801c97aed8d71b47e37a3a732dcfdee793b803)
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
            type_hints = typing.get_type_hints(_typecheckingstub__24de99fb74dcabb57dade4253e87612fc24123bf432b677494a9be092846a609)
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
            type_hints = typing.get_type_hints(_typecheckingstub__0c2e3c85b312b18258f3d797107906b67cffc507fd1be70c926b99220832426b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbot]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbot]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbot]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f6fc28ce7783d9adb83287809daa0fa3aec3c3fd04ec0f599632342c4bb064d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChatbotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChatbotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d46ea254277d30073e9b3bb13d0c6a1330adfd7296cd0a5222ce0f7e2d78af62)
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
            type_hints = typing.get_type_hints(_typecheckingstub__50456857166a73079f35d55f4dc9ce1ddeefd24b8e2dead294e39d4572b3e31d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "buttonBackgroundColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logo")
    def logo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logo"))

    @logo.setter
    def logo(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81460a09e365a1928e097c9951abfc494451e342f2f41d10c8004acef2592ebb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logo", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d78b1fca1f8eee5b11b8f185065dbdc55659a91d31f5af0ca461ddc4bb3babe2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="primaryColor")
    def primary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryColor"))

    @primary_color.setter
    def primary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0e8dc1d36bd44dbae7a835922f3ff15afb27fcd3d98955b5a198b0fd2c477236)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "primaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="secondaryColor")
    def secondary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryColor"))

    @secondary_color.setter
    def secondary_color(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1a672b091dfc3f3eda1243b360805b81439e0936938bf5543cf48e2572eff730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "secondaryColor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="startingMessage")
    def starting_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingMessage"))

    @starting_message.setter
    def starting_message(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8481a435323a6f1c36b473c8d3dd0574f36441964874a14a0dfe49fda5425987)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "startingMessage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbot]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbot]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbot]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__959e5979f41c54a4821d6121c85e0a5e38bdc65eb07e6baa7e10739f00cf349b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgents",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4f02d5e65877929d25ad96a6ff62902d646d8ab3ddda5437d2df5d6c83831bfe)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28020bf562023fb77ff518ea5e62e3df33458480be16588c1810b404fd786f24)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ff8c8354cf3518b5b600be2e9e0180456a42d560984ec06ec1ee86bd1ceb231)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7b94f6f8ed3a1dcf70fca5c18893c2760117238e9c391b5a73df73d39dd1431f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__94a7da25cce3e4948425a2a3b4c9d96d80a17737948e0beea046a115bc592f8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ec810260e8f052f0ed07be9109eafafe1b743fa2ba3fd100732c2281d5f97ba6)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e08d6e7e8a75c2ff1f6440fa5f4ececed89c82941b641c0128dd505dd092f84)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2b83355fab72a9d8848da09f99faf2370630c0fb8d60140304c4495f7ae7ba3d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__28249d151a985ee9705fd8d3832e4ec65fd161c54fa900c169f1aa97feaa5565)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18130b6c50472f70b173bbd7d630f4bbde34ad52cc7711c80279459a41b3a796)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6179f8a6d66ebe94f822e3aa1c16c4baaa9a45e5871fb9f029ce54e955dc625f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2d18751144326491a38f28b56ec0b915305b1b87c9b8a6612c9ae6559c99ed50)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__85bd5ac3eaf92950086c2721aac0eb1abdcdd4a1a6d47fa20ed3e5c24d60e56a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6654350b4cc214b389d512221ea9f08f6ea91cddab7a81667e920eadef66851c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsApiKeys",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgentsApiKeys:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgentsApiKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentChildAgentsApiKeysList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsApiKeysList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3f1ff8838143a43f2d6de159761c4ee743bdde39cce4696eb1f1e4819049a343)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsApiKeysOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93818f9487728138ef1f3c0ec00e0dd07d7257dc836965daf00f06c8caa00197)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsApiKeysOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__983c0ca6825c01bbde495e29180b2f1da4609e4cc030f8dffc6e85c6fb571db4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a0b0c38407c85d97d3b3d2cd85050546cd8aafb4a6435ab10960392706e75465)
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
            type_hints = typing.get_type_hints(_typecheckingstub__52def4f288040749aa3a6520d1efddb55804befe9fb8d20af97968f557809651)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsApiKeysOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsApiKeysOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9bcda4fae834fec34e7b567e25543b4323c43ff80f1b17055d42e2d93a96045)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeys]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeys], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeys],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__50dca3f7ebafa30a14cd4bcb24193e40887fabe49da44e0ff6fb861401eb24e0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsChatbot",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgentsChatbot:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgentsChatbot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__89aac4f9c82f71ce8bdbb1d21f9b4afdf5b36c0f984b1cbfb86f311862812db4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6235e30005acdd3ec1fbce4bab13cb5173fd82308b662a5252bf9e0156594470)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f3d31961bdd2416fd456c0a85ad08c34240008fd5daab2049e622611c4adcf4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__50e759dc028b419058446803d043448bafb0b4c7daec5155a1db17f96bb55a8a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b0c96fcf0b82935d71cb57a1112e4bbe15bfff3c2ffb707788e0fda193d4c9d9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__bd45ad34167a972a0a1c3da697fbac246844d9547ec8d15ec577b79ab758df00)
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
    ) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__93b1085dd102682b5a43750daa56f51d74b3217dcb84b8732efcdc8238d6d09a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsChatbotList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsChatbotList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0374c9ae188cd1b2624afed43d907c4ebe59c6cd474b8ce3c90c695560d4a03d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsChatbotOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b08f82fa1f932f6d5ece9f080374f2f50016414425a8e55d2fdb1f9d93a74543)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsChatbotOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6ab477883b1c2eb98b9d3c3fc04f9880c76ccac0ea785174e4ccfc2191a4299)
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
            type_hints = typing.get_type_hints(_typecheckingstub__44f96be3b8d1634708f5f022b7a2827cb8692287d56fd3f3b32d18245f669c97)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cf65bb06f0cd8fe61b524db56e7191356703f3e6fa0781cfe813248cea87594f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsChatbotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsChatbotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__52ea33cabbb00e7e334b6e10c32edd39c0be35f774191d2fea254abe0d1eaca5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColor")
    def button_background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonBackgroundColor"))

    @builtins.property
    @jsii.member(jsii_name="logo")
    def logo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logo"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="primaryColor")
    def primary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryColor"))

    @builtins.property
    @jsii.member(jsii_name="secondaryColor")
    def secondary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryColor"))

    @builtins.property
    @jsii.member(jsii_name="startingMessage")
    def starting_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingMessage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbot]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbot],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a43e5b3ddd33571e159b508a1e71097174bce2296553ae5d47d3ae402799848)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsDeployment",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentChildAgentsDeployment:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentChildAgentsDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentChildAgentsDeploymentList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsDeploymentList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__585524ff16782071fba02b94f09f69694e9bc5ea3cd537e4aae5d2ceba0f02bd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsDeploymentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aaeaadcfff49cbc6dbdb9efdb881996123d8185a4f1641039fe0b5196f826510)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsDeploymentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c3180e5253052aeba7e7500220b3b872c8ca3e871615447af82688d192c9e839)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2c3a95343286682340ced4e5b3aa6e21d5da2968e1d36c2aa73f7b013a7a5e4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__688dac456e7d8c8d3980077bac90ec112f3fd731876d8ae17678f62a13f5c0c2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__0d79556b58d0c029e4a6865cb3331727a252dbd23a0d2dce640db1f9b2e06dfd)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgentsDeployment]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgentsDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7fb6e649aa49f924fa225f6201a4e205e638abc439ade7607153ef8c0cdddf53)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__425b7648fbd3c16305b0602e2f5fbad9db225f83d13d1602052eb0695a49fb3a)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentChildAgentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ec84ae1afa71d8f3b4be75c2b29c86c07a30d28d9935c7d79aa00752f8b3fc2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentChildAgentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b7f43a25f8bc795770b79d51339386ec3f678e0e7293516342edb166798b464)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e091c14e0a33797286addc3a4d0b8c5740254c82d5e480d8db58a8566eaf32d8)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc358a2c98d2290fe2e45fbec91e02d1f2be97e54bc409487086eee6fbe86a98)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentChildAgentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentChildAgentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__179bd55ce31daaaa0c07dfe5cbee9d0bd71b8f3f36aaf10e8b810bc557d975f4)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentId"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(
        self,
    ) -> DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyList:
        return typing.cast(DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyList, jsii.get(self, "anthropicApiKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfos")
    def api_key_infos(self) -> DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosList:
        return typing.cast(DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosList, jsii.get(self, "apiKeyInfos"))

    @builtins.property
    @jsii.member(jsii_name="apiKeys")
    def api_keys(self) -> DataDigitaloceanGenaiAgentChildAgentsApiKeysList:
        return typing.cast(DataDigitaloceanGenaiAgentChildAgentsApiKeysList, jsii.get(self, "apiKeys"))

    @builtins.property
    @jsii.member(jsii_name="chatbot")
    def chatbot(self) -> DataDigitaloceanGenaiAgentChildAgentsChatbotList:
        return typing.cast(DataDigitaloceanGenaiAgentChildAgentsChatbotList, jsii.get(self, "chatbot"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiers")
    def chatbot_identifiers(
        self,
    ) -> DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersList:
        return typing.cast(DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersList, jsii.get(self, "chatbotIdentifiers"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> DataDigitaloceanGenaiAgentChildAgentsDeploymentList:
        return typing.cast(DataDigitaloceanGenaiAgentChildAgentsDeploymentList, jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @builtins.property
    @jsii.member(jsii_name="modelUuid")
    def model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelUuid"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDigitaloceanGenaiAgentChildAgents]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentChildAgents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentChildAgents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a116ff421788295f59c193eb0dd1b67e59970e3cc32597a9505b72e733a83f7b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentConfig",
    jsii_struct_bases=[_cdktf_9a9027ec.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "agent_id": "agentId",
        "agent_guardrail": "agentGuardrail",
        "anthropic_api_key": "anthropicApiKey",
        "api_key_infos": "apiKeyInfos",
        "api_keys": "apiKeys",
        "chatbot": "chatbot",
        "chatbot_identifiers": "chatbotIdentifiers",
        "deployment": "deployment",
        "description": "description",
        "functions": "functions",
        "id": "id",
        "if_case": "ifCase",
        "k": "k",
        "knowledge_bases": "knowledgeBases",
        "max_tokens": "maxTokens",
        "model": "model",
        "open_ai_api_key": "openAiApiKey",
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
class DataDigitaloceanGenaiAgentConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        agent_id: builtins.str,
        agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]]] = None,
        anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
        api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
        chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
        deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentDeployment", typing.Dict[builtins.str, typing.Any]]]]] = None,
        description: typing.Optional[builtins.str] = None,
        functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentFunctions", typing.Dict[builtins.str, typing.Any]]]]] = None,
        id: typing.Optional[builtins.str] = None,
        if_case: typing.Optional[builtins.str] = None,
        k: typing.Optional[jsii.Number] = None,
        knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_tokens: typing.Optional[jsii.Number] = None,
        model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentOpenAiApiKey", typing.Dict[builtins.str, typing.Any]]]]] = None,
        retrieval_method: typing.Optional[builtins.str] = None,
        route_created_by: typing.Optional[builtins.str] = None,
        route_name: typing.Optional[builtins.str] = None,
        route_uuid: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        temperature: typing.Optional[jsii.Number] = None,
        template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplate", typing.Dict[builtins.str, typing.Any]]]]] = None,
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
        :param agent_id: ID of the Agent to retrieve. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_id DataDigitaloceanGenaiAgent#agent_id}
        :param agent_guardrail: agent_guardrail block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_guardrail DataDigitaloceanGenaiAgent#agent_guardrail}
        :param anthropic_api_key: anthropic_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#anthropic_api_key DataDigitaloceanGenaiAgent#anthropic_api_key}
        :param api_key_infos: api_key_infos block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key_infos DataDigitaloceanGenaiAgent#api_key_infos}
        :param api_keys: api_keys block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_keys DataDigitaloceanGenaiAgent#api_keys}
        :param chatbot: chatbot block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot DataDigitaloceanGenaiAgent#chatbot}
        :param chatbot_identifiers: chatbot_identifiers block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot_identifiers DataDigitaloceanGenaiAgent#chatbot_identifiers}
        :param deployment: deployment block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#deployment DataDigitaloceanGenaiAgent#deployment}
        :param description: Description for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param functions: functions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#functions DataDigitaloceanGenaiAgent#functions}
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#id DataDigitaloceanGenaiAgent#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param if_case: If case condition. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#if_case DataDigitaloceanGenaiAgent#if_case}
        :param k: K value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#k DataDigitaloceanGenaiAgent#k}
        :param knowledge_bases: knowledge_bases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#knowledge_bases DataDigitaloceanGenaiAgent#knowledge_bases}
        :param max_tokens: Maximum tokens allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#max_tokens DataDigitaloceanGenaiAgent#max_tokens}
        :param model: model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#model DataDigitaloceanGenaiAgent#model}
        :param open_ai_api_key: open_ai_api_key block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#open_ai_api_key DataDigitaloceanGenaiAgent#open_ai_api_key}
        :param retrieval_method: Retrieval method used. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#retrieval_method DataDigitaloceanGenaiAgent#retrieval_method}
        :param route_created_by: User who created the route. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_created_by DataDigitaloceanGenaiAgent#route_created_by}
        :param route_name: Route name. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_name DataDigitaloceanGenaiAgent#route_name}
        :param route_uuid: Route UUID. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_uuid DataDigitaloceanGenaiAgent#route_uuid}
        :param tags: List of Tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        :param temperature: Agent temperature setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#temperature DataDigitaloceanGenaiAgent#temperature}
        :param template: template block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#template DataDigitaloceanGenaiAgent#template}
        :param top_p: Top P sampling parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#top_p DataDigitaloceanGenaiAgent#top_p}
        :param url: URL for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param user_id: User ID linked with the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7cd2f69e97f123464bb992af3789462ccdfbeaf24bc9bc57b8783ac085ec7ad2)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument agent_id", value=agent_id, expected_type=type_hints["agent_id"])
            check_type(argname="argument agent_guardrail", value=agent_guardrail, expected_type=type_hints["agent_guardrail"])
            check_type(argname="argument anthropic_api_key", value=anthropic_api_key, expected_type=type_hints["anthropic_api_key"])
            check_type(argname="argument api_key_infos", value=api_key_infos, expected_type=type_hints["api_key_infos"])
            check_type(argname="argument api_keys", value=api_keys, expected_type=type_hints["api_keys"])
            check_type(argname="argument chatbot", value=chatbot, expected_type=type_hints["chatbot"])
            check_type(argname="argument chatbot_identifiers", value=chatbot_identifiers, expected_type=type_hints["chatbot_identifiers"])
            check_type(argname="argument deployment", value=deployment, expected_type=type_hints["deployment"])
            check_type(argname="argument description", value=description, expected_type=type_hints["description"])
            check_type(argname="argument functions", value=functions, expected_type=type_hints["functions"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument if_case", value=if_case, expected_type=type_hints["if_case"])
            check_type(argname="argument k", value=k, expected_type=type_hints["k"])
            check_type(argname="argument knowledge_bases", value=knowledge_bases, expected_type=type_hints["knowledge_bases"])
            check_type(argname="argument max_tokens", value=max_tokens, expected_type=type_hints["max_tokens"])
            check_type(argname="argument model", value=model, expected_type=type_hints["model"])
            check_type(argname="argument open_ai_api_key", value=open_ai_api_key, expected_type=type_hints["open_ai_api_key"])
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
            "agent_id": agent_id,
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
        if max_tokens is not None:
            self._values["max_tokens"] = max_tokens
        if model is not None:
            self._values["model"] = model
        if open_ai_api_key is not None:
            self._values["open_ai_api_key"] = open_ai_api_key
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
    def agent_id(self) -> builtins.str:
        '''ID of the Agent to retrieve.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_id DataDigitaloceanGenaiAgent#agent_id}
        '''
        result = self._values.get("agent_id")
        assert result is not None, "Required property 'agent_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def agent_guardrail(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAgentGuardrail]]]:
        '''agent_guardrail block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agent_guardrail DataDigitaloceanGenaiAgent#agent_guardrail}
        '''
        result = self._values.get("agent_guardrail")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAgentGuardrail]]], result)

    @builtins.property
    def anthropic_api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAnthropicApiKey]]]:
        '''anthropic_api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#anthropic_api_key DataDigitaloceanGenaiAgent#anthropic_api_key}
        '''
        result = self._values.get("anthropic_api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAnthropicApiKey]]], result)

    @builtins.property
    def api_key_infos(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeyInfos]]]:
        '''api_key_infos block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key_infos DataDigitaloceanGenaiAgent#api_key_infos}
        '''
        result = self._values.get("api_key_infos")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeyInfos]]], result)

    @builtins.property
    def api_keys(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeys]]]:
        '''api_keys block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_keys DataDigitaloceanGenaiAgent#api_keys}
        '''
        result = self._values.get("api_keys")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeys]]], result)

    @builtins.property
    def chatbot(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbot]]]:
        '''chatbot block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot DataDigitaloceanGenaiAgent#chatbot}
        '''
        result = self._values.get("chatbot")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbot]]], result)

    @builtins.property
    def chatbot_identifiers(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbotIdentifiers]]]:
        '''chatbot_identifiers block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#chatbot_identifiers DataDigitaloceanGenaiAgent#chatbot_identifiers}
        '''
        result = self._values.get("chatbot_identifiers")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbotIdentifiers]]], result)

    @builtins.property
    def deployment(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentDeployment"]]]:
        '''deployment block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#deployment DataDigitaloceanGenaiAgent#deployment}
        '''
        result = self._values.get("deployment")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentDeployment"]]], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def functions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentFunctions"]]]:
        '''functions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#functions DataDigitaloceanGenaiAgent#functions}
        '''
        result = self._values.get("functions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentFunctions"]]], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#id DataDigitaloceanGenaiAgent#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def if_case(self) -> typing.Optional[builtins.str]:
        '''If case condition.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#if_case DataDigitaloceanGenaiAgent#if_case}
        '''
        result = self._values.get("if_case")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k(self) -> typing.Optional[jsii.Number]:
        '''K value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#k DataDigitaloceanGenaiAgent#k}
        '''
        result = self._values.get("k")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def knowledge_bases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentKnowledgeBases"]]]:
        '''knowledge_bases block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#knowledge_bases DataDigitaloceanGenaiAgent#knowledge_bases}
        '''
        result = self._values.get("knowledge_bases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentKnowledgeBases"]]], result)

    @builtins.property
    def max_tokens(self) -> typing.Optional[jsii.Number]:
        '''Maximum tokens allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#max_tokens DataDigitaloceanGenaiAgent#max_tokens}
        '''
        result = self._values.get("max_tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def model(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModel"]]]:
        '''model block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#model DataDigitaloceanGenaiAgent#model}
        '''
        result = self._values.get("model")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModel"]]], result)

    @builtins.property
    def open_ai_api_key(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentOpenAiApiKey"]]]:
        '''open_ai_api_key block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#open_ai_api_key DataDigitaloceanGenaiAgent#open_ai_api_key}
        '''
        result = self._values.get("open_ai_api_key")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentOpenAiApiKey"]]], result)

    @builtins.property
    def retrieval_method(self) -> typing.Optional[builtins.str]:
        '''Retrieval method used.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#retrieval_method DataDigitaloceanGenaiAgent#retrieval_method}
        '''
        result = self._values.get("retrieval_method")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_created_by(self) -> typing.Optional[builtins.str]:
        '''User who created the route.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_created_by DataDigitaloceanGenaiAgent#route_created_by}
        '''
        result = self._values.get("route_created_by")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_name(self) -> typing.Optional[builtins.str]:
        '''Route name.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_name DataDigitaloceanGenaiAgent#route_name}
        '''
        result = self._values.get("route_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def route_uuid(self) -> typing.Optional[builtins.str]:
        '''Route UUID.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#route_uuid DataDigitaloceanGenaiAgent#route_uuid}
        '''
        result = self._values.get("route_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def temperature(self) -> typing.Optional[jsii.Number]:
        '''Agent temperature setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#temperature DataDigitaloceanGenaiAgent#temperature}
        '''
        result = self._values.get("temperature")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def template(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplate"]]]:
        '''template block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#template DataDigitaloceanGenaiAgent#template}
        '''
        result = self._values.get("template")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplate"]]], result)

    @builtins.property
    def top_p(self) -> typing.Optional[jsii.Number]:
        '''Top P sampling parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#top_p DataDigitaloceanGenaiAgent#top_p}
        '''
        result = self._values.get("top_p")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''User ID linked with the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentDeployment",
    jsii_struct_bases=[],
    name_mapping={
        "name": "name",
        "status": "status",
        "url": "url",
        "uuid": "uuid",
        "visibility": "visibility",
    },
)
class DataDigitaloceanGenaiAgentDeployment:
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
        :param name: Name of the API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param status: Status of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#status DataDigitaloceanGenaiAgent#status}
        :param url: Url of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        :param visibility: Visibility of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#visibility DataDigitaloceanGenaiAgent#visibility}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__878cfeb5b6b6a73d8619ea2806b517677769fb166d2c88424e22e8610bf9d389)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def status(self) -> typing.Optional[builtins.str]:
        '''Status of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#status DataDigitaloceanGenaiAgent#status}
        '''
        result = self._values.get("status")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Url of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def visibility(self) -> typing.Optional[builtins.str]:
        '''Visibility of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#visibility DataDigitaloceanGenaiAgent#visibility}
        '''
        result = self._values.get("visibility")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentDeploymentList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentDeploymentList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7f06e725c825025a3afbb7b8cdf6baf3b738454c7c84302edc6644ea781beaf)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentDeploymentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ed6ba9a8ef56b2abeb1da320f46ccbe7b5fafab4600921d4a538f2c2b1dff694)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentDeploymentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__78986f0e490f7bf8fa7c6efcaf96538cb70aeb74ced8b6c0cdf60c7564a9be89)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b683d5e4ff6996cfaf7d24cb8700fc31fc7ef2561274283d647a60fdddc1a602)
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
            type_hints = typing.get_type_hints(_typecheckingstub__13bf1558b9559c30ba995526e01299d3c3f4278d166c33344ef579fb4fc0a0de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentDeployment]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentDeployment]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentDeployment]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2945e7cc92d1b6a8d0ea5f7a818406deb8dcb0ad04f6acfc5382e8edd897c076)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ba7e391d2966bd9e70c84bbee53de0fc19ec7b8cb54c36292da1995d2d655f75)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bfbc2e4cc415de98a509cdafb720e4c01ceb7c7797439cbeaf26f30f218fa1fa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @status.setter
    def status(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d00d21dde52563dd0842025e0b9e35343621e9b52ba3610703e6d01bd61e55d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "status", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1317e497e8aad8626a9ea57042c0fba4e669432e4e68699e201b8d4aa64c8051)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__244eb711bf53cce707f265f4bda99a7da00b80dbdb62282f6464e018624f5887)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @visibility.setter
    def visibility(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1b66d0626535684025ffe17a1c872926efe3a6ee0c7bda65cd6790f05264f56)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "visibility", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentDeployment]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentDeployment]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentDeployment]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97225efdee331c5f1d70aef80ae0f47609fb09a44de7612de18726d102a66d68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentFunctions",
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
class DataDigitaloceanGenaiAgentFunctions:
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
        :param api_key: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key DataDigitaloceanGenaiAgent#api_key}
        :param description: Description of the Function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param faasname: Name of function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#faasname DataDigitaloceanGenaiAgent#faasname}
        :param faasnamespace: Namespace of function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#faasnamespace DataDigitaloceanGenaiAgent#faasnamespace}
        :param guardrail_uuid: Guardrail UUID for the Function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#guardrail_uuid DataDigitaloceanGenaiAgent#guardrail_uuid}
        :param name: Name of function. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param url: Url of the Deployment. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param uuid: API Key value. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fe419d851e0a68377484695207aa2f1b7b6cff03737b127ea7412b5e9e1daa17)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key DataDigitaloceanGenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        '''Description of the Function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def faasname(self) -> typing.Optional[builtins.str]:
        '''Name of function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#faasname DataDigitaloceanGenaiAgent#faasname}
        '''
        result = self._values.get("faasname")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def faasnamespace(self) -> typing.Optional[builtins.str]:
        '''Namespace of function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#faasnamespace DataDigitaloceanGenaiAgent#faasnamespace}
        '''
        result = self._values.get("faasnamespace")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def guardrail_uuid(self) -> typing.Optional[builtins.str]:
        '''Guardrail UUID for the Function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#guardrail_uuid DataDigitaloceanGenaiAgent#guardrail_uuid}
        '''
        result = self._values.get("guardrail_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of function.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''Url of the Deployment.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''API Key value.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentFunctions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentFunctionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentFunctionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d8932c737407a5c507b5139d4abdc4548cfa5de86e7088de584fc8f908378277)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentFunctionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b299846e1c793c844043d8399c434aad1eaf133c2cb4a51a02ed9ab99cb54d1a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentFunctionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d30aa883ef9599d76159c6bd9c98ccdef52299533dd101031a1e8fe749b5fb4)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9488a732a52f93de1291cc5f2f13364cc94e8576e757061eb758797da116b98a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a2845b2ffffbabd526b333c91dfa67320a505d34551bed0f16485d455bba2ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentFunctions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentFunctions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentFunctions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__400204d5c5e5db4b2fba2e398ca43eaca678e320c6a726467b85daca5f070356)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentFunctionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentFunctionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c437a1d8ae6003b97d7a457ee1c43e9e74902ff0d67d51a7ec175e26620e0238)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d23c4039d775447918b23125b98d76384e643a20637832c98c8c858e73528433)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @description.setter
    def description(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9e81c1c3537ac8219b564211e136f8be8f50d2900c07e9f1ed31160b4a2b8934)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faasname")
    def faasname(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "faasname"))

    @faasname.setter
    def faasname(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a5e9c1f415e2dad778234dac3d1393787b6be4ec5aed3a58dc4ae0324bbd796a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faasname", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="faasnamespace")
    def faasnamespace(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "faasnamespace"))

    @faasnamespace.setter
    def faasnamespace(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d1ca82be36ab8f42e048744cebe61cbedc2888421999e6b472d8c34183d9e8aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "faasnamespace", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="guardrailUuid")
    def guardrail_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "guardrailUuid"))

    @guardrail_uuid.setter
    def guardrail_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb6a848c8c327b8f16f2aea2e83f3b6f1493be8554877ffd7d828c748adee7e5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "guardrailUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d89cf350e11ad3482d6bb1a99fd79a8a45f5535d01ed7dba61acee3b0f2528)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2b2f647bc08c321bdb16b93b05edf382eef8f3a21790aa523da91390e2dac825)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b22e873f121715ba07086defc511c092c088446c168a2d0eda3164ac82d16a1c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentFunctions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentFunctions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentFunctions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__190c4f05f5243abfc2d15db403bba2ca7878cb658a8ea520f4a932740d4f5f18)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentKnowledgeBases",
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
class DataDigitaloceanGenaiAgentKnowledgeBases:
    def __init__(
        self,
        *,
        database_id: typing.Optional[builtins.str] = None,
        embedding_model_uuid: typing.Optional[builtins.str] = None,
        is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_indexing_job: typing.Optional[typing.Union["DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database_id: Database ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#database_id DataDigitaloceanGenaiAgent#database_id}
        :param embedding_model_uuid: Embedding model UUID for the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#embedding_model_uuid DataDigitaloceanGenaiAgent#embedding_model_uuid}
        :param is_public: Indicates if the Knowledge Base is public. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_public DataDigitaloceanGenaiAgent#is_public}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#last_indexing_job DataDigitaloceanGenaiAgent#last_indexing_job}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param project_id: Project ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#project_id DataDigitaloceanGenaiAgent#project_id}
        :param region: Region of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#region DataDigitaloceanGenaiAgent#region}
        :param tags: List of tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        :param user_id: User ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        '''
        if isinstance(last_indexing_job, dict):
            last_indexing_job = DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob(**last_indexing_job)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__25757f34ce3888bf48388906e9f776eb4eb4d118df2e06945fa934bb236239ae)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#database_id DataDigitaloceanGenaiAgent#database_id}
        '''
        result = self._values.get("database_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embedding_model_uuid(self) -> typing.Optional[builtins.str]:
        '''Embedding model UUID for the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#embedding_model_uuid DataDigitaloceanGenaiAgent#embedding_model_uuid}
        '''
        result = self._values.get("embedding_model_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Knowledge Base is public.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_public DataDigitaloceanGenaiAgent#is_public}
        '''
        result = self._values.get("is_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def last_indexing_job(
        self,
    ) -> typing.Optional["DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob"]:
        '''last_indexing_job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#last_indexing_job DataDigitaloceanGenaiAgent#last_indexing_job}
        '''
        result = self._values.get("last_indexing_job")
        return typing.cast(typing.Optional["DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Project ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#project_id DataDigitaloceanGenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#region DataDigitaloceanGenaiAgent#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''User ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentKnowledgeBases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob",
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
class DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob:
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#completed_datasources DataDigitaloceanGenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#data_source_uuids DataDigitaloceanGenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#phase DataDigitaloceanGenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tokens DataDigitaloceanGenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#total_datasources DataDigitaloceanGenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fafa2175a106711aefb9293ecc32c1d989b048727e723098e298d6e8787e5984)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#completed_datasources DataDigitaloceanGenaiAgent#completed_datasources}
        '''
        result = self._values.get("completed_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_source_uuids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Datasource UUIDs for the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#data_source_uuids DataDigitaloceanGenaiAgent#data_source_uuids}
        '''
        result = self._values.get("data_source_uuids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase(self) -> typing.Optional[builtins.str]:
        '''Phase of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#phase DataDigitaloceanGenaiAgent#phase}
        '''
        result = self._values.get("phase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Number of tokens processed in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tokens DataDigitaloceanGenaiAgent#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_datasources(self) -> typing.Optional[jsii.Number]:
        '''Total number of datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#total_datasources DataDigitaloceanGenaiAgent#total_datasources}
        '''
        result = self._values.get("total_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID  of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6a251aa4b31bf54b282d59a24e08bef1907d1dd6303ad22b9c3ae414b4e88dc5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9e86c1fac6bdd63b3d38f1e0390f23e62dfa8f7f57f3ef31d92c1a2613c3410e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuids")
    def data_source_uuids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataSourceUuids"))

    @data_source_uuids.setter
    def data_source_uuids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02cf8bc9e60a473bd0b3ae5add0ec3698e3ec050cb9606ceff5a303981a77f75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceUuids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase")
    def phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phase"))

    @phase.setter
    def phase(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d6b30747c7e472572cc31b327cda5cbe9cad26f3d3b21c5eba1e415654d0e464)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ab42971bf32964f0fb340cd159ef1948f46566185fc027d44b362e394a43af3a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDatasources")
    def total_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalDatasources"))

    @total_datasources.setter
    def total_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__902ec2f195ebe6834cc58ca9ad33466b9541599a80b7e9e6ac034ec6cc510ef5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__453ba52e4f2d835319e652a0bbe335bb557edf48e11e4396314755f66afef168)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e7d6ddce91078ab444579f808984efbeaf19a57ac9f9b440d9bec2d0382d441)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentKnowledgeBasesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentKnowledgeBasesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f12dae8473788a51bebb8a299916a4894da3530508d39cabfc839b8eae883e41)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentKnowledgeBasesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a277bd938b525fb895c825391ca569fab446be0fd9b3220c01b3291501b6fe8e)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentKnowledgeBasesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8daeeace70ba782fcb0aefa378cb9c5faf3cea07ed1e77598db662a8a7cded06)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d28c08cb5ee220c7908d82fb084db5f98aa904e84ede53abbe7957fd29bff9b0)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f48c4b575a2c88b923a7d99f30b97796cec548fed52789d8664d803eca46018f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentKnowledgeBases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentKnowledgeBases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentKnowledgeBases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5ed2a61c3cf1523cccf0545c48b8b79beeef4280ff80f23cc0818f00d84badba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentKnowledgeBasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentKnowledgeBasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d365fc61998021e460187be81258ec0bd129b707c9152573928969fe013f6a5)
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#completed_datasources DataDigitaloceanGenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#data_source_uuids DataDigitaloceanGenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#phase DataDigitaloceanGenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tokens DataDigitaloceanGenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#total_datasources DataDigitaloceanGenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        value = DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob(
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
    ) -> DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJobOutputReference:
        return typing.cast(DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJobOutputReference, jsii.get(self, "lastIndexingJob"))

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
    ) -> typing.Optional[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob], jsii.get(self, "lastIndexingJobInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__caa5a393f7a99aab0bbbe9620ec19ec731f4452c992059f2152161e9aaf02f1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuid")
    def embedding_model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelUuid"))

    @embedding_model_uuid.setter
    def embedding_model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__add83557e1ba02a3ed624fa2706f773aa71f8f8ce969cc5d644bdc1161fe6686)
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
            type_hints = typing.get_type_hints(_typecheckingstub__621ba0985b010c805d4fa868cb81e0d334643051a38d7f2ccffc45664db81898)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPublic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9ff5b77bc8218273119ed3c1fb3ced6ab0219fcad0e408a3a0b2c5fc3469b0de)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a625a17546d9127eecca3b210de9d090cf381d66e23c25f82daa141cf56c680f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73821ff36017d0251a367393ec8e31cd713fd628bb74489df728fcd082cfb581)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__141b5f8aa2f365e1d629996778924faeffc92c4466b9fb88b0969953970f18c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__56b18d3aa0536a0989987dd8fbd13a7c059832f4ff457a800744e48468cdf386)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentKnowledgeBases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentKnowledgeBases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentKnowledgeBases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02a6aff56cb080220c0a134a4ba0de01fe2d114c2496802ef34814d68c2ba06d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModel",
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
class DataDigitaloceanGenaiAgentModel:
    def __init__(
        self,
        *,
        agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentModelAgreement", typing.Dict[builtins.str, typing.Any]]]]] = None,
        inference_name: typing.Optional[builtins.str] = None,
        inference_version: typing.Optional[builtins.str] = None,
        is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        parent_uuid: typing.Optional[builtins.str] = None,
        provider: typing.Optional[builtins.str] = None,
        upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
        versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentModelVersions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param agreement: agreement block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agreement DataDigitaloceanGenaiAgent#agreement}
        :param inference_name: Inference name of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_name DataDigitaloceanGenaiAgent#inference_name}
        :param inference_version: Infernce version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_version DataDigitaloceanGenaiAgent#inference_version}
        :param is_foundational: Indicates if the Model Base is foundational. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_foundational DataDigitaloceanGenaiAgent#is_foundational}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param parent_uuid: Parent UUID of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#parent_uuid DataDigitaloceanGenaiAgent#parent_uuid}
        :param provider: Provider of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#provider DataDigitaloceanGenaiAgent#provider}
        :param upload_complete: Indicates if the Model upload is complete. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#upload_complete DataDigitaloceanGenaiAgent#upload_complete}
        :param url: URL of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param usecases: List of Usecases for the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#usecases DataDigitaloceanGenaiAgent#usecases}
        :param versions: versions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#versions DataDigitaloceanGenaiAgent#versions}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5e8e8248c46e8acd5957b66dec426f0951cddaf40d6ea14cfe933d3f2fb4a85b)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModelAgreement"]]]:
        '''agreement block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agreement DataDigitaloceanGenaiAgent#agreement}
        '''
        result = self._values.get("agreement")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModelAgreement"]]], result)

    @builtins.property
    def inference_name(self) -> typing.Optional[builtins.str]:
        '''Inference name of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_name DataDigitaloceanGenaiAgent#inference_name}
        '''
        result = self._values.get("inference_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_version(self) -> typing.Optional[builtins.str]:
        '''Infernce version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_version DataDigitaloceanGenaiAgent#inference_version}
        '''
        result = self._values.get("inference_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_foundational(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model Base is foundational.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_foundational DataDigitaloceanGenaiAgent#is_foundational}
        '''
        result = self._values.get("is_foundational")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_uuid(self) -> typing.Optional[builtins.str]:
        '''Parent UUID of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#parent_uuid DataDigitaloceanGenaiAgent#parent_uuid}
        '''
        result = self._values.get("parent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider(self) -> typing.Optional[builtins.str]:
        '''Provider of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#provider DataDigitaloceanGenaiAgent#provider}
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upload_complete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model upload is complete.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#upload_complete DataDigitaloceanGenaiAgent#upload_complete}
        '''
        result = self._values.get("upload_complete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usecases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Usecases for the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#usecases DataDigitaloceanGenaiAgent#usecases}
        '''
        result = self._values.get("usecases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def versions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModelVersions"]]]:
        '''versions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#versions DataDigitaloceanGenaiAgent#versions}
        '''
        result = self._values.get("versions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModelVersions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelAgreement",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "name": "name",
        "url": "url",
        "uuid": "uuid",
    },
)
class DataDigitaloceanGenaiAgentModelAgreement:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Description of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param name: Name of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param url: URL of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param uuid: UUID of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0c5207c689b6f75146850829e6ba4b3610e038883b99bb9885405f1cbc0e8688)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentModelAgreement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentModelAgreementList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelAgreementList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__e7fb0fb7e9df35288691313f5ea36f593323c807ebda16e5b0edb5b1cfcb18a5)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentModelAgreementOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__26821daf51353be928f68c8db0e62ec226eacee345cb80100e25ebed2d3b90b7)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentModelAgreementOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e96bb983c081e90d638bfbfd7b3f81a6aeb5e7c991478d50f89e556cf8af296)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8a6506fe67a81833e560cb1950a207c411aae639d1cf4e19a655beebe2c7731c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__ded0983ddfb013eb258effb7c56465a5684f1e70091480378c2ae565fb5723d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelAgreement]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelAgreement]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__538ee70cdb812ad91d884ec9f26b800bf8dde01916ad6e57481f1e02740e5777)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentModelAgreementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelAgreementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__22658bb3b0ab564978d09613d1f704c4b89dfebb64004608e2affe144b67c804)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a2223a633760eb49ac2257a1fae5e99fb0a1690ef0931f16495a219def16a0ba)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__76900bdd2f48a94c3a6ceb01e24748fa10bf235eb25a446e5d5199070696d3f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfe0d361ec8253d6d18ffd04ebaca26ac1dfb2bbc32ee0a661ab9a822fb3ad9a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be4ab2498559f8cf2fed894e9e9682aeb0bd73ce42f060658a2e4516c21aa569)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelAgreement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelAgreement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelAgreement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f61fe6be9a548e27193c4df5335e7e5c936e817fec7e7bd16169815bd4c9f526)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentModelList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__44071294b1a68982d1fd62fabff7e7b58986c7b32daf7db6537b40a31b7a8bed)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentModelOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ad48e1275fbbfe2ebecf764f2ad5467128d9b86a37788d27981a3af0719cca8)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentModelOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1cfc45b754f10485ecfc27da8ba050af2bd9caaef054db95e05aa4bf67ed0a5)
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
            type_hints = typing.get_type_hints(_typecheckingstub__8068f86701351aef5888498b744de356d7e769824dc41898f388ef916d613c14)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f1036ea44bb8ffc1de70b6ab08b9e3188f11897c776ef55fbaafc54b43bfb7fd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModel]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModel]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0518560baa8554ac2ef0a41b86b9523c0f233abc324194794aa961aeb5d9f3d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b818a92a46cf495262c52d2f2df24c0bb83938695cdbcb8ce1b727c86f91ef81)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAgreement")
    def put_agreement(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__824fa1c121934b35df746159052fd85adcff8a4055e9b6740406cbd6cb4a8079)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAgreement", [value]))

    @jsii.member(jsii_name="putVersions")
    def put_versions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentModelVersions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__53efa633b9fcba73cbbbb5cfd03968c719b885852df835de884ccd12708ee071)
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
    def agreement(self) -> DataDigitaloceanGenaiAgentModelAgreementList:
        return typing.cast(DataDigitaloceanGenaiAgentModelAgreementList, jsii.get(self, "agreement"))

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
    def versions(self) -> "DataDigitaloceanGenaiAgentModelVersionsList":
        return typing.cast("DataDigitaloceanGenaiAgentModelVersionsList", jsii.get(self, "versions"))

    @builtins.property
    @jsii.member(jsii_name="agreementInput")
    def agreement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelAgreement]]], jsii.get(self, "agreementInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModelVersions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentModelVersions"]]], jsii.get(self, "versionsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceName")
    def inference_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceName"))

    @inference_name.setter
    def inference_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__94f5684104d78bcb1be0f3c20a2c1aff2f56c2bd43e2e1c80c6698502db97e94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inferenceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inferenceVersion")
    def inference_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceVersion"))

    @inference_version.setter
    def inference_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c1116bdea05987f2927ad82be18cbbf89526f2d0a6c88138b77fea02c2aec7a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b2e87086737b2644565ee4a055eb05b4aa080fcb9b8241de65b6ea1af7f01e1f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isFoundational", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__989057d95fb31464ad5ba4a7ded9c8906dea6100782c229fc2c11ce88e617ca7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentUuid")
    def parent_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentUuid"))

    @parent_uuid.setter
    def parent_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1270d4585206c3294dfdf353deaff11ecd4bf0efc8c3b980508405fa3d6441fc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__279a0002ca549f1c25cbe9c05b475ee9c47c3a01938972691a791f2eac6f1516)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c37312500d12027e6332c200816f7e1a27c155d00925b168097577389b13d3e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uploadComplete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a85658c963df639e089d3d8c75bc223142d35daba6bda74cd1fa6b0f985bed4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usecases")
    def usecases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usecases"))

    @usecases.setter
    def usecases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f7bdcbbdefa0205c7c665ee0974ece1dfa105977605859ca3fc1f77d14b9d4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usecases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModel]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModel]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModel]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f5e56dd4bd900d153735093757c50cd9b7d7c1ca37e573c7f645386a58a5649)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelVersions",
    jsii_struct_bases=[],
    name_mapping={"major": "major", "minor": "minor", "patch": "patch"},
)
class DataDigitaloceanGenaiAgentModelVersions:
    def __init__(
        self,
        *,
        major: typing.Optional[jsii.Number] = None,
        minor: typing.Optional[jsii.Number] = None,
        patch: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param major: Major version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#major DataDigitaloceanGenaiAgent#major}
        :param minor: Minor version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#minor DataDigitaloceanGenaiAgent#minor}
        :param patch: Patch version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#patch DataDigitaloceanGenaiAgent#patch}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__43983929b34f5507091fad6169c1285d31f5958c85bef526511392793853554b)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#major DataDigitaloceanGenaiAgent#major}
        '''
        result = self._values.get("major")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minor(self) -> typing.Optional[jsii.Number]:
        '''Minor version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#minor DataDigitaloceanGenaiAgent#minor}
        '''
        result = self._values.get("minor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def patch(self) -> typing.Optional[jsii.Number]:
        '''Patch version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#patch DataDigitaloceanGenaiAgent#patch}
        '''
        result = self._values.get("patch")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentModelVersions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentModelVersionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelVersionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__008585ae03738eb278feabf9c189063b174caf2f1293eb4badcadd7b20087b20)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentModelVersionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1042b51bc3b5ebd1b1c3cca6c419e9fe5ed044a11dc43e1d031af157ddfac61c)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentModelVersionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aab68abb02dfe0e13183b9372cbd6efb02ecedd4ef755f6b415acf60df7630a1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__058df50f09bb1def2380e84ae6a839c8cba88bbba1ca6c027a6ac3e0f62a458c)
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
            type_hints = typing.get_type_hints(_typecheckingstub__167d5592965508c1f574c0aa2df9fbb4cff170b9e502cbbf39e9c873558cf3f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelVersions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelVersions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelVersions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2ac53bfd7e719708ab19800e60772b970f8eb4d22c85e1b47b6656c0f38d6364)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentModelVersionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentModelVersionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__19195bde706988ba4c6f22cfaa0bca68b4b2b0ab9507843e8e9a25f4be376bc9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__dc71a491aeb5b216f7a2a1b420d7117377d19d954c8029a170b220428ed3a212)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "major", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minor")
    def minor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minor"))

    @minor.setter
    def minor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__badf8ee9ca0618d51ab73d6bda3bed2ecea9fd4e21f3140b2ff778faffc194c6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="patch")
    def patch(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "patch"))

    @patch.setter
    def patch(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b639566c48e58cb5e42aaaa3b0892d89a316aa75dc136bc28576da9386e2fc9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "patch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelVersions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelVersions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelVersions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b5add1c9fe26ca3ee49dd6418b154e9141a549451cf68c36c48f8b22481a40a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentOpenAiApiKey",
    jsii_struct_bases=[],
    name_mapping={"api_key": "apiKey"},
)
class DataDigitaloceanGenaiAgentOpenAiApiKey:
    def __init__(self, *, api_key: typing.Optional[builtins.str] = None) -> None:
        '''
        :param api_key: OpenAI API Key. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key DataDigitaloceanGenaiAgent#api_key}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1e2f8fb006a932d3d0c6ba8c2120a5b0e590c9550f6688eac867918a0d88c016)
            check_type(argname="argument api_key", value=api_key, expected_type=type_hints["api_key"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if api_key is not None:
            self._values["api_key"] = api_key

    @builtins.property
    def api_key(self) -> typing.Optional[builtins.str]:
        '''OpenAI API Key.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#api_key DataDigitaloceanGenaiAgent#api_key}
        '''
        result = self._values.get("api_key")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentOpenAiApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentOpenAiApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentOpenAiApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ffd868c05a1d5f08086ed0715330716f6c428bf922a52090675702a906e69b53)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentOpenAiApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__77edc5c1aaa3587aaa6cded0418282279ae7d21b7d9621d234eea96dede96285)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentOpenAiApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9595c393cf1b9d163d3fc8aa59711a0c88f829d610d7771f4fa9202c1aac2957)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a07b50a2b845657d4249648a90a4a28bd6824c0367718a8b6c5b3c8d4d412f2d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__257cd214ea2c0999eb7300da79cb0fa107cd93709cea8a4ef5857ba3f0cc94f1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentOpenAiApiKey]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentOpenAiApiKey]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentOpenAiApiKey]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__92d8e6d25c5aee84d5e935ff585bfe01549efc4c7921a2a6a64faa84cf3b8c5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentOpenAiApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentOpenAiApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__81dd448ef1dae9bb6dcdcdb36240a9ce90563fe425de011b329842911cccde9a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__e21d4159ed18814eeb8d6ea84f59f80795499918f4902bff75d451a9ec71d1f2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "apiKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentOpenAiApiKey]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentOpenAiApiKey]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentOpenAiApiKey]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2274617da0249e99cb79687a8f01d1ca4bba228a611ce947ee6b8560c286ac41)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgents",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgents:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgents(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__a5629abf5b489839d13c15e10912130ff1046d535c40c6df2cc30384838f5c12)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__22ba9993a501e970ae2cf371ee4007121e42a72c15d8f807af02509b97fdd8f1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ba7a27e49441a48b71d69b30706209ef88d0566ae346e8178cab9a057abe45c1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f3bace42fcbdb35057dcc36e3387f8db8ebf11be343e6865b59b7f73b1f9a8ab)
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
            type_hints = typing.get_type_hints(_typecheckingstub__4a5b243339e65f0b5a853a16c8b03fc257a6360fb6e24105167dc30a2609bf94)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__4fb94ced0b4377be7b8e70e563a1ec8d3d32052d510a7b2bae72bb45be09582e)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__34056c54427ae33d400b3c6cb1cb2b0be906e02d56a61d1a63dcc5b675bdd9c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__448874ddfca73d47d174bffda92f408a251b3377d5fe29239e0da89ce17083b9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97091c8c71315c037943e76f50408b9eea550cfdf654b5435e409d06a6aba538)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__360b51a497228f5b0b7270e07106f728401ba265d5ab9a8737434dbcab641198)
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
            type_hints = typing.get_type_hints(_typecheckingstub__54a6eddf0e600e23eda694fdfa9c8d67df487712c9c947b2d2fb3de7dc5aa43a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__db7432c8f264fb897623283dbbdd6b6929e512c84a49cc66d38c2ea60b56ea39)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d5642fe535156a12d82b583ae61731bbac5f521d1b5e1d85fdf0eeab8320ca9f)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="createdBy")
    def created_by(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdBy"))

    @builtins.property
    @jsii.member(jsii_name="deletedAt")
    def deleted_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "deletedAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="secretKey")
    def secret_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secretKey"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b1ab42618ff06b577b19c5f26a47704d29eb3177f3a1cfd229f001a117bcf0b3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsApiKeys",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgentsApiKeys:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgentsApiKeys(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentParentAgentsApiKeysList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsApiKeysList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__cdb3cad4c6d83b70c7994c2d1bb5172bbe503c68498deda293213bfb16cba0a8)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsApiKeysOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3169b879f184855c049f85c96cbe78f3af11249c2d8312973f335a06df754b46)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsApiKeysOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bd7950c4ec95c274e5c4a8e491bf014c398f1d92a8badd134a76e0fa47d437e)
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
            type_hints = typing.get_type_hints(_typecheckingstub__74cfafb97327ccc9015d7f2ab3373433c2d7adda471d824e932db203c78f05f6)
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
            type_hints = typing.get_type_hints(_typecheckingstub__3a330fb691c332ae5391d81eb276269b84c3ab47af39a5a0594eae2ea51249c7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsApiKeysOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsApiKeysOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__d9672fbbea52dfd528213d2a8903ead4705af859105fcf202cd9f4e38f11829d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="apiKey")
    def api_key(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "apiKey"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeys]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeys], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeys],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef064b2045c1cdc3cd7d46f87a30e0f919034c8e51eebd97f3040e7d6f998598)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsChatbot",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgentsChatbot:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgentsChatbot(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__9898f902484f5a4d1925f420e3efdaab0754f76521096138f02c48130111a317)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6a3f517c69aa0ed95288f94fa975e77d070ca27932469d30fb9aeda28aba33b2)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bda2a67360197f7f3be89a32648c207e984086417c6a2cd8ed0488eb6747f3b9)
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
            type_hints = typing.get_type_hints(_typecheckingstub__2e06eb87f0cb8f29993731fce2680018d3a9f2b2f504392f79cb343356394525)
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
            type_hints = typing.get_type_hints(_typecheckingstub__da458f6d22b8fd7efde6cdb4291815b8397fb671fd15068b5e77a5d37cb6c891)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5d8e5a57333bf3f543fb261b1a6bea465b2651fe87f9fa91e64183a6a4a8e4c2)
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
    ) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__51fdb10c7c7bcb5692f677e0d2f576a64e7215598b9937d4ae17bcdb3e84a3ae)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsChatbotList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsChatbotList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fdda80ab9c501ef1e2a1207b465bbd3b6f190f589cbfaa2f597478cd956496aa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsChatbotOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ee1e801c61de8b739a2d850b53402f93a5350ae976a9d1f9d3bea53f86c9e31)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsChatbotOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9d3e637daa66c707cfe3e296c784173b908f54e5e1f1100c2bc6830386d7f54a)
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
            type_hints = typing.get_type_hints(_typecheckingstub__c16c5d222f43aca09b781cb524994c1b0bbc0a51fcccc1b7e44f4d9f835b0716)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a6562a41da0ba900e48cbf85fe295b485e898da808da3d583d6b70f4ed645582)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsChatbotOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsChatbotOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2f393659e1a2ee5e1d0f72d97c71f81db271bccf5ea6388dd855703cf40f94c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="buttonBackgroundColor")
    def button_background_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "buttonBackgroundColor"))

    @builtins.property
    @jsii.member(jsii_name="logo")
    def logo(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logo"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="primaryColor")
    def primary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "primaryColor"))

    @builtins.property
    @jsii.member(jsii_name="secondaryColor")
    def secondary_color(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "secondaryColor"))

    @builtins.property
    @jsii.member(jsii_name="startingMessage")
    def starting_message(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "startingMessage"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbot]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbot], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbot],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c600ed91f86c6ac737a7ee80e0069613003c0961d83fd4d2448f6e602b36efee)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsDeployment",
    jsii_struct_bases=[],
    name_mapping={},
)
class DataDigitaloceanGenaiAgentParentAgentsDeployment:
    def __init__(self) -> None:
        self._values: typing.Dict[builtins.str, typing.Any] = {}

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentParentAgentsDeployment(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentParentAgentsDeploymentList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsDeploymentList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__046e4ffbdacb82ce7f851d94b3a1121fe8fe870ff3a941876beeaa613af79a5b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsDeploymentOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d97072d783bc72f07d09766a671f2ab44c56327f88245cf80746b9409fb2126)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsDeploymentOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__850b48f3477a9ff77627c0d8550c9e44bc3850affd9e3ea37e32145781382818)
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
            type_hints = typing.get_type_hints(_typecheckingstub__21182c0d8171a8fde8d7eef3e487dfe31fd50403abece381fd3eda76ee4761dc)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a8aaf20015c613653f816532bdeb4ad8d3e4f9101b209d51360b5e68292e4da0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsDeploymentOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsDeploymentOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__5bac2844ca92f38988c7dee70c2ebbb50b8afcc818f5f5f15b3994c96c0570f1)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="createdAt")
    def created_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "createdAt"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="status")
    def status(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "status"))

    @builtins.property
    @jsii.member(jsii_name="updatedAt")
    def updated_at(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "updatedAt"))

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @builtins.property
    @jsii.member(jsii_name="visibility")
    def visibility(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "visibility"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgentsDeployment]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgentsDeployment], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsDeployment],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95fa3e6956aee6b7d8138820ff87f6ccc48fc6cca620a1c4ffcced55e3e929c4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3bc8648b400663ac3f6a3ad4c67f314d53ae5dc3a47d06bd4bd6ed9a4836e286)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentParentAgentsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__00cc14fb44b6dea0c6a9d26390e5f8fd033af97af4e042f1781b3272b85b101a)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentParentAgentsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4f41fe0d29ea0ea4c0bacc7b64341efcdc2ab1965a0024b79bcef3632e3a1842)
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
            type_hints = typing.get_type_hints(_typecheckingstub__cbc081995116954b33d045034393125b3125a7b3dc83597743aaef551cbe0ab1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__f2f5fffc993a3fb0308819c8b128f1398d5e1d7b074237fe2a878450713356cf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentParentAgentsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentParentAgentsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ed75d71aedaccb4e4546af2403b1f3b7abd585f0cb0072ffe6b2fea32193706c)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @builtins.property
    @jsii.member(jsii_name="agentId")
    def agent_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "agentId"))

    @builtins.property
    @jsii.member(jsii_name="anthropicApiKey")
    def anthropic_api_key(
        self,
    ) -> DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyList:
        return typing.cast(DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyList, jsii.get(self, "anthropicApiKey"))

    @builtins.property
    @jsii.member(jsii_name="apiKeyInfos")
    def api_key_infos(self) -> DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosList:
        return typing.cast(DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosList, jsii.get(self, "apiKeyInfos"))

    @builtins.property
    @jsii.member(jsii_name="apiKeys")
    def api_keys(self) -> DataDigitaloceanGenaiAgentParentAgentsApiKeysList:
        return typing.cast(DataDigitaloceanGenaiAgentParentAgentsApiKeysList, jsii.get(self, "apiKeys"))

    @builtins.property
    @jsii.member(jsii_name="chatbot")
    def chatbot(self) -> DataDigitaloceanGenaiAgentParentAgentsChatbotList:
        return typing.cast(DataDigitaloceanGenaiAgentParentAgentsChatbotList, jsii.get(self, "chatbot"))

    @builtins.property
    @jsii.member(jsii_name="chatbotIdentifiers")
    def chatbot_identifiers(
        self,
    ) -> DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersList:
        return typing.cast(DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersList, jsii.get(self, "chatbotIdentifiers"))

    @builtins.property
    @jsii.member(jsii_name="deployment")
    def deployment(self) -> DataDigitaloceanGenaiAgentParentAgentsDeploymentList:
        return typing.cast(DataDigitaloceanGenaiAgentParentAgentsDeploymentList, jsii.get(self, "deployment"))

    @builtins.property
    @jsii.member(jsii_name="description")
    def description(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "description"))

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @builtins.property
    @jsii.member(jsii_name="modelUuid")
    def model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "modelUuid"))

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DataDigitaloceanGenaiAgentParentAgents]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentParentAgents], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentParentAgents],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18e559fcbca99d4df2913e016de58eb73cf9823b7b7a269b0ca494108a97e651)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplate",
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
class DataDigitaloceanGenaiAgentTemplate:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        instruction: typing.Optional[builtins.str] = None,
        k: typing.Optional[jsii.Number] = None,
        knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplateKnowledgeBases", typing.Dict[builtins.str, typing.Any]]]]] = None,
        max_tokens: typing.Optional[jsii.Number] = None,
        model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplateModel", typing.Dict[builtins.str, typing.Any]]]]] = None,
        name: typing.Optional[builtins.str] = None,
        temperature: typing.Optional[jsii.Number] = None,
        top_p: typing.Optional[jsii.Number] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Description of the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param instruction: Instruction for the Agent. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#instruction DataDigitaloceanGenaiAgent#instruction}
        :param k: K value for the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#k DataDigitaloceanGenaiAgent#k}
        :param knowledge_bases: knowledge_bases block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#knowledge_bases DataDigitaloceanGenaiAgent#knowledge_bases}
        :param max_tokens: Maximum tokens allowed. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#max_tokens DataDigitaloceanGenaiAgent#max_tokens}
        :param model: model block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#model DataDigitaloceanGenaiAgent#model}
        :param name: Name of the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param temperature: Agent temperature setting. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#temperature DataDigitaloceanGenaiAgent#temperature}
        :param top_p: Top P sampling parameter. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#top_p DataDigitaloceanGenaiAgent#top_p}
        :param uuid: uuid of the Agent Template. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88b8d0a05edcf0871a6e59f9acc4d9517991821ccc328c01ea14c8171065b952)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def instruction(self) -> typing.Optional[builtins.str]:
        '''Instruction for the Agent.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#instruction DataDigitaloceanGenaiAgent#instruction}
        '''
        result = self._values.get("instruction")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def k(self) -> typing.Optional[jsii.Number]:
        '''K value for the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#k DataDigitaloceanGenaiAgent#k}
        '''
        result = self._values.get("k")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def knowledge_bases(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateKnowledgeBases"]]]:
        '''knowledge_bases block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#knowledge_bases DataDigitaloceanGenaiAgent#knowledge_bases}
        '''
        result = self._values.get("knowledge_bases")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateKnowledgeBases"]]], result)

    @builtins.property
    def max_tokens(self) -> typing.Optional[jsii.Number]:
        '''Maximum tokens allowed.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#max_tokens DataDigitaloceanGenaiAgent#max_tokens}
        '''
        result = self._values.get("max_tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def model(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModel"]]]:
        '''model block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#model DataDigitaloceanGenaiAgent#model}
        '''
        result = self._values.get("model")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModel"]]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def temperature(self) -> typing.Optional[jsii.Number]:
        '''Agent temperature setting.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#temperature DataDigitaloceanGenaiAgent#temperature}
        '''
        result = self._values.get("temperature")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def top_p(self) -> typing.Optional[jsii.Number]:
        '''Top P sampling parameter.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#top_p DataDigitaloceanGenaiAgent#top_p}
        '''
        result = self._values.get("top_p")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''uuid of the Agent Template.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentTemplate(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateKnowledgeBases",
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
class DataDigitaloceanGenaiAgentTemplateKnowledgeBases:
    def __init__(
        self,
        *,
        database_id: typing.Optional[builtins.str] = None,
        embedding_model_uuid: typing.Optional[builtins.str] = None,
        is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        last_indexing_job: typing.Optional[typing.Union["DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob", typing.Dict[builtins.str, typing.Any]]] = None,
        name: typing.Optional[builtins.str] = None,
        project_id: typing.Optional[builtins.str] = None,
        region: typing.Optional[builtins.str] = None,
        tags: typing.Optional[typing.Sequence[builtins.str]] = None,
        user_id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param database_id: Database ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#database_id DataDigitaloceanGenaiAgent#database_id}
        :param embedding_model_uuid: Embedding model UUID for the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#embedding_model_uuid DataDigitaloceanGenaiAgent#embedding_model_uuid}
        :param is_public: Indicates if the Knowledge Base is public. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_public DataDigitaloceanGenaiAgent#is_public}
        :param last_indexing_job: last_indexing_job block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#last_indexing_job DataDigitaloceanGenaiAgent#last_indexing_job}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param project_id: Project ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#project_id DataDigitaloceanGenaiAgent#project_id}
        :param region: Region of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#region DataDigitaloceanGenaiAgent#region}
        :param tags: List of tags. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        :param user_id: User ID of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        '''
        if isinstance(last_indexing_job, dict):
            last_indexing_job = DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob(**last_indexing_job)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a0e890a7ae8d8a64b64d80a51cb963caa10294cd47c5336989daab186f0b7aa8)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#database_id DataDigitaloceanGenaiAgent#database_id}
        '''
        result = self._values.get("database_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def embedding_model_uuid(self) -> typing.Optional[builtins.str]:
        '''Embedding model UUID for the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#embedding_model_uuid DataDigitaloceanGenaiAgent#embedding_model_uuid}
        '''
        result = self._values.get("embedding_model_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_public(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Knowledge Base is public.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_public DataDigitaloceanGenaiAgent#is_public}
        '''
        result = self._values.get("is_public")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def last_indexing_job(
        self,
    ) -> typing.Optional["DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob"]:
        '''last_indexing_job block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#last_indexing_job DataDigitaloceanGenaiAgent#last_indexing_job}
        '''
        result = self._values.get("last_indexing_job")
        return typing.cast(typing.Optional["DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob"], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def project_id(self) -> typing.Optional[builtins.str]:
        '''Project ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#project_id DataDigitaloceanGenaiAgent#project_id}
        '''
        result = self._values.get("project_id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def region(self) -> typing.Optional[builtins.str]:
        '''Region of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#region DataDigitaloceanGenaiAgent#region}
        '''
        result = self._values.get("region")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of tags.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tags DataDigitaloceanGenaiAgent#tags}
        '''
        result = self._values.get("tags")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def user_id(self) -> typing.Optional[builtins.str]:
        '''User ID of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#user_id DataDigitaloceanGenaiAgent#user_id}
        '''
        result = self._values.get("user_id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentTemplateKnowledgeBases(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob",
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
class DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob:
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#completed_datasources DataDigitaloceanGenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#data_source_uuids DataDigitaloceanGenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#phase DataDigitaloceanGenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tokens DataDigitaloceanGenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#total_datasources DataDigitaloceanGenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7977b483c22deb2a599cd6d06652684ca8bca68612fadbea3613a5a9d8e80cc5)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#completed_datasources DataDigitaloceanGenaiAgent#completed_datasources}
        '''
        result = self._values.get("completed_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def data_source_uuids(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Datasource UUIDs for the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#data_source_uuids DataDigitaloceanGenaiAgent#data_source_uuids}
        '''
        result = self._values.get("data_source_uuids")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def phase(self) -> typing.Optional[builtins.str]:
        '''Phase of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#phase DataDigitaloceanGenaiAgent#phase}
        '''
        result = self._values.get("phase")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def tokens(self) -> typing.Optional[jsii.Number]:
        '''Number of tokens processed in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tokens DataDigitaloceanGenaiAgent#tokens}
        '''
        result = self._values.get("tokens")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def total_datasources(self) -> typing.Optional[jsii.Number]:
        '''Total number of datasources in the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#total_datasources DataDigitaloceanGenaiAgent#total_datasources}
        '''
        result = self._values.get("total_datasources")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID  of the last indexing job.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__72e9db58e3c41fc1575f1a7a6ae177e571d99e37d09deb60807ec3b996b9ee8b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__95e5dce13003a1169f73e587663c2af5dc94f0b3aeb58effe0057a132cb9a5cd)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "completedDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="dataSourceUuids")
    def data_source_uuids(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "dataSourceUuids"))

    @data_source_uuids.setter
    def data_source_uuids(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__037003fb6cdffb1d54b38f95ca78e6633e3ea2f98f082e518d80b6ab36aac3ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "dataSourceUuids", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="phase")
    def phase(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "phase"))

    @phase.setter
    def phase(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1599328b8e653fa617bb1f30e45254a2d9b67a1b68de292491f401edd6b19a65)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "phase", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tokens")
    def tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tokens"))

    @tokens.setter
    def tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__be8ea30b0a32e410e4f648be2d370c032ea81e29530a5cbdda395796de24a4aa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="totalDatasources")
    def total_datasources(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "totalDatasources"))

    @total_datasources.setter
    def total_datasources(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__97b502906d548e6488262ed3291d7f89d4543f7dcd381a1ded672cb269f6a7f3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "totalDatasources", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f98ce4e05ccb957c442afc6781cf5d08279d44badb059bd472a1bb1d91987a9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__069c1bc3b103a2ff863f5c7d565962ba244dbceb70180fcc11d7c4e2cc4d3647)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateKnowledgeBasesList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateKnowledgeBasesList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__3c12d2fb76a871aa48ae2c0859164c29ed4e36062e79df6f0d6dc286b84602dc)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentTemplateKnowledgeBasesOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3c4d5509eacc37b5421ea527b614c86241266c45cda756e7fd1449b60017e254)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentTemplateKnowledgeBasesOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b856dfd74d67fcb57fed7b7f866d236dbf85bf4ef106bfb2ed85f5da77a7099d)
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
            type_hints = typing.get_type_hints(_typecheckingstub__d4f93429f919862f0f0ee8be117d68e77659f79798a1dc43d309ffef31d6fccf)
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
            type_hints = typing.get_type_hints(_typecheckingstub__1d23aebeeb063ee53586ae47bf9cf9739f041e9fff522539d32a4706990e6f16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__193c05d2e03aee71caa35d16357a00175e07eddfdc8810db3aad8df11afb2da9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateKnowledgeBasesOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateKnowledgeBasesOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fb4ed687cda41f445c4a09a99bdb4c63852ead32d0f387582990af9a00987298)
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
        :param completed_datasources: Number of completed datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#completed_datasources DataDigitaloceanGenaiAgent#completed_datasources}
        :param data_source_uuids: Datasource UUIDs for the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#data_source_uuids DataDigitaloceanGenaiAgent#data_source_uuids}
        :param phase: Phase of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#phase DataDigitaloceanGenaiAgent#phase}
        :param tokens: Number of tokens processed in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#tokens DataDigitaloceanGenaiAgent#tokens}
        :param total_datasources: Total number of datasources in the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#total_datasources DataDigitaloceanGenaiAgent#total_datasources}
        :param uuid: UUID of the last indexing job. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        value = DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob(
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
    ) -> DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference:
        return typing.cast(DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference, jsii.get(self, "lastIndexingJob"))

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
    ) -> typing.Optional[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob]:
        return typing.cast(typing.Optional[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob], jsii.get(self, "lastIndexingJobInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__12bcf6837d39801ee1ae872cc2505f3ffbe81848d319349c7ccd7c04db7e6dc1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "databaseId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="embeddingModelUuid")
    def embedding_model_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "embeddingModelUuid"))

    @embedding_model_uuid.setter
    def embedding_model_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13c016c6aa68cd59c0977795b9afc83ddce92ba5cbd18643605f8f34f6559675)
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
            type_hints = typing.get_type_hints(_typecheckingstub__05b18026e4621978786ae1d696dcc72e6b44915f7aa5c7475a70318a99a2f3f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isPublic", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d2f7eb0a7c235c7989d3d0486d51aae86cfc15e790ee9b86deddbf6c2565b9d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="projectId")
    def project_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "projectId"))

    @project_id.setter
    def project_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__350d0419b144d6a5acfbb9c8d6307df2edf138850313837a9f5f7e836c24ad8e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "projectId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="region")
    def region(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "region"))

    @region.setter
    def region(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__164b398d4fa7991d1a2da076b5134c5ea6f58969605bc2c41196631ef88b64f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "region", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tags")
    def tags(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "tags"))

    @tags.setter
    def tags(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__33b2d7fef5915d1ffe5e3948d2a3692e36f2a281afbd8ce8144b4e7d5480fd3c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tags", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="userId")
    def user_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "userId"))

    @user_id.setter
    def user_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__81ea278d15818193efa60e7023b80d3f3b908e01677a016b3f08d1477765b81f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "userId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateKnowledgeBases]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateKnowledgeBases]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__88009895492d571e6d337167feb981215edd14f084c94e895dadefe973ca3a5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__b211ae5c9df7fa7ae62b3b13b56d992153ce338da4e1a52a71d160a562437e95)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentTemplateOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7d9691957c17bde83ef0019776674478abf5ba9f350f8933e5d34fad56524ec1)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentTemplateOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cb77712d4cc63cc90b292160932bf74d3f515e72b25128db2aeeb73e35f0a260)
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
            type_hints = typing.get_type_hints(_typecheckingstub__52b1b2330eb2845a119364b4f5a0155307c0914da8481080903cefa64d29da90)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fc88a976b214dc2be4e9c71e82359050eddad75bacb36ba3bc718656321a4e40)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplate]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplate]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplate]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__80225fcfc308a2f8dd5d8dca6b50ef4b36639dc971729312455831ba24811460)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModel",
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
class DataDigitaloceanGenaiAgentTemplateModel:
    def __init__(
        self,
        *,
        agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplateModelAgreement", typing.Dict[builtins.str, typing.Any]]]]] = None,
        inference_name: typing.Optional[builtins.str] = None,
        inference_version: typing.Optional[builtins.str] = None,
        is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        name: typing.Optional[builtins.str] = None,
        parent_uuid: typing.Optional[builtins.str] = None,
        provider: typing.Optional[builtins.str] = None,
        upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        url: typing.Optional[builtins.str] = None,
        usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
        versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplateModelVersions", typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''
        :param agreement: agreement block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agreement DataDigitaloceanGenaiAgent#agreement}
        :param inference_name: Inference name of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_name DataDigitaloceanGenaiAgent#inference_name}
        :param inference_version: Infernce version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_version DataDigitaloceanGenaiAgent#inference_version}
        :param is_foundational: Indicates if the Model Base is foundational. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_foundational DataDigitaloceanGenaiAgent#is_foundational}
        :param name: Name of the Knowledge Base. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param parent_uuid: Parent UUID of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#parent_uuid DataDigitaloceanGenaiAgent#parent_uuid}
        :param provider: Provider of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#provider DataDigitaloceanGenaiAgent#provider}
        :param upload_complete: Indicates if the Model upload is complete. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#upload_complete DataDigitaloceanGenaiAgent#upload_complete}
        :param url: URL of the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param usecases: List of Usecases for the Model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#usecases DataDigitaloceanGenaiAgent#usecases}
        :param versions: versions block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#versions DataDigitaloceanGenaiAgent#versions}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8dd0fbba5b152dba73c6dc32366684d82ef272b60547516f5cd272c7e03d0046)
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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModelAgreement"]]]:
        '''agreement block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#agreement DataDigitaloceanGenaiAgent#agreement}
        '''
        result = self._values.get("agreement")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModelAgreement"]]], result)

    @builtins.property
    def inference_name(self) -> typing.Optional[builtins.str]:
        '''Inference name of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_name DataDigitaloceanGenaiAgent#inference_name}
        '''
        result = self._values.get("inference_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def inference_version(self) -> typing.Optional[builtins.str]:
        '''Infernce version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#inference_version DataDigitaloceanGenaiAgent#inference_version}
        '''
        result = self._values.get("inference_version")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def is_foundational(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model Base is foundational.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#is_foundational DataDigitaloceanGenaiAgent#is_foundational}
        '''
        result = self._values.get("is_foundational")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the Knowledge Base.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def parent_uuid(self) -> typing.Optional[builtins.str]:
        '''Parent UUID of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#parent_uuid DataDigitaloceanGenaiAgent#parent_uuid}
        '''
        result = self._values.get("parent_uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def provider(self) -> typing.Optional[builtins.str]:
        '''Provider of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#provider DataDigitaloceanGenaiAgent#provider}
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def upload_complete(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Indicates if the Model upload is complete.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#upload_complete DataDigitaloceanGenaiAgent#upload_complete}
        '''
        result = self._values.get("upload_complete")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def usecases(self) -> typing.Optional[typing.List[builtins.str]]:
        '''List of Usecases for the Model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#usecases DataDigitaloceanGenaiAgent#usecases}
        '''
        result = self._values.get("usecases")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def versions(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModelVersions"]]]:
        '''versions block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#versions DataDigitaloceanGenaiAgent#versions}
        '''
        result = self._values.get("versions")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModelVersions"]]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentTemplateModel(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelAgreement",
    jsii_struct_bases=[],
    name_mapping={
        "description": "description",
        "name": "name",
        "url": "url",
        "uuid": "uuid",
    },
)
class DataDigitaloceanGenaiAgentTemplateModelAgreement:
    def __init__(
        self,
        *,
        description: typing.Optional[builtins.str] = None,
        name: typing.Optional[builtins.str] = None,
        url: typing.Optional[builtins.str] = None,
        uuid: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param description: Description of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        :param name: Name of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        :param url: URL of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        :param uuid: UUID of the agreement. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__18221e74a4815b138be011384ccf90e203bb5a2f2d75c1534b7edc4d1bf5fe5b)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#description DataDigitaloceanGenaiAgent#description}
        '''
        result = self._values.get("description")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        '''Name of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#name DataDigitaloceanGenaiAgent#name}
        '''
        result = self._values.get("name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def url(self) -> typing.Optional[builtins.str]:
        '''URL of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#url DataDigitaloceanGenaiAgent#url}
        '''
        result = self._values.get("url")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def uuid(self) -> typing.Optional[builtins.str]:
        '''UUID of the agreement.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#uuid DataDigitaloceanGenaiAgent#uuid}
        '''
        result = self._values.get("uuid")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentTemplateModelAgreement(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentTemplateModelAgreementList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelAgreementList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__169b827f297a0053f89c5254777997b5ae7656f26b304b0a90dc81d6a0ea63b2)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentTemplateModelAgreementOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07c898497413ff19c5389d5b1131cd5e519b4c045559d42df86bfaa20cccd1fe)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentTemplateModelAgreementOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4812bf40a1558809ad6c497458072e90eb65b801c027a71471b2adab8b2fa120)
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
            type_hints = typing.get_type_hints(_typecheckingstub__a271297faee1bf54e7e512882a50ca403824e2106ac7753089cf5cef14f23487)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b14cc6212f2da99c91f4408e276fff825dabaf5df85b9742105d8cc1e0c3a7d1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelAgreement]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelAgreement]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__01fe754cbd4728fae6eaa0137154b33b0bb1266c4d9e5646048d94fcacf22086)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateModelAgreementOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelAgreementOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__58e80dc00a751dd1284e0bbb9239a30f5fae35ece964a40ee119117d89470418)
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
            type_hints = typing.get_type_hints(_typecheckingstub__bf3df6d41225317a42c496ec9621a0e8d7f126db7578a3a45a62f282fc09a6ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bb308d75b895ca3521dfae4c16a94f464c1a472c2e3bcdf6bfdf57b866337fe)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e76b66a9aaa6f61d28e0a67b40fc37e3b44cff7b0f5b536b3f8a4449e70949f9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70d9eebb8998debf5aed26252f1f85e05c448280630064e2e7d2440dd7f72643)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelAgreement]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelAgreement]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelAgreement]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0d564c9c30f6fe9094b142bc3b07f106d084a86a6606498aae7ae9d24ddc3d58)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateModelList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__ef43765b810d00f2b033e1499369e5fc1bbe987fd95a617b6f5aa8fce276a149)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentTemplateModelOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30bbbed0f1e28522f4791c4eb3540023cdc26b927f590f1a39da077fdf33ae5f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentTemplateModelOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6c3681bf31480625ec93ed4e2fe60a58552ce8ea0a2f5ea4c94f55a3ea422ee1)
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
            type_hints = typing.get_type_hints(_typecheckingstub__9768070a0c0ab66bd843df7e0c9db5fde758cd9ab1f98991575730378a4b0915)
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
            type_hints = typing.get_type_hints(_typecheckingstub__95f208a80ff6210751e3e297269526250272073a9dd3d7bf1dddb861db310f79)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModel]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModel]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__07223c8a2d6a67d3a3f4f73abd316c4d6ed0a144e5b85a17e314cdbbe8fa1a16)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateModelOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__2db6bef5e1858e430c9ab3a766d72bee5b724606fb059382275458e1b1b2305d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putAgreement")
    def put_agreement(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d8329a0768c764d6a7ad1dc22b87a62c2ece19c4ee02ac80cb90224487c0dfca)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putAgreement", [value]))

    @jsii.member(jsii_name="putVersions")
    def put_versions(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DataDigitaloceanGenaiAgentTemplateModelVersions", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0ae93433c550ed3244a89f94042a58ecdffb3a17638b824a1791f8635174d567)
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
    def agreement(self) -> DataDigitaloceanGenaiAgentTemplateModelAgreementList:
        return typing.cast(DataDigitaloceanGenaiAgentTemplateModelAgreementList, jsii.get(self, "agreement"))

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
    def versions(self) -> "DataDigitaloceanGenaiAgentTemplateModelVersionsList":
        return typing.cast("DataDigitaloceanGenaiAgentTemplateModelVersionsList", jsii.get(self, "versions"))

    @builtins.property
    @jsii.member(jsii_name="agreementInput")
    def agreement_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelAgreement]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelAgreement]]], jsii.get(self, "agreementInput"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModelVersions"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DataDigitaloceanGenaiAgentTemplateModelVersions"]]], jsii.get(self, "versionsInput"))

    @builtins.property
    @jsii.member(jsii_name="inferenceName")
    def inference_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceName"))

    @inference_name.setter
    def inference_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1517939790064bf4614a4e344eaba95b55069140954564114ea834376f151285)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "inferenceName", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="inferenceVersion")
    def inference_version(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "inferenceVersion"))

    @inference_version.setter
    def inference_version(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__24161f201f47f57057efba551a0e7fe90140221c49b3006b23e311225eda4e3b)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7f79ea212cd49c685adf1abd8369ca95652aed3834b27db0bc86c65376306541)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "isFoundational", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2d95f3447b6f750bef4885300aeb86836d60635e0c59aee4158b6efb8a645d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="parentUuid")
    def parent_uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "parentUuid"))

    @parent_uuid.setter
    def parent_uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__84e2b66bcf386fd53cb35d619f55ca04e8c34717ffa35fbd01ce83fb01927e6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "parentUuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__eefb2f2771bb1431c2fec0fad345164878b5ce3ccb1548eb4ab9514eba39737f)
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
            type_hints = typing.get_type_hints(_typecheckingstub__32b6eb3172bd09e14f11aa62b1da0154aab369dfaa466bc576a530f78c3e93a4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uploadComplete", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="url")
    def url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "url"))

    @url.setter
    def url(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cfbc695330510d60ed8544f783faedc7afa7bc3e8e8cf6a42d2901c6977f170d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "url", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="usecases")
    def usecases(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "usecases"))

    @usecases.setter
    def usecases(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7a4bcf701a8ce4260fda61a5c54b4daf64ca41fe2e89aed9185f067e0e21310c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "usecases", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModel]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModel]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModel]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__82f7bfb1ff66f537bd2dc844883b88f07caa00be631d0eddabc71e82c8c264dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelVersions",
    jsii_struct_bases=[],
    name_mapping={"major": "major", "minor": "minor", "patch": "patch"},
)
class DataDigitaloceanGenaiAgentTemplateModelVersions:
    def __init__(
        self,
        *,
        major: typing.Optional[jsii.Number] = None,
        minor: typing.Optional[jsii.Number] = None,
        patch: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param major: Major version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#major DataDigitaloceanGenaiAgent#major}
        :param minor: Minor version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#minor DataDigitaloceanGenaiAgent#minor}
        :param patch: Patch version of the model. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#patch DataDigitaloceanGenaiAgent#patch}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1fd62ba9e7e3e796386364d76105ab66f833b005c447882ff23d13045ad16d42)
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

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#major DataDigitaloceanGenaiAgent#major}
        '''
        result = self._values.get("major")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def minor(self) -> typing.Optional[jsii.Number]:
        '''Minor version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#minor DataDigitaloceanGenaiAgent#minor}
        '''
        result = self._values.get("minor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def patch(self) -> typing.Optional[jsii.Number]:
        '''Patch version of the model.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/data-sources/genai_agent#patch DataDigitaloceanGenaiAgent#patch}
        '''
        result = self._values.get("patch")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DataDigitaloceanGenaiAgentTemplateModelVersions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DataDigitaloceanGenaiAgentTemplateModelVersionsList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelVersionsList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__c677b5ed27f52827b9a1f973e4dbaf3a8b9f65f7f63732e687f4047423242c0b)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DataDigitaloceanGenaiAgentTemplateModelVersionsOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__582d71d5ca8b25454e964a3af3f82aa8c52b17bb5791a6767771883b4227ae36)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DataDigitaloceanGenaiAgentTemplateModelVersionsOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7bab4f6f644f97546f1d4653da27798036ec33e2d6017a75283e271057c8fa18)
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
            type_hints = typing.get_type_hints(_typecheckingstub__31520f72acd7f8d494f9d4cbaefd50346934a1d211acc62108a95b38f9a06407)
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
            type_hints = typing.get_type_hints(_typecheckingstub__7d0ff90b2b470732daedf1d59361fc43948663c332bc434ed5da3580738422dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelVersions]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelVersions]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelVersions]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__0b85e712a3f1cef7f4f8a7164fc259ed7466cca748aa6cad3be96aa15958d7b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateModelVersionsOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateModelVersionsOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa8c32242efabbb80a260b0c47f259aa9f23fd55ddab71a6258c00e1c7f6d5b2)
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
            type_hints = typing.get_type_hints(_typecheckingstub__fa14e71bdbc18b1291042d25d3f55d926872d00bb5916162ab0011a7b9e50b8a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "major", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minor")
    def minor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minor"))

    @minor.setter
    def minor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b11a9dd881ffacae337b3d5319b986648dff963015faeedfd2537838841a402)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="patch")
    def patch(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "patch"))

    @patch.setter
    def patch(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6f1938873e5216cf95ac5b306e7167cca5cb50c6b95d3cdf2e538312cee75435)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "patch", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelVersions]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelVersions]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelVersions]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5b41faba11febaaea3f2dee1d69e634e0c568b0a127c624b429df1993a1431dc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DataDigitaloceanGenaiAgentTemplateOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.dataDigitaloceanGenaiAgent.DataDigitaloceanGenaiAgentTemplateOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__66f6f9f551336fc44a19e74b409cc55f97d836d0308e5d8ef194627fd7fcc628)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="putKnowledgeBases")
    def put_knowledge_bases(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__44acdd9e805d846fd9dc6a617094367f7e2e8846eef40690c45c6ad47deda9b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putKnowledgeBases", [value]))

    @jsii.member(jsii_name="putModel")
    def put_model(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModel, typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1ee9ea0374369552a9976ddb081d55a109655644e0746270a3bc6d1b7074ae44)
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
    def knowledge_bases(self) -> DataDigitaloceanGenaiAgentTemplateKnowledgeBasesList:
        return typing.cast(DataDigitaloceanGenaiAgentTemplateKnowledgeBasesList, jsii.get(self, "knowledgeBases"))

    @builtins.property
    @jsii.member(jsii_name="model")
    def model(self) -> DataDigitaloceanGenaiAgentTemplateModelList:
        return typing.cast(DataDigitaloceanGenaiAgentTemplateModelList, jsii.get(self, "model"))

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
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]], jsii.get(self, "knowledgeBasesInput"))

    @builtins.property
    @jsii.member(jsii_name="maxTokensInput")
    def max_tokens_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxTokensInput"))

    @builtins.property
    @jsii.member(jsii_name="modelInput")
    def model_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModel]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModel]]], jsii.get(self, "modelInput"))

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
            type_hints = typing.get_type_hints(_typecheckingstub__2c08191ac6d98af88378cabc1ebb8b03d72172c44c87a4046690f9fd53d916e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "description", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="instruction")
    def instruction(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "instruction"))

    @instruction.setter
    def instruction(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef3f5353430b5c3decc1e2a25c60eec212cfdf9a24b17535b7f741716ae2b0e7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "instruction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="k")
    def k(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "k"))

    @k.setter
    def k(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8ca263b5217fb792f5162bb4047ed073d4390254515ee48b3c091c3dfd3753d2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "k", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxTokens")
    def max_tokens(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxTokens"))

    @max_tokens.setter
    def max_tokens(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7b26b496dcb3f70a0b70beb28ba07c55aa3041be79c9067a15c1a4a30d497901)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxTokens", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="name")
    def name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "name"))

    @name.setter
    def name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ecedccf68946d2197dc1cea96f615513805c04aae69418298419688134b6f421)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "name", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="temperature")
    def temperature(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "temperature"))

    @temperature.setter
    def temperature(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a802e36c42b805d1125c883708e534bafdad5f3236d8354f6f1cab411294890)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "temperature", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="topP")
    def top_p(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "topP"))

    @top_p.setter
    def top_p(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__10fadab782d7e91bf188c084ba70a99a93075d2519c02664d7257c511603d730)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "topP", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="uuid")
    def uuid(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "uuid"))

    @uuid.setter
    def uuid(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8c9180a79000ae9e6099483807022687af260210c19c659d99ca52d188de8dbc)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "uuid", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplate]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplate]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplate]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2e01643598e03196f81e14ebc38773342d078ffdd2c080442136d24cd03b0284)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DataDigitaloceanGenaiAgent",
    "DataDigitaloceanGenaiAgentAgentGuardrail",
    "DataDigitaloceanGenaiAgentAgentGuardrailList",
    "DataDigitaloceanGenaiAgentAgentGuardrailOutputReference",
    "DataDigitaloceanGenaiAgentAnthropicApiKey",
    "DataDigitaloceanGenaiAgentAnthropicApiKeyList",
    "DataDigitaloceanGenaiAgentAnthropicApiKeyOutputReference",
    "DataDigitaloceanGenaiAgentApiKeyInfos",
    "DataDigitaloceanGenaiAgentApiKeyInfosList",
    "DataDigitaloceanGenaiAgentApiKeyInfosOutputReference",
    "DataDigitaloceanGenaiAgentApiKeys",
    "DataDigitaloceanGenaiAgentApiKeysList",
    "DataDigitaloceanGenaiAgentApiKeysOutputReference",
    "DataDigitaloceanGenaiAgentChatbot",
    "DataDigitaloceanGenaiAgentChatbotIdentifiers",
    "DataDigitaloceanGenaiAgentChatbotIdentifiersList",
    "DataDigitaloceanGenaiAgentChatbotIdentifiersOutputReference",
    "DataDigitaloceanGenaiAgentChatbotList",
    "DataDigitaloceanGenaiAgentChatbotOutputReference",
    "DataDigitaloceanGenaiAgentChildAgents",
    "DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey",
    "DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyList",
    "DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKeyOutputReference",
    "DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos",
    "DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosList",
    "DataDigitaloceanGenaiAgentChildAgentsApiKeyInfosOutputReference",
    "DataDigitaloceanGenaiAgentChildAgentsApiKeys",
    "DataDigitaloceanGenaiAgentChildAgentsApiKeysList",
    "DataDigitaloceanGenaiAgentChildAgentsApiKeysOutputReference",
    "DataDigitaloceanGenaiAgentChildAgentsChatbot",
    "DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers",
    "DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersList",
    "DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiersOutputReference",
    "DataDigitaloceanGenaiAgentChildAgentsChatbotList",
    "DataDigitaloceanGenaiAgentChildAgentsChatbotOutputReference",
    "DataDigitaloceanGenaiAgentChildAgentsDeployment",
    "DataDigitaloceanGenaiAgentChildAgentsDeploymentList",
    "DataDigitaloceanGenaiAgentChildAgentsDeploymentOutputReference",
    "DataDigitaloceanGenaiAgentChildAgentsList",
    "DataDigitaloceanGenaiAgentChildAgentsOutputReference",
    "DataDigitaloceanGenaiAgentConfig",
    "DataDigitaloceanGenaiAgentDeployment",
    "DataDigitaloceanGenaiAgentDeploymentList",
    "DataDigitaloceanGenaiAgentDeploymentOutputReference",
    "DataDigitaloceanGenaiAgentFunctions",
    "DataDigitaloceanGenaiAgentFunctionsList",
    "DataDigitaloceanGenaiAgentFunctionsOutputReference",
    "DataDigitaloceanGenaiAgentKnowledgeBases",
    "DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob",
    "DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJobOutputReference",
    "DataDigitaloceanGenaiAgentKnowledgeBasesList",
    "DataDigitaloceanGenaiAgentKnowledgeBasesOutputReference",
    "DataDigitaloceanGenaiAgentModel",
    "DataDigitaloceanGenaiAgentModelAgreement",
    "DataDigitaloceanGenaiAgentModelAgreementList",
    "DataDigitaloceanGenaiAgentModelAgreementOutputReference",
    "DataDigitaloceanGenaiAgentModelList",
    "DataDigitaloceanGenaiAgentModelOutputReference",
    "DataDigitaloceanGenaiAgentModelVersions",
    "DataDigitaloceanGenaiAgentModelVersionsList",
    "DataDigitaloceanGenaiAgentModelVersionsOutputReference",
    "DataDigitaloceanGenaiAgentOpenAiApiKey",
    "DataDigitaloceanGenaiAgentOpenAiApiKeyList",
    "DataDigitaloceanGenaiAgentOpenAiApiKeyOutputReference",
    "DataDigitaloceanGenaiAgentParentAgents",
    "DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey",
    "DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyList",
    "DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKeyOutputReference",
    "DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos",
    "DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosList",
    "DataDigitaloceanGenaiAgentParentAgentsApiKeyInfosOutputReference",
    "DataDigitaloceanGenaiAgentParentAgentsApiKeys",
    "DataDigitaloceanGenaiAgentParentAgentsApiKeysList",
    "DataDigitaloceanGenaiAgentParentAgentsApiKeysOutputReference",
    "DataDigitaloceanGenaiAgentParentAgentsChatbot",
    "DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers",
    "DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersList",
    "DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiersOutputReference",
    "DataDigitaloceanGenaiAgentParentAgentsChatbotList",
    "DataDigitaloceanGenaiAgentParentAgentsChatbotOutputReference",
    "DataDigitaloceanGenaiAgentParentAgentsDeployment",
    "DataDigitaloceanGenaiAgentParentAgentsDeploymentList",
    "DataDigitaloceanGenaiAgentParentAgentsDeploymentOutputReference",
    "DataDigitaloceanGenaiAgentParentAgentsList",
    "DataDigitaloceanGenaiAgentParentAgentsOutputReference",
    "DataDigitaloceanGenaiAgentTemplate",
    "DataDigitaloceanGenaiAgentTemplateKnowledgeBases",
    "DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob",
    "DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJobOutputReference",
    "DataDigitaloceanGenaiAgentTemplateKnowledgeBasesList",
    "DataDigitaloceanGenaiAgentTemplateKnowledgeBasesOutputReference",
    "DataDigitaloceanGenaiAgentTemplateList",
    "DataDigitaloceanGenaiAgentTemplateModel",
    "DataDigitaloceanGenaiAgentTemplateModelAgreement",
    "DataDigitaloceanGenaiAgentTemplateModelAgreementList",
    "DataDigitaloceanGenaiAgentTemplateModelAgreementOutputReference",
    "DataDigitaloceanGenaiAgentTemplateModelList",
    "DataDigitaloceanGenaiAgentTemplateModelOutputReference",
    "DataDigitaloceanGenaiAgentTemplateModelVersions",
    "DataDigitaloceanGenaiAgentTemplateModelVersionsList",
    "DataDigitaloceanGenaiAgentTemplateModelVersionsOutputReference",
    "DataDigitaloceanGenaiAgentTemplateOutputReference",
]

publication.publish()

def _typecheckingstub__55a53b6a78cf146a503d1f19eeacdb1d3829fa2fafbef56283577fa93da8975c(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    agent_id: builtins.str,
    agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentDeployment, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentFunctions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    if_case: typing.Optional[builtins.str] = None,
    k: typing.Optional[jsii.Number] = None,
    knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_tokens: typing.Optional[jsii.Number] = None,
    model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentOpenAiApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    retrieval_method: typing.Optional[builtins.str] = None,
    route_created_by: typing.Optional[builtins.str] = None,
    route_name: typing.Optional[builtins.str] = None,
    route_uuid: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    temperature: typing.Optional[jsii.Number] = None,
    template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplate, typing.Dict[builtins.str, typing.Any]]]]] = None,
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

def _typecheckingstub__2d0ea88a78b21f3689f9c2d6dc92be5df8c3d1d47ebb2490a6dc8c0fc147c3ea(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__83ebe970b72f3f3507ffd7bf46c3baea1d28babf1a59ad1fc173ec899caa1e6f(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e79a33d4b6b880a00f4d6916aea21270073298be868e7d52c688a2711cb78064(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05fb131661efa2909f749221537be395c716aa3cec768599c701983be533dc31(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0223298a6d9b679d34db380be80aea15e1e59388b8fcf40ffe8c93454192d72a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d83d40b5c2219bc36fd5f0dbb99bf3f3e91c0fdde1032990c6a77056857fa3fc(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c5405a40453f1f0c806eca5afc875fe44bde16621e977f3ded8843b891854732(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a32ee71b08dedf3f4bbb780220d1ca9db3db0cc596d8c99ea0dcc254fd8e9e5(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentDeployment, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26ffccf1d181d1bb6631a6053efc568eb95b35e9ccd7612d83bce9c678db8ab7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentFunctions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0642f7b338f25553492f65e75ee8a0ca4c1a931e555961d17213e700188b2527(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab3bcada87c193b273a20cc6cf63002e45790e78b16eb381a594c2599059d889(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModel, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5ea59a705a4575409367998196a1fb967cc56584d1ddefb978319f8b7a9ae5d(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentOpenAiApiKey, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__86c229ef9e907b3f91f0fb85265294c9029c545e718032cb2edb873ed956bea2(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplate, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ff6b7dd50277f86b47fd2fd9c2adaacba0110df7228a3e3b74ae5be100a0598d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f97d41549aced3c3893a7b8e162e707f5b71df7f82c86129230c24c30ed5f048(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__63c949afb24261cc7d6d50b7aba0fb0b69c01acb84194db76067bc2871bfa551(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1acf113bd572bfc94ce0879c41e78f265964b6607f655934431df7741e28423(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__018d5534e38a17e97649d086a0d1b3c1cb7b3e446d60d9ef67dffe2838cf7a27(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e5479d15015d0f0789650daeee3bb882def748b90e1ff84050d953b3f7fc0db(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__869d1d4671d116f16ac0840c0f58be0edb1a043befaf7bcf875f8303becb15f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfe8aa441cbe5b41474573c690b6a2ceacdfe1d41d90a0c796aeeac603c11692(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__652917699e2f5b3b0b249f8e0ff49ce62a0574d6ba69098490b1d6934597ce5f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a02cd1f4846b330dd0975b6e6912d7e9be13da88915c2c4428d4a20263be56f8(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee275474486d9f205f335c8b245c93c9a86dadd10b25a140eca5e2f4ad14c52f(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bdb5af2fc0f4080b32f9e68becbac63e64f5cd3239c36972a73a9c0e69b6dbd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__40570ba5c536e8d647b6e6f74f55c709ad808c5c42aff78f47f19232694d1f55(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d95f67e3a6c970c914525fd2a5abf563701cae72c5ad92d85c2016e56d4747e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bef3e214677f39675f8631610863824c9cd41ea85807228b2edba9713a024d8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4148f22b82dc0c264e0e38e77896c1a463570d0ef5ac43ebba13e6577f31bd84(
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

def _typecheckingstub__aa7263551e1aeb2f478bac6741389c2caba2fff9ce811afc4408dc13b4ea4531(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e448793233dd0ef3e84e9692fb955ae6516e0b9d023582c498ba1851bf4bc793(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb59843b8f891d1b7def5da857c25594f09babfc2c4790c8230ee236fa10a882(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58489b7a027b431b61bb48c0b6205a40901e94467726a2d0c096bea5961861e4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aef5eb324a58ee4b3e25d26871ec3edc1b8afc9e80136bb34bd7f241b03e0b9b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e08bcc1be3f5d44283a4abb47aa5ec125162c414e5dd26444e6892443faa251(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAgentGuardrail]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78db844d77fecc4bed90929c162d4475fd0198df8e2cdfbce6278fe03a3d9d82(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0129369d281022db08e214df971b5bf6a60718f44f79697e3e64e9455c870fc0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b385fe47a9eca35f45b73528cd3a9232f6ab132faa380def02b8343c5ae56c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4eb55537f234204dec96d4b2a5678d5fdd9120f4a8ce1d903360fedddfc10f2a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__de41e48f7dd100a6d0274344bf19dd70cf78721105f7b2f51efe6ddd876a3ba3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1dbb4145e467f653d16449a0ad1f7b9f2edbec6245c43dd5666de58a456e576f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__792aed5a3a790d38f45cc3a7d314bf744be7a7ce4dec374435f20afa00b9f825(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bb417d2696ddab0c653c1d72bfe701abc4072dfb48158376ca668dd906000f2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__138b64edd90747b7cad76e04e0448d21d08e5eb1f67568848dd95bbb009d7eda(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d2a5249e10c6429a98c998cfa3ccdadc7d265bebaa998217a7d76ddbf418956(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24ef6572b3afb385dc55607b380d7d81e76d1b27b1c423aebce05e04ba5c96ab(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAgentGuardrail]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__38ba73ee3aed1a5541136e25472d14a34994b3bab9ab9c89626bc0ce055d14d1(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb5a1ba2f9c6104cb59e57e8237cf2a3ae2f2e48c3870c90a8e17b846073f39(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__119028dbc7bd05564ae2c2a63b0e0dfdecd7cb6205da7391f37a7fe16c5c774a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82b50c3d1427a55c94b91cfb8d6aed6d2e1642ec4708e780d77c3e51941c3790(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70da977f9f2b266b8e693bf2932b149e02d99f57e76c8765819abf8393026d96(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__99ca7b616cb7b17333407d3c353d0f5055d75e2619345ff42efe3e5b880cf676(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c6faa1830c09a76442b2269a35b8b21157444ce12c6fdee262e17f7cb0b3f2d6(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentAnthropicApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ffb4b6f99a74dfef8210f4f7039a5bccb8748fe2b0e774cfe2a952d2276c915(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__90503be41741dac6fd234e7dde2161fd5f0244d989460eb5dc0756e4b970c2c7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a958250a0f8a1a6c1aa9b8103afada041df126a27c38f5f2f149c3c5b5b948b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33d53c97e12edb62681f234b378143447824310b005a8e8c37c48a532364dd82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bcf120e586acfedafd0a65ca9bf80a3414562cd2f1df972e6df586ba91a43b60(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentAnthropicApiKey]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7ded080fd3cbd2a0cdb2cf1520aa26c5b4833b0d24838c43a9b7268a02a38a25(
    *,
    created_by: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    secret_key: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5314bb0f238e14f39b077cb662f3c1e4463af572c70e721578bcf9fbaf66f1c9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd833d8316094b6ba27e4b71f6c230dd66ca9c3320d1d29e69a3ab3ede736e1e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2520213b1201facf67ca5ac31bafcbdf6d4aa9789b214a7e449e5f2f398a79f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed832516552aec6c833e8df19c544880f559ac7af531b83a8b02b8f1d9a45a2c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__082cf98e664d0c6ef18dd3472084c1140b4fea009f306cb0e015e4a9a5be0be6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bab423fa1795455e9621709e48e64d37da77f4724ab9559e3ffd62dd1ec63cd4(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeyInfos]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b52fb1c8420130756683a8f75e05df7c66e8beec36a958728f9766fd74e66da4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01976ef1bcdf60c93a6d292ecb210a7b34d5b0b02ec994c1bb47657c5aade9a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1fa2149927547db68cda42b44b457919bbf7b6d040acded5b6c659729dd6ce2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd7ac3a561d6062b3f75c287950fb77d2e689a7ae9bdd8327b5841d7d7613312(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dddef34524f58ce8130ecf8ca8f378b5225953ab2a65722053ddf4ba590a3515(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__71f185330fcaaaf0857296aa570b49bd25f8d96e59191256055a100fcadf8eaa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeyInfos]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e4e893f7d8048996e26c829a945691e54aec9390f47188440d53963a5609936(
    *,
    api_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a0f1b60ace4890ddbcba8023cd78d86a88f76b8041e23da5ce769f4a1abbddb(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bc571d90441f71d1e99484e055c4f83b8f38ee69ef9fab660325cd742bd2003(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73102bd0ba435498276f1d0a5ac792ed2ffbf9ab8abaca03e4792c89b8501d2e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2be27a0085ee7ac546fb0ddd2ae0348b51002ddae1bacadc0113ef0da29fe568(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89144df563a2cf5401f2fa579fe27dd3da9d97d268088dda303e7fd83d00bf04(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__55e9b8cb776445857224cc63c1a17059540f7c28da53f0ffabc8b587be5e2ab2(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentApiKeys]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c516f2a14a0911deb46f096762085c6067d896bcb2e83fe4d1e72d54da37e08(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e3023831f55efcfa27402d530cf25bcab42072114938c39bd9ba42f7f696c82(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c89ad2582a44fc6367b02734ef25c48b1508b01995925ab1376e4298ffebdc32(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentApiKeys]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9e190799d3fca7427295789b2c609454e7abd8b9eafd5d6b6f2c01f58081950(
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

def _typecheckingstub__3dce3a0093de50f0e3841a61c0a6fd63c8d62237a428bb4e2d2fe0bc9b8b3da1(
    *,
    chatbot_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebaf60d63d2c369f06fe62cc515f41f96db79f93f02f1ed6e73b2510361d4076(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecae4e947eb3984b272722ddeb2de2eb1cd61c6c5c2217d1fb8005eff7da593f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ae7be4bb027905d5dcd1ffcfbbbc8b3228e7cd59a1ed8ed05118cbcc84fcc0ee(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe46fa384d1b72946ba37d4385f968ca68863d5b850f2165333743daeb2e6115(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebba11235b740876849de8ac6448649706015a2adbdffa0c5fc4b6e265cbaffd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f51094a0a11a40722a68c0cb4f77c4f3df29988dc26fcba7ad948667ed53a7aa(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbotIdentifiers]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c69dbca9cd4acd395674e7a27fc4983b6c48693b3a93e14ebfb04d9904cd169(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__509eae7c7528137a2d343a2f2fa87d0fe8483b63f1a714c97d73b6404d49121d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0fb4b46f7a63be64635251d08fe95de61ec8c1e20da0756aef142e714d59bcce(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbotIdentifiers]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef7fa39cfd6efd16751015a80fb39453d30ccfc6eab39aef904661b75390943e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9df83f1f2ec5b81cb8c11127a5b23e36c9adc2322b5e378f48b17491124d4811(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c888f775f3dfaa6cecb0d0397b801c97aed8d71b47e37a3a732dcfdee793b803(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24de99fb74dcabb57dade4253e87612fc24123bf432b677494a9be092846a609(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c2e3c85b312b18258f3d797107906b67cffc507fd1be70c926b99220832426b(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f6fc28ce7783d9adb83287809daa0fa3aec3c3fd04ec0f599632342c4bb064d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentChatbot]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d46ea254277d30073e9b3bb13d0c6a1330adfd7296cd0a5222ce0f7e2d78af62(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50456857166a73079f35d55f4dc9ce1ddeefd24b8e2dead294e39d4572b3e31d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81460a09e365a1928e097c9951abfc494451e342f2f41d10c8004acef2592ebb(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d78b1fca1f8eee5b11b8f185065dbdc55659a91d31f5af0ca461ddc4bb3babe2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0e8dc1d36bd44dbae7a835922f3ff15afb27fcd3d98955b5a198b0fd2c477236(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1a672b091dfc3f3eda1243b360805b81439e0936938bf5543cf48e2572eff730(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8481a435323a6f1c36b473c8d3dd0574f36441964874a14a0dfe49fda5425987(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__959e5979f41c54a4821d6121c85e0a5e38bdc65eb07e6baa7e10739f00cf349b(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentChatbot]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f02d5e65877929d25ad96a6ff62902d646d8ab3ddda5437d2df5d6c83831bfe(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28020bf562023fb77ff518ea5e62e3df33458480be16588c1810b404fd786f24(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ff8c8354cf3518b5b600be2e9e0180456a42d560984ec06ec1ee86bd1ceb231(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b94f6f8ed3a1dcf70fca5c18893c2760117238e9c391b5a73df73d39dd1431f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94a7da25cce3e4948425a2a3b4c9d96d80a17737948e0beea046a115bc592f8a(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ec810260e8f052f0ed07be9109eafafe1b743fa2ba3fd100732c2281d5f97ba6(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e08d6e7e8a75c2ff1f6440fa5f4ececed89c82941b641c0128dd505dd092f84(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsAnthropicApiKey],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b83355fab72a9d8848da09f99faf2370630c0fb8d60140304c4495f7ae7ba3d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__28249d151a985ee9705fd8d3832e4ec65fd161c54fa900c169f1aa97feaa5565(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18130b6c50472f70b173bbd7d630f4bbde34ad52cc7711c80279459a41b3a796(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6179f8a6d66ebe94f822e3aa1c16c4baaa9a45e5871fb9f029ce54e955dc625f(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2d18751144326491a38f28b56ec0b915305b1b87c9b8a6612c9ae6559c99ed50(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85bd5ac3eaf92950086c2721aac0eb1abdcdd4a1a6d47fa20ed3e5c24d60e56a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6654350b4cc214b389d512221ea9f08f6ea91cddab7a81667e920eadef66851c(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeyInfos],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3f1ff8838143a43f2d6de159761c4ee743bdde39cce4696eb1f1e4819049a343(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93818f9487728138ef1f3c0ec00e0dd07d7257dc836965daf00f06c8caa00197(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__983c0ca6825c01bbde495e29180b2f1da4609e4cc030f8dffc6e85c6fb571db4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0b0c38407c85d97d3b3d2cd85050546cd8aafb4a6435ab10960392706e75465(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52def4f288040749aa3a6520d1efddb55804befe9fb8d20af97968f557809651(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9bcda4fae834fec34e7b567e25543b4323c43ff80f1b17055d42e2d93a96045(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50dca3f7ebafa30a14cd4bcb24193e40887fabe49da44e0ff6fb861401eb24e0(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsApiKeys],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__89aac4f9c82f71ce8bdbb1d21f9b4afdf5b36c0f984b1cbfb86f311862812db4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6235e30005acdd3ec1fbce4bab13cb5173fd82308b662a5252bf9e0156594470(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f3d31961bdd2416fd456c0a85ad08c34240008fd5daab2049e622611c4adcf4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__50e759dc028b419058446803d043448bafb0b4c7daec5155a1db17f96bb55a8a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b0c96fcf0b82935d71cb57a1112e4bbe15bfff3c2ffb707788e0fda193d4c9d9(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bd45ad34167a972a0a1c3da697fbac246844d9547ec8d15ec577b79ab758df00(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__93b1085dd102682b5a43750daa56f51d74b3217dcb84b8732efcdc8238d6d09a(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbotIdentifiers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0374c9ae188cd1b2624afed43d907c4ebe59c6cd474b8ce3c90c695560d4a03d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b08f82fa1f932f6d5ece9f080374f2f50016414425a8e55d2fdb1f9d93a74543(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6ab477883b1c2eb98b9d3c3fc04f9880c76ccac0ea785174e4ccfc2191a4299(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44f96be3b8d1634708f5f022b7a2827cb8692287d56fd3f3b32d18245f669c97(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf65bb06f0cd8fe61b524db56e7191356703f3e6fa0781cfe813248cea87594f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52ea33cabbb00e7e334b6e10c32edd39c0be35f774191d2fea254abe0d1eaca5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a43e5b3ddd33571e159b508a1e71097174bce2296553ae5d47d3ae402799848(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsChatbot],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__585524ff16782071fba02b94f09f69694e9bc5ea3cd537e4aae5d2ceba0f02bd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aaeaadcfff49cbc6dbdb9efdb881996123d8185a4f1641039fe0b5196f826510(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c3180e5253052aeba7e7500220b3b872c8ca3e871615447af82688d192c9e839(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2c3a95343286682340ced4e5b3aa6e21d5da2968e1d36c2aa73f7b013a7a5e4(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__688dac456e7d8c8d3980077bac90ec112f3fd731876d8ae17678f62a13f5c0c2(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d79556b58d0c029e4a6865cb3331727a252dbd23a0d2dce640db1f9b2e06dfd(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7fb6e649aa49f924fa225f6201a4e205e638abc439ade7607153ef8c0cdddf53(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgentsDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__425b7648fbd3c16305b0602e2f5fbad9db225f83d13d1602052eb0695a49fb3a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ec84ae1afa71d8f3b4be75c2b29c86c07a30d28d9935c7d79aa00752f8b3fc2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b7f43a25f8bc795770b79d51339386ec3f678e0e7293516342edb166798b464(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e091c14e0a33797286addc3a4d0b8c5740254c82d5e480d8db58a8566eaf32d8(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc358a2c98d2290fe2e45fbec91e02d1f2be97e54bc409487086eee6fbe86a98(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__179bd55ce31daaaa0c07dfe5cbee9d0bd71b8f3f36aaf10e8b810bc557d975f4(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a116ff421788295f59c193eb0dd1b67e59970e3cc32597a9505b72e733a83f7b(
    value: typing.Optional[DataDigitaloceanGenaiAgentChildAgents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7cd2f69e97f123464bb992af3789462ccdfbeaf24bc9bc57b8783ac085ec7ad2(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    agent_id: builtins.str,
    agent_guardrail: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAgentGuardrail, typing.Dict[builtins.str, typing.Any]]]]] = None,
    anthropic_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentAnthropicApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_key_infos: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeyInfos, typing.Dict[builtins.str, typing.Any]]]]] = None,
    api_keys: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentApiKeys, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbot, typing.Dict[builtins.str, typing.Any]]]]] = None,
    chatbot_identifiers: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentChatbotIdentifiers, typing.Dict[builtins.str, typing.Any]]]]] = None,
    deployment: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentDeployment, typing.Dict[builtins.str, typing.Any]]]]] = None,
    description: typing.Optional[builtins.str] = None,
    functions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentFunctions, typing.Dict[builtins.str, typing.Any]]]]] = None,
    id: typing.Optional[builtins.str] = None,
    if_case: typing.Optional[builtins.str] = None,
    k: typing.Optional[jsii.Number] = None,
    knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_tokens: typing.Optional[jsii.Number] = None,
    model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    open_ai_api_key: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentOpenAiApiKey, typing.Dict[builtins.str, typing.Any]]]]] = None,
    retrieval_method: typing.Optional[builtins.str] = None,
    route_created_by: typing.Optional[builtins.str] = None,
    route_name: typing.Optional[builtins.str] = None,
    route_uuid: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    temperature: typing.Optional[jsii.Number] = None,
    template: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplate, typing.Dict[builtins.str, typing.Any]]]]] = None,
    top_p: typing.Optional[jsii.Number] = None,
    url: typing.Optional[builtins.str] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__878cfeb5b6b6a73d8619ea2806b517677769fb166d2c88424e22e8610bf9d389(
    *,
    name: typing.Optional[builtins.str] = None,
    status: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
    visibility: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7f06e725c825025a3afbb7b8cdf6baf3b738454c7c84302edc6644ea781beaf(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed6ba9a8ef56b2abeb1da320f46ccbe7b5fafab4600921d4a538f2c2b1dff694(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__78986f0e490f7bf8fa7c6efcaf96538cb70aeb74ced8b6c0cdf60c7564a9be89(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b683d5e4ff6996cfaf7d24cb8700fc31fc7ef2561274283d647a60fdddc1a602(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13bf1558b9559c30ba995526e01299d3c3f4278d166c33344ef579fb4fc0a0de(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2945e7cc92d1b6a8d0ea5f7a818406deb8dcb0ad04f6acfc5382e8edd897c076(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentDeployment]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7e391d2966bd9e70c84bbee53de0fc19ec7b8cb54c36292da1995d2d655f75(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bfbc2e4cc415de98a509cdafb720e4c01ceb7c7797439cbeaf26f30f218fa1fa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d00d21dde52563dd0842025e0b9e35343621e9b52ba3610703e6d01bd61e55d4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1317e497e8aad8626a9ea57042c0fba4e669432e4e68699e201b8d4aa64c8051(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__244eb711bf53cce707f265f4bda99a7da00b80dbdb62282f6464e018624f5887(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1b66d0626535684025ffe17a1c872926efe3a6ee0c7bda65cd6790f05264f56(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97225efdee331c5f1d70aef80ae0f47609fb09a44de7612de18726d102a66d68(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentDeployment]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fe419d851e0a68377484695207aa2f1b7b6cff03737b127ea7412b5e9e1daa17(
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

def _typecheckingstub__d8932c737407a5c507b5139d4abdc4548cfa5de86e7088de584fc8f908378277(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b299846e1c793c844043d8399c434aad1eaf133c2cb4a51a02ed9ab99cb54d1a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d30aa883ef9599d76159c6bd9c98ccdef52299533dd101031a1e8fe749b5fb4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9488a732a52f93de1291cc5f2f13364cc94e8576e757061eb758797da116b98a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a2845b2ffffbabd526b333c91dfa67320a505d34551bed0f16485d455bba2ea(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__400204d5c5e5db4b2fba2e398ca43eaca678e320c6a726467b85daca5f070356(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentFunctions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c437a1d8ae6003b97d7a457ee1c43e9e74902ff0d67d51a7ec175e26620e0238(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d23c4039d775447918b23125b98d76384e643a20637832c98c8c858e73528433(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e81c1c3537ac8219b564211e136f8be8f50d2900c07e9f1ed31160b4a2b8934(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5e9c1f415e2dad778234dac3d1393787b6be4ec5aed3a58dc4ae0324bbd796a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d1ca82be36ab8f42e048744cebe61cbedc2888421999e6b472d8c34183d9e8aa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb6a848c8c327b8f16f2aea2e83f3b6f1493be8554877ffd7d828c748adee7e5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d89cf350e11ad3482d6bb1a99fd79a8a45f5535d01ed7dba61acee3b0f2528(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2b2f647bc08c321bdb16b93b05edf382eef8f3a21790aa523da91390e2dac825(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b22e873f121715ba07086defc511c092c088446c168a2d0eda3164ac82d16a1c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__190c4f05f5243abfc2d15db403bba2ca7878cb658a8ea520f4a932740d4f5f18(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentFunctions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__25757f34ce3888bf48388906e9f776eb4eb4d118df2e06945fa934bb236239ae(
    *,
    database_id: typing.Optional[builtins.str] = None,
    embedding_model_uuid: typing.Optional[builtins.str] = None,
    is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_indexing_job: typing.Optional[typing.Union[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fafa2175a106711aefb9293ecc32c1d989b048727e723098e298d6e8787e5984(
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

def _typecheckingstub__6a251aa4b31bf54b282d59a24e08bef1907d1dd6303ad22b9c3ae414b4e88dc5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9e86c1fac6bdd63b3d38f1e0390f23e62dfa8f7f57f3ef31d92c1a2613c3410e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02cf8bc9e60a473bd0b3ae5add0ec3698e3ec050cb9606ceff5a303981a77f75(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d6b30747c7e472572cc31b327cda5cbe9cad26f3d3b21c5eba1e415654d0e464(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ab42971bf32964f0fb340cd159ef1948f46566185fc027d44b362e394a43af3a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__902ec2f195ebe6834cc58ca9ad33466b9541599a80b7e9e6ac034ec6cc510ef5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__453ba52e4f2d835319e652a0bbe335bb557edf48e11e4396314755f66afef168(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e7d6ddce91078ab444579f808984efbeaf19a57ac9f9b440d9bec2d0382d441(
    value: typing.Optional[DataDigitaloceanGenaiAgentKnowledgeBasesLastIndexingJob],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f12dae8473788a51bebb8a299916a4894da3530508d39cabfc839b8eae883e41(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a277bd938b525fb895c825391ca569fab446be0fd9b3220c01b3291501b6fe8e(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8daeeace70ba782fcb0aefa378cb9c5faf3cea07ed1e77598db662a8a7cded06(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d28c08cb5ee220c7908d82fb084db5f98aa904e84ede53abbe7957fd29bff9b0(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f48c4b575a2c88b923a7d99f30b97796cec548fed52789d8664d803eca46018f(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5ed2a61c3cf1523cccf0545c48b8b79beeef4280ff80f23cc0818f00d84badba(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentKnowledgeBases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d365fc61998021e460187be81258ec0bd129b707c9152573928969fe013f6a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__caa5a393f7a99aab0bbbe9620ec19ec731f4452c992059f2152161e9aaf02f1a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__add83557e1ba02a3ed624fa2706f773aa71f8f8ce969cc5d644bdc1161fe6686(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__621ba0985b010c805d4fa868cb81e0d334643051a38d7f2ccffc45664db81898(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9ff5b77bc8218273119ed3c1fb3ced6ab0219fcad0e408a3a0b2c5fc3469b0de(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a625a17546d9127eecca3b210de9d090cf381d66e23c25f82daa141cf56c680f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73821ff36017d0251a367393ec8e31cd713fd628bb74489df728fcd082cfb581(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__141b5f8aa2f365e1d629996778924faeffc92c4466b9fb88b0969953970f18c5(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__56b18d3aa0536a0989987dd8fbd13a7c059832f4ff457a800744e48468cdf386(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02a6aff56cb080220c0a134a4ba0de01fe2d114c2496802ef34814d68c2ba06d(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentKnowledgeBases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5e8e8248c46e8acd5957b66dec426f0951cddaf40d6ea14cfe933d3f2fb4a85b(
    *,
    agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModelAgreement, typing.Dict[builtins.str, typing.Any]]]]] = None,
    inference_name: typing.Optional[builtins.str] = None,
    inference_version: typing.Optional[builtins.str] = None,
    is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    parent_uuid: typing.Optional[builtins.str] = None,
    provider: typing.Optional[builtins.str] = None,
    upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
    versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModelVersions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0c5207c689b6f75146850829e6ba4b3610e038883b99bb9885405f1cbc0e8688(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e7fb0fb7e9df35288691313f5ea36f593323c807ebda16e5b0edb5b1cfcb18a5(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__26821daf51353be928f68c8db0e62ec226eacee345cb80100e25ebed2d3b90b7(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e96bb983c081e90d638bfbfd7b3f81a6aeb5e7c991478d50f89e556cf8af296(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8a6506fe67a81833e560cb1950a207c411aae639d1cf4e19a655beebe2c7731c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ded0983ddfb013eb258effb7c56465a5684f1e70091480378c2ae565fb5723d1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__538ee70cdb812ad91d884ec9f26b800bf8dde01916ad6e57481f1e02740e5777(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelAgreement]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22658bb3b0ab564978d09613d1f704c4b89dfebb64004608e2affe144b67c804(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a2223a633760eb49ac2257a1fae5e99fb0a1690ef0931f16495a219def16a0ba(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__76900bdd2f48a94c3a6ceb01e24748fa10bf235eb25a446e5d5199070696d3f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfe0d361ec8253d6d18ffd04ebaca26ac1dfb2bbc32ee0a661ab9a822fb3ad9a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be4ab2498559f8cf2fed894e9e9682aeb0bd73ce42f060658a2e4516c21aa569(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f61fe6be9a548e27193c4df5335e7e5c936e817fec7e7bd16169815bd4c9f526(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelAgreement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44071294b1a68982d1fd62fabff7e7b58986c7b32daf7db6537b40a31b7a8bed(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ad48e1275fbbfe2ebecf764f2ad5467128d9b86a37788d27981a3af0719cca8(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1cfc45b754f10485ecfc27da8ba050af2bd9caaef054db95e05aa4bf67ed0a5(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8068f86701351aef5888498b744de356d7e769824dc41898f388ef916d613c14(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f1036ea44bb8ffc1de70b6ab08b9e3188f11897c776ef55fbaafc54b43bfb7fd(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0518560baa8554ac2ef0a41b86b9523c0f233abc324194794aa961aeb5d9f3d7(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModel]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b818a92a46cf495262c52d2f2df24c0bb83938695cdbcb8ce1b727c86f91ef81(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__824fa1c121934b35df746159052fd85adcff8a4055e9b6740406cbd6cb4a8079(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__53efa633b9fcba73cbbbb5cfd03968c719b885852df835de884ccd12708ee071(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentModelVersions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__94f5684104d78bcb1be0f3c20a2c1aff2f56c2bd43e2e1c80c6698502db97e94(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c1116bdea05987f2927ad82be18cbbf89526f2d0a6c88138b77fea02c2aec7a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b2e87086737b2644565ee4a055eb05b4aa080fcb9b8241de65b6ea1af7f01e1f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__989057d95fb31464ad5ba4a7ded9c8906dea6100782c229fc2c11ce88e617ca7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1270d4585206c3294dfdf353deaff11ecd4bf0efc8c3b980508405fa3d6441fc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__279a0002ca549f1c25cbe9c05b475ee9c47c3a01938972691a791f2eac6f1516(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c37312500d12027e6332c200816f7e1a27c155d00925b168097577389b13d3e7(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a85658c963df639e089d3d8c75bc223142d35daba6bda74cd1fa6b0f985bed4(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7bdcbbdefa0205c7c665ee0974ece1dfa105977605859ca3fc1f77d14b9d4d(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f5e56dd4bd900d153735093757c50cd9b7d7c1ca37e573c7f645386a58a5649(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModel]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__43983929b34f5507091fad6169c1285d31f5958c85bef526511392793853554b(
    *,
    major: typing.Optional[jsii.Number] = None,
    minor: typing.Optional[jsii.Number] = None,
    patch: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__008585ae03738eb278feabf9c189063b174caf2f1293eb4badcadd7b20087b20(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1042b51bc3b5ebd1b1c3cca6c419e9fe5ed044a11dc43e1d031af157ddfac61c(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aab68abb02dfe0e13183b9372cbd6efb02ecedd4ef755f6b415acf60df7630a1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__058df50f09bb1def2380e84ae6a839c8cba88bbba1ca6c027a6ac3e0f62a458c(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__167d5592965508c1f574c0aa2df9fbb4cff170b9e502cbbf39e9c873558cf3f6(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2ac53bfd7e719708ab19800e60772b970f8eb4d22c85e1b47b6656c0f38d6364(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentModelVersions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19195bde706988ba4c6f22cfaa0bca68b4b2b0ab9507843e8e9a25f4be376bc9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dc71a491aeb5b216f7a2a1b420d7117377d19d954c8029a170b220428ed3a212(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__badf8ee9ca0618d51ab73d6bda3bed2ecea9fd4e21f3140b2ff778faffc194c6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b639566c48e58cb5e42aaaa3b0892d89a316aa75dc136bc28576da9386e2fc9f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b5add1c9fe26ca3ee49dd6418b154e9141a549451cf68c36c48f8b22481a40a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentModelVersions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1e2f8fb006a932d3d0c6ba8c2120a5b0e590c9550f6688eac867918a0d88c016(
    *,
    api_key: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ffd868c05a1d5f08086ed0715330716f6c428bf922a52090675702a906e69b53(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__77edc5c1aaa3587aaa6cded0418282279ae7d21b7d9621d234eea96dede96285(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9595c393cf1b9d163d3fc8aa59711a0c88f829d610d7771f4fa9202c1aac2957(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a07b50a2b845657d4249648a90a4a28bd6824c0367718a8b6c5b3c8d4d412f2d(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__257cd214ea2c0999eb7300da79cb0fa107cd93709cea8a4ef5857ba3f0cc94f1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__92d8e6d25c5aee84d5e935ff585bfe01549efc4c7921a2a6a64faa84cf3b8c5e(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentOpenAiApiKey]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81dd448ef1dae9bb6dcdcdb36240a9ce90563fe425de011b329842911cccde9a(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e21d4159ed18814eeb8d6ea84f59f80795499918f4902bff75d451a9ec71d1f2(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2274617da0249e99cb79687a8f01d1ca4bba228a611ce947ee6b8560c286ac41(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentOpenAiApiKey]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a5629abf5b489839d13c15e10912130ff1046d535c40c6df2cc30384838f5c12(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__22ba9993a501e970ae2cf371ee4007121e42a72c15d8f807af02509b97fdd8f1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ba7a27e49441a48b71d69b30706209ef88d0566ae346e8178cab9a057abe45c1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f3bace42fcbdb35057dcc36e3387f8db8ebf11be343e6865b59b7f73b1f9a8ab(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a5b243339e65f0b5a853a16c8b03fc257a6360fb6e24105167dc30a2609bf94(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4fb94ced0b4377be7b8e70e563a1ec8d3d32052d510a7b2bae72bb45be09582e(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__34056c54427ae33d400b3c6cb1cb2b0be906e02d56a61d1a63dcc5b675bdd9c4(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsAnthropicApiKey],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__448874ddfca73d47d174bffda92f408a251b3377d5fe29239e0da89ce17083b9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97091c8c71315c037943e76f50408b9eea550cfdf654b5435e409d06a6aba538(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__360b51a497228f5b0b7270e07106f728401ba265d5ab9a8737434dbcab641198(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__54a6eddf0e600e23eda694fdfa9c8d67df487712c9c947b2d2fb3de7dc5aa43a(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db7432c8f264fb897623283dbbdd6b6929e512c84a49cc66d38c2ea60b56ea39(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d5642fe535156a12d82b583ae61731bbac5f521d1b5e1d85fdf0eeab8320ca9f(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b1ab42618ff06b577b19c5f26a47704d29eb3177f3a1cfd229f001a117bcf0b3(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeyInfos],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdb3cad4c6d83b70c7994c2d1bb5172bbe503c68498deda293213bfb16cba0a8(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3169b879f184855c049f85c96cbe78f3af11249c2d8312973f335a06df754b46(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bd7950c4ec95c274e5c4a8e491bf014c398f1d92a8badd134a76e0fa47d437e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__74cfafb97327ccc9015d7f2ab3373433c2d7adda471d824e932db203c78f05f6(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3a330fb691c332ae5391d81eb276269b84c3ab47af39a5a0594eae2ea51249c7(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d9672fbbea52dfd528213d2a8903ead4705af859105fcf202cd9f4e38f11829d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef064b2045c1cdc3cd7d46f87a30e0f919034c8e51eebd97f3040e7d6f998598(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsApiKeys],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9898f902484f5a4d1925f420e3efdaab0754f76521096138f02c48130111a317(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6a3f517c69aa0ed95288f94fa975e77d070ca27932469d30fb9aeda28aba33b2(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bda2a67360197f7f3be89a32648c207e984086417c6a2cd8ed0488eb6747f3b9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e06eb87f0cb8f29993731fce2680018d3a9f2b2f504392f79cb343356394525(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__da458f6d22b8fd7efde6cdb4291815b8397fb671fd15068b5e77a5d37cb6c891(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5d8e5a57333bf3f543fb261b1a6bea465b2651fe87f9fa91e64183a6a4a8e4c2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__51fdb10c7c7bcb5692f677e0d2f576a64e7215598b9937d4ae17bcdb3e84a3ae(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbotIdentifiers],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fdda80ab9c501ef1e2a1207b465bbd3b6f190f589cbfaa2f597478cd956496aa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ee1e801c61de8b739a2d850b53402f93a5350ae976a9d1f9d3bea53f86c9e31(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9d3e637daa66c707cfe3e296c784173b908f54e5e1f1100c2bc6830386d7f54a(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c16c5d222f43aca09b781cb524994c1b0bbc0a51fcccc1b7e44f4d9f835b0716(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a6562a41da0ba900e48cbf85fe295b485e898da808da3d583d6b70f4ed645582(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f393659e1a2ee5e1d0f72d97c71f81db271bccf5ea6388dd855703cf40f94c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c600ed91f86c6ac737a7ee80e0069613003c0961d83fd4d2448f6e602b36efee(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsChatbot],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__046e4ffbdacb82ce7f851d94b3a1121fe8fe870ff3a941876beeaa613af79a5b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d97072d783bc72f07d09766a671f2ab44c56327f88245cf80746b9409fb2126(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__850b48f3477a9ff77627c0d8550c9e44bc3850affd9e3ea37e32145781382818(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__21182c0d8171a8fde8d7eef3e487dfe31fd50403abece381fd3eda76ee4761dc(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a8aaf20015c613653f816532bdeb4ad8d3e4f9101b209d51360b5e68292e4da0(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bac2844ca92f38988c7dee70c2ebbb50b8afcc818f5f5f15b3994c96c0570f1(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95fa3e6956aee6b7d8138820ff87f6ccc48fc6cca620a1c4ffcced55e3e929c4(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgentsDeployment],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3bc8648b400663ac3f6a3ad4c67f314d53ae5dc3a47d06bd4bd6ed9a4836e286(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__00cc14fb44b6dea0c6a9d26390e5f8fd033af97af4e042f1781b3272b85b101a(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4f41fe0d29ea0ea4c0bacc7b64341efcdc2ab1965a0024b79bcef3632e3a1842(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cbc081995116954b33d045034393125b3125a7b3dc83597743aaef551cbe0ab1(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f2f5fffc993a3fb0308819c8b128f1398d5e1d7b074237fe2a878450713356cf(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ed75d71aedaccb4e4546af2403b1f3b7abd585f0cb0072ffe6b2fea32193706c(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18e559fcbca99d4df2913e016de58eb73cf9823b7b7a269b0ca494108a97e651(
    value: typing.Optional[DataDigitaloceanGenaiAgentParentAgents],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88b8d0a05edcf0871a6e59f9acc4d9517991821ccc328c01ea14c8171065b952(
    *,
    description: typing.Optional[builtins.str] = None,
    instruction: typing.Optional[builtins.str] = None,
    k: typing.Optional[jsii.Number] = None,
    knowledge_bases: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]]] = None,
    max_tokens: typing.Optional[jsii.Number] = None,
    model: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModel, typing.Dict[builtins.str, typing.Any]]]]] = None,
    name: typing.Optional[builtins.str] = None,
    temperature: typing.Optional[jsii.Number] = None,
    top_p: typing.Optional[jsii.Number] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a0e890a7ae8d8a64b64d80a51cb963caa10294cd47c5336989daab186f0b7aa8(
    *,
    database_id: typing.Optional[builtins.str] = None,
    embedding_model_uuid: typing.Optional[builtins.str] = None,
    is_public: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    last_indexing_job: typing.Optional[typing.Union[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob, typing.Dict[builtins.str, typing.Any]]] = None,
    name: typing.Optional[builtins.str] = None,
    project_id: typing.Optional[builtins.str] = None,
    region: typing.Optional[builtins.str] = None,
    tags: typing.Optional[typing.Sequence[builtins.str]] = None,
    user_id: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7977b483c22deb2a599cd6d06652684ca8bca68612fadbea3613a5a9d8e80cc5(
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

def _typecheckingstub__72e9db58e3c41fc1575f1a7a6ae177e571d99e37d09deb60807ec3b996b9ee8b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95e5dce13003a1169f73e587663c2af5dc94f0b3aeb58effe0057a132cb9a5cd(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__037003fb6cdffb1d54b38f95ca78e6633e3ea2f98f082e518d80b6ab36aac3ea(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1599328b8e653fa617bb1f30e45254a2d9b67a1b68de292491f401edd6b19a65(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__be8ea30b0a32e410e4f648be2d370c032ea81e29530a5cbdda395796de24a4aa(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__97b502906d548e6488262ed3291d7f89d4543f7dcd381a1ded672cb269f6a7f3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f98ce4e05ccb957c442afc6781cf5d08279d44badb059bd472a1bb1d91987a9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__069c1bc3b103a2ff863f5c7d565962ba244dbceb70180fcc11d7c4e2cc4d3647(
    value: typing.Optional[DataDigitaloceanGenaiAgentTemplateKnowledgeBasesLastIndexingJob],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c12d2fb76a871aa48ae2c0859164c29ed4e36062e79df6f0d6dc286b84602dc(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3c4d5509eacc37b5421ea527b614c86241266c45cda756e7fd1449b60017e254(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b856dfd74d67fcb57fed7b7f866d236dbf85bf4ef106bfb2ed85f5da77a7099d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4f93429f919862f0f0ee8be117d68e77659f79798a1dc43d309ffef31d6fccf(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1d23aebeeb063ee53586ae47bf9cf9739f041e9fff522539d32a4706990e6f16(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__193c05d2e03aee71caa35d16357a00175e07eddfdc8810db3aad8df11afb2da9(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateKnowledgeBases]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fb4ed687cda41f445c4a09a99bdb4c63852ead32d0f387582990af9a00987298(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__12bcf6837d39801ee1ae872cc2505f3ffbe81848d319349c7ccd7c04db7e6dc1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13c016c6aa68cd59c0977795b9afc83ddce92ba5cbd18643605f8f34f6559675(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__05b18026e4621978786ae1d696dcc72e6b44915f7aa5c7475a70318a99a2f3f6(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d2f7eb0a7c235c7989d3d0486d51aae86cfc15e790ee9b86deddbf6c2565b9d6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__350d0419b144d6a5acfbb9c8d6307df2edf138850313837a9f5f7e836c24ad8e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__164b398d4fa7991d1a2da076b5134c5ea6f58969605bc2c41196631ef88b64f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__33b2d7fef5915d1ffe5e3948d2a3692e36f2a281afbd8ce8144b4e7d5480fd3c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__81ea278d15818193efa60e7023b80d3f3b908e01677a016b3f08d1477765b81f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__88009895492d571e6d337167feb981215edd14f084c94e895dadefe973ca3a5a(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateKnowledgeBases]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b211ae5c9df7fa7ae62b3b13b56d992153ce338da4e1a52a71d160a562437e95(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d9691957c17bde83ef0019776674478abf5ba9f350f8933e5d34fad56524ec1(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cb77712d4cc63cc90b292160932bf74d3f515e72b25128db2aeeb73e35f0a260(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__52b1b2330eb2845a119364b4f5a0155307c0914da8481080903cefa64d29da90(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fc88a976b214dc2be4e9c71e82359050eddad75bacb36ba3bc718656321a4e40(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__80225fcfc308a2f8dd5d8dca6b50ef4b36639dc971729312455831ba24811460(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplate]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8dd0fbba5b152dba73c6dc32366684d82ef272b60547516f5cd272c7e03d0046(
    *,
    agreement: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModelAgreement, typing.Dict[builtins.str, typing.Any]]]]] = None,
    inference_name: typing.Optional[builtins.str] = None,
    inference_version: typing.Optional[builtins.str] = None,
    is_foundational: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    name: typing.Optional[builtins.str] = None,
    parent_uuid: typing.Optional[builtins.str] = None,
    provider: typing.Optional[builtins.str] = None,
    upload_complete: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    url: typing.Optional[builtins.str] = None,
    usecases: typing.Optional[typing.Sequence[builtins.str]] = None,
    versions: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModelVersions, typing.Dict[builtins.str, typing.Any]]]]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__18221e74a4815b138be011384ccf90e203bb5a2f2d75c1534b7edc4d1bf5fe5b(
    *,
    description: typing.Optional[builtins.str] = None,
    name: typing.Optional[builtins.str] = None,
    url: typing.Optional[builtins.str] = None,
    uuid: typing.Optional[builtins.str] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__169b827f297a0053f89c5254777997b5ae7656f26b304b0a90dc81d6a0ea63b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07c898497413ff19c5389d5b1131cd5e519b4c045559d42df86bfaa20cccd1fe(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4812bf40a1558809ad6c497458072e90eb65b801c027a71471b2adab8b2fa120(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a271297faee1bf54e7e512882a50ca403824e2106ac7753089cf5cef14f23487(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b14cc6212f2da99c91f4408e276fff825dabaf5df85b9742105d8cc1e0c3a7d1(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__01fe754cbd4728fae6eaa0137154b33b0bb1266c4d9e5646048d94fcacf22086(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelAgreement]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__58e80dc00a751dd1284e0bbb9239a30f5fae35ece964a40ee119117d89470418(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf3df6d41225317a42c496ec9621a0e8d7f126db7578a3a45a62f282fc09a6ed(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bb308d75b895ca3521dfae4c16a94f464c1a472c2e3bcdf6bfdf57b866337fe(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e76b66a9aaa6f61d28e0a67b40fc37e3b44cff7b0f5b536b3f8a4449e70949f9(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70d9eebb8998debf5aed26252f1f85e05c448280630064e2e7d2440dd7f72643(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0d564c9c30f6fe9094b142bc3b07f106d084a86a6606498aae7ae9d24ddc3d58(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelAgreement]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef43765b810d00f2b033e1499369e5fc1bbe987fd95a617b6f5aa8fce276a149(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30bbbed0f1e28522f4791c4eb3540023cdc26b927f590f1a39da077fdf33ae5f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6c3681bf31480625ec93ed4e2fe60a58552ce8ea0a2f5ea4c94f55a3ea422ee1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9768070a0c0ab66bd843df7e0c9db5fde758cd9ab1f98991575730378a4b0915(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95f208a80ff6210751e3e297269526250272073a9dd3d7bf1dddb861db310f79(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__07223c8a2d6a67d3a3f4f73abd316c4d6ed0a144e5b85a17e314cdbbe8fa1a16(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModel]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2db6bef5e1858e430c9ab3a766d72bee5b724606fb059382275458e1b1b2305d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d8329a0768c764d6a7ad1dc22b87a62c2ece19c4ee02ac80cb90224487c0dfca(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModelAgreement, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0ae93433c550ed3244a89f94042a58ecdffb3a17638b824a1791f8635174d567(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModelVersions, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1517939790064bf4614a4e344eaba95b55069140954564114ea834376f151285(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__24161f201f47f57057efba551a0e7fe90140221c49b3006b23e311225eda4e3b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7f79ea212cd49c685adf1abd8369ca95652aed3834b27db0bc86c65376306541(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2d95f3447b6f750bef4885300aeb86836d60635e0c59aee4158b6efb8a645d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__84e2b66bcf386fd53cb35d619f55ca04e8c34717ffa35fbd01ce83fb01927e6f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__eefb2f2771bb1431c2fec0fad345164878b5ce3ccb1548eb4ab9514eba39737f(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__32b6eb3172bd09e14f11aa62b1da0154aab369dfaa466bc576a530f78c3e93a4(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cfbc695330510d60ed8544f783faedc7afa7bc3e8e8cf6a42d2901c6977f170d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7a4bcf701a8ce4260fda61a5c54b4daf64ca41fe2e89aed9185f067e0e21310c(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__82f7bfb1ff66f537bd2dc844883b88f07caa00be631d0eddabc71e82c8c264dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModel]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1fd62ba9e7e3e796386364d76105ab66f833b005c447882ff23d13045ad16d42(
    *,
    major: typing.Optional[jsii.Number] = None,
    minor: typing.Optional[jsii.Number] = None,
    patch: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c677b5ed27f52827b9a1f973e4dbaf3a8b9f65f7f63732e687f4047423242c0b(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__582d71d5ca8b25454e964a3af3f82aa8c52b17bb5791a6767771883b4227ae36(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7bab4f6f644f97546f1d4653da27798036ec33e2d6017a75283e271057c8fa18(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31520f72acd7f8d494f9d4cbaefd50346934a1d211acc62108a95b38f9a06407(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7d0ff90b2b470732daedf1d59361fc43948663c332bc434ed5da3580738422dc(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__0b85e712a3f1cef7f4f8a7164fc259ed7466cca748aa6cad3be96aa15958d7b0(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DataDigitaloceanGenaiAgentTemplateModelVersions]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa8c32242efabbb80a260b0c47f259aa9f23fd55ddab71a6258c00e1c7f6d5b2(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa14e71bdbc18b1291042d25d3f55d926872d00bb5916162ab0011a7b9e50b8a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b11a9dd881ffacae337b3d5319b986648dff963015faeedfd2537838841a402(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6f1938873e5216cf95ac5b306e7167cca5cb50c6b95d3cdf2e538312cee75435(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5b41faba11febaaea3f2dee1d69e634e0c568b0a127c624b429df1993a1431dc(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplateModelVersions]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__66f6f9f551336fc44a19e74b409cc55f97d836d0308e5d8ef194627fd7fcc628(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__44acdd9e805d846fd9dc6a617094367f7e2e8846eef40690c45c6ad47deda9b7(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateKnowledgeBases, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1ee9ea0374369552a9976ddb081d55a109655644e0746270a3bc6d1b7074ae44(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DataDigitaloceanGenaiAgentTemplateModel, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2c08191ac6d98af88378cabc1ebb8b03d72172c44c87a4046690f9fd53d916e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef3f5353430b5c3decc1e2a25c60eec212cfdf9a24b17535b7f741716ae2b0e7(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8ca263b5217fb792f5162bb4047ed073d4390254515ee48b3c091c3dfd3753d2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7b26b496dcb3f70a0b70beb28ba07c55aa3041be79c9067a15c1a4a30d497901(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ecedccf68946d2197dc1cea96f615513805c04aae69418298419688134b6f421(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a802e36c42b805d1125c883708e534bafdad5f3236d8354f6f1cab411294890(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__10fadab782d7e91bf188c084ba70a99a93075d2519c02664d7257c511603d730(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8c9180a79000ae9e6099483807022687af260210c19c659d99ca52d188de8dbc(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2e01643598e03196f81e14ebc38773342d078ffdd2c080442136d24cd03b0284(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DataDigitaloceanGenaiAgentTemplate]],
) -> None:
    """Type checking stubs"""
    pass
