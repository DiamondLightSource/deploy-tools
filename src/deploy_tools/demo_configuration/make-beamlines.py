#!/usr/bin/env python3
from pathlib import Path

import jinja2

gh = "github.com/epics-containers"
gl = "gitlab.diamond.ac.uk/controls/containers/beamline"
beamlines = [
    {"p45": ["pollux", gh]},
    {"p46": ["pollux", gh]},
    {"p47": ["pollux", gh]},
    {"p48": ["pollux", gh]},
    {"p49": ["pollux", gh]},
    {"p38": ["k8s-p38", gl]},
    {"p51": ["k8s-i20-1", gl]},
    {"p99": ["k8s-p99", gl]},
    {"b01-1": ["k8s-b01-1", gl]},
    {"b07": ["k8s-b07", gl]},
    {"b07-1": ["k8s-b07-1", gl]},
    {"b16": ["k8s-b16", gl]},
    {"b18": ["k8s-b18", gl]},
    {"b21": ["k8s-b21", gl]},
    {"b22": ["k8s-b22", gl]},
    {"b23": ["k8s-b23", gl]},
    {"b24": ["k8s-b24", gl]},
    {"i02-1": ["k8s-i02-1", gl]},
    {"i02-2": ["k8s-i02-2", gl]},
    {"i03": ["k8s-i03", gl]},
    {"i04": ["k8s-i04", gl]},
    {"i04-1": ["k8s-i04-1", gl]},
    {"i05": ["k8s-i05", gl]},
    {"i06": ["k8s-i06", gl]},
    {"i07": ["k8s-i07", gl]},
    {"i08": ["k8s-i08", gl]},
    {"i09": ["k8s-i09", gl]},
    {"i10": ["k8s-i10", gl]},
    {"i11": ["k8s-i11", gl]},
    {"i12": ["k8s-i12", gl]},
    {"i13": ["k8s-i13", gl]},
    {"i13-1": ["k8s-i13-1", gl]},
    {"i14": ["k8s-i14", gl]},
    {"i15": ["k8s-i15", gl]},
    {"i16": ["k8s-i16", gl]},
    {"i18": ["k8s-i18", gl]},
    {"i19": ["k8s-i19", gl]},
    {"i20": ["k8s-i20", gl]},
    {"i20-1": ["k8s-i20-1", gl]},
    {"i21": ["k8s-i21", gl]},
    {"i22": ["k8s-i22", gl]},
    {"i23": ["k8s-i23", gl]},
    {"i24": ["k8s-i24", gl]},
    {"k11": ["k8s-k11", gl]},
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
