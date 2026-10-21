#!/usr/bin/env python3
"""Rebuild blueprints/automation/IkeaStyrbar.yaml from EPMatt's upstream STYRBAR blueprint.

The fork keeps every upstream input definition and everything from "# Automation schema" down
byte for byte; it only replaces the blueprint metadata and groups the inputs into sections.
When upstream adds or renames an input, the script stops and SECTIONS below needs an update.

Usage (from the repository root):
  python3 scripts/update_styrbar_fork.py                  # download upstream from GitHub (main)
  python3 scripts/update_styrbar_fork.py upstream.yaml    # use a local copy of the upstream file
Then review the diff and update the version in README.md (IKEA STYRBAR changelog).
"""
import json
import re
import sys
import urllib.request

UPSTREAM_PATH = "blueprints/controllers/ikea_e2001_e2002/ikea_e2001_e2002.yaml"
UPSTREAM_RAW = f"https://raw.githubusercontent.com/EPMatt/awesome-ha-blueprints/main/{UPSTREAM_PATH}"
UPSTREAM_COMMITS = (
    f"https://api.github.com/repos/EPMatt/awesome-ha-blueprints/commits?path={UPSTREAM_PATH}&per_page=1"
)
OUTPUT = "blueprints/automation/IkeaStyrbar.yaml"

HEADER = """\
# IKEA STYRBAR remote (E2001/E2002) – fork with grouped inputs
#
# Original: "Controller - IKEA E2001/E2002 STYRBAR Remote control" by EPMatt and contributors,
# Awesome HA Blueprints project, https://github.com/EPMatt/awesome-ha-blueprints
# (blueprints/controllers/ikea_e2001_e2002/ikea_e2001_e2002.yaml, commit {commit}, blueprint
# version {version}), licensed under GPL-3.0.
#
# Changes in this fork (Shadala, 2026-10): inputs grouped into collapsible sections with icons
# and descriptions, new name, description and source_url. The input definitions and everything
# from "# Automation schema" down are the upstream code without changes.
blueprint:
  name: IKEA STYRBAR remote (E2001/E2002)
  # One line per paragraph: Home Assistant shows every line break in the description.
  description: |
    Run any action on a **short press**, **long press** (optionally repeated until release), **release** or a virtual **double press** of each of the four STYRBAR buttons. Works with **Zigbee2MQTT**, **ZHA** and **deCONZ**.

    This is a fork of the [IKEA STYRBAR controller blueprint](https://github.com/EPMatt/awesome-ha-blueprints/blob/main/blueprints/controllers/ikea_e2001_e2002/ikea_e2001_e2002.yaml) by **EPMatt** from the [Awesome HA Blueprints](https://epmatt.github.io/awesome-ha-blueprints) project (GPL-3.0, version {version}). The automation logic is unchanged, the fork only groups the inputs into collapsible sections with icons. [Hooks](https://epmatt.github.io/awesome-ha-blueprints/docs/blueprints/hooks) keep working.

    **Before you start:** create a **Text helper** for the remote (*Settings → Devices & services → Helpers → Create helper → Text*). It stores the last button event and is needed for the double press and, with ZHA and Zigbee2MQTT, for the release.

    [Upstream documentation](https://epmatt.github.io/awesome-ha-blueprints/docs/blueprints/controllers/ikea_e2001_e2002) · [About this fork](https://github.com/tavarez992/HomeassistantBlueprints#ikea-styrbar-remote)
  domain: automation
  author: EPMatt (fork by Shadala)
  source_url: https://github.com/tavarez992/HomeassistantBlueprints/blob/main/blueprints/automation/IkeaStyrbar.yaml
  homeassistant:
    min_version: {min_version}
  input:"""

BUTTON_DESC = (
    "Short press, virtual double press, long press and release of the {what}. Turn on *Expose "
    "{word} button double press event* before you use the double press: the short press then "
    "waits for the double-press window before it runs."
)

# (key, name, icon, collapsed, description, inputs in display order)
SECTIONS = [
    ("remote_section", "Remote", "mdi:remote", False,
     "Integration, the STYRBAR device and the Text helper for the last button event.",
     ["integration", "controller_device", "helper_last_controller_event"]),
]
for word, what, icon in [
    ("left", "left arrow button", "mdi:arrow-left-bold"),
    ("right", "right arrow button", "mdi:arrow-right-bold"),
    ("up", "up button (I)", "mdi:arrow-up-bold"),
    ("down", "down button (O)", "mdi:arrow-down-bold"),
]:
    SECTIONS.append((
        f"{word}_section", what[0].upper() + what[1:], icon, True,
        BUTTON_DESC.format(what=what, word=word),
        [f"action_button_{word}_short", f"button_{word}_double_press", f"action_button_{word}_double",
         f"action_button_{word}_long", f"button_{word}_long_loop", f"button_{word}_long_max_loop_repeats",
         f"action_button_{word}_release"],
    ))
SECTIONS.append((
    "timing_section", "Timing", "mdi:timer-cog-outline", True,
    "Double-press window and debouncing. The defaults work for most remotes.",
    ["helper_double_press_delay", "helper_debounce_delay"],
))


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return response.read().decode("utf-8")


def main():
    if len(sys.argv) > 1:
        upstream = open(sys.argv[1], encoding="utf-8").read()
        commit = input("Upstream commit of this file (short hash): ").strip()
    else:
        upstream = fetch(UPSTREAM_RAW)
        commit = json.loads(fetch(UPSTREAM_COMMITS))[0]["sha"][:7]

    lines = upstream.split("\n")
    start = lines.index("  input:") + 1
    end = lines.index("# Automation schema")
    version = re.search(r"^  ahb_version: (\S+)", upstream, re.M).group(1)
    min_version = re.search(r"^    min_version: (\S+)", upstream, re.M).group(1)

    # Split the inputs into blocks by their key (4 spaces). Group comments on the same level are
    # dropped (the sections replace them), comments inside a block stay.
    blocks, current = {}, None
    for line in lines[start:end]:
        match = re.match(r"^    ([a-z0-9_]+):\s*$", line)
        if match:
            current = match.group(1)
            blocks[current] = [line]
        elif re.match(r"^    #", line):
            continue
        elif current is not None:
            blocks[current].append(line)

    used = [key for section in SECTIONS for key in section[5]]
    if sorted(used) != sorted(blocks) or len(used) != len(set(used)):
        sys.exit(f"Inputs changed upstream, update SECTIONS: {sorted(set(used) ^ set(blocks))}")

    out = [HEADER.format(commit=commit, version=version, min_version=min_version)]
    for key, name, icon, collapsed, description, inputs in SECTIONS:
        out += [f"    {key}:", f"      name: {name}", f"      icon: {icon}", "      description: >-"]
        line = "       "
        for word in description.split():
            if len(line) + 1 + len(word) > 104:
                out.append(line)
                line = "       "
            line += " " + word
        out.append(line)
        if collapsed:
            out.append("      collapsed: true")
        out.append("      input:")
        for input_key in inputs:
            out += [("    " + line) if line.strip() else line for line in blocks[input_key]]
    out += lines[end:]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(out))
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{OUTPUT}: upstream {version} (commit {commit}), {len(used)} inputs in {len(SECTIONS)} sections")


if __name__ == "__main__":
    main()
