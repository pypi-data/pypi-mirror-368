# SPDX-License-Identifier: LGPL-3.0-or-later

# Cerbose
# made by jasperredis
# A simple Python library for making colourful, tagged terminal output, along with additional console features.
# Version 1.0.1
# LICENSE: LGPL v3 (View in LICENSE-LGPL file in library root or at <https://www.gnu.org/licenses/lgpl-3.0.html>)
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# This library is distributed WITHOUT ANY WARRANTY; without even
# the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library. If not, see <https://www.gnu.org/licenses/>.

__version__ = "1.0"
__author__ = "jasperredis <https://www.jris.straw.page>"
__license__ = "GNU Lesser General Public License v3 or later"
__description__ = "Cerbose: A simple library for colourful, tagged console output (plus additional features)"

# Imports
import os
import json
import datetime as dt

# Setup
try:
    from colorama import Fore, Style, init
except ImportError:
    INTERNAL_iprint("error", "cerbose could not import colorama.")
    exit(1)
init(autoreset=True)

# * INTERNAL FUNCTIONS
# These were previously part of seperate modules. When modularity issues arised, I decided to move them into the main script.

INTERNAL_SUBSITUTE = {
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
    "lightblack": Fore.LIGHTBLACK_EX,
    "lightred": Fore.LIGHTRED_EX,
    "lightgreen": Fore.LIGHTGREEN_EX,
    "lightyellow": Fore.LIGHTYELLOW_EX,
    "lightblue": Fore.LIGHTBLUE_EX,
    "lightmagenta": Fore.LIGHTMAGENTA_EX,
    "lightcyan": Fore.LIGHTCYAN_EX,
    "lightwhite": Fore.LIGHTWHITE_EX,
    "normal": Fore.RESET,
}


def INTERNAL_get_type_data_item(item, config):
    try:
        return {
            "label": config["tags"]["text"][item],
            "colour": SUBSITUTE[config["tags"]["colours"][item]],
        }
    except Exception as e:
        INTERNAL_iprint("error", f"CERBOSE: {e}")


def INTERNAL_config_is_valid(config):
    MAIN_KEYS = ["tags", "cerbar", "space-repeat-tolerance", "timeformat"]
    TAGS_KEYS = ["colours", "text", "symbols"]
    COAT_KEYS = ["none"]  # coat = COlours And Text
    TAG_SYMBOL_KEYS = ["bracket left", "bracket right", "text divisor"]
    CERBAR_KEYS = ["bracket left", "bracket right", "fill symbol", "empty symbol"]
    for item in MAIN_KEYS:
        if item not in config:
            INTERNAL_iprint(
                "error",
                f"defconf: configIsValid: Invalid configuration was passed. Missing key: {item}",
            )
            return False
    for item in TAGS_KEYS:
        if item not in config["tags"]:
            INTERNAL_iprint(
                "error",
                f"defconf: configIsValid: Invalid configuration was passed. Missing key: {item}",
            )
            return False
    for item in COAT_KEYS:
        if item not in config["tags"]["colours"] or item not in config["tags"]["text"]:
            INTERNAL_iprint(
                "error",
                f"defconf: configIsValid: Invalid configuration was passed. Missing key: {item}",
            )
            return False
    for item in TAG_SYMBOL_KEYS:
        if item not in config["tags"]["symbols"]:
            INTERNAL_iprint(
                "error",
                f"defconf: configIsValid: Invalid configuration was passed. Missing key: {item}",
            )
            return False
    for item in CERBAR_KEYS:
        if item not in config["cerbar"]:
            INTERNAL_iprint(
                "error",
                f"defconf: configIsValid: Invalid configuration was passed. Missing key: {item}",
            )
            return False
    return True


def INTERNAL_get_cin(options, cprint, lower):
    gotans = False
    while not gotans:
        ans = input("> ")
        if lower:
            ans = ans.lower()
        if options != "any" and ans not in options:
            INTERNAL_iprint("error", f"cin: getCin: '{ans}' is not a valid option!")
        else:
            gotans = True
    return ans


def INTERNAL_iprint(type, text):
    global TYPES
    ogconf = TYPES
    nconf = {
        "meta": {"program": "Cerbose Default", "author": "jasperredis"},
        "tags": {
            "colours": {
                "none": "white",
                "error": "red",
                "warn": "yellow",
                "info": "cyan",
            },
            "text": {"none": "NONE", "error": "ERROR", "warn": "WARN", "info": "INFO"},
            "symbols": {"bracket left": "[", "bracket right": "]", "text divisor": ":"},
        },
        "cerbar": {
            "bracket left": "[",
            "bracket right": "]",
            "fill symbol": "#",
            "empty symbol": "-",
        },
        "space-repeat-tolerance": 5,
        "timeformat": "%H:%M:%S",
    }
    defconf("i", nconf)
    cprint(type, text)
    defconf("i", ogconf)


