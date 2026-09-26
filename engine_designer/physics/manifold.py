"""
Propellant intake manifold: the header/collar that collects each propellant
from its feed line and distributes it to the injector orifices. Until now
this was ZERO in every sense - physics/injectors.py's element_geometry()
starts downstream of it (at the orifices), physics/mass_model.py never
counted its mass, and both 3D previews / the 2D schematic drew a purely
cosmetic, fixed-proportion-of-chamber-radius stand-in with no connection to
mdot or density (in the OpenGL 3D preview, that stand-in is in fact the
regen-COOLANT jacket's manifold ring reused for looks - see
gui/preview3d_gl.py's collar block - physically unrelated to this module).

Round 2 added the actual regen-COOLANT jacket's own coolant-supply ring(s) -
size_jacket_manifolds(), below - to this same module (for _bore_and_wall/
_assemble reuse), so the module now sizes TWO conceptually different kinds
of ring: size_manifolds()'s injector-feed rings (fuel+ox, downstream of the
jacket, right before the orifices) and size_jacket_manifolds()'s jacket
rings (fuel only, upstream of - or turning around within - the jacket
itself). Don't confuse them: an injector-feed ring's pressure is
pc_feed + injector dP (post-jacket); a jacket ring's pressure is
pc_feed + injector dP + jacket_dp_pa or a fraction of it (pre-jacket, or
mid-jacket at a turnaround) - see size_jacket_manifolds' own docstring.

Two independent rings are sized here, one per propellant (most real engines
route fuel and ox through separate injector-head manifolds): cross-section
from continuity at a target bulk feed velocity (mdot = rho * V * A), wall
thickness/mass from thin-wall hoop stress against the real local feed
pressure (pc_feed + that propellant's own injector dP - see module docstring
below for why NOT pump discharge pressure).

Each per-propellant result dict is also this round's frozen "hook point" for
a future plumbing/piping feature (see HOOK_POINT_FIELDS below) - attachment
position/direction, bore, mdot and design velocity, with no pipe geometry
drawn yet (data-only, by explicit design decision this round).

The two rings are placed at different AXIAL stations, not stacked radially
outside one another - two full 360-degree tori centered on the same axis can
only avoid intersecting by separating radially (stacking) or axially
(different positions along the engine axis); axial separation was chosen so
each ring's own radius depends only on its own size, not on also clearing
the other propellant's footprint (a first pass used radial stacking and
produced a combined structure reaching ~3x the collar's own radius - visibly
oversized next to this renderer's other, deliberately subtle, cosmetic
hardware).

No real-engine manifold-diameter/wall-thickness figure exists anywhere in
this project to spot-check against (Engine_Configs/*.cfg headers carry only
Isp/Pc/eps/MR tables, not manufacturing geometry) - the sizing physics is
self-consistent (continuity + hoop stress, both exact relations) but the
feed-velocity target and allowable-stress/density constants below are
engineering-judgment Tier-3 defaults, not derived. See ASSUMPTIONS.md.

Round 3 added propellant-density-scaled feed velocity (V ~ 1/sqrt(rho) at a
fixed velocity-head budget). Round 4 (2026-09-22) replaced its UNCITED 15 m/s
kerolox "baseline" with velocities anchored to what each ring feeds:
- injector-feed rings (size_manifolds): the velocity whose head 0.5*rho*V^2
  is a set FRACTION of that leg's own injector dP
  (velocity_from_head_fraction) - the manifold-uniformity rationale of
  [SP-8087 Sec.2.1.2.1 p.19-20], [SP-8120 Sec.2.2.5.2.3 p.47] (H-1 dam) and
  [CR-128318] (low-velocity manifold for ~1% per-element uniformity). The
  1/sqrt(rho) law now falls out of it instead of being a separate rule. The
  direction is cited; the fraction's VALUE is Tier 3.
- regen-jacket rings (size_jacket_manifolds): the coolant-PASSAGE velocity
  at the ring's own station (cooling.passage_velocity_ms) - SP-8087's
  constant-velocity torus gives every passage the same inlet velocity, and
  Fagherazzi's volute design avoids abrupt manifold-to-channel velocity
  changes.
Both are checked against SP-8087 Sec.3.1.1.5.3's 61 m/s liquid-coolant
limit (velocity_cap_warning) - a coolant-PASSAGE limit, borrowed as a
ceiling for the manifolds feeding them. Same earlier round also raised
MANIFOLD_SIGMA_ALLOW_PA off its overly-conservative generic-mild-steel
value - see that constant's own comment below.
"""
import math

from . import mass_model

# --- Tier 3 constants (see ASSUMPTIONS.md) ----------------------------------
# Injector-feed ring velocity head as a FRACTION of that leg's own injector dP:
# 0.5*rho*V^2 = f * dP_inj  ->  V = sqrt(2*f*dP_inj/rho). The DIRECTION is cited
# (a slow manifold - small dynamic head vs. the orifice dP downstream - is what
# keeps every orifice at the same static pressure: [SP-8087 Sec.2.1.2.1 p.19-20],
# [SP-8120] H-1 fuel-manifold dam, [CR-128318] ~1% per-element manifold design);
# no source gives a numeric ratio, so the VALUE is Tier 3. 0.04 was picked to
# reproduce the tool's previous RS-29-class kerolox header velocities (~15 m/s
# RP-1 / ~12.6 m/s LOX at ~2 MPa injector dP), so the re-anchoring moved the
# rationale, not the answer, for a typical design. User slider
# (EngineDesign.fuel_/ox_manifold_head_fraction).
MANIFOLD_VELOCITY_HEAD_FRACTION_DEFAULT = 0.04
MANIFOLD_VELOCITY_HEAD_FRACTION_MIN = 0.01
MANIFOLD_VELOCITY_HEAD_FRACTION_MAX = 0.15

# [SP-8087 Sec.3.1.1.5.3 p.61]: "keep liquid coolants at velocities below
# 200 ft/sec (61 m/sec)"; gases below Mach 0.3 recommended / 0.5 max. A coolant-
# PASSAGE limit, applied here to the manifolds that feed those passages (and to
# the injector-feed rings as a liquid-line ceiling). LH2 at jacket conditions is
# supercritical, so the liquid figure does not apply and the gas (Mach) criterion
# would need a speed-of-sound model this tool doesn't have - velocity_cap_warning
# skips it (see claude_lit/OPEN_QUESTIONS.md).
LIQUID_VELOCITY_MAX_MS = 61.0

# --- Split + tapered ring (Round 4) ------------------------------------------
# A ring fed at one inlet splits the flow two ways, so each branch carries at
# most mdot/2 [SP-8087 Sec.2.1.2.1 p.19-20]; the inlet cross-section is sized on
# that half-flow. Around each branch the flow drains into the orifices/passages,
# remaining fraction (1 - phi/pi) at angle phi from the inlet. SP-8087 gives two
# extremes - constant AREA (least pressure loss, maldistribution) and constant
# VELOCITY (area proportional to remaining flow, Fagherazzi's A(theta) =
# mdot(theta)/(rho*v)) - and the criterion that a real torus lies BETWEEN them
# [SP-8087 Sec.3.1.2.1 p.62]. The blend b (0 = constant area, 1 = constant
# velocity) interpolates: A(phi) = A_in * max(1 - b*phi/pi, floor). 0.5 is the
# "between" midpoint - Tier 3, the source gives no number.
MANIFOLD_TAPER_BLEND_DEFAULT = 0.5
# Tier 3 (fabrication/structure): the far side never shrinks below this fraction
# of the inlet area - a real torus stays a buildable, weldable tube all the way
# round (and a b=1 constant-velocity ring would otherwise pinch to zero).
MANIFOLD_TAPER_MIN_AREA_FRACTION = 0.15
_TAPER_MASS_SAMPLES = 72
# --- Scroll ring (2026-09-25) -------------------------------------------------
# A ring fed TANGENTIALLY at one inlet with the flow going one way round (a
# volute) - the real F-1 and J-2 turbine-exhaust manifolds: the duct runs
# tangentially into a torus "of decreasing (from inlet to exit) cross-sectional
# area" [F1-Man §1-18] (photos: F-1 thrust chamber, enginehistory.org RPE 8.12;
# J-2, Science Museum 1977-0402). Sized on the FULL flow at the inlet; the
# remaining flow at phi along the flow is (1 - phi/360), so the same blend b
# gives A(phi) = A_in * max(1 - b*phi/360, MANIFOLD_TAPER_MIN_AREA_FRACTION).
RING_KIND_SPLIT = "split"
RING_KIND_SCROLL = "scroll"

# This module's own fallback for a caller that passes no explicit
# feed_velocity_target_ms (the self-test only - design.py always passes one):
# the RS-29-class values MANIFOLD_VELOCITY_HEAD_FRACTION_DEFAULT reproduces.
FEED_VELOCITY_TARGET_MS = {
    "fuel": 15.0,
    "ox": 15.0 * math.sqrt(810.0 / 1141.0),
}

# Generic cold-side (propellant-wetted, near-ambient/cryo temperature) steel/
# Inconel structural allowable stress and density for the manifold shell -
# same idiom and tier as mass_model.INJECTOR_PLATE_SIGMA_ALLOW_PA/
# INJECTOR_PLATE_DENSITY_KG_M3, deliberately NOT wired to materials.py (that
# catalog only stores already-thermally-DERATED hot-combustion-gas-side
# allowables, at or near each material's max service temperature - no
# un-derated/room-temperature value is stored anywhere to borrow for this
# cold-side application - verified this round) or turbopump_materials.py (no
# numeric allowable-stress field exists there, only a qualitative
# strength_class string). Raised this round (was 4.0e8) off its earlier
# generic-mild-steel-level floor to a more realistic forged/welded
# corrosion-resistant-steel or Inconel allowable for cold propellant-wetted
# service - still an uncited Tier-3 pick, just a less conservative one.
MANIFOLD_SIGMA_ALLOW_PA = 6.0e8
MANIFOLD_DENSITY_KG_M3 = 7900.0

# Collar placement (packaging, matches the existing cosmetic collar's own
# chamber_head_r*1.10 convention already used at gui/preview3d_gl.py's
# injector-head collar, gui/preview3d.py's matplotlib fallback, and
# gui/schematic.py's rc*1.06 dome - so the new rings' mass and the rendered
# geometry never disagree about where the collar sits).
MANIFOLD_COLLAR_R_MULT = 1.10
MANIFOLD_RING_CLEARANCE_M = 0.01   # RADIAL gap: chamber-head hardware -> each ring's own
                                    # inner edge (applied independently to both fuel and ox -
                                    # see size_manifolds' placement, not stacked one outside
                                    # the other)
MANIFOLD_AXIAL_CLEARANCE_M = 0.01  # AXIAL gap: collar/dome (which sit at/behind x=0) -> the
                                    # first (fuel) ring's own near edge, so the ring sits
                                    # just downstream of them rather than overlapping
MANIFOLD_AXIAL_RING_GAP_M = 0.006  # AXIAL gap: fuel ring's far edge -> ox ring's near edge
                                    # (the two rings are placed at different axial stations,
                                    # not stacked radially - see size_manifolds)

# Warn-don't-block plausibility thresholds (Tier 3, not derived).
THIN_WALL_RATIO_WARN = 0.30                # t/r above this stretches the thin-wall
                                            # hoop-stress approximation thin
MANIFOLD_MASS_DRY_FRACTION_WARN = 0.35     # manifold mass vs. dry mass, same idiom as
                                            # design.py's battery_motor_mass_kg check

# The exact fields of each per-propellant result dict that make up this
# round's frozen hook-point contract for a future plumbing/piping feature.
# Everything else in the dict (wall_thickness_m, mass_kg, feed_pressure_pa,
# major_radius_m, outer_radius_m, thin_wall_ratio) is this round's own
# sizing/mass detail, kept in the same dict for convenience but NOT part of
# the contract - a future plumbing feature should only rely on these seven.
# attach_axial_station_m genuinely differs between fuel and ox (each ring
# sits at its own axial station - see the module docstring) - arguably more
# useful for a future plumbing feature than a shared value would be, since
# real engines commonly do route fuel/ox manifolds at different axial
# positions, not just an artifact of how this tool avoids ring overlap.
HOOK_POINT_FIELDS = (
    "attach_axial_station_m", "attach_radial_offset_m", "attach_angular_position_deg",
    "attach_direction_xyz", "inner_diameter_m", "mdot_kgs", "design_feed_velocity_ms",
)

# --- Jacket-manifold constants (Round 2) ------------------------------------
# Real F-1 value (heroicrelics.org/info/f-1/f-1-thrust-chamber.html, read this
# round): 30% of fuel bypasses the cooling jacket entirely, straight to the
# Fuel Injector Manifold (= this module's existing fuel ring); the other 70%
# goes down the "down tubes" for regen cooling. Tier 2 - real-engine-derived,
# but from an informal web source, not a claude_lit-tier citation. See
# ASSUMPTIONS.md. User-adjustable slider (EngineDesign.manifold_bypass_fraction).
MANIFOLD_BYPASS_FRACTION_DEFAULT = 0.30
MANIFOLD_BYPASS_FRACTION_MIN = 0.0
MANIFOLD_BYPASS_FRACTION_MAX = 0.6   # generous but bounded; no data grades values
                                      # within this range, so no plausibility _check
                                      # exists for it beyond the slider's own clamp

# Tier 3, no citation: how much of the jacket's total pressure drop
# (jacket_dp_pa) is "used up" by the down-leg before fuel reaches the return
# manifold, under f1_split_reverse_flow - an arbitrary symmetric split, not
# derived. See size_jacket_manifolds and ASSUMPTIONS.md.
JACKET_RETURN_SPLIT_FRACTION = 0.5

# Tier 3, geometric reasoning only (no measured value): the f1_split_reverse_flow
# "jacket_return" ring is a TURNAROUND manifold, not a header - each down-tube
# hands its flow straight to the adjacent up-tube(s) across a small common
# annulus welded/brazed over the aft tube ends ([SP-8087 §2.1.2.1 p.20,
# §3.1.2.1-2 p.62-64]: common annulus preferred for storable coolants, turnaround
# integral with the aft flange; real F-1 fuel return manifold photo,
# heroicrelics.org). No net flow goes around the ring, so its bore follows the
# local coolant-passage size, NOT continuity on the whole down-leg mdot. Bore ~2x
# the local passage height = room for the U-turn from a down-tube into its
# neighbour. Trust "small collar, a few passage heights" - not the exact 2.0.
TURNAROUND_BORE_PASSAGE_MULT = 2.0
# Fallback when no per-station passage geometry exists (non-"channels" regen
# model): bore = this x throat diameter - 2x the 3D preview's existing
# MANIFOLD_TUBE_R_THROAT_DIA_MULT (0.03, a far-end ring's cross-section RADIUS),
# i.e. the same established proportion, not a new one.
TURNAROUND_BORE_THROAT_DIA_MULT = 0.06


def velocity_from_head_fraction(head_fraction, dp_injector_leg_pa, rho_kg_m3):
    """Injector-feed ring bulk velocity whose dynamic head 0.5*rho*V^2 is
    `head_fraction` of that leg's injector dP (see
    MANIFOLD_VELOCITY_HEAD_FRACTION_DEFAULT). Lower density -> higher velocity
    at the same head, i.e. the old V ~ 1/sqrt(rho) law as a consequence."""
    if head_fraction <= 0 or dp_injector_leg_pa <= 0 or rho_kg_m3 <= 0:
        return 0.0
    return math.sqrt(2.0 * head_fraction * dp_injector_leg_pa / rho_kg_m3)


def velocity_cap_warning(velocity_ms, label, supercritical=False):
    """Warn (string) if a manifold's bulk velocity exceeds SP-8087's 61 m/s
    liquid limit; None if it's fine or if the fluid is `supercritical` (LH2 -
    the liquid limit doesn't apply and no Mach model exists; see
    LIQUID_VELOCITY_MAX_MS). Warn, don't block."""
    if supercritical or velocity_ms <= LIQUID_VELOCITY_MAX_MS:
        return None
    return (f"{label} manifold bulk velocity {velocity_ms:.1f} m/s exceeds SP-8087's "
            f"{LIQUID_VELOCITY_MAX_MS:.0f} m/s liquid-coolant limit [SP-8087 Sec.3.1.1.5.3] "
            f"(a coolant-passage figure, borrowed as a ceiling for the manifold) - expect "
            f"high line losses and poor flow distribution around the ring.")


def required_flow_radius_m(mdot_kgs, rho_kg_m3, target_velocity_ms):
    """Inner (flow-bore) radius of a circular-section manifold passing
    mdot_kgs at target_velocity_ms: A = mdot/(rho*V), r = sqrt(A/pi) - the
    direct inverse of the continuity relation injectors.py's own orifice
    sizing already uses, at the manifold's own (lower, header-scale) target
    velocity instead of the orifice jet velocity."""
    if mdot_kgs <= 0 or rho_kg_m3 <= 0 or target_velocity_ms <= 0:
        return 0.0
    area = mdot_kgs / (rho_kg_m3 * target_velocity_ms)
    return math.sqrt(area / math.pi)


def manifold_wall_thickness_m(manifold_pressure_pa, flow_radius_m,
                               allowable_stress_pa=MANIFOLD_SIGMA_ALLOW_PA):
    """Thin-wall hoop stress on the manifold's own bore radius, treating a
    thin torus LOCALLY as a straight cylinder (major radius >> minor radius)
    - the standard thin-torus approximation, not a full toroidal-shell
    solution. Delegates straight to mass_model.wall_thickness_m (same
    t = SAFETY_FACTOR*P*r/sigma_allow relation) rather than re-deriving it -
    one hoop-stress formula in the whole tool."""
    return mass_model.wall_thickness_m(manifold_pressure_pa, flow_radius_m, allowable_stress_pa)


def manifold_ring_mass_kg(major_radius_m, flow_radius_m, wall_thickness_m_,
                           density_kg_m3=MANIFOLD_DENSITY_KG_M3):
    """Exact thin toroidal shell mass at the wall's own mid-surface radius
    (flow_radius_m + wall_thickness_m_/2): surface area 4*pi^2*R*r_mid, times
    thickness, times density - a torus has one simple closed-form area
    unlike mass_model.shell_mass_kg's arbitrary-profile frustum integration,
    so no per-station loop is needed here."""
    if major_radius_m <= 0 or flow_radius_m <= 0 or wall_thickness_m_ <= 0:
        return 0.0
    r_mid = flow_radius_m + wall_thickness_m_ / 2.0
    surface_area = 4.0 * math.pi ** 2 * major_radius_m * r_mid
    return surface_area * wall_thickness_m_ * density_kg_m3


def thin_wall_warning(thin_wall_ratio, propellant_label):
    """Warn (string) if the manifold wall is thick enough relative to its own
    flow-bore radius that the thin-wall hoop-stress approximation is
    stretched thin; None if it's fine."""
    if thin_wall_ratio <= THIN_WALL_RATIO_WARN:
        return None
    return (f"{propellant_label} manifold wall thickness is {thin_wall_ratio:.2f}x its own "
            f"flow-bore radius - the thin-wall hoop-stress approximation (this tool's only "
            f"manifold-structure model) is no longer a good fit at this thickness/radius "
            f"ratio; treat the mass figure as increasingly approximate. Lower chamber "
            f"pressure to shrink this.")


def bore_vs_chamber_warning(inner_diameter_m, chamber_dia_m, propellant_label):
    """Warn (string) if the manifold's flow bore would exceed the chamber
    diameter it feeds - an unbuildable packaging; None if it's fine."""
    if inner_diameter_m <= chamber_dia_m:
        return None
    return (f"{propellant_label} manifold flow bore ({inner_diameter_m * 1000.0:.0f} mm) "
            f"exceeds the chamber diameter ({chamber_dia_m * 1000.0:.0f} mm) it feeds - not "
            f"a buildable packaging at this mdot/velocity combination.")


def taper_area_fraction(phi_from_inlet_deg, taper_blend):
    """Local flow-area fraction (vs. the inlet) of a split/tapered ring at
    `phi_from_inlet_deg` around the ring from its inlet (folded to 0..180 -
    the two branches are symmetric). See MANIFOLD_TAPER_BLEND_DEFAULT."""
    phi = abs((phi_from_inlet_deg + 180.0) % 360.0 - 180.0)
    b = min(max(taper_blend, 0.0), 1.0)
    return max(1.0 - b * phi / 180.0, MANIFOLD_TAPER_MIN_AREA_FRACTION)


def scroll_area_fraction(phi_along_flow_deg, taper_blend):
    """Local flow-area fraction (vs. the inlet) of a SCROLL ring at
    `phi_along_flow_deg` (0 at the inlet .. 360 at the tail, measured along the
    flow) - see RING_KIND_SCROLL."""
    phi = min(max(phi_along_flow_deg, 0.0), 360.0)
    b = min(max(taper_blend, 0.0), 1.0)
    return max(1.0 - b * phi / 360.0, MANIFOLD_TAPER_MIN_AREA_FRACTION)


def scroll_phi_along_flow_deg(ring, angle_deg):
    """Angle travelled along a scroll ring's flow from its inlet to absolute
    angle `angle_deg`, in [0, 360)."""
    d = angle_deg - ring.get("attach_angular_position_deg", 0.0)
    return (d * (1.0 if ring.get("scroll_dir", 1) >= 0 else -1.0)) % 360.0


def ring_area_fraction_at(ring, angle_deg):
    """Local flow-area fraction of any ring dict at absolute angle `angle_deg`
    (split header: symmetric two-branch taper; scroll: one-way taper)."""
    if ring.get("ring_kind") == RING_KIND_SCROLL:
        return scroll_area_fraction(scroll_phi_along_flow_deg(ring, angle_deg),
                                    ring.get("taper_blend", 0.0))
    return taper_area_fraction(angle_deg - ring.get("attach_angular_position_deg", 0.0),
                               ring.get("taper_blend", 0.0))


def ring_is_scroll(ring):
    return bool(ring) and ring.get("ring_kind") == RING_KIND_SCROLL


def scroll_rotated_to(ring, angle_deg):
    """A copy of a scroll ring dict with its INLET turned to `angle_deg` (the
    duct run's attach angle - a scroll's inlet is wherever its duct lands; the
    ring is otherwise axisymmetric, so mass/sizing are unchanged). A non-scroll
    ring comes back unchanged (same object)."""
    if not ring_is_scroll(ring):
        return ring
    a = float(angle_deg) % 360.0
    sd = 1 if ring.get("scroll_dir", 1) >= 0 else -1
    th = math.radians(a)
    out = dict(ring)
    out["attach_angular_position_deg"] = a
    out["attach_direction_xyz"] = (0.0, sd * math.sin(th), -sd * math.cos(th))
    return out


def ring_flow_radius_at(ring, angle_deg):
    """Flow-bore radius of a manifold ring dict at absolute angle `angle_deg`
    (same convention as attach_angular_position_deg: 0 = +y)."""
    frac = ring_area_fraction_at(ring, angle_deg)
    return ring.get("inlet_flow_radius_m", ring["flow_radius_m"]) * math.sqrt(frac)


def ring_outer_radius_at(ring, angle_deg):
    """Outer (tube-surface) radius of a manifold ring dict at `angle_deg` -
    the wall scales with the local bore (hoop stress, t/r constant)."""
    return ring_flow_radius_at(ring, angle_deg) * (1.0 + ring.get("thin_wall_ratio", 0.0))


def tapered_ring_mass_kg(major_radius_m, inlet_flow_radius_m, thin_wall_ratio, taper_blend,
                         density_kg_m3=MANIFOLD_DENSITY_KG_M3, kind=RING_KIND_SPLIT):
    """Thin toroidal shell mass with a bore varying around the ring (see
    taper_area_fraction / scroll_area_fraction by `kind`), wall t =
    thin_wall_ratio * local bore: numeric integral of 2*pi*r_mid(phi)*t(phi)
    * R dphi. taper_blend = 0 reproduces manifold_ring_mass_kg's closed form
    exactly (either kind)."""
    frac_fn = scroll_area_fraction if kind == RING_KIND_SCROLL else taper_area_fraction
    if major_radius_m <= 0 or inlet_flow_radius_m <= 0 or thin_wall_ratio <= 0:
        return 0.0
    n = _TAPER_MASS_SAMPLES
    total = 0.0
    for i in range(n):
        phi = (i + 0.5) * 360.0 / n
        r = inlet_flow_radius_m * math.sqrt(frac_fn(phi, taper_blend))
        t = thin_wall_ratio * r
        total += 2.0 * math.pi * (r + t / 2.0) * t
    return total / n * 2.0 * math.pi * major_radius_m * density_kg_m3


def _bore_and_wall(mdot_kgs, rho_kg_m3, dp_injector_leg_pa, pc_feed_pa, target_velocity_ms):
    """Flow-bore radius, wall thickness and feed pressure - all independent
    of WHERE the ring is placed (major_radius_m only scales its mass, not
    its own cross-section), so ring placement (which needs both rings'
    outer radii to avoid overlap) can be resolved afterward.

    Round 4: `r_flow` is the ring's INLET bore, sized on HALF the flow (the
    two-way split - see MANIFOLD_TAPER_BLEND_DEFAULT); the full-flow feed bore
    (what the connecting pipe carries) is sqrt(2) larger and is derived by
    _assemble."""
    r_flow = required_flow_radius_m(0.5 * mdot_kgs, rho_kg_m3, target_velocity_ms)
    feed_pressure_pa = pc_feed_pa + dp_injector_leg_pa
    wall_t = manifold_wall_thickness_m(feed_pressure_pa, r_flow) if r_flow > 0 else 0.0
    return r_flow, wall_t, feed_pressure_pa


def _assemble(mdot_kgs, target_velocity_ms, angle_deg, major_radius_m, axial_station_m,
              r_flow, wall_t, feed_pressure_pa, taper_blend=0.0, split=True,
              kind=RING_KIND_SPLIT, scroll_dir=1):
    """One ring result dict. `r_flow`/`wall_t` are the INLET (largest) bore and
    wall; with `split` the ring was sized on half the flow (a header ring) and
    tapers by `taper_blend` away from its inlet at `angle_deg`, and the hook's
    `inner_diameter_m` is the FULL-flow feed bore (sqrt(2) x the inlet bore) -
    what a connecting pipe carries. `split=False` (a turnaround collar - no net
    flow around it) keeps a constant section and inner_diameter_m = its bore.
    `kind=RING_KIND_SCROLL` (split ignored): a tangentially-fed one-way scroll
    sized on the FULL flow - inner_diameter_m = the inlet bore, tapering along
    the flow (direction `scroll_dir`, +1 = increasing angle) to its tail; the
    hook direction is the ring tangent AGAINST the flow (where the duct leaves)."""
    scroll = kind == RING_KIND_SCROLL
    k = (wall_t / r_flow) if r_flow > 0 else 0.0
    blend = taper_blend if (split or scroll) else 0.0
    r_outer = r_flow + wall_t
    mass_kg = tapered_ring_mass_kg(major_radius_m, r_flow, k, blend,
                                   kind=RING_KIND_SCROLL if scroll else RING_KIND_SPLIT)
    if scroll:
        r_min = r_flow * math.sqrt(scroll_area_fraction(360.0, blend))
        r_feed = r_flow
    else:
        r_min = r_flow * math.sqrt(taper_area_fraction(180.0, blend))
        r_feed = r_flow * math.sqrt(2.0) if split else r_flow
    angle_rad = math.radians(angle_deg)
    sd = 1 if scroll_dir >= 0 else -1
    if scroll:
        # tangent of increasing angle is (0, -sin, cos); the duct leaves
        # against the flow
        attach_dir = (0.0, sd * math.sin(angle_rad), -sd * math.cos(angle_rad))
    else:
        attach_dir = (0.0, math.cos(angle_rad), math.sin(angle_rad))
    extra = {"ring_kind": RING_KIND_SCROLL, "scroll_dir": sd} if scroll else {}
    return {
        **extra,
        # --- hook point (see HOOK_POINT_FIELDS) ---
        "attach_axial_station_m": axial_station_m,
        "attach_radial_offset_m": major_radius_m,
        "attach_angular_position_deg": angle_deg,
        # Outward unit normal of the manifold wall at the attachment point -
        # a future pipe run approaches along the NEGATIVE of this vector.
        # (Scroll: the tangent against the flow - the duct's own direction.)
        "attach_direction_xyz": attach_dir,
        "inner_diameter_m": 2.0 * r_feed,
        "mdot_kgs": mdot_kgs,
        "design_feed_velocity_ms": target_velocity_ms,
        # --- sizing/mass detail (this round's mass rollup + GUI use only) ---
        # flow_radius_m / outer_radius_m / wall_thickness_m are the INLET
        # (largest) section - every placement/clearance call site uses them as
        # the ring's max envelope; ring_*_radius_at() give the local values.
        "flow_radius_m": r_flow,
        "outer_radius_m": r_outer,
        "wall_thickness_m": wall_t,
        "inlet_flow_radius_m": r_flow,
        "min_flow_radius_m": r_min,
        "ring_inlet_inner_diameter_m": 2.0 * r_flow,
        "taper_blend": blend,
        "feed_wall_thickness_m": k * r_feed,
        "major_radius_m": major_radius_m,
        "feed_pressure_pa": feed_pressure_pa,
        "mass_kg": mass_kg,
        "thin_wall_ratio": k,
    }


