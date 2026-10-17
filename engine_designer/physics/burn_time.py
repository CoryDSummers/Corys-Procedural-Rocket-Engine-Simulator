"""
Rated burn time (the engine's qualified duty) capped by a physical life limit,
and the RO-corpus fits behind the exported TestFlight burn times.

How RealismOverhaul's TestFlight reads these (TestFlight_Generic_Engines.cfg):
the per-second failure chance is (1 - cycleReliability) / ratedBurnTime, and
the `cycle` curve is 1x until ratedBurnTime + 5 s, 2x at testedBurnTime and
100x at 2.5 x testedBurnTime. So ratedBurnTime = the mission duty the engine is
qualified for, testedBurnTime = the longest SINGLE burn demonstrated.

Model (real engines are designed TO a duty, and the hardware life covers it
with a factor - [SP-8110 Sec.2.4.1] / [ASR72-238] "SF 4 on cycles and on creep
life fraction"):

  duty target   EngineDesign.rated_burn_time_target_s; 0 = the RO-corpus fit for
                this engine's role (booster / upper stage / pressure-fed),
                vacuum thrust and era (RATED_FIT, over the real ratedBurnTime of
                every dated liquid-bipropellant RO config).
  life limit    the longest single burn the hardware survives. Round A has ONE
                mechanism - the wall-temperature margin:
                  life = LIFE_FACTOR x duty_ref x margin ** THERMAL_LIFE_EXPONENT
                anchored so a wall at THERMAL_LIFE_MARGIN_REF (reverse-solved on
                the real validation engines) carries the corpus duty with the
                cited life factor,
                and steepening with temperature at [Quentmeyer-TMX73665]'s
                copper-liner exponent (cycles ~ T_gw ** -1/0.205, a cycles-vs-
                temperature law used here as a life-vs-temperature proxy - Tier
                3 transfer, see ASSUMPTIONS.md). Ablative walls instead size
                their char liner to the target (SP-8124), so they carry it by
                construction. Round B adds creep / coking / turbine / bearing
                mechanisms as further rows of the same table.
  rated         min(target, life / LIFE_FACTOR)
  tested        min(rated x corpus tested/rated ratio, life), never below rated
                (ablative: tested = rated, the real "no extra time" pattern)

So better cooling raises the life, which lets a longer target stand and gives
more demonstrated overburn - the design lever the GUI's "Burn-time limits"
table points at.
"""
import math

REF_YEAR = 1970                 # decade terms are (year - REF_YEAR) / 10
YEAR_MIN, YEAR_MAX = 1945, 2030  # clamp before extrapolating the era terms
ROLE_ISP_RATIO = 0.80           # sea-level / vacuum Isp above this = a sea-level (booster) engine

# testedBurnTime / ratedBurnTime, ln-linear fit over 426 dated RO liquid-bipropellant
# configs (catalog/testflight_corpus.json; refit_tested() reproduces these):
#   ln(ratio) = A + PER_DECADE*(year-1970)/10 + PF*pressure_fed + RESTART*restartable + UPPER*upper
TESTED_FIT_A = 1.332
TESTED_FIT_PER_DECADE = 0.190
TESTED_FIT_PF = -0.583
TESTED_FIT_RESTART = 0.117
TESTED_FIT_UPPER = -0.363
TESTED_FIT_RMS_LOG = 0.596      # one sigma = x1.8 scatter
TESTED_RATIO_MIN = 1.0          # tested is never shorter than rated

# ratedBurnTime duty by role: ln(rated) = a + b*ln(F_vac kN) + c*(year-1970)/10
RATED_FIT = {                   # role: (a, b, c, rms_log, n)
    "booster": (5.841, -0.087, 0.128, 0.640, 220),
    "upper": (7.503, -0.284, 0.226, 1.004, 242),
    "pressure_fed": (8.324, -0.645, 0.455, 1.353, 61),
}

