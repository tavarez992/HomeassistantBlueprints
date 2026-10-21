#!/usr/bin/env python3
"""Rebuild the IKEA controller forks from EPMatt's upstream blueprints (Awesome HA Blueprints).

Each fork keeps every upstream input definition and everything from "# Automation schema" down
byte for byte; it only replaces the blueprint metadata and groups the inputs into sections.
When upstream adds or renames an input, the script stops and the controller's sections below
need an update.

Usage (from the repository root):
  python3 scripts/update_epmatt_forks.py                            # all forks, upstream from GitHub (main)
  python3 scripts/update_epmatt_forks.py styrbar                    # one fork
  python3 scripts/update_epmatt_forks.py tradfri --upstream x.yaml  # local copy of the upstream file
Then review the diff and update the version in README.md (changelog of the fork).
"""
import json
import re
import sys
import urllib.request

UPSTREAM_REPO = "EPMatt/awesome-ha-blueprints"

BUTTON_DESC = (
    "Short press, virtual double press, long press and release of the {what}. Turn on *Expose "
    "{word} button double press event* before you use the double press: the short press then "
    "waits for the double-press window before it runs."
)
CENTER_DESC = (
    "Short press, virtual double press and long press of the {what}. Turn on *Expose "
    "{word} button double press event* before you use the double press: the short press then "
    "waits for the double-press window before it runs."
)


def button_section(word, what, icon, with_release=True):
    """Section with all settings of one button: short, double, long (with looping) and release."""
    if with_release:
        inputs = [f"action_button_{word}_short", f"button_{word}_double_press", f"action_button_{word}_double",
                  f"action_button_{word}_long", f"button_{word}_long_loop",
                  f"button_{word}_long_max_loop_repeats", f"action_button_{word}_release"]
        description = BUTTON_DESC.format(what=what, word=word)
    else:
        inputs = [f"action_button_{word}_short", f"button_{word}_double_press", f"action_button_{word}_double",
                  f"action_button_{word}_long"]
        description = CENTER_DESC.format(what=what, word=word)
    return (f"{word}_section", what[0].upper() + what[1:], icon, True, description, inputs)


def remote_section(device):
    return ("remote_section", "Remote", "mdi:remote", False,
            f"Integration, the {device} and the Text helper for the last button event.",
            ["integration", "controller_device", "helper_last_controller_event"])


TIMING_SECTION = (
    "timing_section", "Timing", "mdi:timer-cog-outline", True,
    "Double-press window and debouncing. The defaults work for most remotes.",
    ["helper_double_press_delay", "helper_debounce_delay"],
)

# section = (key, name, icon, collapsed, description, inputs in display order)
CONTROLLERS = {
    "styrbar": {
        "upstream": "blueprints/controllers/ikea_e2001_e2002/ikea_e2001_e2002.yaml",
        "output": "blueprints/automation/IkeaStyrbar.yaml",
        "title": "IKEA STYRBAR remote (E2001/E2002)",
        "original": "Controller - IKEA E2001/E2002 STYRBAR Remote control",
        "link_text": "IKEA STYRBAR controller blueprint",
        "docs": "ikea_e2001_e2002",
        "anchor": "ikea-styrbar-remote",
        "summary": "Run any action on a **short press**, **long press** (optionally repeated until release), "
                   "**release** or a virtual **double press** of each of the four STYRBAR buttons. Works with "
                   "**Zigbee2MQTT**, **ZHA** and **deCONZ**.",
        "release_integrations": "ZHA and Zigbee2MQTT",
        "sections": [
            remote_section("STYRBAR device"),
            button_section("left", "left arrow button", "mdi:arrow-left-bold"),
            button_section("right", "right arrow button", "mdi:arrow-right-bold"),
            button_section("up", "up button (I)", "mdi:arrow-up-bold"),
            button_section("down", "down button (O)", "mdi:arrow-down-bold"),
            TIMING_SECTION,
        ],
    },
    "tradfri": {
        "upstream": "blueprints/controllers/ikea_e1524_e1810/ikea_e1524_e1810.yaml",
        "output": "blueprints/automation/IkeaTradfriRemote.yaml",
        "title": "IKEA TRÅDFRI remote (E1524/E1810)",
        "original": "Controller - IKEA E1524/E1810 TRÅDFRI Wireless 5-Button Remote",
        "link_text": "IKEA TRÅDFRI remote controller blueprint",
        "docs": "ikea_e1524_e1810",
        "anchor": "ikea-tradfri-remote",
        "summary": "Run any action on a **short press**, **long press** (optionally repeated until release), "
                   "**release** or a virtual **double press** of the five buttons of the IKEA TRÅDFRI remote "
                   "control. Works with **Zigbee2MQTT**, **ZHA** and **deCONZ**.",
        "release_integrations": "ZHA",
        "sections": [
            remote_section("TRÅDFRI remote"),
            button_section("center", "center button (power)", "mdi:power", with_release=False),
            button_section("up", "up button (brighter)", "mdi:arrow-up-bold"),
            button_section("down", "down button (dimmer)", "mdi:arrow-down-bold"),
            button_section("left", "left arrow button", "mdi:arrow-left-bold"),
            button_section("right", "right arrow button", "mdi:arrow-right-bold"),
            TIMING_SECTION,
        ],
    },
}

