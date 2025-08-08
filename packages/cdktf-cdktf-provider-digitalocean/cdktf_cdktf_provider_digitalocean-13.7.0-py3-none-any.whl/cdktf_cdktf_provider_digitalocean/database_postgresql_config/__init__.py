r'''
# `digitalocean_database_postgresql_config`

Refer to the Terraform Registry for docs: [`digitalocean_database_postgresql_config`](https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config).
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


class DatabasePostgresqlConfig(
    _cdktf_9a9027ec.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfig",
):
    '''Represents a {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config digitalocean_database_postgresql_config}.'''

    def __init__(
        self,
        scope: _constructs_77d1e7e8.Construct,
        id_: builtins.str,
        *,
        cluster_id: builtins.str,
        autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
        autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
        autovacuum_max_workers: typing.Optional[jsii.Number] = None,
        autovacuum_naptime: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        bgwriter_delay: typing.Optional[jsii.Number] = None,
        bgwriter_flush_after: typing.Optional[jsii.Number] = None,
        bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
        bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
        deadlock_timeout: typing.Optional[jsii.Number] = None,
        default_toast_compression: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
        jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
        log_error_verbosity: typing.Optional[builtins.str] = None,
        log_line_prefix: typing.Optional[builtins.str] = None,
        log_min_duration_statement: typing.Optional[jsii.Number] = None,
        max_files_per_process: typing.Optional[jsii.Number] = None,
        max_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_logical_replication_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
        max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_prepared_transactions: typing.Optional[jsii.Number] = None,
        max_replication_slots: typing.Optional[jsii.Number] = None,
        max_stack_depth: typing.Optional[jsii.Number] = None,
        max_standby_archive_delay: typing.Optional[jsii.Number] = None,
        max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
        max_wal_senders: typing.Optional[jsii.Number] = None,
        max_worker_processes: typing.Optional[jsii.Number] = None,
        pgbouncer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DatabasePostgresqlConfigPgbouncer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
        pg_partman_bgw_role: typing.Optional[builtins.str] = None,
        pg_stat_statements_track: typing.Optional[builtins.str] = None,
        shared_buffers_percentage: typing.Optional[jsii.Number] = None,
        temp_file_limit: typing.Optional[jsii.Number] = None,
        timescaledb: typing.Optional[typing.Union["DatabasePostgresqlConfigTimescaledb", typing.Dict[builtins.str, typing.Any]]] = None,
        timezone: typing.Optional[builtins.str] = None,
        track_activity_query_size: typing.Optional[jsii.Number] = None,
        track_commit_timestamp: typing.Optional[builtins.str] = None,
        track_functions: typing.Optional[builtins.str] = None,
        track_io_timing: typing.Optional[builtins.str] = None,
        wal_sender_timeout: typing.Optional[jsii.Number] = None,
        wal_writer_delay: typing.Optional[jsii.Number] = None,
        work_mem: typing.Optional[jsii.Number] = None,
        connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
        count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
        depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
        for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
        provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    ) -> None:
        '''Create a new {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config digitalocean_database_postgresql_config} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#cluster_id DatabasePostgresqlConfig#cluster_id}.
        :param autovacuum_analyze_scale_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_analyze_scale_factor DatabasePostgresqlConfig#autovacuum_analyze_scale_factor}.
        :param autovacuum_analyze_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_analyze_threshold DatabasePostgresqlConfig#autovacuum_analyze_threshold}.
        :param autovacuum_freeze_max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_freeze_max_age DatabasePostgresqlConfig#autovacuum_freeze_max_age}.
        :param autovacuum_max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_max_workers DatabasePostgresqlConfig#autovacuum_max_workers}.
        :param autovacuum_naptime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_naptime DatabasePostgresqlConfig#autovacuum_naptime}.
        :param autovacuum_vacuum_cost_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_cost_delay DatabasePostgresqlConfig#autovacuum_vacuum_cost_delay}.
        :param autovacuum_vacuum_cost_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_cost_limit DatabasePostgresqlConfig#autovacuum_vacuum_cost_limit}.
        :param autovacuum_vacuum_scale_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_scale_factor DatabasePostgresqlConfig#autovacuum_vacuum_scale_factor}.
        :param autovacuum_vacuum_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_threshold DatabasePostgresqlConfig#autovacuum_vacuum_threshold}.
        :param backup_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#backup_hour DatabasePostgresqlConfig#backup_hour}.
        :param backup_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#backup_minute DatabasePostgresqlConfig#backup_minute}.
        :param bgwriter_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_delay DatabasePostgresqlConfig#bgwriter_delay}.
        :param bgwriter_flush_after: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_flush_after DatabasePostgresqlConfig#bgwriter_flush_after}.
        :param bgwriter_lru_maxpages: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_lru_maxpages DatabasePostgresqlConfig#bgwriter_lru_maxpages}.
        :param bgwriter_lru_multiplier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_lru_multiplier DatabasePostgresqlConfig#bgwriter_lru_multiplier}.
        :param deadlock_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#deadlock_timeout DatabasePostgresqlConfig#deadlock_timeout}.
        :param default_toast_compression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#default_toast_compression DatabasePostgresqlConfig#default_toast_compression}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#id DatabasePostgresqlConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idle_in_transaction_session_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#idle_in_transaction_session_timeout DatabasePostgresqlConfig#idle_in_transaction_session_timeout}.
        :param jit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#jit DatabasePostgresqlConfig#jit}.
        :param log_autovacuum_min_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_autovacuum_min_duration DatabasePostgresqlConfig#log_autovacuum_min_duration}.
        :param log_error_verbosity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_error_verbosity DatabasePostgresqlConfig#log_error_verbosity}.
        :param log_line_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_line_prefix DatabasePostgresqlConfig#log_line_prefix}.
        :param log_min_duration_statement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_min_duration_statement DatabasePostgresqlConfig#log_min_duration_statement}.
        :param max_files_per_process: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_files_per_process DatabasePostgresqlConfig#max_files_per_process}.
        :param max_locks_per_transaction: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_locks_per_transaction DatabasePostgresqlConfig#max_locks_per_transaction}.
        :param max_logical_replication_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_logical_replication_workers DatabasePostgresqlConfig#max_logical_replication_workers}.
        :param max_parallel_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_parallel_workers DatabasePostgresqlConfig#max_parallel_workers}.
        :param max_parallel_workers_per_gather: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_parallel_workers_per_gather DatabasePostgresqlConfig#max_parallel_workers_per_gather}.
        :param max_pred_locks_per_transaction: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_pred_locks_per_transaction DatabasePostgresqlConfig#max_pred_locks_per_transaction}.
        :param max_prepared_transactions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_prepared_transactions DatabasePostgresqlConfig#max_prepared_transactions}.
        :param max_replication_slots: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_replication_slots DatabasePostgresqlConfig#max_replication_slots}.
        :param max_stack_depth: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_stack_depth DatabasePostgresqlConfig#max_stack_depth}.
        :param max_standby_archive_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_standby_archive_delay DatabasePostgresqlConfig#max_standby_archive_delay}.
        :param max_standby_streaming_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_standby_streaming_delay DatabasePostgresqlConfig#max_standby_streaming_delay}.
        :param max_wal_senders: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_wal_senders DatabasePostgresqlConfig#max_wal_senders}.
        :param max_worker_processes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_worker_processes DatabasePostgresqlConfig#max_worker_processes}.
        :param pgbouncer: pgbouncer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pgbouncer DatabasePostgresqlConfig#pgbouncer}
        :param pg_partman_bgw_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_partman_bgw_interval DatabasePostgresqlConfig#pg_partman_bgw_interval}.
        :param pg_partman_bgw_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_partman_bgw_role DatabasePostgresqlConfig#pg_partman_bgw_role}.
        :param pg_stat_statements_track: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_stat_statements_track DatabasePostgresqlConfig#pg_stat_statements_track}.
        :param shared_buffers_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#shared_buffers_percentage DatabasePostgresqlConfig#shared_buffers_percentage}.
        :param temp_file_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#temp_file_limit DatabasePostgresqlConfig#temp_file_limit}.
        :param timescaledb: timescaledb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#timescaledb DatabasePostgresqlConfig#timescaledb}
        :param timezone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#timezone DatabasePostgresqlConfig#timezone}.
        :param track_activity_query_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_activity_query_size DatabasePostgresqlConfig#track_activity_query_size}.
        :param track_commit_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_commit_timestamp DatabasePostgresqlConfig#track_commit_timestamp}.
        :param track_functions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_functions DatabasePostgresqlConfig#track_functions}.
        :param track_io_timing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_io_timing DatabasePostgresqlConfig#track_io_timing}.
        :param wal_sender_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#wal_sender_timeout DatabasePostgresqlConfig#wal_sender_timeout}.
        :param wal_writer_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#wal_writer_delay DatabasePostgresqlConfig#wal_writer_delay}.
        :param work_mem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#work_mem DatabasePostgresqlConfig#work_mem}.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__36ae334279827dd362dc523f8365017d681274f272f4887907413e59112c65ce)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = DatabasePostgresqlConfigConfig(
            cluster_id=cluster_id,
            autovacuum_analyze_scale_factor=autovacuum_analyze_scale_factor,
            autovacuum_analyze_threshold=autovacuum_analyze_threshold,
            autovacuum_freeze_max_age=autovacuum_freeze_max_age,
            autovacuum_max_workers=autovacuum_max_workers,
            autovacuum_naptime=autovacuum_naptime,
            autovacuum_vacuum_cost_delay=autovacuum_vacuum_cost_delay,
            autovacuum_vacuum_cost_limit=autovacuum_vacuum_cost_limit,
            autovacuum_vacuum_scale_factor=autovacuum_vacuum_scale_factor,
            autovacuum_vacuum_threshold=autovacuum_vacuum_threshold,
            backup_hour=backup_hour,
            backup_minute=backup_minute,
            bgwriter_delay=bgwriter_delay,
            bgwriter_flush_after=bgwriter_flush_after,
            bgwriter_lru_maxpages=bgwriter_lru_maxpages,
            bgwriter_lru_multiplier=bgwriter_lru_multiplier,
            deadlock_timeout=deadlock_timeout,
            default_toast_compression=default_toast_compression,
            id=id,
            idle_in_transaction_session_timeout=idle_in_transaction_session_timeout,
            jit=jit,
            log_autovacuum_min_duration=log_autovacuum_min_duration,
            log_error_verbosity=log_error_verbosity,
            log_line_prefix=log_line_prefix,
            log_min_duration_statement=log_min_duration_statement,
            max_files_per_process=max_files_per_process,
            max_locks_per_transaction=max_locks_per_transaction,
            max_logical_replication_workers=max_logical_replication_workers,
            max_parallel_workers=max_parallel_workers,
            max_parallel_workers_per_gather=max_parallel_workers_per_gather,
            max_pred_locks_per_transaction=max_pred_locks_per_transaction,
            max_prepared_transactions=max_prepared_transactions,
            max_replication_slots=max_replication_slots,
            max_stack_depth=max_stack_depth,
            max_standby_archive_delay=max_standby_archive_delay,
            max_standby_streaming_delay=max_standby_streaming_delay,
            max_wal_senders=max_wal_senders,
            max_worker_processes=max_worker_processes,
            pgbouncer=pgbouncer,
            pg_partman_bgw_interval=pg_partman_bgw_interval,
            pg_partman_bgw_role=pg_partman_bgw_role,
            pg_stat_statements_track=pg_stat_statements_track,
            shared_buffers_percentage=shared_buffers_percentage,
            temp_file_limit=temp_file_limit,
            timescaledb=timescaledb,
            timezone=timezone,
            track_activity_query_size=track_activity_query_size,
            track_commit_timestamp=track_commit_timestamp,
            track_functions=track_functions,
            track_io_timing=track_io_timing,
            wal_sender_timeout=wal_sender_timeout,
            wal_writer_delay=wal_writer_delay,
            work_mem=work_mem,
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
        '''Generates CDKTF code for importing a DatabasePostgresqlConfig resource upon running "cdktf plan ".

        :param scope: The scope in which to define this construct.
        :param import_to_id: The construct id used in the generated config for the DatabasePostgresqlConfig to import.
        :param import_from_id: The id of the existing DatabasePostgresqlConfig that should be imported. Refer to the {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#import import section} in the documentation of this resource for the id to use
        :param provider: ? Optional instance of the provider where the DatabasePostgresqlConfig to import is found.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__560f9b24f98813ef980695c73cd2a9786636dbe7fb7628db347b2bcbed9f8cde)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument import_to_id", value=import_to_id, expected_type=type_hints["import_to_id"])
            check_type(argname="argument import_from_id", value=import_from_id, expected_type=type_hints["import_from_id"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
        return typing.cast(_cdktf_9a9027ec.ImportableResource, jsii.sinvoke(cls, "generateConfigForImport", [scope, import_to_id, import_from_id, provider]))

    @jsii.member(jsii_name="putPgbouncer")
    def put_pgbouncer(
        self,
        value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DatabasePostgresqlConfigPgbouncer", typing.Dict[builtins.str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__70f76af5b9ecf4195271bf2efcc29ff16185f0b28c5b6f2ff8a8397a9007cc6a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putPgbouncer", [value]))

    @jsii.member(jsii_name="putTimescaledb")
    def put_timescaledb(
        self,
        *,
        max_background_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_background_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_background_workers DatabasePostgresqlConfig#max_background_workers}.
        '''
        value = DatabasePostgresqlConfigTimescaledb(
            max_background_workers=max_background_workers
        )

        return typing.cast(None, jsii.invoke(self, "putTimescaledb", [value]))

    @jsii.member(jsii_name="resetAutovacuumAnalyzeScaleFactor")
    def reset_autovacuum_analyze_scale_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumAnalyzeScaleFactor", []))

    @jsii.member(jsii_name="resetAutovacuumAnalyzeThreshold")
    def reset_autovacuum_analyze_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumAnalyzeThreshold", []))

    @jsii.member(jsii_name="resetAutovacuumFreezeMaxAge")
    def reset_autovacuum_freeze_max_age(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumFreezeMaxAge", []))

    @jsii.member(jsii_name="resetAutovacuumMaxWorkers")
    def reset_autovacuum_max_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumMaxWorkers", []))

    @jsii.member(jsii_name="resetAutovacuumNaptime")
    def reset_autovacuum_naptime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumNaptime", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumCostDelay")
    def reset_autovacuum_vacuum_cost_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumCostDelay", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumCostLimit")
    def reset_autovacuum_vacuum_cost_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumCostLimit", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumScaleFactor")
    def reset_autovacuum_vacuum_scale_factor(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumScaleFactor", []))

    @jsii.member(jsii_name="resetAutovacuumVacuumThreshold")
    def reset_autovacuum_vacuum_threshold(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutovacuumVacuumThreshold", []))

    @jsii.member(jsii_name="resetBackupHour")
    def reset_backup_hour(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupHour", []))

    @jsii.member(jsii_name="resetBackupMinute")
    def reset_backup_minute(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBackupMinute", []))

    @jsii.member(jsii_name="resetBgwriterDelay")
    def reset_bgwriter_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterDelay", []))

    @jsii.member(jsii_name="resetBgwriterFlushAfter")
    def reset_bgwriter_flush_after(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterFlushAfter", []))

    @jsii.member(jsii_name="resetBgwriterLruMaxpages")
    def reset_bgwriter_lru_maxpages(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterLruMaxpages", []))

    @jsii.member(jsii_name="resetBgwriterLruMultiplier")
    def reset_bgwriter_lru_multiplier(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetBgwriterLruMultiplier", []))

    @jsii.member(jsii_name="resetDeadlockTimeout")
    def reset_deadlock_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDeadlockTimeout", []))

    @jsii.member(jsii_name="resetDefaultToastCompression")
    def reset_default_toast_compression(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDefaultToastCompression", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetIdleInTransactionSessionTimeout")
    def reset_idle_in_transaction_session_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIdleInTransactionSessionTimeout", []))

    @jsii.member(jsii_name="resetJit")
    def reset_jit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetJit", []))

    @jsii.member(jsii_name="resetLogAutovacuumMinDuration")
    def reset_log_autovacuum_min_duration(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogAutovacuumMinDuration", []))

    @jsii.member(jsii_name="resetLogErrorVerbosity")
    def reset_log_error_verbosity(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogErrorVerbosity", []))

    @jsii.member(jsii_name="resetLogLinePrefix")
    def reset_log_line_prefix(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogLinePrefix", []))

    @jsii.member(jsii_name="resetLogMinDurationStatement")
    def reset_log_min_duration_statement(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetLogMinDurationStatement", []))

    @jsii.member(jsii_name="resetMaxFilesPerProcess")
    def reset_max_files_per_process(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxFilesPerProcess", []))

    @jsii.member(jsii_name="resetMaxLocksPerTransaction")
    def reset_max_locks_per_transaction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLocksPerTransaction", []))

    @jsii.member(jsii_name="resetMaxLogicalReplicationWorkers")
    def reset_max_logical_replication_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxLogicalReplicationWorkers", []))

    @jsii.member(jsii_name="resetMaxParallelWorkers")
    def reset_max_parallel_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxParallelWorkers", []))

    @jsii.member(jsii_name="resetMaxParallelWorkersPerGather")
    def reset_max_parallel_workers_per_gather(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxParallelWorkersPerGather", []))

    @jsii.member(jsii_name="resetMaxPredLocksPerTransaction")
    def reset_max_pred_locks_per_transaction(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPredLocksPerTransaction", []))

    @jsii.member(jsii_name="resetMaxPreparedTransactions")
    def reset_max_prepared_transactions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxPreparedTransactions", []))

    @jsii.member(jsii_name="resetMaxReplicationSlots")
    def reset_max_replication_slots(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxReplicationSlots", []))

    @jsii.member(jsii_name="resetMaxStackDepth")
    def reset_max_stack_depth(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStackDepth", []))

    @jsii.member(jsii_name="resetMaxStandbyArchiveDelay")
    def reset_max_standby_archive_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStandbyArchiveDelay", []))

    @jsii.member(jsii_name="resetMaxStandbyStreamingDelay")
    def reset_max_standby_streaming_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxStandbyStreamingDelay", []))

    @jsii.member(jsii_name="resetMaxWalSenders")
    def reset_max_wal_senders(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWalSenders", []))

    @jsii.member(jsii_name="resetMaxWorkerProcesses")
    def reset_max_worker_processes(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxWorkerProcesses", []))

    @jsii.member(jsii_name="resetPgbouncer")
    def reset_pgbouncer(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgbouncer", []))

    @jsii.member(jsii_name="resetPgPartmanBgwInterval")
    def reset_pg_partman_bgw_interval(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgPartmanBgwInterval", []))

    @jsii.member(jsii_name="resetPgPartmanBgwRole")
    def reset_pg_partman_bgw_role(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgPartmanBgwRole", []))

    @jsii.member(jsii_name="resetPgStatStatementsTrack")
    def reset_pg_stat_statements_track(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPgStatStatementsTrack", []))

    @jsii.member(jsii_name="resetSharedBuffersPercentage")
    def reset_shared_buffers_percentage(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSharedBuffersPercentage", []))

    @jsii.member(jsii_name="resetTempFileLimit")
    def reset_temp_file_limit(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTempFileLimit", []))

    @jsii.member(jsii_name="resetTimescaledb")
    def reset_timescaledb(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimescaledb", []))

    @jsii.member(jsii_name="resetTimezone")
    def reset_timezone(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTimezone", []))

    @jsii.member(jsii_name="resetTrackActivityQuerySize")
    def reset_track_activity_query_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackActivityQuerySize", []))

    @jsii.member(jsii_name="resetTrackCommitTimestamp")
    def reset_track_commit_timestamp(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackCommitTimestamp", []))

    @jsii.member(jsii_name="resetTrackFunctions")
    def reset_track_functions(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackFunctions", []))

    @jsii.member(jsii_name="resetTrackIoTiming")
    def reset_track_io_timing(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTrackIoTiming", []))

    @jsii.member(jsii_name="resetWalSenderTimeout")
    def reset_wal_sender_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWalSenderTimeout", []))

    @jsii.member(jsii_name="resetWalWriterDelay")
    def reset_wal_writer_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWalWriterDelay", []))

    @jsii.member(jsii_name="resetWorkMem")
    def reset_work_mem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetWorkMem", []))

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
    @jsii.member(jsii_name="pgbouncer")
    def pgbouncer(self) -> "DatabasePostgresqlConfigPgbouncerList":
        return typing.cast("DatabasePostgresqlConfigPgbouncerList", jsii.get(self, "pgbouncer"))

    @builtins.property
    @jsii.member(jsii_name="timescaledb")
    def timescaledb(self) -> "DatabasePostgresqlConfigTimescaledbOutputReference":
        return typing.cast("DatabasePostgresqlConfigTimescaledbOutputReference", jsii.get(self, "timescaledb"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeScaleFactorInput")
    def autovacuum_analyze_scale_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumAnalyzeScaleFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeThresholdInput")
    def autovacuum_analyze_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumAnalyzeThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumFreezeMaxAgeInput")
    def autovacuum_freeze_max_age_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumFreezeMaxAgeInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumMaxWorkersInput")
    def autovacuum_max_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumMaxWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumNaptimeInput")
    def autovacuum_naptime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumNaptimeInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostDelayInput")
    def autovacuum_vacuum_cost_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumCostDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostLimitInput")
    def autovacuum_vacuum_cost_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumCostLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumScaleFactorInput")
    def autovacuum_vacuum_scale_factor_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumScaleFactorInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumThresholdInput")
    def autovacuum_vacuum_threshold_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autovacuumVacuumThresholdInput"))

    @builtins.property
    @jsii.member(jsii_name="backupHourInput")
    def backup_hour_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupHourInput"))

    @builtins.property
    @jsii.member(jsii_name="backupMinuteInput")
    def backup_minute_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "backupMinuteInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterDelayInput")
    def bgwriter_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterFlushAfterInput")
    def bgwriter_flush_after_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterFlushAfterInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMaxpagesInput")
    def bgwriter_lru_maxpages_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterLruMaxpagesInput"))

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMultiplierInput")
    def bgwriter_lru_multiplier_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "bgwriterLruMultiplierInput"))

    @builtins.property
    @jsii.member(jsii_name="clusterIdInput")
    def cluster_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "clusterIdInput"))

    @builtins.property
    @jsii.member(jsii_name="deadlockTimeoutInput")
    def deadlock_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "deadlockTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="defaultToastCompressionInput")
    def default_toast_compression_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "defaultToastCompressionInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="idleInTransactionSessionTimeoutInput")
    def idle_in_transaction_session_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "idleInTransactionSessionTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="jitInput")
    def jit_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "jitInput"))

    @builtins.property
    @jsii.member(jsii_name="logAutovacuumMinDurationInput")
    def log_autovacuum_min_duration_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logAutovacuumMinDurationInput"))

    @builtins.property
    @jsii.member(jsii_name="logErrorVerbosityInput")
    def log_error_verbosity_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logErrorVerbosityInput"))

    @builtins.property
    @jsii.member(jsii_name="logLinePrefixInput")
    def log_line_prefix_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "logLinePrefixInput"))

    @builtins.property
    @jsii.member(jsii_name="logMinDurationStatementInput")
    def log_min_duration_statement_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "logMinDurationStatementInput"))

    @builtins.property
    @jsii.member(jsii_name="maxFilesPerProcessInput")
    def max_files_per_process_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxFilesPerProcessInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLocksPerTransactionInput")
    def max_locks_per_transaction_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLocksPerTransactionInput"))

    @builtins.property
    @jsii.member(jsii_name="maxLogicalReplicationWorkersInput")
    def max_logical_replication_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxLogicalReplicationWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkersInput")
    def max_parallel_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParallelWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkersPerGatherInput")
    def max_parallel_workers_per_gather_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxParallelWorkersPerGatherInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPredLocksPerTransactionInput")
    def max_pred_locks_per_transaction_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPredLocksPerTransactionInput"))

    @builtins.property
    @jsii.member(jsii_name="maxPreparedTransactionsInput")
    def max_prepared_transactions_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxPreparedTransactionsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxReplicationSlotsInput")
    def max_replication_slots_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxReplicationSlotsInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStackDepthInput")
    def max_stack_depth_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStackDepthInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStandbyArchiveDelayInput")
    def max_standby_archive_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStandbyArchiveDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="maxStandbyStreamingDelayInput")
    def max_standby_streaming_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxStandbyStreamingDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWalSendersInput")
    def max_wal_senders_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWalSendersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxWorkerProcessesInput")
    def max_worker_processes_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxWorkerProcessesInput"))

    @builtins.property
    @jsii.member(jsii_name="pgbouncerInput")
    def pgbouncer_input(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabasePostgresqlConfigPgbouncer"]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabasePostgresqlConfigPgbouncer"]]], jsii.get(self, "pgbouncerInput"))

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwIntervalInput")
    def pg_partman_bgw_interval_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "pgPartmanBgwIntervalInput"))

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwRoleInput")
    def pg_partman_bgw_role_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgPartmanBgwRoleInput"))

    @builtins.property
    @jsii.member(jsii_name="pgStatStatementsTrackInput")
    def pg_stat_statements_track_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "pgStatStatementsTrackInput"))

    @builtins.property
    @jsii.member(jsii_name="sharedBuffersPercentageInput")
    def shared_buffers_percentage_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "sharedBuffersPercentageInput"))

    @builtins.property
    @jsii.member(jsii_name="tempFileLimitInput")
    def temp_file_limit_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "tempFileLimitInput"))

    @builtins.property
    @jsii.member(jsii_name="timescaledbInput")
    def timescaledb_input(
        self,
    ) -> typing.Optional["DatabasePostgresqlConfigTimescaledb"]:
        return typing.cast(typing.Optional["DatabasePostgresqlConfigTimescaledb"], jsii.get(self, "timescaledbInput"))

    @builtins.property
    @jsii.member(jsii_name="timezoneInput")
    def timezone_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "timezoneInput"))

    @builtins.property
    @jsii.member(jsii_name="trackActivityQuerySizeInput")
    def track_activity_query_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "trackActivityQuerySizeInput"))

    @builtins.property
    @jsii.member(jsii_name="trackCommitTimestampInput")
    def track_commit_timestamp_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackCommitTimestampInput"))

    @builtins.property
    @jsii.member(jsii_name="trackFunctionsInput")
    def track_functions_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackFunctionsInput"))

    @builtins.property
    @jsii.member(jsii_name="trackIoTimingInput")
    def track_io_timing_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "trackIoTimingInput"))

    @builtins.property
    @jsii.member(jsii_name="walSenderTimeoutInput")
    def wal_sender_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "walSenderTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="walWriterDelayInput")
    def wal_writer_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "walWriterDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="workMemInput")
    def work_mem_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "workMemInput"))

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeScaleFactor")
    def autovacuum_analyze_scale_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumAnalyzeScaleFactor"))

    @autovacuum_analyze_scale_factor.setter
    def autovacuum_analyze_scale_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c8cb8cacf4ab66add1fb1ab4a3f6768d47c8d9c06e68543723d6c827ce70e3b4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumAnalyzeScaleFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumAnalyzeThreshold")
    def autovacuum_analyze_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumAnalyzeThreshold"))

    @autovacuum_analyze_threshold.setter
    def autovacuum_analyze_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4c5b0aa207e52134ff7cad3cc6676a1111475865171ba7c03edd618b3670b836)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumAnalyzeThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumFreezeMaxAge")
    def autovacuum_freeze_max_age(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumFreezeMaxAge"))

    @autovacuum_freeze_max_age.setter
    def autovacuum_freeze_max_age(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__551ef82e60078ce905590ef9d6c9f04d1d0f79f541fabf9cc2b7ab4ad7f3c5b9)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumFreezeMaxAge", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumMaxWorkers")
    def autovacuum_max_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumMaxWorkers"))

    @autovacuum_max_workers.setter
    def autovacuum_max_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e6df494e2576c8ff5592ffe982cf62941f10f0dab725e37c7e3e6a4ecffa773b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumMaxWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumNaptime")
    def autovacuum_naptime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumNaptime"))

    @autovacuum_naptime.setter
    def autovacuum_naptime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__73ae6ca7fa5aecaa51bf078e3cc0f267cc524d621de7fa2ca12b0756dc80ceac)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumNaptime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostDelay")
    def autovacuum_vacuum_cost_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumCostDelay"))

    @autovacuum_vacuum_cost_delay.setter
    def autovacuum_vacuum_cost_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2741682952a259bcb01e4eb52c098ae70341a7216c678d7452e6c7dbdc52c5ff)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumCostDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumCostLimit")
    def autovacuum_vacuum_cost_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumCostLimit"))

    @autovacuum_vacuum_cost_limit.setter
    def autovacuum_vacuum_cost_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a4e1ab990d18f608c3728a8ae680e1eddfa2fa8e812179a6409c193259ca9b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumCostLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumScaleFactor")
    def autovacuum_vacuum_scale_factor(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumScaleFactor"))

    @autovacuum_vacuum_scale_factor.setter
    def autovacuum_vacuum_scale_factor(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6842f737f9af54e01d9534846971f87cdef94dbe5d376666e036e65b438cc85f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumScaleFactor", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autovacuumVacuumThreshold")
    def autovacuum_vacuum_threshold(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autovacuumVacuumThreshold"))

    @autovacuum_vacuum_threshold.setter
    def autovacuum_vacuum_threshold(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__df1dbc530fb7d19143663d0736329f5fd5b0656e36e1f45e46a147f09f59557d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autovacuumVacuumThreshold", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupHour")
    def backup_hour(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupHour"))

    @backup_hour.setter
    def backup_hour(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c02ff090065ac02b734d6940f99b559e0c59182a36ac62fc946c5d7e6ffa1d72)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupHour", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="backupMinute")
    def backup_minute(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "backupMinute"))

    @backup_minute.setter
    def backup_minute(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1579dfd5b8fe3d68c49bbfc02b3c7b80cae20f98e543f332a139971e6223b7ed)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "backupMinute", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterDelay")
    def bgwriter_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterDelay"))

    @bgwriter_delay.setter
    def bgwriter_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a350a0a3e92b3b6e7a90950d4962a8b1d5b9b14489ac927c85a4b0f8add77ea5)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterFlushAfter")
    def bgwriter_flush_after(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterFlushAfter"))

    @bgwriter_flush_after.setter
    def bgwriter_flush_after(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__631699ab98fb193205354888bbd72aa6b6f9d504179f31e817ce611bbae535f4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterFlushAfter", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMaxpages")
    def bgwriter_lru_maxpages(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterLruMaxpages"))

    @bgwriter_lru_maxpages.setter
    def bgwriter_lru_maxpages(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9582e76b3aed73295774bcf739aa5c241cadc9603c4e9e8faafb15a1d831ad6f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterLruMaxpages", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="bgwriterLruMultiplier")
    def bgwriter_lru_multiplier(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "bgwriterLruMultiplier"))

    @bgwriter_lru_multiplier.setter
    def bgwriter_lru_multiplier(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5f2a0d1ea52bce1892367de9368a535e2b51d1ac9d646d83d352e17aa81e4eda)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "bgwriterLruMultiplier", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="clusterId")
    def cluster_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "clusterId"))

    @cluster_id.setter
    def cluster_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f4d97c11f4d12bba50146c1d07f48da89da9db86ef56c2f12d75270369f2f5a6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "clusterId", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="deadlockTimeout")
    def deadlock_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "deadlockTimeout"))

    @deadlock_timeout.setter
    def deadlock_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__11f9cf40eaba5940058c8078b70c95d23b20728a93750eebd99d1177247bfe75)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "deadlockTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="defaultToastCompression")
    def default_toast_compression(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "defaultToastCompression"))

    @default_toast_compression.setter
    def default_toast_compression(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a1fe2ccc4dd1943dbc279768bc0dfd574f62de58a94758327b6eb08eafb6645c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "defaultToastCompression", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__af49235e8b49370c90e490924ddd420e7291fa3b658eb1a149a5c6c335c3605b)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="idleInTransactionSessionTimeout")
    def idle_in_transaction_session_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "idleInTransactionSessionTimeout"))

    @idle_in_transaction_session_timeout.setter
    def idle_in_transaction_session_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8e86fc61ee2adc8b5b72e9995f27c64945b0e640795f5cab32d0e1a243588675)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "idleInTransactionSessionTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="jit")
    def jit(self) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "jit"))

    @jit.setter
    def jit(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__8f7a63b2508de7c1362fa6573785a9012a92cdd8c49bc38823eec7c95d91e568)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "jit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logAutovacuumMinDuration")
    def log_autovacuum_min_duration(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logAutovacuumMinDuration"))

    @log_autovacuum_min_duration.setter
    def log_autovacuum_min_duration(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__d4c9266b415bc874281e8edfcfde5312960a34e5bbfdb4ef2fc24f4b5c79e733)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logAutovacuumMinDuration", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logErrorVerbosity")
    def log_error_verbosity(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logErrorVerbosity"))

    @log_error_verbosity.setter
    def log_error_verbosity(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__15c02a63880c2aaf220a9633663facc5173d69ae23dc20d71b95e3a657d27d99)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logErrorVerbosity", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logLinePrefix")
    def log_line_prefix(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "logLinePrefix"))

    @log_line_prefix.setter
    def log_line_prefix(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1523bf2416b9686f7f415b4847806be719f0f7874077cc1629566d27037eaa46)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logLinePrefix", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="logMinDurationStatement")
    def log_min_duration_statement(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "logMinDurationStatement"))

    @log_min_duration_statement.setter
    def log_min_duration_statement(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5a97bd859799e9a7201d48afb1dfcf31eac7fe46b8c71bde52d79c9fef3462b2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "logMinDurationStatement", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxFilesPerProcess")
    def max_files_per_process(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxFilesPerProcess"))

    @max_files_per_process.setter
    def max_files_per_process(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__02401c10838b9a3870152e0bf23190e05fd7383eef9f5fc645032bd5cf1d372f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxFilesPerProcess", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLocksPerTransaction")
    def max_locks_per_transaction(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLocksPerTransaction"))

    @max_locks_per_transaction.setter
    def max_locks_per_transaction(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__5c292ec3617c104be3d39b1b4df43cfbfd16d74a5ee1b9f86feff49c692fd6d4)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLocksPerTransaction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxLogicalReplicationWorkers")
    def max_logical_replication_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxLogicalReplicationWorkers"))

    @max_logical_replication_workers.setter
    def max_logical_replication_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ee4b7d06711e360b6b6fcce551fb114d797e7f5939624f84911ccd5dfaf123d0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxLogicalReplicationWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkers")
    def max_parallel_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxParallelWorkers"))

    @max_parallel_workers.setter
    def max_parallel_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__271a9399c4c53956937726c11c9f75ef68fea608b82bc8888cf15e38f7530bd2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxParallelWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxParallelWorkersPerGather")
    def max_parallel_workers_per_gather(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxParallelWorkersPerGather"))

    @max_parallel_workers_per_gather.setter
    def max_parallel_workers_per_gather(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__48476fa3fa36b3c541cb143cc5531ecbacd68877b209f7f39922f388d40b4b68)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxParallelWorkersPerGather", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPredLocksPerTransaction")
    def max_pred_locks_per_transaction(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPredLocksPerTransaction"))

    @max_pred_locks_per_transaction.setter
    def max_pred_locks_per_transaction(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__595957e05767a2d201948886b279202fecd84575362ae9ad4d70f68608b8bad2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPredLocksPerTransaction", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxPreparedTransactions")
    def max_prepared_transactions(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxPreparedTransactions"))

    @max_prepared_transactions.setter
    def max_prepared_transactions(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__06e9d05428b3e0ef491041170ccea36d5f8ebbbc039ba7e1ba56b569243f6344)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxPreparedTransactions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxReplicationSlots")
    def max_replication_slots(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxReplicationSlots"))

    @max_replication_slots.setter
    def max_replication_slots(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e235307a0604b823c6513830500e8c975f5ed91784a3bd83213e3e0b24380b1a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxReplicationSlots", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStackDepth")
    def max_stack_depth(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStackDepth"))

    @max_stack_depth.setter
    def max_stack_depth(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c598b10d26cc6aaa1855a2935fca0ffa162e1f70ea84d3a9d26e514a7f4d25f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStackDepth", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStandbyArchiveDelay")
    def max_standby_archive_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStandbyArchiveDelay"))

    @max_standby_archive_delay.setter
    def max_standby_archive_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__e491e0c22971b69ed3264f1d0cf3854823ed7e23dcfac8bf76182bc5330eaec3)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStandbyArchiveDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxStandbyStreamingDelay")
    def max_standby_streaming_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxStandbyStreamingDelay"))

    @max_standby_streaming_delay.setter
    def max_standby_streaming_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4b7465efc822816da9c28e1eca1d7d54a385f18aada66275048d37e901e299a2)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxStandbyStreamingDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxWalSenders")
    def max_wal_senders(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWalSenders"))

    @max_wal_senders.setter
    def max_wal_senders(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__b68cec5decf1f26165e1a2f0b6789631372cbd467e82ca1fecb5b794dd5c202f)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWalSenders", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="maxWorkerProcesses")
    def max_worker_processes(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxWorkerProcesses"))

    @max_worker_processes.setter
    def max_worker_processes(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__240024e4b4b5c0ab1de0793a75e351de454675bf160068be6f2a55947860c725)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxWorkerProcesses", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwInterval")
    def pg_partman_bgw_interval(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "pgPartmanBgwInterval"))

    @pg_partman_bgw_interval.setter
    def pg_partman_bgw_interval(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__31e36eeaa41f207d9035c19060d66e6e89772607a339abe2c835cdc35f1e6687)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgPartmanBgwInterval", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgPartmanBgwRole")
    def pg_partman_bgw_role(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgPartmanBgwRole"))

    @pg_partman_bgw_role.setter
    def pg_partman_bgw_role(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__6cb18a5005e4ffec1654b9af64ff4492050ae1f5ee2241cb29ba6208b8d6ac1e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgPartmanBgwRole", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="pgStatStatementsTrack")
    def pg_stat_statements_track(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "pgStatStatementsTrack"))

    @pg_stat_statements_track.setter
    def pg_stat_statements_track(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7c3f530cf3b19da938ae75257efc39b23a500a718a6d357fb3f27e0af9782665)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "pgStatStatementsTrack", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="sharedBuffersPercentage")
    def shared_buffers_percentage(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "sharedBuffersPercentage"))

    @shared_buffers_percentage.setter
    def shared_buffers_percentage(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__a62147ee12ea623aa3f5d55eb1cc8894b4c6ec85261a4668fd31a1f48c4699be)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "sharedBuffersPercentage", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="tempFileLimit")
    def temp_file_limit(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "tempFileLimit"))

    @temp_file_limit.setter
    def temp_file_limit(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__23746ed95e113c6ae816853cda6d236d298bb74b9bc3a936b3bf27027db8b57c)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "tempFileLimit", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="timezone")
    def timezone(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "timezone"))

    @timezone.setter
    def timezone(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__95b7566f7a612c5f071a3502e5da55f7f3244bdca55a7978e95cd6a4fc1919ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "timezone", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackActivityQuerySize")
    def track_activity_query_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "trackActivityQuerySize"))

    @track_activity_query_size.setter
    def track_activity_query_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__85d024500969a4e5168d667072b566a69df3576eca46136dec294a834dff858e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackActivityQuerySize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackCommitTimestamp")
    def track_commit_timestamp(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackCommitTimestamp"))

    @track_commit_timestamp.setter
    def track_commit_timestamp(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__aa0f7214b2301ae800438f7f42a260e818f483004341d2de55bbdd133da027f0)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackCommitTimestamp", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackFunctions")
    def track_functions(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackFunctions"))

    @track_functions.setter
    def track_functions(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ebb48ce48ae32b1cff0aef359a15d799e6c0727ccc1844529883ba5ffee143e1)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackFunctions", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="trackIoTiming")
    def track_io_timing(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "trackIoTiming"))

    @track_io_timing.setter
    def track_io_timing(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__61b287a29d4615aa84270ce4cc059f0f3d3aee9608b32c638ba6382ca01b6dce)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "trackIoTiming", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="walSenderTimeout")
    def wal_sender_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "walSenderTimeout"))

    @wal_sender_timeout.setter
    def wal_sender_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__7efb1bcc70bdae5301362002edce88e5e9fadfbcd86474944923a06cf3b26e88)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "walSenderTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="walWriterDelay")
    def wal_writer_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "walWriterDelay"))

    @wal_writer_delay.setter
    def wal_writer_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bbdc94037c0a357ce6bce4aead77602bfdc14f861adbb6c5dcd27bf91c3e1ede)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "walWriterDelay", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="workMem")
    def work_mem(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "workMem"))

    @work_mem.setter
    def work_mem(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__cdd6f586e5f9d4cca6f6ad929bcdd350deb4277edd06549d24ac6d98d736b4ea)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "workMem", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfigConfig",
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
        "autovacuum_analyze_scale_factor": "autovacuumAnalyzeScaleFactor",
        "autovacuum_analyze_threshold": "autovacuumAnalyzeThreshold",
        "autovacuum_freeze_max_age": "autovacuumFreezeMaxAge",
        "autovacuum_max_workers": "autovacuumMaxWorkers",
        "autovacuum_naptime": "autovacuumNaptime",
        "autovacuum_vacuum_cost_delay": "autovacuumVacuumCostDelay",
        "autovacuum_vacuum_cost_limit": "autovacuumVacuumCostLimit",
        "autovacuum_vacuum_scale_factor": "autovacuumVacuumScaleFactor",
        "autovacuum_vacuum_threshold": "autovacuumVacuumThreshold",
        "backup_hour": "backupHour",
        "backup_minute": "backupMinute",
        "bgwriter_delay": "bgwriterDelay",
        "bgwriter_flush_after": "bgwriterFlushAfter",
        "bgwriter_lru_maxpages": "bgwriterLruMaxpages",
        "bgwriter_lru_multiplier": "bgwriterLruMultiplier",
        "deadlock_timeout": "deadlockTimeout",
        "default_toast_compression": "defaultToastCompression",
        "id": "id",
        "idle_in_transaction_session_timeout": "idleInTransactionSessionTimeout",
        "jit": "jit",
        "log_autovacuum_min_duration": "logAutovacuumMinDuration",
        "log_error_verbosity": "logErrorVerbosity",
        "log_line_prefix": "logLinePrefix",
        "log_min_duration_statement": "logMinDurationStatement",
        "max_files_per_process": "maxFilesPerProcess",
        "max_locks_per_transaction": "maxLocksPerTransaction",
        "max_logical_replication_workers": "maxLogicalReplicationWorkers",
        "max_parallel_workers": "maxParallelWorkers",
        "max_parallel_workers_per_gather": "maxParallelWorkersPerGather",
        "max_pred_locks_per_transaction": "maxPredLocksPerTransaction",
        "max_prepared_transactions": "maxPreparedTransactions",
        "max_replication_slots": "maxReplicationSlots",
        "max_stack_depth": "maxStackDepth",
        "max_standby_archive_delay": "maxStandbyArchiveDelay",
        "max_standby_streaming_delay": "maxStandbyStreamingDelay",
        "max_wal_senders": "maxWalSenders",
        "max_worker_processes": "maxWorkerProcesses",
        "pgbouncer": "pgbouncer",
        "pg_partman_bgw_interval": "pgPartmanBgwInterval",
        "pg_partman_bgw_role": "pgPartmanBgwRole",
        "pg_stat_statements_track": "pgStatStatementsTrack",
        "shared_buffers_percentage": "sharedBuffersPercentage",
        "temp_file_limit": "tempFileLimit",
        "timescaledb": "timescaledb",
        "timezone": "timezone",
        "track_activity_query_size": "trackActivityQuerySize",
        "track_commit_timestamp": "trackCommitTimestamp",
        "track_functions": "trackFunctions",
        "track_io_timing": "trackIoTiming",
        "wal_sender_timeout": "walSenderTimeout",
        "wal_writer_delay": "walWriterDelay",
        "work_mem": "workMem",
    },
)
class DatabasePostgresqlConfigConfig(_cdktf_9a9027ec.TerraformMetaArguments):
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
        autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
        autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
        autovacuum_max_workers: typing.Optional[jsii.Number] = None,
        autovacuum_naptime: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
        autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
        backup_hour: typing.Optional[jsii.Number] = None,
        backup_minute: typing.Optional[jsii.Number] = None,
        bgwriter_delay: typing.Optional[jsii.Number] = None,
        bgwriter_flush_after: typing.Optional[jsii.Number] = None,
        bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
        bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
        deadlock_timeout: typing.Optional[jsii.Number] = None,
        default_toast_compression: typing.Optional[builtins.str] = None,
        id: typing.Optional[builtins.str] = None,
        idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
        jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
        log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
        log_error_verbosity: typing.Optional[builtins.str] = None,
        log_line_prefix: typing.Optional[builtins.str] = None,
        log_min_duration_statement: typing.Optional[jsii.Number] = None,
        max_files_per_process: typing.Optional[jsii.Number] = None,
        max_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_logical_replication_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers: typing.Optional[jsii.Number] = None,
        max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
        max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
        max_prepared_transactions: typing.Optional[jsii.Number] = None,
        max_replication_slots: typing.Optional[jsii.Number] = None,
        max_stack_depth: typing.Optional[jsii.Number] = None,
        max_standby_archive_delay: typing.Optional[jsii.Number] = None,
        max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
        max_wal_senders: typing.Optional[jsii.Number] = None,
        max_worker_processes: typing.Optional[jsii.Number] = None,
        pgbouncer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union["DatabasePostgresqlConfigPgbouncer", typing.Dict[builtins.str, typing.Any]]]]] = None,
        pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
        pg_partman_bgw_role: typing.Optional[builtins.str] = None,
        pg_stat_statements_track: typing.Optional[builtins.str] = None,
        shared_buffers_percentage: typing.Optional[jsii.Number] = None,
        temp_file_limit: typing.Optional[jsii.Number] = None,
        timescaledb: typing.Optional[typing.Union["DatabasePostgresqlConfigTimescaledb", typing.Dict[builtins.str, typing.Any]]] = None,
        timezone: typing.Optional[builtins.str] = None,
        track_activity_query_size: typing.Optional[jsii.Number] = None,
        track_commit_timestamp: typing.Optional[builtins.str] = None,
        track_functions: typing.Optional[builtins.str] = None,
        track_io_timing: typing.Optional[builtins.str] = None,
        wal_sender_timeout: typing.Optional[jsii.Number] = None,
        wal_writer_delay: typing.Optional[jsii.Number] = None,
        work_mem: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param cluster_id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#cluster_id DatabasePostgresqlConfig#cluster_id}.
        :param autovacuum_analyze_scale_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_analyze_scale_factor DatabasePostgresqlConfig#autovacuum_analyze_scale_factor}.
        :param autovacuum_analyze_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_analyze_threshold DatabasePostgresqlConfig#autovacuum_analyze_threshold}.
        :param autovacuum_freeze_max_age: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_freeze_max_age DatabasePostgresqlConfig#autovacuum_freeze_max_age}.
        :param autovacuum_max_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_max_workers DatabasePostgresqlConfig#autovacuum_max_workers}.
        :param autovacuum_naptime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_naptime DatabasePostgresqlConfig#autovacuum_naptime}.
        :param autovacuum_vacuum_cost_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_cost_delay DatabasePostgresqlConfig#autovacuum_vacuum_cost_delay}.
        :param autovacuum_vacuum_cost_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_cost_limit DatabasePostgresqlConfig#autovacuum_vacuum_cost_limit}.
        :param autovacuum_vacuum_scale_factor: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_scale_factor DatabasePostgresqlConfig#autovacuum_vacuum_scale_factor}.
        :param autovacuum_vacuum_threshold: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_threshold DatabasePostgresqlConfig#autovacuum_vacuum_threshold}.
        :param backup_hour: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#backup_hour DatabasePostgresqlConfig#backup_hour}.
        :param backup_minute: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#backup_minute DatabasePostgresqlConfig#backup_minute}.
        :param bgwriter_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_delay DatabasePostgresqlConfig#bgwriter_delay}.
        :param bgwriter_flush_after: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_flush_after DatabasePostgresqlConfig#bgwriter_flush_after}.
        :param bgwriter_lru_maxpages: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_lru_maxpages DatabasePostgresqlConfig#bgwriter_lru_maxpages}.
        :param bgwriter_lru_multiplier: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_lru_multiplier DatabasePostgresqlConfig#bgwriter_lru_multiplier}.
        :param deadlock_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#deadlock_timeout DatabasePostgresqlConfig#deadlock_timeout}.
        :param default_toast_compression: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#default_toast_compression DatabasePostgresqlConfig#default_toast_compression}.
        :param id: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#id DatabasePostgresqlConfig#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param idle_in_transaction_session_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#idle_in_transaction_session_timeout DatabasePostgresqlConfig#idle_in_transaction_session_timeout}.
        :param jit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#jit DatabasePostgresqlConfig#jit}.
        :param log_autovacuum_min_duration: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_autovacuum_min_duration DatabasePostgresqlConfig#log_autovacuum_min_duration}.
        :param log_error_verbosity: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_error_verbosity DatabasePostgresqlConfig#log_error_verbosity}.
        :param log_line_prefix: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_line_prefix DatabasePostgresqlConfig#log_line_prefix}.
        :param log_min_duration_statement: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_min_duration_statement DatabasePostgresqlConfig#log_min_duration_statement}.
        :param max_files_per_process: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_files_per_process DatabasePostgresqlConfig#max_files_per_process}.
        :param max_locks_per_transaction: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_locks_per_transaction DatabasePostgresqlConfig#max_locks_per_transaction}.
        :param max_logical_replication_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_logical_replication_workers DatabasePostgresqlConfig#max_logical_replication_workers}.
        :param max_parallel_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_parallel_workers DatabasePostgresqlConfig#max_parallel_workers}.
        :param max_parallel_workers_per_gather: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_parallel_workers_per_gather DatabasePostgresqlConfig#max_parallel_workers_per_gather}.
        :param max_pred_locks_per_transaction: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_pred_locks_per_transaction DatabasePostgresqlConfig#max_pred_locks_per_transaction}.
        :param max_prepared_transactions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_prepared_transactions DatabasePostgresqlConfig#max_prepared_transactions}.
        :param max_replication_slots: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_replication_slots DatabasePostgresqlConfig#max_replication_slots}.
        :param max_stack_depth: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_stack_depth DatabasePostgresqlConfig#max_stack_depth}.
        :param max_standby_archive_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_standby_archive_delay DatabasePostgresqlConfig#max_standby_archive_delay}.
        :param max_standby_streaming_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_standby_streaming_delay DatabasePostgresqlConfig#max_standby_streaming_delay}.
        :param max_wal_senders: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_wal_senders DatabasePostgresqlConfig#max_wal_senders}.
        :param max_worker_processes: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_worker_processes DatabasePostgresqlConfig#max_worker_processes}.
        :param pgbouncer: pgbouncer block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pgbouncer DatabasePostgresqlConfig#pgbouncer}
        :param pg_partman_bgw_interval: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_partman_bgw_interval DatabasePostgresqlConfig#pg_partman_bgw_interval}.
        :param pg_partman_bgw_role: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_partman_bgw_role DatabasePostgresqlConfig#pg_partman_bgw_role}.
        :param pg_stat_statements_track: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_stat_statements_track DatabasePostgresqlConfig#pg_stat_statements_track}.
        :param shared_buffers_percentage: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#shared_buffers_percentage DatabasePostgresqlConfig#shared_buffers_percentage}.
        :param temp_file_limit: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#temp_file_limit DatabasePostgresqlConfig#temp_file_limit}.
        :param timescaledb: timescaledb block. Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#timescaledb DatabasePostgresqlConfig#timescaledb}
        :param timezone: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#timezone DatabasePostgresqlConfig#timezone}.
        :param track_activity_query_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_activity_query_size DatabasePostgresqlConfig#track_activity_query_size}.
        :param track_commit_timestamp: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_commit_timestamp DatabasePostgresqlConfig#track_commit_timestamp}.
        :param track_functions: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_functions DatabasePostgresqlConfig#track_functions}.
        :param track_io_timing: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_io_timing DatabasePostgresqlConfig#track_io_timing}.
        :param wal_sender_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#wal_sender_timeout DatabasePostgresqlConfig#wal_sender_timeout}.
        :param wal_writer_delay: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#wal_writer_delay DatabasePostgresqlConfig#wal_writer_delay}.
        :param work_mem: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#work_mem DatabasePostgresqlConfig#work_mem}.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = _cdktf_9a9027ec.TerraformResourceLifecycle(**lifecycle)
        if isinstance(timescaledb, dict):
            timescaledb = DatabasePostgresqlConfigTimescaledb(**timescaledb)
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__c11b99d17599e15f503a616b34e789a2d05c2d0ee3cf1d57e090661bc9c4aa61)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument cluster_id", value=cluster_id, expected_type=type_hints["cluster_id"])
            check_type(argname="argument autovacuum_analyze_scale_factor", value=autovacuum_analyze_scale_factor, expected_type=type_hints["autovacuum_analyze_scale_factor"])
            check_type(argname="argument autovacuum_analyze_threshold", value=autovacuum_analyze_threshold, expected_type=type_hints["autovacuum_analyze_threshold"])
            check_type(argname="argument autovacuum_freeze_max_age", value=autovacuum_freeze_max_age, expected_type=type_hints["autovacuum_freeze_max_age"])
            check_type(argname="argument autovacuum_max_workers", value=autovacuum_max_workers, expected_type=type_hints["autovacuum_max_workers"])
            check_type(argname="argument autovacuum_naptime", value=autovacuum_naptime, expected_type=type_hints["autovacuum_naptime"])
            check_type(argname="argument autovacuum_vacuum_cost_delay", value=autovacuum_vacuum_cost_delay, expected_type=type_hints["autovacuum_vacuum_cost_delay"])
            check_type(argname="argument autovacuum_vacuum_cost_limit", value=autovacuum_vacuum_cost_limit, expected_type=type_hints["autovacuum_vacuum_cost_limit"])
            check_type(argname="argument autovacuum_vacuum_scale_factor", value=autovacuum_vacuum_scale_factor, expected_type=type_hints["autovacuum_vacuum_scale_factor"])
            check_type(argname="argument autovacuum_vacuum_threshold", value=autovacuum_vacuum_threshold, expected_type=type_hints["autovacuum_vacuum_threshold"])
            check_type(argname="argument backup_hour", value=backup_hour, expected_type=type_hints["backup_hour"])
            check_type(argname="argument backup_minute", value=backup_minute, expected_type=type_hints["backup_minute"])
            check_type(argname="argument bgwriter_delay", value=bgwriter_delay, expected_type=type_hints["bgwriter_delay"])
            check_type(argname="argument bgwriter_flush_after", value=bgwriter_flush_after, expected_type=type_hints["bgwriter_flush_after"])
            check_type(argname="argument bgwriter_lru_maxpages", value=bgwriter_lru_maxpages, expected_type=type_hints["bgwriter_lru_maxpages"])
            check_type(argname="argument bgwriter_lru_multiplier", value=bgwriter_lru_multiplier, expected_type=type_hints["bgwriter_lru_multiplier"])
            check_type(argname="argument deadlock_timeout", value=deadlock_timeout, expected_type=type_hints["deadlock_timeout"])
            check_type(argname="argument default_toast_compression", value=default_toast_compression, expected_type=type_hints["default_toast_compression"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument idle_in_transaction_session_timeout", value=idle_in_transaction_session_timeout, expected_type=type_hints["idle_in_transaction_session_timeout"])
            check_type(argname="argument jit", value=jit, expected_type=type_hints["jit"])
            check_type(argname="argument log_autovacuum_min_duration", value=log_autovacuum_min_duration, expected_type=type_hints["log_autovacuum_min_duration"])
            check_type(argname="argument log_error_verbosity", value=log_error_verbosity, expected_type=type_hints["log_error_verbosity"])
            check_type(argname="argument log_line_prefix", value=log_line_prefix, expected_type=type_hints["log_line_prefix"])
            check_type(argname="argument log_min_duration_statement", value=log_min_duration_statement, expected_type=type_hints["log_min_duration_statement"])
            check_type(argname="argument max_files_per_process", value=max_files_per_process, expected_type=type_hints["max_files_per_process"])
            check_type(argname="argument max_locks_per_transaction", value=max_locks_per_transaction, expected_type=type_hints["max_locks_per_transaction"])
            check_type(argname="argument max_logical_replication_workers", value=max_logical_replication_workers, expected_type=type_hints["max_logical_replication_workers"])
            check_type(argname="argument max_parallel_workers", value=max_parallel_workers, expected_type=type_hints["max_parallel_workers"])
            check_type(argname="argument max_parallel_workers_per_gather", value=max_parallel_workers_per_gather, expected_type=type_hints["max_parallel_workers_per_gather"])
            check_type(argname="argument max_pred_locks_per_transaction", value=max_pred_locks_per_transaction, expected_type=type_hints["max_pred_locks_per_transaction"])
            check_type(argname="argument max_prepared_transactions", value=max_prepared_transactions, expected_type=type_hints["max_prepared_transactions"])
            check_type(argname="argument max_replication_slots", value=max_replication_slots, expected_type=type_hints["max_replication_slots"])
            check_type(argname="argument max_stack_depth", value=max_stack_depth, expected_type=type_hints["max_stack_depth"])
            check_type(argname="argument max_standby_archive_delay", value=max_standby_archive_delay, expected_type=type_hints["max_standby_archive_delay"])
            check_type(argname="argument max_standby_streaming_delay", value=max_standby_streaming_delay, expected_type=type_hints["max_standby_streaming_delay"])
            check_type(argname="argument max_wal_senders", value=max_wal_senders, expected_type=type_hints["max_wal_senders"])
            check_type(argname="argument max_worker_processes", value=max_worker_processes, expected_type=type_hints["max_worker_processes"])
            check_type(argname="argument pgbouncer", value=pgbouncer, expected_type=type_hints["pgbouncer"])
            check_type(argname="argument pg_partman_bgw_interval", value=pg_partman_bgw_interval, expected_type=type_hints["pg_partman_bgw_interval"])
            check_type(argname="argument pg_partman_bgw_role", value=pg_partman_bgw_role, expected_type=type_hints["pg_partman_bgw_role"])
            check_type(argname="argument pg_stat_statements_track", value=pg_stat_statements_track, expected_type=type_hints["pg_stat_statements_track"])
            check_type(argname="argument shared_buffers_percentage", value=shared_buffers_percentage, expected_type=type_hints["shared_buffers_percentage"])
            check_type(argname="argument temp_file_limit", value=temp_file_limit, expected_type=type_hints["temp_file_limit"])
            check_type(argname="argument timescaledb", value=timescaledb, expected_type=type_hints["timescaledb"])
            check_type(argname="argument timezone", value=timezone, expected_type=type_hints["timezone"])
            check_type(argname="argument track_activity_query_size", value=track_activity_query_size, expected_type=type_hints["track_activity_query_size"])
            check_type(argname="argument track_commit_timestamp", value=track_commit_timestamp, expected_type=type_hints["track_commit_timestamp"])
            check_type(argname="argument track_functions", value=track_functions, expected_type=type_hints["track_functions"])
            check_type(argname="argument track_io_timing", value=track_io_timing, expected_type=type_hints["track_io_timing"])
            check_type(argname="argument wal_sender_timeout", value=wal_sender_timeout, expected_type=type_hints["wal_sender_timeout"])
            check_type(argname="argument wal_writer_delay", value=wal_writer_delay, expected_type=type_hints["wal_writer_delay"])
            check_type(argname="argument work_mem", value=work_mem, expected_type=type_hints["work_mem"])
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
        if autovacuum_analyze_scale_factor is not None:
            self._values["autovacuum_analyze_scale_factor"] = autovacuum_analyze_scale_factor
        if autovacuum_analyze_threshold is not None:
            self._values["autovacuum_analyze_threshold"] = autovacuum_analyze_threshold
        if autovacuum_freeze_max_age is not None:
            self._values["autovacuum_freeze_max_age"] = autovacuum_freeze_max_age
        if autovacuum_max_workers is not None:
            self._values["autovacuum_max_workers"] = autovacuum_max_workers
        if autovacuum_naptime is not None:
            self._values["autovacuum_naptime"] = autovacuum_naptime
        if autovacuum_vacuum_cost_delay is not None:
            self._values["autovacuum_vacuum_cost_delay"] = autovacuum_vacuum_cost_delay
        if autovacuum_vacuum_cost_limit is not None:
            self._values["autovacuum_vacuum_cost_limit"] = autovacuum_vacuum_cost_limit
        if autovacuum_vacuum_scale_factor is not None:
            self._values["autovacuum_vacuum_scale_factor"] = autovacuum_vacuum_scale_factor
        if autovacuum_vacuum_threshold is not None:
            self._values["autovacuum_vacuum_threshold"] = autovacuum_vacuum_threshold
        if backup_hour is not None:
            self._values["backup_hour"] = backup_hour
        if backup_minute is not None:
            self._values["backup_minute"] = backup_minute
        if bgwriter_delay is not None:
            self._values["bgwriter_delay"] = bgwriter_delay
        if bgwriter_flush_after is not None:
            self._values["bgwriter_flush_after"] = bgwriter_flush_after
        if bgwriter_lru_maxpages is not None:
            self._values["bgwriter_lru_maxpages"] = bgwriter_lru_maxpages
        if bgwriter_lru_multiplier is not None:
            self._values["bgwriter_lru_multiplier"] = bgwriter_lru_multiplier
        if deadlock_timeout is not None:
            self._values["deadlock_timeout"] = deadlock_timeout
        if default_toast_compression is not None:
            self._values["default_toast_compression"] = default_toast_compression
        if id is not None:
            self._values["id"] = id
        if idle_in_transaction_session_timeout is not None:
            self._values["idle_in_transaction_session_timeout"] = idle_in_transaction_session_timeout
        if jit is not None:
            self._values["jit"] = jit
        if log_autovacuum_min_duration is not None:
            self._values["log_autovacuum_min_duration"] = log_autovacuum_min_duration
        if log_error_verbosity is not None:
            self._values["log_error_verbosity"] = log_error_verbosity
        if log_line_prefix is not None:
            self._values["log_line_prefix"] = log_line_prefix
        if log_min_duration_statement is not None:
            self._values["log_min_duration_statement"] = log_min_duration_statement
        if max_files_per_process is not None:
            self._values["max_files_per_process"] = max_files_per_process
        if max_locks_per_transaction is not None:
            self._values["max_locks_per_transaction"] = max_locks_per_transaction
        if max_logical_replication_workers is not None:
            self._values["max_logical_replication_workers"] = max_logical_replication_workers
        if max_parallel_workers is not None:
            self._values["max_parallel_workers"] = max_parallel_workers
        if max_parallel_workers_per_gather is not None:
            self._values["max_parallel_workers_per_gather"] = max_parallel_workers_per_gather
        if max_pred_locks_per_transaction is not None:
            self._values["max_pred_locks_per_transaction"] = max_pred_locks_per_transaction
        if max_prepared_transactions is not None:
            self._values["max_prepared_transactions"] = max_prepared_transactions
        if max_replication_slots is not None:
            self._values["max_replication_slots"] = max_replication_slots
        if max_stack_depth is not None:
            self._values["max_stack_depth"] = max_stack_depth
        if max_standby_archive_delay is not None:
            self._values["max_standby_archive_delay"] = max_standby_archive_delay
        if max_standby_streaming_delay is not None:
            self._values["max_standby_streaming_delay"] = max_standby_streaming_delay
        if max_wal_senders is not None:
            self._values["max_wal_senders"] = max_wal_senders
        if max_worker_processes is not None:
            self._values["max_worker_processes"] = max_worker_processes
        if pgbouncer is not None:
            self._values["pgbouncer"] = pgbouncer
        if pg_partman_bgw_interval is not None:
            self._values["pg_partman_bgw_interval"] = pg_partman_bgw_interval
        if pg_partman_bgw_role is not None:
            self._values["pg_partman_bgw_role"] = pg_partman_bgw_role
        if pg_stat_statements_track is not None:
            self._values["pg_stat_statements_track"] = pg_stat_statements_track
        if shared_buffers_percentage is not None:
            self._values["shared_buffers_percentage"] = shared_buffers_percentage
        if temp_file_limit is not None:
            self._values["temp_file_limit"] = temp_file_limit
        if timescaledb is not None:
            self._values["timescaledb"] = timescaledb
        if timezone is not None:
            self._values["timezone"] = timezone
        if track_activity_query_size is not None:
            self._values["track_activity_query_size"] = track_activity_query_size
        if track_commit_timestamp is not None:
            self._values["track_commit_timestamp"] = track_commit_timestamp
        if track_functions is not None:
            self._values["track_functions"] = track_functions
        if track_io_timing is not None:
            self._values["track_io_timing"] = track_io_timing
        if wal_sender_timeout is not None:
            self._values["wal_sender_timeout"] = wal_sender_timeout
        if wal_writer_delay is not None:
            self._values["wal_writer_delay"] = wal_writer_delay
        if work_mem is not None:
            self._values["work_mem"] = work_mem

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
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#cluster_id DatabasePostgresqlConfig#cluster_id}.'''
        result = self._values.get("cluster_id")
        assert result is not None, "Required property 'cluster_id' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def autovacuum_analyze_scale_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_analyze_scale_factor DatabasePostgresqlConfig#autovacuum_analyze_scale_factor}.'''
        result = self._values.get("autovacuum_analyze_scale_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_analyze_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_analyze_threshold DatabasePostgresqlConfig#autovacuum_analyze_threshold}.'''
        result = self._values.get("autovacuum_analyze_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_freeze_max_age(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_freeze_max_age DatabasePostgresqlConfig#autovacuum_freeze_max_age}.'''
        result = self._values.get("autovacuum_freeze_max_age")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_max_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_max_workers DatabasePostgresqlConfig#autovacuum_max_workers}.'''
        result = self._values.get("autovacuum_max_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_naptime(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_naptime DatabasePostgresqlConfig#autovacuum_naptime}.'''
        result = self._values.get("autovacuum_naptime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_cost_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_cost_delay DatabasePostgresqlConfig#autovacuum_vacuum_cost_delay}.'''
        result = self._values.get("autovacuum_vacuum_cost_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_cost_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_cost_limit DatabasePostgresqlConfig#autovacuum_vacuum_cost_limit}.'''
        result = self._values.get("autovacuum_vacuum_cost_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_scale_factor(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_scale_factor DatabasePostgresqlConfig#autovacuum_vacuum_scale_factor}.'''
        result = self._values.get("autovacuum_vacuum_scale_factor")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autovacuum_vacuum_threshold(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autovacuum_vacuum_threshold DatabasePostgresqlConfig#autovacuum_vacuum_threshold}.'''
        result = self._values.get("autovacuum_vacuum_threshold")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_hour(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#backup_hour DatabasePostgresqlConfig#backup_hour}.'''
        result = self._values.get("backup_hour")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def backup_minute(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#backup_minute DatabasePostgresqlConfig#backup_minute}.'''
        result = self._values.get("backup_minute")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_delay DatabasePostgresqlConfig#bgwriter_delay}.'''
        result = self._values.get("bgwriter_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_flush_after(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_flush_after DatabasePostgresqlConfig#bgwriter_flush_after}.'''
        result = self._values.get("bgwriter_flush_after")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_lru_maxpages(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_lru_maxpages DatabasePostgresqlConfig#bgwriter_lru_maxpages}.'''
        result = self._values.get("bgwriter_lru_maxpages")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def bgwriter_lru_multiplier(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#bgwriter_lru_multiplier DatabasePostgresqlConfig#bgwriter_lru_multiplier}.'''
        result = self._values.get("bgwriter_lru_multiplier")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def deadlock_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#deadlock_timeout DatabasePostgresqlConfig#deadlock_timeout}.'''
        result = self._values.get("deadlock_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def default_toast_compression(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#default_toast_compression DatabasePostgresqlConfig#default_toast_compression}.'''
        result = self._values.get("default_toast_compression")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#id DatabasePostgresqlConfig#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def idle_in_transaction_session_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#idle_in_transaction_session_timeout DatabasePostgresqlConfig#idle_in_transaction_session_timeout}.'''
        result = self._values.get("idle_in_transaction_session_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def jit(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#jit DatabasePostgresqlConfig#jit}.'''
        result = self._values.get("jit")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    @builtins.property
    def log_autovacuum_min_duration(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_autovacuum_min_duration DatabasePostgresqlConfig#log_autovacuum_min_duration}.'''
        result = self._values.get("log_autovacuum_min_duration")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def log_error_verbosity(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_error_verbosity DatabasePostgresqlConfig#log_error_verbosity}.'''
        result = self._values.get("log_error_verbosity")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_line_prefix(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_line_prefix DatabasePostgresqlConfig#log_line_prefix}.'''
        result = self._values.get("log_line_prefix")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def log_min_duration_statement(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#log_min_duration_statement DatabasePostgresqlConfig#log_min_duration_statement}.'''
        result = self._values.get("log_min_duration_statement")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_files_per_process(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_files_per_process DatabasePostgresqlConfig#max_files_per_process}.'''
        result = self._values.get("max_files_per_process")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_locks_per_transaction(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_locks_per_transaction DatabasePostgresqlConfig#max_locks_per_transaction}.'''
        result = self._values.get("max_locks_per_transaction")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_logical_replication_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_logical_replication_workers DatabasePostgresqlConfig#max_logical_replication_workers}.'''
        result = self._values.get("max_logical_replication_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_parallel_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_parallel_workers DatabasePostgresqlConfig#max_parallel_workers}.'''
        result = self._values.get("max_parallel_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_parallel_workers_per_gather(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_parallel_workers_per_gather DatabasePostgresqlConfig#max_parallel_workers_per_gather}.'''
        result = self._values.get("max_parallel_workers_per_gather")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_pred_locks_per_transaction(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_pred_locks_per_transaction DatabasePostgresqlConfig#max_pred_locks_per_transaction}.'''
        result = self._values.get("max_pred_locks_per_transaction")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_prepared_transactions(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_prepared_transactions DatabasePostgresqlConfig#max_prepared_transactions}.'''
        result = self._values.get("max_prepared_transactions")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_replication_slots(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_replication_slots DatabasePostgresqlConfig#max_replication_slots}.'''
        result = self._values.get("max_replication_slots")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_stack_depth(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_stack_depth DatabasePostgresqlConfig#max_stack_depth}.'''
        result = self._values.get("max_stack_depth")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_standby_archive_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_standby_archive_delay DatabasePostgresqlConfig#max_standby_archive_delay}.'''
        result = self._values.get("max_standby_archive_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_standby_streaming_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_standby_streaming_delay DatabasePostgresqlConfig#max_standby_streaming_delay}.'''
        result = self._values.get("max_standby_streaming_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_wal_senders(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_wal_senders DatabasePostgresqlConfig#max_wal_senders}.'''
        result = self._values.get("max_wal_senders")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def max_worker_processes(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_worker_processes DatabasePostgresqlConfig#max_worker_processes}.'''
        result = self._values.get("max_worker_processes")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pgbouncer(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabasePostgresqlConfigPgbouncer"]]]:
        '''pgbouncer block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pgbouncer DatabasePostgresqlConfig#pgbouncer}
        '''
        result = self._values.get("pgbouncer")
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List["DatabasePostgresqlConfigPgbouncer"]]], result)

    @builtins.property
    def pg_partman_bgw_interval(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_partman_bgw_interval DatabasePostgresqlConfig#pg_partman_bgw_interval}.'''
        result = self._values.get("pg_partman_bgw_interval")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def pg_partman_bgw_role(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_partman_bgw_role DatabasePostgresqlConfig#pg_partman_bgw_role}.'''
        result = self._values.get("pg_partman_bgw_role")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def pg_stat_statements_track(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#pg_stat_statements_track DatabasePostgresqlConfig#pg_stat_statements_track}.'''
        result = self._values.get("pg_stat_statements_track")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def shared_buffers_percentage(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#shared_buffers_percentage DatabasePostgresqlConfig#shared_buffers_percentage}.'''
        result = self._values.get("shared_buffers_percentage")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def temp_file_limit(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#temp_file_limit DatabasePostgresqlConfig#temp_file_limit}.'''
        result = self._values.get("temp_file_limit")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def timescaledb(self) -> typing.Optional["DatabasePostgresqlConfigTimescaledb"]:
        '''timescaledb block.

        Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#timescaledb DatabasePostgresqlConfig#timescaledb}
        '''
        result = self._values.get("timescaledb")
        return typing.cast(typing.Optional["DatabasePostgresqlConfigTimescaledb"], result)

    @builtins.property
    def timezone(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#timezone DatabasePostgresqlConfig#timezone}.'''
        result = self._values.get("timezone")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_activity_query_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_activity_query_size DatabasePostgresqlConfig#track_activity_query_size}.'''
        result = self._values.get("track_activity_query_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def track_commit_timestamp(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_commit_timestamp DatabasePostgresqlConfig#track_commit_timestamp}.'''
        result = self._values.get("track_commit_timestamp")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_functions(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_functions DatabasePostgresqlConfig#track_functions}.'''
        result = self._values.get("track_functions")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def track_io_timing(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#track_io_timing DatabasePostgresqlConfig#track_io_timing}.'''
        result = self._values.get("track_io_timing")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def wal_sender_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#wal_sender_timeout DatabasePostgresqlConfig#wal_sender_timeout}.'''
        result = self._values.get("wal_sender_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def wal_writer_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#wal_writer_delay DatabasePostgresqlConfig#wal_writer_delay}.'''
        result = self._values.get("wal_writer_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def work_mem(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#work_mem DatabasePostgresqlConfig#work_mem}.'''
        result = self._values.get("work_mem")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabasePostgresqlConfigConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfigPgbouncer",
    jsii_struct_bases=[],
    name_mapping={
        "autodb_idle_timeout": "autodbIdleTimeout",
        "autodb_max_db_connections": "autodbMaxDbConnections",
        "autodb_pool_mode": "autodbPoolMode",
        "autodb_pool_size": "autodbPoolSize",
        "ignore_startup_parameters": "ignoreStartupParameters",
        "min_pool_size": "minPoolSize",
        "server_idle_timeout": "serverIdleTimeout",
        "server_lifetime": "serverLifetime",
        "server_reset_query_always": "serverResetQueryAlways",
    },
)
class DatabasePostgresqlConfigPgbouncer:
    def __init__(
        self,
        *,
        autodb_idle_timeout: typing.Optional[jsii.Number] = None,
        autodb_max_db_connections: typing.Optional[jsii.Number] = None,
        autodb_pool_mode: typing.Optional[builtins.str] = None,
        autodb_pool_size: typing.Optional[jsii.Number] = None,
        ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
        min_pool_size: typing.Optional[jsii.Number] = None,
        server_idle_timeout: typing.Optional[jsii.Number] = None,
        server_lifetime: typing.Optional[jsii.Number] = None,
        server_reset_query_always: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    ) -> None:
        '''
        :param autodb_idle_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_idle_timeout DatabasePostgresqlConfig#autodb_idle_timeout}.
        :param autodb_max_db_connections: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_max_db_connections DatabasePostgresqlConfig#autodb_max_db_connections}.
        :param autodb_pool_mode: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_pool_mode DatabasePostgresqlConfig#autodb_pool_mode}.
        :param autodb_pool_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_pool_size DatabasePostgresqlConfig#autodb_pool_size}.
        :param ignore_startup_parameters: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#ignore_startup_parameters DatabasePostgresqlConfig#ignore_startup_parameters}.
        :param min_pool_size: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#min_pool_size DatabasePostgresqlConfig#min_pool_size}.
        :param server_idle_timeout: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#server_idle_timeout DatabasePostgresqlConfig#server_idle_timeout}.
        :param server_lifetime: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#server_lifetime DatabasePostgresqlConfig#server_lifetime}.
        :param server_reset_query_always: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#server_reset_query_always DatabasePostgresqlConfig#server_reset_query_always}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ca19ae104304f64f7e9828af736de01357fa8255d209f09395b29cada72e4959)
            check_type(argname="argument autodb_idle_timeout", value=autodb_idle_timeout, expected_type=type_hints["autodb_idle_timeout"])
            check_type(argname="argument autodb_max_db_connections", value=autodb_max_db_connections, expected_type=type_hints["autodb_max_db_connections"])
            check_type(argname="argument autodb_pool_mode", value=autodb_pool_mode, expected_type=type_hints["autodb_pool_mode"])
            check_type(argname="argument autodb_pool_size", value=autodb_pool_size, expected_type=type_hints["autodb_pool_size"])
            check_type(argname="argument ignore_startup_parameters", value=ignore_startup_parameters, expected_type=type_hints["ignore_startup_parameters"])
            check_type(argname="argument min_pool_size", value=min_pool_size, expected_type=type_hints["min_pool_size"])
            check_type(argname="argument server_idle_timeout", value=server_idle_timeout, expected_type=type_hints["server_idle_timeout"])
            check_type(argname="argument server_lifetime", value=server_lifetime, expected_type=type_hints["server_lifetime"])
            check_type(argname="argument server_reset_query_always", value=server_reset_query_always, expected_type=type_hints["server_reset_query_always"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if autodb_idle_timeout is not None:
            self._values["autodb_idle_timeout"] = autodb_idle_timeout
        if autodb_max_db_connections is not None:
            self._values["autodb_max_db_connections"] = autodb_max_db_connections
        if autodb_pool_mode is not None:
            self._values["autodb_pool_mode"] = autodb_pool_mode
        if autodb_pool_size is not None:
            self._values["autodb_pool_size"] = autodb_pool_size
        if ignore_startup_parameters is not None:
            self._values["ignore_startup_parameters"] = ignore_startup_parameters
        if min_pool_size is not None:
            self._values["min_pool_size"] = min_pool_size
        if server_idle_timeout is not None:
            self._values["server_idle_timeout"] = server_idle_timeout
        if server_lifetime is not None:
            self._values["server_lifetime"] = server_lifetime
        if server_reset_query_always is not None:
            self._values["server_reset_query_always"] = server_reset_query_always

    @builtins.property
    def autodb_idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_idle_timeout DatabasePostgresqlConfig#autodb_idle_timeout}.'''
        result = self._values.get("autodb_idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autodb_max_db_connections(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_max_db_connections DatabasePostgresqlConfig#autodb_max_db_connections}.'''
        result = self._values.get("autodb_max_db_connections")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def autodb_pool_mode(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_pool_mode DatabasePostgresqlConfig#autodb_pool_mode}.'''
        result = self._values.get("autodb_pool_mode")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def autodb_pool_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#autodb_pool_size DatabasePostgresqlConfig#autodb_pool_size}.'''
        result = self._values.get("autodb_pool_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def ignore_startup_parameters(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#ignore_startup_parameters DatabasePostgresqlConfig#ignore_startup_parameters}.'''
        result = self._values.get("ignore_startup_parameters")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def min_pool_size(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#min_pool_size DatabasePostgresqlConfig#min_pool_size}.'''
        result = self._values.get("min_pool_size")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_idle_timeout(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#server_idle_timeout DatabasePostgresqlConfig#server_idle_timeout}.'''
        result = self._values.get("server_idle_timeout")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_lifetime(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#server_lifetime DatabasePostgresqlConfig#server_lifetime}.'''
        result = self._values.get("server_lifetime")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def server_reset_query_always(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#server_reset_query_always DatabasePostgresqlConfig#server_reset_query_always}.'''
        result = self._values.get("server_reset_query_always")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabasePostgresqlConfigPgbouncer(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabasePostgresqlConfigPgbouncerList(
    _cdktf_9a9027ec.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfigPgbouncerList",
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
            type_hints = typing.get_type_hints(_typecheckingstub__6ef6a72776f07838c680e005d5a1af14c35bcb1a491bf9547562c6471b2eef5d)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(
        self,
        index: jsii.Number,
    ) -> "DatabasePostgresqlConfigPgbouncerOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__59d7453062b86d4a37be280c4c39af36a9aabe8ea441b1412a1ae440aaccc51f)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("DatabasePostgresqlConfigPgbouncerOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__1f40e8fa0bf5573e7ded9abaf34d29fd332763bda99b0184e88d9df98ccf9b85)
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
            type_hints = typing.get_type_hints(_typecheckingstub__b7a3f65a259fd7d69e264a836e7f593c7daa0d70500b07d30791bba519dc8e93)
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
            type_hints = typing.get_type_hints(_typecheckingstub__df3d0b06bc6364d5cc4f0375a54aed4017b4352945d3f247bc8c9c4e5cc35a28)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabasePostgresqlConfigPgbouncer]]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabasePostgresqlConfigPgbouncer]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabasePostgresqlConfigPgbouncer]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__20104e7e59609690ce799d11e37998476cc3dbc59771c552d89adc4c55de6ceb)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


class DatabasePostgresqlConfigPgbouncerOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfigPgbouncerOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__7c82bfbfb39372b0244d375a6ad36708c4bd17cd080d091afaebe9590c8860fa)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetAutodbIdleTimeout")
    def reset_autodb_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbIdleTimeout", []))

    @jsii.member(jsii_name="resetAutodbMaxDbConnections")
    def reset_autodb_max_db_connections(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbMaxDbConnections", []))

    @jsii.member(jsii_name="resetAutodbPoolMode")
    def reset_autodb_pool_mode(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbPoolMode", []))

    @jsii.member(jsii_name="resetAutodbPoolSize")
    def reset_autodb_pool_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAutodbPoolSize", []))

    @jsii.member(jsii_name="resetIgnoreStartupParameters")
    def reset_ignore_startup_parameters(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetIgnoreStartupParameters", []))

    @jsii.member(jsii_name="resetMinPoolSize")
    def reset_min_pool_size(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinPoolSize", []))

    @jsii.member(jsii_name="resetServerIdleTimeout")
    def reset_server_idle_timeout(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerIdleTimeout", []))

    @jsii.member(jsii_name="resetServerLifetime")
    def reset_server_lifetime(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerLifetime", []))

    @jsii.member(jsii_name="resetServerResetQueryAlways")
    def reset_server_reset_query_always(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetServerResetQueryAlways", []))

    @builtins.property
    @jsii.member(jsii_name="autodbIdleTimeoutInput")
    def autodb_idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbIdleTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbMaxDbConnectionsInput")
    def autodb_max_db_connections_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbMaxDbConnectionsInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbPoolModeInput")
    def autodb_pool_mode_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "autodbPoolModeInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbPoolSizeInput")
    def autodb_pool_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "autodbPoolSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="ignoreStartupParametersInput")
    def ignore_startup_parameters_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "ignoreStartupParametersInput"))

    @builtins.property
    @jsii.member(jsii_name="minPoolSizeInput")
    def min_pool_size_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minPoolSizeInput"))

    @builtins.property
    @jsii.member(jsii_name="serverIdleTimeoutInput")
    def server_idle_timeout_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "serverIdleTimeoutInput"))

    @builtins.property
    @jsii.member(jsii_name="serverLifetimeInput")
    def server_lifetime_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "serverLifetimeInput"))

    @builtins.property
    @jsii.member(jsii_name="serverResetQueryAlwaysInput")
    def server_reset_query_always_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]], jsii.get(self, "serverResetQueryAlwaysInput"))

    @builtins.property
    @jsii.member(jsii_name="autodbIdleTimeout")
    def autodb_idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbIdleTimeout"))

    @autodb_idle_timeout.setter
    def autodb_idle_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__492be0082a4fb8019c9e1a997bb1bbd0be30197ee821d8ed453dca94f069da5a)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbIdleTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autodbMaxDbConnections")
    def autodb_max_db_connections(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbMaxDbConnections"))

    @autodb_max_db_connections.setter
    def autodb_max_db_connections(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__dfa05b6ee333e66a0d54d4aed0a929d225575e038c8fc27328180b6a288d7e09)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbMaxDbConnections", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autodbPoolMode")
    def autodb_pool_mode(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "autodbPoolMode"))

    @autodb_pool_mode.setter
    def autodb_pool_mode(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4d8746eb5809a30039ddcb0b9102acf659e1e256897b91ffe4f5f367e9beb7f6)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbPoolMode", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="autodbPoolSize")
    def autodb_pool_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "autodbPoolSize"))

    @autodb_pool_size.setter
    def autodb_pool_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4e8e695035e2ea06daca4a14db804dd769cb82af25139f643055f546e6ffd84e)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "autodbPoolSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="ignoreStartupParameters")
    def ignore_startup_parameters(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "ignoreStartupParameters"))

    @ignore_startup_parameters.setter
    def ignore_startup_parameters(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__9c74768e7b832fd82e338b351aa15267dd5d3195bc9dd4cf2d9df5cf0478cb89)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "ignoreStartupParameters", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="minPoolSize")
    def min_pool_size(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minPoolSize"))

    @min_pool_size.setter
    def min_pool_size(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__f0542fc27f37dc0b2d4da9269faaa0b45b9705621a0fd6105e7d14b9f0450a90)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minPoolSize", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverIdleTimeout")
    def server_idle_timeout(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "serverIdleTimeout"))

    @server_idle_timeout.setter
    def server_idle_timeout(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__bf530f7878367b7526238dfca06da7a5049d4931d59d0b99301ba0009886b90d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverIdleTimeout", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverLifetime")
    def server_lifetime(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "serverLifetime"))

    @server_lifetime.setter
    def server_lifetime(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__ef722ec31bd2e63a58b0ceaae561425ca50bdd6c742bb32548c0e7fd2e979169)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverLifetime", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="serverResetQueryAlways")
    def server_reset_query_always(
        self,
    ) -> typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable], jsii.get(self, "serverResetQueryAlways"))

    @server_reset_query_always.setter
    def server_reset_query_always(
        self,
        value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__45b8d94c79c24163a879f99300d081abab1c97d0321f1199078f1acfae768b4d)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverResetQueryAlways", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabasePostgresqlConfigPgbouncer]]:
        return typing.cast(typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabasePostgresqlConfigPgbouncer]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabasePostgresqlConfigPgbouncer]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__4a520656df06765da8399883ee672f3e9b657493a016403c99e9ec45d1d11901)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


@jsii.data_type(
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfigTimescaledb",
    jsii_struct_bases=[],
    name_mapping={"max_background_workers": "maxBackgroundWorkers"},
)
class DatabasePostgresqlConfigTimescaledb:
    def __init__(
        self,
        *,
        max_background_workers: typing.Optional[jsii.Number] = None,
    ) -> None:
        '''
        :param max_background_workers: Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_background_workers DatabasePostgresqlConfig#max_background_workers}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__2a51ccb4086d5527ff25260c5aa02f60ab4c079aea5e631972b2232918d6f593)
            check_type(argname="argument max_background_workers", value=max_background_workers, expected_type=type_hints["max_background_workers"])
        self._values: typing.Dict[builtins.str, typing.Any] = {}
        if max_background_workers is not None:
            self._values["max_background_workers"] = max_background_workers

    @builtins.property
    def max_background_workers(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://registry.terraform.io/providers/digitalocean/digitalocean/2.63.0/docs/resources/database_postgresql_config#max_background_workers DatabasePostgresqlConfig#max_background_workers}.'''
        result = self._values.get("max_background_workers")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DatabasePostgresqlConfigTimescaledb(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class DatabasePostgresqlConfigTimescaledbOutputReference(
    _cdktf_9a9027ec.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-digitalocean.databasePostgresqlConfig.DatabasePostgresqlConfigTimescaledbOutputReference",
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
            type_hints = typing.get_type_hints(_typecheckingstub__954f6d27e980e241fab411dac244eccfd6f743e502ef7ddc652eee12ac807df9)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetMaxBackgroundWorkers")
    def reset_max_background_workers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMaxBackgroundWorkers", []))

    @builtins.property
    @jsii.member(jsii_name="maxBackgroundWorkersInput")
    def max_background_workers_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "maxBackgroundWorkersInput"))

    @builtins.property
    @jsii.member(jsii_name="maxBackgroundWorkers")
    def max_background_workers(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "maxBackgroundWorkers"))

    @max_background_workers.setter
    def max_background_workers(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__3d8ff4f9d5f40da0f45dc2f30950128a7db89a983830cbdfc2ac412963c90476)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "maxBackgroundWorkers", value) # pyright: ignore[reportArgumentType]

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[DatabasePostgresqlConfigTimescaledb]:
        return typing.cast(typing.Optional[DatabasePostgresqlConfigTimescaledb], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[DatabasePostgresqlConfigTimescaledb],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(_typecheckingstub__19bcf4f398a8c00f3ea14ad3f0daf49d2f9c154e60ffd97366dd2469e326c4b7)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value) # pyright: ignore[reportArgumentType]


__all__ = [
    "DatabasePostgresqlConfig",
    "DatabasePostgresqlConfigConfig",
    "DatabasePostgresqlConfigPgbouncer",
    "DatabasePostgresqlConfigPgbouncerList",
    "DatabasePostgresqlConfigPgbouncerOutputReference",
    "DatabasePostgresqlConfigTimescaledb",
    "DatabasePostgresqlConfigTimescaledbOutputReference",
]

publication.publish()

def _typecheckingstub__36ae334279827dd362dc523f8365017d681274f272f4887907413e59112c65ce(
    scope: _constructs_77d1e7e8.Construct,
    id_: builtins.str,
    *,
    cluster_id: builtins.str,
    autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
    autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
    autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
    autovacuum_max_workers: typing.Optional[jsii.Number] = None,
    autovacuum_naptime: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    bgwriter_delay: typing.Optional[jsii.Number] = None,
    bgwriter_flush_after: typing.Optional[jsii.Number] = None,
    bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
    bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
    deadlock_timeout: typing.Optional[jsii.Number] = None,
    default_toast_compression: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
    jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
    log_error_verbosity: typing.Optional[builtins.str] = None,
    log_line_prefix: typing.Optional[builtins.str] = None,
    log_min_duration_statement: typing.Optional[jsii.Number] = None,
    max_files_per_process: typing.Optional[jsii.Number] = None,
    max_locks_per_transaction: typing.Optional[jsii.Number] = None,
    max_logical_replication_workers: typing.Optional[jsii.Number] = None,
    max_parallel_workers: typing.Optional[jsii.Number] = None,
    max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
    max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
    max_prepared_transactions: typing.Optional[jsii.Number] = None,
    max_replication_slots: typing.Optional[jsii.Number] = None,
    max_stack_depth: typing.Optional[jsii.Number] = None,
    max_standby_archive_delay: typing.Optional[jsii.Number] = None,
    max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
    max_wal_senders: typing.Optional[jsii.Number] = None,
    max_worker_processes: typing.Optional[jsii.Number] = None,
    pgbouncer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DatabasePostgresqlConfigPgbouncer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
    pg_partman_bgw_role: typing.Optional[builtins.str] = None,
    pg_stat_statements_track: typing.Optional[builtins.str] = None,
    shared_buffers_percentage: typing.Optional[jsii.Number] = None,
    temp_file_limit: typing.Optional[jsii.Number] = None,
    timescaledb: typing.Optional[typing.Union[DatabasePostgresqlConfigTimescaledb, typing.Dict[builtins.str, typing.Any]]] = None,
    timezone: typing.Optional[builtins.str] = None,
    track_activity_query_size: typing.Optional[jsii.Number] = None,
    track_commit_timestamp: typing.Optional[builtins.str] = None,
    track_functions: typing.Optional[builtins.str] = None,
    track_io_timing: typing.Optional[builtins.str] = None,
    wal_sender_timeout: typing.Optional[jsii.Number] = None,
    wal_writer_delay: typing.Optional[jsii.Number] = None,
    work_mem: typing.Optional[jsii.Number] = None,
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

def _typecheckingstub__560f9b24f98813ef980695c73cd2a9786636dbe7fb7628db347b2bcbed9f8cde(
    scope: _constructs_77d1e7e8.Construct,
    import_to_id: builtins.str,
    import_from_id: builtins.str,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__70f76af5b9ecf4195271bf2efcc29ff16185f0b28c5b6f2ff8a8397a9007cc6a(
    value: typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DatabasePostgresqlConfigPgbouncer, typing.Dict[builtins.str, typing.Any]]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c8cb8cacf4ab66add1fb1ab4a3f6768d47c8d9c06e68543723d6c827ce70e3b4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4c5b0aa207e52134ff7cad3cc6676a1111475865171ba7c03edd618b3670b836(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__551ef82e60078ce905590ef9d6c9f04d1d0f79f541fabf9cc2b7ab4ad7f3c5b9(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e6df494e2576c8ff5592ffe982cf62941f10f0dab725e37c7e3e6a4ecffa773b(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__73ae6ca7fa5aecaa51bf078e3cc0f267cc524d621de7fa2ca12b0756dc80ceac(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2741682952a259bcb01e4eb52c098ae70341a7216c678d7452e6c7dbdc52c5ff(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a4e1ab990d18f608c3728a8ae680e1eddfa2fa8e812179a6409c193259ca9b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6842f737f9af54e01d9534846971f87cdef94dbe5d376666e036e65b438cc85f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df1dbc530fb7d19143663d0736329f5fd5b0656e36e1f45e46a147f09f59557d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c02ff090065ac02b734d6940f99b559e0c59182a36ac62fc946c5d7e6ffa1d72(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1579dfd5b8fe3d68c49bbfc02b3c7b80cae20f98e543f332a139971e6223b7ed(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a350a0a3e92b3b6e7a90950d4962a8b1d5b9b14489ac927c85a4b0f8add77ea5(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__631699ab98fb193205354888bbd72aa6b6f9d504179f31e817ce611bbae535f4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9582e76b3aed73295774bcf739aa5c241cadc9603c4e9e8faafb15a1d831ad6f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5f2a0d1ea52bce1892367de9368a535e2b51d1ac9d646d83d352e17aa81e4eda(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f4d97c11f4d12bba50146c1d07f48da89da9db86ef56c2f12d75270369f2f5a6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__11f9cf40eaba5940058c8078b70c95d23b20728a93750eebd99d1177247bfe75(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a1fe2ccc4dd1943dbc279768bc0dfd574f62de58a94758327b6eb08eafb6645c(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__af49235e8b49370c90e490924ddd420e7291fa3b658eb1a149a5c6c335c3605b(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8e86fc61ee2adc8b5b72e9995f27c64945b0e640795f5cab32d0e1a243588675(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__8f7a63b2508de7c1362fa6573785a9012a92cdd8c49bc38823eec7c95d91e568(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__d4c9266b415bc874281e8edfcfde5312960a34e5bbfdb4ef2fc24f4b5c79e733(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__15c02a63880c2aaf220a9633663facc5173d69ae23dc20d71b95e3a657d27d99(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1523bf2416b9686f7f415b4847806be719f0f7874077cc1629566d27037eaa46(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5a97bd859799e9a7201d48afb1dfcf31eac7fe46b8c71bde52d79c9fef3462b2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__02401c10838b9a3870152e0bf23190e05fd7383eef9f5fc645032bd5cf1d372f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__5c292ec3617c104be3d39b1b4df43cfbfd16d74a5ee1b9f86feff49c692fd6d4(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ee4b7d06711e360b6b6fcce551fb114d797e7f5939624f84911ccd5dfaf123d0(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__271a9399c4c53956937726c11c9f75ef68fea608b82bc8888cf15e38f7530bd2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__48476fa3fa36b3c541cb143cc5531ecbacd68877b209f7f39922f388d40b4b68(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__595957e05767a2d201948886b279202fecd84575362ae9ad4d70f68608b8bad2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__06e9d05428b3e0ef491041170ccea36d5f8ebbbc039ba7e1ba56b569243f6344(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e235307a0604b823c6513830500e8c975f5ed91784a3bd83213e3e0b24380b1a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c598b10d26cc6aaa1855a2935fca0ffa162e1f70ea84d3a9d26e514a7f4d25f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__e491e0c22971b69ed3264f1d0cf3854823ed7e23dcfac8bf76182bc5330eaec3(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4b7465efc822816da9c28e1eca1d7d54a385f18aada66275048d37e901e299a2(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b68cec5decf1f26165e1a2f0b6789631372cbd467e82ca1fecb5b794dd5c202f(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__240024e4b4b5c0ab1de0793a75e351de454675bf160068be6f2a55947860c725(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__31e36eeaa41f207d9035c19060d66e6e89772607a339abe2c835cdc35f1e6687(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6cb18a5005e4ffec1654b9af64ff4492050ae1f5ee2241cb29ba6208b8d6ac1e(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c3f530cf3b19da938ae75257efc39b23a500a718a6d357fb3f27e0af9782665(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__a62147ee12ea623aa3f5d55eb1cc8894b4c6ec85261a4668fd31a1f48c4699be(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__23746ed95e113c6ae816853cda6d236d298bb74b9bc3a936b3bf27027db8b57c(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__95b7566f7a612c5f071a3502e5da55f7f3244bdca55a7978e95cd6a4fc1919ea(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__85d024500969a4e5168d667072b566a69df3576eca46136dec294a834dff858e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__aa0f7214b2301ae800438f7f42a260e818f483004341d2de55bbdd133da027f0(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ebb48ce48ae32b1cff0aef359a15d799e6c0727ccc1844529883ba5ffee143e1(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__61b287a29d4615aa84270ce4cc059f0f3d3aee9608b32c638ba6382ca01b6dce(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7efb1bcc70bdae5301362002edce88e5e9fadfbcd86474944923a06cf3b26e88(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bbdc94037c0a357ce6bce4aead77602bfdc14f861adbb6c5dcd27bf91c3e1ede(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__cdd6f586e5f9d4cca6f6ad929bcdd350deb4277edd06549d24ac6d98d736b4ea(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__c11b99d17599e15f503a616b34e789a2d05c2d0ee3cf1d57e090661bc9c4aa61(
    *,
    connection: typing.Optional[typing.Union[typing.Union[_cdktf_9a9027ec.SSHProvisionerConnection, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.WinrmProvisionerConnection, typing.Dict[builtins.str, typing.Any]]]] = None,
    count: typing.Optional[typing.Union[jsii.Number, _cdktf_9a9027ec.TerraformCount]] = None,
    depends_on: typing.Optional[typing.Sequence[_cdktf_9a9027ec.ITerraformDependable]] = None,
    for_each: typing.Optional[_cdktf_9a9027ec.ITerraformIterator] = None,
    lifecycle: typing.Optional[typing.Union[_cdktf_9a9027ec.TerraformResourceLifecycle, typing.Dict[builtins.str, typing.Any]]] = None,
    provider: typing.Optional[_cdktf_9a9027ec.TerraformProvider] = None,
    provisioners: typing.Optional[typing.Sequence[typing.Union[typing.Union[_cdktf_9a9027ec.FileProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.LocalExecProvisioner, typing.Dict[builtins.str, typing.Any]], typing.Union[_cdktf_9a9027ec.RemoteExecProvisioner, typing.Dict[builtins.str, typing.Any]]]]] = None,
    cluster_id: builtins.str,
    autovacuum_analyze_scale_factor: typing.Optional[jsii.Number] = None,
    autovacuum_analyze_threshold: typing.Optional[jsii.Number] = None,
    autovacuum_freeze_max_age: typing.Optional[jsii.Number] = None,
    autovacuum_max_workers: typing.Optional[jsii.Number] = None,
    autovacuum_naptime: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_cost_delay: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_cost_limit: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_scale_factor: typing.Optional[jsii.Number] = None,
    autovacuum_vacuum_threshold: typing.Optional[jsii.Number] = None,
    backup_hour: typing.Optional[jsii.Number] = None,
    backup_minute: typing.Optional[jsii.Number] = None,
    bgwriter_delay: typing.Optional[jsii.Number] = None,
    bgwriter_flush_after: typing.Optional[jsii.Number] = None,
    bgwriter_lru_maxpages: typing.Optional[jsii.Number] = None,
    bgwriter_lru_multiplier: typing.Optional[jsii.Number] = None,
    deadlock_timeout: typing.Optional[jsii.Number] = None,
    default_toast_compression: typing.Optional[builtins.str] = None,
    id: typing.Optional[builtins.str] = None,
    idle_in_transaction_session_timeout: typing.Optional[jsii.Number] = None,
    jit: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
    log_autovacuum_min_duration: typing.Optional[jsii.Number] = None,
    log_error_verbosity: typing.Optional[builtins.str] = None,
    log_line_prefix: typing.Optional[builtins.str] = None,
    log_min_duration_statement: typing.Optional[jsii.Number] = None,
    max_files_per_process: typing.Optional[jsii.Number] = None,
    max_locks_per_transaction: typing.Optional[jsii.Number] = None,
    max_logical_replication_workers: typing.Optional[jsii.Number] = None,
    max_parallel_workers: typing.Optional[jsii.Number] = None,
    max_parallel_workers_per_gather: typing.Optional[jsii.Number] = None,
    max_pred_locks_per_transaction: typing.Optional[jsii.Number] = None,
    max_prepared_transactions: typing.Optional[jsii.Number] = None,
    max_replication_slots: typing.Optional[jsii.Number] = None,
    max_stack_depth: typing.Optional[jsii.Number] = None,
    max_standby_archive_delay: typing.Optional[jsii.Number] = None,
    max_standby_streaming_delay: typing.Optional[jsii.Number] = None,
    max_wal_senders: typing.Optional[jsii.Number] = None,
    max_worker_processes: typing.Optional[jsii.Number] = None,
    pgbouncer: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.Sequence[typing.Union[DatabasePostgresqlConfigPgbouncer, typing.Dict[builtins.str, typing.Any]]]]] = None,
    pg_partman_bgw_interval: typing.Optional[jsii.Number] = None,
    pg_partman_bgw_role: typing.Optional[builtins.str] = None,
    pg_stat_statements_track: typing.Optional[builtins.str] = None,
    shared_buffers_percentage: typing.Optional[jsii.Number] = None,
    temp_file_limit: typing.Optional[jsii.Number] = None,
    timescaledb: typing.Optional[typing.Union[DatabasePostgresqlConfigTimescaledb, typing.Dict[builtins.str, typing.Any]]] = None,
    timezone: typing.Optional[builtins.str] = None,
    track_activity_query_size: typing.Optional[jsii.Number] = None,
    track_commit_timestamp: typing.Optional[builtins.str] = None,
    track_functions: typing.Optional[builtins.str] = None,
    track_io_timing: typing.Optional[builtins.str] = None,
    wal_sender_timeout: typing.Optional[jsii.Number] = None,
    wal_writer_delay: typing.Optional[jsii.Number] = None,
    work_mem: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ca19ae104304f64f7e9828af736de01357fa8255d209f09395b29cada72e4959(
    *,
    autodb_idle_timeout: typing.Optional[jsii.Number] = None,
    autodb_max_db_connections: typing.Optional[jsii.Number] = None,
    autodb_pool_mode: typing.Optional[builtins.str] = None,
    autodb_pool_size: typing.Optional[jsii.Number] = None,
    ignore_startup_parameters: typing.Optional[typing.Sequence[builtins.str]] = None,
    min_pool_size: typing.Optional[jsii.Number] = None,
    server_idle_timeout: typing.Optional[jsii.Number] = None,
    server_lifetime: typing.Optional[jsii.Number] = None,
    server_reset_query_always: typing.Optional[typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable]] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__6ef6a72776f07838c680e005d5a1af14c35bcb1a491bf9547562c6471b2eef5d(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    wraps_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__59d7453062b86d4a37be280c4c39af36a9aabe8ea441b1412a1ae440aaccc51f(
    index: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__1f40e8fa0bf5573e7ded9abaf34d29fd332763bda99b0184e88d9df98ccf9b85(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__b7a3f65a259fd7d69e264a836e7f593c7daa0d70500b07d30791bba519dc8e93(
    value: _cdktf_9a9027ec.IInterpolatingParent,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__df3d0b06bc6364d5cc4f0375a54aed4017b4352945d3f247bc8c9c4e5cc35a28(
    value: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__20104e7e59609690ce799d11e37998476cc3dbc59771c552d89adc4c55de6ceb(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, typing.List[DatabasePostgresqlConfigPgbouncer]]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__7c82bfbfb39372b0244d375a6ad36708c4bd17cd080d091afaebe9590c8860fa(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
    complex_object_index: jsii.Number,
    complex_object_is_from_set: builtins.bool,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__492be0082a4fb8019c9e1a997bb1bbd0be30197ee821d8ed453dca94f069da5a(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__dfa05b6ee333e66a0d54d4aed0a929d225575e038c8fc27328180b6a288d7e09(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4d8746eb5809a30039ddcb0b9102acf659e1e256897b91ffe4f5f367e9beb7f6(
    value: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4e8e695035e2ea06daca4a14db804dd769cb82af25139f643055f546e6ffd84e(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__9c74768e7b832fd82e338b351aa15267dd5d3195bc9dd4cf2d9df5cf0478cb89(
    value: typing.List[builtins.str],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__f0542fc27f37dc0b2d4da9269faaa0b45b9705621a0fd6105e7d14b9f0450a90(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__bf530f7878367b7526238dfca06da7a5049d4931d59d0b99301ba0009886b90d(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__ef722ec31bd2e63a58b0ceaae561425ca50bdd6c742bb32548c0e7fd2e979169(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__45b8d94c79c24163a879f99300d081abab1c97d0321f1199078f1acfae768b4d(
    value: typing.Union[builtins.bool, _cdktf_9a9027ec.IResolvable],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__4a520656df06765da8399883ee672f3e9b657493a016403c99e9ec45d1d11901(
    value: typing.Optional[typing.Union[_cdktf_9a9027ec.IResolvable, DatabasePostgresqlConfigPgbouncer]],
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__2a51ccb4086d5527ff25260c5aa02f60ab4c079aea5e631972b2232918d6f593(
    *,
    max_background_workers: typing.Optional[jsii.Number] = None,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__954f6d27e980e241fab411dac244eccfd6f743e502ef7ddc652eee12ac807df9(
    terraform_resource: _cdktf_9a9027ec.IInterpolatingParent,
    terraform_attribute: builtins.str,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__3d8ff4f9d5f40da0f45dc2f30950128a7db89a983830cbdfc2ac412963c90476(
    value: jsii.Number,
) -> None:
    """Type checking stubs"""
    pass

def _typecheckingstub__19bcf4f398a8c00f3ea14ad3f0daf49d2f9c154e60ffd97366dd2469e326c4b7(
    value: typing.Optional[DatabasePostgresqlConfigTimescaledb],
) -> None:
    """Type checking stubs"""
    pass
