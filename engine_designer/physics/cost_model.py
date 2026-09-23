"""
CER-style engine cost estimate: a recurring per-unit `cost` and an R&D
`entryCost`, both for the RP-1 career economy.

EXPORT-TIME ONLY - nothing here feeds EngineDesign.compute(), so no validate.py
spot check moves. It turns the `relative_cost_factor` fields that already sit on
every materials / injectors / turbopump-tech / controller-tech entry (tracked
but, until now, never combined) into an actual number, driven by the computed
dry mass, chamber pressure, cycle complexity and chamber count.

`Engine_Configs/` carries no `entryCost` / `cost` (RP-1 installs those via its
own patches), so the calibration anchors are this project's own gating files:
  H3-250K   ~1.4 MN kerolox GG, ~500 kg dry  ->  entryCost 15000 / cost 20
  H4-250K   ~1.5 MN kerolox GG               ->  entryCost 18000 / cost 25
  TR341     lunar-lander pressure-fed thruster ->  entryCost 5000  / cost 5
All coefficients are Tier 3 - trust the ordering (heavier / higher-Pc /
more-complex-cycle / pricier-material -> costs more), not the exact funds.
"""
from . import controller_tech, injectors, materials, turbopump_tech

COST_BASE = 0.33               # tuned so a ~1.4 MN / ~500 kg kerolox GG lands near cost 20
MASS_EXP = 0.55
PC_REF_PA = 7.0e6
PC_COST_EXP = 0.30
COST_BY_CYCLE = {
    "pressure_fed": 0.7,
    "gas_generator": 1.0,
    "tap_off": 1.1,
    "expander": 1.3,
    "electric_pump": 1.2,
    "frsc": 1.8,
    "orsc": 2.2,
    "ffsc": 2.6,
}
_CYCLE_FALLBACK = 1.0

ENTRY_COST_MULT = 730.0        # entryCost = cost x this x cycle R&D factor
ENTRY_CYCLE_EXTRA = {
    "frsc": 1.5,
    "orsc": 2.0,
    "ffsc": 2.5,
    "expander": 1.3,
    "tap_off": 1.15,
    "electric_pump": 1.2,
}


def _blend(f):
    """Damp a relative_cost_factor around its neutral value 1.0 so an exotic
    material / injector / turbopump doesn't swing cost 2x on its own."""
    return 0.5 + 0.5 * f


def estimate_cost(design, result):
    """Return dict(cost, entry_cost) - integers, in RP-1 career funds."""
    m = max(result.get("computed_dry_mass_kg", 0.0), 1.0)
    mat = materials.MATERIALS[design.material_key].relative_cost_factor
    inj = injectors.INJECTORS[design.injector_type].relative_cost_factor
    tp = turbopump_tech.TURBOPUMP_TECHS[design.turbopump_tech_key].relative_cost_factor
    ctl = controller_tech.CONTROLLER_TECHS[design.controller_tech_key].relative_cost_factor
    chambers = getattr(design, "chamber_count", 1)

    cost = (COST_BASE
            * m ** MASS_EXP
            * COST_BY_CYCLE.get(design.cycle, _CYCLE_FALLBACK)
            * (design.chamber_pressure_pa / PC_REF_PA) ** PC_COST_EXP
            * _blend(mat) * _blend(inj) * _blend(tp) * _blend(ctl)
            * max(1, chambers))
    entry = cost * ENTRY_COST_MULT * ENTRY_CYCLE_EXTRA.get(design.cycle, 1.0)
    return {"cost": max(1, round(cost)), "entry_cost": max(1, round(entry))}


if __name__ == "__main__":
    from .design import EngineDesign

    def c(pair, cycle, **kw):
        d = EngineDesign(propellant_pair=pair, cycle=cycle, **kw)
        return estimate_cost(d, d.compute())

    # Ballpark envelopes (see module docstring for the anchors).
    kerolox_gg = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6,
                    target_vac_thrust_n=1.4e6)          # H3/H4-class
    big_orsc = c("LOX/RP-1", "orsc", chamber_pressure_pa=25e6, mixture_ratio=2.7,
                  target_vac_thrust_n=4.0e6)
    thruster = c("N2O4/MMH", "pressure_fed", chamber_pressure_pa=0.8e6,
                  injector_type="impinging", target_vac_thrust_n=1.5e4)
    print(f"  kerolox GG (~1.4 MN):  cost {kerolox_gg['cost']:>5}  entryCost {kerolox_gg['entry_cost']:>8}")
    print(f"  big ORSC   (~4 MN):    cost {big_orsc['cost']:>5}  entryCost {big_orsc['entry_cost']:>8}")
    print(f"  small thruster:        cost {thruster['cost']:>5}  entryCost {thruster['entry_cost']:>8}")
    assert 8 <= kerolox_gg["cost"] <= 60, kerolox_gg
    assert 6000 <= kerolox_gg["entry_cost"] <= 40000, kerolox_gg
    assert big_orsc["cost"] > kerolox_gg["cost"] > thruster["cost"]
    assert big_orsc["entry_cost"] > kerolox_gg["entry_cost"] > thruster["entry_cost"]
    assert 1 <= thruster["cost"] <= 15, thruster

    # Monotonicity: heavier / higher-Pc / pricier-material -> higher cost.
    base = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6, target_vac_thrust_n=1e6)
    heavy = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6, target_vac_thrust_n=4e6)
    hipc = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=16e6, target_vac_thrust_n=1e6)
    exotic = c("LOX/RP-1", "gas_generator", chamber_pressure_pa=8e6, target_vac_thrust_n=1e6,
                material_key="rhenium_iridium")
    assert heavy["cost"] > base["cost"] and hipc["cost"] > base["cost"]
    assert exotic["cost"] > base["cost"]

    print("cost_model.py self-checks: OK")
