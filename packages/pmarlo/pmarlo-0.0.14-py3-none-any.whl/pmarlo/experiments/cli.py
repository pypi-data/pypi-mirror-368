import argparse
import json
import logging
from pathlib import Path

from .msm import MSMConfig, run_msm_experiment
from .replica_exchange import ReplicaExchangeConfig, run_replica_exchange_experiment
from .simulation import SimulationConfig, run_simulation_experiment

# CLI sets logging level; modules themselves do not configure basicConfig


def _tests_data_dir() -> Path:
    # Resolve to package root / tests / data
    here = Path(__file__).resolve().parents[2]
    return here / "tests" / "data"


def main():
    parser = argparse.ArgumentParser(
        description="PMARLO Experiments Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # 1) Simulation experiment
    sim = sub.add_parser("simulation", help="Run single-T simulation experiment")
    sim.add_argument("--pdb", default=str(_tests_data_dir() / "3gd8-fixed.pdb"))
    sim.add_argument("--steps", type=int, default=500)
    sim.add_argument("--out", default="experiments_output/simulation")
    sim.add_argument("--no-meta", action="store_true", help="Disable metadynamics")

    # 2) Replica exchange experiment
    remd = sub.add_parser("remd", help="Run replica exchange experiment")
    remd.add_argument("--pdb", default=str(_tests_data_dir() / "3gd8-fixed.pdb"))
    remd.add_argument("--steps", type=int, default=800)
    remd.add_argument("--equil", type=int, default=200)
    remd.add_argument("--freq", type=int, default=50, help="Exchange frequency")
    remd.add_argument("--out", default="experiments_output/replica_exchange")
    remd.add_argument("--no-meta", action="store_true", help="Disable metadynamics")

    # 3) MSM experiment
    msm = sub.add_parser("msm", help="Run MSM experiment on trajectories")
    msm.add_argument(
        "--traj",
        nargs="+",
        default=[str(_tests_data_dir() / "traj.dcd")],
        help="Trajectory files (DCD)",
    )
    msm.add_argument("--top", default=str(_tests_data_dir() / "3gd8-fixed.pdb"))
    msm.add_argument("--clusters", type=int, default=60)
    msm.add_argument("--lag", type=int, default=20)
    msm.add_argument("--out", default="experiments_output/msm")

    args = parser.parse_args()

    if args.cmd == "simulation":
        cfg = SimulationConfig(
            pdb_file=args.pdb,
            output_dir=args.out,
            steps=args.steps,
            use_metadynamics=not args.no_meta,
        )
        result = run_simulation_experiment(cfg)
    elif args.cmd == "remd":
        cfg = ReplicaExchangeConfig(
            pdb_file=args.pdb,
            output_dir=args.out,
            total_steps=args.steps,
            equilibration_steps=args.equil,
            exchange_frequency=args.freq,
            use_metadynamics=not args.no_meta,
        )
        result = run_replica_exchange_experiment(cfg)
    else:
        cfg = MSMConfig(
            trajectory_files=args.traj,
            topology_file=args.top,
            output_dir=args.out,
            n_clusters=args.clusters,
            lag_time=args.lag,
        )
        result = run_msm_experiment(cfg)

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
