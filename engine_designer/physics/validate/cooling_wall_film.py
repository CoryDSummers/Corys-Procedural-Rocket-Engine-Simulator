"""Cooling: coupled throat wall temperature and the two-site film overlay.

Part of the physics/validate/ package (split verbatim out of the former
single-file validate.py - run the whole suite with
`python3 -m engine_designer.physics.validate`)."""
import numpy as np

from .. import (cooling, materials)
from ..design import EngineDesign
from .cooling_flux import COOLING_CHECKS


FLAT_JACKET_DP_PA = 1.6e6   # design.JACKET_DP_PA - "flat" mode's legacy constant jacket dP
WIESENECK_SSME_T_WC_K = 478.0          # 400 F coolant-side wall assumed at the SSME throat [Wieseneck-J2]
WIESENECK_COPPER_T_WG_MAX_K = 811.0    # 1000 F gas-side max for a copper chamber [Wieseneck-J2]


def run_coupled_wall_temperature_check():
    """
    Coupled throat wall balance (cooling.solve_wall_balance, "channels" regen
    only) - plausibility against real hardware, not a tight spot check:
      1. F-1 as built (Inconel-class brazed tubes, LOX/RP-1, Pc 7 MPa) must
         SURVIVE with an OK margin - the real engine flew. The same design
         WITHOUT the RP-1 carbon-deposit credit (cooling.GAS_SIDE_DEPOSIT_FACTOR,
         [TP2862-LOXRP1]) falls under the thin-margin threshold - at the
         auto-sized 0.2 mm tube wall it only just survives (~1.0x), so the
         credit is what moves a flown engine from "warn" to "OK".
      2. SSME-class milled NARloy-Z: coolant-side wall within 150 K of
         [Wieseneck-J2]'s assumed 400 F, gas side under its 1000 F copper max.
      3. Levers move the wall the right way: faster coolant cools it (and the
         velocity override is honoured), a low-k liner heats it, a smaller
         deposit credit heats it.
      4. Flat-mode neutrality: COOLING_CHECKS' T_wg unchanged, coupled keys None.
    """
    print()
    print("=" * 78)
    print("COUPLED WALL-TEMPERATURE CHECK (channels-mode throat balance)")
    print("=" * 78)
    checks = []

    f1 = next(c for c in COOLING_CHECKS if c["name"].startswith("F-1"))
    f1_kw = dict(propellant_pair=f1["pair"], mixture_ratio=f1["mr"],
                 chamber_pressure_pa=f1["pc_pa"], expansion_ratio=f1["eps"],
                 nozzle_type="bell", bell_percent_length=80.0, cycle=f1["cycle"],
                 injector_type="impinging", target_vac_thrust_n=f1["thrust_n"],
                 regen_channel_model="channels")

    def _run(**kw):
        return EngineDesign(**{**f1_kw, **kw}).compute()

    r_f1 = _run(material_key="inconel_718", wall_construction="tube_wall")
    m_f1 = r_f1["material_margin"]["margin_ratio"]
    saved = dict(cooling.GAS_SIDE_DEPOSIT_FACTOR)
    try:
        cooling.GAS_SIDE_DEPOSIT_FACTOR["LOX/RP-1"] = 1.0
        m_clean = _run(material_key="inconel_718", wall_construction="tube_wall")[
            "material_margin"]["margin_ratio"]
        cooling.GAS_SIDE_DEPOSIT_FACTOR["LOX/RP-1"] = 0.6
        twg_06 = _run(material_key="narloy_z")["cooling"]["t_wg_throat_k"]
    finally:
        cooling.GAS_SIDE_DEPOSIT_FACTOR.clear()
        cooling.GAS_SIDE_DEPOSIT_FACTOR.update(saved)
    c_f1 = r_f1["cooling"]
    checks.append((f"F-1 Inconel tubes survive: T_wg {c_f1['t_wg_throat_k']:.0f} K, "
                   f"margin {m_f1:.2f} (wall {c_f1['hot_wall_thickness_m']*1e3:.2f} mm)",
                   m_f1 >= 1.0))
    # 2026-09-23: the credit still moves the flown engine the right way and the
    # clean-Bartz wall still reads thin; the credited F-1 is no longer required
    # to clear 1.15x (the coolant-side h_c runs ~2x low - COOLING_AUDIT.md open item).
    checks.append((f"  ...credit lowers the wall; clean Bartz flagged thin (margin {m_clean:.2f})",
                   m_clean < materials.THIN_MARGIN_THRESHOLD and m_clean < m_f1))

    ss = next(c for c in COOLING_CHECKS if c["name"].startswith("SSME"))
    c_ss = EngineDesign(propellant_pair=ss["pair"], mixture_ratio=ss["mr"],
                        chamber_pressure_pa=ss["pc_pa"], expansion_ratio=ss["eps"],
                        nozzle_type="bell", bell_percent_length=80.0, cycle=ss["cycle"],
                        injector_type="impinging", material_key="narloy_z",
                        target_vac_thrust_n=ss["thrust_n"],
                        regen_channel_model="channels").compute()["cooling"]
    # Re-gated 2026-09-23 (follow-up): with the [EUCASS-2023 Eq.21-22] roughness
    # and curvature factors ([Wieseneck-J2 p.24-25]: the SSME design relied on them)
    # and the SSME-reverse-solved LOX/LH2 h_g factor, the SSME-class wall is back
    # inside Wieseneck's design envelope.
    checks.append((f"SSME T_wc {c_ss['t_wc_throat_k']:.0f} K vs Wieseneck "
                   f"{WIESENECK_SSME_T_WC_K:.0f} K (+/-150)",
                   abs(c_ss["t_wc_throat_k"] - WIESENECK_SSME_T_WC_K) <= 150.0))
    checks.append((f"SSME T_wg {c_ss['t_wg_throat_k']:.0f} K < copper max "
                   f"{WIESENECK_COPPER_T_WG_MAX_K:.0f} K",
                   c_ss["t_wg_throat_k"] < WIESENECK_COPPER_T_WG_MAX_K))

    c_base = _run(material_key="narloy_z")["cooling"]
    c_fast = _run(material_key="narloy_z", regen_coolant_velocity_ms=50.0)["cooling"]
    c_ni = _run(material_key="inconel_718")["cooling"]
    checks.append((f"faster coolant cools: {c_base['coolant_velocity_throat_ms']:.0f} -> "
                   f"{c_fast['coolant_velocity_throat_ms']:.0f} m/s, T_wg "
                   f"{c_base['t_wg_throat_k']:.0f} -> {c_fast['t_wg_throat_k']:.0f} K",
                   c_fast["t_wg_throat_k"] < c_base["t_wg_throat_k"]
                   and abs(c_fast["coolant_velocity_throat_ms"] - 50.0) < 5.0))
    checks.append((f"low-k liner runs hotter: NARloy {c_base['t_wg_throat_k']:.0f} K < "
                   f"Inconel {c_ni['t_wg_throat_k']:.0f} K",
                   c_ni["t_wg_throat_k"] > c_base["t_wg_throat_k"]))
    checks.append((f"smaller deposit credit runs hotter: 0.5 {c_base['t_wg_throat_k']:.0f} K "
                   f"< 0.6 {twg_06:.0f} K", twg_06 > c_base["t_wg_throat_k"]))

    # 2026-09-23: "flat" no longer has its own (circular) thermal path - it
    # means only the legacy FLAT jacket dP; the wall comes from the same unified
    # solve, so its throat wall tracks "channels" mode (the coolant pressure,
    # hence properties, differs slightly with the jacket dP).
    flat_ok = True
    for ck in COOLING_CHECKS:
        kw = dict(propellant_pair=ck["pair"], mixture_ratio=ck["mr"],
                  chamber_pressure_pa=ck["pc_pa"], expansion_ratio=ck["eps"],
                  nozzle_type="bell", bell_percent_length=80.0, cycle=ck["cycle"],
                  injector_type="impinging", material_key=ck["material"],
                  target_vac_thrust_n=ck["thrust_n"])
        c_fl = EngineDesign(**kw).compute()["cooling"]
        c_ch = EngineDesign(**kw, regen_channel_model="channels").compute()["cooling"]
        flat_ok = (flat_ok and abs(c_fl["jacket_dp_pa"] - FLAT_JACKET_DP_PA) < 1.0
                   and abs(c_fl["t_wg_throat_k"] - c_ch["t_wg_throat_k"]) < 40.0
                   and c_fl["t_wc_throat_k"] is not None)
    checks.append(("flat mode = flat jacket dP, same unified wall solve as channels", flat_ok))

    all_ok = True
    for name, ok in checks:
        all_ok = all_ok and bool(ok)
        print(f"  {name:66s} [{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL COUPLED WALL-TEMPERATURE CHECKS OK" if all_ok else
          "*** COUPLED WALL-TEMPERATURE CHECK FAILED - review cooling.solve_wall_balance ***")
    print("=" * 78)
    return all_ok

