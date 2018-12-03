import queue
import time

from .ds import Datastore
from .generate import generate_payloads, generate_transormation, generate_test
from .pool import execute_operations, sync_execute_operations, timed_execute_operations
from .util.conf import config
from .util import conv
from .util.log import Log
from .util import s3
from .workload import build_workloads, EnvironmentWorkload, ListWorkload
from .util.error import WorkloadTimeoutError
_log = Log('run')

def main(seed = None, count = -1, step = 0):
    exit_code = 0
    for i, step_seed in enumerate(conv.iter_prng(seed, count = count, step = step)):
        for zenko_datastore, aws_datastore in build_environment(step_seed, 1, 0):
            transform_environment(step_seed, zenko_datastore, aws_datastore)
            if run_tests(step_seed, zenko_datastore, aws_datastore):
                _log.info('Listing PASSED, seed: %s, step: %s'%(seed, i))
            else:
                exit_code = 1
                _log.error('Listing FAILED!, seed: %s, step %s'%(seed, i))
            _log.info('Cleaning up Zenko environment....')
            conv.cleanup_bucket(config.zenko.bucket, s3.build_zenko_client)
            _log.info('Cleaning up AWS environment....')
            conv.cleanup_bucket(config.aws.bucket, s3.build_aws_client)
    return exit_code


def build_environment(seed, count = -1, step = 0):
    for payload in generate_payloads(seed, count, step):
        _log.info('Generating Zenko environment...')
        results = sync_execute_operations(build_workloads(payload(config.zenko.bucket), EnvironmentWorkload, s3.build_zenko_client))
        zenko_datastore = build_datastore(results)
        _log.info('Generating AWS environment...')
        results = sync_execute_operations(build_workloads(payload(config.aws.bucket), EnvironmentWorkload, s3.build_aws_client))
        aws_datastore = build_datastore(results)
        yield zenko_datastore, aws_datastore


def build_datastore(results):
    ds = Datastore()
    for op in results:
        ds.put(*op.results[0][1][:2], op.results[0][0])
    return ds

def transform_environment(seed, zds, ads):
    prng = conv.prng(seed)
    transformation = generate_transormation(seed, zds)
    _log.info('Transforming Zenko environment...')
    sync_execute_operations(build_workloads(transformation(config.zenko.bucket), client=s3.build_zenko_client))
    _log.info('Transforming AWS environment...')
    transformation = generate_transormation(seed, ads)
    sync_execute_operations(build_workloads(transformation(config.aws.bucket), client=s3.build_aws_client))


def run_tests(seed, zds, ads):
        test = generate_test(seed, zds)
        check_func, zenko_test = test(config.zenko.bucket)
        try:
            zenko_results = timed_execute_operations(build_workloads([zenko_test], ListWorkload, client=s3.build_zenko_client))
        except WorkloadTimeoutError:
            _log.critical('Zenko listing timed out, probably hit a bug!')
            return False
        test = generate_test(seed, ads)
        _, aws_test = test(config.aws.bucket)
        try:
            aws_results = timed_execute_operations(build_workloads([aws_test], ListWorkload, client=s3.build_aws_client))
        except WorkloadTimeoutError:
            _log.critical('AWS listing timed out, probably a slow netowrk')
            return False
        for zenko, aws in zip(zenko_results, aws_results):
            for i, zres, ares in conv.enumazip(zenko.results[0], aws.results[0]):
                try:
                    check_func(zres, ares)
                except AssertionError as e:
                    _log.error('Comparison between listings has FAILED!')
                    return False
            return True
