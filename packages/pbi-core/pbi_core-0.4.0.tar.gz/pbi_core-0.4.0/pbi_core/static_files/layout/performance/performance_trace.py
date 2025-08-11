import datetime
import json
import math
import textwrap
import threading
import time
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import jinja2
from pbi_pyadomd import Connection, Reader

from pbi_core.logging import get_logger
from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel
from pbi_core.ssas.server.trace.trace_enums import TraceEvents

logger = get_logger()
TRACE_DIR = Path(__file__).parent / "templates"
TRACE_TEMPLATES: dict[str, jinja2.Template] = {
    f.name: jinja2.Template(f.read_text()) for f in TRACE_DIR.iterdir() if f.is_file()
}

TRACE_DEFAULT_EVENTS = (
    TraceEvents.DISCOVER_BEGIN,
    TraceEvents.COMMAND_BEGIN,
    TraceEvents.QUERY_END,
    TraceEvents.QUERY_SUBCUBE,
    TraceEvents.VERTIPAQ_SE_QUERY_BEGIN,
    TraceEvents.VERTIPAQ_SE_QUERY_END,
    TraceEvents.VERTIPAQ_SE_QUERY_CACHE_MATCH,
    TraceEvents.VERTIPAQ_SE_QUERY_CACHE_MISS,
    TraceEvents.AGGREGATE_TABLE_REWRITE_QUERY,
    TraceEvents.DIRECT_QUERY_END,
    TraceEvents.QUERY_BEGIN,
    TraceEvents.EXECUTION_METRICS,
)


def pretty_size(n: int) -> str:
    """Convert a number of bytes into a human-readable format."""
    units = ["B"] + [f"{p}iB" for p in "KMGTPEZY"]

    prefix = int(math.log(max(n, 1), 1024))
    prefix = min(prefix, len(units) - 1)
    pretty_n = round(n / 1024**prefix, 1)
    return f"{pretty_n} {units[prefix]}"


@dataclass
class ThreadResult:
    command: str
    rows_returned: int
    error: Exception | None = None

    def get_performance(self, trace_records: list[dict[str, Any]]) -> "Performance":
        event_info = {}
        for record in trace_records:
            event_info[record["EventClass"]] = record

        execution_metrics = json.loads(event_info["EXECUTION_METRICS"]["TextData"])
        command_text = event_info["QUERY_END"]["TextData"]
        start_datetime = datetime.datetime.strptime(execution_metrics["timeStart"], "%Y-%m-%dT%H:%M:%S.%f%z")
        end_datetime = datetime.datetime.strptime(execution_metrics["timeEnd"], "%Y-%m-%dT%H:%M:%S.%f%z")
        total_duration = execution_metrics["durationMs"]
        total_cpu_time = execution_metrics["totalCpuTimeMs"]
        query_cpu_time = execution_metrics["queryProcessingCpuTimeMs"]
        vertipaq_cpu_time = execution_metrics["vertipaqJobCpuTimeMs"]
        execution_delay = execution_metrics["executionDelayMs"]
        approximate_peak_consumption_kb = execution_metrics["approximatePeakMemConsumptionKB"]

        for record in trace_records:
            if record.get("EventClass") == "QUERY_END":
                return Performance(
                    command_text=command_text,
                    start_datetime=start_datetime,
                    end_datetime=end_datetime,
                    total_duration=total_duration,
                    total_cpu_time=total_cpu_time,
                    query_cpu_time=query_cpu_time,
                    vertipaq_cpu_time=vertipaq_cpu_time,
                    execution_delay=execution_delay,
                    approximate_peak_consumption_kb=approximate_peak_consumption_kb,
                    rows_returned=self.rows_returned,
                    full_trace_log=trace_records,
                )
        msg = f"Command '{self.command}' not found in trace records."
        raise ValueError(msg)


@dataclass
class Performance:
    command_text: str
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    query_cpu_time: int
    # duration is the total time in milliseconds
    total_duration: int
    total_cpu_time: int
    vertipaq_cpu_time: int
    execution_delay: int
    approximate_peak_consumption_kb: int
    rows_returned: int
    full_trace_log: list[dict[str, Any]]

    def __repr__(self) -> str:
        total_duration = round(self.total_duration / 1000, 2)
        total_cpu_time = round(self.total_cpu_time / 1000, 2)
        approximate_peak_consumption = pretty_size(self.approximate_peak_consumption_kb * 1024)
        return f"Performance(rows={self.rows_returned}, total_duration={total_duration}, total_cpu_time={total_cpu_time}, peak_consumption={approximate_peak_consumption}"  # noqa: E501

    def pprint(self) -> str:
        """Pretty print the performance metrics."""
        command_text = textwrap.indent(self.command_text, " " * 8)
        return f"""Performance(
    Command:

{command_text}

    Start Time: {self.start_datetime.isoformat()}
    End Time: {self.end_datetime.isoformat()}
    Total Duration: {self.total_duration} ms
    Total CPU Time: {self.total_cpu_time} ms
    Query CPU Time: {self.query_cpu_time} ms
    Vertipaq CPU Time: {self.vertipaq_cpu_time} ms
    Execution Delay: {self.execution_delay} ms
    Approximate Peak Consumption: {pretty_size(self.approximate_peak_consumption_kb * 1024)}
    Rows Returned: {self.rows_returned}
)"""


