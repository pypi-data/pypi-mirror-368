# Copyright (c) 2025 PMARLO Development Team
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Simulation module for PMARLO.

Provides molecular dynamics simulation capabilities with metadynamics and system preparation.
"""

from collections import defaultdict

import mdtraj as md
import numpy as np
import openmm.unit
from openmm import *
from openmm import Platform
from openmm.app import *
from openmm.app import Modeller
from openmm.app.metadynamics import Metadynamics
from openmm.unit import *
from sklearn.cluster import MiniBatchKMeans

# PDBFixer is optional - users can install with: pip install "pmarlo[fixer]"
try:
    from pdbfixer import PDBFixer

    HAS_PDBFIXER = True
except ImportError:
    PDBFixer = None
    HAS_PDBFIXER = False
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple

import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
TESTS_DIR = BASE_DIR / "tests" / "data"


class Simulation:
    """
    Molecular Dynamics Simulation class for PMARLO.

    Handles system preparation, equilibration, and production runs with metadynamics.
    """

    def __init__(
        self,
        pdb_file: str,
        temperature: float = 300.0,
        steps: int = 1000,
        output_dir: str = "output/simulation",
        use_metadynamics: bool = True,
    ):
        """
        Initialize the Simulation.

        Args:
            pdb_file: Path to the prepared PDB file
            temperature: Simulation temperature in Kelvin
            steps: Number of production steps
            output_dir: Directory for output files
            use_metadynamics: Whether to use metadynamics biasing
        """
        self.pdb_file = pdb_file
        self.temperature = temperature
        self.steps = steps
        self.output_dir = Path(output_dir)
        self.use_metadynamics = use_metadynamics

        # OpenMM objects
        self.openmm_simulation = None
        self.meta = None
        self.system = None
        self.integrator = None

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def prepare_system(
        self,
    ) -> Tuple["openmm.app.Simulation", Optional["Metadynamics"]]:
        """Prepare the molecular system with forcefield and optional metadynamics."""
        simulation, meta = prepare_system(
            self.pdb_file, self.temperature, self.use_metadynamics, self.output_dir
        )
        return simulation, meta

    def run_production(self, openmm_simulation=None, meta=None) -> str:
        """Run production molecular dynamics simulation."""
        if openmm_simulation is None:
            openmm_simulation = self.openmm_simulation
        if meta is None:
            meta = self.meta

        trajectory_file = production_run(
            self.steps, openmm_simulation, meta, self.output_dir
        )
        return str(trajectory_file)

    def extract_features(self, trajectory_file: str) -> np.ndarray:
        """Extract features from trajectory for MSM analysis."""
        states = feature_extraction(trajectory_file, self.pdb_file)
        return np.array(states)

    def run_complete_simulation(self) -> Tuple[str, np.ndarray]:
        """Run complete simulation pipeline and return trajectory file and states."""
        logger.info(f"Starting simulation for {self.pdb_file}")

        # Prepare system
        self.openmm_simulation, self.meta = self.prepare_system()

        # Run production
        trajectory_file = self.run_production()

        # Extract features
        states = self.extract_features(trajectory_file)

        logger.info(f"Simulation complete. Trajectory: {trajectory_file}")
        return trajectory_file, states


def prepare_system(
    pdb_file_name, temperature=300.0, use_metadynamics=True, output_dir=None
):
    """Prepare the molecular system with forcefield and optional metadynamics."""
    pdb = PDBFile(pdb_file_name)
    forcefield = ForceField("amber14-all.xml", "amber14/tip3pfb.xml")

    system = forcefield.createSystem(
        pdb.topology, nonbondedMethod=PME, constraints=HBonds
    )

    meta = None
    if use_metadynamics:
        traj0 = md.load_pdb(pdb_file_name)
        phi_indices, _ = md.compute_phi(traj0)
        if len(phi_indices) == 0:
            raise RuntimeError(
                "No φ dihedral found in the PDB structure – cannot set up CV."
            )

        phi_atoms = [int(i) for i in phi_indices[0]]

        phi_force = CustomTorsionForce("theta")
        phi_force.addTorsion(*phi_atoms, [])

        phi_cv = BiasVariable(
            phi_force,
            minValue=-np.pi,
            maxValue=np.pi,
            biasWidth=0.35,  # ~20°
            periodic=True,
        )

        if output_dir is None:
            # Default all artifacts under unified output tree
            output_dir = Path("output") / "simulation"
        else:
            output_dir = Path(output_dir)
        bias_dir = output_dir / "bias"

        # Clear existing bias files to avoid conflicts
        if bias_dir.exists():
            for file in bias_dir.glob("bias_*.npy"):
                try:
                    file.unlink()
                except Exception:
                    pass

        os.makedirs(str(bias_dir), exist_ok=True)

        meta = Metadynamics(
            system,
            [phi_cv],
            temperature=temperature * kelvin,
            biasFactor=10.0,
            height=1.0 * kilojoules_per_mole,
            frequency=500,  # hill every 1 ps (500 × 2 fs)
            biasDir=str(bias_dir),
            saveFrequency=1000,
        )

    integrator = LangevinIntegrator(
        temperature * kelvin, 1 / picosecond, 2 * femtoseconds  # T  # γ
    )  # Δt

    # DO *NOT* add phi_force to the System – Metadynamics will own it.
    platform = Platform.getPlatformByName("CPU")  # or "CPU", "OpenCL", etc.

    from openmm.app import Simulation as OpenMMSimulation

    simulation = OpenMMSimulation(pdb.topology, system, integrator, platform)
    simulation.context.setPositions(pdb.positions)

    simulation.minimizeEnergy(maxIterations=100)
    simulation.step(1000)
    print("✔ Build & equilibration complete\n")
    return simulation, meta


def production_run(steps, simulation, meta, output_dir=None):
    """Run production molecular dynamics simulation."""
    print("Stage 3/5  –  production run...")

    if output_dir is None:
        output_dir = Path("output") / "simulation"
    else:
        output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dcd_filename = str(output_dir / "traj.dcd")
    dcd = DCDReporter(dcd_filename, 10)  # save every 10 steps
    simulation.reporters.append(dcd)

    total_steps = steps
    step_size = 10
    bias_list = []

    if meta is not None:
        for i in range(total_steps // step_size):
            meta.step(simulation, step_size)
            simulation.step(0)  # triggers reporters
            try:
                bias_val = meta._currentBias
            except AttributeError:
                bias_val = 0.0
            for _ in range(step_size):
                bias_list.append(bias_val)
    else:
        # Run without metadynamics
        simulation.step(total_steps)

    simulation.saveState(str(output_dir / "final.xml"))
    print("✔ MD + biasing finished\n")

    # Remove DCDReporter and force garbage collection to finalize file
    simulation.reporters.remove(dcd)
    import gc

    del dcd
    gc.collect()

    if meta is not None:
        # Save the bias array for this run
        bias_array = np.array(bias_list)
        bias_file = output_dir / "bias_for_run.npy"
        np.save(str(bias_file), bias_array)
        print(
            f"[INFO] Saved bias array for this run to {bias_file} (length: {len(bias_array)})"
        )

    return dcd_filename


def feature_extraction(dcd_path, pdb_path):
    """Extract features from trajectory for MSM analysis."""
    print("Stage 4/5  –  featurisation + clustering ...")

    # Load the trajectory and compute φ dihedral angles
    t = md.load(dcd_path, top=pdb_path)
    print("Number of frames loaded:", t.n_frames)
    phi_vals, _ = md.compute_phi(t)
    phi_vals = phi_vals.squeeze()
    X = np.cos(phi_vals)
    X = X.reshape(-1, 1)

    kmeans = MiniBatchKMeans(n_clusters=40, random_state=0).fit(X)
    states = kmeans.labels_
    print("✔ Clustering done\n")
    return states


def build_transition_model(states, bias=None):
    """Build transition model from clustered states."""
    print("Stage 5/5  –  Markov model ...")

    tau = 20  # frames → 40 ps
    C = defaultdict(float)
    kT = 0.593  # kcal/mol at 300K
    F_est = 0.0  # For now, can be improved later
    n_transitions = len(states) - tau
    if bias is not None and len(bias) != len(states):
        raise ValueError(
            f"Bias array length ({len(bias)}) does not match number of states ({len(states)})"
        )
    for i in range(n_transitions):
        if bias is not None:
            w_t = np.exp((bias[i] - F_est) / kT)
        else:
            w_t = 1.0
        C[(states[i], states[i + tau])] += w_t

    # Dense count matrix → row-normalised transition matrix
    n = np.max(states) + 1
    Cmat = np.zeros((n, n))
    for (i, j), w in C.items():
        Cmat[i, j] = w

    T = (Cmat.T / Cmat.sum(axis=1)).T  # row-stochastic

    # Stationary distribution (left eigenvector of T)
    evals, evecs = np.linalg.eig(T.T)
    pi = np.real_if_close(evecs[:, np.argmax(evals)].flatten())
    pi /= pi.sum()
    DG = -kT * np.log(pi)  # 0.593 kcal/mol ≈ kT at 300 K

    print("✔ Finished – free energies (kcal/mol) written to DG array")
    return DG


def relative_energies(DG):
    """Calculate relative energies."""
    return DG - np.min(DG)


def plot_DG(DG):
    """Plot free energy profile."""
    plt.figure()
    plt.bar(np.arange(len(DG)), DG, color="blue")
    plt.xlabel("State Index")
    plt.ylabel("Free Energy (kcal/mol)")
    plt.title("Free Energy Profile")
    plt.tight_layout()
    plt.show()
