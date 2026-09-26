"""
Cosmetic-only mesh-detail constants (no physics meaning, no validate.py
spot-check implication) for the OpenGL 3D preview's hardware/geometry
builders in this package - flange/ring/hatband/bolt/manifold/duct sizing
multipliers and the visual channel-count cap. Split out of the former
single-file gui/preview3d_gl_core.py as pure data with no self-test (see
that module's __init__.py for the package overview).
"""
# Cosmetic-only mesh-detail constants (no physics meaning, no validate.py
# spot-check implication - purely how much visual detail the solid-shell
# builder below adds on top of the real per-station numbers it's given).
VISUAL_CHANNEL_COUNT_MAX = 500   # safety-valve cap on drawn ribs/tubes only, not
                                  # a legibility choice: the real physical count
                                  # (cooling.channel_count(), calibrated to real
                                  # engines - F-1 ~178, SSME ~390, RL10 ~180, see
                                  # physics/cooling.py:543) IS the realistic look
                                  # (this is what F-1/RL10 reference photos show -
                                  # many thin tubes, not a handful of fat ones);
                                  # rendering/self-tests already handle hundreds
                                  # of discrete tube meshes fine. Only an unusual
                                  # design forcing an extreme channel-count
                                  # override would ever actually hit this cap.
FLANGE_HALF_WIDTH_THROAT_DIA_MULT = 0.05   # flange collar half-width, x throat diameter -
                                            # throat-diameter-relative like HATBAND_*/BOLT_*
                                            # below, not local-wall-thickness-relative: a
                                            # correctly-thin nozzle-extension skirt wall
                                            # (sub-mm once wall thickness uses local static
                                            # pressure past the throat) would make a
                                            # thickness-relative flange imperceptible.
FLANGE_HEIGHT_THROAT_DIA_MULT = 0.04       # flange collar height, x throat diameter
RING_SPACING_THROAT_DIA_MULT = 2.5   # nozzle stiffening-ring spacing, x throat diameter
RING_HALF_WIDTH_FACTOR = 1.5     # stiffening-ring half-width, x local wall thickness
RING_HEIGHT_FACTOR = 0.3         # stiffening-ring height, x local wall thickness
ORTHOGRID_RIB_SPACING_THROAT_DIA_MULT = 1.2   # orthogrid rib pitch (both circumferential
                                  # and axial), x throat diameter - cosmetic/rendering only,
                                  # same tier as RING_SPACING_THROAT_DIA_MULT above. The
                                  # MASS implication of an orthogrid pattern lives solely in
                                  # mass_model.ORTHOGRID_MASS_FRACTION, kept deliberately
                                  # separate from this purely-visual rib density.
ORTHOGRID_POCKET_DEPTH_FRACTION = 0.5   # orthogrid pocket recess depth, x local wall
                                  # thickness (clamped to 0.6x by tube_bundle.
                                  # orthogrid_modulated_grid regardless) - cosmetic/
                                  # rendering only, no mass/physics implication.
ORTHOGRID_RIB_FRACTION = 0.2     # orthogrid rib width as a fraction of the pitch, in
                                  # EACH direction (theta and axial) - cosmetic only.
TUBE_BRAZE_SEAM_FRAC = 0.03   # tube_wall: each drawn tube's circumferential width is
                               # (1 - this) x the local centre-to-centre chord, so
                               # neighbouring tubes always touch across a thin braze seam
                               # (a real brazed bundle is contiguous: tubes are swaged,
                               # then "spanked" round/oval to fill the pitch at every
                               # station [Huzel p.113-114; SP-8087 Sec.2.1.1.3 p.12-13]).
                               # Cosmetic tier: the seam width itself is just legibility.
CHANNEL_OUTER_JACKET_M = 1.0e-3  # thin structural wrap over a tube/channel bundle -
                                  # cosmetic/rendering only, no physics implication.
