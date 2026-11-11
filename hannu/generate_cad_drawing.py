"""
Generate professional 2D/3D CAD drawing of Hannu Sauna using CADCraft CLI with structured JSON commands.
"""
import subprocess
import os
import json

def build_cadcraft_commands():
    cmds = []
    
    # Layers
    layers = [
        {"name": "A-WALL", "color": "White"},
        {"name": "A-DOOR", "color": "Green"},
        {"name": "A-GLAZ", "color": "Cyan"},
        {"name": "A-FURN", "color": "Yellow"},
        {"name": "A-ROOF", "color": "Red"},
        {"name": "A-DIMS", "color": "Yellow"},
        {"name": "A-TEXT", "color": "White"},
    ]
    for l in layers:
        cmds.append(("layer.new", {"name": l["name"], "color": l["color"]}))

    def set_layer(name):
        cmds.append(("layer.current", {"name": name}))

    # ==========================================
    # 1. PLANRITNING (Y = 0 to 2500)
    # ==========================================
    set_layer("A-WALL")
    # Outer sauna walls
    cmds.append(("rectang", {"p1": [0, 0], "p2": [3000, 2500]}))
    cmds.append(("rectang", {"p1": [44, 44], "p2": [2956, 2456]}))
    # Terrace back wall
    cmds.append(("rectang", {"p1": [3000, 2456], "p2": [4200, 2500]}))
    # Terrace front corner post
    cmds.append(("rectang", {"p1": [4100, 0], "p2": [4200, 100]}))

    # Corner knot horns (knutskallar)
    knots = [
        [-80, -44, 0, 44],
        [-44, -80, 44, 0],
        [-80, 2456, 0, 2544],
        [-44, 2500, 44, 2580],
        [2956, 2500, 3044, 2580],
        [4200, 2456, 4280, 2544],
        [4156, 2500, 4244, 2580],
    ]
    for k in knots:
        cmds.append(("rectang", {"p1": [k[0], k[1]], "p2": [k[2], k[3]]}))

    # Terrace floor deck lines
    set_layer("A-FURN")
    for ty in range(200, 2400, 160):
        cmds.append(("line", {"points": [[3050, ty], [4150, ty]]}))

    # Front panoramic windows (3 pcs 875 mm)
    set_layer("A-GLAZ")
    cmds.append(("rectang", {"p1": [150, -20], "p2": [1025, 44]}))
    cmds.append(("rectang", {"p1": [1065, -20], "p2": [1940, 44]}))
    cmds.append(("rectang", {"p1": [1980, -20], "p2": [2855, 44]}))

    # Sauna door on veranda wall (X=3000, Y=150 to 1040)
    set_layer("A-DOOR")
    cmds.append(("line", {"points": [[3000, 150], [3000, 1040]]}))
    cmds.append(("line", {"points": [[3000, 150], [3750, 550]]}))
    cmds.append(("arc", {"start": [3000, 1040], "center": [3000, 150], "end": [3750, 550]}))

    # Sauna benches (Lavar)
    set_layer("A-FURN")
    cmds.append(("rectang", {"p1": [44, 1900], "p2": [2956, 2456]})) # Upper lave
    cmds.append(("rectang", {"p1": [44, 1300], "p2": [2956, 1900]})) # Lower lave
    cmds.append(("rectang", {"p1": [44, 900], "p2": [1200, 1300]}))  # Foot step
    cmds.append(("rectang", {"p1": [3050, 1950], "p2": [4150, 2456]})) # Terrace bench
    
    # Harvia tower heater (front left corner)
    cmds.append(("circle", {"center": [450, 450], "radius": 180}))
    cmds.append(("circle", {"center": [450, 450], "radius": 150}))
    cmds.append(("line", {"points": [[40, 200], [40, 700]]})) # Heat shield
    cmds.append(("line", {"points": [[40, 700], [200, 700]]}))

    # Roof overhang
    set_layer("A-ROOF")
    cmds.append(("rectang", {"p1": [-150, -450], "p2": [4450, 2750]}))

    # Text & Annotations
    set_layer("A-TEXT")
    cmds.append(("text", {"at": [950, 1600], "text": "BASTURUM 7.2 m2 (6-8 pers)", "height": 90}))
    cmds.append(("text", {"at": [950, 1450], "text": "Ovre lave (djup 550 mm) + Undre lave", "height": 70}))
    cmds.append(("text", {"at": [3200, 1300], "text": "VERANDA / RELAX", "height": 80}))
    cmds.append(("text", {"at": [3200, 1150], "text": "Vaderskyddad sittplats", "height": 65}))
    cmds.append(("text", {"at": [600, -150], "text": "PANORAMAFONSTER MOT FORSEN (3x 875 mm)", "height": 75}))
    cmds.append(("text", {"at": [0, 2850], "text": "HANNU 44 - PLANLOSNING (SKALA 1:50)", "height": 120}))

    # Dimensions
    set_layer("A-DIMS")
    cmds.append(("line", {"points": [[0, -320], [3000, -320]]}))
    cmds.append(("text", {"at": [1250, -300], "text": "3000 mm (Bastu)", "height": 75}))
    cmds.append(("line", {"points": [[3000, -320], [4200, -320]]}))
    cmds.append(("text", {"at": [3350, -300], "text": "1200 mm (Veranda)", "height": 75}))
    cmds.append(("line", {"points": [[-320, 0], [-320, 2500]]}))
    cmds.append(("text", {"at": [-350, 1050], "text": "2500 mm", "height": 75, "rotation": 90}))

    # ==========================================
    # 2. FASADRITNING - MOT FORSEN (Y = 4000 to 7000)
    # ==========================================
    set_layer("A-WALL")
    # Ground line
    cmds.append(("line", {"points": [[-600, 4000], [4800, 4000]]}))
    # Foundation plinths
    cmds.append(("rectang", {"p1": [50, 4000], "p2": [250, 4150]}))
    cmds.append(("rectang", {"p1": [1400, 4000], "p2": [1600, 4150]}))
    cmds.append(("rectang", {"p1": [2850, 4000], "p2": [3050, 4150]}))
    cmds.append(("rectang", {"p1": [4050, 4000], "p2": [4250, 4150]}))
    
    # Sauna front timber wall (X=0 to 3000, Y=4150 to 6650)
    cmds.append(("rectang", {"p1": [0, 4150], "p2": [3000, 6650]}))
    # Wall log horizontal grooves (knuttimmer profil 135mm)
    for ly in range(4150 + 135, 6650, 135):
        cmds.append(("line", {"points": [[0, ly], [3000, ly]]}))

    # Terrace corner post (X=4150 to 4250, Y=4150 to 6650)
    cmds.append(("rectang", {"p1": [4150, 4150], "p2": [4250, 6650]}))
    # Terrace roof beam
    cmds.append(("rectang", {"p1": [3000, 6500], "p2": [4250, 6650]}))
    # Terrace deck floor edge
    set_layer("A-FURN")
    cmds.append(("rectang", {"p1": [3000, 4150], "p2": [4250, 4250]}))
    # Bench seen under porch
    cmds.append(("rectang", {"p1": [3300, 4250], "p2": [4150, 4700]}))

    # Panorama windows (3 pcs)
    set_layer("A-GLAZ")
    cmds.append(("rectang", {"p1": [150, 4550], "p2": [1025, 6250]}))
    cmds.append(("rectang", {"p1": [1065, 4550], "p2": [1940, 6250]}))
    cmds.append(("rectang", {"p1": [1980, 4550], "p2": [2855, 6250]}))
    # Glass panes inner line
    cmds.append(("rectang", {"p1": [190, 4590], "p2": [985, 6210]}))
    cmds.append(("rectang", {"p1": [1105, 4590], "p2": [1900, 6210]}))
    cmds.append(("rectang", {"p1": [2020, 4590], "p2": [2815, 6210]}))

    # Sloping roof fascia board
    set_layer("A-ROOF")
    cmds.append(("rectang", {"p1": [-150, 6650], "p2": [4450, 6850]}))

    set_layer("A-TEXT")
    cmds.append(("text", {"at": [0, 7100], "text": "FASAD MOT FORSEN / SÖDER (SKALA 1:50)", "height": 120}))
    cmds.append(("text", {"at": [600, 6350], "text": "3x Stora panoreringsglas (utsikt över strömmen)", "height": 75}))
    cmds.append(("text", {"at": [3200, 5200], "text": "Relax/Entré", "height": 80}))

    # Height dimensions
    set_layer("A-DIMS")
    cmds.append(("line", {"points": [[4500, 4000], [4500, 6850]]}))
    cmds.append(("text", {"at": [4550, 5300], "text": "Hojd: 2850 mm", "height": 80, "rotation": 90}))

    return cmds

def run():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    dxf_path = os.path.join(out_dir, "hannu_planritning.dxf")
    png_path = os.path.join(out_dir, "hannu_planritning.png")

    cadcraft_exe = r"C:\Program Files\ArtCraft\CADCraft\cadcraft-cli.exe"
    cmds = build_cadcraft_commands()
    
    cli_args = [cadcraft_exe, "run", "--metric"]
    for cid, params in cmds:
        cli_args.extend(["--cmd", f"{cid} {json.dumps(params)}"])
        
    cli_args.extend(["--save", dxf_path, "--export", png_path])

    print(f"Executing CADCraft with {len(cmds)} commands...")
    res = subprocess.run(cli_args, capture_output=True, text=True)
    if res.stderr:
        print("CADCraft stderr:", res.stderr)
    print("DXF exists:", os.path.exists(dxf_path), f"({os.path.getsize(dxf_path)} bytes)" if os.path.exists(dxf_path) else "")
    print("PNG exists:", os.path.exists(png_path), f"({os.path.getsize(png_path)} bytes)" if os.path.exists(png_path) else "")

if __name__ == "__main__":
    run()
