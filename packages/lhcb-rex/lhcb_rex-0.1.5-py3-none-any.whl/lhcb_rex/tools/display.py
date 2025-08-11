import lhcb_rex.settings.globals as myGlobals
from termcolor import colored
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime
from rich.table import Table
import uproot
import os
import string
import re


def print_decay_splash(
    decay_strings,
    daughter_string,
    label_string,
    ordering_string,
    naming_scheme,
    mass_hypotheses,
    model_scheme,
):
    # myGlobals.console.print("")

    # Create hierarchy_string and hierarchy_labels using letters
    hierarchy_string = f"{decay_strings[0]} -> {daughter_string}"
    hierarchy_labels = f"{len(decay_strings[0]) * 'a'} cc "

    # Convert numerical labels to letters
    for character in label_string:
        if character == " ":
            hierarchy_labels += character
        else:
            hierarchy_labels += string.ascii_lowercase[(int(character) + 1) * 2]

    bracketless_hierarchy_string = ""
    bracketless_hierarchy_labels = ""

    # Iterate through the characters of hierarchy_string and hierarchy_labels together
    for char, label in zip(hierarchy_string, hierarchy_labels):
        if char not in ["{", "}"]:
            bracketless_hierarchy_string += char
            bracketless_hierarchy_labels += label

    # Remove double spaces
    bracketless_hierarchy_string = bracketless_hierarchy_string.replace("  ", " ")
    bracketless_hierarchy_labels = bracketless_hierarchy_labels.replace("  ", " ")

    bracketless_ordering_string = ordering_string.replace("{", "")
    bracketless_ordering_string = bracketless_ordering_string.replace("}", "")
    bracketless_ordering_string = bracketless_ordering_string.replace("  ", " ")

    labelled_bracketless_hierarchy_string = ""
    labelled_bracketless_hierarchy_labels = ""
    labelled_dim_string = ""
    for particle, particle_labels, ordering_i in zip(
        bracketless_hierarchy_string.split(" "),
        bracketless_hierarchy_labels.split(" "),
        bracketless_ordering_string.split(" "),
    ):
        if particle != " ":
            if particle == "->":
                labelled_bracketless_hierarchy_string += f" {particle}"
                labelled_bracketless_hierarchy_labels += f" {particle_labels}"
                labelled_dim_string += f" {len(particle_labels) * 'd'}"
            else:
                if len(particle) > 0:
                    current_label = particle_labels[0]

                    labelled_bracketless_hierarchy_string += f" {particle}"
                    labelled_bracketless_hierarchy_labels += f" {particle_labels}"

                    # now add label
                    next_label = (
                        string.ascii_lowercase[
                            string.ascii_lowercase.index(current_label) + 1
                        ]
                        if current_label != "z"
                        else "a"
                    )

                    label_i = f"{naming_scheme[int(ordering_i)]}"

                    if model_scheme[int(ordering_i)] != "PHSP":
                        label_i += f", {model_scheme[int(ordering_i)].split(' ')[0]}"
                    if mass_hypotheses is not None:
                        if naming_scheme[int(ordering_i)] in mass_hypotheses:
                            label_i += (
                                f", {mass_hypotheses[naming_scheme[int(ordering_i)]]}"
                            )

                    to_append = f"[{label_i}]  "
                    # if naming_scheme[int(ordering_i)] != 'NA': # this particle is reconstructed
                    if (
                        not re.match(r"^NA_\d{8}$", naming_scheme[int(ordering_i)])
                        and naming_scheme[int(ordering_i)] != "NA"
                    ):  # this particle is reconstructed
                        labelled_bracketless_hierarchy_string += to_append
                        labelled_bracketless_hierarchy_labels += (
                            f"{len(to_append) * next_label}"
                        )
                        labelled_dim_string += (
                            f" {len(particle_labels) * 'n'}{len(to_append) * 'n'}"
                        )
                    else:
                        labelled_dim_string += f" {len(particle_labels) * 'd'}"

    labelled_bracketless_hierarchy_string = labelled_bracketless_hierarchy_string[1:]
    labelled_bracketless_hierarchy_labels = labelled_bracketless_hierarchy_labels[1:]
    labelled_dim_string = labelled_dim_string[1:]

    bracketless_hierarchy_string = labelled_bracketless_hierarchy_string
    bracketless_hierarchy_labels = labelled_bracketless_hierarchy_labels

    max_label = max(bracketless_hierarchy_labels)

    colours = [
        "spring_green3",
        "cornflower_blue",
        "red3",
        "yellow2",
        "hot_pink",
        "pale_turquoise1",
    ]

    for counts, index in enumerate(string.ascii_lowercase):
        if counts % 2 == 0:
            myGlobals.console.print("")

        colour = colours[int(counts / 2.0)]

        # Create a new string of the same length as bracketless_hierarchy_string filled with spaces
        output_line = [" "] * len(bracketless_hierarchy_string)

        # Populate the output_line with characters from bracketless_hierarchy_string where the label matches the current index
        for i, (char, label, dim_string) in enumerate(
            zip(
                bracketless_hierarchy_string,
                bracketless_hierarchy_labels,
                labelled_dim_string,
            )
        ):
            if label == index:
                if dim_string == "d":
                    output_line[i] = f"[dim]{char}[/dim]"
                else:
                    if char == "[":
                        output_line[i] = r"\["
                    else:
                        output_line[i] = char

        line = "".join(output_line)
        myGlobals.console.print(f"[{colour}]{line}")
        myGlobals.my_decay_splash.append(f"[{colour}]{line}")

        if index == max_label:
            break

    myGlobals.console.print("")