MANIFOLD_TUBE_R_THROAT_DIA_MULT = 0.03  # far-end coolant-return manifold ring cross-
                                         # section radius, x throat diameter - sized off
                                         # throat diameter rather than local effective
                                         # (wall + channel) thickness. That thickness
                                         # varies non-monotonically along the profile
                                         # (it tracks the coolant-channel-height march,
                                         # not a smooth structural taper), so a manifold
                                         # placed at a station where it happens to be
                                         # tiny rendered as an imperceptible sliver
                                         # (looking "missing"), while a station where it
                                         # happens to be large rendered as a hugely
                                         # oversized ring - both symptoms reported in the
                                         # same session, both from the same root cause.
                                         # Same fix already applied to hatbands: drop the
                                         # thickness dependency, use a fixed, predictable
                                         # throat-diameter proportion instead.
DUCT_APPROACH_STANDOFF_BEND_RADIUS_MULT = 2.5  # bent_tube_duct_mesh demo (fuel main-inlet
                                         # duct stub, gui/preview3d_gl.py): distance of the
                                         # corner waypoint from the manifold ring's own
                                         # hook point, x the duct's OWN bend_radius_m (NOT
                                         # throat_dia_m - an earlier version sized this off
                                         # throat diameter while the bend radius is sized off
                                         # the duct's tube diameter, an independent reference
                                         # that could fall short of fillet_polyline's own
                                         # trim distance whenever the manifold tube is fat
                                         # relative to the throat, tripping its clamp guard
                                         # on real designs (confirmed via a real-run warning)
                                         # - sizing this off the SAME radius the fillet
                                         # actually needs to fit avoids that by construction.
                                         # The waypoint sits OUTWARD of the hook point along
                                         # +attach_direction_xyz (the ring's own outward
                                         # normal), so the final segment travels along
                                         # -attach_direction_xyz into the ring - the hook
                                         # point's own documented approach direction (see
                                         # physics/manifold.py's HOOK_POINT_FIELDS comment) -
                                         # without needing a second explicit bend. Paired with
                                         # DUCT_STUB_LENGTH_BEND_RADIUS_MULT below (both legs
                                         # meet at the same corner, so both need the same
                                         # bend-radius-scaled safety margin) - reduced from an
                                         # earlier 3.0 (shorter arm, requested after seeing the
                                         # duct in a real run) while staying above the
                                         # ~2.1x-bend-radius minimum a ~90-degree corner needs
                                         # to clear fillet_polyline's 0.49x-segment-length
                                         # clamp guard. Cosmetic/rendering only, arbitrary-but-
                                         # reasonable; the clamp guard remains a legitimate
                                         # backstop for any geometry sharp enough to still
                                         # exceed it.
DUCT_STUB_LENGTH_BEND_RADIUS_MULT = 2.1  # RAW (pre-trim) length of the short stub past the
                                         # bend (the duct's upstream terminus, capped) - x
                                         # the duct's OWN bend_radius_m. This is NOT the
                                         # visible straight length after the fillet arc -
                                         # fillet_polyline trims bend_radius_m/tan(half the
                                         # corner angle) off each incident segment before
                                         # placing the arc, and this corner's angle is always
                                         # exactly 90 degrees by construction (the stub's
                                         # direction is pure axial, the ring's outward normal
                                         # is pure radial, always perpendicular), so the trim
                                         # here is always exactly 1x bend_radius_m. A raw
                                         # length of 2.0x would put the VISIBLE stub at
                                         # exactly 1x bend_radius (the requested length) but
                                         # sits inside fillet_polyline's own clamp guard,
                                         # which fires whenever trim exceeds 0.49x of the
                                         # shorter adjacent segment - i.e. the raw segment
                                         # must exceed 1.0/0.49 ~= 2.04x bend_radius_m to
                                         # avoid re-triggering the exact clamp warning fixed
                                         # two rounds ago. 2.1x leaves a small, deliberate
                                         # safety margin over that threshold, so the visible
                                         # post-arc stub ends up ~1.1x bend_radius_m - as
                                         # close to a clean 1x as it can safely get. Cosmetic/
                                         # rendering only, arbitrary-but-reasonable.