class Subscriber:
    trace_records: dict[str, list[dict[str, Any]]]
    reader: Reader

    def __init__(self, subscription_create_command: str, conn: Connection, events: Iterable[TraceEvents]) -> None:
        self.reader = conn.execute_dax(
            subscription_create_command,
        )  # occasionally seems to hang, but might actually be bad queries??
        self.events = events
        self.trace_records = {}
        self.command_request_ids: dict[str, str] = {}
        self.thread = threading.Thread(target=self.poll_cursor, daemon=True)
        self.thread.start()

    def poll_cursor(self) -> None:
        event_mapping = {e.value: e.name for e in self.events}
        for record in self.reader.fetch_stream():
            if "EventClass" in record:
                record["EventClass"] = event_mapping[record["EventClass"]]
            self.trace_records.setdefault(record["RequestID"], []).append(record)
            if "TextData" in record:
                self.command_request_ids[record["TextData"]] = record["RequestID"]

    def kill_polling(self) -> None:
        if self.thread.is_alive():
            self.thread.join(timeout=1)

    def __repr__(self) -> str:
        return f"Subscriber(records={len(self.trace_records)})"


class PerformanceTrace:
    events: Iterable[TraceEvents]
    db: BaseTabularModel
    commands: list[str]
    trace_create_command: str
    subscription_create_command: str
    trace_delete_command: str
    clear_cache_command: str

    def __init__(
        self,
        db: BaseTabularModel,
        commands: list[str],
        events: Iterable[TraceEvents] = TRACE_DEFAULT_EVENTS,
    ) -> None:
        self.events = events
        self.db: BaseTabularModel = db
        self.commands = [x.replace("\r\n", "\n") for x in commands]

        next_day = (datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        trace_name = f"pbi_core_{next_day.replace(':', '_')}"
        subscription_name = f"pbi_core_subscription_{next_day.replace(':', '_')}"
        self.trace_create_command = TRACE_TEMPLATES["trace_create.xml"].render(
            trace_name=trace_name,
            stop_time=next_day,
            events=self.events,
        )
        self.subscription_create_command = TRACE_TEMPLATES["subscription_create.xml"].render(
            trace_name=trace_name,
            subscription_name=subscription_name,
        )
        self.trace_delete_command = TRACE_TEMPLATES["trace_delete.xml"].render(
            trace_name=trace_name,
        )
        self.clear_cache_command = TRACE_TEMPLATES["clear_cache.xml"].render(database_name=self.db.db_name)

    def initialize_tracing(self) -> "PerformanceTrace":
        logger.info("Beginning trace")
        self.db.server.query_xml(self.trace_create_command)
        self.subscriber = Subscriber(
            self.subscription_create_command,
            self.get_conn(),
            self.events,
        )
        return self

    def terminate_tracing(self) -> None:
        logger.info("Terminating trace")
        with self.db.server.conn(db_name=self.db.db_name) as conn:
            conn.execute_xml(self.trace_delete_command)

    def get_performance(self, *, clear_cache: bool = False) -> list[Performance]:
        def thread_func(command: str) -> ThreadResult:
            try:
                with self.get_conn() as conn:
                    reader = conn.execute_dax(command)
                    rows_returned = len(reader.fetch_many(limit=500))

                    # See note in Reader.fetch_stream() documentation for why we do this
                    reader.close()

            except ValueError as e:
                return ThreadResult(
                    command=command,
                    rows_returned=-1,
                    error=e,
                )
            # The limit of 500 is to mimic the behavior of PowerBI, which returns by defult 500 rows
            return ThreadResult(
                command=command,
                rows_returned=rows_returned,
            )

        self.initialize_tracing()
        if clear_cache:
            logger.info("Clearing cache before performance testing")
            with self.db.server.conn(db_name=self.db.db_name) as conn:
                conn.execute_xml(self.clear_cache_command)

        with ThreadPoolExecutor() as dax_executor:
            logger.info("Running DAX commands")
            command_results = list(dax_executor.map(thread_func, self.commands))

        missing_subscription_records = command_results
        for _ in range(5):
            # Testing for 15 seconds to check that all commands have an entry in the trace
            new_missing_subscription_records = []
            for command in missing_subscription_records:
                request_id = self.subscriber.command_request_ids.get(command.command)
                if request_id is None:
                    new_missing_subscription_records.append(command)
                    continue
                command_events = self.subscriber.trace_records.get(request_id, [])
                if not any(x["EventClass"] == "QUERY_END" for x in command_events):
                    new_missing_subscription_records.append(command)

            if not new_missing_subscription_records:
                break
            time.sleep(1)
            missing_subscription_records = new_missing_subscription_records
        else:
            missing_commands = ", ".join(cmd.command for cmd in missing_subscription_records)
            msg = f"Some commands did not have trace records: {missing_commands}"
            raise ValueError(msg)

        self.subscriber.kill_polling()
        self.terminate_tracing()

        return [
            command_result.get_performance(
                self.subscriber.trace_records[self.subscriber.command_request_ids[command_result.command]],
            )
            for command_result in command_results
        ]

    def get_conn(self) -> Connection:
        return self.db.server.conn(db_name=self.db.db_name).open()
