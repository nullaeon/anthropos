import subprocess
import os
import sys
from pathlib import Path

def test_openscad_render():
    """
    Verifies OpenSCAD installation, Manifold engine availability, 
    and headless rendering via Xvfb.
    """
    test_file = Path("test_tools/tmp_part.scad")
    output_img = Path("test_tools/test_render.png")
    
    # 1. Create a simple parametric SCAD file
    scad_code = """
    $fn = 50;
    difference() {
        cube([20, 20, 10], center=true);
        sphere(d=25);
    }
    """
    
    print("🚀 Starting OpenSCAD Integration Test...")
    
    try:
        test_file.write_text(scad_code)
        
        # 2. Construct the command
        # xvfb-run handles the virtual display buffer
        # --enable=manifold uses the high-speed engine
        cmd = [
            "xvfb-run", "-a", 
            "openscad", 
            "--enable=manifold",
            "-o", str(output_img),
            "--imgsize=800,600",
            str(test_file)
        ]
        
        print(f"📦 Running render command...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # 3. Validation
        if output_img.exists() and output_img.stat().st_size > 0:
            print("✅ Success: OpenSCAD rendered a valid PNG headlessly.")
            print(f"📊 Image saved to: {output_img}")
        else:
            print("❌ Failure: Output file was not created or is empty.")
            sys.exit(1)
            
    except subprocess.CalledProcessError as e:
        print(f"❌ OpenSCAD Error:\n{e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ Error: 'openscad' or 'xvfb-run' not found in PATH.")
        sys.exit(1)
    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
        print("🧹 Cleanup complete.")

if __name__ == "__main__":
    test_openscad_render()