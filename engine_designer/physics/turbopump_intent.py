"""
Directional pump DESIGN INTENT (turbopump Round 2): the user states priorities,
the tool derives the exact geometry.

Four sliders, each -1 .. +1 with 0 = today's constants exactly (so an untouched
design is geometrically identical to Round 1), plus two dropdowns:

  pump_priority            Efficient (-1) <-> Compact (+1)
      stage Ns target and head coefficient psi. A faster, higher-psi pump is
      smaller and lighter; a slower, larger one keeps more of its efficiency
      (size effect [SP-8109 Fig. 6], disk friction, Ss penalty [Fig. 9]).
  pump_head_curve          Stable/throttleable (-1) <-> Max head (+1)
      discharge blade angle beta2 and a psi increment. Backswept low-psi
      impellers give a falling (stable) H-Q curve and wide range; radial-ish
      high-psi ones droop [SP-8109 p.29, Fig. 13, §3.3.1.3].
  suction_aggressiveness   Conservative (-1) <-> Aggressive (+1)
      the inducer blade cavitation number K (Round 1's DESIGN_CAVITATION_NUMBER
      at 0): lower K = higher design Ss = faster suction-limited rotor, at an
      efficiency cost [SP-8109 Fig. 9].
  tip_speed_aggressiveness Stress margin (-1) <-> Max tip speed (+1)
      fraction of the rotor material's tip-speed limit used to set the stage
      count (turbopump_sizing.TIP_SPEED_DESIGN_FRACTION at 0).
  inducer_mode             auto | on | off   (off = no-inducer Ss limit)
  diffuser_type            auto | volute | vaned
      auto = vaned when psi > 0.5 or stage Ns < 1000 [SP-8109 §3.4.1.2.2].

`intent_parameters()` is the ONE mapping; every endpoint is bounded by a cited
real-hardware range (see each constant). Pure module; self-test at __main__.
"""
import math
from dataclasses import dataclass

# --- neutral values (== turbopump_sizing / inducer constants; asserted in the self-test) ---
NS_NEUTRAL_US = 2200.0            # turbopump_sizing.NS_TARGET_US
PSI_NEUTRAL = 0.50                # turbopump_sizing.HEAD_COEFFICIENT_PSI
TIP_FRACTION_NEUTRAL = 0.85       # turbopump_sizing.TIP_SPEED_DESIGN_FRACTION
K_NEUTRAL = 0.0145                # inducer.DESIGN_CAVITATION_NUMBER
BETA2_NEUTRAL_DEG = 25.0          # F-1 / J-2 / H-1 production impellers are all 25 deg
                                  # [SP-8109 Table I]; Huzel's average 22.5 [p.208]

# --- slider spans (Tier 2: endpoints inside the cited ranges) ---
NS_LOG_SPAN = 0.30                # Ns 2200*e^(+-0.3) = 1,630 .. 2,970: inside the flight-proven
                                  # centrifugal 450-2100 (Mark 14 to 3000) [SP-8109 p.7] and
                                  # the eta >= 0.80 band 1500-3200 [SP-8109 Fig. 5]
PSI_PRIORITY_SPAN = 0.08          # psi 0.42 .. 0.58 inside 0.35-0.70+ [SP-8109 p.28]
PSI_HEAD_CURVE_SPAN = 0.06        # the head-curve slider's extra psi
BETA2_STABLE_DEG = 20.0           # -1: 20 deg (Hansen tests 20.75 deg [SP-8109 p.23]; Huzel 17-28)
BETA2_MAX_HEAD_DEG = 45.0         # +1: 45 deg (the Fig. 16 lower-sheet edge; Titan/M-1 35)
K_LOG_SPAN = 0.55                 # K 0.0145*e^(-+0.55): Ss ~30k (conservative) .. ~55k
                                  # (aggressive) - inducer (Nss) 20,000-50,000 [Huzel Table 6-5],
                                  # "~55000 with inducers" [Huzel p.192], A-2 53,400 [SC 6-10]
TIP_FRACTION_SPAN = 0.10          # 0.75 .. 0.95 of the material tip-speed limit
PSI_MIN, PSI_MAX = 0.35, 0.70     # [SP-8109 §2.3.1.2 p.28]

