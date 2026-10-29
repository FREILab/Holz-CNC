"""Exercise FluidNC's real TMC SPI transfer code against a host HAL shim."""

from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "FluidNC/FluidNC/esp32/tmc_spi_support.c"

HAL = r"""
#include <assert.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>
typedef struct { int unused; } spi_dev_t;
typedef unsigned spi_ll_clock_val_t;
typedef struct { int a, b, c; } spi_line_mode_t;
spi_dev_t GPSPI2;
static int started, applied, transfers;
#define APB_CLK_FREQ 80000000
static void spi_ll_master_cal_clock(int a,int b,int c,spi_ll_clock_val_t *d) { *d=1; }
static void spi_ll_master_set_clock_by_reg(spi_dev_t *h,spi_ll_clock_val_t *v) {}
static void spi_ll_master_init(spi_dev_t *h) {}
static void spi_ll_master_set_mode(spi_dev_t *h,int m) {}
static void spi_ll_set_half_duplex(spi_dev_t *h,bool v) {}
static void spi_ll_master_set_line_mode(spi_dev_t *h,spi_line_mode_t m) {}
static void spi_ll_set_mosi_bitlen(spi_dev_t *h,int n) {}
static void spi_ll_set_miso_bitlen(spi_dev_t *h,int n) {}
static void spi_ll_set_addr_bitlen(spi_dev_t *h,int n) {}
static void spi_ll_set_command_bitlen(spi_dev_t *h,int n) {}
static void spi_ll_write_buffer(spi_dev_t *h,const uint8_t *b,int n) {}
static void spi_ll_enable_mosi(spi_dev_t *h,int v) {}
static void spi_ll_enable_miso(spi_dev_t *h,int v) {}
static void spi_ll_clear_int_stat(spi_dev_t *h) { started=0; applied=0; }
static void spi_ll_apply_config(spi_dev_t *h) { applied=1; }
static void spi_ll_user_start(spi_dev_t *h) { assert(applied); started=1; }
static void spi_ll_master_user_start(spi_dev_t *h) { started=1; }
static bool spi_ll_usr_is_done(spi_dev_t *h) {
    assert(started && "SPI completion polled without starting a transfer");
    ++transfers;
    return true;
}
static void spi_ll_read_buffer(spi_dev_t *h,uint8_t *b,int n) {
    if (n) memset(b,0,n/8);
}
"""


@unittest.skipUnless(SOURCE.exists(), "Requires the local FluidNC checkout")
class TmcSpiStartTests(unittest.TestCase):
    def exercise(self, version):
        with tempfile.TemporaryDirectory(prefix="tmc-spi-") as directory:
            root = Path(directory)
            (root / "hal").mkdir()
            (root / "soc").mkdir()
            (root / "hal/spi_ll.h").write_text(HAL)
            (root / "soc/rtc.h").write_text("")
            (root / "sdkconfig.h").write_text("#define CONFIG_IDF_TARGET_ESP32S3 1\n")
            (root / "esp_idf_version.h").write_text(
                f"#define ESP_IDF_VERSION_MAJOR {version}\n"
            )
            harness = root / "test.c"
            harness.write_text(
                f'#include "{SOURCE}"\n'
                "int main(void) {\n"
                "  uint8_t data[5] = {0};\n"
                "  tmc_spi_bus_setup();\n"
                "  tmc_spi_rw_reg(0x80, 0, -1);\n"
                "  tmc_spi_transfer_data(data, 40, data, 40);\n"
                "  assert(transfers == 2);\n"
                "  return 0;\n}\n"
            )
            binary = root / "test"
            subprocess.run(
                ["cc", "-I", str(root), str(harness), "-o", str(binary)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                [str(binary)], capture_output=True, text=True, timeout=3
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_idf4_starts_transfer_before_waiting(self):
        self.exercise(4)

    def test_idf5_applies_config_and_starts_transfer_before_waiting(self):
        self.exercise(5)


if __name__ == "__main__":
    unittest.main()
