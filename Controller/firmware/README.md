# FluidNC firmware builds and recovery

## CURRENT: clean upstream main, c82d217 (2026-10-24)

Issue [#1930](https://github.com/bdring/FluidNC/issues/1930) was closed with a
maintainer comment pointing to #1918, included in merged PR #1907. Clean
upstream `main` commit `c82d217cad69fa937d57cee24fcf7ce9080fba05` was fetched
and built with `pio run -e wifi_s3`, without our patch or OLED override.
All 347 upstream host tests and both local TMC HAL regression tests passed
against the new source.

Source worktree: ignored `FluidNC/.pio/upstream-20261024/`; the original
v4.1.1 checkout and its local modifications are preserved. Build/install
artifacts: `FluidNC/.pio/upstream-install-20261024/`, including the matching
ELF and `build-manifest.json`. Application SHA-256:
`ae9ee6152859384783a2a1b7cda0a25c176c496a7158eabbaf1aac76cb6f4e78`.
ELF SHA-256:
`fb84b7172431887143acf270130005df1dc94c3e6989701ad8d01215608d6b90`.

The user explicitly requested stopping the full-flash backup and flashing
immediately. **The partial `full-flash-before.bin` is NOT a valid backup.**
Actual config and file listing were already saved; previous complete backups
and official v4.0.3 rollback artifacts remain intact. Live partition metadata
matches the new build and its valid OTA entry selects app0. Application-only
flashing at `0x10000` completed with esptool hash verification passed. No
config, filesystem, NVS, bootloader, partition table or OTA selection was written.

**Boot verification passed:** `$I` reports `FluidNC v4.1.1 (HEAD-c82d217)` /
`esp32s3-wifi`; the real X-Carve config loads and X/Y/Y2/Z driver tests all
pass. Fault input, Cartesian kinematics, ATC, relay, probe and toolsetter
initialize. Status is Idle at MPos 0,0,0. The on-device config is unchanged
byte-for-byte. Evidence: `flash.log`, `identity-after.log`, `startup-after.log`,
`status-after.log`, `config-before.yaml` and `config-after.yaml` in the install
artifact directory. `$Heap` via HTTP returned no body, so no runtime heap
measurement is claimed. ESP-NOW is included but pendant operation was not
tested. OLED remains disabled. No motion, homing, spindle or SD-download test
was performed; the separate SD/WebDAV failure is not proven fixed.
**Rehome before future motion.**

### Subsequent file-loading crash on this build (2026-10-24)

The user reports loading approximately 1 MB G-code still crashes the controller.
Read-only Telnet confirms `v4.1.1 (HEAD-c82d217)` now in `Default (Test Drive)` /
Alarm. `$SS` reports a previous panic and retains the prior real-machine
startup with all four TMC tests passed; `$BS` has no saved backtrace. The latest
crash was not captured live and must not be decoded using yesterday's traces.
No reset, unlock, motion, config change or additional crash reproduction was
performed during reporting. Do not bypass the fallback alarm with `$X`.

Searched related upstream issues/PRs; no clear duplicate found. Published with
user authorization: https://github.com/bdring/FluidNC/issues/1931 . Report body:
[`issues/sd-webdav-loading-crash.md`](issues/sd-webdav-loading-crash.md).
Read-only diagnostics: ignored
`FluidNC/.pio/upstream-install-20261024/post-sd-crash-network.log`.
The earlier Idle result above establishes initial boot only, not current state
or runtime stability. The TMC startup fix works; SD file-loading instability
persists. No firmware rollback was requested or performed.

## Previous installation: official v4.0.3 rollback (2026-10-23)

At the user's request, installed official v4.0.3 ESP32-S3 Wi-Fi firmware,
application-only at 0x10000. The release uses ESP-IDF 4.4.7. Archive checksum,
chip/image type and partition compatibility were verified before writing;
flash verification passed. No filesystem image, bootloader, partition table
or NVS was written. Existing `config.yaml` remains unchanged, without OLED.

**Boot verification passed:** all four TMC5160 tests pass; Cartesian, fault,
ATC, relay, probe and toolsetter initialization complete. `$I` identifies
`FluidNC v4.0.3 (esp32s3-wifi)` / X-Carve and status is Idle. No configuration
errors were observed in the captured boot. No motion or SD-download test has
been performed on this version, so stability under file loading is unproven.
ESP-NOW pendant support is absent; the user accepted this rollback tradeoff.
Rehome before any future motion after the firmware restart.

Official release: https://github.com/bdring/FluidNC/releases/tag/v4.0.3

```text
5ec0233f952bef36eef5785049d0e0ad59ca18b852d16670f9c329dc3bafa081  fluidnc-v4.0.3-posix.zip
c49c3128ad12319c955b1b253713162215f9b997259fd0445a5b1566fd191ce9  wifi_s3/firmware.bin
bfe8b9f1440888eb6af0aefc0fde02c42c8f3023725961e7359a6204e931cbac  esp32s3-wifi-firmware.elf
```

Files retained in ignored `FluidNC/.pio/official-v4.0.3/`: official archive,
application/partitions/matching ELF, `boot-official-v4.0.3.log`,
`config-before-v4.0.3.yaml`, `files-before-v4.0.3.json`, and previous patched
4.1.1 no-OLED rollback application/ELF. That backup directory may contain
network/site details; do not commit it. The remaining sections are historical.

## Previous build: minimal custom firmware, no OLED

On 2026-10-23, built the standard `wifi_s3` target from v4.1.1 with only the
TMC SPI source patch below, without the OLED include override:

```sh
# Inside FluidNC/, after applying ../firmware/tmc-spi-idf5-start.patch once:
pio run -e wifi_s3
```

Build passed; both host SPI regression tests pass. OLED class/module symbols
are absent from the ELF, the TMC transfer routine is present, and the partition
table matches the official S3 build. Outputs:

- `FluidNC/.pio/build/wifi_s3/firmware.bin` (2,154,208 bytes).
- `FluidNC/.pio/build/wifi_s3/firmware.elf` (matching crash-decoding ELF).

```text
8c16105d79f34e3a746b2873413a24c6d1e4084952b2d33233eb1d4221f2031a  firmware.bin
03c1094c344b5456ca6ed8db625504a475ec34c7be25241034f5ae8dd91cf54c  firmware.elf
```

Static RAM: 119,916 bytes; application flash usage: 2,153,800 / 3,145,728
bytes. This removes OLED code, not merely its YAML section. The standard
ESP-NOW/Wi-Fi and interrupt-vtable settings remain inherited from `wifi_s3`.
The user subsequently authorized flashing. This binary was installed
application-only at 0x10000, with flash hash verification passed. Boot loads
the real X-Carve config, all four TMC driver tests pass, and `$I`, status and
`$Heap` respond. Initial state is Idle; free heap 87,172 bytes, minimum 71,696,
largest free block 45,044. Boot log:
`FluidNC/.pio/build/wifi_s3/boot-no-oled-spi-fixed.log`.

No motion or SD-download test was performed on this latest build. Removing
OLED is not a demonstrated fix for the separate HTTP/SD memory-exhaustion
crash. Config, FigUI, macros, NVS and partition table were left in place.

**Subsequent failure on the no-OLED build:** user reported another crash and
repeated alarm. Read-only network checks confirmed fallback `Default (Test
Drive)` + Alarm; `$SS` retained the previous no-OLED machine startup with all
four TMC tests passed, while `$BS` reported no saved backtrace. Evidence:
`FluidNC/.pio/build/wifi_s3/latest-crash-network.log`. Current fallback heap
was 82,816 bytes (minimum 68,348), not a measurement of memory before the
crash. No reset/unlock/config change was made during that check. The exact
latest crash cause remains unknown; it cannot be equated to the earlier
decoded SD/DMA crash without a new trace. Runtime stability is NOT established.

A subsequent **live no-OLED reproduction** captured another failure:
`Low memory: 14172 bytes`, then task watchdog timeout in `async_tcp`.
Decoded against ELF `03c1094c...`, the task was executing WebDAV.cpp:636 →
FileStream::read → FAT/SDMMC read/send-status → SD `poll_busy()` → SPI polling
transfer. The SD driver was polling for the card to become ready inside the
HTTP callback. This establishes that the download path can block the network
task until its watchdog expires; it does not establish whether the underlying
cause is card latency, SPI interference, memory pressure, or another issue.
This is distinct from the earlier NULL-pointer allocation-cleanup panic.

The controller automatically rebooted into the real machine config and Idle,
MPos 0,0,0 (not fallback). Position/homing must be treated as lost. User had
completed Z/XY homing before the crash; the agent sent no motion/reset/config
commands during reproduction. Evidence in `.pio/build/wifi_s3/`:
`reproduction-serial-20261023-181718.log`,
`reproduction-watchdog-decoded.log`, `post-watchdog-state.log`.
The raw serial capture was attached without DTR/RTS reset ioctls.

It has since been replaced by official v4.0.3 as described above.

## Previous official v4.1.1 trial (2026-10-23)

At the user's request, OLED and I2C sections were removed from main
`config.yaml`, validated, uploaded and verified byte-for-byte. The unaltered
official v4.1.1 `wifi_s3/firmware.bin` was then installed application-only at
0x10000. Partition table/active app0 selection were checked before writing;
NVS, bootloader, LittleFS, macros and FigUI were not replaced. Flash hash
verification passed.

**Official v4.1.1 reproduces the startup stall after `Z Pos Limit`.** No TMC
test results or normal command responses followed during the serial test.
No automatic rollback was performed. The user later authorized replacing it
with the patched no-OLED build described above; the official build is no
longer installed.

Downloaded from https://github.com/bdring/FluidNC/releases/tag/v4.1.1:

```text
9012318d5c9f46319a92648b68ad7c2da4d11645280e9d5c4b290740111a31b0  fluidnc-v4.1.1-posix.zip
467287c7723407f6e9288c607c4b7ebfd3797a52067a6a4e150ddc8dc7beb052  wifi_s3/firmware.bin
07cd933ebc000f6746170d14d2730dde1a7f8c7a0a0d15497df62ff6bd3dbe42  esp32s3-wifi-firmware.elf
```

Archive and ELF checksums were verified against GitHub's published digests.
Local artifacts are under ignored `FluidNC/.pio/official-v4.1.1/`, including
`boot-official-no-oled.log`, `metadata-before-official.bin`,
`config-before-official-with-oled.yaml`, and rollback files
`rollback-patched-firmware.bin` / `rollback-patched-firmware.elf`.

Issue draft: [`issues/tmc-spi-idf5-start.md`](issues/tmc-spi-idf5-start.md).
The sections below document the earlier custom build and its local fix.

Target: PiBot V5.88 Ultra (ESP32-S3, 8 MB flash), Wi-Fi firmware.

Upstream's latest stable release checked on 2026-10-21 is **v4.1.1**, commit
`fdc17a2c9c0367b07345c16da3937ff0739d4702`.

OLED support was not deleted: `FluidNC/esp32/OLED.cpp` remains in the source,
but `[common_esp32s3]` excludes it from the standard S3 firmware. Our separate
`wifi_s3_oled` environment includes it again, retaining the upstream Wi-Fi,
partition, USB-host and interrupt-vtable build settings. It does not enable
octal PSRAM or make unrelated firmware changes.

## Source and build

The local upstream checkout is at `../FluidNC/` relative to this document's
directory and is ignored by the parent repository. To recreate it, run from
the parent repository root:

```sh
git clone --branch v4.1.1 --depth 1 https://github.com/bdring/FluidNC.git FluidNC
```

Add the following environment to the checkout's existing
`FluidNC/platformio_override.ini`; preserve all its other sections:

```ini
[env:wifi_s3_oled]
extends = env:wifi_s3
build_src_filter =
    ${env:wifi_s3.build_src_filter}
    +<../esp32/OLED.cpp>
```

Then run inside the checkout:

```sh
git apply ../firmware/tmc-spi-idf5-start.patch
pio run -e wifi_s3_oled
```

The patch fixes the v4.1.1 TMC SPI transfer path on ESP-IDF 5: the original
code clears the completion flag but only starts transfers on IDF < 5, then
waits forever. The S3 IDF 5 path must call `spi_ll_apply_config()` followed by
`spi_ll_user_start()`. Without this fix the full machine config stops after
printing the Z limit, before any TMC driver communication-test result.
The regression harness runs the actual C routine against a host HAL shim:
`python3 -m unittest discover -s tests -v` from the parent repository root.
It failed on IDF 5 before the patch; IDF 4 and 5 both pass afterward.
Do not apply the patch twice; `git apply --reverse --check` can check whether
it is already present. The upstream checkout is ignored, so the patch is
retained here to make the fix reproducible.

The final include overrides the inherited OLED exclusion. Do not use the
upstream `[env:oled]` target: it extends the classic ESP32 environment, not S3.

## Build outputs

Build completed successfully on 2026-10-21. Confirmed `OLED::init()` and
`OLED::group()` are linked into `firmware.elf`. PlatformIO reports application
flash usage of 2,188,172 / 3,145,728 bytes (69.6%) and static RAM usage of
120,028 / 327,680 bytes (36.6%). These are build-time figures, not runtime heap
headroom or hardware validation.

SHA-256 checksums for this build:

```text
50cef13934f6e8fc76adab72616a3a6f2a1f750e9239d7b8ba856e30d0141a24  firmware.bin
7c4649b1de80ccb37763a5e486ed0a54e7606e619097cc5a7ec497a21ed81f63  firmware.elf
```

The original build above was flashed on 2026-10-23 and exhibited the TMC SPI
startup stall. The no-output recovery config boots, serves the preserved WebUI
at `http://10.30.0.11/`, and responds to `$I` and status over Telnet.

Rebuilt and flashed application-only on 2026-10-23 with the IDF 5 SPI-start fix:

```text
1009e4f2bb78dc2fc948403615a90b6130ab30a8f9c454dc91098144caa4b93c  firmware.bin
b75bee70d7798376f85f4853394f1667f011a7e2ce48756a99d32eb022525e81  firmware.elf
```

Hardware retest passed: the original full config now reports driver-test
success for X, Y, Y2 and Z, then completes startup including fault input,
ATC, relay, probe and toolsetter. `$I` and status queries respond normally.
The same succeeds with OLED settings added. No motion, homing, spindle or
pendant integration tests were performed.

After a successful build, outputs are under
`FluidNC/.pio/build/wifi_s3_oled/` from the parent repository root:

- `firmware.bin` — application firmware.
- `firmware.elf` — retain this exact file for crash-backtrace decoding.
- `bootloader.bin` and `partitions.bin` — build outputs, not a request to replace
  the controller's existing bootloader or partition table.
- `firmware.factory.bin` — automatically generated combined image; do not use
  this for an application-only update.

The source release is pinned, but some upstream library dependencies follow
Git branches or version ranges. Preserve the PlatformIO dependency versions
and build outputs if you need to reproduce an exact binary later.

## Installation and display configuration

**Building does not flash or reboot the controller.** Before any installation,
back up the controller's actual config, files, settings and working firmware.
Do not erase flash, upload a filesystem image, or use a merged image as a
routine firmware update: those operations can overwrite config and FigUI.
Confirm partition compatibility before updating application firmware.

Main `config.yaml` temporarily enabled `i2c0:` and `oled:` during custom-build
testing. These sections have since been removed for the official-build trial.
`config_door.yaml` remains unchanged and does not enable the display.
PiBot's OLED header uses GPIO.13 for SCL and GPIO.14 for SDA, plus **3.3 V** and
GND. Verify the module's connector order, display controller, dimensions and
I2C address before connecting it; power off before changing wiring.

PiBot's [V5.88 pinout reference, item 22](https://wiki.pibot.com/doku.php?id=pibot_cnc_laser_series:v588_ultra:pinout_reference:start#pb22)
and its test YAML specify GPIO13 SCL, GPIO14 SDA, 128x64, address 0x3C
(decimal `60.000` in our YAML). OLED and RJ12 use independent pins on V5.88.
`examples/bisect/config_recovery_oled.yaml` is a display-only test using those
settings, with no physical machine outputs.

On-device test with the main config recognizes the correct bus and settings:

```text
I2C SDA: gpio.14, SCL: gpio.13, Freq: 100000, Bus #: 0
OLED I2C address: 0x3c width: 128 height: 64
Error writing to I2C device -4
OLED is not responding
```

The controller still completes boot. Display operation is unresolved; `-4`
maps to Wire's general "other error", not specifically a missing-address
NACK. Check display supply, connection and module address, and if necessary
instrument the Arduino I2C driver (`i2c_master_init` currently ignores the
return value from `TwoWire::begin`). Do not guess different GPIOs or change
wiring while powered. The PSRAM warning also remains but did not prevent
either the recovery or full machine config from booting.

Later on 2026-10-23 the user reported Config Alarm and the previous-panic
startup log. Network `$I` confirmed the fallback `Default (Test Drive)` config;
`$BS` reported no saved backtrace. After USB reattachment and serial-open reset,
the full config booted again, OLED initialized without an I2C error, and the
paired PiBot pendant connected via ESP-NOW (200 ms reporting). Status and `$I`
confirmed X-Carve + Idle during roughly one minute of observation. This is
recovery from fallback, NOT a diagnosis/fix of the unexplained panic. Capture
live serial panic output and `$BS` before another reset if it recurs. Visible
OLED operation still needs confirmation. Logs retained under
`FluidNC/.pio/recovery-20261023/`: `panic-oled-backtrace.log`,
`boot-oled-panic-serial.log`, and `post-reset-health.log`.

Recovery backups (ignored local files; do not commit, may contain credentials):

- Full 8 MB controller flash: `FluidNC/.pio/controller-before-oled-c04e303917e8-20261023-115200.bin`.
  SHA-256: `07e90242339eef2a1329fc75d23428c35f3a22063c45733c06f6dce821864629`.
- Fresh pre-recovery LittleFS: `FluidNC/.pio/recovery-20261023/littlefs-current-before-recovery.bin`.
- Original config also retained on-device as `config.pre-recovery-20261023.yaml`.
- No-output recovery retained on-device as `config.recovery-no-outputs.yaml`;
  active filename is `config.yaml`, currently without OLED/I2C.
- Original OLED application/ELF retained in `FluidNC/.pio/recovery-20261023/before-spi-fix-firmware.bin`
  and `before-spi-fix-firmware.elf`.

Recovery replaced only four changed 4 KB LittleFS sectors; every other file's
content (WebUI and macros) was checked unchanged. NVS and application partitions
were not touched by the config recovery operation.

A successful compile is not a hardware test. Verify USB boot logs, display
updates, limits and safe motion before returning the machine to service.