def error_splash(stderr=None, pre_message="", post_message=""):
    print("\n\n")
    print(colored("++" * 50, "red"))
    if pre_message != "":
        print(f"ERROR {pre_message}\n")
    if stderr:
        if Path(stderr).is_file():
            f = open(stderr, "r")
            f_lines = f.readlines()
            for idx, line in enumerate(f_lines):
                line = line.replace("\n", "")
                print(colored(f"\t{line}", "red"))
    if post_message != "":
        print("\nERROR message:", colored(f"{post_message}", "red"))

    raise RuntimeError()


@contextmanager
def log_execution(message: str):
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [dim] \t[deep_pink3]{message}...[deep_pink3]"
    )
    yield  # Allow the block of code to execute
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [dim] \t[bold cyan][i]complete[/i][/bold cyan]"
    )


def info_print(message: str):
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [dim] \t[grey39]{message}...[grey39]"
    )


def warning_print(message: str):
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [dim] \t[red3]{message}...[red3]"
    )


@contextmanager
def status_execution(status_message: str, complete_message: str):
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] {status_message.replace('[bold green]', '[bold slate_blue3]')}"
    )
    with myGlobals.console.status(
        f"{status_message.replace('[bold green]', '[bold slate_blue3]')}",
        spinner="material",
    ):
        yield  # Allow the block of code to execute
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] \t{complete_message}"
    )


@contextmanager
def status_execution_rapidsim(status_message: str, complete_message: str):
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] {status_message.replace('[bold green]', '[bold slate_blue3]')}"
    )
    with myGlobals.console.status(
        f"{status_message.replace('[bold green]', '[bold slate_blue3]')}",
        spinner="material",
    ) as status:
        yield status  # Pass the status object into the block

    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] \t{complete_message}"
    )


def events_table(events, tuple_loc):
    file = uproot.open(f"{tuple_loc}:DecayTree")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Requested", justify="right", width=20)
    table.add_column("Returned", justify="right", width=20)
    table.add_column("Efficiency", justify="right", width=20)

    table.add_row(
        f"{events}",
        f"{file.num_entries}",
        f"{file.num_entries / events:.3f}",
    )

    myGlobals.console.print(table)


