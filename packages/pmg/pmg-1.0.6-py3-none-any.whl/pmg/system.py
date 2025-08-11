import functools
import importlib.metadata
import logging
import os
import platform
import sched
import time

import pmg

log = logging.getLogger(__name__)


def get_os_name():
    os_name = f"{platform.system()} {platform.version()}"
    try:
        if os.path.isfile("/etc/os-release"):
            with open("/etc/os-release", "rt", encoding="utf-8") as f:
                for line in f:
                    k, v = line.split("=")
                    if k == "PRETTY_NAME":
                        os_name = pmg.unquote(v.strip(), '"')
                        break
    except Exception:
        pass
    return f"{os_name} ({platform.platform()})"


def get_package_versions(*packages_start_with):
    versions = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"] or dist.metadata.get("Summary", "")
        if any(name.startswith(prefix) for prefix in packages_start_with):
            versions.append(f"{name} {dist.version}")

    return sorted(versions)


def run_every(sleep_seconds, run_at_start=False, wait_after_fail=15):
    def wrapper(func):
        @functools.wraps(func)
        def looping_function(*args, **kwargs):
            @pmg.logwrap(log)
            def run_it():
                try:
                    return func(*args, **kwargs)
                except Exception:
                    log.exception(
                        "Exception during service function, pausing %d seconds...",
                        wait_after_fail,
                    )
                    time.sleep(wait_after_fail)

            if run_at_start:
                run_it()
            sch = sched.scheduler()
            while True:
                sch.enter(sleep_seconds, 1, run_it)
                sch.run()

        return looping_function

    return wrapper
