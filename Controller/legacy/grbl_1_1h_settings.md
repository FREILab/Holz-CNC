# Legacy Stock X-Carve Controller with GRBL 1.1h Settings

Below is a GRBL 1.1h settings list. Parameter IDs, names, units, and typical boolean/mask usage follow the official GRBL 1.1h specification.

```text
$0=10        (Step pulse time, microseconds)
$1=25        (Step idle delay, milliseconds)
$2=0         (Step pulse invert, mask)
$3=0         (Step direction invert, mask)
$4=0         (Invert step enable pin, boolean)
$5=0         (Invert limit pins, boolean)
$6=0         (Invert probe pin, boolean)
$10=1        (Status report options, mask)
$11=0.010    (Junction deviation, millimeters)
$12=0.002    (Arc tolerance, millimeters)
$13=0        (Report in inches, boolean)
$20=0        (Soft limits enable, boolean)
$21=0        (Hard limits enable, boolean)
$22=1        (Homing cycle enable, boolean)
$23=3        (Homing direction invert, mask)
$24=25.000   (Homing locate feed rate, mm/min)
$25=500.000  (Homing search seek rate, mm/min)
$26=250      (Homing switch debounce delay, milliseconds)
$27=1.000    (Homing switch pull-off distance, millimeters)
$30=1000     (Maximum spindle speed, RPM)
$31=0        (Minimum spindle speed, RPM)
$32=0        (Laser-mode enable, boolean)
$100=250.000 (X-axis travel resolution, step/mm)
$101=250.000 (Y-axis travel resolution, step/mm)
$102=500.000 (Z-axis travel resolution, step/mm)
$110=5000.000 (X-axis maximum rate, mm/min)
$111=5000.000 (Y-axis maximum rate, mm/min)
$112=500.000 (Z-axis maximum rate, mm/min)
$120=500.000 (X-axis acceleration, mm/sec^2)
$121=500.000 (Y-axis acceleration, mm/sec^2)
$122=100.000 (Z-axis acceleration, mm/sec^2)
$130=200.000 (X-axis maximum travel, millimeters)
$131=200.000 (Y-axis maximum travel, millimeters)
$132=100.000 (Z-axis maximum travel, millimeters)
```

## Notes

- Masks (e.g., `$2`, `$3`, `$23`) are bitfields; values depend on your axis configuration.
- Booleans are `0` (false) or `1` (true).
- Rates are in mm/min; accelerations in mm/sec^2; distances in mm.