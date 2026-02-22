import subprocess
import sys
from pathlib import Path

# Test dir is next to this script (tools_test/), so the test works from any CWD
TEST_DIR = Path(__file__).resolve().parent


def test_openscad_render():
    """
    Verifies OpenSCAD installation and headless rendering via Xvfb.
    """
    test_file = TEST_DIR / "tmp_part.scad"
    output_img = TEST_DIR / "test_render.png"

    scad_code = """
    $fn = 50;
    difference() {
        cube([20, 20, 10], center=true);
        sphere(d=25);
    }
    """

    print("🚀 Starting OpenSCAD Integration Test...")

    try:
        TEST_DIR.mkdir(parents=True, exist_ok=True)
        test_file.write_text(scad_code)

        # xvfb-run provides a virtual display; no --enable=manifold (not in OpenSCAD 2021.01)
        cmd = [
            "xvfb-run", "-a",
            "openscad",
            "-o", str(output_img),
            "--imgsize=800,600",
            str(test_file),
        ]

        print("📦 Running render command...")
        subprocess.run(cmd, capture_output=True, text=True, check=True)

        if output_img.exists() and output_img.stat().st_size > 0:
            print("✅ Success: OpenSCAD rendered a valid PNG headlessly.")
            print(f"📊 Image saved to: {output_img}")
        else:
            print("❌ Failure: Output file was not created or is empty.")
            sys.exit(1)

    except subprocess.CalledProcessError as e:
        print(f"❌ OpenSCAD Error:\n{e.stderr or e.stdout}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: 'openscad' or 'xvfb-run' not found in PATH.")
        sys.exit(1)
    finally:
        if test_file.exists():
            test_file.unlink()
        if output_img.exists():
            output_img.unlink()
        print("🧹 Cleanup complete.")

if __name__ == "__main__":
    test_openscad_render()