"""
Generate 3D models (OBJ/MTL, GLTF) and CADCraft drawings for Hannu sauna
Based on Polhus Hannu architectural drawings.
"""
import math
import json
import os
import subprocess

def create_cuboid(min_x, min_y, min_z, max_x, max_y, max_z):
    """Return vertices (8) and 12 triangles (quads split into 2 tris) for a box."""
    v = [
        [min_x, min_y, min_z], # 0
        [max_x, min_y, min_z], # 1
        [max_x, max_y, min_z], # 2
        [min_x, max_y, min_z], # 3
        [min_x, min_y, max_z], # 4
        [max_x, min_y, max_z], # 5
        [max_x, max_y, max_z], # 6
        [min_x, max_y, max_z], # 7
    ]
    # Faces: normal pointing outwards
    # Front (Z-min): 0, 3, 2 / 0, 2, 1
    # Back (Z-max): 5, 6, 7 / 5, 7, 4
    # Left (X-min): 4, 7, 3 / 4, 3, 0
    # Right (X-max): 1, 2, 6 / 1, 6, 5
    # Bottom (Y-min): 4, 0, 1 / 4, 1, 5
    # Top (Y-max): 3, 7, 6 / 3, 6, 2
    f = [
        [0, 3, 2], [0, 2, 1], # Front
        [5, 6, 7], [5, 7, 4], # Back
        [4, 7, 3], [4, 3, 0], # Left
        [1, 2, 6], [1, 6, 5], # Right
        [4, 0, 1], [4, 1, 5], # Bottom
        [3, 7, 6], [3, 6, 2], # Top
    ]
    return v, f

def create_cylinder(center_x, center_z, base_y, top_y, radius, segments=16):
    """Return vertices and faces for a cylinder."""
    v = []
    # Bottom ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = center_x + radius * math.cos(angle)
        z = center_z + radius * math.sin(angle)
        v.append([x, base_y, z])
    # Top ring
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x = center_x + radius * math.cos(angle)
        z = center_z + radius * math.sin(angle)
        v.append([x, top_y, z])
    
    # Bottom center & top center
    bc_idx = len(v)
    v.append([center_x, base_y, center_z])
    tc_idx = len(v)
    v.append([center_x, top_y, center_z])

    f = []
    # Side walls
    for i in range(segments):
        nxt = (i + 1) % segments
        b1, b2 = i, nxt
        t1, t2 = i + segments, nxt + segments
        f.append([b1, t1, t2])
        f.append([b1, t2, b2])
    # Caps
    for i in range(segments):
        nxt = (i + 1) % segments
        f.append([bc_idx, (i + 1) % segments, i])
        f.append([tc_idx, i + segments, nxt + segments])
        
    return v, f

class ModelBuilder:
    def __init__(self):
        self.materials = {} # name -> props
        self.objects = {}   # obj_name -> list of (vertices, faces, mat_name)
        
    def add_mesh(self, obj_name, verts, faces, mat_name):
        if obj_name not in self.objects:
            self.objects[obj_name] = []
        self.objects[obj_name].append((verts, faces, mat_name))

    def add_box(self, obj_name, min_x, min_y, min_z, max_x, max_y, max_z, mat_name):
        v, f = create_cuboid(min_x, min_y, min_z, max_x, max_y, max_z)
        self.add_mesh(obj_name, v, f, mat_name)

    def add_cylinder(self, obj_name, cx, cz, by, ty, r, mat_name, segs=16):
        v, f = create_cylinder(cx, cz, by, ty, r, segs)
        self.add_mesh(obj_name, v, f, mat_name)

    def export_obj(self, obj_path, mtl_path):
        mtl_filename = os.path.basename(mtl_path)
        with open(mtl_path, "w", encoding="utf-8") as fm:
            fm.write("# Materials for Hannu Sauna\n\n")
            for name, m in self.materials.items():
                fm.write(f"newmtl {name}\n")
                kd = m.get("kd", [0.8, 0.8, 0.8])
                ks = m.get("ks", [0.2, 0.2, 0.2])
                d = m.get("d", 1.0)
                ns = m.get("ns", 10.0)
                fm.write(f"Kd {kd[0]:.3f} {kd[1]:.3f} {kd[2]:.3f}\n")
                fm.write(f"Ks {ks[0]:.3f} {ks[1]:.3f} {ks[2]:.3f}\n")
                fm.write(f"d {d:.2f}\n")
                fm.write(f"Ns {ns:.1f}\n")
                fm.write(f"illum 2\n\n")

        with open(obj_path, "w", encoding="utf-8") as fo:
            fo.write(f"# Wavefront OBJ: Hannu Bastu (Polhus 44mm)\n")
            fo.write(f"mtllib {mtl_filename}\n\n")
            vert_offset = 1

            for obj_name, meshes in self.objects.items():
                fo.write(f"o {obj_name}\n")
                # Group by material
                current_mat = None
                for verts, faces, mat in meshes:
                    if mat != current_mat:
                        fo.write(f"usemtl {mat}\n")
                        current_mat = mat
                    for v in verts:
                        fo.write(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n")
                    for tri in faces:
                        i1 = tri[0] + vert_offset
                        i2 = tri[1] + vert_offset
                        i3 = tri[2] + vert_offset
                        fo.write(f"f {i1} {i2} {i3}\n")
                    vert_offset += len(verts)
                fo.write("\n")

def build_hannu_sauna():
    mb = ModelBuilder()
    
    # Define Materials
    # Charcoal exterior timber
    mb.materials["TimberExterior"] = {"kd": [0.18, 0.18, 0.19], "ks": [0.08, 0.08, 0.08], "d": 1.0, "ns": 15.0}
    # Warm spruce/aspen interior & benches
    mb.materials["WoodInterior"] = {"kd": [0.91, 0.76, 0.54], "ks": [0.15, 0.12, 0.09], "d": 1.0, "ns": 20.0}
    # Terrace wood decking (impregnated / weathered pine)
    mb.materials["WoodDecking"] = {"kd": [0.58, 0.53, 0.44], "ks": [0.10, 0.10, 0.10], "d": 1.0, "ns": 10.0}
    # Black roof felt / trim
    mb.materials["RoofFelt"] = {"kd": [0.12, 0.12, 0.13], "ks": [0.05, 0.05, 0.05], "d": 1.0, "ns": 5.0}
    # Window/door frames (black anthracite)
    mb.materials["WindowFrame"] = {"kd": [0.10, 0.10, 0.10], "ks": [0.25, 0.25, 0.25], "d": 1.0, "ns": 40.0}
    # Glass (slightly tinted transparent)
    mb.materials["Glass"] = {"kd": [0.75, 0.85, 0.90], "ks": [0.90, 0.95, 1.00], "d": 0.35, "ns": 90.0}
    # Heater metal mesh
    mb.materials["HeaterMetal"] = {"kd": [0.25, 0.25, 0.27], "ks": [0.50, 0.50, 0.55], "d": 1.0, "ns": 60.0}
    # Sauna stones (dark olivine diabase)
    mb.materials["SaunaStones"] = {"kd": [0.28, 0.26, 0.24], "ks": [0.05, 0.05, 0.05], "d": 1.0, "ns": 5.0}
    # Concrete plinths
    mb.materials["Concrete"] = {"kd": [0.65, 0.65, 0.65], "ks": [0.05, 0.05, 0.05], "d": 1.0, "ns": 5.0}

    # Sauna dimensions (in meters)
    # Total width: 4.40m (Sauna: 3.20m exterior, Porch: 1.20m)
    # Total depth: 2.70m exterior
    # Front height: 2.50m wall, ~2.70m with roof
    # Rear height: 2.16m wall, ~2.35m with roof
    
    Y_BASE = 0.20 # Plinths raise building 20 cm
    
    # 1. Foundation Plinths (Plintplan: 3 rows of 7 plinths)
    # X from 0.05 to 4.25, Z from 0.10 to 2.55
    x_plinths = [0.05, 0.70, 1.35, 2.00, 2.65, 3.45, 4.25]
    z_plinths = [0.10, 1.35, 2.55]
    for x in x_plinths:
        for z in z_plinths:
            mb.add_box("Foundation", x - 0.10, 0.0, z - 0.10, x + 0.10, Y_BASE, z + 0.10, "Concrete")

    # Foundation joists (Bärlinor/Golvbjälkar 45x90)
    for z in z_plinths:
        mb.add_box("Joists", 0.0, Y_BASE, z - 0.045, 4.30, Y_BASE + 0.09, z + 0.045, "WoodDecking")

    # 2. Floor & Decking
    # Sauna floor (internal: 0.05 to 2.95, Z: 0.05 to 2.45)
    mb.add_box("SaunaFloor", 0.05, Y_BASE + 0.09, 0.05, 2.95, Y_BASE + 0.12, 2.45, "WoodInterior")
    # Terrace decking (X: 3.00 to 4.25, Z: 0.05 to 2.45) with plank gaps
    mb.add_box("TerraceDeck", 3.00, Y_BASE + 0.09, 0.05, 4.25, Y_BASE + 0.12, 2.45, "WoodDecking")

    Y_FLOOR = Y_BASE + 0.12
    WALL_T = 0.044 # 44 mm timber
    
    # Sloping wall top function:
    # At front (Z = 0): Y_top = Y_FLOOR + 2.38 = 2.70m
    # At rear (Z = 2.50): Y_top = Y_FLOOR + 2.04 = 2.36m
    def wall_height_at(z):
        slope = (2.04 - 2.38) / 2.50
        return Y_FLOOR + 2.38 + slope * z

    # 3. Walls
    # Back Wall (spanning sauna + terrace: X=0 to 4.30, Z=2.50)
    mb.add_box("Walls_Back", -0.05, Y_FLOOR, 2.50 - WALL_T, 4.35, wall_height_at(2.50), 2.50, "TimberExterior")

    # Left Wall (Sein A, X=0, Z=0 to 2.50)
    # Sloping top: we model as 4 stepping segments or angled block
    steps = 10
    dz = 2.50 / steps
    for s in range(steps):
        z0 = s * dz
        z1 = (s + 1) * dz
        h = wall_height_at((z0 + z1)/2.0)
        mb.add_box("Walls_Left", -WALL_T, Y_FLOOR, z0, 0.0, h, z1, "TimberExterior")
        # Corner knot overhangs
        if s == 0:
            mb.add_box("Knots", -WALL_T - 0.08, Y_FLOOR, -0.08, 0.0, h, 0.08, "TimberExterior")
        if s == steps - 1:
            mb.add_box("Knots", -WALL_T - 0.08, Y_FLOOR, 2.42, 0.0, h, 2.58, "TimberExterior")

    # Divider Wall (Sein B, X=3.00, between sauna and terrace)
    # Has sauna door at Z = 0.15 to 1.05 (width 0.90m, height 1.95m)
    # Part above door:
    mb.add_box("Walls_Divider", 3.00, Y_FLOOR + 1.95, 0.0, 3.00 + WALL_T, wall_height_at(0.5), 1.10, "TimberExterior")
    # Part to right of door (rear part Z=1.10 to 2.50):
    for s in range(5):
        z0 = 1.10 + s * (1.40 / 5)
        z1 = 1.10 + (s + 1) * (1.40 / 5)
        h = wall_height_at((z0 + z1)/2.0)
        mb.add_box("Walls_Divider", 3.00, Y_FLOOR, z0, 3.00 + WALL_T, h, z1, "TimberExterior")

    # Front Wall (Sein 1, Z=0, X=0 to 3.00)
    # Contains 3 large windows!
    # Bottom wall log under windows (height 0.40m):
    mb.add_box("Walls_Front", -0.05, Y_FLOOR, 0.0, 3.05, Y_FLOOR + 0.40, WALL_T, "TimberExterior")
    # Top wall log above windows (from Y=2.15 to wall top ~2.70):
    mb.add_box("Walls_Front", -0.05, Y_FLOOR + 2.15, 0.0, 3.05, wall_height_at(0.0), WALL_T, "TimberExterior")
    # Side posts around windows:
    mb.add_box("Walls_Front", -0.05, Y_FLOOR + 0.40, 0.0, 0.12, Y_FLOOR + 2.15, WALL_T, "TimberExterior")
    mb.add_box("Walls_Front", 2.88, Y_FLOOR + 0.40, 0.0, 3.05, Y_FLOOR + 2.15, WALL_T, "TimberExterior")

    # 4. Front Panoramic Windows (3 pcs 875 x 1700)
    # Total window width ~2.76m. Each glass pane ~0.86m wide with mullions
    win_w = 0.88
    for i in range(3):
        wx0 = 0.15 + i * (win_w + 0.04)
        wx1 = wx0 + win_w
        # Window frame (anthracite)
        FT = 0.04
        mb.add_box("WinFrames", wx0, Y_FLOOR + 0.40, 0.005, wx1, Y_FLOOR + 0.40 + FT, 0.04, "WindowFrame") # bottom
        mb.add_box("WinFrames", wx0, Y_FLOOR + 2.15 - FT, 0.005, wx1, Y_FLOOR + 2.15, 0.04, "WindowFrame") # top
        mb.add_box("WinFrames", wx0, Y_FLOOR + 0.40, 0.005, wx0 + FT, Y_FLOOR + 2.15, 0.04, "WindowFrame") # left
        mb.add_box("WinFrames", wx1 - FT, Y_FLOOR + 0.40, 0.005, wx1, Y_FLOOR + 2.15, 0.04, "WindowFrame") # right
        # Glass
        mb.add_box("GlassPanes", wx0 + FT, Y_FLOOR + 0.40 + FT, 0.02, wx1 - FT, Y_FLOOR + 2.15 - FT, 0.025, "Glass")

    # 5. Terrace Door (in wall B at X=3.00, Z=0.18 to 1.07)
    # Door frame
    mb.add_box("DoorFrame", 3.00 - 0.01, Y_FLOOR, 0.16, 3.00 + WALL_T + 0.01, Y_FLOOR + 1.95, 0.20, "WindowFrame")
    mb.add_box("DoorFrame", 3.00 - 0.01, Y_FLOOR, 1.05, 3.00 + WALL_T + 0.01, Y_FLOOR + 1.95, 1.09, "WindowFrame")
    mb.add_box("DoorFrame", 3.00 - 0.01, Y_FLOOR + 1.91, 0.16, 3.00 + WALL_T + 0.01, Y_FLOOR + 1.95, 1.09, "WindowFrame")
    # Door Leaf (dark timber vertical planks)
    mb.add_box("DoorLeaf", 3.005, Y_FLOOR + 0.02, 0.20, 3.035, Y_FLOOR + 1.91, 1.05, "TimberExterior")
    # Round porthole window (skeppsventil) on door (center Z=0.62, Y=Y_FLOOR + 1.35)
    mb.add_cylinder("DoorPortholeRing", 3.02, 0.62, Y_FLOOR + 1.35 - 0.18, Y_FLOOR + 1.35 + 0.18, 0.18, "WindowFrame", 16)
    mb.add_cylinder("DoorPortholeGlass", 3.02, 0.62, Y_FLOOR + 1.35 - 0.14, Y_FLOOR + 1.35 + 0.14, 0.14, "Glass", 16)
    # Door handle
    mb.add_box("DoorHandle", 2.97, Y_FLOOR + 0.95, 0.26, 3.05, Y_FLOOR + 0.99, 0.29, "WindowFrame")

    # 6. Terrace Relax Post & Bench
    # Outer front corner timber post (X=4.25, Z=0.0)
    mb.add_box("TerracePost", 4.20, Y_FLOOR, -WALL_T, 4.30, wall_height_at(0.0), 0.06, "TimberExterior")
    # Terrace beam spanning from X=3.00 to 4.30 at front top
    mb.add_box("TerraceBeam", 3.00, wall_height_at(0.0) - 0.15, -WALL_T, 4.30, wall_height_at(0.0), 0.06, "TimberExterior")
    # Terrace Relax Bench (at rear of porch Z=1.90 to 2.45, X=3.08 to 4.25)
    mb.add_box("TerraceBench", 3.08, Y_FLOOR + 0.45, 1.90, 4.25, Y_FLOOR + 0.49, 2.45, "WoodInterior")
    # Bench legs & brace
    mb.add_box("TerraceBenchLeg", 4.15, Y_FLOOR, 1.95, 4.25, Y_FLOOR + 0.45, 2.40, "TimberExterior")

    # 7. Interior Sauna Benches (Lavar)
    # Upper lave (back wall Z=1.85 to 2.45, X=0.08 to 2.92, height Y=1.05)
    mb.add_box("LaveUpper", 0.08, Y_FLOOR + 0.90, 1.85, 2.92, Y_FLOOR + 0.96, 2.45, "WoodInterior")
    # Lower lave (back wall Z=1.25 to 1.85, X=0.08 to 2.92, height Y=0.50)
    mb.add_box("LaveLower", 0.08, Y_FLOOR + 0.45, 1.25, 2.92, Y_FLOOR + 0.51, 1.85, "WoodInterior")
    # Bench skirt / slats (between upper and lower)
    mb.add_box("LaveSkirt", 0.08, Y_FLOOR + 0.51, 1.85, 2.92, Y_FLOOR + 0.90, 1.88, "WoodInterior")
    # Foot step (X=0.08 to 1.20, Z=0.85 to 1.25, Y=0.25)
    mb.add_box("LaveStep", 0.08, Y_FLOOR + 0.22, 0.85, 1.20, Y_FLOOR + 0.27, 1.25, "WoodInterior")
    # Backrest along rear wall
    mb.add_box("Backrest", 0.08, Y_FLOOR + 1.20, 2.44, 2.92, Y_FLOOR + 1.45, 2.46, "WoodInterior")

    # 8. Sauna Heater (Harvia Cilindro style pillar heater at front left)
    # Centered at X=0.45, Z=0.45
    mb.add_cylinder("HeaterMesh", 0.45, 0.45, Y_FLOOR + 0.02, Y_FLOOR + 1.05, 0.18, "HeaterMetal", 18)
    mb.add_cylinder("HeaterStones", 0.45, 0.45, Y_FLOOR + 0.05, Y_FLOOR + 1.03, 0.165, "SaunaStones", 14)
    # Heat shield behind heater against wall
    mb.add_box("HeatShield", 0.01, Y_FLOOR + 0.05, 0.15, 0.02, Y_FLOOR + 1.30, 0.75, "HeaterMetal")

    # 9. Roof (Pulpettak / Mono-pitch roof)
    # Front overhang: Z = -0.45
    # Rear overhang: Z = 2.75
    # Width: X = -0.15 to 4.45 (total width 4.60m)
    # Sloping roof plane
    ROOF_THICK = 0.08
    r_steps = 15
    r_z0 = -0.45
    r_z1 = 2.75
    r_dz = (r_z1 - r_z0) / r_steps
    
    # Roof beams (Takåsar 70x140) running crosswise
    mb.add_box("RoofBeams", -0.10, wall_height_at(0.0) + 0.02, -0.05, 4.40, wall_height_at(0.0) + 0.16, 0.05, "WoodInterior")
    mb.add_box("RoofBeams", -0.10, wall_height_at(1.25) + 0.02, 1.20, 4.40, wall_height_at(1.25) + 0.16, 1.30, "WoodInterior")
    mb.add_box("RoofBeams", -0.10, wall_height_at(2.50) + 0.02, 2.45, 4.40, wall_height_at(2.50) + 0.16, 2.55, "WoodInterior")

    for s in range(r_steps):
        z_a = r_z0 + s * r_dz
        z_b = r_z0 + (s + 1) * r_dz
        # Base height interpolated
        h_mid = wall_height_at((z_a + z_b)/2.0) + 0.16
        # Top roof covering (Takpapp / EPDM)
        mb.add_box("RoofCovering", -0.15, h_mid, z_a, 4.45, h_mid + ROOF_THICK, z_b, "RoofFelt")

    # Fascia boards (Vindskivor & takfotsbrädor)
    # Front fascia
    mb.add_box("RoofFascia", -0.16, wall_height_at(-0.45) + 0.10, -0.48, 4.46, wall_height_at(-0.45) + 0.26, -0.44, "RoofFelt")
    # Rear fascia
    mb.add_box("RoofFascia", -0.16, wall_height_at(2.75) + 0.10, 2.74, 4.46, wall_height_at(2.75) + 0.26, 2.78, "RoofFelt")
    # Side bargeboards (left and right)
    for s in range(r_steps):
        z_a = r_z0 + s * r_dz
        z_b = r_z0 + (s + 1) * r_dz
        h_mid = wall_height_at((z_a + z_b)/2.0) + 0.16
        mb.add_box("RoofBargeboard", -0.18, h_mid - 0.05, z_a, -0.14, h_mid + ROOF_THICK + 0.04, z_b, "RoofFelt")
        mb.add_box("RoofBargeboard", 4.44, h_mid - 0.05, z_a, 4.48, h_mid + ROOF_THICK + 0.04, z_b, "RoofFelt")

    return mb

def export_gltf(mb, gltf_path):
    """Export the ModelBuilder to a standard single-file GLTF (with base64 buffers)."""
    import base64
    import struct
    
    # Collect all vertices and indices
    all_positions = []
    all_normals = []
    all_indices = []
    
    # We will create primitives per material
    material_primitives = {} # mat_name -> {'positions': [], 'indices': []}
    
    for obj_name, meshes in mb.objects.items():
        for verts, faces, mat in meshes:
            if mat not in material_primitives:
                material_primitives[mat] = {'positions': [], 'indices': []}
            base_idx = len(material_primitives[mat]['positions'])
            for v in verts:
                material_primitives[mat]['positions'].append(v)
            for f in faces:
                material_primitives[mat]['indices'].extend([f[0] + base_idx, f[1] + base_idx, f[2] + base_idx])

    # Build binary buffer
    bin_buffer = bytearray()
    buffer_views = []
    accessors = []
    materials_list = []
    mat_map = {}
    
    # Materials definitions for glTF PBR
    mat_pbr_colors = {
        "TimberExterior": [0.18, 0.18, 0.19, 1.0],
        "WoodInterior": [0.91, 0.76, 0.54, 1.0],
        "WoodDecking": [0.58, 0.53, 0.44, 1.0],
        "RoofFelt": [0.12, 0.12, 0.13, 1.0],
        "WindowFrame": [0.10, 0.10, 0.10, 1.0],
        "Glass": [0.75, 0.85, 0.90, 0.4],
        "HeaterMetal": [0.35, 0.35, 0.37, 1.0],
        "SaunaStones": [0.28, 0.26, 0.24, 1.0],
        "Concrete": [0.65, 0.65, 0.65, 1.0],
    }

    primitives = []
    for mat_name, data in material_primitives.items():
        if not data['positions']:
            continue
            
        mat_idx = len(materials_list)
        pbr_col = mat_pbr_colors.get(mat_name, [0.8, 0.8, 0.8, 1.0])
        mat_entry = {
            "name": mat_name,
            "pbrMetallicRoughness": {
                "baseColorFactor": pbr_col,
                "metallicFactor": 0.1 if mat_name not in ["WindowFrame", "HeaterMetal"] else 0.8,
                "roughnessFactor": 0.8 if mat_name != "Glass" else 0.1
            }
        }
        if mat_name == "Glass":
            mat_entry["alphaMode"] = "BLEND"
            mat_entry["doubleSided"] = True
        materials_list.append(mat_entry)
        
        # Position buffer
        pos_offset = len(bin_buffer)
        pos_min = [float('inf')]*3
        pos_max = [float('-inf')]*3
        for p in data['positions']:
            for k in range(3):
                pos_min[k] = min(pos_min[k], p[k])
                pos_max[k] = max(pos_max[k], p[k])
            bin_buffer.extend(struct.pack('<fff', p[0], p[1], p[2]))
        pos_len = len(bin_buffer) - pos_offset
        
        # Align 4 bytes
        while len(bin_buffer) % 4 != 0:
            bin_buffer.append(0)
            
        # Index buffer (unsigned int or unsigned short)
        idx_offset = len(bin_buffer)
        use_uint32 = len(data['positions']) > 65535
        for idx in data['indices']:
            if use_uint32:
                bin_buffer.extend(struct.pack('<I', idx))
            else:
                bin_buffer.extend(struct.pack('<H', idx))
        idx_len = len(bin_buffer) - idx_offset
        while len(bin_buffer) % 4 != 0:
            bin_buffer.append(0)
            
        # Buffer views
        pv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": pos_offset,
            "byteLength": pos_len,
            "target": 34962 # ARRAY_BUFFER
        })
        iv_idx = len(buffer_views)
        buffer_views.append({
            "buffer": 0,
            "byteOffset": idx_offset,
            "byteLength": idx_len,
            "target": 34963 # ELEMENT_ARRAY_BUFFER
        })
        
        # Accessors
        pa_idx = len(accessors)
        accessors.append({
            "bufferView": pv_idx,
            "byteOffset": 0,
            "componentType": 5126, # FLOAT
            "count": len(data['positions']),
            "type": "VEC3",
            "min": pos_min,
            "max": pos_max
        })
        ia_idx = len(accessors)
        accessors.append({
            "bufferView": iv_idx,
            "byteOffset": 0,
            "componentType": 5125 if use_uint32 else 5123, # UNSIGNED_INT / UNSIGNED_SHORT
            "count": len(data['indices']),
            "type": "SCALAR"
        })
        
        primitives.append({
            "attributes": {"POSITION": pa_idx},
            "indices": ia_idx,
            "material": mat_idx
        })

    b64_buffer = base64.b64encode(bin_buffer).decode('ascii')
    
    gltf_doc = {
        "asset": {"version": "2.0", "generator": "HannuSauna3DGenerator"},
        "scenes": [{"nodes": [0]}],
        "nodes": [{"name": "HannuSauna", "mesh": 0}],
        "meshes": [{"name": "SaunaMesh", "primitives": primitives}],
        "materials": materials_list,
        "accessors": accessors,
        "bufferViews": buffer_views,
        "buffers": [{
            "byteLength": len(bin_buffer),
            "uri": "data:application/octet-stream;base64," + b64_buffer
        }]
    }
    
    with open(gltf_path, "w", encoding="utf-8") as f:
        json.dump(gltf_doc, f, indent=2)

if __name__ == "__main__":
    out_dir = r"C:\Users\david\git\bastu"
    obj_file = os.path.join(out_dir, "hannu_bastu.obj")
    mtl_file = os.path.join(out_dir, "hannu_bastu.mtl")
    gltf_file = os.path.join(out_dir, "hannu_bastu.gltf")
    
    print("Building Hannu Sauna 3D model...")
    model = build_hannu_sauna()
    model.export_obj(obj_file, mtl_file)
    print(f"Exported OBJ: {obj_file}")
    export_gltf(model, gltf_file)
    print(f"Exported GLTF: {gltf_file}")
