# SPDX-FileCopyrightText: UL Research Institutes
# SPDX-License-Identifier: Apache-2.0

import hashlib
import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from io import StringIO

import ruamel.yaml
from termcolor import colored

from ..config.user import CACHE_DIR, CACHE_TIMEOUT, GITLAB_PRIVATE_TOKEN, GITLAB_URL

INCLUDE_CACHE_TIMEOUT = CACHE_TIMEOUT

INCLUDE_CACHE_DIR = CACHE_DIR / "include"

API_V4_URL = f"{GITLAB_URL}/api/v4"

HEADERS: dict[str, str] = {}

if GITLAB_PRIVATE_TOKEN:
    HEADERS.update({"PRIVATE-TOKEN": GITLAB_PRIVATE_TOKEN})


def to_fragment(text):
    if not isinstance(text, str):
        return text
    return urllib.parse.quote(text, safe="")


def get_apiv4_url(url):
    try:
        url = f"{API_V4_URL}{url}"
        request = urllib.request.Request(url=url, headers=HEADERS)
        response = urllib.request.urlopen(request)
        content = response.read()
        return json.loads(content)
    except urllib.error.HTTPError:
        return None


def get_project(project_id):
    return get_apiv4_url(f"/projects/{to_fragment(project_id)}")


def get_latest_release(project_id):
    return get_apiv4_url(
        f"/projects/{to_fragment(project_id)}/releases/permalink/latest"
    )


def write_project_data(filename, project_name):
    project = get_project(project_name)
    get_latest_release(project["id"])
    with open(filename, "w") as handle:
        handle.write(
            json.dumps(
                {"project": project, "release": get_latest_release(project["id"])},
                indent=4,
            )
        )


def update_include(include, force=False):
    if any(key not in include for key in ("project", "file")):
        return include

    includehash = hashlib.sha1(include["project"].lower().encode()).hexdigest()
    include_hash_file = INCLUDE_CACHE_DIR / f"{includehash}.json"

    if not force and include_hash_file.exists():
        current_timestamp = datetime.now().timestamp()
        file_timestamp = include_hash_file.stat().st_mtime
        if current_timestamp > file_timestamp + INCLUDE_CACHE_TIMEOUT:
            write_project_data(include_hash_file, include["project"])
    else:
        write_project_data(include_hash_file, include["project"])

    include_data = json.load(open(include_hash_file, "r"))
    project = include_data["project"]
    project_name = project["path_with_namespace"]
    latest_release = include_data["release"]

    if latest_release:
        latest_tag = latest_release["tag_name"]
        current_tag = include.get("ref", None)
        if current_tag:
            if current_tag != latest_tag:
                print(
                    colored("updated", "magenta"),
                    project_name,
                    colored("from", "magenta"),
                    current_tag,
                    colored("to", "magenta"),
                    latest_tag,
                )
        elif not current_tag:
            print(
                colored("updated", "magenta"),
                project_name,
                colored("to", "magenta"),
                latest_tag,
            )
        include["ref"] = latest_tag
    newinclude = {}
    newinclude["project"] = include["project"]
    if "ref" in include:
        newinclude["ref"] = include["ref"]
    newinclude["file"] = include["file"]
    return newinclude


def update_includes(includes, force=False):
    if not isinstance(includes, list):
        return includes

    return [update_include(include, force=force) for include in includes]


def update_command(parser, args):
    yaml = ruamel.yaml.YAML()
    data = yaml.load(open(args.filename))

    if not INCLUDE_CACHE_DIR.exists():
        INCLUDE_CACHE_DIR.mkdir(mode=0o755, parents=True, exist_ok=True)

    if "include" in data:
        data["include"] = update_includes(data["include"], force=args.force)

    output_file = StringIO()

    yaml.indent(mapping=2, sequence=4, offset=2)
    yaml.dump(data, output_file)

    output = output_file.getvalue()
    output = "\n".join([line.rstrip() for line in output.splitlines()]) + "\n"

    with open(args.filename, "w") as handle:
        handle.write(output)


def update_parser(subparsers):
    parser = subparsers.add_parser(
        "update", help="pin CI includes to the latest versions"
    )
    parser.add_argument(
        "-f", "--force", action="store_true", help="update CI includes right now"
    )
    parser.add_argument("filename", nargs="?", default=".gitlab-ci.yml")
    parser.set_defaults(func=update_command)
    return parser
