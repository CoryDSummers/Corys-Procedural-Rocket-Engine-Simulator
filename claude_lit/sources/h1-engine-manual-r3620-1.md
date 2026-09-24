# [H1-Man] — H-1 Rocket Engine Technical Manual, Engine Data (H-1C/H-1D)

## Identity

- **Title**: Rocketdyne *H-1 Rocket Engine* technical manual, Section I (description) +
  Section III (performance) — the Saturn I/IB H-1C (inboard, fixed) and H-1D (outboard,
  gimbaled) engines.
- **Report**: **R-3620-1** (Rocketdyne), change pages dated **Change No. 1 (9 Sep 1966)**
  through **Change No. 6 (9 Sep 1968)**.
- **File**: `literature/H-1C-D_Manual.pdf` (14.4 MB, 78 PDF leaves, scanned with an OCR text
  layer).
- **Extent read**: **targeted only** (2026-09-24). The OCR text layer was extracted with a
  throwaway zlib/`TJ`-operator script, no pymupdf. Sections read: engine description (§1-5/1-6),
  the exhaust system (§1-39..1-51 + Fig 1-20/1-21), the gas generator (Fig 1-28), the turbine
  (§1-101 + Fig 1-47), thrust-chamber characteristics (Fig 1-17/1-18) and line flows
  (Fig 1-56). **Not read**: the valve/sequence/start-system text, section II
  (weights/handling) and most of section III.
- **Page reference**: printed page numbers (`1-25`, `1-28`, ...) are the manual's own and
  appear in the OCR footer of each leaf.

## Character

This is a field/maintenance manual, not a design report. It gives exact hardware
descriptions and a few nominal operating tables, with no derivations. **It is the only source
in `claude_lit` that describes a turbine-exhaust aspirator**, so it closes
`OPEN_QUESTIONS.md` item (g). Numeric tables sometimes OCR as label and value columns out of
order. Where a table lists "Rating at 200K / Rating at 205K" but only one value column is
legible, this note says so.

## Key parameters

| Parameter | Value | Where |
|---|---|---|
| Sea-level thrust (200K / 205K rating) | 199,300 / 204,300 lbf | Fig 1-18 p.1-24 |
| Sea-level Isp (200K / 205K) | 267.9 / 268.7 s | Fig 1-18 |
| Chamber total flow (200K / 205K) | 743.9 / 760.2 lb/s, O/F 2.338 / 2.341 | Fig 1-18 |
| Injector-end Pc (200K / 205K) | 689.3 / 701.8 psia | Fig 1-18 |
| c\* efficiency | 97.6 % | Fig 1-18 |
| Nozzle area ratio | **8:1**; throat dia 16.13 in, exit dia **45.62 in** | Fig 1-17 p.1-23 |
| Chamber | contraction ratio 1.62, L\* 39.10 in, overall length **86.15 in**, 292 tubes, wall 0.012 in | Fig 1-17 |
| Jacket dP | 135 psi at 225 lb/s fuel | Fig 1-18 |
| **GG total flow** | **17.22 lb/s** (200K; Fig 1-56 lists 17.2 / 18.13 lb/s for 200K / 205K engines) | Fig 1-28 p.1-35, Fig 1-56 p.1-64 |
| **GG mixture ratio** | **O/F 0.346** (fuel-rich LOX/RP-1) | Fig 1-28 |
| GG chamber pressure / temperature | value column not legible in OCR (a "629.10" appears next to the pressure row) | Fig 1-28 |
| **Turbine inlet pressure** | **599.0 psia total** (519.0 psia static) | Fig 1-47 p.1-53 |
| **Turbine exit pressure** | **33.8 psia** (the table defines PR as "total inlet / static exhaust" → **≈17.7**) | Fig 1-47 |
| Turbine power / efficiency | 4,007 bhp, **69.59 %** | Fig 1-47 |
| Turbine type | impulse, two-stage, pressure-compounded | §1-101 p.1-50 |

Only one value column of Fig 1-47 is legible. Its values are consistent with either rating.

## Key results — turbine exhaust system (§1-39..1-51, p.1-25..1-28)

- **The two H-1 models differ only in their exhaust system and vehicle attach hardware.**
  - **H-1C (inboard, fixed):** a **curved turbine exhaust duct**.
  - **H-1D (outboard, gimbaled):** an **aspirator** (§1-13, Fig 1-20).
- **The exhaust path is the same on both** (§1-43): turbine → **turbine exhaust hood** →
  **heat exchanger** → aspirator or exhaust duct, "to be directed into the thrust chamber exit
  flow stream".
  - The **heat exchanger** uses the exhaust heat to turn LOX into **GOX for vehicle systems**
    (tank pressurisation).
  - The exhaust is described as "**fuel-rich**".
