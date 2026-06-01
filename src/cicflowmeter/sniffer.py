import argparse
import time
import threading
from collections.abc import Callable
from pathlib import Path

from scapy.sendrecv import AsyncSniffer

from cicflowmeter.flow_session import FlowSession

GC_INTERVAL = 1.0  # seconds (tune as needed)

LogFn = Callable[[str], None] | None
CancelFn = Callable[[], bool] | None


def _emit(message: str, log: LogFn = None) -> None:
    if log:
        log(message)
    else:
        print(message)


def _cancelled(should_cancel: CancelFn) -> bool:
    return bool(should_cancel and should_cancel())


def _parse_fields(fields: str | list[str] | None) -> list[str] | None:
    if fields is None:
        return None
    if isinstance(fields, str):
        return [f.strip() for f in fields.split(",") if f.strip()]
    return list(fields)


def _stop_session_gc(session: FlowSession) -> None:
    if hasattr(session, "_gc_stop"):
        session._gc_stop.set()
        session._gc_thread.join(timeout=2.0)


def _start_periodic_gc(session: FlowSession, interval: float = GC_INTERVAL) -> None:
    stop_event = threading.Event()

    def _gc_loop():
        while not stop_event.wait(interval):
            try:
                session.garbage_collect(time.time())
            except Exception:
                session.logger.exception("Periodic GC error")

    t = threading.Thread(target=_gc_loop, name="flow-gc", daemon=True)
    t.start()
    session._gc_thread = t
    session._gc_stop = stop_event


def create_sniffer(
    input_file,
    input_interface,
    output_mode,
    output,
    input_directory=None,
    fields=None,
    verbose=False,
):
    assert sum([input_file is None, input_interface is None, input_directory is None]) == 2, (
        "Provide exactly one: interface, file, or directory input"
    )
    parsed_fields = _parse_fields(fields)

    session = FlowSession(
        output_mode=output_mode,
        output=output,
        fields=parsed_fields,
        verbose=verbose,
    )

    _start_periodic_gc(session, interval=GC_INTERVAL)

    if input_file:
        sniffer = AsyncSniffer(
            offline=input_file,
            filter="ip and (tcp or udp)",
            prn=session.process,
            store=False,
        )
    else:
        sniffer = AsyncSniffer(
            iface=input_interface,
            filter="ip and (tcp or udp)",
            prn=session.process,
            store=False,
        )
    return sniffer, session


def run_sniffer(
    *,
    input_file: str | None = None,
    input_interface: str | None = None,
    output_mode: str,
    output: str,
    fields: str | list[str] | None = None,
    verbose: bool = False,
    should_cancel: CancelFn = None,
    log: LogFn = None,
    on_session: Callable[[FlowSession], None] | None = None,
) -> FlowSession:
    """Run live or offline capture until finished or cancelled."""
    sniffer, session = create_sniffer(
        input_file=input_file,
        input_interface=input_interface,
        output_mode=output_mode,
        output=output,
        fields=fields,
        verbose=verbose,
    )
    if on_session:
        on_session(session)
    sniffer.start()
    try:
        while getattr(sniffer, "running", False):
            if _cancelled(should_cancel):
                _emit("Stopping capture...", log)
                sniffer.stop()
                break
            time.sleep(0.1)
        sniffer.join()
    finally:
        _stop_session_gc(session)
        session.flush_flows()
    return session


def process_directory_merged(
    input_dir,
    output_dir,
    fields=None,
    verbose=False,
    log: LogFn = None,
    should_cancel: CancelFn = None,
):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    parsed_fields = _parse_fields(fields)

    if not input_path.exists():
        _emit(f"Error: Input directory '{input_dir}' does not exist", log)
        return

    if not input_path.is_dir():
        _emit(f"Error: Input path '{input_dir}' is not a directory", log)
        return

    if output_path.exists() and output_path.is_file():
        _emit(f"Error: Output path '{output_dir}' already exists as a file.", log)
        return

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        _emit(f"Error: Could not create output directory '{output_dir}': {e}", log)
        return

    pcap_files = list(input_path.glob("*.pcap")) + list(input_path.glob("*.pcapng"))

    if not pcap_files:
        _emit(f"Error: No pcap files found in {input_dir}", log)
        return

    output_file = output_path / "merged_output.csv"
    _emit(f"Found {len(pcap_files)} pcap file(s) to process", log)
    _emit(f"Merging all flows into: {output_file.name}", log)

    session = FlowSession(
        output_mode="csv",
        output=str(output_file),
        fields=parsed_fields,
        verbose=verbose,
    )

    _start_periodic_gc(session, interval=GC_INTERVAL)

    for idx, pcap_file in enumerate(pcap_files, 1):
        if _cancelled(should_cancel):
            _emit("Batch processing cancelled.", log)
            break

        _emit(f"[{idx}/{len(pcap_files)}] Processing {pcap_file.name}...", log)

        try:
            sniffer = AsyncSniffer(
                offline=str(pcap_file),
                filter="ip and (tcp or udp)",
                prn=session.process,
                store=False,
            )

            sniffer.start()
            sniffer.join()

            _emit(f"[{idx}/{len(pcap_files)}] Completed {pcap_file.name}", log)
        except Exception as e:
            _emit(f"Error processing {pcap_file.name}: {e}", log)
            continue

    _stop_session_gc(session)
    session.flush_flows()

    if not _cancelled(should_cancel):
        _emit(f"\nAll done! Merged output saved to: {output_file}", log)