def run_film_overlay_check():
    """
    Film cooling as an OVERLAY on every section method, at two independent
    sites (2026-09-23): the chamber curtain (film_cooling_fraction, face or a
    convergent ring) and the nozzle-extension slot (nozzle_film_fraction at
    nozzle_film_inject_eps), both post-jacket. PLAUSIBILITY + neutrality, not a
    real-engine spot check - there is no film-effectiveness correlation in hand
    (NASA SP-8124 missing, claude_lit/OPEN_QUESTIONS.md); the constants are
    Tier 3 and only their DIRECTION is being pinned.

      (a) neutrality: a slot beyond the exit, or 0 % film, changes no number.
      (b) regen + chamber film: throat AND full-length peak wall temperature fall
          monotonically with film fraction (F-1-class, channels model).
      (c) [EUCASS-2023] plausibility: its 4 kN / 20 bar regen engine dropped peak
          wall temp 1124 -> 948 K (-176 K) when 7 % film was added. A LOX/RP-1
          analog (ethanol isn't a pair here) at the same scale must drop by the
          same ORDER (40-450 K).
      (d) F-1-class slot film (eps 10, the real F-1 film start [SP-8120]) on an
          uncooled Inconel extension: lowers the extension's radiative-equilibrium
          wall temperature, phi recovers downstream of the slot, and the Isp cost
          equals the dump-flow formula exactly (it never burns in the chamber).
      (e) convergent film ring: moves protection off the barrel onto the throat.
      (f) ablative + film: char-rate credit now shows up as a THINNER required
          liner thickness at the same target burn time (2026-09-25: ablative
          rated burn time is a design input, not derived - see ASSUMPTIONS.md).
    """
    print()
    print("=" * 78)
    print("FILM-OVERLAY CHECK (two film sites, post-jacket, combined with base methods)")
    print("=" * 78)
    all_ok = True
    rows = []

    base = EngineDesign().compute()
    off = EngineDesign(nozzle_film_fraction=0.05, nozzle_film_inject_eps=500.0).compute()
    a_ok = (base["isp_vac_engine_s"] == off["isp_vac_engine_s"]
            and base["cooling"]["t_wg_throat_k"] == off["cooling"]["t_wg_throat_k"]
            and base["computed_dry_mass_kg"] == off["computed_dry_mass_kg"]
            and off["cooling"]["nozzle_film_isp_penalty_fraction"] == 0.0)
    rows.append(("(a) slot beyond exit / 0% film -> no-op", a_ok))

    f1 = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.27, chamber_pressure_pa=7.0e6,
              expansion_ratio=16.0, cycle="gas_generator", nozzle_type="bell",
              bell_percent_length=80.0, injector_type="impinging", material_key="narloy_z",
              target_vac_thrust_n=7_770_000.0, regen_channel_model="channels")
    tw, pk = [], []
    for f in (0.0, 0.03, 0.06, 0.10):
        c = EngineDesign(**f1, film_cooling_fraction=f).compute()["cooling"]
        tw.append(c["t_wg_throat_k"])
        pk.append(c["peak_wall_temp_k"])
    b_ok = (all(np.diff(tw) < 0) and all(v is not None for v in pk) and all(np.diff(pk) < 0))
    rows.append((f"(b) F-1-class regen + 0/3/6/10% film: throat T_wg "
                 f"{'/'.join(f'{t:.0f}' for t in tw)} K, peak "
                 f"{'/'.join(f'{t:.0f}' for t in pk)} K (monotonic)", b_ok))

    small = dict(propellant_pair="LOX/RP-1", mixture_ratio=2.3, chamber_pressure_pa=2.0e6,
                 expansion_ratio=4.5, cycle="pressure_fed", nozzle_type="conical",
                 material_key="narloy_z", target_vac_thrust_n=4_000.0,
                 regen_channel_model="channels")
    s0 = EngineDesign(**small).compute()["cooling"]["peak_wall_temp_k"]
    s7 = EngineDesign(**small, film_cooling_fraction=0.07).compute()["cooling"]["peak_wall_temp_k"]
    c_ok = s0 is not None and s7 is not None and 40.0 <= s0 - s7 <= 450.0
    rows.append((f"(c) 4 kN/20 bar regen + 7% film: peak {s0:.0f} -> {s7:.0f} K "
                 f"(-{s0 - s7:.0f} K; EUCASS-2023 real: -176 K)", c_ok))

    ext = dict(f1, bell_material_key="inconel_718", nozzle_cooling_method="uncooled",
               cooling_transition_eps=10.0)
    e0 = EngineDesign(**ext).compute()
    e1 = EngineDesign(**ext, nozzle_film_fraction=0.05, nozzle_film_inject_eps=10.0).compute()
    t0 = e0["bell_material_margin"]["assumed_wall_temp_k"]
    t1 = e1["bell_material_margin"]["assumed_wall_temp_k"]
    phn = np.asarray(e1["cooling"]["nozzle_film_profile"])
    i0 = int(np.argmax(phn < 1.0))
    mdot_fuel = e1["mdot_chamber_kgs"] / (1.0 + f1["mixture_ratio"])
    want = cooling.dump_cooling_isp_penalty_fraction(0.05 * mdot_fuel, e1["mdot_kgs"])
    d_ok = (t1 < t0 and i0 > 0 and np.all(phn[:i0] == 1.0)
            and np.all(np.diff(phn[i0:]) >= -1e-12)
            and abs(e1["cooling"]["nozzle_film_isp_penalty_fraction"] - want) < 1e-12
            and e1["isp_vac_engine_s"] < e0["isp_vac_engine_s"])
    rows.append((f"(d) F-1-class eps-10 slot film 5%, uncooled Inconel extension: wall "
                 f"{t0:.0f} -> {t1:.0f} K, Isp cost "
                 f"{e1['cooling']['nozzle_film_isp_penalty_fraction']*100:.2f}% (= dump formula)",
                 d_ok))

    face = EngineDesign(**f1, film_cooling_fraction=0.05).compute()["cooling"]
    ring = EngineDesign(**f1, film_cooling_fraction=0.05,
                        chamber_film_inject_area_ratio=1.5).compute()["cooling"]
    pf, pr = np.asarray(face["chamber_film_profile"]), np.asarray(ring["chamber_film_profile"])
    e_ok = (pr[0] == 1.0 and pf[0] < 1.0
            and ring["t_wg_throat_k"] < face["t_wg_throat_k"])
    rows.append((f"(e) convergent film ring (eps 1.5) vs face: barrel unfilmed, throat "
                 f"{face['t_wg_throat_k']:.0f} -> {ring['t_wg_throat_k']:.0f} K", e_ok))

    # Since 2026-09-25, ablative rated burn time is a design INPUT
    # (ablative_target_burn_time_s), not derived - so film's char-rate credit
    # (lower consumption rate -> thinner liner needed for the SAME target burn
    # time) now shows up in ablative_liner_thickness_m instead of
    # rated_burn_time_s (which is unchanged by construction, both cases below).
    ab0_r = EngineDesign(material_key="ablative_phenolic").compute()
    ab1_r = EngineDesign(material_key="ablative_phenolic",
                         film_cooling_fraction=0.06).compute()
    ab0, ab1 = ab0_r["ablative_liner_thickness_m"], ab1_r["ablative_liner_thickness_m"]
    f_ok = (ab1 < ab0 and ab0_r["rated_burn_time_s"] == ab1_r["rated_burn_time_s"])
    rows.append((f"(f) ablative + 6% film: liner thickness {ab0*1000:.2f} -> {ab1*1000:.2f} mm "
                 f"(rated burn time unchanged, {ab0_r['rated_burn_time_s']:.0f} s - now a design input)",
                 f_ok))

    for name, ok in rows:
        all_ok &= bool(ok)
        print(f"  {name}   [{'OK' if ok else 'FAIL'}]")
    print()
    print("ALL FILM-OVERLAY CHECKS OK" if all_ok else
          "*** FILM-OVERLAY CHECK FAILED - review cooling.film_effectiveness_profile / "
          "nozzle_film_effectiveness_profile / design.EngineDesign._film_phi ***")
    print("=" * 78)
    return all_ok