DUCT_BEND_RADIUS_TUBE_DIA_MULT = 0.5    # fillet_polyline bend radius, x the duct's own
                                         # tube DIAMETER (2x inner_diameter_m/2). User-
                                         # confirmed visual default (via gui/app.py's debug
                                         # "duct bend radius" slider, checked against
                                         # rs-29.json), not a real-pipe-elbow bend-ratio
                                         # computation - cosmetic/rendering only, no
                                         # structural or physics implication.
MANIFOLD_RING_WALL_CLEARANCE_M = 0.005  # gui/mesh_builder.py: radial gap between the real
                                         # rendered chamber/bell wall and a manifold ring's
                                         # (fuel/ox injector-feed OR jacket coolant-supply)
                                         # own inner edge, when snapping
                                         # the ring's RENDER position onto that real wall
                                         # (Option A - see this round's plan) instead of
                                         # physics/manifold.py's formula-derived
                                         # major_radius_m, which has no idea what the real
                                         # wall (thickness/regen jacket/tube ribs) looks like.
                                         # A separate constant from physics/manifold.py's own
                                         # MANIFOLD_RING_CLEARANCE_M (collar-to-ring, a
                                         # different gap entirely) - this one is rendering-
                                         # only and deliberately not conflated with it.
                                         # Small and fixed rather than throat-diameter-scaled
                                         # since it's just meant to avoid an exact-zero-gap
                                         # z-fighting seam, not a real structural clearance.
FLANGE_HARDWARE_CLEARANCE_MARGIN_M = 0.005  # extra ABSOLUTE margin (5mm), not throat-
                                         # diameter-scaled, added on top of the flange-
                                         # plate-half-width + bolt-head-reach when
                                         # shifting the single-pass manifold ring clear of
                                         # a real bolted-flange joint (see gui/
                                         # preview3d_gl.py's manifold_clear_of_flange_x
                                         # call) - the throat-diameter-relative terms
                                         # alone can shrink to a fraction of a mm on a
                                         # small engine, reading as still touching/
                                         # grazing the bolt heads on a real render.
                                         # Arbitrary-but-reasonable, chosen to read as a
                                         # clean visual gap regardless of engine scale.
TUBE_END_CAP_HALF_WIDTH_THROAT_DIA_MULT = 0.06  # F-1-style double-pass turnaround
                                         # end-cap band half-width, x throat diameter -
                                         # a fixed-size opaque collar covering the sharp
                                         # edge where discrete tube geometry HARD-STOPS
                                         # (no taper - see gui/preview3d_gl.py's
                                         # channel_heights hard cutoff) at the far-end
                                         # cover's own x position, hiding the step in
                                         # the outer wall envelope there (the channel/
                                         # tube height's contribution to wall offset
                                         # drops to zero). Since 2026-09-22 this band IS
                                         # the drawn fuel RETURN (turnaround) manifold
                                         # under f1_split_reverse_flow - the separate
                                         # jacket_return torus is no longer rendered
                                         # (gui/mesh_builder.py) - and was halved from
                                         # 0.12 per user direction to read as the small
                                         # real F-1 return manifold (heroicrelics photo),
                                         # now narrower than
                                         # HATBAND_HALF_WIDTH_THROAT_DIA_MULT (0.08).
                                         # Cosmetic/rendering only,
                                         # arbitrary-but-reasonable.
TUBE_COVER_PENETRATION_RING_FRACTION = 1.0  # how far past the manifold ring's own
                                         # CENTER (x its own cross-section radius) a
                                         # single_pass_upflow pipe's termination pushes -
                                         # 1.0 means all the way to the ring's own FAR
                                         # (downstream) axial edge, spanning the ring's
                                         # entire axial footprint rather than stopping at
                                         # its center. An earlier round tried solving for
                                         # where the pipe's own (essentially zero-width,
                                         # centerline) path genuinely crosses INSIDE the
                                         # ring's solid torus volume - geometrically real,
                                         # but capped by the LOCAL bell slope: the closest
                                         # approach achievable by pure axial motion is
                                         # ring_r/sqrt(1+slope^2), which for the shallow
                                         # slopes typical of a real bell is barely below
                                         # ring_r - a few percent at best, often not even
                                         # visually perceptible. Spanning the ring's whole
                                         # width instead is slope-independent and always
                                         # reads as "the pipe runs through the ring," not
                                         # "the pipe barely grazes the ring's surface."
                                         # Cosmetic/rendering only, arbitrary-but-
                                         # reasonable.
