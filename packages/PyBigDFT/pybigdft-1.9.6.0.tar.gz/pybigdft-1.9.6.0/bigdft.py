#!/usr/bin/env python
"""
Executable script to create and launch a BigDFT calculation from the inputs.

Requires:
- structure.json (from ase.write())
- input.yaml

And optionally (advised):
- submission.yaml

call with

./bigdft.py --structure structure.json --parameters input.yaml --submission submission.yaml
"""
import os.path

from BigDFT.Calculators import SystemCalculator
from BigDFT.Inputfiles import Inputfile
from BigDFT.Interop.ASEInterop import ase_to_bigdft
from BigDFT.Logfiles import Logfile
from BigDFT.Systems import System
import ase.io
import click
import yaml


@click.command()
@click.option("--structure", help="path to structure json file")
@click.option("--parameters", help="yaml dumped dft parameters")
@click.option("--submission", help="extra submission parameters")
def run(
    structure: str = None, parameters: str = None, submission: str = None
) -> Logfile:
    """
    Run the calculation. Requires three file path inputs:

    Args:
        structure (str):
            path to the serialised ASE json file
        parameters (str):
            path to the serialised BigDFTParameters yaml file
        submission (str):
            path to the serialised submission yaml file

    Returns:
        BigDFT.Logfile
    """
    ########################
    ### submission param ###
    ########################
    params_sub = {}
    if submission is not None:
        with open(submission, encoding="utf8") as o:
            params_sub = yaml.safe_load(o)

    calc_args = {}

    if "mpirun" in params_sub:
        calc_args["mpi_run"] = params_sub["mpirun"]

    ########################
    ####    structure    ###
    ########################
    if structure is None:
        structure = "structure.json"
    structure = os.path.abspath(structure)
    struct_ase = ase.io.read(structure)

    # structure proper
    frag = ase_to_bigdft(struct_ase)

    sys = System()
    sys["FRA:1"] = frag

    ########################
    ####   calc params   ###
    ########################
    if parameters is None:
        parameters = "input.yaml"
    with open(parameters, encoding="utf8") as o:
        parameters = yaml.safe_load(o)
    inp = Inputfile(parameters)

    ########################
    ###    calculation   ###
    ########################
    code = SystemCalculator(**calc_args)
    log = code.run(
        input=inp, sys=sys, name=params_sub.get("jobname", "bigdft_calculation")
    )

    return log


if __name__ == "__main__":
    run()