def print_file_info(file_path, time=None):
    # Get the file size in bytes
    size_bytes = os.path.getsize(file_path)

    file = uproot.open(f"{file_path}:DecayTree")

    # List of size units
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0

    # Convert to the appropriate unit
    while size_bytes >= 1024 and unit_index < len(units) - 1:
        size_bytes /= 1024
        unit_index += 1

    # Print the file size with appropriate unit
    # print(f"File size: {size_bytes:.2f} {units[unit_index]}")
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [sea_green1] Output file: [bold] {file_path} [bold] [sea_green1]"
    )
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [sea_green1] [dim] \tsize: {size_bytes:.2f} {units[unit_index]} [sea_green1]"
    )
    myGlobals.console.print(
        f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [sea_green1] [dim] \tentries: {file.num_entries} [sea_green1]"
    )
    if time:
        myGlobals.console.print(
            f"[grey39][{datetime.now().strftime('%H:%M:%S')}][grey39] [sea_green1] [dim] \tentries/min: {file.num_entries / (time / 60.0):.1f} [sea_green1]"
        )


def timings_table(only_rapidsim=False, only_vertexing=False):
    total_time = myGlobals.stopwatches.read_sum()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column(" ", style="bold", width=12)
    table.add_column("Configuration", justify="right", width=20)
    table.add_column("Generation", justify="right", width=20)
    table.add_column("Processing", justify="right", width=20)
    table.add_column("Total", justify="right", width=20)
    if not only_vertexing:
        table.add_row(
            "RapidSim",
            f"{myGlobals.stopwatches.read('RapidSim - config'):.2f}s ({myGlobals.stopwatches.read('RapidSim - config') / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('RapidSim - generation'):.2f}s ({myGlobals.stopwatches.read('RapidSim - generation') / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('RapidSim - processing'):.2f}s ({myGlobals.stopwatches.read('RapidSim - processing') / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('RapidSim - config') + myGlobals.stopwatches.read('RapidSim - generation') + myGlobals.stopwatches.read('RapidSim - processing'):.2f}s ({(myGlobals.stopwatches.read('RapidSim - config') + myGlobals.stopwatches.read('RapidSim - generation') + myGlobals.stopwatches.read('RapidSim - processing')) / total_time * 100.0:.2f} %)",
        )
    if not only_rapidsim:
        table.add_row(
            "Vertexing",
            f"{myGlobals.stopwatches.read('Networks - config'):.2f}s ({myGlobals.stopwatches.read('Networks - config') / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('Networks - generation'):.2f}s ({myGlobals.stopwatches.read('Networks - generation') / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('Networks - processing'):.2f}s ({myGlobals.stopwatches.read('Networks - processing') / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('Networks - config') + myGlobals.stopwatches.read('Networks - generation') + myGlobals.stopwatches.read('Networks - processing'):.2f}s ({(myGlobals.stopwatches.read('Networks - config') + myGlobals.stopwatches.read('Networks - generation') + myGlobals.stopwatches.read('Networks - processing')) / total_time * 100.0:.2f} %)",
        )
    if not only_vertexing and not only_rapidsim:
        table.add_row("", "", "")  # This will act as a horizontal line
        table.add_row(
            "Total",
            f"{myGlobals.stopwatches.read('RapidSim - config') + myGlobals.stopwatches.read('Networks - config'):.2f}s ({(myGlobals.stopwatches.read('RapidSim - config') + myGlobals.stopwatches.read('Networks - config')) / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('RapidSim - generation') + myGlobals.stopwatches.read('Networks - generation'):.2f}s ({(myGlobals.stopwatches.read('RapidSim - generation') + myGlobals.stopwatches.read('Networks - generation')) / total_time * 100.0:.2f} %)",
            f"{myGlobals.stopwatches.read('RapidSim - processing') + myGlobals.stopwatches.read('Networks - processing'):.2f}s ({(myGlobals.stopwatches.read('RapidSim - processing') + myGlobals.stopwatches.read('Networks - processing')) / total_time * 100.0:.2f} %)",
            f"{total_time:.2f}s",
        )

    myGlobals.console.print(table)
    return total_time
