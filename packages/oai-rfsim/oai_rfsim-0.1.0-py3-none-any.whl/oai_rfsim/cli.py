"""Command‑line interface for the oai‑rfsim package.

The CLI is built with the standard :mod:`argparse` module to avoid
pulling in heavy external dependencies.  It exposes subcommands for
common tasks such as cloning the sources, building the softmodems and
running them.  Internally it delegates to helper functions that
execute the relevant shell commands.  These functions use
`subprocess.run` and propagate exceptions to the caller when a
command fails.

Example usage::

    # clone the sources
    oai-rfsim init --path ./openairinterface5g

    # build gNB and nrUE on the host machine
    oai-rfsim build baremetal --gnb --nrue

    # build a gNB docker image tagged oai-gnb:develop
    oai-rfsim build docker --target gnb --os ubuntu22 --tag oai-gnb:develop

    # run the gNB with an RF simulator
    oai-rfsim run baremetal --target gnb --config my_gnb.conf --serveraddr server

The commands executed by this script are derived from the official
OpenAirInterface documentation.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: list[str], cwd: Path | None = None) -> None:
    """Run a shell command and raise if it fails.

    Parameters
    ----------
    cmd : list[str]
        The command and its arguments to execute.  Each element in the
        list corresponds to one argument; no shell expansion is
        performed.
    cwd : Path | None, optional
        If given, the working directory to use for the command.  If
        not provided the current working directory is used.

    Raises
    ------
    subprocess.CalledProcessError
        When the command returns a non‑zero exit code.
    """
    print(f"[*] Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=True)


def clone_sources(path: Path, branch: str = "develop") -> None:
    """Clone the OpenAirInterface sources into *path*.

    The function runs a shallow clone of the `openairinterface5g`
    repository from GitHub.  It is equivalent to the following
    command::

        git clone --depth 1 --branch develop \
            https://github.com/OPENAIRINTERFACE/openairinterface5g.git <path>

    Parameters
    ----------
    path : Path
        Destination directory for the clone.
    branch : str, optional
        Branch to clone; defaults to ``develop``.
    """
    if path.exists():
        raise FileExistsError(f"Destination {path} already exists")
    run_cmd([
        "git",
        "clone",
        "--depth",
        "1",
        "--branch",
        branch,
        "https://github.com/OPENAIRINTERFACE/openairinterface5g.git",
        str(path),
    ])


def build_baremetal(
    source_dir: Path,
    *,
    gnb: bool = False,
    nrue: bool = False,
    enb: bool = False,
    ue: bool = False,
    all_targets: bool = False,
    ninja: bool = True,
    clean: bool = False,
    install_deps: bool = False,
) -> None:
    """Build the OAI softmodems on the host machine.

    Parameters
    ----------
    source_dir : Path
        Location of the cloned ``openairinterface5g`` repository.
    gnb : bool, optional
        Whether to build the 5G gNB (`nr‑softmodem`).
    nrue : bool, optional
        Whether to build the 5G UE (`nr‑uesoftmodem`).
    enb : bool, optional
        Whether to build the LTE eNB (`lte‑softmodem`).
    ue : bool, optional
        Whether to build the LTE UE (`lte‑uesoftmodem`).
    all_targets : bool, optional
        Build all four modems (equivalent to specifying all of the above).
    ninja : bool, optional
        Use `ninja` instead of `make` for faster builds.  Defaults to
        True.
    clean : bool, optional
        If True, pass ``-c`` to the build script to force a full
        rebuild.
    install_deps : bool, optional
        If True, run the build script with ``-I`` to install
        prerequisites first.  Requires sudo privileges.
    """
    cmake_targets = source_dir / "cmake_targets"
    build_script = cmake_targets / "build_oai"
    if not build_script.exists():
        raise FileNotFoundError(
            f"build script not found at {build_script}. Did you clone the sources?"
        )

    # Build options
    opts: list[str] = []
    if install_deps:
        opts.append("-I")
        # install optional packages as well; this speeds up subsequent builds
        opts.append("--install-optional-packages")
    if clean:
        opts.append("-c")
    if ninja:
        opts.append("--ninja")
    # Always include the RF simulator device
    opts.extend(["-w", "SIMU"])
    # Targets
    if all_targets or (not gnb and not nrue and not enb and not ue):
        gnb = nrue = enb = ue = True
    if gnb:
        opts.append("--gNB")
    if nrue:
        opts.append("--nrUE")
    if enb:
        opts.append("--eNB")
    if ue:
        opts.append("--UE")

    cmd = ["bash", str(build_script)] + opts
    run_cmd(cmd, cwd=cmake_targets)


def build_docker(
    source_dir: Path,
    *,
    target: str,
    os_version: str = "ubuntu22",
    tag: str | None = None,
    build_args: list[str] | None = None,
) -> None:
    """Build a Docker image for the specified OAI target.

    This function constructs the appropriate Dockerfile name based on
    the target and OS version and delegates the build to Docker.  The
    default strategy follows the official OAI guidelines: build the
    `ran-base` and `ran-build` images first and then build the
    particular modem image.  When building your own
    images you may want to specify a custom tag, otherwise `latest`
    will be used.  Additional build arguments can be passed via
    ``build_args``.

    Parameters
    ----------
    source_dir : Path
        Root of the cloned OAI repository.
    target : str
        Name of the target to build, e.g. ``gnb``, ``nrue``, ``enb`` or
        ``lteue``.  Case‑insensitive.
    os_version : str, optional
        Operating system to use.  Valid values correspond to existing
        Dockerfiles in the `docker` directory (e.g. ``ubuntu22``,
        ``rhel9``, ``rocky``).  Defaults to ``ubuntu22``.
    tag : str | None, optional
        Name (including tag) to assign to the resulting Docker image.
        If omitted the image will be tagged as ``oai-<TARGET>:latest``.
    build_args : list[str] | None, optional
        Extra arguments to pass to `docker build`.  Each argument
        should be formatted as a full `--build-arg ...` string.
    """
    docker_dir = source_dir / "docker"
    if not docker_dir.exists():
        raise FileNotFoundError("Docker directory not found; ensure the sources are cloned")

    target_lower = target.lower()
    # Determine the Dockerfile name.  For UE we use NR UE; LTE UE is lteUE
    if target_lower in {"gnb", "g_nb", "5g"}:
        df = f"Dockerfile.gNB.{os_version}"
        image_default = "oai-gnb"
    elif target_lower in {"nrue", "nr_ue", "5gue"}:
        df = f"Dockerfile.nrUE.{os_version}"
        image_default = "oai-nr-ue"
    elif target_lower in {"enb", "e_nb", "4g"}:
        df = f"Dockerfile.eNB.{os_version}"
        image_default = "oai-enb"
    elif target_lower in {"lteue", "lte_ue", "4gue"}:
        df = f"Dockerfile.lteUE.{os_version}"
        image_default = "oai-lte-ue"
    else:
        raise ValueError(f"Unknown target: {target}")

    dockerfile = docker_dir / df
    if not dockerfile.exists():
        raise FileNotFoundError(f"Dockerfile {dockerfile} not found. Unsupported OS/version combination.")
    image_tag = tag or f"{image_default}:latest"

    # Build the base and build images first, if they do not already exist.
    # Users can choose to skip this step by passing build_args containing
    # --skip-base-build or similar custom behaviour.
    # Build ran-base
    base_df = docker_dir / f"Dockerfile.base.{os_version}"
    run_cmd([
        "docker",
        "build",
        "--target",
        "ran-base",
        "--tag",
        "ran-base:latest",
        "--file",
        str(base_df),
        ".",
    ], cwd=source_dir)
    # Build ran-build
    build_df = docker_dir / f"Dockerfile.build.{os_version}"
    run_cmd([
        "docker",
        "build",
        "--target",
        "ran-build",
        "--tag",
        "ran-build:latest",
        "--file",
        str(build_df),
        ".",
    ], cwd=source_dir)

    # Now build the requested image
    cmd = [
        "docker",
        "build",
        "--target",
        f"oai-{target_lower}",
        "--tag",
        image_tag,
        "--file",
        str(dockerfile),
    ]
    if build_args:
        cmd.extend(build_args)
    cmd.append(".")
    run_cmd(cmd, cwd=source_dir)


def run_baremetal(
    source_dir: Path,
    *,
    target: str,
    config: str | None = None,
    serveraddr: str | None = None,
    additional_args: list[str] | None = None,
) -> None:
    """Run a softmodem on the host in RF simulator mode.

    Parameters
    ----------
    source_dir : Path
        Root of the cloned OAI repository.
    target : str
        Which softmodem to run (``gnb``, ``nrue``, ``enb`` or ``lteue``).
    config : str | None
        Path to a YAML configuration file for the modem.  If omitted
        the program will run with default settings.
    serveraddr : str | None
        For UE softmodems, address of the gNB/eNB to connect to.  For
        gNB/eNB you can specify ``server`` to listen for connections.
    additional_args : list[str] | None
        Extra command‑line arguments to pass verbatim to the softmodem.
    """
    # Determine binary name and working directory
    build_dir = source_dir / "cmake_targets" / "ran_build" / "build"
    if target.lower() in {"gnb", "g_nb", "5g"}:
        exe = "nr-softmodem"
    elif target.lower() in {"nrue", "nr_ue", "5gue"}:
        exe = "nr-uesoftmodem"
    elif target.lower() in {"enb", "e_nb", "4g"}:
        exe = "lte-softmodem"
    elif target.lower() in {"lteue", "lte_ue", "4gue"}:
        exe = "lte-uesoftmodem"
    else:
        raise ValueError(f"Unknown target: {target}")
    executable = build_dir / exe
    if not executable.exists():
        raise FileNotFoundError(
            f"Executable {exe} not found. Make sure you built the softmodem first."
        )
    # Compose arguments
    args: list[str] = []
    if config:
        args.extend(["-O", config])
    # Always enable RF simulation
    args.append("--rfsim")
    if serveraddr:
        args.extend(["--rfsimulator.serveraddr", serveraddr])
    if additional_args:
        args.extend(additional_args)
    # Prepend sudo if we are not root
    cmd = []
    if os.geteuid() != 0:
        cmd.append("sudo")
    cmd.append(str(executable))
    cmd.extend(args)
    run_cmd(cmd, cwd=build_dir)


def parse_args(args: list[str] | None = None) -> argparse.Namespace:
    """Set up the argument parser and return parsed arguments."""
    parser = argparse.ArgumentParser(
        description="OpenAirInterface RF simulator command‑line helper."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    init_p = subparsers.add_parser("init", help="clone the OAI develop branch")
    init_p.add_argument(
        "--path",
        type=Path,
        default=Path("openairinterface5g"),
        help="destination directory to clone into",
    )
    init_p.add_argument(
        "--branch",
        type=str,
        default="develop",
        help="git branch to clone (default: develop)",
    )

    # build subcommand
    build_p = subparsers.add_parser("build", help="build the softmodems or Docker images")
    build_sub = build_p.add_subparsers(dest="build_type", required=True)

    # build baremetal
    bm = build_sub.add_parser("baremetal", help="build softmodems on the host machine")
    bm.add_argument("source", type=Path, help="path to the OAI source tree")
    bm.add_argument("--gnb", action="store_true", help="build the 5G gNB")
    bm.add_argument("--nrue", action="store_true", help="build the 5G UE")
    bm.add_argument("--enb", action="store_true", help="build the LTE eNB")
    bm.add_argument("--ue", action="store_true", help="build the LTE UE")
    bm.add_argument("--all", action="store_true", help="build all four modems")
    bm.add_argument("--clean", action="store_true", help="force a full rebuild")
    bm.add_argument(
        "--no-ninja",
        action="store_true",
        help="use make instead of ninja (slower)",
    )
    bm.add_argument(
        "--install-deps",
        action="store_true",
        help="install prerequisites before compiling (requires sudo)",
    )

    # build docker
    bd = build_sub.add_parser("docker", help="build Docker images")
    bd.add_argument("source", type=Path, help="path to the OAI source tree")
    bd.add_argument(
        "--target",
        type=str,
        required=True,
        choices=["gnb", "nrue", "enb", "lteue"],
        help="which image to build",
    )
    bd.add_argument(
        "--os",
        type=str,
        default="ubuntu22",
        help="OS version (ubuntu22, rhel9, rocky)",
    )
    bd.add_argument(
        "--tag",
        type=str,
        default=None,
        help="tag for the resulting image (defaults to oai-<target>:latest)",
    )
    bd.add_argument(
        "--build-arg",
        dest="build_args",
        action="append",
        default=None,
        help="additional --build-arg options for docker build",
    )

    # run subcommand
    run_p = subparsers.add_parser("run", help="run a softmodem")
    run_sub = run_p.add_subparsers(dest="run_type", required=True)

    # run baremetal
    rb = run_sub.add_parser("baremetal", help="run on the host machine")
    rb.add_argument("source", type=Path, help="path to the OAI source tree")
    rb.add_argument(
        "--target",
        type=str,
        required=True,
        choices=["gnb", "nrue", "enb", "lteue"],
        help="which softmodem to run",
    )
    rb.add_argument(
        "--config",
        type=str,
        default=None,
        help="YAML/CFG configuration file for the modem",
    )
    rb.add_argument(
        "--serveraddr",
        type=str,
        default=None,
        help="server address (eNB/gNB) or remote UE IP",
    )
    rb.add_argument(
        "--extra",
        dest="additional_args",
        action="append",
        default=None,
        help="any extra arguments to pass to the softmodem",
    )

    # run docker – this simply prints instructions because
    # orchestrating container runs can be highly use‑case specific
    rd = run_sub.add_parser("docker", help="print docker run instructions")
    rd.add_argument(
        "--target",
        type=str,
        required=True,
        choices=["gnb", "nrue", "enb", "lteue"],
        help="which image to run",
    )
    rd.add_argument(
        "--tag",
        type=str,
        default=None,
        help="image name:tag to run (defaults to oai-<target>:latest)",
    )
    rd.add_argument(
        "--config",
        type=str,
        default=None,
        help="mount a configuration file inside the container",
    )

    return parser.parse_args(args)


def main(argv: list[str] | None = None) -> int:
    """Entry point for the console script."""
    args = parse_args(argv)
    try:
        if args.command == "init":
            clone_sources(args.path, branch=args.branch)
        elif args.command == "build":
            if args.build_type == "baremetal":
                build_baremetal(
                    args.source,
                    gnb=args.gnb,
                    nrue=args.nrue,
                    enb=args.enb,
                    ue=args.ue,
                    all_targets=args.all,
                    ninja=not args.no_ninja,
                    clean=args.clean,
                    install_deps=args.install_deps,
                )
            elif args.build_type == "docker":
                build_docker(
                    args.source,
                    target=args.target,
                    os_version=args.os,
                    tag=args.tag,
                    build_args=args.build_args,
                )
        elif args.command == "run":
            if args.run_type == "baremetal":
                run_baremetal(
                    args.source,
                    target=args.target,
                    config=args.config,
                    serveraddr=args.serveraddr,
                    additional_args=args.additional_args,
                )
            elif args.run_type == "docker":
                # Print instructions for running in docker.  Running a
                # containerised gNB/UE typically involves using
                # docker-compose and network configuration.  We
                # therefore provide a basic example and refer the user
                # to the OAI documentation for advanced setups
                image = args.tag or f"oai-{args.target}:latest"
                print(
                    f"Run the {args.target} container with:\n"
                    f"  docker run --rm --network host {image} [additional docker args]\n"
                    f"Mount your configuration file (if any) under /opt/oai/share/conf by adding:\n"
                    f"  -v <path_to_conf>:/opt/oai/share/conf/{os.path.basename(args.config) if args.config else '<your.conf>'}"
                )
        return 0
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())