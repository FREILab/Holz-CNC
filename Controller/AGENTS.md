# AGENTS.md

## Purpose

Author and maintain a FluidNC `config.yaml` for an **Inventables X-Carve (XYYZ)** running on a **PiBot V5.88 Ultra** board with **4× PiBot SilentStep TMC5160 V5** SPI stepper drivers. Optional hardware: PiBot CNC Pendant V4.2.

This directory (`Controller/`) is part of the FREILab `Holz-CNC` repo, which is the single source of truth for the machine. Schaltkasten wiring and the PiBot↔Schaltkasten interface are documented in `../HW/Verdrahtung.md`; keep it in sync when pins change. The router is an **AMB FME-1050W** (230 V, on/off only via the Schaltkasten relay chain; speed set by hand on the router). The production config is `config.yaml` in this directory. `examples/` holds bring-up drafts: `config_pibot_v588_x_spi_minus1_test.yaml` (single-driver `spi_index: -1` smoke test), `config_pibot_v588_xyyz_independent_test.yaml` (4-driver independent-SPI test), `config_pibot_v588_xyyz_daisychain_test.yaml` (abandoned daisy-chain draft, kept for reference). The older `config_pibot_v588_x_spi_test.yaml` still has a stale V4 `r_sense_ohms: 0.075`.

Probe + toolsetter are wired (`probe: pin: gpio.41:low`, `toolsetter_pin: gpio.37`, `control: fault_pin: gpio.36:pu`). Manual ATC configured (`atc_manual`). Main `config.yaml` has no safety-door input or parking, and router delays are back to `0.000`. The door/parking variant is preserved as root `config_door.yaml`: `control: safety_door_pin: gpio.48` (no `:low`; contact closed to GND with door closed, opens with door open; verify actual sensor polarity). That variant parks Z at machine Z=150 mm (5 mm pullout at 250 mm/min, retract at 800 mm/min; requires Z homed), with router delays of `5000.000` ms. See README for commissioning.

## Firmware status: clean upstream main c82d217 (2026-10-24)

**LATEST RUNTIME STATE (2026-10-24, supersedes the initial Idle boot record below): user reports loading ~1 MB G-code still crashes clean c82d217. Read-only Telnet confirms `Default (Test Drive)` / Alarm; `$SS` says previous panic and shows all four TMC tests passed in the prior real-machine startup; `$BS` has no saved backtrace. No reset/unlock/motion/config writes performed. Separate runtime issue published with user authorization: https://github.com/bdring/FluidNC/issues/1931 . Body retained at `firmware/issues/sd-webdav-loading-crash.md`; raw read-only evidence at `FluidNC/.pio/upstream-install-20261024/post-sd-crash-network.log`. Latest crash has NO live decoded trace; historical 03c1094c/b75bee70 traces are not current fb84b717 ELF. Do not bypass fallback Alarm with `$X`.**

**CURRENT DEVICE STATE (2026-10-24): clean upstream `main` commit `c82d217cad69fa937d57cee24fcf7ce9080fba05`, standard `wifi_s3`, installed application-only at 0x10000 with user authorization; flash hash verified. Reports `v4.1.1 (HEAD-c82d217)`. PR #1918 is included through merged #1907, as the maintainer comment on #1930 states. No local patch/OLED override applied. X/Y/Y2/Z TMC tests pass, full machine config and fault/ATC/relay/probe/toolsetter initialize; status Idle. Config unchanged byte-for-byte; filesystem/NVS/bootloader/partition table/OTA metadata not written. ESP-NOW included, pendant not tested; OLED disabled. NO motion/homing/spindle/SD-download test; separate SD/WebDAV failures not proven fixed. Rehome before motion. Matching ELF: `FluidNC/.pio/upstream-install-20261024/firmware.elf`, SHA256 `fb84b7172431887143acf270130005df1dc94c3e6989701ad8d01215608d6b90`. Application SHA256 `ae9ee6152859384783a2a1b7cda0a25c176c496a7158eabbaf1aac76cb6f4e78`. Install directory holds flash/startup/status/config evidence. User explicitly cancelled full-flash backup: partial `full-flash-before.bin` is NOT valid. Earlier complete backups and official v4.0.3 rollback retained. Clean source worktree: `FluidNC/.pio/upstream-20261024/`; original patched v4.1.1 checkout preserved. 347 upstream host tests and both TMC HAL tests pass on new source.**

