#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

"""
records-tkinter.py

A tkinter records management GUI application, using records.py module backend.

:author: "Craig MacEachern"
:email: "craigmaceachern@fastmail.com"
:license: "MIT"
:version: 1.20

TODO:
    * Convert to exe
    * Write to file
"""
import argparse
import logging
# Python 2/3 compatibility
try:
    import Tkinter as tk
    import ScrolledText as tkst
    import ttk
    import tkFileDialog as tkfd
    import tkMessageBox as tkmb
except ImportError:  # We are on Python 3+
    import tkinter as tk
    import tkinter.scrolledtext as tkst
    import tkinter.filedialog as tkfd
    import tkinter.messagebox as tkmb
    import tkinter.ttk as ttk
import records  # Custom module


class Application(ttk.Frame):  # Tkinter.Frame
    """
    Instance of a Tkinter GUI application using new ttk styles.
    """
    def __init__(self, cli_args, master=None):
        """
        Initialize ttk themed Tk frame.

        :param cli_args: a list of arguments passed in from command line.
        :param master: Optional. Parent of this Frame.
        """
        ttk.Frame.__init__(self, master)

        # Make the Frame span all columns and rows so it contains all widgets
        self.grid(column=0, row=0, columnspan=4, rowspan=9, padx=10, pady=10)
        self._create_widgets()

        # Logger with name of this file
        self.log = logging.getLogger(__name__)

        if cli_args.verbose or cli_args.v:
                self.log.setLevel(logging.DEBUG)
                print("Using DEBUG level because detected -v flag")
        else:
            self.log.setLevel(logging.DEBUG) # Remove on release
            """
            self.log.setLevel(logging.ERROR)
            print("Using ERROR level logging because no verbosity flags found")
            """

        # Logger handler and format
        _log_console_handler = logging.StreamHandler()  # Writing to stderr
        _log_console_format = logging.Formatter("%(asctime)s: %(levelname)s:"
                                                " %(message)s")
        _log_console_handler.setFormatter(_log_console_format)

        # Register the log handler
        self.log.addHandler(_log_console_handler)

        # Init here to check if results exist if we try to save before
        # searching first
        self.results = []

    def _create_widgets(self):
        """Create and position the ttk/Tk widgets in the Frame."""
        # ################################################################
        #           LABELS, ENTRIES & BUTTONS
        # ################################################################

        # Save results -- if using this, remove the save file field and btn
        self.save_results_btn = ttk.Button(self, text="Save", width=10,
                                           command=self.write_results_to_file)

        # Scan path
        self.scan_lbl = ttk.Label(self, text="Scan path start")
        self.scan_path_value = tk.StringVar()
        self.scan_path_value.set("")  # Default text
        self.scan_path_entry = ttk.Entry(self,
                                         width=50,
                                         textvariable=self.scan_path_value,
                                         state="disabled"
                                         )
        self.scan_path_btn = ttk.Button(self,
                                        width=10,
                                        text="...",
                                        command=self.btn_path_clicked
                                        )

        # Blacklist
        self.blacklist_lbl = ttk.Label(self, text="Blacklist file")
        self.blacklist_file_value = tk.StringVar()
        self.blacklist_file_value.set("")
        self.blacklist_entry = ttk.Entry(self,
                                         textvariable=(
                                             self.blacklist_file_value
                                             ),
                                         width=50,
                                         state="disabled"
                                         )
        self.blacklist_btn = ttk.Button(self,
                                        width=10,
                                        text="...",
                                        command=self.btn_blacklist_clicked
                                        )

        # Format selection
        self.format_lbl = ttk.Label(self, text="Save Format")
        self.format_value = tk.StringVar()
        self.format_value.set("txt")  # use .get() to get string from it
        self.format_combobox = ttk.Combobox(self,
                                            values=("txt", "csv"),
                                            textvariable=self.format_value,
                                            width=10,
                                            state="readonly"
                                            )

        # Last selection
        self.last_lbl = ttk.Label(self, text="File last")
        self.last_value = tk.StringVar()
        self.last_value.set("modified")
        self.last_combobox = ttk.Combobox(self,
                                          values=("modified", "accessed"),
                                          textvariable=self.last_value,
                                          width=10,
                                          state="readonly"
                                          )

        # Hidden selection
        self.hidden_lbl = ttk.Label(self, text="Include hidden")
        self.hidden_value = tk.StringVar()
        self.hidden_value.set("no")
        self.hidden_combobox = ttk.Combobox(self,
                                            values=("no", "yes"),
                                            textvariable=self.hidden_value,
                                            width=10,
                                            state="readonly"
                                            )

        # Days entry
        self.days_lbl = ttk.Label(self, text="Days")
        self.days_value = tk.IntVar()
        self.days_value.set(90)
        # No ttk themed Spinbox, requires Tk 8.5.9+, using classic Tk one
        self.days_entry = ttk.Entry(self,
                                    width=10,
                                    textvariable=self.days_value,
                                    )

        # Results area
        self.results_text = tkst.ScrolledText(self,
                                              borderwidth=5,
                                              state="disabled"
                                              )

        # Save results button
        self.save_file_btn = ttk.Button(self,
                                        width=10,
                                        text="Save",
                                        command=self.write_results_to_file
                                        )
        # Start Scan button
        self.scan_btn = ttk.Button(self,
                                   width=10,
                                   text="Scan",
                                   command=self.btn_go_scan
                                   )

        # ################################################################
        #           GRID PLACEMENTS
        # ################################################################

        self.scan_lbl.grid(column=0, row=0)
        self.scan_path_entry.grid(column=0, row=1)
        self.scan_path_btn.grid(column=1, row=1, sticky=tk.W)

        """
        # Remove in favour of explicit button to save file.
        self.save_lbl.grid(column=0, row=2)
        self.save_file_entry.grid(column=0, row=3)
        self.save_file_btn.grid(column=1, row=3, sticky=tk.W)
        """

        self.blacklist_lbl.grid(column=0, row=3)
        self.blacklist_entry.grid(column=0, row=4)
        self.blacklist_btn.grid(column=1, row=4, sticky=tk.W)

        self.format_lbl.grid(column=2, row=0)
        self.format_combobox.grid(column=2, row=1)

        self.last_lbl.grid(column=2, row=2)
        self.last_combobox.grid(column=2, row=3)

        self.days_lbl.grid(column=3, row=0)
        self.days_entry.grid(column=3, row=1)

        self.hidden_lbl.grid(column=3, row=2)
        self.hidden_combobox.grid(column=3, row=3)

        self.results_text.grid(column=0, row=7, pady=10, columnspan=4)

        self.save_file_btn.grid(column=2, row=8, sticky=tk.E)
        self.scan_btn.grid(column=3, row=8, sticky=tk.E)

    def collect_options(self):
        """
        Get all GUI options and return a dict of all the options selected.

        :returns: A dictionary of keys named after the GUI fields.
        """
        options = {'scan_path': self.scan_path_value.get(),
                   'blacklist_file': self.blacklist_file_value.get(),
                   'format': self.format_value.get(),
                   'last': self.last_value.get(),
                   'hidden': self.hidden_value.get(),
                   'days': self.days_entry.get()
                   }
        return options

    def validate_options(self, opts):
        """
        Return a tuple of (True, None) if dictionary 'opts' passes validation
        tests, otherwise return a tuple of False and the key of 'opts' that
        failed.

        :param opts: a dictionary to check for false-y values.
        :returns: A tuple of (Bool, string or None).
        """
        for k, v in opts.iteritems():
            if k == "blacklist_file":  # Gotcha: this field CAN be false-y!
                continue
            if k == "days":  # Gotcha: make sure we can cast it to int
                try:
                    self.options[k] = int(v)
                except ValueError:
                    return False, k
            if not v:  # False-y, like empty string or 0
                return False, k  # Return key that had the False-y state
        return True, None

    def btn_go_scan(self):
        """
        Uses records.py module to search and ouputs results if any to
        the tkst widget area.
        """
        self.options = self.collect_options()

        self.log.debug("Using options: {}".format(self.options))

        # Check selected GUI options
        validate_ok, false_key = self.validate_options(self.options)

        if validate_ok:
            self.log.debug("Options passed validation")
            # Run scan
            self.log.info("Scan starting...")

            # ##################################################
            #           MAIN WORK OF ACTUAL SEARCH GOES ON HERE
            # ##################################################

            # Get blacklist
            if not self.options["blacklist_file"]:  # Gotcha: if field is empty
                self.blacklist = []
            else:
                self.blacklist = records.get_blacklist(self.options[
                                                       "blacklist_file"]
                                                       )
            self.log.debug("Using these blacklist values: ")
            self.log.debug(self.blacklist)

            # Gather all the files using our module
            self.all_files = records.get_file_paths(self.options["scan_path"],
                                                    self.blacklist,
                                                    self.options["hidden"]
                                                    )
            self.log.debug("Found all these files in the given path: \n")
            self.log.debug(self.all_files)

            # Filter all found files by our criteria
            self.results = records.get_cutoff_files(self.all_files,
                                                    self.options["days"],
                                                    self.options["last"]
                                                    )
            self.log.debug("The filtered results: \n")
            self.log.debug(self.results)

            # Write results to the window
            self.show_results()

            # ##################################################
            #           MAIN WORK OF ACTUAL SEARCH DONE
            # ##################################################

        # Validation failed, present message to user and debug info
        else:
            self.log.error("Options failed validation")
            self.log.debug("{} field reports False state".format(false_key))
            # Tell user
            tkmb.showerror(message="One or more options incorrect.")

    def show_results(self):
        """
        Write the list to the tkst widget on the screen using a
        string format defined here to show some details about each file.
        """
        pass

    def write_results_to_file(self):
        """
        Returns True if able to write the contents of result_list to file,
        otherwise returns False.
        """
        if not self.results:  # We haven't scanned yet!
            self.log.error("results list is empty, can not save to file")
            tkmb.showerror(message="There are no results to write to file")
        else:
            # Open file dialog here to get file to save to
            self.log.debug("Opening Tk save file dialog.")
            save_dialog = tkfd.SaveAs(self)
            save_loc = save_dialog.show()

            try:
                records.write_to_file(self.results, save_loc,
                                      self.options["format"],
                                      self.options["last"]
                                      )
            except IOError:  # records.write_to_file() raises this
                self.log.error("Could not write to file!")
                tkmb.showinfo(message="Could not write results to "
                                      " file: {}".format(save_loc))
            else:
                # Notify user of success in log and visually
                self.log.info("Successfully wrote to "
                              "file: {}".format(save_loc))
                tkmb.showinfo(message="Successfully wrote results to"
                                      " file: {}".format(save_loc))

    def btn_blacklist_clicked(self):
        """
        Open a Tk file dialog to select blacklist file.
        """
        self.log.debug("Blacklist file dialog opened.")
        self.blacklist_file = tkfd.askopenfile()
        if self.blacklist_file:
            self.log.info("Using blacklist " +
                          "file:{}".format(self.blacklist_file))
            self.blacklist_file_value.set(self.blacklist_file.name)

    def btn_path_clicked(self):
        """
        Open a Tk file dialog to ask for a directory to start the scan from.
        """
        self.log.debug("Path to start scanning dialog opened.")
        self.dirname = tkfd.askdirectory()
        if self.dirname:
            self.log.info("Starting scan at path: {}".format(self.dirname))
            self.scan_path_value.set(self.dirname)

if __name__ == "__main__":
    # Set up Tkinter.Tk() window
    root = tk.Tk()
    root.wm_resizable(0, 0)  # No resizing either direction
    # Get arguments if any from command line for log verbosity
    parser = argparse.ArgumentParser(prog="Records Manager",
                                     description=("A program to find files "
                                                  "over a certain amount of "
                                                  "days")
                                     )
    parser.add_argument("-v", help="Show debugging messages at runtime.",
                        action="store_true")
    parser.add_argument("--verbose",
                        help="Show debugging messages at runtime.",
                        action="store_true")
    cli_args = parser.parse_args()
    # Our application
    app = Application(cli_args, master=root)
    app.master.title("Records Manager")
    app.master.configure(width=640, height=480)
    app.mainloop()
