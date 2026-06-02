"""Dialog for choosing which flow features to export."""

from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

import customtkinter as ctk

from cicflowmeter.fields import EXPORT_FIELD_NAMES, FIELD_GROUPS


class FieldPickerDialog(ctk.CTkToplevel):
    """Modal dialog with grouped checkboxes for export columns."""

    def __init__(
        self,
        master: ctk.CTk,
        *,
        initial: list[str] | None = None,
        on_apply: Callable[[list[str] | None], None] | None = None,
    ) -> None:
        super().__init__(master)
        self.title("Select export columns")
        self.geometry("640x560")
        self.minsize(520, 420)
        self.transient(master)
        self.grab_set()

        self._on_apply = on_apply
        self._result: list[str] | None = initial
        self._vars: dict[str, tk.BooleanVar] = {}

        selected = set(initial) if initial is not None else set(EXPORT_FIELD_NAMES)
        for name in EXPORT_FIELD_NAMES:
            var = tk.BooleanVar(value=name in selected)
            var.trace_add("write", lambda *_: self._update_count_label())
            self._vars[name] = var

        self._build_ui()
        self._center_over(master)
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.bind("<Escape>", lambda _e: self._cancel())

    def _center_over(self, master: ctk.CTk) -> None:
        self.update_idletasks()
        mx = master.winfo_rootx() + (master.winfo_width() - self.winfo_width()) // 2
        my = master.winfo_rooty() + (master.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{max(mx, 0)}+{max(my, 0)}")

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=(12, 6))
        toolbar.grid_columnconfigure(2, weight=1)

        ctk.CTkButton(toolbar, text="Select all", width=100, command=self._select_all).grid(
            row=0, column=0, padx=(0, 6)
        )
        ctk.CTkButton(toolbar, text="Clear all", width=100, command=self._clear_all).grid(
            row=0, column=1, padx=(0, 12)
        )

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._apply_search_filter())
        search = ctk.CTkEntry(toolbar, placeholder_text="Filter columns…", textvariable=self._search_var)
        search.grid(row=0, column=2, sticky="ew")

        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=1, column=0, sticky="nsew", padx=12, pady=6)
        scroll.grid_columnconfigure(0, weight=1)

        self._checkbox_widgets: list[tuple[ctk.CTkBaseClass, str, str]] = []
        row = 0
        for group_title, names in FIELD_GROUPS:
            header = ctk.CTkLabel(scroll, text=group_title, font=ctk.CTkFont(weight="bold"))
            header.grid(row=row, column=0, sticky="w", pady=(8, 2))
            self._checkbox_widgets.append((header, group_title, "header"))
            row += 1

            for name in names:
                cb = ctk.CTkCheckBox(scroll, text=name, variable=self._vars[name])
                cb.grid(row=row, column=0, sticky="w", padx=16, pady=1)
                self._checkbox_widgets.append((cb, name, "field"))
                row += 1

        self._count_label = ctk.CTkLabel(self, text="", anchor="w")
        self._count_label.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 4))
        self._update_count_label()

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="e", padx=12, pady=(0, 12))
        ctk.CTkButton(actions, text="Cancel", width=100, command=self._cancel).pack(
            side="right", padx=(8, 0)
        )
        ctk.CTkButton(actions, text="Apply", width=100, command=self._apply).pack(side="right")

    def _apply_search_filter(self) -> None:
        query = self._search_var.get().strip().lower()
        for widget, label, kind in self._checkbox_widgets:
            if kind == "header":
                # Show header if any field in its group matches (handled below per field).
                continue
            visible = not query or query in label.lower()
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

        # Hide group headers with no visible children.
        idx = 0
        while idx < len(self._checkbox_widgets):
            widget, label, kind = self._checkbox_widgets[idx]
            if kind == "header":
                has_visible = False
                j = idx + 1
                while j < len(self._checkbox_widgets) and self._checkbox_widgets[j][2] == "field":
                    child, child_label, _ = self._checkbox_widgets[j]
                    if not query or query in child_label.lower():
                        if child.winfo_ismapped():
                            has_visible = True
                            break
                    j += 1
                if has_visible or not query:
                    widget.grid()
                else:
                    widget.grid_remove()
            idx += 1

    def _selected_names(self) -> list[str]:
        return [name for name in EXPORT_FIELD_NAMES if self._vars[name].get()]

    def _update_count_label(self) -> None:
        count = len(self._selected_names())
        total = len(EXPORT_FIELD_NAMES)
        self._count_label.configure(text=f"{count} of {total} columns selected")

    def _select_all(self) -> None:
        for var in self._vars.values():
            var.set(True)
        self._update_count_label()

    def _clear_all(self) -> None:
        for var in self._vars.values():
            var.set(False)
        self._update_count_label()

    def _apply(self) -> None:
        selected = self._selected_names()
        if not selected:
            from tkinter import messagebox

            messagebox.showerror(
                "No columns selected",
                "Select at least one column to export, or cancel to keep the previous selection.",
                parent=self,
            )
            return

        if len(selected) == len(EXPORT_FIELD_NAMES):
            self._result = None
        else:
            self._result = selected

        if self._on_apply:
            self._on_apply(self._result)
        self.grab_release()
        self.destroy()

    def _cancel(self) -> None:
        self.grab_release()
        self.destroy()

    @property
    def result(self) -> list[str] | None:
        return self._result
