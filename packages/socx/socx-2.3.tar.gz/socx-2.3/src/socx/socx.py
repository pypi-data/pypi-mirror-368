#!/usr/bin/env python3

from contextlib import suppress
import subprocess
from unittest import skipUnless
from urllib.parse import unquote

try:
    import argparse
    import os
    import time
    import re
    import socket
    import hashlib
    import requests
    import sqlite3 as sql
    import pandas as pd
    import keyring
    import xml.etree.ElementTree as ET
    from pathlib import Path

    try:
        from . import util
    except:
        import util
except ImportError as e:
    print(
        f"""You are missing a required module ({e.name})
Try installing it with:
    pip install {e.name}
or
    python -m pip install {e.name} --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org"""
    )
    exit(1)


###########################
# Constants and Variables #
###########################.

PROGRAM_NAME = "socx"
# Also change this in pyproject.toml
VERSION = "2.1.1"
ABOUT = f"""
   _____ ____  _______  __
  / ___// __ \/ ____/ |/ /
  \__ \/ / / / /    |   / 
 ___/ / /_/ / /___ /   |  
/____/\____/\____//_/|_|  

Version: {VERSION}
A tool to assist with day to day activites in a security operations center (pronounced "socks")

Visit https://enlace.one/ for more information.
"""
USAGE = f"""Usage:
    {PROGRAM_NAME} [universal options] [function] [arguments]
    python {PROGRAM_NAME}.py [universal options] [function] [arguments]
        
Examples:
    {PROGRAM_NAME} --help
    {PROGRAM_NAME} info -h
    {PROGRAM_NAME} info -ip 1.2.3.4
    {PROGRAM_NAME} -v 3 info -d google.com
    {PROGRAM_NAME} find -f filename.txt -i
    {PROGRAM_NAME} find -f fold.*name -r
    {PROGRAM_NAME} unwrap --url "https://urldefense.com/v3/__https:/..."
    {PROGRAM_NAME} combine --csvs 5
    {PROGRAM_NAME} awake --minutes 90
    {PROGRAM_NAME} awake --restart
"""
verbosity = 1
environmental_variables = {
    "InsightVMAPI_BASE_URL": "",
    "InsightVMAPI_KEY": "",
    "VirusTotalAPI_KEY": "",
}

# ----------------#
# Util Functions #
# ----------------#


def p(*args_, v=1, end="\n", sep=" ", file=None):
    if verbosity >= v:
        print(*args_, end=end, sep=sep, file=file)


def unwrap_url(url):
    pp_decoder = util.URLDefenseDecoder()
    if "safelinks" in url:
        url = unquote(url.split("url=")[1])
    url = pp_decoder.decode(url)
    return url


def search(pattern, string, case_insensitive):
    if case_insensitive:
        return re.search(pattern, string, re.IGNORECASE)
    else:
        return re.search(pattern, string)


def find_file(
    filename,
    directory=os.getcwd(),
    is_regex=False,
    case_insensitive=True,
    find_all=False,
):
    files_found = []
    filename_copy = filename
    p(f"Starting file search in {directory}", v=5)
    if case_insensitive and not is_regex:
        filename = filename.lower()
    for root, dirs, files in os.walk(directory):
        if is_regex:
            r_files = [
                os.path.join(root, file)
                for file in files + dirs
                if search(filename, file, case_insensitive)
            ]
            if find_all:
                files_found.extend(r_files)
            elif len(r_files) > 0:
                return r_files[0]
        else:
            if case_insensitive:
                files = [file.lower() for file in files]
                dirs = [dir.lower() for dir in dirs]
            if filename in files or filename in dirs:
                if find_all:
                    files_found.append(os.path.join(root, filename_copy))
                else:
                    return os.path.join(root, filename_copy)
    if find_all:
        return files_found
    else:
        return None


