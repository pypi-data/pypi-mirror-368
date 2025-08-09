"""Jobset utils: wraps CRUD operations for jobsets"""

import enum
import json
import tempfile
import typing
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

import colorama

if typing.TYPE_CHECKING:
    from datetime import timedelta

import konduktor
from konduktor import kube_client, logging
from konduktor.backends import constants as backend_constants
from konduktor.backends import pod_utils
from konduktor.utils import (
    common_utils,
    kubernetes_utils,
    log_utils,
)

if typing.TYPE_CHECKING:
    pass

logger = logging.get_logger(__name__)

JOBSET_API_GROUP = 'jobset.x-k8s.io'
JOBSET_API_VERSION = 'v1alpha2'
JOBSET_PLURAL = 'jobsets'

# Use shared constants from konduktor.backends.constants
JOBSET_NAME_LABEL = backend_constants.JOB_NAME_LABEL
JOBSET_USERID_LABEL = backend_constants.USERID_LABEL
JOBSET_USER_LABEL = backend_constants.USER_LABEL
JOBSET_ACCELERATOR_LABEL = backend_constants.ACCELERATOR_LABEL
JOBSET_NUM_ACCELERATORS_LABEL = backend_constants.NUM_ACCELERATORS_LABEL

SECRET_BASENAME_LABEL = backend_constants.SECRET_BASENAME_LABEL

_JOBSET_METADATA_LABELS = {
    'jobset_name_label': JOBSET_NAME_LABEL,
    'jobset_userid_label': JOBSET_USERID_LABEL,
    'jobset_user_label': JOBSET_USER_LABEL,
    'jobset_accelerator_label': JOBSET_ACCELERATOR_LABEL,
    'jobset_num_accelerators_label': JOBSET_NUM_ACCELERATORS_LABEL,
}


class JobNotFoundError(Exception):
    pass


class JobStatus(enum.Enum):
    SUSPENDED = 'SUSPENDED'
    ACTIVE = 'ACTIVE'
    COMPLETED = 'COMPLETED'
    FAILED = 'FAILED'
    PENDING = 'PENDING'


if typing.TYPE_CHECKING:
    import konduktor


