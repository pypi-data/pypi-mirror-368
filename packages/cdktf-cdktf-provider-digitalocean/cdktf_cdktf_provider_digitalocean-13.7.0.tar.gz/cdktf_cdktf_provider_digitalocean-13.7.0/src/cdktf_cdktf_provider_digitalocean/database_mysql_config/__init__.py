r'''
# `digitalocean_database_mysql_config`

Refer to the Terraform Registry for docs: [`digitalocean_database_mysql_config`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config).
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


class DatabaseMysqlConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databaseMysqlConfig.DatabaseMysqlConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config digitalocean_database_mysql_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        binlog_retention_period: typing.Optional[jsii.Number] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        default_time_zone: typing.Optional[builtins.str] = None,
        group_concat_max_len: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
        innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
        innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
        innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
        innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
        innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
        innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        interactive_timeout: typing.Optional[jsii.Number] = None,
        internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
        long_query_time: typing.Optional[jsii.Number] = None,
        max_allowed_packet: typing.Optional[jsii.Number] = None,
        max_heap_table_size: typing.Optional[jsii.Number] = None,
        net_read_timeout: typing.Optional[jsii.Number] = None,
        net_write_timeout: typing.Optional[jsii.Number] = None,
        slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sort_buffer_size: typing.Optional[jsii.Number] = None,
        sql_mode: typing.Optional[builtins.str] = None,
        sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tmp_table_size: typing.Optional[jsii.Number] = None,
        wait_timeout: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config digitalocean_database_mysql_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#cluster_id DatabaseMysqlConfig#cluster_id}.
        :param backup_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#backup_hour DatabaseMysqlConfig#backup_hour}.
        :param backup_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#backup_minute DatabaseMysqlConfig#backup_minute}.
        :param binlog_retention_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#binlog_retention_period DatabaseMysqlConfig#binlog_retention_period}.
        :param connect_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#connect_timeout DatabaseMysqlConfig#connect_timeout}.
        :param default_time_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#default_time_zone DatabaseMysqlConfig#default_time_zone}.
        :param group_concat_max_len: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#group_concat_max_len DatabaseMysqlConfig#group_concat_max_len}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#id DatabaseMysqlConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param information_schema_stats_expiry: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#information_schema_stats_expiry DatabaseMysqlConfig#information_schema_stats_expiry}.
        :param innodb_ft_min_token_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_ft_min_token_size DatabaseMysqlConfig#innodb_ft_min_token_size}.
        :param innodb_ft_server_stopword_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_ft_server_stopword_table DatabaseMysqlConfig#innodb_ft_server_stopword_table}.
        :param innodb_lock_wait_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_lock_wait_timeout DatabaseMysqlConfig#innodb_lock_wait_timeout}.
        :param innodb_log_buffer_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_log_buffer_size DatabaseMysqlConfig#innodb_log_buffer_size}.
        :param innodb_online_alter_log_max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_online_alter_log_max_size DatabaseMysqlConfig#innodb_online_alter_log_max_size}.
        :param innodb_print_all_deadlocks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_print_all_deadlocks DatabaseMysqlConfig#innodb_print_all_deadlocks}.
        :param innodb_rollback_on_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_rollback_on_timeout DatabaseMysqlConfig#innodb_rollback_on_timeout}.
        :param interactive_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#interactive_timeout DatabaseMysqlConfig#interactive_timeout}.
        :param internal_tmp_mem_storage_engine: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#internal_tmp_mem_storage_engine DatabaseMysqlConfig#internal_tmp_mem_storage_engine}.
        :param long_query_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#long_query_time DatabaseMysqlConfig#long_query_time}.
        :param max_allowed_packet: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#max_allowed_packet DatabaseMysqlConfig#max_allowed_packet}.
        :param max_heap_table_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#max_heap_table_size DatabaseMysqlConfig#max_heap_table_size}.
        :param net_read_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#net_read_timeout DatabaseMysqlConfig#net_read_timeout}.
        :param net_write_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#net_write_timeout DatabaseMysqlConfig#net_write_timeout}.
        :param slow_query_log: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#slow_query_log DatabaseMysqlConfig#slow_query_log}.
        :param sort_buffer_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sort_buffer_size DatabaseMysqlConfig#sort_buffer_size}.
        :param sql_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sql_mode DatabaseMysqlConfig#sql_mode}.
        :param sql_require_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sql_require_primary_key DatabaseMysqlConfig#sql_require_primary_key}.
        :param tmp_table_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#tmp_table_size DatabaseMysqlConfig#tmp_table_size}.
        :param wait_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#wait_timeout DatabaseMysqlConfig#wait_timeout}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4ad3c49940b908d433860913c22510a475efb6f1f25e5643e3e7edb0472908b)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabaseMysqlConfigConfig(
            cluster_id=cluster_id,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            binlog_retention_period=binlog_retention_period,
            connect_timeout=connect_timeout,
            default_time_zone=default_time_zone,
            group_concat_max_len=group_concat_max_len,
            id=id,
            information_schema_stats_expiry=information_schema_stats_expiry,
            innodb_ft_min_token_size=innodb_ft_min_token_size,
            innodb_ft_server_stopword_table=innodb_ft_server_stopword_table,
            innodb_lock_wait_timeout=innodb_lock_wait_timeout,
            innodb_log_buffer_size=innodb_log_buffer_size,
            innodb_online_alter_log_max_size=innodb_online_alter_log_max_size,
            innodb_print_all_deadlocks=innodb_print_all_deadlocks,
            innodb_rollback_on_timeout=innodb_rollback_on_timeout,
            interactive_timeout=interactive_timeout,
            internal_tmp_mem_storage_engine=internal_tmp_mem_storage_engine,
            long_query_time=long_query_time,
            max_allowed_packet=max_allowed_packet,
            max_heap_table_size=max_heap_table_size,
            net_read_timeout=net_read_timeout,
            net_write_timeout=net_write_timeout,
            slow_query_log=slow_query_log,
            sort_buffer_size=sort_buffer_size,
            sql_mode=sql_mode,
            sql_require_primary_key=sql_require_primary_key,
            tmp_table_size=tmp_table_size,
            wait_timeout=wait_timeout,
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
        '''Generates CDKTF code for importing a DatabaseMysqlConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabaseMysqlConfig to import.
        :param import_from_id: The id of the existing DatabaseMysqlConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabaseMysqlConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__695b8acfeee0ceb65c82f993879bc119b73a4b5cc0d7cf144300764d70dcb3c7)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetBinlogRetentionPeriod")
    def reset_binlog_retention_period(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBinlogRetentionPeriod", []))

    @jsii.member(jsii_name="resetConnectTimeout")
    def reset_connect_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConnectTimeout", []))

    @jsii.member(jsii_name="resetDefaultTimeZone")
    def reset_default_time_zone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultTimeZone", []))

    @jsii.member(jsii_name="resetGroupConcatMaxLen")
    def reset_group_concat_max_len(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetGroupConcatMaxLen", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetInformationSchemaStatsExpiry")
    def reset_information_schema_stats_expiry(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInformationSchemaStatsExpiry", []))

    @jsii.member(jsii_name="resetInnodbFtMinTokenSize")
    def reset_innodb_ft_min_token_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFtMinTokenSize", []))

    @jsii.member(jsii_name="resetInnodbFtServerStopwordTable")
    def reset_innodb_ft_server_stopword_table(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbFtServerStopwordTable", []))

    @jsii.member(jsii_name="resetInnodbLockWaitTimeout")
    def reset_innodb_lock_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbLockWaitTimeout", []))

    @jsii.member(jsii_name="resetInnodbLogBufferSize")
    def reset_innodb_log_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbLogBufferSize", []))

    @jsii.member(jsii_name="resetInnodbOnlineAlterLogMaxSize")
    def reset_innodb_online_alter_log_max_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbOnlineAlterLogMaxSize", []))

    @jsii.member(jsii_name="resetInnodbPrintAllDeadlocks")
    def reset_innodb_print_all_deadlocks(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbPrintAllDeadlocks", []))

    @jsii.member(jsii_name="resetInnodbRollbackOnTimeout")
    def reset_innodb_rollback_on_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInnodbRollbackOnTimeout", []))

    @jsii.member(jsii_name="resetInteractiveTimeout")
    def reset_interactive_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInteractiveTimeout", []))

    @jsii.member(jsii_name="resetInternalTmpMemStorageEngine")
    def reset_internal_tmp_mem_storage_engine(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetInternalTmpMemStorageEngine", []))

    @jsii.member(jsii_name="resetLongQueryTime")
    def reset_long_query_time(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLongQueryTime", []))

    @jsii.member(jsii_name="resetMaxAllowedPacket")
    def reset_max_allowed_packet(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxAllowedPacket", []))

    @jsii.member(jsii_name="resetMaxHeapTableSize")
    def reset_max_heap_table_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxHeapTableSize", []))

    @jsii.member(jsii_name="resetNetReadTimeout")
    def reset_net_read_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetReadTimeout", []))

    @jsii.member(jsii_name="resetNetWriteTimeout")
    def reset_net_write_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetNetWriteTimeout", []))

    @jsii.member(jsii_name="resetSlowQueryLog")
    def reset_slow_query_log(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSlowQueryLog", []))

    @jsii.member(jsii_name="resetSortBufferSize")
    def reset_sort_buffer_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSortBufferSize", []))

    @jsii.member(jsii_name="resetSqlMode")
    def reset_sql_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlMode", []))

    @jsii.member(jsii_name="resetSqlRequirePrimaryKey")
    def reset_sql_require_primary_key(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSqlRequirePrimaryKey", []))

    @jsii.member(jsii_name="resetTmpTableSize")
    def reset_tmp_table_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTmpTableSize", []))

    @jsii.member(jsii_name="resetWaitTimeout")
    def reset_wait_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWaitTimeout", []))

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
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="binlogRetentionPeriodInput")
    def binlog_retention_period_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "binlogRetentionPeriodInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="connectTimeoutInput")
    def connect_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "connectTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultTimeZoneInput")
    def default_time_zone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultTimeZoneInput"))

    @builtins.property
    @jsii.member(jsii_name="groupConcatMaxLenInput")
    def group_concat_max_len_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "groupConcatMaxLenInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="informationSchemaStatsExpiryInput")
    def information_schema_stats_expiry_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "informationSchemaStatsExpiryInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbFtMinTokenSizeInput")
    def innodb_ft_min_token_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbFtMinTokenSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbFtServerStopwordTableInput")
    def innodb_ft_server_stopword_table_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "innodbFtServerStopwordTableInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbLockWaitTimeoutInput")
    def innodb_lock_wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbLockWaitTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbLogBufferSizeInput")
    def innodb_log_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbLogBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbOnlineAlterLogMaxSizeInput")
    def innodb_online_alter_log_max_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "innodbOnlineAlterLogMaxSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbPrintAllDeadlocksInput")
    def innodb_print_all_deadlocks_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "innodbPrintAllDeadlocksInput"))

    @builtins.property
    @jsii.member(jsii_name="innodbRollbackOnTimeoutInput")
    def innodb_rollback_on_timeout_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "innodbRollbackOnTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="interactiveTimeoutInput")
    def interactive_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "interactiveTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="internalTmpMemStorageEngineInput")
    def internal_tmp_mem_storage_engine_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "internalTmpMemStorageEngineInput"))

    @builtins.property
    @jsii.member(jsii_name="longQueryTimeInput")
    def long_query_time_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "longQueryTimeInput"))

    @builtins.property
    @jsii.member(jsii_name="maxAllowedPacketInput")
    def max_allowed_packet_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxAllowedPacketInput"))

    @builtins.property
    @jsii.member(jsii_name="maxHeapTableSizeInput")
    def max_heap_table_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxHeapTableSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="netReadTimeoutInput")
    def net_read_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netReadTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="netWriteTimeoutInput")
    def net_write_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "netWriteTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="slowQueryLogInput")
    def slow_query_log_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "slowQueryLogInput"))

    @builtins.property
    @jsii.member(jsii_name="sortBufferSizeInput")
    def sort_buffer_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sortBufferSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlModeInput")
    def sql_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "sqlModeInput"))

    @builtins.property
    @jsii.member(jsii_name="sqlRequirePrimaryKeyInput")
    def sql_require_primary_key_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "sqlRequirePrimaryKeyInput"))

    @builtins.property
    @jsii.member(jsii_name="tmpTableSizeInput")
    def tmp_table_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tmpTableSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="waitTimeoutInput")
    def wait_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "waitTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f13fceacd969e659201e5682c153cbb34c6bab1d13452726997047883040ffc2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__17085ec1a7b6adcfe438b7dbbfdac5323901c5f53f4ae2a7abbc39421dadc1d6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="binlogRetentionPeriod")
    def binlog_retention_period(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "binlogRetentionPeriod"))

    @binlog_retention_period.setter
    def binlog_retention_period(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfbf39674c1f42b5f7743335875489da78e4ce410e34276b6a95d55e8d0544b0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "binlogRetentionPeriod", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa3211b627a4919734f153ed8a2adeb11b3d310cffc2b603c116514edefb5cfa)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="connectTimeout")
    def connect_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "connectTimeout"))

    @connect_timeout.setter
    def connect_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cf302982893e609f3c1ffbc6bb300c4cc5303e5a58b9428bd961b138d59d9bbf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "connectTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultTimeZone")
    def default_time_zone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultTimeZone"))

    @default_time_zone.setter
    def default_time_zone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__db9c8ac48d5f348b17ab5d14e250a1d84437bfb9f4136eb05ec8ddbc5478364e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultTimeZone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="groupConcatMaxLen")
    def group_concat_max_len(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "groupConcatMaxLen"))

    @group_concat_max_len.setter
    def group_concat_max_len(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fd5cfa5d59341d19647ce9cd1566b9013d3429eba1f6923b04cf1ed66d41506e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "groupConcatMaxLen", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3ba1355371243ec588f37c8b02551c2b9244bcf96e3f27e9f1d987ebfd99a45d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="informationSchemaStatsExpiry")
    def information_schema_stats_expiry(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "informationSchemaStatsExpiry"))

    @information_schema_stats_expiry.setter
    def information_schema_stats_expiry(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__555c19ae655a5973ab96286fba44a24634631b2fd206fb371a071bb18331f605)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "informationSchemaStatsExpiry", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbFtMinTokenSize")
    def innodb_ft_min_token_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbFtMinTokenSize"))

    @innodb_ft_min_token_size.setter
    def innodb_ft_min_token_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d59fbf46b1852216fbde555e157b033d8e4ca560a69bf36840545b3f668fe6d7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbFtMinTokenSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbFtServerStopwordTable")
    def innodb_ft_server_stopword_table(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "innodbFtServerStopwordTable"))

    @innodb_ft_server_stopword_table.setter
    def innodb_ft_server_stopword_table(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__fa45c7be658da725d64dda2534f7fef3ef40b9cdc62a6ea5e9a3dace0cf34d9d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbFtServerStopwordTable", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbLockWaitTimeout")
    def innodb_lock_wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbLockWaitTimeout"))

    @innodb_lock_wait_timeout.setter
    def innodb_lock_wait_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e1d00e09b0af16c9b0fdf2db84a3e619e45880b71da3392522362f18f98b9b9c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbLockWaitTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbLogBufferSize")
    def innodb_log_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbLogBufferSize"))

    @innodb_log_buffer_size.setter
    def innodb_log_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9131dd1c6a47e92612f2395da03cd4df2e359d0a9ccc02e418850bc0c4001d37)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbLogBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbOnlineAlterLogMaxSize")
    def innodb_online_alter_log_max_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "innodbOnlineAlterLogMaxSize"))

    @innodb_online_alter_log_max_size.setter
    def innodb_online_alter_log_max_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__13401d662f819a127eae2f2a882452e306d21ddcc67d166209c5af1360228c57)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbOnlineAlterLogMaxSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbPrintAllDeadlocks")
    def innodb_print_all_deadlocks(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "innodbPrintAllDeadlocks"))

    @innodb_print_all_deadlocks.setter
    def innodb_print_all_deadlocks(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5bd8adfa75eb64dafef268615fc36796dfd09bed0c52883bd1b1a29a4efcc1c5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbPrintAllDeadlocks", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="innodbRollbackOnTimeout")
    def innodb_rollback_on_timeout(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "innodbRollbackOnTimeout"))

    @innodb_rollback_on_timeout.setter
    def innodb_rollback_on_timeout(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e8b573253fd8e6d27c977288c28bf8090286925ec31792f64a9acd6ff56d0e5e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "innodbRollbackOnTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="interactiveTimeout")
    def interactive_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "interactiveTimeout"))

    @interactive_timeout.setter
    def interactive_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__570f0e4af7e0d018c81561a9617085338c40dfe983b8947e74953a1f185adc60)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "interactiveTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalTmpMemStorageEngine")
    def internal_tmp_mem_storage_engine(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "internalTmpMemStorageEngine"))

    @internal_tmp_mem_storage_engine.setter
    def internal_tmp_mem_storage_engine(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__549077d29d3f89a8b0492a15cf5736d4b0df84e11c115800c1525c94c1fae585)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalTmpMemStorageEngine", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="longQueryTime")
    def long_query_time(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "longQueryTime"))

    @long_query_time.setter
    def long_query_time(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af39d82a158517a99c15bd63bd8220fe18a335bf1a0409179c6e9edc37f91466)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "longQueryTime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxAllowedPacket")
    def max_allowed_packet(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxAllowedPacket"))

    @max_allowed_packet.setter
    def max_allowed_packet(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45a8ba20565d2e003c0b8c7029aaa61e40499fad768c5489a6f02b929fcaf7bf)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxAllowedPacket", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxHeapTableSize")
    def max_heap_table_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxHeapTableSize"))

    @max_heap_table_size.setter
    def max_heap_table_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__30a5761ec00b11b093edf25cb84b0f276348ccc44232ca45b7b6be15dd077823)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxHeapTableSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netReadTimeout")
    def net_read_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netReadTimeout"))

    @net_read_timeout.setter
    def net_read_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bc7c9aea3d71f21027c2a8a6b9a62dfe94158541d0a855ded779f9c4ef67882d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netReadTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="netWriteTimeout")
    def net_write_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "netWriteTimeout"))

    @net_write_timeout.setter
    def net_write_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5573557eb919697cc7fd0b74acd53c15c5d51d5ff29902a6bf13d92157ae10ac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "netWriteTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="slowQueryLog")
    def slow_query_log(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "slowQueryLog"))

    @slow_query_log.setter
    def slow_query_log(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1647285b3c56975106df296b2ce50f669fcac2013eeffc202c337403378b4775)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "slowQueryLog", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sortBufferSize")
    def sort_buffer_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sortBufferSize"))

    @sort_buffer_size.setter
    def sort_buffer_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f50434fb392299150506d2c74e1e93f6d99a11ccde08ec3847ae2f2a25b80ef)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sortBufferSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlMode")
    def sql_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "sqlMode"))

    @sql_mode.setter
    def sql_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c604263f1502ffb3db4d7eb0558e9b66ac60c30d7fab92b01799cc99941bcce3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sqlRequirePrimaryKey")
    def sql_require_primary_key(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "sqlRequirePrimaryKey"))

    @sql_require_primary_key.setter
    def sql_require_primary_key(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__75ac513fdaa48c85eb057d10213f205c8c5eaa9c087a06322dc87d69bbde4b9f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sqlRequirePrimaryKey", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tmpTableSize")
    def tmp_table_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tmpTableSize"))

    @tmp_table_size.setter
    def tmp_table_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2bca463b95a02402a331d481fa35454e37bd6d6bece69f88c6eca2d97b865a67)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tmpTableSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="waitTimeout")
    def wait_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "waitTimeout"))

    @wait_timeout.setter
    def wait_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c4e15dff7650ae7eeba2fef0668c7be19896144aac74c32f7d87df190f9c2b2a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "waitTimeout", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databaseMysqlConfig.DatabaseMysqlConfigConfig",
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
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "binlog_retention_period": "binlogRetentionPeriod",
        "connect_timeout": "connectTimeout",
        "default_time_zone": "defaultTimeZone",
        "group_concat_max_len": "groupConcatMaxLen",
        "id": "id",
        "information_schema_stats_expiry": "informationSchemaStatsExpiry",
        "innodb_ft_min_token_size": "innodbFtMinTokenSize",
        "innodb_ft_server_stopword_table": "innodbFtServerStopwordTable",
        "innodb_lock_wait_timeout": "innodbLockWaitTimeout",
        "innodb_log_buffer_size": "innodbLogBufferSize",
        "innodb_online_alter_log_max_size": "innodbOnlineAlterLogMaxSize",
        "innodb_print_all_deadlocks": "innodbPrintAllDeadlocks",
        "innodb_rollback_on_timeout": "innodbRollbackOnTimeout",
        "interactive_timeout": "interactiveTimeout",
        "internal_tmp_mem_storage_engine": "internalTmpMemStorageEngine",
        "long_query_time": "longQueryTime",
        "max_allowed_packet": "maxAllowedPacket",
        "max_heap_table_size": "maxHeapTableSize",
        "net_read_timeout": "netReadTimeout",
        "net_write_timeout": "netWriteTimeout",
        "slow_query_log": "slowQueryLog",
        "sort_buffer_size": "sortBufferSize",
        "sql_mode": "sqlMode",
        "sql_require_primary_key": "sqlRequirePrimaryKey",
        "tmp_table_size": "tmpTableSize",
        "wait_timeout": "waitTimeout",
    },
)
class DatabaseMysqlConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        binlog_retention_period: typing.Optional[jsii.Number] = None,
        connect_timeout: typing.Optional[jsii.Number] = None,
        default_time_zone: typing.Optional[builtins.str] = None,
        group_concat_max_len: typing.Optional[jsii.Number] = None,
        id: typing.Optional[builtins.str] = None,
        information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
        innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
        innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
        innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
        innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
        innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
        innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        interactive_timeout: typing.Optional[jsii.Number] = None,
        internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
        long_query_time: typing.Optional[jsii.Number] = None,
        max_allowed_packet: typing.Optional[jsii.Number] = None,
        max_heap_table_size: typing.Optional[jsii.Number] = None,
        net_read_timeout: typing.Optional[jsii.Number] = None,
        net_write_timeout: typing.Optional[jsii.Number] = None,
        slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        sort_buffer_size: typing.Optional[jsii.Number] = None,
        sql_mode: typing.Optional[builtins.str] = None,
        sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        tmp_table_size: typing.Optional[jsii.Number] = None,
        wait_timeout: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#cluster_id DatabaseMysqlConfig#cluster_id}.
        :param backup_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#backup_hour DatabaseMysqlConfig#backup_hour}.
        :param backup_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#backup_minute DatabaseMysqlConfig#backup_minute}.
        :param binlog_retention_period: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#binlog_retention_period DatabaseMysqlConfig#binlog_retention_period}.
        :param connect_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#connect_timeout DatabaseMysqlConfig#connect_timeout}.
        :param default_time_zone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#default_time_zone DatabaseMysqlConfig#default_time_zone}.
        :param group_concat_max_len: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#group_concat_max_len DatabaseMysqlConfig#group_concat_max_len}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#id DatabaseMysqlConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param information_schema_stats_expiry: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#information_schema_stats_expiry DatabaseMysqlConfig#information_schema_stats_expiry}.
        :param innodb_ft_min_token_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_ft_min_token_size DatabaseMysqlConfig#innodb_ft_min_token_size}.
        :param innodb_ft_server_stopword_table: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_ft_server_stopword_table DatabaseMysqlConfig#innodb_ft_server_stopword_table}.
        :param innodb_lock_wait_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_lock_wait_timeout DatabaseMysqlConfig#innodb_lock_wait_timeout}.
        :param innodb_log_buffer_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_log_buffer_size DatabaseMysqlConfig#innodb_log_buffer_size}.
        :param innodb_online_alter_log_max_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_online_alter_log_max_size DatabaseMysqlConfig#innodb_online_alter_log_max_size}.
        :param innodb_print_all_deadlocks: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_print_all_deadlocks DatabaseMysqlConfig#innodb_print_all_deadlocks}.
        :param innodb_rollback_on_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_rollback_on_timeout DatabaseMysqlConfig#innodb_rollback_on_timeout}.
        :param interactive_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#interactive_timeout DatabaseMysqlConfig#interactive_timeout}.
        :param internal_tmp_mem_storage_engine: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#internal_tmp_mem_storage_engine DatabaseMysqlConfig#internal_tmp_mem_storage_engine}.
        :param long_query_time: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#long_query_time DatabaseMysqlConfig#long_query_time}.
        :param max_allowed_packet: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#max_allowed_packet DatabaseMysqlConfig#max_allowed_packet}.
        :param max_heap_table_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#max_heap_table_size DatabaseMysqlConfig#max_heap_table_size}.
        :param net_read_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#net_read_timeout DatabaseMysqlConfig#net_read_timeout}.
        :param net_write_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#net_write_timeout DatabaseMysqlConfig#net_write_timeout}.
        :param slow_query_log: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#slow_query_log DatabaseMysqlConfig#slow_query_log}.
        :param sort_buffer_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sort_buffer_size DatabaseMysqlConfig#sort_buffer_size}.
        :param sql_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sql_mode DatabaseMysqlConfig#sql_mode}.
        :param sql_require_primary_key: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sql_require_primary_key DatabaseMysqlConfig#sql_require_primary_key}.
        :param tmp_table_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#tmp_table_size DatabaseMysqlConfig#tmp_table_size}.
        :param wait_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#wait_timeout DatabaseMysqlConfig#wait_timeout}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1262baf3cb3035b672daa9c25cca9ecc026b7142fbfb54dd062aeb617bb0e59b)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument backup_hour", value=backup_hour, expected_type=type_hints["backup_hour"])
            check_type(argname="argument backup_minute", value=backup_minute, expected_type=type_hints["backup_minute"])
            check_type(argname="argument binlog_retention_period", value=binlog_retention_period, expected_type=type_hints["binlog_retention_period"])
            check_type(argname="argument connect_timeout", value=connect_timeout, expected_type=type_hints["connect_timeout"])
            check_type(argname="argument default_time_zone", value=default_time_zone, expected_type=type_hints["default_time_zone"])
            check_type(argname="argument group_concat_max_len", value=group_concat_max_len, expected_type=type_hints["group_concat_max_len"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument information_schema_stats_expiry", value=information_schema_stats_expiry, expected_type=type_hints["information_schema_stats_expiry"])
            check_type(argname="argument innodb_ft_min_token_size", value=innodb_ft_min_token_size, expected_type=type_hints["innodb_ft_min_token_size"])
            check_type(argname="argument innodb_ft_server_stopword_table", value=innodb_ft_server_stopword_table, expected_type=type_hints["innodb_ft_server_stopword_table"])
            check_type(argname="argument innodb_lock_wait_timeout", value=innodb_lock_wait_timeout, expected_type=type_hints["innodb_lock_wait_timeout"])
            check_type(argname="argument innodb_log_buffer_size", value=innodb_log_buffer_size, expected_type=type_hints["innodb_log_buffer_size"])
            check_type(argname="argument innodb_online_alter_log_max_size", value=innodb_online_alter_log_max_size, expected_type=type_hints["innodb_online_alter_log_max_size"])
            check_type(argname="argument innodb_print_all_deadlocks", value=innodb_print_all_deadlocks, expected_type=type_hints["innodb_print_all_deadlocks"])
            check_type(argname="argument innodb_rollback_on_timeout", value=innodb_rollback_on_timeout, expected_type=type_hints["innodb_rollback_on_timeout"])
            check_type(argname="argument interactive_timeout", value=interactive_timeout, expected_type=type_hints["interactive_timeout"])
            check_type(argname="argument internal_tmp_mem_storage_engine", value=internal_tmp_mem_storage_engine, expected_type=type_hints["internal_tmp_mem_storage_engine"])
            check_type(argname="argument long_query_time", value=long_query_time, expected_type=type_hints["long_query_time"])
            check_type(argname="argument max_allowed_packet", value=max_allowed_packet, expected_type=type_hints["max_allowed_packet"])
            check_type(argname="argument max_heap_table_size", value=max_heap_table_size, expected_type=type_hints["max_heap_table_size"])
            check_type(argname="argument net_read_timeout", value=net_read_timeout, expected_type=type_hints["net_read_timeout"])
            check_type(argname="argument net_write_timeout", value=net_write_timeout, expected_type=type_hints["net_write_timeout"])
            check_type(argname="argument slow_query_log", value=slow_query_log, expected_type=type_hints["slow_query_log"])
            check_type(argname="argument sort_buffer_size", value=sort_buffer_size, expected_type=type_hints["sort_buffer_size"])
            check_type(argname="argument sql_mode", value=sql_mode, expected_type=type_hints["sql_mode"])
            check_type(argname="argument sql_require_primary_key", value=sql_require_primary_key, expected_type=type_hints["sql_require_primary_key"])
            check_type(argname="argument tmp_table_size", value=tmp_table_size, expected_type=type_hints["tmp_table_size"])
            check_type(argname="argument wait_timeout", value=wait_timeout, expected_type=type_hints["wait_timeout"])
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
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if binlog_retention_period is not None:
            self._values["binlog_retention_period"] = binlog_retention_period
        if connect_timeout is not None:
            self._values["connect_timeout"] = connect_timeout
        if default_time_zone is not None:
            self._values["default_time_zone"] = default_time_zone
        if group_concat_max_len is not None:
            self._values["group_concat_max_len"] = group_concat_max_len
        if id is not None:
            self._values["id"] = id
        if information_schema_stats_expiry is not None:
            self._values["information_schema_stats_expiry"] = information_schema_stats_expiry
        if innodb_ft_min_token_size is not None:
            self._values["innodb_ft_min_token_size"] = innodb_ft_min_token_size
        if innodb_ft_server_stopword_table is not None:
            self._values["innodb_ft_server_stopword_table"] = innodb_ft_server_stopword_table
        if innodb_lock_wait_timeout is not None:
            self._values["innodb_lock_wait_timeout"] = innodb_lock_wait_timeout
        if innodb_log_buffer_size is not None:
            self._values["innodb_log_buffer_size"] = innodb_log_buffer_size
        if innodb_online_alter_log_max_size is not None:
            self._values["innodb_online_alter_log_max_size"] = innodb_online_alter_log_max_size
        if innodb_print_all_deadlocks is not None:
            self._values["innodb_print_all_deadlocks"] = innodb_print_all_deadlocks
        if innodb_rollback_on_timeout is not None:
            self._values["innodb_rollback_on_timeout"] = innodb_rollback_on_timeout
        if interactive_timeout is not None:
            self._values["interactive_timeout"] = interactive_timeout
        if internal_tmp_mem_storage_engine is not None:
            self._values["internal_tmp_mem_storage_engine"] = internal_tmp_mem_storage_engine
        if long_query_time is not None:
            self._values["long_query_time"] = long_query_time
        if max_allowed_packet is not None:
            self._values["max_allowed_packet"] = max_allowed_packet
        if max_heap_table_size is not None:
            self._values["max_heap_table_size"] = max_heap_table_size
        if net_read_timeout is not None:
            self._values["net_read_timeout"] = net_read_timeout
        if net_write_timeout is not None:
            self._values["net_write_timeout"] = net_write_timeout
        if slow_query_log is not None:
            self._values["slow_query_log"] = slow_query_log
        if sort_buffer_size is not None:
            self._values["sort_buffer_size"] = sort_buffer_size
        if sql_mode is not None:
            self._values["sql_mode"] = sql_mode
        if sql_require_primary_key is not None:
            self._values["sql_require_primary_key"] = sql_require_primary_key
        if tmp_table_size is not None:
            self._values["tmp_table_size"] = tmp_table_size
        if wait_timeout is not None:
            self._values["wait_timeout"] = wait_timeout

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#cluster_id DatabaseMysqlConfig#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#backup_hour DatabaseMysqlConfig#backup_hour}.'''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#backup_minute DatabaseMysqlConfig#backup_minute}.'''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def binlog_retention_period(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#binlog_retention_period DatabaseMysqlConfig#binlog_retention_period}.'''
        result = self._values.get("binlog_retention_period")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def connect_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#connect_timeout DatabaseMysqlConfig#connect_timeout}.'''
        result = self._values.get("connect_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_time_zone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#default_time_zone DatabaseMysqlConfig#default_time_zone}.'''
        result = self._values.get("default_time_zone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def group_concat_max_len(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#group_concat_max_len DatabaseMysqlConfig#group_concat_max_len}.'''
        result = self._values.get("group_concat_max_len")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#id DatabaseMysqlConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def information_schema_stats_expiry(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#information_schema_stats_expiry DatabaseMysqlConfig#information_schema_stats_expiry}.'''
        result = self._values.get("information_schema_stats_expiry")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_ft_min_token_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_ft_min_token_size DatabaseMysqlConfig#innodb_ft_min_token_size}.'''
        result = self._values.get("innodb_ft_min_token_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_ft_server_stopword_table(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_ft_server_stopword_table DatabaseMysqlConfig#innodb_ft_server_stopword_table}.'''
        result = self._values.get("innodb_ft_server_stopword_table")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def innodb_lock_wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_lock_wait_timeout DatabaseMysqlConfig#innodb_lock_wait_timeout}.'''
        result = self._values.get("innodb_lock_wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_log_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_log_buffer_size DatabaseMysqlConfig#innodb_log_buffer_size}.'''
        result = self._values.get("innodb_log_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_online_alter_log_max_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_online_alter_log_max_size DatabaseMysqlConfig#innodb_online_alter_log_max_size}.'''
        result = self._values.get("innodb_online_alter_log_max_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def innodb_print_all_deadlocks(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_print_all_deadlocks DatabaseMysqlConfig#innodb_print_all_deadlocks}.'''
        result = self._values.get("innodb_print_all_deadlocks")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def innodb_rollback_on_timeout(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#innodb_rollback_on_timeout DatabaseMysqlConfig#innodb_rollback_on_timeout}.'''
        result = self._values.get("innodb_rollback_on_timeout")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def interactive_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#interactive_timeout DatabaseMysqlConfig#interactive_timeout}.'''
        result = self._values.get("interactive_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def internal_tmp_mem_storage_engine(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#internal_tmp_mem_storage_engine DatabaseMysqlConfig#internal_tmp_mem_storage_engine}.'''
        result = self._values.get("internal_tmp_mem_storage_engine")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def long_query_time(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#long_query_time DatabaseMysqlConfig#long_query_time}.'''
        result = self._values.get("long_query_time")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_allowed_packet(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#max_allowed_packet DatabaseMysqlConfig#max_allowed_packet}.'''
        result = self._values.get("max_allowed_packet")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_heap_table_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#max_heap_table_size DatabaseMysqlConfig#max_heap_table_size}.'''
        result = self._values.get("max_heap_table_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def net_read_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#net_read_timeout DatabaseMysqlConfig#net_read_timeout}.'''
        result = self._values.get("net_read_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def net_write_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#net_write_timeout DatabaseMysqlConfig#net_write_timeout}.'''
        result = self._values.get("net_write_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def slow_query_log(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#slow_query_log DatabaseMysqlConfig#slow_query_log}.'''
        result = self._values.get("slow_query_log")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def sort_buffer_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sort_buffer_size DatabaseMysqlConfig#sort_buffer_size}.'''
        result = self._values.get("sort_buffer_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def sql_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sql_mode DatabaseMysqlConfig#sql_mode}.'''
        result = self._values.get("sql_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def sql_require_primary_key(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#sql_require_primary_key DatabaseMysqlConfig#sql_require_primary_key}.'''
        result = self._values.get("sql_require_primary_key")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def tmp_table_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#tmp_table_size DatabaseMysqlConfig#tmp_table_size}.'''
        result = self._values.get("tmp_table_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def wait_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_mysql_config#wait_timeout DatabaseMysqlConfig#wait_timeout}.'''
        result = self._values.get("wait_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabaseMysqlConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DatabaseMysqlConfig",
    "DatabaseMysqlConfigConfig",
]

publication.publish()

def _typecheckingstub__d4ad3c49940b908d433860913c22510a475efb6f1f25e5643e3e7edb0472908b(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    binlog_retention_period: typing.Optional[jsii.Number] = None,
    connect_timeout: typing.Optional[jsii.Number] = None,
    default_time_zone: typing.Optional[builtins.str] = None,
    group_concat_max_len: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
    innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
    innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
    innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
    innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
    innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
    innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    interactive_timeout: typing.Optional[jsii.Number] = None,
    internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
    long_query_time: typing.Optional[jsii.Number] = None,
    max_allowed_packet: typing.Optional[jsii.Number] = None,
    max_heap_table_size: typing.Optional[jsii.Number] = None,
    net_read_timeout: typing.Optional[jsii.Number] = None,
    net_write_timeout: typing.Optional[jsii.Number] = None,
    slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sort_buffer_size: typing.Optional[jsii.Number] = None,
    sql_mode: typing.Optional[builtins.str] = None,
    sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tmp_table_size: typing.Optional[jsii.Number] = None,
    wait_timeout: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__695b8acfeee0ceb65c82f993879bc119b73a4b5cc0d7cf144300764d70dcb3c7(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f13fceacd969e659201e5682c153cbb34c6bab1d13452726997047883040ffc2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__17085ec1a7b6adcfe438b7dbbfdac5323901c5f53f4ae2a7abbc39421dadc1d6(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfbf39674c1f42b5f7743335875489da78e4ce410e34276b6a95d55e8d0544b0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa3211b627a4919734f153ed8a2adeb11b3d310cffc2b603c116514edefb5cfa(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cf302982893e609f3c1ffbc6bb300c4cc5303e5a58b9428bd961b138d59d9bbf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__db9c8ac48d5f348b17ab5d14e250a1d84437bfb9f4136eb05ec8ddbc5478364e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fd5cfa5d59341d19647ce9cd1566b9013d3429eba1f6923b04cf1ed66d41506e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3ba1355371243ec588f37c8b02551c2b9244bcf96e3f27e9f1d987ebfd99a45d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__555c19ae655a5973ab96286fba44a24634631b2fd206fb371a071bb18331f605(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d59fbf46b1852216fbde555e157b033d8e4ca560a69bf36840545b3f668fe6d7(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__fa45c7be658da725d64dda2534f7fef3ef40b9cdc62a6ea5e9a3dace0cf34d9d(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e1d00e09b0af16c9b0fdf2db84a3e619e45880b71da3392522362f18f98b9b9c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9131dd1c6a47e92612f2395da03cd4df2e359d0a9ccc02e418850bc0c4001d37(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__13401d662f819a127eae2f2a882452e306d21ddcc67d166209c5af1360228c57(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5bd8adfa75eb64dafef268615fc36796dfd09bed0c52883bd1b1a29a4efcc1c5(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e8b573253fd8e6d27c977288c28bf8090286925ec31792f64a9acd6ff56d0e5e(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__570f0e4af7e0d018c81561a9617085338c40dfe983b8947e74953a1f185adc60(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__549077d29d3f89a8b0492a15cf5736d4b0df84e11c115800c1525c94c1fae585(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af39d82a158517a99c15bd63bd8220fe18a335bf1a0409179c6e9edc37f91466(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45a8ba20565d2e003c0b8c7029aaa61e40499fad768c5489a6f02b929fcaf7bf(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__30a5761ec00b11b093edf25cb84b0f276348ccc44232ca45b7b6be15dd077823(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bc7c9aea3d71f21027c2a8a6b9a62dfe94158541d0a855ded779f9c4ef67882d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5573557eb919697cc7fd0b74acd53c15c5d51d5ff29902a6bf13d92157ae10ac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1647285b3c56975106df296b2ce50f669fcac2013eeffc202c337403378b4775(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f50434fb392299150506d2c74e1e93f6d99a11ccde08ec3847ae2f2a25b80ef(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c604263f1502ffb3db4d7eb0558e9b66ac60c30d7fab92b01799cc99941bcce3(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__75ac513fdaa48c85eb057d10213f205c8c5eaa9c087a06322dc87d69bbde4b9f(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2bca463b95a02402a331d481fa35454e37bd6d6bece69f88c6eca2d97b865a67(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c4e15dff7650ae7eeba2fef0668c7be19896144aac74c32f7d87df190f9c2b2a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1262baf3cb3035b672daa9c25cca9ecc026b7142fbfb54dd062aeb617bb0e59b(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    binlog_retention_period: typing.Optional[jsii.Number] = None,
    connect_timeout: typing.Optional[jsii.Number] = None,
    default_time_zone: typing.Optional[builtins.str] = None,
    group_concat_max_len: typing.Optional[jsii.Number] = None,
    id: typing.Optional[builtins.str] = None,
    information_schema_stats_expiry: typing.Optional[jsii.Number] = None,
    innodb_ft_min_token_size: typing.Optional[jsii.Number] = None,
    innodb_ft_server_stopword_table: typing.Optional[builtins.str] = None,
    innodb_lock_wait_timeout: typing.Optional[jsii.Number] = None,
    innodb_log_buffer_size: typing.Optional[jsii.Number] = None,
    innodb_online_alter_log_max_size: typing.Optional[jsii.Number] = None,
    innodb_print_all_deadlocks: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    innodb_rollback_on_timeout: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    interactive_timeout: typing.Optional[jsii.Number] = None,
    internal_tmp_mem_storage_engine: typing.Optional[builtins.str] = None,
    long_query_time: typing.Optional[jsii.Number] = None,
    max_allowed_packet: typing.Optional[jsii.Number] = None,
    max_heap_table_size: typing.Optional[jsii.Number] = None,
    net_read_timeout: typing.Optional[jsii.Number] = None,
    net_write_timeout: typing.Optional[jsii.Number] = None,
    slow_query_log: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    sort_buffer_size: typing.Optional[jsii.Number] = None,
    sql_mode: typing.Optional[builtins.str] = None,
    sql_require_primary_key: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    tmp_table_size: typing.Optional[jsii.Number] = None,
    wait_timeout: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass
