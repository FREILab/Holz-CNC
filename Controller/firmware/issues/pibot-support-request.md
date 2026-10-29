Subject: V5.88 Ultra — FluidNC 4.1.1 startup/SD crashes; request tested ESP-NOW-compatible firmware

Hello PiBot Support,

I need help finding a stable, supported FluidNC firmware for my PiBot V5.88
Ultra. The controller operates an Inventables X-Carve (XYYZ) with four PiBot
SilentStep TMC5160 V5 external drivers in independent SPI mode. I also have a
PiBot Pendant V4.2 and need ESP-NOW connectivity.

We have reproduced two problems with FluidNC v4.1.1:

**1. Official ESP32-S3 Wi-Fi firmware hangs during startup.**

With the unmodified official v4.1.1 release, startup stops after the Z-limit
description, before any TMC driver-test results. OLED/I2C sections were removed,
so this is reproducible without OLED support. Source investigation found that
the ESP-IDF 5 TMC SPI path waits for completion without starting the transfer.
A small local patch allows startup to complete and all four driver tests pass.
We reported this upstream, including the config, boot log and proposed fix:

https://github.com/bdring/FluidNC/issues/1930

**2. SD file loading is very slow and can reboot the controller.**

After applying that startup fix, loading/previewing G-code from SD through the
WebUI still causes failures. This was also reproduced with a standard no-OLED
build containing only the TMC SPI fix. Serial captures show:

- Low-memory warnings, down to approximately 1.5 KB free in one capture.
- An SPI DMA allocation failure followed by a null-pointer panic.
- In another capture, an `async_tcp` watchdog timeout while HTTP/WebDAV was
  reading from SD and polling for the card to become ready.

These failures occur during file loading/download, not necessarily while
executing a machining job. Following a panic, FluidNC can enter its fallback
configuration and Config Alarm, which also disables homing.

**Working comparison:** we have now installed official FluidNC v4.0.3 on the
same controller with the same machine config, SD card and wiring. All four
driver tests pass, it boots normally, and SD file loading now works correctly.
However, v4.0.3 predates upstream ESP-NOW pendant support, so this is only a
temporary workaround for our requirements.

Your V5.88 downloads page currently lists v4.0.3, while the Pendant V4.2 manual
describes ESP-NOW operation. Could you please:

1. Provide the latest PiBot-tested V5.88 Ultra ESP32-S3 firmware that supports
   both independent-SPI TMC5160 drivers and ESP-NOW pendant pairing.
2. Confirm whether these startup and SD-download failures are known, and
   provide a corrected firmware or an actionable fix/workaround.
3. Specify the matching pendant firmware, controller configuration requirements
   and recommended SD-card format/specifications for that tested combination.

I do not need OLED support. My priority is a reliable CNC with working SD file
loading and ESP-NOW pendant connectivity, without maintaining custom firmware
patches.

I can provide sanitized serial crash logs, decoded backtraces, firmware
checksums and the machine configuration. Please do not recommend a factory
reset unless it is necessary; the current configuration and files are backed up.

Thank you,
Matteo