- **Turbine exhaust hood** (§1-45): a stainless-steel welded elbow. It has two mating flanges,
  two doubler rings, and a **bellows** with an integral liner, which allows the required
  movement.
- **Heat exchanger** (§1-47, Fig 1-21): a welded stainless-steel shell with a **helix-wound
  four-coil** system and coil inlet/outlet manifolds.
  - The turbine exhaust flows through the shell and heats the coils.
  - LOX at turbopump pressure enters **three** of the four coils; the fourth is blanked off.
  - Later changes (MD64/MD66) clamp the top coils against vibration damage.
- **Turbine exhaust duct, H-1C** (§1-49): a **curved stainless-steel** assembly mounted on the
  thrust chamber. It has a mating flange, a forward support bracket, a **bellows section**,
  the curved duct and an aft support bracket.
- **Aspirator, H-1D** (§1-51), quoted in full:
  > "The exhaust gas aspirator is a welded, **Hastelloy C shell** assembly installed over, and
  > extending beyond, the thrust chamber exit on all outboard engines. The aspirator is welded
  > to the thrust chamber forward channel band, located approximately **20 inches forward of
  > the thrust chamber exit**. The aft end of the aspirator is not secured to the thrust
  > chamber. This provides a **0.440-inch clearance** between the thrust chamber fuel return
  > manifold and the aspirator, for the gas generator exhaust gases to escape."

  So the aspirator is a **shroud around the aft ~20 in of the nozzle**. The GG exhaust enters
  its forward end, flows aft in the annulus between the shroud and the nozzle's outer wall,
  and leaves through a **0.440 in annular slot at the exit lip** into the edge of the main
  plume. **[SP-8120]** describes the same "annulus at the exit" pattern for the Atlas
  sustainer. On the Saturn IB it kept the fuel-rich exhaust from recirculating into the base
  of the gimbaled outboard engines.
- **Instrumentation taps** (Fig 1-55): "exhaust hood outlet pressure" (TG2a); "exhaust duct
  inlet pressure / temperature" (TG4a/b, **H-1C only**).

## Derived numbers (computed here, not printed in the manual)

- **GG flow as a fraction of total engine flow**: 17.22 / (743.9 + 17.22) = **2.26 %**, or
  2.31 % of chamber flow.
- **Turbine inlet pressure / main-chamber injector-end Pc**: 599.0 / 689.3 = **0.87**. This
  assumes the Fig 1-47 column is the 200K rating; against 205K it is 599 / 701.8 = 0.85.
- **Aspirator slot area**: π × (45.62 + 2 × wall + 2 × 0.44) × 0.44 ≈ **64-66 in²**. The slot
  sits outside the exit lip and fuel-return manifold, so its true diameter is somewhat larger
  than the 45.62 in exit diameter.
- **Shroud length**: 20 in forward of the exit, on a chamber 86.15 in long overall. That is
  ~23 % of overall length, and ~30-35 % of the throat-to-exit length. The throat-to-exit
  length is not printed; this is an estimate from the contour.

## Section map (printed pages)

- §1-5/1-6 engine description (p.1-1)
- Fig 1-17/1-18 chamber characteristics (p.1-23/1-24)
- §1-39..1-51 exhaust system (p.1-25..1-28)
- Fig 1-20 exhaust system (p.1-26)
- Fig 1-21 heat exchanger (p.1-27)
- Fig 1-28 GG characteristics (p.1-35)
- §1-96..1-102 turbopump/turbine (p.1-49..1-53)
- Fig 1-47 turbine characteristics (p.1-53)
- Fig 1-55 instrumentation taps (p.1-62)
- Fig 1-56 line sizes and flowrates (p.1-64)

## Caveats

- **This is a targeted read.** Most of the manual (valves, start sequence, section II/III) is
  undistilled.
- **Some table values are OCR-garbled or not legible:**
  - the GG chamber temperature, and the GG pressure row;
  - the Fig 1-47 200K/205K column split.
- **Aspirator: the geometry is given, the aerodynamics are not.** The manual gives no
  aspirator thrust, back-pressure or entrainment figure. Any aspirator Isp in
  `engine_designer` is therefore a model (a choked annular slot at the exit plane), anchored
  only by this geometry.
- **The 0.440 in is a clearance, not an effective throat.** It is the gap over the fuel-return
  manifold, which is the minimum passage, so it is the best available proxy for the choked
  slot.