LIFE_FACTOR = 4.0               # [SP-8110 Sec.2.4.1] ">= 4 on cycles"; [ASR72-238] SF 4 on cycles + creep
THERMAL_LIFE_EXPONENT = 1.0 / 0.205   # [Quentmeyer-TMX73665] OFHC T_gw = 2511*N_f^-0.205 K
# The wall-temperature margin (material max service temp / computed hot-wall
# temp) at which the hardware carries the corpus duty with LIFE_FACTOR of life.
# REVERSE-SOLVED on the validation corpus (validate/burn_time_checks.py): every
# real engine there must carry its real RO ratedBurnTime uncapped, and the
# binding ones are Raptor-2 (0.81 at 360 s, dated by its controller tier) and
# RD-180 (0.71 at its real 255 s) - real engines
# run full duty below the tool's margin 1.0 (coatings, film, conservative
# catalog service temperatures), so the absolute margin level is calibrated
# here, not assumed.
THERMAL_LIFE_MARGIN_REF = 0.69
TESTED_BURN_TIME_CAP_S = 180000.0     # the longest testedBurnTime in the RO corpus (RL10B-2)
RATED_MIN_S = 5.0               # TestFlight's own cushion is 5 s - below that the curve is meaningless


def engine_role(isp_vac_s, isp_sl_s, pressure_fed):
    if pressure_fed:
        return "pressure_fed"
    if isp_vac_s and isp_sl_s and isp_sl_s / isp_vac_s > ROLE_ISP_RATIO:
        return "booster"
    return "upper"


def design_year(design):
    """(year, source): the start year of the design's RP-1 tech node, else the
    controller tier's era year. Clamped to [YEAR_MIN, YEAR_MAX]."""
    year, source = None, ""
    node = (getattr(design, "tech_node", "") or "").strip()
    if node:
        try:
            from ..catalog import build_rp1_snapshot
            year = build_rp1_snapshot.tech_node_year(node)
        except Exception:
            year = None
        if year:
            source = f"tech node {node}"
    if not year:
        from .controller_tech import CONTROLLER_TECHS
        tier = CONTROLLER_TECHS.get(getattr(design, "controller_tech_key", ""), None)
        year = tier.era_year if tier else REF_YEAR
        source = f"controller tier ({tier.display_name})" if tier else "default"
    return max(YEAR_MIN, min(YEAR_MAX, int(year))), source


def default_duty_s(role, thrust_vac_kn, year):
    """The RO-corpus median ratedBurnTime for this role / thrust / era."""
    a, b, c, _rms, _n = RATED_FIT[role]
    return math.exp(a + b * math.log(max(thrust_vac_kn, 0.01)) + c * (year - REF_YEAR) / 10.0)


def thermal_life_s(duty_ref_s, margin_ratio):
    """Longest single burn the wall survives (s) at this temperature margin;
    +inf when the margin is unknown."""
    if margin_ratio is None or not math.isfinite(margin_ratio):
        return float("inf")
    return (LIFE_FACTOR * duty_ref_s
            * (max(margin_ratio, 1e-3) / THERMAL_LIFE_MARGIN_REF) ** THERMAL_LIFE_EXPONENT)


def rated_and_limits(target_s, duty_ref_s, limits):
    """rated = min(target, shortest life / LIFE_FACTOR). `limits` = [{"key",
    "label", "life_s", "lever"}]; returns (rated_s, governing life_s, the
    limit dict that governs or None when the target governs). A limit row
    with life_s = None carries the target by construction (ablative)."""
    finite = [lim for lim in limits if lim.get("life_s") is not None]
    gov = min(finite, key=lambda lim: lim["life_s"]) if finite else None
    life = gov["life_s"] if gov else float("inf")
    cap = life / LIFE_FACTOR
    if cap < target_s:
        return max(RATED_MIN_S, cap), life, gov
    return target_s, life, None


def tested_ratio(year, pressure_fed, restartable, upper):
    return max(TESTED_RATIO_MIN, math.exp(
        TESTED_FIT_A + TESTED_FIT_PER_DECADE * (year - REF_YEAR) / 10.0
        + (TESTED_FIT_PF if pressure_fed else 0.0)
        + (TESTED_FIT_RESTART if restartable else 0.0)
        + (TESTED_FIT_UPPER if upper else 0.0)))


def tested_burn_time_s(rated_s, life_s, ratio, ablative=False):
    if ablative:
        return rated_s
    t = rated_s * ratio
    if life_s is not None and math.isfinite(life_s):
        t = min(t, life_s)
    return min(TESTED_BURN_TIME_CAP_S, max(rated_s, t))