def size_manifolds(mdot_fuel_kgs, mdot_ox_kgs, rho_fuel, rho_ox, pc_feed_pa,
                    dp_injector_fuel_pa, dp_injector_ox_pa, chamber_dia_m,
                    feed_velocity_target_ms=None, taper_blend=MANIFOLD_TAPER_BLEND_DEFAULT,
                    inlet_angles_deg=None):
    """
    Size the fuel and ox propellant-intake manifolds from actual mdot,
    density and local feed pressure (pc_feed_pa + that leg's injector dP -
    the pressure the manifold itself actually sees, NOT pump discharge
    pressure: design.py's dp_fuel/dp_ox already include jacket dP/line-loss/
    tank-head terms that are upstream of the manifold, and are undefined on
    the pressure-fed cycle branch).

    Two full-360-degree rings, fuel at angle 0 (+y), ox at 180 (-y) -
    matching the convention already used by gui/schematic.py's F/O stubs and
    gui/preview3d.py's +-y stub loop. Each ring's own RADIUS depends only on
    its own size (independently clearing the collar by MANIFOLD_RING_
    CLEARANCE_M - no longer "ox stacks outside fuel's entire footprint").
    The two rings are separated AXIALLY instead: fuel sits just downstream of
    the collar/dome, ox sits further downstream still, clearing fuel's own
    far edge by MANIFOLD_AXIAL_RING_GAP_M - so they can never overlap by
    construction, without inflating either ring's radius to clear the other.

    `taper_blend` is one value for both rings or a per-ring {"fuel", "ox"}
    dict (EngineDesign's fuel_/ox_manifold_taper_blend).

    Returns {"fuel": {...}, "ox": {...}, "total_mass_kg": float}; each
    per-propellant dict's hook-point fields are listed in HOOK_POINT_FIELDS.
    """
    fvt = feed_velocity_target_ms or FEED_VELOCITY_TARGET_MS
    tb = (dict(taper_blend) if isinstance(taper_blend, dict)
          else {"fuel": taper_blend, "ox": taper_blend})
    chamber_r_m = chamber_dia_m / 2.0
    base_r_m = chamber_r_m * MANIFOLD_COLLAR_R_MULT + MANIFOLD_RING_CLEARANCE_M

    # Bore/wall first (independent of placement or of the other propellant).
    fuel_r_flow, fuel_wall_t, fuel_feed_p = _bore_and_wall(
        mdot_fuel_kgs, rho_fuel, dp_injector_fuel_pa, pc_feed_pa, fvt["fuel"])
    fuel_r_outer = fuel_r_flow + fuel_wall_t
    ox_r_flow, ox_wall_t, ox_feed_p = _bore_and_wall(
        mdot_ox_kgs, rho_ox, dp_injector_ox_pa, pc_feed_pa, fvt["ox"])
    ox_r_outer = ox_r_flow + ox_wall_t

    # Radius: each ring independently just clears the collar - symmetric
    # formula, no dependency on the other propellant's size.
    r_major_fuel = base_r_m + fuel_r_outer
    r_major_ox = base_r_m + ox_r_outer

    # Axial station: fuel just downstream of the collar/dome (both of which
    # sit at/behind x=0), ox further downstream still, clearing fuel's own
    # far edge - both offsets positive (+x, into the chamber body), so
    # neither ring ever pokes backward into the dome.
    x_fuel = fuel_r_outer + MANIFOLD_AXIAL_CLEARANCE_M
    x_ox = x_fuel + fuel_r_outer + MANIFOLD_AXIAL_RING_GAP_M + ox_r_outer

    ang = {"fuel": 0.0, "ox": 180.0}
    ang.update(inlet_angles_deg or {})
    fuel = _assemble(mdot_fuel_kgs, fvt["fuel"], ang["fuel"], r_major_fuel, x_fuel,
                      fuel_r_flow, fuel_wall_t, fuel_feed_p, taper_blend=tb["fuel"])
    ox = _assemble(mdot_ox_kgs, fvt["ox"], ang["ox"], r_major_ox, x_ox,
                    ox_r_flow, ox_wall_t, ox_feed_p, taper_blend=tb["ox"])
    return {"fuel": fuel, "ox": ox, "total_mass_kg": fuel["mass_kg"] + ox["mass_kg"]}