def print_ip_info(ip):
    url = f"https://whois.arin.net/rest/ip/{ip}"
    ip_xml = requests.request("GET", url=url).text
    namespaces = {"ns": "https://www.arin.net/whoisrws/core/v1"}
    organization_url = ET.fromstring(ip_xml).find("ns:orgRef", namespaces).text
    org_xml = requests.request("GET", url=organization_url).text
    root = ET.fromstring(org_xml)
    org_name = root.find("ns:name", namespaces).text
    org_city = root.find("ns:city", namespaces).text
    org_country = root.find("ns:iso3166-1/ns:name", namespaces).text
    org_handle = root.find("ns:handle", namespaces).text
    registration_date = root.find("ns:registrationDate", namespaces).text
    print(f"(whois) Organization: {org_name}")
    print(f"(whois) Country: {org_country}")
    print(f"(whois) City: {org_city}")
    print(f"(whois) Handle: {org_handle}")
    print(f"(whois) Registration Date: {registration_date}")


def get_enironmental_variable(name):
    value = keyring.get_password("system", "_socX__" + name)
    if value is None:
        value = environmental_variables[name]
    return value


#####################
# Primary Functions #
#####################.


def do_config():
    while True:
        p("Settings, keys, variables", v=1)
        for index, var in enumerate(environmental_variables.keys()):
            print(f"\t{index} - {var}")
        index = input(
            "Enter the index of the variable you want to edit (Nothing to stop): "
        )
        if index == "":
            break
        else:
            index = int(index)
        p(f"Editing '{list(environmental_variables.keys())[index]}'", v=1)
        old_value = get_enironmental_variable(
            list(environmental_variables.keys())[index]
        )
        print(f"Old value:'{old_value}'")
        new_value = input("New value (Nothing to cancel): ")
        if new_value == "":
            continue
        print("_socX__" + list(environmental_variables.keys())[index])
        keyring.set_password(
            "system",
            "_socX__" + list(environmental_variables.keys())[index],
            new_value,
        )
        p("Value updated\n", v=1)


def do_ip_info(ip):
    p(f"Getting information on {ip}", v=1)
    try:
        hostname = socket.gethostbyaddr(ip)
        print(f"Hostname: {hostname}")
    except Exception as e:
        p(f"Hostname: Error - {e}", v=1)
    ping_response = os.system(f"ping -n 1 {ip} > nul")
    if ping_response == 0:
        print(f"Ping: {ip} is up")
    else:
        print(f"Ping: {ip} is down")
    print_ip_info(ip)
    if (
        get_enironmental_variable("InsightVMAPI_BASE_URL") != ""
        and get_enironmental_variable("InsightVMAPI_KEY") != ""
    ):
        ivm = util.InsightVM(
            get_enironmental_variable("InsightVMAPI_BASE_URL"),
            get_enironmental_variable("InsightVMAPI_KEY"),
        )
        for asset in ivm.ip_search(ip):
            print(ivm._format_return_string(asset))


def do_domain_info(domain):
    if domain.startswith("http"):
        domain = domain.split("//")[1]
    if domain.startswith("www."):
        domain = domain.split("www.")[1]
    p(f"Getting information on {domain}", v=1)
    try:
        ip = socket.gethostbyname(domain)
        print(f"IP: {ip}")
    except Exception as e:
        p(f"IP: Error - {e}", v=1)
    ping_response = os.system(f"ping -n 1 {domain} > nul")
    if ping_response == 0:
        print(f"Ping: {domain} is up")
    else:
        print(f"Ping: {domain} is down")
    print_ip_info(ip)
    print(f"Whois record: https://www.whois.com/whois/{domain}")


def do_url_info(url):
    url = unwrap_url(url)
    vt_api_key = get_enironmental_variable("VirusTotalAPI_KEY")
    vt_report_url = ""
    if vt_api_key != "":
        response = requests.request(
            "POST",
            url="https://www.virustotal.com/api/v3/urls",
            headers={"x-apikey": vt_api_key},
            data={"url": url},
        )
        vt_report_url = response.json()["data"]["links"]["self"]
    p(f"Getting information on {url} (unwrapped)", v=1)
    if vt_api_key != "":
        p("Waiting for Virustotal to process..", v=3)
        for seconds in [5, 7, 10, 15]:
            time.sleep(seconds)
            report_response = requests.request(
                "GET", url=vt_report_url, headers={"x-apikey": vt_api_key}
            ).json()
            if report_response["data"]["attributes"]["status"] != "queued":
                print("Virustotal:", report_response["data"]["links"]["item"])
                print(
                    "Virustotal:",
                    report_response["data"]["attributes"]["stats"],
                )
                p("P.S. Run again if stats are incomplete now.", v=3)
                break


