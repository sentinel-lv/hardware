# Hardware — probe, AFE, power, enclosure

**Owner:** TBD
**Deliverable for M2:** a validated analog front end plus a characterisation dataset.

You are the critical path. PCB fabrication and shipping is 12–18 days including customs, and it cannot be compressed by working harder. Every other track can absorb a slipped week; yours cannot. Order early and order two revisions' worth of components.

## 1. Safety first — read this before touching anything

You are working near mains potential. Non-negotiable:

- All bench work on the energised side goes through an isolation transformer and an RCD.
- Use a variac to bring voltage up from zero; never plug a new setup straight into the wall.
- One person never works alone on an energised bench.
- The probe is non-contact by design. If at any point your test setup requires galvanic contact with a live conductor, stop and redesign the test.
- The scaled demo rig for the finale must be low voltage (≤ 50 V) with a visible physical break mechanism. Do not bring 230 V onto a hackathon stage.

Document your safety setup with photos. Judges from a utility take this seriously, and showing that you do separates you from teams who clearly did not.

## 2. Sensing principle

An energised conductor at 230 V creates a 50 Hz electric field in the surrounding air. A conductive plate placed in that field develops a small displacement current through its stray capacitance to the line — typically sub-picofarad at a few tens of centimetres. Measuring that current gives a signal proportional to line voltage, with no CT, no line tap and no outage required to install.

The engineering problem is entirely one of impedance and shielding. The source impedance is enormous, so the first stage must be a very high input impedance buffer placed as close to the plate as physically possible.

## 3. Analog front end

```
[ sense plate ]
       │     (guard ring around plate, driven at buffer output potential)
       ▼
   JFET / CMOS opamp buffer           TL072, OPA2140, or discrete JFET source follower
   Rin > 1 GΩ, bias resistor 1 GΩ to ground
       ▼
   Band-pass 40–60 Hz                 2nd order Sallen-Key, rejects DC drift and RF
       ▼
   Gain stage, switchable             ×10 / ×100, set at commissioning per standoff
       ▼
   Level shift to 0–3.3 V
       ▼
   MCU ADC
```

Design notes that matter:

- Guard ring, driven, not grounded. A grounded guard shunts your signal. Drive it from the buffer output so the guard sits at the same potential as the plate and stray capacitance to it carries no current.
- Keep the plate-to-buffer trace under 10 mm. Put the buffer directly behind the plate on the PCB.
- Use a PTFE standoff or guarded PCB layout for the bias resistor; surface leakage across FR4 at 1 GΩ scale is real, especially in Kerala humidity. Consider a conformal coating.
- Provide a calibration input — a small known-amplitude 50 Hz injection so the node can self-test daily and report AFE health.

## 4. Characterisation — this is your deliverable, not the PCB

The PCB is a means. The dataset is what makes the project credible. For a fixed test conductor, sweep and log:

| Variable | Range | Why |
|----------|-------|-----|
| Standoff distance | 10–80 cm | determines mounting spec and gain setting |
| Angular position | 0–90° off perpendicular | mounting tolerance |
| Temperature | ambient to 55 °C | enclosure heating in Kerala sun |
| Relative humidity | 40–95% | monsoon; expect leakage effects |
| Simulated rain | spray bottle on enclosure | quantify the false-positive scenario |
| Adjacent conductor | second energised line 1 m away | crosstalk, three-phase reality |
| Line voltage | 50–250 V via variac | linearity |

Output: a CSV in `hardware/data/`, plus plots. Then hand this to the simulator owner so the synthetic signal model is re-fitted to real probe behaviour instead of a guess.

The rain and humidity rows are the ones a KSEBL engineer will ask about. Have the numbers.

## 5. Power

| Component | Spec |
|-----------|------|
| Panel | 6 V, 1 W polycrystalline |
| Cell | 1 × 18650 LiFePO4, 1500 mAh |
| Charger | CN3791 MPPT or TP5000 for LiFePO4 chemistry |
| Regulator | low-Iq LDO, quiescent < 10 µA |
| Budget | 5 days autonomy in monsoon overcast |

LiFePO4 over Li-ion: it survives the temperature range on a pole and does not vent violently. Say so in the PPT — it reads as field awareness.

## 6. BOM target

Under ₹1,800 per node at prototype quantity. Maintain `hardware/BOM.csv` with live pricing and a projected 1,000-unit cost. A cost-effectiveness claim in the problem statement means the panel will ask for the number.

**Budget status (auto-checked by `hardware/tests/test_bom.py`, currently RED):**
priced rows sum to **₹1,755** with the IP65 enclosure + clamp + jig still at ₹0/TBD —
over target as specced. Do not hide this: either find ~₹300+ of cost-down
(single probe+node PCB, 1k-unit SX1262 pricing into a separate column,
ESP32-C3 variant) or re-scope the target with Pranav before the finale.
Filling the enclosure row green while the sum exceeds ₹1,800 fails the build.

## 7. Task list

### Phase 1 — breadboard (start today)

- [ ] Source components; order extras of everything
- [ ] Build buffer + band-pass + gain on breadboard
- [ ] Safe bench setup: isolation transformer, variac, RCD, documented with photos
- [ ] First signal: scope the output with a conductor energised at 230 V, 30 cm standoff
- [ ] Confirm output collapses when the conductor is de-energised

### Phase 2 — characterisation → M2

- [ ] Run the full sweep in §4, log to `data/`
- [ ] Plot standoff vs. output, temperature drift, humidity effect
- [ ] Rain test, quantified
- [ ] Hand the dataset to `simulator/` for signal-model re-fit

### Phase 3 — PCB

- [ ] KiCad schematic, reviewed by a second person before ordering
- [ ] 2-layer layout: guard ring geometry, short plate trace, guarded bias resistor
- [ ] DRC clean, JLCPCB fab + assembly order placed
- [ ] Order two revisions' worth of parts

### Phase 4 — bring-up

- [ ] Power rails, quiescent current measurement
- [ ] AFE output matches breadboard characterisation
- [ ] Solar charge cycle verified over a full day
- [ ] Measured average current < 5 mA with firmware running

### Phase 5 — mechanical

- [ ] IP65 off-the-shelf enclosure, no drilled holes on the top face
- [ ] 3D-printed pole clamp, fits 90–140 mm pole diameter
- [ ] Plate orientation jig so installers cannot mount it wrong
- [ ] Scaled demo rig: mock pole span, low-voltage conductor, physical cut mechanism

## 8. Acceptance criteria for M2

1. Repeatable output vs. standoff curve, three runs agreeing within 5%.
2. Signal collapses below 5% of nominal within 200 ms of de-energisation.
3. Rain spray produces a deviation smaller than the 60% collapse threshold, documented.
4. Temperature drift over the full range is slower than the baseline EWMA can track — verified against `firmware/baseline.c`.

## 9. Gotchas

- Humidity leakage will surprise you. At 1 GΩ, a fingerprint across the bias resistor pad changes the reading. Clean with IPA, use a guard trace, conformal coat.
- Everything is an antenna at this impedance. Expect the breadboard to behave differently from the PCB. Do not tune thresholds on breadboard data.
- Three-phase crosstalk is not a corner case. Real LV distribution has multiple conductors on the same pole. Characterise it now, not at the finale.
- Order the PCB before the design feels finished. Revision two is cheaper than a missed deadline.