VANED_PSI_ABOVE = 0.5             # [SP-8109 §3.4.1.2.2 p.75] vaned diffuser when psi > 0.5 ...
VANED_NS_BELOW = 1000.0           # ... or stage Ns < 1000

INDUCER_MODES = ("auto", "on", "off")
DIFFUSER_TYPES = ("auto", "volute", "vaned")
PUMP_TYPES = ("auto", "centrifugal", "axial")


def _clamp(x, lo=-1.0, hi=1.0):
    try:
        x = float(x)
    except (TypeError, ValueError):
        return 0.0
    return max(lo, min(hi, x))


@dataclass(frozen=True)
class PumpIntent:
    """Resolved design parameters for both pump legs (the intent sliders are
    shared; pump type is per leg)."""
    ns_target_us: float
    psi: float
    beta2_deg: float
    tip_speed_fraction: float
    cavitation_number: float
    inducer: bool
    diffuser: str            # "auto" | "volute" | "vaned" (auto resolved per stage)
    pump_type_fuel: str      # "centrifugal" | "axial"
    pump_type_ox: str
    priority: float = 0.0
    head_curve: float = 0.0
    suction: float = 0.0
    tip_speed: float = 0.0

    @property
    def neutral(self):
        """True when every slider is at 0 (geometry == Round 1)."""
        return (self.priority == 0.0 and self.head_curve == 0.0
                and self.suction == 0.0 and self.tip_speed == 0.0)

    def pump_type(self, leg):
        return self.pump_type_fuel if leg == "fuel" else self.pump_type_ox


def resolve_pump_type(choice):
    """"auto" = centrifugal: every LH2 pump designed after the J-2S (SSME, RL10,
    Vulcain, LE-7) is centrifugal, and axial is only for non-throttled service
    [SP-8125 §3.2.1]. Axial is an explicit choice (J-2 / M-1 class)."""
    return "axial" if str(choice) == "axial" else "centrifugal"


def intent_parameters(pump_priority=0.0, pump_head_curve=0.0, suction_aggressiveness=0.0,
                      tip_speed_aggressiveness=0.0, inducer_mode="auto", diffuser_type="auto",
                      pump_type_fuel="auto", pump_type_ox="auto"):
    """The ONE intent -> parameter mapping. All sliders at 0 reproduce the Round 1
    constants exactly."""
    p = _clamp(pump_priority)
    h = _clamp(pump_head_curve)
    s = _clamp(suction_aggressiveness)
    t = _clamp(tip_speed_aggressiveness)
    ns = NS_NEUTRAL_US * math.exp(NS_LOG_SPAN * p) if p else NS_NEUTRAL_US
    psi = PSI_NEUTRAL + PSI_PRIORITY_SPAN * p + PSI_HEAD_CURVE_SPAN * h
    psi = max(PSI_MIN, min(PSI_MAX, psi))
    if h >= 0:
        beta2 = BETA2_NEUTRAL_DEG + (BETA2_MAX_HEAD_DEG - BETA2_NEUTRAL_DEG) * h
    else:
        beta2 = BETA2_NEUTRAL_DEG + (BETA2_NEUTRAL_DEG - BETA2_STABLE_DEG) * h
    k = K_NEUTRAL * math.exp(-K_LOG_SPAN * s) if s else K_NEUTRAL
    tip = TIP_FRACTION_NEUTRAL + TIP_FRACTION_SPAN * t
    inducer = str(inducer_mode) != "off"
    diffuser = str(diffuser_type) if str(diffuser_type) in DIFFUSER_TYPES else "auto"
    return PumpIntent(ns_target_us=ns, psi=psi, beta2_deg=beta2, tip_speed_fraction=tip,
                      cavitation_number=k, inducer=inducer, diffuser=diffuser,
                      pump_type_fuel=resolve_pump_type(pump_type_fuel),
                      pump_type_ox=resolve_pump_type(pump_type_ox),
                      priority=p, head_curve=h, suction=s, tip_speed=t)


def from_design(design):
    """intent_parameters() from an EngineDesign's fields (missing -> neutral)."""
    g = lambda name, d: getattr(design, name, d)
    return intent_parameters(g("pump_priority", 0.0), g("pump_head_curve", 0.0),
                             g("suction_aggressiveness", 0.0),
                             g("tip_speed_aggressiveness", 0.0),
                             g("inducer_mode", "auto"), g("diffuser_type", "auto"),
                             g("pump_type_fuel", "auto"), g("pump_type_ox", "auto"))