def do_info(**kwargs):
    if "ip" in kwargs:
        return do_ip_info(kwargs["ip"])
    elif "domain" in kwargs:
        return do_domain_info(kwargs["domain"])
    elif "url" in kwargs:
        return do_url_info(kwargs["url"])
    else:
        print("Error: you must provide a valid argument")


def do_filename_search(
    filename,
    directory=os.getcwd(),
    find_all=False,
    is_regex=False,
    case_sensitive=False,
    skip_smart=False,
):

    case_insensitive = not case_sensitive

    p(f"Searching for {filename}", v=1)
    if case_insensitive:
        p("Performing case insensitive search", v=3)
    if find_all:
        p("Finding all occurances", v=3)
    if find_all:
        result = find_file(
            filename,
            directory="C:\\",
            is_regex=is_regex,
            find_all=find_all,
            case_insensitive=case_insensitive,
        )
        result += find_file(
            filename,
            directory="D:\\",
            is_regex=is_regex,
            find_all=find_all,
            case_insensitive=case_insensitive,
        )
        result = set(result)
        if len(result) == 0:
            print("File/Folder not found")
        else:
            for file in result:
                print(f"File/Folder found at {file}")
    elif not skip_smart:
        for path in dict.fromkeys(
            [
                directory,
                os.path.dirname(os.path.dirname(directory)),
                os.path.expanduser("~"),
                "C:\\",
                "D:\\",
            ]
        ):
            p(f"Checking {path}..", v=3)
            result = find_file(
                filename,
                directory=path,
                is_regex=is_regex,
                case_insensitive=case_insensitive,
            )
            if result is None:
                p(f"File not found in {path}..", v=2)
            else:
                break
        if result is None:
            print("File/Folder not found")
        else:
            print(f"File/Folder found at {result}")
    else:
        result = find_file(
            filename,
            directory=directory,
            is_regex=is_regex,
            case_insensitive=case_insensitive,
        )
        if result is None:
            print("File/Folder not found")
        else:
            print(f"File/Folder found at {result}")


def do_url_unwrap(url):
    p("Unwrapping URL\n", v=3)
    print(f"Unwrapped URL:\n{unwrap_url(url)}")
    p("\n", v=3)


def do_browser_history(user="~"):
    p("Gathering browser history. Will output to cwd", v=3)
    p(
        "You may want to close the browser before running this, otherwise you may get 'database is locked' errors",
        v=5,
    )
    browser_history_paths = [
        {
            "path": "/AppData/Local/Google/Chrome/User Data/Default/",
            "browser": "Chrome",
            "databases": [
                "History",
                "Cookies",
                "Vistied Links",
                "Web Data",
                "Shortcuts",
                "Top Sites",
                "Favicons",
                "Network Action Predictor",
            ],
        },
        {
            "browser": "Brave",
            "path": "/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/",
            "databases": [
                "History",
                "Cookies",
                "Vistied Links",
                "Web Data",
                "Shortcuts",
                "Top Sites",
                "Favicons",
                "Network Action Predictor",
            ],
        },
        {
            "browser": "FireFox",
            "path": "/AppData/Roaming/Mozilla/Firefox/Profiles/",
            "databases": [
                "formhistory.sqlite",
                "favicons.sqlite",
                "places.sqlite",
                "cookies.sqlite",
            ],
        },
        {
            "browser": "Edge",
            "path": "/AppData/Local/Microsoft/Edge/User Data/Default/",
            "databases": [
                "History",
                "Visited Links",
                "Shortcuts",
                "Top Sites",
                "Bookmarks",
            ],
        },
    ]
    for browser in browser_history_paths:
        folder = os.path.expanduser(user) + browser["path"]
        if os.path.exists(folder):
            p(f"Found {browser['browser']} at {folder}", v=5)
            os.makedirs(browser["browser"], exist_ok=True)
            for name in browser["databases"]:
                if os.path.exists(folder + name):
                    try:
                        p(f"Found {name} at {folder}", v=5)
                        con = sql.connect(folder + name)
                        cursor = con.cursor()
                        cursor.execute(
                            "SELECT name FROM sqlite_schema WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY 1;"
                        )
                        for i in cursor.fetchall():
                            table = i[0]
                            df = pd.read_sql(f"SELECT * FROM {table}", con)
                            df.to_csv(f"{browser['browser']}/{table}.csv")
                        con.close()
                    except Exception as e:
                        p(f"Error with {name} - {e}", v=3)


