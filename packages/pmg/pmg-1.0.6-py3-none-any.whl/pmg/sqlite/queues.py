import logging
import time

import pmg
import pmg.sqlite

log = logging.getLogger(__name__)


class SqliteQueue:
    """
        The minimal table needed for a queue:
        CREATE TABLE "<queue_name>" (
        "<task_name>Id"	INTEGER NOT NULL,
        "StartDt"	TEXT,
        "EndDt"	TEXT,
        "Runtime"	INTEGER,
        "Status"	TEXT,
        "Result"	TEXT,
        "LastUpdateDt"	TEXT,
        PRIMARY KEY("<task_name>Id" AUTOINCREMENT)
    );
    """

    def __init__(self, db_path, queue_name, task_name=None, reset_running_tasks=False):
        self.queue_name = queue_name
        self.task_name = task_name or "Job"
        self.db = pmg.sqlite.open_db(db_path)
        self.db.row_factory = pmg.sqlite.namedtuple_factory
        if reset_running_tasks:
            # Reset tests flagged as RUNNING
            self.db.execute(
                f"UPDATE {self.queue_name} SET Status = NULL, StartDt = NULL WHERE Status = 'RUNNING'"
            )
            self.db.commit()

    def get_work(self, sleep_interval, limit_per_run):
        while True:
            work = self.db.execute(
                f"SELECT {self.task_name}Id AS QueuedTaskId, * FROM {self.queue_name} WHERE Status IS NULL ORDER BY {self.task_name}Id LIMIT ?",
                (limit_per_run,),
            ).fetchall()
            for r in work:
                start_time = time.time()
                self.update_work_item(r.QueuedTaskId, "RUNNING")
                yield r
                run_time = time.time() - start_time
                self.db.execute(
                    f"UPDATE {self.queue_name} SET Runtime = ? WHERE {self.task_name}Id = ?",
                    (run_time, r.QueuedTaskId),
                )
                self.db.commit()
                log.debug(
                    "Task #%d in Queue '%s' completed after %f seconds.",
                    r.QueuedTaskId,
                    self.queue_name,
                    run_time,
                    extra={
                        f"{self.task_name}Id": r.QueuedTaskId,
                        "Queue": self.queue_name,
                    },
                )
            time.sleep(sleep_interval)

    def run_queue(self, proc_func, *args, **kwargs):
        for r in self.get_work(*args, **kwargs):
            try:
                result = proc_func(r)
                self.update_work_item(r.QueuedTaskId, "OK", str(result))
            except Exception as e:
                log.exception(
                    "Task #%d in Queue '%s' failed with exception:\n%s",
                    r.QueuedTaskId,
                    self.queue_name,
                    str(e),
                    extra={
                        f"{self.task_name}Id": r.QueuedTaskId,
                        "Queue": self.queue_name,
                    },
                )
                self.update_work_item(r.QueuedTaskId, "ERROR", str(e))

    def update_work_item(self, work_item_id, status, result=None):
        if status in ["OK", "ERROR"]:
            self.db.execute(
                f"UPDATE {self.queue_name} SET LastUpdateDt = datetime('now'), EndDt = datetime('now'), Status = ?, Result = ? WHERE {self.task_name}Id = ?",
                (status, result, work_item_id),
            )
        elif status in ["RUNNING"]:
            self.db.execute(
                f"UPDATE {self.queue_name} SET LastUpdateDt = datetime('now'), StartDt = datetime('now'), Status = ?, Result = ? WHERE {self.task_name}Id = ?",
                (status, result, work_item_id),
            )
        else:
            self.db.execute(
                f"UPDATE {self.queue_name} SET LastUpdateDt = datetime('now'), Status = ?, Result = ? WHERE {self.task_name}Id = ?",
                (status, result, work_item_id),
            )
        self.db.commit()