### Historical state below (superseded by the 2026-10-24 installation)

- **User-confirmed result:** SD file loading works correctly again on official v4.0.3. No claim of completed cutting/spindle validation. Upstream TMC startup issue published with user authorization: https://github.com/bdring/FluidNC/issues/1930 (full no-OLED config and official v4.1.1 startup log included; SD failures kept separate). PiBot support message drafted, NOT sent, at `firmware/issues/pibot-support-request.md`.
**CURRENT DEVICE STATE (2026-10-23): official unmodified FluidNC v4.0.3 `wifi_s3` application (ESP-IDF 4.4.7) installed at 0x10000 with user authorization; flash hash verified. Existing no-OLED `config.yaml`, LittleFS/FigUI/macros, NVS and partition table retained. Boot completes, all four TMC5160 tests pass, fault/probe/toolsetter/ATC initialize, real X-Carve config reports Idle. NO motion or SD-download test performed on 4.0.3; do not claim proven machining stability. ESP-NOW is unavailable on this upstream release; user explicitly accepted that. Current matching ELF is `.pio/official-v4.0.3/official-esp32s3-wifi-firmware.elf`, SHA256 `bfe8b9f1440888eb6af0aefc0fde02c42c8f3023725961e7359a6204e931cbac`. Boot log `.pio/official-v4.0.3/boot-official-v4.0.3.log`. Previous no-OLED 4.1.1 application/ELF/config saved there for rollback. Rehome before future motion after the firmware restart.**