def do_combine_csvs(csvs=0, skip_og_filename_column=False, directory=os.getcwd()):
    p("Starting combine CSVs", v=5)
    p("The current directory will be used to find the CSVs.", v=1)
    paths = sorted(Path(directory).iterdir(), key=os.path.getmtime)
    paths.reverse()
    if csvs < 2:
        accum = 1
        p("File Paths", v=3)
        for path in paths:
            if str(path).endswith(".csv"):
                p(f"{accum} - {path}")
                accum += 1
        csvs = int(input("Enter the index of the last CSV to include:"))
    file_paths = []
    for path in paths:
        if str(path).endswith(".csv"):
            file_paths.append(str(path))
            p(f"Added {path}", v=4)
            csvs -= 1
            if csvs == 0:
                break
    dfs = []
    for path in file_paths:
        df = pd.read_csv(path)
        if not skip_og_filename_column:
            df["Original CSV Filename"] = os.path.basename(path)
        dfs.append(df)
    df = pd.concat(dfs)
    df.to_csv("COMBINED_FILE.csv", index=False)
    p("Outputed to COMBINED_FILE.csv", v=3)


def do_command_history(user="~"):
    p("Gathering command history. Will output to cwd.", v=3)
    cwd = os.getcwd()
    cmd_history_path = (
        os.path.expanduser(user)
        + "/AppData\\Roaming\\Microsoft\\Windows\\PowerShell\\PSReadLine\\ConsoleHost_history.txt"
    )
    with open(cmd_history_path, "r") as file:
        with open(cwd + "\\powershell_history.txt", "w") as output_file:
            for line in file:
                output_file.write(line)
    p("Command history gathered", v=3)


def awake(minutes=60, restart=False):
    interval = 10  # seconds
    iterations = (minutes * 60) / interval

    p(f"Keeping the device awake for {minutes} minutes...")
    cmd = [
        "powershell",
        "-Command",
        "$WShell = New-Object -ComObject 'WScript.Shell'; "
        f"for ($i = 0; $i -lt {iterations}; $i++) {{ "
        f"$WShell.SendKeys('%'); Start-Sleep -Seconds {interval}; $temp = [Math]::Round(($i*{interval})/60, 1); Write-Output \"$temp of {minutes}. CTRL+C to End\"}}",
    ]

    with subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
    ) as proc:
        for line in proc.stdout:
            print(line, end="")

    if restart:
        p("Restarting device...")
        cmd = ["shutdown", "/r", "/t", "0"]
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True
        )


#############
# Arguments #
#############.