def is_restartable(ignitions):
    return ignitions is None or ignitions <= 0 or ignitions > 1


def tested_ratio_band(ratio):
    """(10th, 90th percentile) of the RO corpus around a fitted tested/rated ratio."""
    k = 1.2816 * TESTED_FIT_RMS_LOG
    return max(TESTED_RATIO_MIN, ratio * math.exp(-k)), ratio * math.exp(k)


def limits_summary_lines(result, tested_s=None, target_is_auto=True):
    """The GUI's "Burn-time limits" table as text lines (pure, headless-testable)."""
    role = {"booster": "sea-level booster", "upper": "upper stage",
            "pressure_fed": "pressure-fed"}.get(result.get("engine_role"), "?")
    lines = [f"Duty target {result['rated_burn_time_target_s']:.0f} s"
             + (f" (auto: RO median for a {role}, {result['design_year']}, "
                f"dated by {result['design_year_source']})" if target_is_auto
                else f" (set; the RO median here is {result['duty_default_s']:.0f} s)")]
    for lim in result.get("burn_time_limits", []):
        if lim.get("life_s") is None:
            lines.append(f"  {lim['label']}: sized to the target")
        else:
            m = f", margin {lim['margin']:.2f}" if lim.get("margin") is not None else ""
            lines.append(f"  {lim['label']}{m}: life {lim['life_s']:.0f} s -> allows "
                         f"{lim['allowable_rated_s']:.0f} s rated (/{LIFE_FACTOR:.0f})")
        lines.append(f"      lever: {lim['lever']}")
    gov = result.get("rated_limited_by", "target")
    lines.append(f"Rated {result['rated_burn_time_s']:.0f} s - "
                 + ("the target is carried" if gov == "target"
                    else f"CAPPED by {gov.replace('_', ' ')}"))
    if tested_s is not None:
        lines.append(f"Tested {tested_s:.0f} s (x{tested_s / max(result['rated_burn_time_s'], 1e-9):.1f} "
                     f"rated; the longest single burn TestFlight treats as demonstrated)")
    return lines


# --- the corpus fits -------------------------------------------------------------

def corpus_rows(rows=None):
    """Dated liquid-bipropellant rows of catalog/testflight_corpus.json."""
    if rows is None:
        from ..catalog import build_testflight_corpus
        rows = build_testflight_corpus.load_rows()
    return [r for r in rows if r["biprop"] and r["year"] and r["thrust_kn"]]


def _upper(r):
    return engine_role(r["isp_vac"], r["isp_sl"], False) == "upper"


def _lstsq(X, y):
    import numpy as np
    X, y = np.array(X, float), np.array(y, float)
    c, *_ = np.linalg.lstsq(X, y, rcond=None)
    return [float(v) for v in c], float(np.sqrt(np.mean((y - X @ c) ** 2)))


def refit_tested(rows=None):
    rows = [r for r in corpus_rows(rows) if r["tested_s"]]
    X = [[1.0, (r["year"] - REF_YEAR) / 10.0, float(r["pressure_fed"]),
          float(is_restartable(r["ignitions"])), float(_upper(r))] for r in rows]
    y = [math.log(r["tested_s"] / r["rated_s"]) for r in rows]
    c, rms = _lstsq(X, y)
    return dict(zip(("A", "per_decade", "pf", "restart", "upper"), c)), rms, len(rows)


def refit_rated(rows=None):
    out = {}
    rows = corpus_rows(rows)
    for role in RATED_FIT:
        sub = [r for r in rows if engine_role(r["isp_vac"], r["isp_sl"], r["pressure_fed"]) == role]
        X = [[1.0, math.log(r["thrust_kn"]), (r["year"] - REF_YEAR) / 10.0] for r in sub]
        y = [math.log(r["rated_s"]) for r in sub]
        c, rms = _lstsq(X, y)
        out[role] = (c[0], c[1], c[2], rms, len(sub))
    return out


