# BMW Diagnostic Agent

Deterministic BMW diagnostic communication scaffold for attaching an LLM/MCP
reasoning layer later without changing vehicle access code.

## V0.1 goal

V0.1 terminates at structured diagnostic data:

```text
BMW → interface → vehicle.py → structured diagnostic data
```

The implemented deterministic sequence is:

```text
identify_vehicle()
    ↓
VIN
    ↓
scan_ecus()
    ↓
ECU inventory
    ↓
read_fault_memory()
    ↓
structured fault database
```



## Mandatory Factory Baseline vault

Factory-baseline preservation is a mandatory architectural component, not an
optional feature. Before any tuning operation or write-capable ECU action, the
system must create an immutable `FACTORY-0001` record for the connected vehicle:

```text
VEHICLE CONNECTED → IDENTIFY VEHICLE → VIN + ECU inventory → FACTORY BASELINE
        ↓
ECU data + calibration references + coding configuration
        ↓
VAULT STORAGE → SHA-256 HASH + VERSION
```

The baseline record intentionally separates diagnostic baseline data from actual
ECU calibration/programming data. Reading ECU identifiers, software versions, or
fault memory is not treated as proof that the system has a complete factory
recovery image. If original calibration data is unavailable, the restore plan
must escalate to the appropriate factory software recovery workflow instead of
fabricating missing data.

Every tune becomes a version rooted at the immutable factory record:

```text
FACTORY-0001
├── TUNE-0002
│   └── TUNE-0003
└── RESTORE → FACTORY-0001
```

The tuning agent can read baseline metadata and request new tune versions, but
it is not allowed to overwrite or delete the factory baseline. Retrieved
baselines are re-hashed and rejected if their SHA-256 integrity hash no longer
matches the stored hash.

### Restore hierarchy

* **Level 1 — Configuration restore:** restore module coding/configuration.
* **Level 2 — Calibration restore:** restore original calibration only when a
  valid original calibration backup is available.
* **Level 3 — Factory software recovery:** use BMW programming/recovery tooling
  when a local calibration backup is missing or cannot be trusted.

### Write safety gate

Before every ECU write, the safety gate requires all of the following evidence:

```text
[✓] Correct VIN
[✓] Correct ECU
[✓] Factory baseline exists
[✓] Baseline integrity verified
[✓] Current ECU state captured
[✓] Proposed change validated
[✓] Power/communication conditions valid
[✓] Restore path available
[✓] User authorization
```


## Hardware and protocol abstraction

The platform is protocol-independent: diagnostic intent is expressed as
`read_ecu_identifier()`, `read_dtc()`, `read_measurement()`, `uds_request()`, or
`execute_service()`. The hardware layer chooses whether the request travels over
ICOM, ENET, J2534, D-CAN, K-Line, CAN/ISO-TP, DoIP, or another supported path.

```text
BMW AI Vehicle Platform
        ↓
Hardware Abstraction
        ↓
OEM interfaces | Pass-Thru / VCI | Direct bus | Measurement hardware
        ↓
Protocol Engine: UDS | KWP2000 | DoIP | ISO-TP | ISO9141/14230/15765
        ↓
BMW vehicle
```

The hardware package models BMW-relevant physical interfaces and buses:

```text
hardware/
├── icom/              # ICOM Next/A/A2/B/C capability discovery
├── enet/              # ENET Ethernet/DoIP facade
├── j2534/             # vendor-independent Pass-Thru API shape
├── dcan/              # D-CAN adapter facade
├── kline/             # K-Line/KWP2000 legacy facade
├── kdcan/             # K+DCAN dual-capable adapter class
├── can/               # native CAN subsystem
├── isotp/             # independent ISO-TP layer
├── doip/              # DoIP discovery/routing/message layer placeholder
├── ethernet/          # automotive Ethernet, 100BASE-TX/T1/1000BASE-T1
├── flexray/ lin/ most/ ibus/ kbus/ bsd/ byteflight/
├── usb/ serial/ wifi/ bluetooth/
└── oscilloscope/ logic_analyzer/ sensors/ dyno/
```