FUNCTIONS = [
    {
        "name": "Edit SOCX Config",
        "command": "config",
        "help": "",
        "function": lambda: do_config(),
        "arguments": [],
    },
    {
        "name": "Interactive mode",
        "command": "interactive",
        "help": "",
        "function": lambda: interactive_mode(),
        "arguments": [],
    },
    {
        "name": "Stay Awake",
        "command": "awake",
        "help": "",
        "function": awake,
        "arguments": [
            {
                "name": "minutes",
                "flag": "--minutes",
                "short_flag": "-m",
                "prompt": "Enter number of minutes to run for: ",
                "type": int,
                "default": 60,
                "required": False,
                "help": "Keeps device awake for this many minutes",
            },
            {
                "name": "restart",
                "flag": "--restart",
                "short_flag": "-r",
                "type": bool,
                "action": "store_true",
                "default": False,
                "required": False,
                "help": "Restart computer once done keeping device awake",
            },
        ],
    },
    {
        "name": "Combine CSVs",
        "command": "combine",
        "help": "",
        "function": do_combine_csvs,
        "arguments": [
            {
                "name": "csvs",
                "flag": "--csvs",
                "short_flag": "-c",
                "prompt": "Enter number of CSVs to combine (1 for walkthrough): ",
                "type": int,
                "default": 0,
                "required": False,
                "help": "Combine the last X modified CSVs in the current directory. Enter 1 for walkthrough",
            },
            {
                "name": "directory",
                "flag": "--directory",
                "short_flag": "-d",
                "type": str,
                "default": os.getcwd(),
                "required": False,
                "help": "The directory to use, defaults to cwd",
            },
            {
                "name": "skip_og_filename_column",
                "flag": "--skip_og_filename_column",
                "short_flag": "-sname",
                "action": "store_true",
                "type": bool,
                "default": False,
                "required": False,
                "help": "Include a column with the OG file name",
            },
        ],
    },
    {
        "name": "Unwrap a URLDefense URL",
        "command": "unwrap",
        "help": "",
        "function": do_url_unwrap,
        "arguments": [
            {
                "name": "url",
                "flag": "--url",
                "short_flag": "-u",
                "prompt": "Enter the URL: ",
                "type": str,
                "required": True,
                "help": "A URL to unwrap (remove safelinks and protectlinks)",
            },
        ],
        "category": "unwrap",
    },
    {
        "name": "Get info on a URL, domain, or ip",
        "command": "info",
        "help": "",
        "function": do_info,
        "rules": {"require_one_of": ["url", "domain", "ip"]},
        "arguments": [
            {
                "name": "url",
                "flag": "--url",
                "short_flag": "-u",
                "prompt": "Enter the URL: ",
                "type": str,
                "required": False,
                "help": "A URL to get info on",
            },
            {
                "name": "domain",
                "flag": "--domain",
                "short_flag": "-d",
                "prompt": "Enter the domain: ",
                "type": str,
                "required": False,
                "help": "A domain (e.g., google.com)",
            },
            {
                "name": "ip",
                "flag": "--ip",
                "short_flag": "-ip",
                "prompt": "Enter the IP: ",
                "type": str,
                "required": False,
                "help": "An IP address",
            },
        ],
        "category": "info",
    },
    {
        "name": "Find a file",
        "command": "find",
        "help": "",
        "function": do_filename_search,
        "arguments": [
            {
                "name": "filename",
                "flag": "--filename",
                "short_flag": "-f",
                "prompt": "Enter the file's name: ",
                "type": str,
                "required": True,
                "help": "A file or folder name",
            },
            {
                "name": "is_regex",
                "flag": "--regex",
                "short_flag": "-r",
                "prompt": "Use regex pattern? (y/n): ",
                "type": bool,
                "action": "store_true",
                "default": False,
                "required": False,
                "help": "The query is a regex pattern",
            },
            {
                "name": "find_all",
                "flag": "--find_all",
                "short_flag": "-a",
                "prompt": "Find all occurrences? (y/n): ",
                "type": bool,
                "action": "store_true",
                "default": False,
                "required": False,
                "help": "Find all occurrences (default is find first)",
            },
            {
                "name": "case_sensitive",
                "flag": "--sensitive",
                "short_flag": "-i",
                "prompt": "Case sensitive search? (y/n): ",
                "type": bool,
                "action": "store_true",
                "default": False,
                "required": False,
                "help": "Search case insensitive (default is case sensitive)",
            },
            {
                "name": "directory",
                "flag": "--directory",
                "short_flag": "-d",
                "type": str,
                "default": os.getcwd(),
                "required": False,
                "help": "The directory to use, defaults to cwd",
            },
            {
                "name": "skip_smart",
                "flag": "--skip_smart",
                "short_flag": "-ss",
                "type": bool,
                "default": False,
                "action": "store_true",
                "required": False,
                "help": "Do smart search (try directory then user folder then C: then D:)",
            },
        ],
    },
    {
        "name": "Gather browser history",
        "command": "browser_history",
        "help": "",
        "function": do_browser_history,
        "arguments": [
            {
                "name": "user",
                "flag": "--user",
                "short_flag": "-U",
                "prompt": "Enter the user's name (~ for current): ",
                "type": str,
                "default": "~",
                "required": False,
                "help": "The user's name to use. Default is current user.",
            }
        ],
    },
    {
        "name": "Gather command history",
        "command": "cmd_history",
        "help": "",
        "function": do_command_history,
        "arguments": [
            {
                "name": "user",
                "flag": "--user",
                "short_flag": "-U",
                "prompt": "Enter the user's name (~ for current): ",
                "type": str,
                "default": "~",
                "required": False,
                "help": "The user's name to use. Default is current user.",
            }
        ],
    },
]