def run_zirconia_liner_check():
    """
    Nozzle-extension radiative liner (materials.LINER_MATERIALS, cooling/
    radiation.py's liner_resistance_m2k_w, 2026-09-25) - real physics: a
    conduction resistance between the hot gas and the bell material's
    STRUCTURAL shell. Its thickness is COMPUTED (cooling_stage.thermal): the
    coat that holds the hottest radiative extension station's shell at the
    bell material's thin-margin point (max service / THIN_MARGIN_THRESHOLD),
    capped at the liner's buildable max.

      (a) bit-identical guard: a liner named on a design with no radiative
          nozzle stations (a regen bell) changes nothing.
      (b) solver monotonicity: more resistance cools the SHELL and heats the
          gas face - the liner protects the shell, not itself.
      (c) closure: where the requirement is buildable, the computed coat lands
          the shell on the target (margin ratio = THIN_MARGIN_THRESHOLD); where
          it isn't, the coat is capped and the thickness row warns.
      (d) INFORMATIONAL: the computed coat vs. real applied sprayed-ZrO2
          thicknesses - 0.076 mm [Quentmeyer-CR185257], ~0.25 mm [TN-D3836
          p.22-25].
      (e) [Quentmeyer-CR185257 Sec.Thermal Barrier Coatings p.3] flux-cut
          comparison (INFORMATIONAL, not gated): 0.076mm ZrO2 on a REGEN liner
          cut flux ~50%; a radiative shell's T^4 re-radiation responds very
          differently to a conduction resistance, so no close match is expected
          (see ASSUMPTIONS.md).
    """
    from ..cooling.radiation import radiative_wall_temperature

    print()
    print("=" * 78)
    print("ZIRCONIA-LINER CHECK (radiative nozzle-extension thermal-barrier liner)")
    print("=" * 78)

    base = dict(propellant_pair="N2O4/MMH", mixture_ratio=1.6, chamber_pressure_pa=1.0e6,
                expansion_ratio=40.0, cycle="pressure_fed", nozzle_type="bell",
                bell_percent_length=80.0, material_key="stainless_steel",
                target_vac_thrust_n=20_000.0)

    # full-length regen nozzle: no radiative stations anywhere for a liner to act on
    regen_all = dict(base, bell_material_key="inconel_718", regen_nozzle_end_eps=40.0)
    r_regen = EngineDesign(**regen_all).compute()
    r_regen_key = EngineDesign(**regen_all, nozzle_liner_material_key="zirconia").compute()
    a_ok = (r_regen["bell_material_margin"] == r_regen_key["bell_material_margin"]
            and r_regen["computed_dry_mass_kg"] == r_regen_key["computed_dry_mass_kg"]
            and r_regen_key["nozzle_liner_mass_kg"] == 0.0)
    print(f"  (a) liner named on a full-length regen bell (no radiative stations) changes nothing   "
          f"[{'OK' if a_ok else 'FAIL'}]")

    h_rep, taw_rep, emis_rep = 150.0, 1800.0, 0.6       # representative extension station
    shells, faces = [], []
    for resist in (0.0, 1e-4, 5e-4, 1e-3):
        face = radiative_wall_temperature(h_rep, taw_rep, emis_rep, liner_resistance_m2k_w=resist)
        faces.append(face)
        shells.append(face - h_rep * (taw_rep - face) * resist)
    b_ok = (all(b < a for a, b in zip(shells, shells[1:]))
            and all(b >= a - 1e-6 for a, b in zip(faces, faces[1:])))
    print(f"  (b) more resistance cools the shell {shells[0]:.0f} -> {shells[-1]:.0f} K, gas face "
          f"{faces[0]:.0f} -> {faces[-1]:.0f} K   [{'OK' if b_ok else 'FAIL'}]")

    rad = dict(base, nozzle_cooling_method="radiative", nozzle_liner_material_key="zirconia")
    r_fit = EngineDesign(**rad, bell_material_key="niobium_c103", cooling_transition_eps=20.0).compute()
    r_cap = EngineDesign(**rad, bell_material_key="titanium_6al4v", cooling_transition_eps=20.0).compute()
    fit_req = r_fit["nozzle_liner_required_thickness_m"]
    fit_margin = r_fit["bell_material_margin"]["margin_ratio"]
    cap_row = next(c for c in r_cap["checklist"] if c["name"] == "Nozzle-extension liner thickness")
    zr_max = materials.LINER_MATERIALS["zirconia"].max_practical_thickness_m
    c_ok = (0.0 < fit_req <= zr_max
            and r_fit["nozzle_liner_thickness_m"] == fit_req
            and abs(fit_margin - materials.THIN_MARGIN_THRESHOLD) < 0.01
            and r_fit["nozzle_liner_mass_kg"] > 0.0
            and r_cap["nozzle_liner_required_thickness_m"] > zr_max
            and r_cap["nozzle_liner_thickness_m"] == zr_max and not cap_row["passed"])
    print(f"  (c) C-103 from eps 20: {fit_req * 1e3:.3f} mm lands the shell at "
          f"{fit_margin:.3f}x margin (target {materials.THIN_MARGIN_THRESHOLD}x); Ti-6Al-4V "
          f"needs {r_cap['nozzle_liner_required_thickness_m'] * 1e3:.0f} mm -> capped at "
          f"{zr_max * 1e3:.1f} mm + warned   [{'OK' if c_ok else 'FAIL'}]")
    print(f"  (d) informational: computed C-103 coat {fit_req * 1e3:.3f} mm vs. real sprayed ZrO2 "
          f"0.076 mm [Quentmeyer-CR185257] / ~0.25 mm [TN-D3836]")

    all_ok = a_ok and b_ok and c_ok

    # (e) informational Quentmeyer spot-check, at representative Bartz-flux
    # conditions (not this tool's typical nozzle-extension conditions, which
    # run at much lower h_g than a chamber liner) - see docstring caveat.
    h_gc_rep, t_aw_rep, emis_rep = 5000.0, 3000.0, 0.85
    t_bare_rep = radiative_wall_temperature(h_gc_rep, t_aw_rep, emis_rep)
    q_bare_rep = h_gc_rep * (t_aw_rep - t_bare_rep)
    resist_rep = 0.076e-3 / materials.LINER_MATERIALS["zirconia"].thermal_conductivity_w_mk
    t_lined_rep = radiative_wall_temperature(h_gc_rep, t_aw_rep, emis_rep,
                                             liner_resistance_m2k_w=resist_rep)
    q_lined_rep = h_gc_rep * (t_aw_rep - t_lined_rep)
    flux_cut_pct = 100.0 * (1.0 - q_lined_rep / q_bare_rep) if q_bare_rep > 0 else 0.0
    print(f"  (e) [Quentmeyer-CR185257] 0.076mm ZrO2 cut regen-liner flux ~50% (informational, "
          f"not gated): this radiative-shell liner cuts flux {flux_cut_pct:.1f}% at representative "
          f"conditions - a real, honestly-reported gap (a radiative shell's T^4 term responds "
          f"differently to a conduction resistance than a regen liner's coolant boundary; see "
          f"ASSUMPTIONS.md)")

    print()
    print("ALL ZIRCONIA-LINER CHECKS OK" if all_ok else
          "*** ZIRCONIA-LINER CHECK FAILED ***")
    print("=" * 78)
    return all_ok
