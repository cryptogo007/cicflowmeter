"""CICFlowMeter desktop application."""

from __future__ import annotations

import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from cicflowmeter.fields import fields_to_csv_arg, selection_summary
from cicflowmeter.flow_session import FlowSession
from cicflowmeter_gui.field_picker import FieldPickerDialog
from cicflowmeter_gui.platform_win import capture_readiness_message, list_network_interfaces
from cicflowmeter_gui.worker import JobRequest, JobType, JobWorker

POLL_MS = 200


class CICFlowMeterApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CICFlowMeter")
        self.geometry("920x720")
        self.minsize(800, 600)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._cancel_event = None
        self._worker: JobWorker | None = None
        self._log_queue: queue.Queue | None = None
        self._session_queue: queue.Queue | None = None
        self._active_session: FlowSession | None = None
        self._running = False
        self._export_fields: list[str] | None = None
        self._export_fields_labels: list[ctk.CTkLabel] = []

        self._build_ui()
        self._refresh_interfaces()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 6))
        self.tab_convert = self.tabview.add("Convert PCAP")
        self.tab_live = self.tabview.add("Live Capture")

        self._build_convert_tab()
        self._build_live_tab()
        self._build_monitor_panel()

    def _build_convert_tab(self) -> None:
        tab = self.tab_convert
        tab.grid_columnconfigure(1, weight=1)

        self.convert_mode = tk.StringVar(value="file")

        ctk.CTkLabel(tab, text="Input mode").grid(row=0, column=0, sticky="w", padx=8, pady=(8, 2))
        mode_frame = ctk.CTkFrame(tab, fg_color="transparent")
        mode_frame.grid(row=0, column=1, sticky="w", padx=8, pady=(8, 2))
        ctk.CTkRadioButton(
            mode_frame, text="Single PCAP", variable=self.convert_mode, value="file", command=self._on_convert_mode
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            mode_frame, text="Folder of PCAPs", variable=self.convert_mode, value="folder", command=self._on_convert_mode
        ).pack(side="left")

        ctk.CTkLabel(tab, text="Input").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        self.convert_input = ctk.CTkEntry(tab, placeholder_text="PCAP file or folder")
        self.convert_input.grid(row=1, column=1, sticky="ew", padx=8, pady=4)
        ctk.CTkButton(tab, text="Browse…", width=90, command=self._browse_convert_input).grid(
            row=1, column=2, padx=8, pady=4
        )

        ctk.CTkLabel(tab, text="Output").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.convert_output = ctk.CTkEntry(tab, placeholder_text="CSV file or output folder")
        self.convert_output.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        ctk.CTkButton(tab, text="Browse…", width=90, command=self._browse_convert_output).grid(
            row=2, column=2, padx=8, pady=4
        )

        self.convert_merge = ctk.CTkCheckBox(tab, text="Merge folder into single CSV (merged_output.csv)")
        self.convert_merge.grid(row=3, column=1, sticky="w", padx=8, pady=4)

        ctk.CTkLabel(tab, text="Output type").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        out_frame = ctk.CTkFrame(tab, fg_color="transparent")
        out_frame.grid(row=4, column=1, sticky="w", padx=8, pady=4)
        self.convert_output_mode_var = tk.StringVar(value="csv")
        ctk.CTkRadioButton(
            out_frame, text="CSV file", variable=self.convert_output_mode_var, value="csv"
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            out_frame, text="HTTP URL", variable=self.convert_output_mode_var, value="url"
        ).pack(side="left")

        self._add_export_fields_row(tab, row=5)

        self.convert_verbose = ctk.CTkCheckBox(tab, text="Verbose logging")
        self.convert_verbose.grid(row=6, column=1, sticky="w", padx=8, pady=4)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=7, column=1, sticky="w", padx=8, pady=12)
        self.convert_start_btn = ctk.CTkButton(btn_frame, text="Start conversion", command=self._start_convert)
        self.convert_start_btn.pack(side="left", padx=(0, 8))
        self.convert_stop_btn = ctk.CTkButton(
            btn_frame, text="Stop", fg_color="#8b0000", hover_color="#a52a2a", command=self._stop_job, state="disabled"
        )
        self.convert_stop_btn.pack(side="left")

        self._on_convert_mode()

    def _build_live_tab(self) -> None:
        tab = self.tab_live
        tab.grid_columnconfigure(1, weight=1)

        self.live_warning = ctk.CTkLabel(
            tab,
            text="",
            text_color="#e6a700",
            wraplength=700,
            justify="left",
        )
        self.live_warning.grid(row=0, column=0, columnspan=3, sticky="ew", padx=8, pady=(8, 4))

        ctk.CTkLabel(tab, text="Interface").grid(row=1, column=0, sticky="w", padx=8, pady=4)
        iface_frame = ctk.CTkFrame(tab, fg_color="transparent")
        iface_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=8, pady=4)
        iface_frame.grid_columnconfigure(0, weight=1)
        self.live_interface = ctk.CTkComboBox(iface_frame, values=["(no interfaces)"])
        self.live_interface.grid(row=0, column=0, sticky="ew")
        ctk.CTkButton(iface_frame, text="Refresh", width=90, command=self._refresh_interfaces).grid(
            row=0, column=1, padx=(8, 0)
        )

        ctk.CTkLabel(tab, text="Output").grid(row=2, column=0, sticky="w", padx=8, pady=4)
        self.live_output = ctk.CTkEntry(tab, placeholder_text="Output CSV path or prediction URL")
        self.live_output.grid(row=2, column=1, sticky="ew", padx=8, pady=4)
        ctk.CTkButton(tab, text="Browse…", width=90, command=self._browse_live_output).grid(
            row=2, column=2, padx=8, pady=4
        )

        ctk.CTkLabel(tab, text="Output type").grid(row=3, column=0, sticky="w", padx=8, pady=4)
        live_out_frame = ctk.CTkFrame(tab, fg_color="transparent")
        live_out_frame.grid(row=3, column=1, sticky="w", padx=8, pady=4)
        self.live_output_mode_var = tk.StringVar(value="csv")
        ctk.CTkRadioButton(
            live_out_frame,
            text="CSV file",
            variable=self.live_output_mode_var,
            value="csv",
            command=self._on_live_output_mode_change,
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            live_out_frame,
            text="HTTP URL",
            variable=self.live_output_mode_var,
            value="url",
            command=self._on_live_output_mode_change,
        ).pack(side="left")

        ctk.CTkLabel(tab, text="CSV rotation").grid(row=4, column=0, sticky="w", padx=8, pady=4)
        rotate_frame = ctk.CTkFrame(tab, fg_color="transparent")
        rotate_frame.grid(row=4, column=1, columnspan=2, sticky="w", padx=8, pady=4)
        self.live_rotate_enable = ctk.CTkCheckBox(
            rotate_frame,
            text="New file every",
            command=self._on_live_rotate_toggle,
        )
        self.live_rotate_enable.pack(side="left", padx=(0, 8))
        self.live_rotate_minutes = ctk.CTkEntry(rotate_frame, width=60, placeholder_text="5")
        self.live_rotate_minutes.pack(side="left", padx=(0, 4))
        ctk.CTkLabel(rotate_frame, text="min → base.csv, base1.csv, base2.csv…").pack(side="left")

        self._add_export_fields_row(tab, row=5)

        self.live_verbose = ctk.CTkCheckBox(tab, text="Verbose logging")
        self.live_verbose.grid(row=6, column=1, sticky="w", padx=8, pady=4)

        btn_frame = ctk.CTkFrame(tab, fg_color="transparent")
        btn_frame.grid(row=7, column=1, sticky="w", padx=8, pady=12)
        self.live_start_btn = ctk.CTkButton(btn_frame, text="Start capture", command=self._start_live)
        self.live_start_btn.pack(side="left", padx=(0, 8))
        self.live_stop_btn = ctk.CTkButton(
            btn_frame, text="Stop", fg_color="#8b0000", hover_color="#a52a2a", command=self._stop_job, state="disabled"
        )
        self.live_stop_btn.pack(side="left")

        self._on_live_output_mode_change()
        self._update_live_warning()

    def _build_monitor_panel(self) -> None:
        panel = ctk.CTkFrame(self)
        panel.grid(row=1, column=0, sticky="ew", padx=12, pady=(6, 12))
        panel.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))
        for i in range(4):
            top.grid_columnconfigure(i, weight=1)

        self.status_label = ctk.CTkLabel(top, text="Status: Idle", anchor="w")
        self.status_label.grid(row=0, column=0, sticky="w", padx=4)
        self.packets_label = ctk.CTkLabel(top, text="Packets: 0", anchor="w")
        self.packets_label.grid(row=0, column=1, sticky="w", padx=4)
        self.active_label = ctk.CTkLabel(top, text="Active flows: 0", anchor="w")
        self.active_label.grid(row=0, column=2, sticky="w", padx=4)
        self.written_label = ctk.CTkLabel(top, text="Flows written: 0", anchor="w")
        self.written_label.grid(row=0, column=3, sticky="w", padx=4)

        self.output_file_label = ctk.CTkLabel(panel, text="Output file: —", anchor="w")
        self.output_file_label.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 0))

        ctk.CTkLabel(panel, text="Activity log").grid(row=2, column=0, sticky="w", padx=12, pady=(4, 0))
        self.log_box = ctk.CTkTextbox(panel, height=160)
        self.log_box.grid(row=3, column=0, sticky="ew", padx=8, pady=(4, 8))
        self.log_box.configure(state="disabled")

    def _add_export_fields_row(self, tab: ctk.CTkFrame, *, row: int) -> None:
        ctk.CTkLabel(tab, text="Export columns").grid(row=row, column=0, sticky="w", padx=8, pady=4)
        fields_frame = ctk.CTkFrame(tab, fg_color="transparent")
        fields_frame.grid(row=row, column=1, columnspan=2, sticky="ew", padx=8, pady=4)
        fields_frame.grid_columnconfigure(0, weight=1)
        label = ctk.CTkLabel(
            fields_frame,
            text=selection_summary(self._export_fields),
            anchor="w",
        )
        label.grid(row=0, column=0, sticky="ew")
        self._export_fields_labels.append(label)
        ctk.CTkButton(
            fields_frame,
            text="Choose columns…",
            width=140,
            command=self._open_field_picker,
        ).grid(row=0, column=1, padx=(8, 0))

    def _open_field_picker(self) -> None:
        def on_apply(selected: list[str] | None) -> None:
            self._export_fields = selected
            summary = selection_summary(selected)
            for lbl in self._export_fields_labels:
                lbl.configure(text=summary)

        FieldPickerDialog(self, initial=self._export_fields, on_apply=on_apply)

    def _export_fields_arg(self) -> str | None:
        return fields_to_csv_arg(self._export_fields)

    def _on_convert_mode(self) -> None:
        is_folder = self.convert_mode.get() == "folder"
        if is_folder:
            self.convert_merge.configure(state="normal")
        else:
            self.convert_merge.deselect()
            self.convert_merge.configure(state="disabled")

    def _on_live_output_mode_change(self) -> None:
        csv_mode = self.live_output_mode_var.get() == "csv"
        state = "normal" if csv_mode else "disabled"
        self.live_rotate_enable.configure(state=state)
        self.live_rotate_minutes.configure(state=state)
        if not csv_mode:
            self.live_rotate_enable.deselect()

    def _on_live_rotate_toggle(self) -> None:
        if self.live_rotate_enable.get() and not self.live_rotate_minutes.get().strip():
            self.live_rotate_minutes.insert(0, "5")

    def _parse_live_rotate_minutes(self) -> float | None:
        if not self.live_rotate_enable.get():
            return None
        if self.live_output_mode_var.get() != "csv":
            return None
        raw = self.live_rotate_minutes.get().strip()
        if not raw:
            messagebox.showerror("Invalid interval", "Enter rotation interval in minutes (e.g. 5).")
            return None
        try:
            minutes = float(raw)
        except ValueError:
            messagebox.showerror("Invalid interval", "Rotation interval must be a number.")
            return None
        if minutes <= 0:
            messagebox.showerror("Invalid interval", "Rotation interval must be greater than 0.")
            return None
        return minutes

    def _refresh_interfaces(self) -> None:
        ifaces = list_network_interfaces()
        if not ifaces:
            ifaces = ["(no interfaces)"]
        self.live_interface.configure(values=ifaces)
        self.live_interface.set(ifaces[0])
        self._update_live_warning()

    def _update_live_warning(self) -> None:
        msg = capture_readiness_message()
        if msg:
            self.live_warning.configure(text=msg)
        else:
            self.live_warning.configure(text="Live capture is ready. Use Stop to end capture and flush flows.")

    def _append_log(self, text: str) -> None:
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=f"Status: {text}")

    def _reset_stats(self) -> None:
        self.packets_label.configure(text="Packets: 0")
        self.active_label.configure(text="Active flows: 0")
        self.written_label.configure(text="Flows written (segment): 0")
        self.output_file_label.configure(text="Output file: —")

    def _update_stats_from_session(self) -> None:
        session = self._active_session
        if session is None:
            return
        try:
            stats = session.get_stats()
        except Exception:
            return
        self.packets_label.configure(text=f"Packets: {stats['packets']:,}")
        self.active_label.configure(text=f"Active flows: {stats['active_flows']:,}")
        segment_written = stats.get("segment_flows_written", stats["flows_written"])
        self.written_label.configure(text=f"Flows written (segment): {segment_written:,}")
        output_file = stats.get("output_file")
        if output_file:
            self.output_file_label.configure(text=f"Output file: {output_file}")

    def _browse_convert_input(self) -> None:
        if self.convert_mode.get() == "file":
            path = filedialog.askopenfilename(
                title="Select PCAP file",
                filetypes=[("PCAP files", "*.pcap *.pcapng"), ("All files", "*.*")],
            )
        else:
            path = filedialog.askdirectory(title="Select folder with PCAP files")
        if path:
            self.convert_input.delete(0, "end")
            self.convert_input.insert(0, path)

    def _browse_convert_output(self) -> None:
        if self.convert_mode.get() == "folder":
            path = filedialog.askdirectory(title="Select output folder")
        else:
            path = filedialog.asksaveasfilename(
                title="Save CSV as",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            )
        if path:
            self.convert_output.delete(0, "end")
            self.convert_output.insert(0, path)

    def _browse_live_output(self) -> None:
        if self.live_output_mode_var.get() == "url":
            return
        path = filedialog.asksaveasfilename(
            title="Save live capture CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if path:
            self.live_output.delete(0, "end")
            self.live_output.insert(0, path)

    def _convert_output_mode(self) -> str:
        return self.convert_output_mode_var.get()

    def _live_output_mode(self) -> str:
        return self.live_output_mode_var.get()

    def _validate_paths(self, input_path: str, output_path: str, *, require_file_input: bool) -> bool:
        if not input_path.strip():
            messagebox.showerror("Missing input", "Please choose an input path.")
            return False
        if not output_path.strip():
            messagebox.showerror("Missing output", "Please choose an output path or URL.")
            return False

        inp = Path(input_path)
        if require_file_input:
            if not inp.is_file():
                messagebox.showerror("Invalid input", f"Input file not found:\n{input_path}")
                return False
        elif not inp.is_dir():
            messagebox.showerror("Invalid input", f"Input folder not found:\n{input_path}")
            return False
        return True

    def _set_running(self, running: bool) -> None:
        self._running = running
        state = "disabled" if running else "normal"
        stop_state = "normal" if running else "disabled"
        self.convert_start_btn.configure(state=state)
        self.live_start_btn.configure(state=state)
        self.convert_stop_btn.configure(state=stop_state)
        self.live_stop_btn.configure(state=stop_state)

    def _start_job(self, request: JobRequest) -> None:
        if self._running:
            messagebox.showwarning("Busy", "A job is already running.")
            return

        self._cancel_event = threading.Event()
        self._log_queue = queue.Queue()
        self._session_queue = queue.Queue()
        self._active_session = None
        self._reset_stats()
        self._set_status("Running")
        self._set_running(True)

        self._worker = JobWorker(
            request=request,
            cancel_event=self._cancel_event,
            log_queue=self._log_queue,
            session_queue=self._session_queue,
        )
        self._worker.start()
        self._poll_queues()

    def _start_convert(self) -> None:
        input_path = self.convert_input.get().strip()
        output_path = self.convert_output.get().strip()
        is_folder = self.convert_mode.get() == "folder"
        merge = bool(self.convert_merge.get()) and is_folder

        if not self._validate_paths(input_path, output_path, require_file_input=not is_folder):
            return

        if merge:
            job_type = JobType.DIRECTORY_MERGED
        elif is_folder:
            job_type = JobType.DIRECTORY
        else:
            job_type = JobType.SINGLE_FILE

        if self._convert_output_mode() == "url" and not output_path.startswith(("http://", "https://")):
            messagebox.showerror("Invalid URL", "URL output must start with http:// or https://")
            return

        request = JobRequest(
            job_type=job_type,
            input_path=input_path,
            output_path=output_path,
            output_mode=self._convert_output_mode(),
            merge=merge,
            fields=self._export_fields_arg(),
            verbose=bool(self.convert_verbose.get()),
        )
        self._append_log(f"Starting conversion ({job_type.value})…")
        self._start_job(request)

    def _start_live(self) -> None:
        iface = self.live_interface.get()
        if iface in ("", "(no interfaces)"):
            messagebox.showerror("No interface", "Select a network interface or install Npcap.")
            return

        output_path = self.live_output.get().strip()
        if not output_path:
            messagebox.showerror("Missing output", "Enter an output CSV path or URL.")
            return

        mode = self._live_output_mode()
        if mode == "url" and not output_path.startswith(("http://", "https://")):
            messagebox.showerror("Invalid URL", "URL output must start with http:// or https://")
            return

        warning = capture_readiness_message()
        if warning:
            if not messagebox.askyesno("Capture warning", f"{warning}\n\nStart capture anyway?"):
                return

        rotate_minutes = self._parse_live_rotate_minutes()
        if rotate_minutes is None and self.live_rotate_enable.get():
            return

        request = JobRequest(
            job_type=JobType.LIVE,
            interface=iface,
            output_path=output_path,
            output_mode=mode,
            fields=self._export_fields_arg(),
            verbose=bool(self.live_verbose.get()),
            rotate_interval_minutes=rotate_minutes,
        )
        if rotate_minutes:
            self._append_log(
                f"Starting live capture on {iface} (new CSV every {rotate_minutes:g} min)…"
            )
        else:
            self._append_log(f"Starting live capture on {iface}…")
        self._start_job(request)

    def _stop_job(self) -> None:
        if self._cancel_event and self._running:
            self._append_log("Stop requested…")
            self._cancel_event.set()
            self._set_status("Stopping")

    def _poll_queues(self) -> None:
        if self._log_queue:
            while True:
                try:
                    kind, payload = self._log_queue.get_nowait()
                except queue.Empty:
                    break
                if kind == "log":
                    self._append_log(str(payload))
                elif kind == "error":
                    self._append_log(f"ERROR: {payload}")
                    messagebox.showerror("Job failed", str(payload))

        if self._session_queue:
            while True:
                try:
                    session = self._session_queue.get_nowait()
                except queue.Empty:
                    break
                self._active_session = session

        self._update_stats_from_session()

        if self._worker and self._worker.is_alive():
            self.after(POLL_MS, self._poll_queues)
            return

        self._finish_job()

    def _finish_job(self) -> None:
        if not self._running:
            return
        self._active_session = None
        self._set_running(False)
        cancelled = self._cancel_event and self._cancel_event.is_set()
        self._set_status("Cancelled" if cancelled else "Idle")
        self._append_log("Job finished." if not cancelled else "Job cancelled.")
        self._worker = None

    def _on_close(self) -> None:
        if self._running:
            if not messagebox.askyesno("Quit", "A job is running. Stop it and quit?"):
                return
            if self._cancel_event:
                self._cancel_event.set()
            if self._worker:
                self._worker.join(timeout=3.0)
        self.destroy()


def main() -> None:
    app = CICFlowMeterApp()
    app.mainloop()