# * END INTERNAL FUNCTIONS

# Different types
TYPES = {
    "meta": {"program": "Cerbose", "author": "jasperredis"},
    "tags": {
        "colours": {
            "none": "white",
            "ok": "green",
            "note": "cyan",
            "warn": "yellow",
            "error": "red",
            "debug": "magenta",
            "info": "cyan",
            "input": "lightblue",
            "load": "red",
            "pause": "yellow",
            "stat": "magenta",
            "fatal": "red",
            "trace": "magenta",
            "proc": "magenta",
        },
        "text": {
            "none": "NONE",
            "ok": "OK",
            "note": "NOTE",
            "warn": "WARN",
            "error": "ERROR",
            "debug": "DEBUG",
            "info": "INFO",
            "input": "INPUT",
            "load": "LOAD",
            "pause": "PAUSE",
            "stat": "STAT",
            "fatal": "FATAL",
            "trace": "TRACE",
            "proc": "PROC",
        },
        "symbols": {"bracket left": "[", "bracket right": "]", "text divisor": ":"},
    },
    "cerbar": {
        "bracket left": "[",
        "bracket right": "]",
        "fill symbol": "#",
        "empty symbol": "-",
    },
    "space-repeat-tolerance": 5,
    "timeformat": "%H:%M:%S",
}
align = 0  # required amount of characters to meet spacing
spacerepeatcount = 0  # the amount of times align has gone unchanged


def cprint(
    type,
    text,
    *,
    logfile=None,
    logfeedback=False,
    textcol="normal",
    stagtype=None,
    timestamp=False,
    valonly=False,
):
    """
    Print a coloured, tagged message.

    Parameters:
        type (str): The tag to use (e.g. 'none', 'ok', 'note', 'warn', 'error', 'debug', 'info', 'input', 'load', 'pause', 'stat', 'fatal', 'trace').
            + Use '' for no type but still align spacing with other tags.
        text (str): The message to print.

    Keyword Arguments:
        logfile (str): Specifies a file for logging. Leave empty if you do not want logging.
        logfeedback (bool): Outputs whenever a log is written if True.
            + Requires logfile to have a value.
            + Is NOT required if logfile has a value.
        textcol: Sets a colour for text. Check documentation or README for valid colours.
        stagtype (str): Adds a second tag behind the main tag. Set to any valid type.
        timestamp (bool): Adds a timestamp behind the second (if exists) and main tags.
            + Timestamp format can be customized and uses that of the datetime module. Check its documentation or the README/docs.
        valonly (bool): Returns the output as a string instead of printing it to the console. INCLUDES COLOURS!
    """
    global align, spacerepeatcount
    symbols = TYPES["tags"]["symbols"]
    if type == "":  # Blank
        backer = " " * (align)
        backer += f"{symbols['text divisor']} "
    else:  # Anything not blank
        tagcol = TYPES["tags"]["colours"].get(
            type, TYPES["tags"]["colours"]["none"]
        )  # Fallback to NONE
        tagtxt = TYPES["tags"]["text"].get(
            type, TYPES["tags"]["text"]["none"]
        )  # Fallback to NONE
        labellength = 0
        # Add timestamp
        if timestamp:
            date = dt.datetime.now()
            timeoutput = date.strftime(TYPES["timeformat"])
            timeoutput = (
                f"{symbols['bracket left']}{timeoutput}{symbols['bracket right']}"
            )
            labellength += len(timeoutput)
        # Add stagtype
        if stagtype != None:
            stagcol = TYPES["tags"]["colours"].get(
                stagtype, TYPES["tags"]["colours"]["none"]
            )  # Fallback to NONE
            stagtxt = TYPES["tags"]["text"].get(
                stagtype, TYPES["tags"]["text"]["none"]
            )  # Fallback to NONE
            labellength += len(
                f"{symbols['bracket left']}{stagtxt}{symbols['bracket right']}"
            )
        labellength += len(
            f"{symbols['bracket left']}{tagtxt}{symbols['bracket right']}{symbols['text divisor']}"
        )
        # Do alignment
        if labellength > align:
            align = labellength
            spacerepeatcount = 0
        else:
            spacerepeatcount += 1
            if (
                spacerepeatcount >= TYPES["space-repeat-tolerance"]
                and align > labellength
            ):
                align = labellength
                spacerepeatcount = 0
        # Make padding
        padlen = align - labellength
        pad = " " * padlen
        # Make final output
        backer = ""
        if timestamp:
            backer += timeoutput
        if stagtype != None:
            backer += f"{symbols['bracket left']}{INTERNAL_SUBSITUTE[stagcol]}{stagtxt}{Style.RESET_ALL}{symbols['bracket right']}"
        backer += f"{symbols['bracket left']}{INTERNAL_SUBSITUTE[tagcol]}{tagtxt}{Style.RESET_ALL}{symbols['bracket right']}{pad}{symbols['text divisor']} "
    # Colour text
    if textcol in INTERNAL_SUBSITUTE:
        ctext = INTERNAL_SUBSITUTE[textcol] + text
    else:
        ctext = Fore.RESET + text  # Fixed in 1.0.1!
        INTERNAL_iprint(
            "warn", "CERBOSE: cprint: Provided texcol colour is not a valid colour."
        )
    # Make output
    if valonly:
        return backer + text
    else:
        print(backer + ctext)
    # Log
    if logfile is not None:
        try:
            with open(logfile, "a") as f:
                writecont = ""
                if timestamp:
                    writecont += timeoutput
                if stagtype != None:
                    writecont += (
                        f"{symbols['bracket left']}{stagtxt}{symbols['bracket right']}"
                    )
                writecont += f"{symbols['bracket left']}{tagtxt}{symbols['bracket right']}{symbols['text divisor']} "
                writecont += text + "\n"
                f.write(writecont)
                if logfeedback:
                    INTERNAL_iprint("info", "Logged last message.")
        except Exception as e:
            INTERNAL_iprint("error", f"cprint (logging): Unknown error: {e}")