def process_directory(
    input_dir,
    output_dir,
    fields=None,
    verbose=False,
    log: LogFn = None,
    should_cancel: CancelFn = None,
):
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    parsed_fields = _parse_fields(fields)

    if not input_path.exists():
        _emit(f"Error: Input directory '{input_dir}' does not exist", log)
        return

    if not input_path.is_dir():
        _emit(f"Error: Input path '{input_dir}' is not a directory", log)
        return

    if output_path.exists() and output_path.is_file():
        _emit(f"Error: Output path '{output_dir}' already exists as a file.", log)
        return

    try:
        output_path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        _emit(f"Error: Could not create output directory '{output_dir}': {e}", log)
        return

    pcap_files = list(input_path.glob("*.pcap")) + list(input_path.glob("*.pcapng"))

    if not pcap_files:
        _emit(f"Error: No pcap files found in {input_dir}", log)
        return

    _emit(f"Found {len(pcap_files)} pcap file(s) to process", log)

    for pcap_file in pcap_files:
        if _cancelled(should_cancel):
            _emit("Batch processing cancelled.", log)
            break

        output_file = output_path / f"{pcap_file.stem}.csv"
        _emit(f"Processing {pcap_file.name} -> {output_file.name}", log)

        try:
            run_sniffer(
                input_file=str(pcap_file),
                output_mode="csv",
                output=str(output_file),
                fields=parsed_fields,
                verbose=verbose,
                should_cancel=should_cancel,
                log=log,
            )
            _emit(f"Completed {pcap_file.name}", log)
        except Exception as e:
            _emit(f"Error processing {pcap_file.name}: {e}", log)
            continue

    if not _cancelled(should_cancel):
        _emit(f"\nAll done! Output files saved to: {output_dir}", log)


def main():
    parser = argparse.ArgumentParser()

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-i",
        "--interface",
        action="store",
        dest="input_interface",
        help="capture online data from INPUT_INTERFACE",
    )
    input_group.add_argument(
        "-f",
        "--file",
        action="store",
        dest="input_file",
        help="capture offline data from INPUT_FILE",
    )
    input_group.add_argument(
        "-d",
        "--directory",
        action="store",
        dest="input_directory",
        help="process all pcap files from INPUT_DIRECTORY",
    )

    output_group = parser.add_mutually_exclusive_group(required=True)
    output_group.add_argument(
        "-c",
        "--csv",
        action="store_const",
        const="csv",
        dest="output_mode",
        help="output flows as csv",
    )
    output_group.add_argument(
        "-u",
        "--url",
        action="store_const",
        const="url",
        dest="output_mode",
        help="output flows as request to url",
    )

    parser.add_argument(
        "output",
        help="output file name (in csv mode), url (in url mode), or output directory (in directory mode)",
    )

    parser.add_argument(
        "--fields",
        action="store",
        dest="fields",
        help="comma separated fields to include in output (default: all)",
    )

    parser.add_argument(
        "--merge",
        action="store_true",
        help="merge all pcap files into a single CSV (only works with -d/--directory mode)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="more verbose")

    args = parser.parse_args()
    if args.merge and not args.input_directory:
        parser.error("--merge can only be used with -d/--directory mode")
    if args.input_directory:
        if args.merge:
            process_directory_merged(
                args.input_directory,
                args.output,
                args.fields,
                args.verbose,
            )
        else:
            process_directory(
                args.input_directory,
                args.output,
                args.fields,
                args.verbose,
            )
        return

    try:
        run_sniffer(
            input_file=args.input_file,
            input_interface=args.input_interface,
            output_mode=args.output_mode,
            output=args.output,
            fields=args.fields,
            verbose=args.verbose,
        )
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
