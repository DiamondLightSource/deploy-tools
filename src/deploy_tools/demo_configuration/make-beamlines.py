#!/usr/bin/env python3
from pathlib import Path

import jinja2

beamlines = [
    {"p45": ["pollux", "github.com/epics-containers"]},
    {"p46": ["pollux", "github.com/epics-containers"]},
    {"p47": ["pollux", "github.com/epics-containers"]},
    {"p48": ["pollux", "github.com/epics-containers"]},
    {"p49": ["pollux", "github.com/epics-containers"]},
    {"p38": ["k8s-p38", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"p99": ["k8s-p99", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"b01-1": ["k8s-b01-1", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"b16": ["k8s-b16", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"b18": ["k8s-b18", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"b21": ["k8s-b21", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i02-1": ["k8s-i02-1", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i02-2": ["k8s-i02-2", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i03": ["k8s-i03", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i04": ["k8s-i04", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i04-1": ["k8s-i04-1", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i06": ["k8s-i06", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i10": ["k8s-i10", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i11": ["k8s-i11", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i13": ["k8s-i13", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i13-1": ["k8s-i13-1", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i15-1": ["k8s-i15-1", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i16": ["k8s-i16", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i18": ["k8s-i18", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i19": ["k8s-i19", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i20-1": ["k8s-i20-1", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i21": ["k8s-i21", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i22": ["k8s-i22", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i23": ["k8s-i23", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"i24": ["k8s-i24", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
    {"k11": ["k8s-k11", "gitlab.diamond.ac.uk/controls/containers/beamline"]},
]

ec_root_dir = Path(__file__).parent / "ec"
template_file = Path(__file__).parent / "beamline.yaml.j2"


def main():
    """make all the beamline module description yaml files"""

    template = template_file.read_text()
    jt = jinja2.Template(template)

    for beamline in beamlines:
        for name, (cluster, organization) in beamline.items():
            print(f"Generating {name} module description")
            module_file = ec_root_dir / f"{name}.yaml"

            rendered = jt.render(
                name=name,
                cluster_name=cluster,
                organization=organization,
            )
            module_file.write_text(rendered + "\n")


if __name__ == "__main__":
    main()