def size_jacket_manifolds(mdot_fuel_kgs, rho_fuel, cooling_flow_topology, bypass_fraction,
                           jacket_inlet_pressure_pa, jacket_return_pressure_pa,
                           chamber_dia_m, local_bore_dia_m,
                           injector_inlet_x_m, jacket_end_x_m,
                           feed_velocity_target_ms, turnaround_passage_height_m=None,
                           throat_dia_m=None, taper_blend=MANIFOLD_TAPER_BLEND_DEFAULT,
                           inlet_angle_deg=0.0, turnaround_velocity_ms=None,
                           mid_inlet_x_m=None, mid_inlet_dia_m=None):
    """
    Size the regen-cooling jacket's OWN coolant-supply ring(s) - fuel only
    (this tool's coolant is always fuel - see design.py's mdot_fuel_kgs/
    cp_fuel usage throughout cooling.py's calls), distinct from
    size_manifolds()'s injector-feed rings above.

    "single_pass_countercurrent" (default - matches cooling.py's existing
    thermal-march assumption, coolant enters near the nozzle/transition end
    and flows up to the injector): ONE ring, "jacket_inlet", placed at the
    bell end (jacket_end_x_m, sized off local_bore_dia_m there) carrying the
    FULL mdot_fuel_kgs at jacket_inlet_pressure_pa - nothing has been
    bypassed or dropped yet at the point coolant enters the jacket.

    "f1_split_reverse_flow" (real F-1 topology - see module docstring and
    ASSUMPTIONS.md): fuel splits at a manifold near the INJECTOR end - a
    bypass_fraction goes straight to the injector (never modeled here, it's
    already counted in size_manifolds()'s existing fuel ring), the rest goes
    down the jacket to a turnaround at the bell end and back. TWO rings:
    "jacket_inlet" near the forward/injector end (injector_inlet_x_m, sized
    off chamber_dia_m - same regime as the existing fuel/ox rings there),
    carrying the down-leg mdot (mdot_fuel_kgs*(1-bypass_fraction)) at the
    same undropped jacket_inlet_pressure_pa; "jacket_return" at the bell end
    (jacket_end_x_m), a small TURNAROUND collar rather than a header: bore =
    TURNAROUND_BORE_PASSAGE_MULT x turnaround_passage_height_m (the local
    coolant-passage height there), or TURNAROUND_BORE_THROAT_DIA_MULT x
    throat_dia_m (chamber_dia_m if that's None too) when no passage geometry
    is known; seated flush on the local wall (major radius = local_bore_dia_m/2
    + its own outer radius, no collar/clearance inflation). It still reports
    the SAME down-leg mdot (conservation - what goes down must come back) at
    jacket_return_pressure_pa (lower, by the down-leg's own share of the
    jacket's total pressure drop - see JACKET_RETURN_SPLIT_FRACTION), and its
    hoop-stress wall/mass use that pressure on the small bore.

    Reuses _bore_and_wall/_assemble unmodified: passing dp_injector_leg_pa=0.0
    degenerates _bore_and_wall's feed_pressure_pa to exactly the pressure_pa
    passed in here, since a jacket station has no separate "injector dP" term
    to add on top - not a bug, just the same function applied to a station
    where that second term is zero.

    Returns {"jacket_inlet": {...}, "jacket_return": {...} or None,
    "total_mass_kg": float}; each ring dict has the same shape as
    size_manifolds()'s per-propellant dicts (HOOK_POINT_FIELDS included).
    """
    mdot_down = (mdot_fuel_kgs * (1.0 - bypass_fraction)
                 if cooling_flow_topology == "f1_split_reverse_flow" else mdot_fuel_kgs)

    def _ring(mdot_kgs, pressure_pa, ref_dia_m, axial_x_m):
        r_flow, wall_t, p = _bore_and_wall(mdot_kgs, rho_fuel, 0.0, pressure_pa,
                                            feed_velocity_target_ms)
        r_outer = r_flow + wall_t
        base_r = (ref_dia_m / 2.0) * MANIFOLD_COLLAR_R_MULT + MANIFOLD_RING_CLEARANCE_M
        return _assemble(mdot_kgs, feed_velocity_target_ms, inlet_angle_deg, base_r + r_outer,
                          axial_x_m, r_flow, wall_t, p, taper_blend=taper_blend)

    def _turnaround_ring(mdot_kgs, pressure_pa, wall_dia_m, axial_x_m):
        # See TURNAROUND_BORE_PASSAGE_MULT: bore from local passage size, not mdot.
        if turnaround_passage_height_m and turnaround_passage_height_m > 0.0:
            bore_m = TURNAROUND_BORE_PASSAGE_MULT * turnaround_passage_height_m
        else:
            bore_m = TURNAROUND_BORE_THROAT_DIA_MULT * (throat_dia_m or chamber_dia_m)
        r_flow = 0.5 * bore_m
        wall_t = manifold_wall_thickness_m(pressure_pa, r_flow)
        r_outer = r_flow + wall_t
        # A turnaround passes flow tube-to-tube locally, so its real velocity
        # is the local coolant-PASSAGE velocity (turnaround_velocity_ms, from
        # design.py). Only without one does it fall back to the bulk velocity
        # the down-leg would need IF it all ran around this small bore - a
        # purely informational number (it never actually does).
        v_report = (turnaround_velocity_ms if turnaround_velocity_ms
                    else mdot_kgs / (rho_fuel * math.pi * r_flow ** 2))
        return _assemble(mdot_kgs, v_report, inlet_angle_deg, wall_dia_m / 2.0 + r_outer,
                          axial_x_m, r_flow, wall_t, pressure_pa, split=False)

    if cooling_flow_topology == "j2_mid_nozzle_inlet":
        # J-2 layout: the inlet header sits flush on the nozzle wall at the
        # mid-nozzle station (mid_inlet_x_m / mid_inlet_dia_m) carrying the
        # FULL fuel flow down the down-tubes (no bypass - the J-2 has none),
        # sized at the down-tube velocity there; the turnaround collar sits at
        # the cooled end exactly as in the F-1 split topology.
        r_flow, wall_t, p = _bore_and_wall(mdot_fuel_kgs, rho_fuel, 0.0,
                                            jacket_inlet_pressure_pa, feed_velocity_target_ms)
        jacket_inlet = _assemble(mdot_fuel_kgs, feed_velocity_target_ms, inlet_angle_deg,
                                 mid_inlet_dia_m / 2.0 + r_flow + wall_t, mid_inlet_x_m,
                                 r_flow, wall_t, p, taper_blend=taper_blend)
        jacket_return = _turnaround_ring(mdot_fuel_kgs, jacket_return_pressure_pa,
                                         local_bore_dia_m, jacket_end_x_m)
        return {"jacket_inlet": jacket_inlet, "jacket_return": jacket_return,
                "total_mass_kg": jacket_inlet["mass_kg"] + jacket_return["mass_kg"]}

    if cooling_flow_topology == "f1_split_reverse_flow":
        jacket_inlet = _ring(mdot_down, jacket_inlet_pressure_pa, chamber_dia_m,
                              injector_inlet_x_m)
        jacket_return = _turnaround_ring(mdot_down, jacket_return_pressure_pa, local_bore_dia_m,
                                          jacket_end_x_m)
        return {"jacket_inlet": jacket_inlet, "jacket_return": jacket_return,
                "total_mass_kg": jacket_inlet["mass_kg"] + jacket_return["mass_kg"]}

    jacket_inlet = _ring(mdot_down, jacket_inlet_pressure_pa, local_bore_dia_m, jacket_end_x_m)
    return {"jacket_inlet": jacket_inlet, "jacket_return": None,
            "total_mass_kg": jacket_inlet["mass_kg"]}


