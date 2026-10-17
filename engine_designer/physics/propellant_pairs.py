"""Propellant-pair VARIANTS: a pair that is another pair's propellants in a
different STATE (today: subcooled / densified LOX/RP-1), with its own baked
equilibrium + coolant tables, densities, inlet temperatures and RealFuels
resources, but the SAME combustion/injector/turbine physics as its base pair.

A leaf module (no imports) so every per-pair table in physics/ - including the
cooling package, which avoids importing combustion.py - can alias a variant
onto its base pair with ``alias_variants(table)`` instead of hand-copying an
entry per dict, and check-sites can compare ``base_pair(pair)`` instead of the
raw string.

What a variant does NOT inherit (each has its own explicit entry): density
(combustion.PROPELLANT_DENSITIES, cooling COOLANT_DENSITY_KG_M3), the equilibrium
and coolant tables (property_data/), the jacket/oxidizer inlet temperatures
(design/constants.py), the pump-suction inlet temperature
(design/suction_stage.PAIR_AUTO_PROPELLANT_TEMP_K) and the RealFuels resource
names (export/cfg_writer._RF_PROPELLANTS).
"""

# variant pair key -> base pair key
PAIR_VARIANT_OF = {
    # Densified LOX at 66 K + chilled RP-1 at 266 K (Falcon 9 "Full Thrust"
    # practice, ~-207 C / -7 C) - see ASSUMPTIONS.md "Subcooled LOX/RP-1".
    "LOX/RP-1 (subcooled)": "LOX/RP-1",
}


def base_pair(pair):
    """The pair whose combustion/injector/turbine physics `pair` shares
    (itself for a non-variant)."""
    return PAIR_VARIANT_OF.get(pair, pair)


def alias_variants(table):
    """Add every variant whose base pair is in `table` and that has no entry of
    its own, pointing at the base pair's value. Returns `table` (mutated)."""
    for variant, base in PAIR_VARIANT_OF.items():
        if base in table and variant not in table:
            table[variant] = table[base]
    return table


if __name__ == "__main__":
    t = alias_variants({"LOX/RP-1": 1, "LOX/LH2": 2})
    assert t["LOX/RP-1 (subcooled)"] == 1 and base_pair("LOX/RP-1 (subcooled)") == "LOX/RP-1"
    assert base_pair("LOX/LH2") == "LOX/LH2"
    t2 = alias_variants({"LOX/RP-1": 1, "LOX/RP-1 (subcooled)": 9})
    assert t2["LOX/RP-1 (subcooled)"] == 9      # an explicit entry is never overwritten
    print("propellant_pairs self-test OK")
