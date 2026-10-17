"""Rated burn time = duty target capped by a physical life limit (2026-10-16,
physics/burn_time.py, design/rollup_stage.py).

(a) SPOT CHECK - every real engine in validation_engines/ with a regen or
    radiative wall, given its REAL RealismOverhaul ratedBurnTime as the duty
    target and its real RP-1 tech node, must carry that duty UNCAPPED: the
    wall-temperature life (burn_time.thermal_life_s) / LIFE_FACTOR >= the real
    rating. burn_time.THERMAL_LIFE_MARGIN_REF was reverse-solved on exactly this
    set (RD-180 binds), so this pins the calibration.
(b) Report-only: the corpus default duty (target 0) vs each real rating - the
    RATED_FIT scatter is large (rms 0.64 in ln for boosters), so it is shown,
    not gated.
(c) Direction: the same design with a hotter worst station (a lower-limit
    extension material) gets a shorter wall life, nozzle film a longer one; a target far past the life is capped,
    flagged in the checklist, and limited by "wall_temperature".
(d) An ablative chamber carries its target by construction (rated == target).

Part of the physics/validate/ package - run the whole suite with
`python3 -m engine_designer.physics.validate`."""
import json
from pathlib import Path

from .. import burn_time
from ..design import EngineDesign

_ENGINES = Path(__file__).resolve().parents[2] / "validation_engines" / "engines"

# validation engine: (RO config, real ratedBurnTime s, RP-1 tech node) - from
# catalog/testflight_corpus.json and catalog/rp1_snapshot.json.
REAL_DUTY = {
    "F-1": ("F-1-1.5M", 165.0, "orbitalRocketry1967"),
    "J-2": ("J-2-200K", 500.0, "improvedHydrolox"),
    "RS-25": ("RS-25", 480.0, "FRSC1981"),
    "RD-180": ("RD-180", 255.0, "stagedCombustion1998"),
    "Merlin-1D": ("Merlin1D", 180.0, "orbitalRocketry2009"),
    "RL10A-3-3": ("RL10A-3-3", 470.0, "improvedHydrolox"),
    "Rutherford": ("Rutherford-SL", 150.0, "orbitalRocketry2014"),
    "Vulcain": ("Vulcain", 580.0, "hydrolox1992"),
    "Aestus": ("Aestus", 1110.0, "orbitalRocketry1992"),
    "Raptor-2": ("Raptor-2", 360.0, ""),          # RO gates it at no RP-1 node
}


def _load(name):
    return EngineDesign.from_dict(json.loads((_ENGINES / f"{name}.json").read_text()))


def run_burn_time_check():
    print("\n=== Rated burn time: duty target vs life limit (physics/burn_time.py) ===")
    ok = True
    for name, (cfg, real_s, node) in REAL_DUTY.items():
        d = _load(name)
        d.tech_node = node
        d.rated_burn_time_target_s = real_s
        r = d.compute()
        wall = next((x for x in r["burn_time_limits"] if x["key"] == "wall_temperature"), None)
        carried = abs(r["rated_burn_time_s"] - real_s) < 1e-6
        d.rated_burn_time_target_s = 0.0
        auto = d.compute()["duty_default_s"]
        ok &= carried
        print(f"  {name:11s} ({cfg}, real {real_s:5.0f} s): rated {r['rated_burn_time_s']:6.0f} s, "
              f"wall margin {wall['margin']:.2f} -> allowable {wall['allowable_rated_s']:7.0f} s; "
              f"corpus default duty {auto:5.0f} s  [{'OK' if carried else 'FAIL'}]")

    # (c) direction: a hotter wall shortens life; a target past it is capped + flagged.
    base = dict(propellant_pair="LOX/RP-1", cycle="gas_generator", chamber_pressure_pa=7.0e6)
    cool = EngineDesign(**base).compute()
    hot = EngineDesign(**dict(base, bell_material_key="stainless_steel")).compute()
    film = EngineDesign(**dict(base, nozzle_film_fraction=0.03)).compute()
    life = lambda r: next(x["life_s"] for x in r["burn_time_limits"] if x["key"] == "wall_temperature")
    dir_ok = life(hot) < life(cool) < life(film)
    big = EngineDesign(**dict(base, rated_burn_time_target_s=life(cool))).compute()
    cap_ok = (big["rated_limited_by"] == "wall_temperature"
              and big["rated_burn_time_s"] < life(cool)
              and any(c["name"] == "Rated burn time vs. life limit" and not c["passed"]
                      for c in big["checklist"]))
    ok &= dir_ok and cap_ok
    print(f"  Wall life follows the hottest station: stainless extension < Inconel 718 "
          f"< 718 + 3 % nozzle film: {life(hot):.0f} < {life(cool):.0f} < {life(film):.0f} s  "
          f"[{'OK' if dir_ok else 'FAIL'}]")
    print(f"  Target = the wall life ({life(cool):.0f} s) is capped at life / {burn_time.LIFE_FACTOR:.0f} "
          f"= {big['rated_burn_time_s']:.0f} s and flagged  [{'OK' if cap_ok else 'FAIL'}]")

    # (d) ablative carries its target by construction.
    abl = EngineDesign(propellant_pair="N2O4/MMH", cycle="pressure_fed", chamber_pressure_pa=0.8e6,
                       injector_type="impinging", material_key="ablative_phenolic",
                       rated_burn_time_target_s=750.0).compute()
    abl_ok = abs(abl["rated_burn_time_s"] - 750.0) < 1e-9 and abl["rated_limited_by"] == "target"
    ok &= abl_ok
    print(f"  Ablative chamber carries its 750 s target (liner "
          f"{abl['ablative_liner_thickness_m'] * 1000:.1f} mm)  [{'OK' if abl_ok else 'FAIL'}]")
    print("ALL BURN-TIME CHECKS OK" if ok else "BURN-TIME CHECKS FAILED")
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if run_burn_time_check() else 1)