if __name__ == "__main__":
    # F-1-class smoke case: mdot_fuel ~789 kg/s RP-1, mdot_ox ~1791 kg/s LOX,
    # Pc 7 MPa, negligible injector dP for a clean nominal-case check.
    mdot_fuel, mdot_ox = 789.0, 1791.0
    rho_fuel_ref, rho_ox_ref = 810.0, 1141.0
    pc_feed = 7.0e6
    dp_leg = 1.2e6

    result = size_manifolds(mdot_fuel, mdot_ox, rho_fuel_ref, rho_ox_ref, pc_feed, dp_leg, dp_leg,
                             chamber_dia_m=0.9)
    fuel, ox = result["fuel"], result["ox"]

    # Bore lands in a sane multi-cm-to-sub-meter range (F-1-class flow is
    # enormous - ~1791 kg/s of LOX alone) - not mm, not multi-meter.
    assert 0.05 < fuel["inner_diameter_m"] < 0.7, fuel["inner_diameter_m"]
    assert 0.05 < ox["inner_diameter_m"] < 0.7, ox["inner_diameter_m"]
    # No overlap by construction: the rings sit at different axial stations
    # (not stacked radially), each ring's own radius independent of the
    # other's - ox's near axial edge clears fuel's far axial edge.
    fuel_x_far = fuel["attach_axial_station_m"] + fuel["outer_radius_m"]
    ox_x_near = ox["attach_axial_station_m"] - ox["outer_radius_m"]
    assert ox_x_near >= fuel_x_far, (fuel_x_far, ox_x_near)
    # Each ring's own radius depends only on its own size now (no more
    # "ox_major = fuel_major + fuel_outer + gap + ox_outer" relationship).
    assert ox["major_radius_m"] != fuel["major_radius_m"] + fuel["outer_radius_m"] + ox["outer_radius_m"]
    assert ox["mass_kg"] > 0.0 and fuel["mass_kg"] > 0.0
    assert result["total_mass_kg"] == fuel["mass_kg"] + ox["mass_kg"]

    # Mass scales up with a 10x mdot bump at the same velocity target.
    result_10x = size_manifolds(mdot_fuel * 10.0, mdot_ox * 10.0, rho_fuel_ref, rho_ox_ref,
                                 pc_feed, dp_leg, dp_leg, chamber_dia_m=0.9)
    assert result_10x["total_mass_kg"] > result["total_mass_kg"]

    # Warnings silent on the nominal case ...
    assert thin_wall_warning(fuel["thin_wall_ratio"], "Fuel") is None
    assert bore_vs_chamber_warning(fuel["inner_diameter_m"], 0.9, "Fuel") is None
    # ... but fire on deliberately pathological inputs. thin_wall_ratio =
    # SAFETY_FACTOR*pressure/sigma_allow is independent of radius/velocity
    # (both the numerator wall_t and the denominator r_flow scale together),
    # so only an extreme PRESSURE triggers it - a tiny velocity target
    # instead blows up the bore diameter, which is what bore_vs_chamber_
    # warning catches.
    hi_p_result = size_manifolds(mdot_fuel, mdot_ox, rho_fuel_ref, rho_ox_ref,
                                  pc_feed_pa=1.5e8, dp_injector_fuel_pa=dp_leg,
                                  dp_injector_ox_pa=dp_leg, chamber_dia_m=0.9)
    assert thin_wall_warning(hi_p_result["fuel"]["thin_wall_ratio"], "Fuel") is not None
    tiny_v_result = size_manifolds(mdot_fuel, mdot_ox, rho_fuel_ref, rho_ox_ref, pc_feed,
                                    dp_leg, dp_leg, chamber_dia_m=0.9,
                                    feed_velocity_target_ms={"fuel": 0.05, "ox": 0.05})
    assert bore_vs_chamber_warning(tiny_v_result["fuel"]["inner_diameter_m"], 0.9, "Fuel") is not None

    # HOOK_POINT_FIELDS are all present on every per-propellant result.
    for field in HOOK_POINT_FIELDS:
        assert field in fuel and field in ox, field

    # Attachment direction: fuel at 0deg -> +y, ox at 180deg -> -y.
    assert abs(fuel["attach_direction_xyz"][1] - 1.0) < 1e-9
    assert abs(ox["attach_direction_xyz"][1] + 1.0) < 1e-9

    # Split + taper (Round 4): the ring's inlet bore carries HALF the flow, the
    # hook's feed bore (inner_diameter_m) the full flow at the same velocity.
    assert abs(fuel["inner_diameter_m"] - math.sqrt(2.0) * fuel["ring_inlet_inner_diameter_m"]) < 1e-12
    assert abs(ring_flow_radius_at(fuel, fuel["attach_angular_position_deg"])
               - fuel["inlet_flow_radius_m"]) < 1e-12
    assert abs(ring_flow_radius_at(fuel, fuel["attach_angular_position_deg"] + 180.0)
               - fuel["min_flow_radius_m"]) < 1e-12
    assert fuel["min_flow_radius_m"] < fuel["inlet_flow_radius_m"]
    # Symmetric branches; outer radius = local bore x (1 + t/r).
    assert abs(ring_flow_radius_at(fuel, 90.0) - ring_flow_radius_at(fuel, -90.0)) < 1e-12
    assert abs(ring_outer_radius_at(fuel, 0.0) - fuel["outer_radius_m"]) < 1e-12
    # Blend 0 = constant section: numeric tapered mass == closed-form torus mass.
    _k = fuel["thin_wall_ratio"]
    _r = fuel["inlet_flow_radius_m"]
    assert abs(tapered_ring_mass_kg(0.5, _r, _k, 0.0)
               - manifold_ring_mass_kg(0.5, _r, _k * _r)) < 1e-9
    # Blend 0.5 (no floor hit) averages 0.75 of the inlet area -> 0.75x the mass.
    assert abs(tapered_ring_mass_kg(0.5, _r, _k, 0.5) / tapered_ring_mass_kg(0.5, _r, _k, 0.0)
               - 0.75) < 1e-9
    # Full constant-velocity taper bottoms out at the fabrication floor.
    assert abs(taper_area_fraction(180.0, 1.0) - MANIFOLD_TAPER_MIN_AREA_FRACTION) < 1e-12
    # Inlet angle follows the caller (e.g. a plumbing run's attach angle).
    _rot = size_manifolds(mdot_fuel, mdot_ox, rho_fuel_ref, rho_ox_ref, pc_feed, dp_leg, dp_leg,
                          chamber_dia_m=0.9, inlet_angles_deg={"fuel": 90.0})
    assert _rot["fuel"]["attach_angular_position_deg"] == 90.0
    assert _rot["ox"]["attach_angular_position_deg"] == 180.0
    assert abs(_rot["total_mass_kg"] - result["total_mass_kg"]) < 1e-9

    # Scroll ring (tangential one-way volute): full-flow inlet = feed bore,
    # monotone taper along the flow (either handedness), tail on the floor,
    # blend 0 = the closed-form constant ring, hook direction = the tangent.
    for _sd in (1, -1):
        _sc = _assemble(10.0, 20.0, 30.0, 1.0, 0.5, 0.1, 0.002, 1e6, taper_blend=1.0,
                        kind=RING_KIND_SCROLL, scroll_dir=_sd)
        assert _sc["ring_kind"] == RING_KIND_SCROLL and _sc["inner_diameter_m"] == 0.2
        _along = [ring_flow_radius_at(_sc, 30.0 + _sd * a) for a in range(0, 360, 10)]
        assert all(a >= b for a, b in zip(_along, _along[1:])) and _along[0] == 0.1
        assert abs(ring_flow_radius_at(_sc, 30.0 - _sd * 1e-6) ** 2 / 0.01
                   - MANIFOLD_TAPER_MIN_AREA_FRACTION) < 1e-9
        _t = (0.0, -math.sin(math.radians(30.0)), math.cos(math.radians(30.0)))
        assert abs(sum(a * b for a, b in zip(_sc["attach_direction_xyz"], _t)) + _sd) < 1e-12
    assert abs(scroll_area_fraction(180.0, 1.0) - 0.5) < 1e-12
    assert abs(tapered_ring_mass_kg(0.5, _r, _k, 0.0, kind=RING_KIND_SCROLL)
               - manifold_ring_mass_kg(0.5, _r, _k * _r)) < 1e-9

    # Regression anchor (pinned reference value on this fixed scenario).
    assert abs(result["total_mass_kg"] - 92.57425407529384) / 92.57425407529384 < 1e-9, \
        result["total_mass_kg"]

    print(f"manifold.py smoke test OK - F-1-class: fuel ID {fuel['inner_diameter_m']*1000:.0f} mm "
          f"({fuel['mass_kg']:.1f} kg), ox ID {ox['inner_diameter_m']*1000:.0f} mm "
          f"({ox['mass_kg']:.1f} kg), total {result['total_mass_kg']:.1f} kg")

    # Velocity-head law: the default fraction reproduces the RS-29-class
    # kerolox header velocities the old flat baseline gave (~15 m/s RP-1 at
    # ~2.16 MPa injector dP), and a low-density propellant runs faster at the
    # same head (the 1/sqrt(rho) law, now a consequence).
    _v_rp1 = velocity_from_head_fraction(MANIFOLD_VELOCITY_HEAD_FRACTION_DEFAULT, 2.16e6, 810.0)
    assert 13.0 < _v_rp1 < 17.0, _v_rp1
    _v_lh2 = velocity_from_head_fraction(MANIFOLD_VELOCITY_HEAD_FRACTION_DEFAULT, 2.16e6, 71.0)
    assert abs(_v_lh2 / _v_rp1 - math.sqrt(810.0 / 71.0)) < 1e-9
    # SP-8087 liquid cap: silent below 61 m/s, fires above, skipped for LH2.
    assert velocity_cap_warning(50.0, "Fuel") is None
    assert velocity_cap_warning(70.0, "Fuel") is not None
    assert velocity_cap_warning(135.0, "Fuel", supercritical=True) is None

    # --- size_jacket_manifolds (Round 2) smoke test, same F-1-class scenario ---
    jacket_p_in = pc_feed + dp_leg + 1.5e6   # a plausible jacket_dp_pa on top
    jacket_p_ret = jacket_p_in - 1.5e6 * JACKET_RETURN_SPLIT_FRACTION
    fvt_fuel = FEED_VELOCITY_TARGET_MS["fuel"]

    single = size_jacket_manifolds(
        mdot_fuel, rho_fuel_ref, "single_pass_countercurrent", MANIFOLD_BYPASS_FRACTION_DEFAULT,
        jacket_p_in, jacket_p_ret, chamber_dia_m=0.9, local_bore_dia_m=1.8,
        injector_inlet_x_m=1.0, jacket_end_x_m=6.0, feed_velocity_target_ms=fvt_fuel)
    assert single["jacket_return"] is None
    assert single["jacket_inlet"]["mdot_kgs"] == mdot_fuel
    assert single["total_mass_kg"] == single["jacket_inlet"]["mass_kg"] > 0.0

    split = size_jacket_manifolds(
        mdot_fuel, rho_fuel_ref, "f1_split_reverse_flow", MANIFOLD_BYPASS_FRACTION_DEFAULT,
        jacket_p_in, jacket_p_ret, chamber_dia_m=0.9, local_bore_dia_m=1.8,
        injector_inlet_x_m=1.0, jacket_end_x_m=6.0, feed_velocity_target_ms=fvt_fuel)
    assert split["jacket_return"] is not None
    _down_mdot = mdot_fuel * (1.0 - MANIFOLD_BYPASS_FRACTION_DEFAULT)
    assert abs(split["jacket_inlet"]["mdot_kgs"] - _down_mdot) < 1e-6
    assert abs(split["jacket_return"]["mdot_kgs"] - _down_mdot) < 1e-6
    assert split["total_mass_kg"] == (split["jacket_inlet"]["mass_kg"]
                                       + split["jacket_return"]["mass_kg"])

    # Non-overlap: split topology's forward jacket_inlet ring sits at
    # injector_inlet_x_m, downstream of wherever the caller placed it (the
    # caller is responsible for clearing the existing ox ring - this test
    # just checks the ring built at that station doesn't poke back upstream
    # of its own near edge, i.e. a sane, non-negative placement).
    _ji = split["jacket_inlet"]
    assert _ji["attach_axial_station_m"] - _ji["outer_radius_m"] >= 0.0

    # jacket_return is a small turnaround collar (TURNAROUND_BORE_*), not a
    # header: much smaller bore than the forward jacket_inlet ring, seated
    # flush on the local wall. No passage height given here -> throat-dia
    # fallback (chamber_dia_m, since throat_dia_m is None too).
    _jr = split["jacket_return"]
    assert _jr["inner_diameter_m"] < 0.4 * _ji["inner_diameter_m"], (_jr, _ji)
    assert abs(_jr["inner_diameter_m"] - TURNAROUND_BORE_THROAT_DIA_MULT * 0.9) < 1e-12
    assert abs(_jr["major_radius_m"] - (1.8 / 2.0 + _jr["outer_radius_m"])) < 1e-12
    # ... and with a real passage height, the bore follows it instead.
    split_passage = size_jacket_manifolds(
        mdot_fuel, rho_fuel_ref, "f1_split_reverse_flow", MANIFOLD_BYPASS_FRACTION_DEFAULT,
        jacket_p_in, jacket_p_ret, chamber_dia_m=0.9, local_bore_dia_m=1.8,
        injector_inlet_x_m=1.0, jacket_end_x_m=6.0, feed_velocity_target_ms=fvt_fuel,
        turnaround_passage_height_m=0.02, throat_dia_m=0.9)
    assert abs(split_passage["jacket_return"]["inner_diameter_m"]
               - TURNAROUND_BORE_PASSAGE_MULT * 0.02) < 1e-12

    # Mass shrinks as more fuel bypasses the jacket (smaller down-leg flow ->
    # smaller bore), pressure/velocity held fixed.
    split_hi_bypass = size_jacket_manifolds(
        mdot_fuel, rho_fuel_ref, "f1_split_reverse_flow", MANIFOLD_BYPASS_FRACTION_MAX,
        jacket_p_in, jacket_p_ret, chamber_dia_m=0.9, local_bore_dia_m=1.8,
        injector_inlet_x_m=1.0, jacket_end_x_m=6.0, feed_velocity_target_ms=fvt_fuel)
    assert split_hi_bypass["total_mass_kg"] < split["total_mass_kg"]

    # Regression anchors (pinned reference values on this fixed scenario).
    assert abs(single["total_mass_kg"] - 65.51400670477112) / 65.51400670477112 < 1e-9, \
        single["total_mass_kg"]
    assert abs(split["total_mass_kg"] - 29.365293410038632) / 29.365293410038632 < 1e-9, \
        split["total_mass_kg"]

    print(f"size_jacket_manifolds smoke test OK - single-pass jacket_inlet "
          f"{single['jacket_inlet']['mass_kg']:.2f} kg; split-topology jacket_inlet "
          f"{split['jacket_inlet']['mass_kg']:.2f} kg + jacket_return "
          f"{split['jacket_return']['mass_kg']:.2f} kg = {split['total_mass_kg']:.2f} kg")