HEADER = """\
# {title} – fork with grouped inputs
#
# Original: "{original}" by EPMatt and contributors,
# Awesome HA Blueprints project, https://github.com/EPMatt/awesome-ha-blueprints
# ({upstream}, commit {commit}, blueprint
# version {version}), licensed under GPL-3.0.
#
# Changes in this fork (Shadala, 2026-10): inputs grouped into collapsible sections with icons
# and descriptions, new name, description and source_url. The input definitions and everything
# from "# Automation schema" down are the upstream code without changes.
blueprint:
  name: {title}
  # One line per paragraph: Home Assistant shows every line break in the description.
  description: |
    {summary}

    This is a fork of the [{link_text}](https://github.com/EPMatt/awesome-ha-blueprints/blob/main/{upstream}) by **EPMatt** from the [Awesome HA Blueprints](https://epmatt.github.io/awesome-ha-blueprints) project (GPL-3.0, version {version}). The automation logic is unchanged, the fork only groups the inputs into collapsible sections with icons. [Hooks](https://epmatt.github.io/awesome-ha-blueprints/docs/blueprints/hooks) keep working.

    **Before you start:** create a **Text helper** for the remote (*Settings → Devices & services → Helpers → Create helper → Text*). It stores the last button event and is needed for the double press and, with {release_integrations}, for the release.

    [Upstream documentation](https://epmatt.github.io/awesome-ha-blueprints/docs/blueprints/controllers/{docs}) · [About this fork](https://github.com/tavarez992/HomeassistantBlueprints#{anchor})
  domain: automation
  author: EPMatt (fork by Shadala)
  source_url: https://github.com/tavarez992/HomeassistantBlueprints/blob/main/{output}
  homeassistant:
    min_version: {min_version}
  input:"""


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "HomeassistantBlueprints-fork-update"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def build(name, upstream_text=None):
    ctrl = CONTROLLERS[name]
    if upstream_text is None:
        upstream_text = fetch(f"https://raw.githubusercontent.com/{UPSTREAM_REPO}/main/{ctrl['upstream']}")
        commits = json.loads(fetch(f"https://api.github.com/repos/{UPSTREAM_REPO}/commits?path={ctrl['upstream']}&per_page=1"))
        commit = commits[0]["sha"][:7]
    else:
        commit = input(f"{name}: upstream commit of this file (short hash): ").strip()

    lines = upstream_text.split("\n")
    start = lines.index("  input:") + 1
    end = lines.index("# Automation schema")
    version = re.search(r"^  ahb_version: (\S+)", upstream_text, re.M).group(1)
    min_version = re.search(r"^    min_version: (\S+)", upstream_text, re.M).group(1)

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

    sections = ctrl["sections"]
    used = [key for section in sections for key in section[5]]
    if sorted(used) != sorted(blocks) or len(used) != len(set(used)):
        sys.exit(f"{name}: inputs changed upstream, update its sections: {sorted(set(used) ^ set(blocks))}")

    fields = {k: v for k, v in ctrl.items() if isinstance(v, str)}
    out = [HEADER.format(commit=commit, version=version, min_version=min_version, **fields)]
    for key, title, icon, collapsed, description, inputs in sections:
        out += [f"    {key}:", f"      name: {title}", f"      icon: {icon}", "      description: >-"]
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
    with open(ctrl["output"], "w", encoding="utf-8") as f:
        f.write(text)
    print(f"{ctrl['output']}: upstream {version} (commit {commit}), {len(used)} inputs in {len(sections)} sections")


def main():
    args = sys.argv[1:]
    upstream_file = None
    if "--upstream" in args:
        i = args.index("--upstream")
        upstream_file = args[i + 1]
        del args[i:i + 2]
    names = args or list(CONTROLLERS)
    unknown = [n for n in names if n not in CONTROLLERS]
    if unknown or (upstream_file and len(names) != 1):
        sys.exit(__doc__)
    for name in names:
        build(name, open(upstream_file, encoding="utf-8").read() if upstream_file else None)


if __name__ == "__main__":
    main()