def mprint(
    type,
    text,
    *,
    logfile=None,
    logfeedback=False,
    textcol="normal",
    stagtype=None,
    timestamp=False,
    valonly=False,
):
    global align
    symbols = TYPES["tags"]["symbols"]
    text = text.split("\n")
    tagtxt = TYPES["tags"]["text"].get(
        type, TYPES["tags"]["text"]["none"]
    )  # Fallback to NONE
    labellength = 0
    # Same as cprint
    if timestamp:  # Add timestamp
        date = dt.datetime.now()
        timeoutput = date.strftime(TYPES["timeformat"])
        timeoutput = f"{symbols['bracket left']}{timeoutput}{symbols['bracket right']}"
        labellength += len(timeoutput)
    # Add stagtype
    if stagtype != None:
        stagtxt = TYPES["tags"]["text"].get(
            stagtype, TYPES["tags"]["text"]["none"]
        )  # Fallback to NONE
        labellength += len(
            f"{symbols['bracket left']}{stagtxt}{symbols['bracket right']}"
        )
    labellength += len(
        f"{symbols['bracket left']}{tagtxt}{symbols['bracket right']}{symbols['text divisor']}"
    )
    labellength -= 1
    padlen = " " * labellength
    text = f"\n{padlen}{symbols['text divisor']} ".join(text)
    cprint(
        type,
        text,
        logfile=logfile,
        logfeedback=logfeedback,
        textcol=textcol,
        stagtype=stagtype,
        timestamp=timestamp,
        valonly=valonly,
    )


def cin(
    type,
    text,
    options,
    *,
    log=False,
    logfile=None,
    logfeedback=False,
    textcol="normal",
    stagtype=None,
    timestamp=False,
    lower=False,
    showop=False,
):
    """
    Takes user input after asking something.

    Parameters:
        type (str): Same as cprint. This goes to the prompt asked.
        text (str): Same as cprint. This goes to the prompt asked.
        options (list/str): The allowed options for opt mode. In text mode, this can be set to 'any' for any input to be permitted.

    Keyword Arguments:
        log (bool): Same as cprint. This goes to the prompt asked.
        logfile (str): Same as cprint. This goes to the prompt asked.
        logfeedback (bool): Same as cprint. This goes to the prompt asked.
        textcol (str): Same as cprint. This goes to the prompt asked.
        stagtype (str): Same as cprint. This goes to the prompt asked.
        timestamp (bool): Same as cprint. This goes to the prompt asked.
        lower (bool): Ignores capitalization in user input and assumes it was all lowercase. Do not use this if you have capitalized options!
        showop (bool): If True, shows all availble options (if there is a strict set, this will not show if options='any'.)
    """
    printext = f"{text}"
    if showop and options != "any":  # Print options (really just get them in memory)
        count = 0
        for item in options:
            count += 1
            printext += f"\n{count}) {item}"
    mprint(
        type,
        printext,
        logfile=logfile,
        logfeedback=logfeedback,
        textcol=textcol,
        stagtype=stagtype,
        timestamp=timestamp,
    )  # Actually print options
    return INTERNAL_get_cin(options, cprint, lower)  # Function for simplicity sake