TUBE_COVER_PENETRATION_BAND_FRACTION = 0.25  # same "push the pipe termination past the
                                         # cover's own center" idea as the ring constant
                                         # above, but a smaller fraction suffices here -
                                         # the band is already much wider than the ring
                                         # (TUBE_END_CAP_HALF_WIDTH_THROAT_DIA_MULT vs.
                                         # MANIFOLD_TUBE_R_THROAT_DIA_MULT), so a modest
                                         # push clears its near edge with margin ("just
                                         # inside," not deep through it) without needing
                                         # to span its full width. Cosmetic/rendering
                                         # only, arbitrary-but-reasonable.
HATBAND_SPACING_THROAT_DIA_MULT = 1.5   # bell hatband spacing, x throat diameter (tighter
                                         # than the stiffening rings' 2.5 - a strap
                                         # convention reads better closer-spaced)
# Hatbands are drawn as separate, discrete ring meshes sitting PROUD of the
# tube crests (not baked into the same offset-profile envelope the tubes are
# computed from) - sized off throat diameter, not local wall thickness, since
# a nozzle-extension skirt's wall thickness can be a fraction of a mm (see
# effective_offset_thickness_m's own docstring) and a band scaled to that is
# imperceptible on a meter-scale engine. This trades a little physical
# precision for actually being visible, the same tradeoff VISUAL_CHANNEL_
# COUNT_MAX/CHANNEL_OUTER_JACKET_M already make elsewhere in this file.
HATBAND_HALF_WIDTH_THROAT_DIA_MULT = 0.08   # hatband half-width, x throat diameter
HATBAND_HEIGHT_THROAT_DIA_MULT = 0.03       # hatband protrusion height (above the
                                             # tube crest), x throat diameter
HATBAND_CLEARANCE_THROAT_DIA_MULT = 0.006   # small standoff gap above the tube
                                             # crest before the band itself starts
HATBAND_SHELL_SLEEVE_THROAT_DIA_MULT = 0.008  # radial thickness of the smooth sleeve drawn
                                             # over the continuous-shell region aft of the
                                             # throat (physics/hatbands.py shell_start/end),
                                             # x throat diameter - cosmetic only (its mass is
                                             # the tube_wall jacket-structure line item)
HARDWARE_SPECULAR_STRENGTH = 0.55   # generic gray hardware (injector collar, coolant
                                     # manifold rings, tube hatbands) not tied to a
                                     # Material lookup - cosmetic/rendering only, same
                                     # tier as color_hex, picked to read as "polished
                                     # steel fitting."
HARDWARE_SHININESS = 65.0           # see HARDWARE_SPECULAR_STRENGTH
BOLT_SPACING_THROAT_DIA_MULT = 0.05   # target arc spacing between bolt-head centers
                                       # around the flange OD, x throat diameter -
                                       # cosmetic/rendering only, same "throat-diameter-
                                       # relative" convention as HATBAND_SPACING_THROAT_
                                       # DIA_MULT/MANIFOLD_TUBE_R_THROAT_DIA_MULT, not a
                                       # real bolt-pattern calculation.
BOLT_HEAD_RADIUS_THROAT_DIA_MULT = 0.015   # bolt-head cylinder radius, x throat diameter
BOLT_HEAD_LENGTH_THROAT_DIA_MULT = 0.02    # bolt-head radial protrusion length, x throat diameter
BOLT_N_THETA_CYL = 8                  # sides per bolt-head cylinder (octagonal
                                       # approximation - cheap, reads fine at hardware scale)
BOLT_MIN_COUNT = 12
BOLT_MAX_COUNT = 150                  # render-sanity cap, same spirit as VISUAL_CHANNEL_COUNT_MAX