####################
# Interactive Mode #
####################.


def interactive_mode():
    # Get Function
    for index, func in enumerate(FUNCTIONS):
        if func["command"] != "interactive":
            print(f"{index}: {func['name']}")
    try:
        index = int(input("Enter the number of the function to perform: "))
        selected = FUNCTIONS[index]
    except (ValueError, IndexError):
        print("Invalid choice.")
        return
    # Get Arguments
    kwargs = {}

    optional_args = [
        arg for arg in selected["arguments"] if not arg.get("required", False)
    ]
    if optional_args:
        print(f"Optional arguments for {selected['name']}:")
        for arg in optional_args:
            if arg.get("action") == "store_true":
                print(f"'{arg['flag']}' : {arg['help']}")
            else:
                print(f"'{arg['flag']} value' : {arg['help']}")
        arguments = input(
            "Enter optional arguments (e.g., --flag --flag2 value): "
        ).strip()
        if arguments:
            tokens = arguments.split()
            i = 0
            while i < len(tokens):
                flag = tokens[i]
                arg_def = next(
                    (arg for arg in optional_args if arg["flag"] == flag), None
                )
                if not arg_def:
                    print(f"Warning: Unknown flag '{flag}' ignored.")
                    i += 1
                    continue
                if arg_def.get("action") == "store_true":
                    kwargs[arg_def["name"]] = True
                    i += 1
                else:
                    if i + 1 >= len(tokens):
                        print(
                            f"Warning: No value provided for '{flag}'. Using default if available."
                        )
                        kwargs[arg_def["name"]] = arg_def.get("default")
                        i += 1
                        continue
                    value = tokens[i + 1]
                    try:
                        kwargs[arg_def["name"]] = arg_def["type"](value)
                        i += 2
                    except (ValueError, TypeError):
                        print(
                            f"Warning: Invalid value '{value}' for '{flag}'. Using default if available."
                        )
                        kwargs[arg_def["name"]] = arg_def.get("default")
                        i += 2
    for arg in optional_args:
        if arg["name"] not in kwargs:
            if arg.get("action") == "store_true":
                kwargs[arg["name"]] = False
            elif arg.get("default", False):
                kwargs[arg["name"]] = arg.get("default")

    required_args = [arg for arg in selected["arguments"] if arg.get("required", False)]
    for arg in required_args:
        while True:
            value = input(arg["prompt"]).strip()
            if not value:
                print("This argument is required. Please provide a value.")
                continue
            try:
                kwargs[arg["name"]] = arg["type"](value)
                break
            except (ValueError, TypeError):
                print(f"Invalid value for {arg['name']}. Please try again.")

    try:
        p(f"Calling function with {kwargs}", v=5)
        selected["function"](**kwargs)
    except TypeError as e:
        print(f"Error calling function: {e}")


###################
# Parse Arguments #
###################.


