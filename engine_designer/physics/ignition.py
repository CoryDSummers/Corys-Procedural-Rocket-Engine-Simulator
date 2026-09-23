"""
Ignition-system dropdown catalog. Explicit choice, replacing v1's hardcoded
per-propellant-pair lookup in export/cfg_writer.py. Picking a propellant
pair suggests a sensible default (see default_for_pair); an implausible
combination gets a warning, not a block, matching the materials/injectors
philosophy.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class IgnitionSystem:
    key: str
    display_name: str
    rf_ignitor_resources: tuple  # tuple of (resource_name, amount)
    forces_single_ignition: bool
    plausible_pairs: tuple  # empty tuple = plausible for anything


IGNITION_SYSTEMS = {
    "tea_teb": IgnitionSystem(
        key="tea_teb",
        display_name="TEA-TEB pyrophoric slug",
        rf_ignitor_resources=(("ElectricCharge", 0.5), ("TEATEB", 1)),
        forces_single_ignition=False,
        plausible_pairs=("LOX/RP-1",),
    ),
    "spark_torch": IgnitionSystem(
        key="spark_torch",
        display_name="Spark torch igniter (electric)",
        rf_ignitor_resources=(("ElectricCharge", 1.0),),
        forces_single_ignition=False,
        plausible_pairs=("LOX/RP-1", "LOX/LH2", "LOX/CH4"),
    ),
    "hypergolic_self_ignite": IgnitionSystem(
        key="hypergolic_self_ignite",
        display_name="Hypergolic self-ignition",
        rf_ignitor_resources=(("ElectricCharge", 0.05),),  # small charge for valve sequencing only
        forces_single_ignition=False,
        plausible_pairs=("N2O4/MMH", "Aerozine-50/NTO"),
    ),
    "pyrotechnic": IgnitionSystem(
        key="pyrotechnic",
        display_name="Pyrotechnic squib (single-shot)",
        rf_ignitor_resources=(("ElectricCharge", 0.2),),
        forces_single_ignition=True,
        plausible_pairs=(),
    ),
    "catalytic": IgnitionSystem(
        key="catalytic",
        display_name="Catalytic decomposition (no separate igniter)",
        rf_ignitor_resources=(("ElectricCharge", 0.01),),  # valve sequencing only, matching
                                                            # MR-80B's real amount=0.005
        forces_single_ignition=False,
        plausible_pairs=("Hydrazine", "H2O2"),
    ),
}

DEFAULT_FOR_PAIR = {
    "LOX/RP-1": "tea_teb",
    "LOX/LH2": "spark_torch",
    "LOX/CH4": "spark_torch",
    "N2O4/MMH": "hypergolic_self_ignite",
    "Aerozine-50/NTO": "hypergolic_self_ignite",
    "Hydrazine": "catalytic",
    "H2O2": "catalytic",
}


def available_ignition_systems():
    return list(IGNITION_SYSTEMS.keys())


def default_for_pair(pair):
    return DEFAULT_FOR_PAIR.get(pair, "spark_torch")


def plausibility_warning(ignition_key, propellant_pair):
    sysdef = IGNITION_SYSTEMS[ignition_key]
    if sysdef.plausible_pairs and propellant_pair not in sysdef.plausible_pairs:
        return (f"{sysdef.display_name} is an unusual choice for {propellant_pair} "
                f"(typically used with {', '.join(sysdef.plausible_pairs)}).")
    return None
