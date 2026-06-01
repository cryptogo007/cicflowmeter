"""Background job execution for the GUI."""

from __future__ import annotations

import queue
import threading
from dataclasses import dataclass
from enum import Enum

from cicflowmeter.flow_session import FlowSession
from cicflowmeter.sniffer import (
    process_directory,
    process_directory_merged,
    run_sniffer,
)


class JobType(Enum):
    SINGLE_FILE = "single_file"
    DIRECTORY = "directory"
    DIRECTORY_MERGED = "directory_merged"
    LIVE = "live"


@dataclass
class JobRequest:
    job_type: JobType
    input_path: str | None = None
    output_path: str = ""
    output_mode: str = "csv"
    interface: str | None = None
    merge: bool = False
    fields: str | None = None
    verbose: bool = False
    rotate_interval_minutes: float | None = None


class JobWorker(threading.Thread):
    def __init__(
        self,
        request: JobRequest,
        cancel_event: threading.Event,
        log_queue: queue.Queue,
        session_queue: queue.Queue,
    ) -> None:
        super().__init__(daemon=True)
        self.request = request
        self.cancel_event = cancel_event
        self.log_queue = log_queue
        self.session_queue = session_queue

    def _log(self, message: str) -> None:
        self.log_queue.put(("log", message))

    def _should_cancel(self) -> bool:
        return self.cancel_event.is_set()

    def _on_session(self, session: FlowSession) -> None:
        self.session_queue.put(session)

    def run(self) -> None:
        req = self.request
        try:
            fields = req.fields.strip() if req.fields and req.fields.strip() else None

            if req.job_type == JobType.SINGLE_FILE:
                run_sniffer(
                    input_file=req.input_path,
                    output_mode=req.output_mode,
                    output=req.output_path,
                    fields=fields,
                    verbose=req.verbose,
                    should_cancel=self._should_cancel,
                    log=self._log,
                    on_session=self._on_session,
                )
            elif req.job_type == JobType.DIRECTORY_MERGED:
                process_directory_merged(
                    req.input_path,
                    req.output_path,
                    fields=fields,
                    verbose=req.verbose,
                    log=self._log,
                    should_cancel=self._should_cancel,
                )
            elif req.job_type == JobType.DIRECTORY:
                process_directory(
                    req.input_path,
                    req.output_path,
                    fields=fields,
                    verbose=req.verbose,
                    log=self._log,
                    should_cancel=self._should_cancel,
                )
            elif req.job_type == JobType.LIVE:
                rotate_seconds = None
                if req.rotate_interval_minutes is not None:
                    rotate_seconds = req.rotate_interval_minutes * 60.0
                run_sniffer(
                    input_interface=req.interface,
                    output_mode=req.output_mode,
                    output=req.output_path,
                    fields=fields,
                    verbose=req.verbose,
                    should_cancel=self._should_cancel,
                    log=self._log,
                    on_session=self._on_session,
                    rotate_interval_seconds=rotate_seconds,
                )
            else:
                raise ValueError(f"Unknown job type: {req.job_type}")
        except Exception as exc:
            self.log_queue.put(("error", str(exc)))
        finally:
            self.log_queue.put(("done", None))