- **Previous no-OLED 4.1.1 build (NOT ACTIVE):** standard `pio run -e wifi_s3` with only retained TMC SPI fix. Binary SHA256 `8c16105d79f34e3a746b2873413a24c6d1e4084952b2d33233eb1d4221f2031a`, ELF SHA256 `03c1094c344b5456ca6ed8db625504a475ec34c7be25241034f5ae8dd91cf54c`. It booted/passed driver tests but also crashed during SD HTTP downloads. Live no-OLED trace: `Low memory: 14172`, async_tcp watchdog in WebDAV.cpp:636 → FileStream::read → FatFS/SDMMC send-status → SD poll_busy → SPI polling. Raw `.pio/build/wifi_s3/reproduction-serial-20261023-181718.log`; decoded `reproduction-watchdog-decoded.log`. This trace uses the old 03c1094c ELF, not current 4.0.3. Passive serial capture was terminated to free USB for rollback.
- **OLED history:** `oled:` is unavailable in stock ESP32-S3 builds (bdring/FluidNC#1804). Our earlier custom `wifi_s3_oled` build restored it. PiBot settings are GPIO13 SCL / GPIO14 SDA, 128x64, address 0x3C (decimal 60); the user confirmed the display worked. I2C error -4 occurred intermittently. OLED/I2C were subsequently removed from main `config.yaml` for the official-build trial; the custom build is NOT active. `config_door.yaml` also omits OLED. See `firmware/README.md`.
- **TMC startup fix:** `Axes::init()` prints all axis descriptors before `config_motors()` programs the TMCs starting at X. In `esp32/tmc_spi_support.c`, IDF 5 cleared the SPI completion flag but never started the transaction, then polled forever. `firmware/tmc-spi-idf5-start.patch` adds S3 HAL `spi_ll_apply_config()` and `spi_ll_user_start()`; apply it in the ignored checkout before rebuilding. Host regression: `python3 -m unittest discover -s tests -v` (real C code with HAL shim). Official v4.1.1 reproduces the stall; both local patched variants (with and without OLED) boot full config and pass all four TMC tests. User completed Z/XY homing on the earlier OLED build, not yet on this latest no-OLED build. No spindle testing performed.
- **Recovery:** full flash and fresh LittleFS backups under ignored `FluidNC/.pio/` (paths/checksums in `firmware/README.md`; can contain credentials). Original config remains on-device as `config.pre-recovery-20261023.yaml`; no-output recovery as `config.recovery-no-outputs.yaml`. Active filename restored to `config.yaml`. FigUI/macros preserved. `examples/bisect/config_recovery_no_outputs.yaml` boots without physical machine outputs; `config_recovery_oled.yaml` adds only the documented display bus. Keep motor/router power off during recovery.
- **Later runtime panic captured on the custom build:** homing completed, then G-code loading from SD via HTTP/WebDAV coincided with free heap warnings (13308 then 1484 bytes), SPI DMA RX allocation failure and LoadProhibited at NULL. Exact ELF `b75bee70...` decodes the stack through WebDAV.cpp:636 → FileStream::read → FatFS/SDMMC → SPI DMA cleanup. Logs: ignored `.pio/recovery-20261023/runtime-panic-live-capture.log` and `runtime-panic-decoded.log`. Memory exhaustion is established; its underlying cause is NOT fixed. User stopped further SD diagnostics; `config_recovery_sd.yaml` was created/validated locally but NOT uploaded or activated. Do not bypass fallback Config Alarm with `$X`.

## Repository layout

- `examples/` — our own drafts for this machine, plus `pibot_vendor_tmc5160_example.yaml` (PiBot-supplied TMC5160 example for an older V4.9 board; reference only).
- `tools/` — vendored FluidNC validator + JSON schema (from bdring/FluidNC `tools/`).
- External, NOT part of this repo (separate local clones, handled outside Holz-CNC): `FluidNC/`, `fluidnc-config-files/`, FluidDial, FigUI/fluidnc-web. Paths below that mention them refer to those local checkouts; place/symlink `FluidNC/` inside `Controller/` if `tests/` should find it.
- `FluidNC/` — (external) ignored local upstream firmware checkout, pinned to v4.1.1 (`fdc17a2c9c0367b07345c16da3937ff0739d4702`). Custom `wifi_s3_oled` target in its `platformio_override.ini` restores OLED via a final `+<../esp32/OLED.cpp>` filter. Build with `pio run -e wifi_s3_oled` inside the checkout; see `firmware/README.md` for recreation and installation precautions. Do not flash without explicit authorization.
- `fluidnc-config-files/` — (external) **read-only** reference clone of `bdring/fluidnc-config-files`. Do not edit; refresh with `git -C fluidnc-config-files pull`.
  - Closest references: `official/6_pack_TMC5160_XYYZ.yaml` (TMC5160 + dual-Y motor0/motor1 pattern; uses independent SPI with per-axis `cs_pin` i2so.3/.6/.11/.14 — same topology as our final wiring), `official/BlackBox_X32_XYYZ-DOOR.yaml` (door sensor), `contributed/6x_CNC_Controller/6x_X_Carve.yaml` (X-Carve travels/steps).
  - Contributed files are unmaintained and contain real bugs (e.g. `6x_X_Carve.yaml` has a duplicated `standard_stepper:` key) — copy patterns, not files.
  - `official/*.yaml` use placeholder kinematics (e.g. 800 steps/mm); X-Carve values differ per microstepping (see `6x_X_Carve.yaml`: 40 steps/mm X/Y at 8×).

## Validating a config (do this after every change)

### Parser formatting rules (hardware recovery, 2026-10-21)

- **No inline comments in configuration YAML.** Put comments on their own lines above the setting, never after a value. The door/parking upload caused boot errors; the user recovered by fixing lines 228, 238 and 239 (parking target and spindle delays).
- **Use explicit decimal notation for numeric setting values**, e.g. `5000.000`, not `5000`, and `150.000`, not `150`. Do not introduce bare whole-number values in future config edits. Pin identifiers are not numeric setting values.
- A successful JSON-schema validation does **not** establish compatibility with FluidNC's on-device parser or prove the board can boot. Check these formatting rules manually as well, and retain a known-working config before uploading changes.

FluidNC's real parser matches keys case-insensitively but unknown keys/values are the main failure mode. **Never guess YAML keys** — check the official schema first:

```sh
# one-time: local venv (system python3 has no pyyaml/jsonschema)
python3 -m venv .venv && .venv/bin/pip install pyyaml jsonschema

# fetch current validator + JSON schema from bdring/FluidNC (main branch)
mkdir -p tools
base=https://raw.githubusercontent.com/bdring/FluidNC/main/tools
curl -fsSL "$base/validate_fluidnc_config.py" -o tools/validate_fluidnc_config.py
curl -fsSL "$base/fluidnc_validate_core.py"   -o tools/fluidnc_validate_core.py
curl -fsSL "$base/fluidnc-config-schema.json" -o tools/fluidnc-config-schema.json

# validate
.venv/bin/python tools/validate_fluidnc_config.py --no-auto-install \
  --schema tools/fluidnc-config-schema.json --permissive <file>.yaml
```

When unsure whether a key/enum value exists, grep `tools/fluidnc-config-schema.json`. The CI workflow in `fluidnc-config-files/.github/workflows/validate-new-configs.yml` shows this exact setup and why (validator always tracks current firmware format).

## Hardware facts that shape the config

- XYYZ: the Y axis has two motors — use `motor0` + `motor1` under `axes.y` with separate limit pins; X and Z have `motor0` only.
- TMC5160s run in **SPI independent mode** — every driver gets `spi_index: -1` and its OWN `cs_pin` (NOT daisy chain). Shared MOSI/SCK/MISO; one CS line per driver.
- PiBot V5.88 connector signal map (EN/DIR/STP/CS, all on the I2SO expander):

  | axis | disable (EN) | direction | step | CS |
  |------|--------------|-----------|------|-----|
  | X  | I2SO.0  | I2SO.1  | I2SO.2  | I2SO.3  |
  | Y1 | I2SO.7  | I2SO.4  | I2SO.5  | I2SO.6  |
  | Y2 | I2SO.8  | I2SO.9  | I2SO.10 | I2SO.11 |
  | Z  | I2SO.15 | I2SO.12 | I2SO.13 | I2SO.14 |

- CS access: `I2SO.3` is on the SPI signal header (`MOSI/SCK/MISO/I2SO.3`); `I2SO.6/.11/.14` are the StepStick sockets' MS3 pins (tap them directly — the A4988 Socket-to-SPI breakout is optional convenience; sockets must be empty). The 3-jumper SPI block (item ⑯) is NOT used for external SPI drivers.
- `spi:` = miso `gpio.2` / mosi `gpio.1` / sck `gpio.21`; `i2so:` = bck/data/ws `16/17/18`; sdcard cs `gpio.9`.
- `r_sense_ohms: 0.1` — SilentStep TMC5160 V5 uses 0.1 Ω sense resistors (confirmed; `0.075` in old drafts is the V4 value).
- `stepping.engine: I2S_STATIC` is required when step pins are on the I2SO expander.

## Docs

- Config file format: http://wiki.fluidnc.com/en/config/overview (full wiki: http://wiki.fluidnc.com/en/home)
- PiBot V5.88 Ultra: https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:v588_ultra:introduction:start
- TMC5160 SilentStep V5: https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:silentstep_tmc5160_v5:start
- Pendant V4.2: https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:cnc_pendant_v42:start