if __name__ == "__main__":
    t, rms, n = refit_tested()
    print(f"tested/rated refit (n={n}, rms {rms:.3f}): " + ", ".join(f"{k} {v:+.3f}" for k, v in t.items()))
    for key, frozen in (("A", TESTED_FIT_A), ("per_decade", TESTED_FIT_PER_DECADE),
                        ("pf", TESTED_FIT_PF), ("restart", TESTED_FIT_RESTART),
                        ("upper", TESTED_FIT_UPPER)):
        assert abs(t[key] - frozen) < 0.01, (key, t[key], frozen)
    assert abs(rms - TESTED_FIT_RMS_LOG) < 0.01 and n > 400, (rms, n)
    for role, fit in refit_rated().items():
        print(f"rated duty refit {role:12s}: a {fit[0]:.3f} b {fit[1]:+.3f} c {fit[2]:+.3f} "
              f"rms {fit[3]:.3f} n {fit[4]}")
        for i in range(4):
            assert abs(fit[i] - RATED_FIT[role][i]) < 0.01, (role, i, fit, RATED_FIT[role])
        assert fit[4] == RATED_FIT[role][4], (role, fit[4])

    # Real-engine sanity (warn-only scatter is large; these are the medians):
    # F-1-class booster 1967 (real rated 165 s), RL10-class upper 1966 (real 470 s),
    # AJ10-class pressure-fed upper 1965 (real 400 s).
    f1 = default_duty_s("booster", 7770.0, 1967)
    rl10 = default_duty_s("upper", 73.0, 1966)
    aj10 = default_duty_s("pressure_fed", 35.0, 1965)
    print(f"duty fit: F-1-like {f1:.0f} s, RL10-like {rl10:.0f} s, AJ10-like {aj10:.0f} s")
    assert 100 < f1 < 250 and 250 < rl10 < 900 and 150 < aj10 < 1500
    # tested/rated: 1960s booster ~3x, 2000s restartable booster ~8x, pressure-fed ~1.5x
    r60 = tested_ratio(1965, False, False, False)
    r00 = tested_ratio(2005, False, True, False)
    rpf = tested_ratio(1965, True, False, True)
    print(f"tested/rated: 1965 booster {r60:.2f}, 2005 restartable booster {r00:.2f}, "
          f"1965 pressure-fed upper {rpf:.2f}")
    assert 2.5 < r60 < 4.5 and 6.0 < r00 < 11.0 and 1.0 <= rpf < 2.0

    # Life cap: the reference margin carries the corpus duty exactly; better
    # cooling raises it, a hotter wall cuts it steeply.
    duty, ref = 200.0, THERMAL_LIFE_MARGIN_REF
    lim = lambda m: [{"key": "wall", "label": "wall", "life_s": thermal_life_s(duty, m), "lever": ""}]
    assert abs(rated_and_limits(duty, duty, lim(ref))[0] - duty) < 1e-9
    r_hot, life_hot, gov = rated_and_limits(duty, duty, lim(0.8 * ref))
    assert gov is not None and r_hot < duty * 0.4, r_hot          # 0.8^4.88 = 0.34
    r_long, _, gov2 = rated_and_limits(600.0, duty, lim(1.3 * ref))   # 1.3^4.88 = 3.6 -> cap 720 s
    assert r_long == 600.0 and gov2 is None
    assert rated_and_limits(900.0, duty, lim(1.3 * ref))[0] < 900.0
    # tested never below rated, capped by life, ablative = rated
    assert tested_burn_time_s(200.0, 4 * 200.0 * 1.0, 7.0) == 800.0
    assert tested_burn_time_s(200.0, float("inf"), 3.0) == 600.0
    assert tested_burn_time_s(200.0, 150.0, 3.0) == 200.0
    assert tested_burn_time_s(200.0, None, 3.0, ablative=True) == 200.0
    assert engine_role(311.0, 265.0, False) == "booster" and engine_role(444.0, 150.0, False) == "upper"
    lo, hi = tested_ratio_band(3.0)
    assert 1.0 <= lo < 3.0 < hi, (lo, hi)

    # The GUI table, on a real compute() result.
    from .design import EngineDesign
    res = EngineDesign(cycle="gas_generator").compute()
    txt = limits_summary_lines(res, tested_s=3.0 * res["rated_burn_time_s"])
    assert txt[0].startswith("Duty target") and any("lever:" in x for x in txt)
    assert txt[-1].startswith("Tested"), txt
    print("  " + "\n  ".join(txt))
    print("burn_time self-checks: OK")