def build_parser():
    parser = argparse.ArgumentParser(prog=PROGRAM_NAME, description=ABOUT, usage=USAGE)
    parser.add_argument(
        "-v",
        "--verbosity",
        type=int,
        default=1,
        help="Verbosity level, 0 for quiet, 5 for very verbose",
    )
    subparsers = parser.add_subparsers(dest="function", help="Function to perform")

    # Categories
    categories = {
        cat["command"]: subparsers.add_parser(cat["command"], help=cat["help"])
        for cat in FUNCTIONS
    }
    for category in categories:
        category_parser = categories[category]
        category_function = [f for f in FUNCTIONS if f["command"] == category][0]
        arg_set = {}
        for arg in category_function.get("arguments", []):
            flag = arg["flag"]
            if flag not in arg_set:
                arg_set[flag] = arg
        for flag, arg in arg_set.items():
            kwargs = {
                "help": arg.get("help", ""),
            }
            if arg.get("action"):
                kwargs["action"] = arg["action"]
            else:
                kwargs["type"] = arg.get("type", str)
                if arg.get("required", False):
                    kwargs["required"] = True
                elif arg.get("default", False):
                    kwargs["default"] = arg.get("default")
            # Use both short and long flags
            flags = [arg["flag"]]
            if arg.get("short_flag"):
                flags.insert(0, arg["short_flag"])  # Short flag first
            category_parser.add_argument(*flags, **kwargs)
    return parser


########
# Main #
########.


def main():
    global verbosity, environmental_variables

    parser = build_parser()
    args = parser.parse_args()

    verbosity = args.verbosity

    if not args.function:
        print(ABOUT)
        print(USAGE)
        print(f"You did not provide a function for {PROGRAM_NAME} to do. ")
        if "y" in input("Would you like to Enter interactive mode? (y/n): ").lower():
            interactive_mode()
            return

    for func in FUNCTIONS:
        if func["command"] == args.function:
            selected = func
            break
    else:
        print(f"Invalid function or missing required arguments for '{args.function}'.")
        print(USAGE)
        return

    p(f"Raw Arguments: {args}", v=5)
    kwargs = {}
    for arg in selected["arguments"]:
        arg_flag_name = arg["flag"].strip("-")
        arg_name = arg["name"]
        p(f"Processing {arg_flag_name}", v=5)

        # If arg is required and missing
        if arg.get("required", False) and getattr(args, arg_flag_name, None) is None:
            print(f"Missing required argument: {arg['flag']}")
            return
        # If arg has a require one of rule
        if selected.get("rules", {}).get("require_one_of", None) is not None:
            require_one_of = selected["rules"]["require_one_of"]
            count = 0
            for a in require_one_of:
                if hasattr(args, a):
                    count += 1
            if not count:
                print(
                    f"Error: You must provide one of these arguments: {', '.join(require_one_of)}"
                )
        # If arg is present
        if getattr(args, arg_flag_name, None) is not None:
            kwargs[arg_name] = getattr(args, arg_flag_name)
        # If arg has default and is not present
        elif getattr(arg, "default", None) is not None:
            kwargs[arg_name] = getattr(arg, "default")

    # Call the function
    try:
        p(f"Calling {selected['function'].__name__} with {kwargs}", v=5)
        selected["function"](**kwargs)
    except TypeError as e:
        print(f"Error calling function '{selected['name']}': {e}")

    # if args.function == "config":
    #     do_config()

    # elif args.function == "info":
    #     if args.ip:
    #         do_ip_info(args.ip)
    #     elif args.domain:
    #         do_domain_info(args.domain)
    #     elif args.url:
    #         do_url_info(args.url)

    # elif args.function == "search":
    #     if args.filename:
    #         do_filename_search(
    #             args.filename, args.find_all, args.regex, args.insensitive
    #         )

    # elif args.function == "tools":
    #     if args.url:
    #         do_url_unwrap(args.url)
    #     elif args.browser_history:
    #         do_browser_history(args.user)
    #     elif args.csvs:
    #         do_combine_csvs(args.csvs)
    #     elif args.cmd_history:
    #         do_command_history(args.user)


if __name__ == "__main__":
    main()