def create_jobset(
    namespace: str,
    task: 'konduktor.Task',
    pod_spec: Dict[str, Any],
    dryrun: bool = False,
) -> Optional[Dict[str, Any]]:
    """Creates a jobset based on the task definition and pod spec
    and returns the created jobset spec
    """
    assert task.resources is not None, 'Task resources are undefined'
    accelerator_type = task.resources.get_accelerator_type() or 'None'
    num_accelerators = task.resources.get_accelerator_count() or 0
    with tempfile.NamedTemporaryFile() as temp:
        common_utils.fill_template(
            'jobset.yaml.j2',
            {
                'job_name': task.name,
                'user_id': common_utils.user_and_hostname_hash(),
                'num_nodes': task.num_nodes,
                'user': common_utils.get_cleaned_username(),
                'accelerator_type': accelerator_type,
                'num_accelerators': num_accelerators,
                'completions': task.resources.get_completions(),
                'max_restarts': task.resources.get_max_restarts(),
                **_JOBSET_METADATA_LABELS,
            },
            temp.name,
        )
        jobset_spec = common_utils.read_yaml(temp.name)
        # Inject JobSet metadata (labels and annotations)
        pod_utils.inject_jobset_metadata(jobset_spec, task)

    # Merge pod spec into JobSet template
    pod_utils.merge_pod_into_jobset_template(jobset_spec, pod_spec)
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        jobset = kube_client.crd_api(context=context).create_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            body=jobset_spec['jobset'],
            dry_run='All' if dryrun else None,
        )
        logger.info(
            f'task {colorama.Fore.CYAN}{colorama.Style.BRIGHT}'
            f'{task.name}{colorama.Style.RESET_ALL} created'
        )
        return jobset
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error creating jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def list_jobset(namespace: str) -> Optional[Dict[str, Any]]:
    """Lists all jobsets in this namespace"""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).list_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error listing jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def get_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Retrieves jobset in this namespace"""
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).get_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
        )
        return response
    except kube_client.api_exception() as err:
        if err.status == 404:
            raise JobNotFoundError(
                f"Jobset '{job_name}' " f"not found in namespace '{namespace}'."
            )
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error getting jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error creating jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def delete_jobset(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Deletes jobset in this namespace

    Args:
        namespace: Namespace where jobset exists
        job_name: Name of jobset to delete

    Returns:
        Response from delete operation
    """
    try:
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.crd_api(context=context).delete_namespaced_custom_object(
            group=JOBSET_API_GROUP,
            version=JOBSET_API_VERSION,
            namespace=namespace,
            plural=JOBSET_PLURAL,
            name=job_name,
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error deleting jobset: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error deleting jobset: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def get_job(namespace: str, job_name: str) -> Optional[Dict[str, Any]]:
    """Gets a specific job from a jobset by name and worker index

    Args:
        namespace: Namespace where job exists
        job_name: Name of jobset containing the job
        worker_id: Index of the worker job to get (defaults to 0)

    Returns:
        Job object if found
    """
    try:
        # Get the job object using the job name
        # pattern {jobset-name}-workers-0-{worker_id}
        job_name = f'{job_name}-workers-0'
        context = kubernetes_utils.get_current_kube_config_context_name()
        response = kube_client.batch_api(context=context).read_namespaced_job(
            name=job_name, namespace=namespace
        )
        return response
    except kube_client.api_exception() as err:
        try:
            error_body = json.loads(err.body)
            error_message = error_body.get('message', '')
            logger.error(f'error getting job: {error_message}')
        except json.JSONDecodeError:
            error_message = str(err.body)
            logger.error(f'error getting job: {error_message}')
        else:
            # Re-raise the exception if it's a different error
            raise err
    return None


def show_status_table(namespace: str, all_users: bool):
    """Compute cluster table values and display.

    Returns:
        Number of pending auto{stop,down} clusters that are not already
        STOPPED.
    """
    # TODO(zhwu): Update the information for autostop clusters.

    def _get_status_string_colorized(status: Dict[str, Any]) -> str:
        terminalState = status.get('terminalState', None)
        if terminalState and terminalState.upper() == JobStatus.COMPLETED.name.upper():
            return (
                f'{colorama.Fore.GREEN}'
                f'{JobStatus.COMPLETED.name}{colorama.Style.RESET_ALL}'
            )
        elif terminalState and terminalState.upper() == JobStatus.FAILED.name.upper():
            return (
                f'{colorama.Fore.RED}'
                f'{JobStatus.FAILED.name}{colorama.Style.RESET_ALL}'
            )
        elif status['replicatedJobsStatus'][0]['ready']:
            return (
                f'{colorama.Fore.CYAN}'
                f'{JobStatus.ACTIVE.name}{colorama.Style.RESET_ALL}'
            )
        elif status['replicatedJobsStatus'][0]['suspended']:
            return (
                f'{colorama.Fore.BLUE}'
                f'{JobStatus.SUSPENDED.name}{colorama.Style.RESET_ALL}'
            )
        else:
            return (
                f'{colorama.Fore.YELLOW}'
                f'{JobStatus.PENDING.name}{colorama.Style.RESET_ALL}'
            )

    def _get_time_delta(timestamp: str) -> Tuple[str, 'timedelta']:
        delta = datetime.now(timezone.utc) - datetime.strptime(
            timestamp, '%Y-%m-%dT%H:%M:%SZ'
        ).replace(tzinfo=timezone.utc)
        total_seconds = int(delta.total_seconds())

        days, remainder = divmod(total_seconds, 86400)  # 86400 seconds in a day
        hours, remainder = divmod(remainder, 3600)  # 3600 seconds in an hour
        minutes, _ = divmod(remainder, 60)  # 60 seconds in a minute

        days_str = f'{days} days, ' if days > 0 else ''
        hours_str = f'{hours} hours, ' if hours > 0 else ''
        minutes_str = f'{minutes} minutes' if minutes > 0 else ''

        return f'{days_str}{hours_str}{minutes_str}', delta

    def _get_resources(job: Dict[str, Any]) -> str:
        num_pods = int(
            job['spec']['replicatedJobs'][0]['template']['spec']['parallelism']
        )  # noqa: E501
        resources = job['spec']['replicatedJobs'][0]['template']['spec']['template'][
            'spec'
        ]['containers'][0]['resources']['limits']  # noqa: E501
        cpu, memory = resources['cpu'], resources['memory']
        accelerator = job['metadata']['labels'].get(JOBSET_ACCELERATOR_LABEL, None)
        if accelerator:
            return f'{num_pods}x({cpu}CPU, memory {memory}, {accelerator})'
        else:
            return f'{num_pods}x({cpu}CPU, memory {memory}GB)'

    if all_users:
        columns = ['NAME', 'USER', 'STATUS', 'RESOURCES', 'SUBMITTED']
    else:
        columns = ['NAME', 'STATUS', 'RESOURCES', 'SUBMITTED']
    job_table = log_utils.create_table(columns)
    job_specs = list_jobset(namespace)
    assert job_specs is not None, 'Retrieving jobs failed'
    rows = []
    for job in job_specs['items']:
        if all_users:
            rows.append(
                [
                    job['metadata']['name'],
                    job['metadata']['labels'][JOBSET_USERID_LABEL],
                    _get_status_string_colorized(job['status']),
                    _get_resources(job),
                    *_get_time_delta(job['metadata']['creationTimestamp']),
                ]
            )
        elif (
            not all_users
            and job['metadata']['labels'][JOBSET_USER_LABEL]
            == common_utils.get_cleaned_username()
        ):
            rows.append(
                [
                    job['metadata']['name'],
                    _get_status_string_colorized(job.get('status', {})),
                    _get_resources(job),
                    *_get_time_delta(job['metadata']['creationTimestamp']),
                ]
            )
    rows = [row[:-1] for row in sorted(rows, key=lambda x: x[-1])]
    # have the most recently submitted jobs at the top
    for row in rows:
        job_table.add_row(row)
    print(job_table)
