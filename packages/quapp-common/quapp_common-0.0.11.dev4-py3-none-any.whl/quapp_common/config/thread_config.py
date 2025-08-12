"""
    QApp Platform Project thread_config.py Copyright © CITYNOW Co. Ltd. All rights reserved.
"""
from concurrent.futures import ThreadPoolExecutor

circuit_exporting_pool = ThreadPoolExecutor(max_workers=10,
                                            thread_name_prefix='circuit-exporting-pool-')

circuit_running_pool = ThreadPoolExecutor(max_workers=20,
                                          thread_name_prefix='circuit-running-pool-')