BMW CAN networks such as PT-CAN, PT-CAN2, F-CAN, K-CAN, K-CAN2, Local-CAN, and
D-CAN are modeled as topology/network variants rather than separate physical
adapter classes. LIN, BSD, byteflight, K-Bus, I-Bus, MOST, and FlexRay remain in
the map so legacy, infotainment, body, and subsystem measurements can be
correlated with ECU diagnostic state.

Wireless links are treated as read-only/diagnostic preference by policy.
Programming-capable paths must be explicitly wired and authorized; a wireless or
read-only interface is never promoted into a programming path automatically.

## BMW software ecosystem

The project is organized as a broader BMW AI Vehicle Engineering Platform rather
than an ISTA-only GUI operator. BMW tooling is represented in separate lanes:

```text
DIAGNOSTICS:  ISTA, ISTA/P
ENGINEERING:  E-Sys, Tool32, INPA, NCS Expert, WinKFP, EDIABAS, PSdZData
KNOWLEDGE:    AIR, TIS, repair information, wiring, parts data
LEGACY:       GT1, DIS, Progman, SSS, SP-Daten
PROTOCOLS:    UDS/KWP over ICOM or J2534-style interfaces
```

The AI layer sits above these software/protocol lanes and must preserve the
factory-baseline vault as the root of diagnose → calculate → simulate → tune →
validate → restore workflows.

## Performance Engineering layer

The Performance Engineering layer sits above deterministic diagnostics and below
LLM tuning recommendations. It models proposed changes before anything is
written to an ECU:

```text
Diagnostic Engine              Performance Engine
ECU / fault data               Vehicle specifications
Live measurements              Engine, fuel, boost, ignition
ISTA test plans                Thermal, torque, gear, aero, tire limits
        \                       /
         \                     /
          Calculation Engine
                 ↓
Power/Torque, Acceleration, Thermal models
                 ↓
Tuning Simulator
                 ↓
Safety Constraints
                 ↓
Recommended setup
```

The calculation engine is deliberately pure: it can calculate, simulate,
compare, and validate candidate calibrations, but it cannot flash or write an
ECU. ECU write operations remain isolated by safety policy.

### Vehicle digital twin

A candidate tune is evaluated against a parameterized `VehicleDigitalTwin`:

```text
Vehicle
├── Engine: displacement, compression ratio, cylinders, redline, turbocharger
├── Fuel system: injector capacity, fuel pressure, fuel type
├── Drivetrain: transmission, gear ratios, final drive, efficiency
└── Chassis: mass, tire, drag coefficient, frontal area
```

The simulator runs a baseline/candidate loop:

```text
BASELINE → calculate → modify parameter → simulate → calculate → compare
```

It currently estimates engine, vehicle, and thermal metrics such as torque,
power, BMEP, air/fuel mass, lambda, injector duty cycle, boost, wheel torque,
acceleration, drivetrain losses, charge-air temperature, oil-temperature
tendency, and heat rejection.

## Repository structure

```text
bmw-diagnostic-agent/
├── agent/          # Future probabilistic reasoning layer
├── mcp/            # Future MCP server/tools
├── vehicle/        # Deterministic vehicle communication boundary
├── performance/    # Digital twin, calculations, tuning simulation
├── baseline/       # Immutable factory baseline vault and tune versions
├── bmw/            # BMW software ecosystem taxonomy and generations
├── hardware/       # Physical transports, interfaces, buses, measurement hardware
├── protocol/       # UDS/KWP/DoIP/ISO protocol engine boundaries
├── ista/           # Future ISTA bridge
├── knowledge/      # Future diagnostic knowledge sources
├── safety/         # Read-only permissions and safety policies
├── logs/           # Diagnostic-session logs
├── config/         # Vehicle/interface configuration
├── tests/          # Automated tests
└── main.py         # V0.1 snapshot entry point
```

## Run V0.1 simulator

```bash
python main.py
```

## Test

```bash
python -m pytest
```