def cerbar(length, total, fill, *, perc=None, count=None):
    """
    Output an ASCII progress bar (with formatting).
    The borders of the bar are squared brackets ([]).
    The filling of the bar is hashtags (#).
    This outputs a formatted string.

    Parameters:
        length (int): How long (in characters) the bar should be.
        total (int): The total value the bar represents.
        fill (int): The amount of items of the total that are filled in.

    Keyword Arguments:
        addperc (bool): Adds a percentage number before or after the bar if True.
            + Requires percpos to have a value.
        percpos (str): Can be 'l' (left) or 'r' (right). Determines where the percentage (if added) is displayed.
        addcount (bool): Adds a counter (fill/total) before or after the bar if True.
            + Requires countpos to have a value.
        countpos (str): Can be 'l' (left) or 'r' (right). Determines where the counter (if added) is displayed.

    Example:
    >>> cerbar(10, 100, 50)
    '[#####-----]'
    """
    symbols = TYPES["cerbar"]
    item = total / length
    fillcnt = fill / item
    filled_chars = round(fillcnt)
    filltxt = symbols["fill symbol"] * filled_chars
    remaincnt = length - filled_chars
    remaintxt = symbols["empty symbol"] * remaincnt

    # Get percentage (if needed)
    perce = None
    if perc is not None:
        perce = (fill / total) * 100
        perce = round(perce, 3)

    # Form output
    OP = ""  # OutPut
    # Add left statistics
    if perc == "l":
        OP += f"{perce:.1f}% "
    if count == "l":
        OP += f"({fill}/{total}) "
    # Add bar
    OP += f"{symbols['bracket left']}{filltxt}{remaintxt}{symbols['bracket right']}"
    # Add right statistics
    if perc == "r":
        OP += f" {perce:.1f}%"
    if count == "r":
        OP += f" ({fill}/{total})"
    return OP


def defconf(type, content):
    """
    Apply a configuration to the Cerbose instance.
    A configuration determines which symbols to use for borders and additional features, what colours to apply in tags, what text appears in tags, and space repeat tolerance (more in README or docs).
    If this function is not used, the default configuration is applied (which is highly recommended).
    This function accepts either a large dictionary (e.g., parsed from JSON) or a file path to load the configuration from.

    Parameters:
        type (str): Determines the source of the configuration.
            Use "i" or "input" to provide the configuration as a variable or text input.
            Use "f" or "file" to provide a file path (which will be expanded with os.path.expanduser()).
        content (str or dict): The configuration data to apply.
            If using "f"/"file" for `type`, this should be a file path.
            If using "i"/"input", this should be a dictionary or raw JSON string.

    Note:
        Using this function is optional. The default configuration works extremely well and is highly recommended.
        See the docs or README for more information about configuration files.
    """
    if type == "f" or type == "file":  # Handle files
        if not os.path.exists(os.path.expanduser(content)):  # Check existence
            INTERNAL_iprint("error", f"defconf: File '{content}' does not exist.")
            return None
        try:
            with open(content, "r") as f:  # Read
                global CERBOSE_CONFIG
                CERBOSE_CONFIG = json.load(f)
        except json.JSONDecodeError as e:  # Error handling
            INTERNAL_iprint("error", f"defconf: Could not parse JSON: {e}")
            return None
        except Exception as e:
            INTERNAL_iprint("error", f"defconf: Unknown error: {e}")
            return None
    elif type == "i" or type == "input":  # Handle non-files
        if isinstance(content, str):  # Strings
            try:
                CERBOSE_CONFIG = json.loads(content)
            except json.JSONDecodeError as e:
                INTERNAL_iprint("error", f"defconf: Could not parse JSON: {e}")
                return None
        elif isinstance(content, dict):  # Dicts
            CERBOSE_CONFIG = content
        else:
            INTERNAL_iprint(
                "error",
                f"defconf: Using input mode but inputted config is not a string or dict.",
            )
            return None
    if not INTERNAL_config_is_valid(CERBOSE_CONFIG):  # Verify all keys are present
        INTERNAL_iprint("error", f"defconf: Config validity check failed.")
        return None
    # Set config
    global TYPES
    TYPES = CERBOSE_CONFIG


def resetalign():
    """
    Resets all alignment-based variables. (align, spacerepeatcount, and labellength)
    This function has no parameters.
    """
    global align, spacerepeatcount, labellength
    align = 0
    spacerepeatcount = 0
    labellength = 0