def resolve_diffuser(intent, psi, ns_stage_us):
    """Per-stage diffuser choice: the user's, or auto per [SP-8109 §3.4.1.2.2]."""
    if intent.diffuser in ("volute", "vaned"):
        return intent.diffuser
    return "vaned" if (psi > VANED_PSI_ABOVE or 0 < ns_stage_us < VANED_NS_BELOW) else "volute"


def readout_lines(intent):
    """Plain-language summary of what the sliders resolved to (GUI readout)."""
    def side(x, neg, pos):
        if abs(x) < 1e-9:
            return "neutral"
        return f"{abs(x):.2f} toward {pos if x > 0 else neg}"
    return [
        f"Efficient<->Compact: {side(intent.priority, 'efficient', 'compact')} -> "
        f"stage Ns {intent.ns_target_us:,.0f}, psi {intent.psi:.2f}",
        f"Stable<->Max head: {side(intent.head_curve, 'stable', 'max head')} -> "
        f"beta2 {intent.beta2_deg:.1f} deg",
        f"Suction: {side(intent.suction, 'conservative', 'aggressive')} -> inducer K "
        f"{intent.cavitation_number:.4f}" + ("" if intent.inducer else " (NO inducer)"),
        f"Tip speed: {side(intent.tip_speed, 'margin', 'max')} -> "
        f"{intent.tip_speed_fraction:.0%} of material limit",
        f"Diffuser: {intent.diffuser}; pump type fuel {intent.pump_type_fuel} / "
        f"ox {intent.pump_type_ox}",
    ]


if __name__ == "__main__":
    from . import turbopump_sizing, inducer
    # neutral values are today's constants, exactly
    assert NS_NEUTRAL_US == turbopump_sizing.NS_TARGET_US
    assert PSI_NEUTRAL == turbopump_sizing.HEAD_COEFFICIENT_PSI
    assert TIP_FRACTION_NEUTRAL == turbopump_sizing.TIP_SPEED_DESIGN_FRACTION
    assert K_NEUTRAL == inducer.DESIGN_CAVITATION_NUMBER
    n = intent_parameters()
    assert n.neutral and n.ns_target_us == 2200.0 and n.psi == 0.5
    assert n.tip_speed_fraction == 0.85 and n.cavitation_number == 0.0145
    assert n.inducer and n.pump_type_fuel == "centrifugal" and n.beta2_deg == 25.0
    # directions
    c = intent_parameters(pump_priority=1.0)
    e = intent_parameters(pump_priority=-1.0)
    assert c.ns_target_us > n.ns_target_us > e.ns_target_us and c.psi > n.psi > e.psi
    hi = intent_parameters(pump_head_curve=1.0)
    lo = intent_parameters(pump_head_curve=-1.0)
    assert hi.beta2_deg == 45.0 and lo.beta2_deg == 20.0 and hi.psi > lo.psi
    ag = intent_parameters(suction_aggressiveness=1.0)
    co = intent_parameters(suction_aggressiveness=-1.0)
    ss = lambda k: inducer.design_suction_specific_speed("ox", k=k)
    print(f"suction Ss (ox): conservative {ss(co.cavitation_number):,.0f} / neutral "
          f"{ss(n.cavitation_number):,.0f} / aggressive {ss(ag.cavitation_number):,.0f}")
    assert 25_000 < ss(co.cavitation_number) < ss(n.cavitation_number) < ss(ag.cavitation_number) < 60_000
    assert intent_parameters(tip_speed_aggressiveness=1.0).tip_speed_fraction == 0.95
    assert not intent_parameters(inducer_mode="off").inducer
    assert intent_parameters(pump_type_fuel="axial").pump_type("fuel") == "axial"
    # clamping + psi band
    x = intent_parameters(pump_priority=9, pump_head_curve=9)
    assert x.psi <= PSI_MAX and x.priority == 1.0
    # diffuser auto rule
    assert resolve_diffuser(n, 0.5, 2200) == "volute"
    assert resolve_diffuser(n, 0.55, 2200) == "vaned"
    assert resolve_diffuser(n, 0.5, 900) == "vaned"
    for line in readout_lines(intent_parameters(pump_priority=0.5, suction_aggressiveness=-0.5)):
        print("  " + line)
    print("turbopump_intent self-test OK")
