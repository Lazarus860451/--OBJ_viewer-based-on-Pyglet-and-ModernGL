import numpy as np
import os
from test import start_timer, end_timer


def load_obj(filepath):
    """read OBJ file, return needed info"""

    start_timer('2a. OBJ parse')

    # get directory path
    model_dir = os.path.dirname(filepath)

    vertices = []  # vertex
    texcoords = []  # texture
    indices = []  # index
    tex_indices = []

    # material groups
    material_groups = []  # {'name': material name, 'start': start index, 'end': end index}
    current_material = None
    current_start = 0

    # temp storage
    temp_vertices = []
    temp_texcoords = []

    # material info
    materials = {}
    mtl_file = None

    f = open(filepath, 'r', encoding='utf-8')
    lines = f.readlines()
    f.close()

    # check empty file
    if len(lines) == 0:
        print("Error: OBJ file empty")
        raise ValueError("Empty file")

    v_count = 0
    f_count = 0
    vertices = [0.0] * (150000 * 3)
    texcoords = [0.0] * (150000 * 2)
    indices = [0] * (300000 * 3)
    tex_indices = [0] * (300000 * 3)

    vt_count = 0
    temp_v_count = 0

    for line in lines:
        line = line.strip()
        if not line or line[0] == '#':
            continue

        parts = line.split()
        cmd = parts[0]

        # read material file
        if cmd == 'mtllib':
            mtl_filename = parts[1]
            mtl_path = os.path.join(model_dir, mtl_filename)
            if os.path.exists(mtl_path):
                materials = load_mtl(mtl_path)

        # material
        elif cmd == 'usemtl':
            if current_material is not None and f_count > current_start:
                material_groups.append({
                    'name': current_material,
                    'start': current_start,
                    'end': f_count
                })
            current_material = parts[1]
            current_start = f_count

        # vertex
        elif cmd == 'v':
            try:
                x = float(parts[1])
                y = float(parts[2])
                z = float(parts[3])
                vertices[v_count * 3] = x
                vertices[v_count * 3 + 1] = y
                vertices[v_count * 3 + 2] = z
                v_count = v_count + 1
            except:
                print("Warning: skipping bad vertex data", line)

        elif cmd == 'vt':
            try:
                u = float(parts[1])
                v = 0.0
                if len(parts) >= 3:
                    v = float(parts[2])
                texcoords[vt_count * 2] = u
                texcoords[vt_count * 2 + 1] = v
                vt_count = vt_count + 1
            except:
                print("Warning: skipping bad texture coordinate", line)

        elif cmd == 'f':
            try:
                # parse triangle
                for i in range(1, 4):
                    part = parts[i]
                    vals = part.split('/')
                    v_idx = int(vals[0]) - 1
                    temp_vertices.append(v_idx)

                    if len(vals) > 1 and vals[1] != '':
                        vt_idx = int(vals[1]) - 1
                        temp_texcoords.append(vt_idx)
                    else:
                        temp_texcoords.append(-1)

                indices[f_count * 3] = temp_vertices[temp_v_count]
                indices[f_count * 3 + 1] = temp_vertices[temp_v_count + 1]
                indices[f_count * 3 + 2] = temp_vertices[temp_v_count + 2]
                tex_indices[f_count * 3] = temp_texcoords[temp_v_count]
                tex_indices[f_count * 3 + 1] = temp_texcoords[temp_v_count + 1]
                tex_indices[f_count * 3 + 2] = temp_texcoords[temp_v_count + 2]
                f_count = f_count + 1
                temp_v_count = temp_v_count + 3

                # handle quad (4 vertices)
                if len(parts) >= 5:
                    part = parts[4]
                    vals = part.split('/')
                    v_idx = int(vals[0]) - 1
                    temp_vertices.append(v_idx)

                    if len(vals) > 1 and vals[1] != '':
                        vt_idx = int(vals[1]) - 1
                        temp_texcoords.append(vt_idx)
                    else:
                        temp_texcoords.append(-1)

                    indices[f_count * 3] = temp_vertices[temp_v_count - 3]
                    indices[f_count * 3 + 1] = temp_vertices[temp_v_count - 1]
                    indices[f_count * 3 + 2] = temp_vertices[temp_v_count]
                    tex_indices[f_count * 3] = temp_texcoords[temp_v_count - 3]
                    tex_indices[f_count * 3 + 1] = temp_texcoords[temp_v_count - 1]
                    tex_indices[f_count * 3 + 2] = temp_texcoords[temp_v_count]
                    f_count = f_count + 1
                    temp_v_count = temp_v_count + 1
            except:
                print("Warning: skipping bad face data", line)

    # check if we got any vertex or face
    if v_count == 0:
        print("Error: No vertex data in OBJ file")
        raise ValueError("No vertex")

    if f_count == 0:
        print("Error: No face data in OBJ file")
        raise ValueError("No face")

    # add last material group
    if current_material is not None and f_count > current_start:
        material_groups.append({
            'name': current_material,
            'start': current_start,
            'end': f_count
        })

    # trim arrays
    vertices = vertices[:v_count * 3]
    texcoords = texcoords[:vt_count * 2]
    indices = indices[:f_count * 3]
    tex_indices = tex_indices[:f_count * 3]

    vertices_array = np.array(vertices, dtype=np.float32)
    indices_array = np.array(indices, dtype=np.uint32)

    vertex_count = len(vertices) // 3
    texcoord_array = np.zeros(vertex_count * 2, dtype=np.float32)

    # assign texture coordinates to vertices
    i = 0
    while i < len(tex_indices) // 3:
        for j in range(3):
            vi = indices[i * 3 + j]
            ti = tex_indices[i * 3 + j]
            if ti >= 0 and ti < vt_count:
                texcoord_array[vi * 2] = texcoords[ti * 2]
                texcoord_array[vi * 2 + 1] = texcoords[ti * 2 + 1]
        i = i + 1

    # generate default color (gray based on Y height)
    y_coords = vertices_array[1::3]
    min_y = np.min(y_coords)
    max_y = np.max(y_coords)

    if max_y == min_y:
        t = np.full(vertex_count, 0.5, dtype=np.float32)
    else:
        t = (y_coords - min_y) / (max_y - min_y)

    gray = 0.3 + t * 0.6

    colors_array = np.zeros(vertex_count * 3, dtype=np.float32)
    colors_array[0::3] = gray
    colors_array[1::3] = gray
    colors_array[2::3] = gray

    # calculate center point
    center_x = (np.min(vertices_array[0::3]) + np.max(vertices_array[0::3])) / 2
    center_y = (np.min(vertices_array[1::3]) + np.max(vertices_array[1::3])) / 2
    center_z = (np.min(vertices_array[2::3]) + np.max(vertices_array[2::3])) / 2

    # calculate size for auto camera distance
    size_x = np.max(vertices_array[0::3]) - np.min(vertices_array[0::3])
    size_y = np.max(vertices_array[1::3]) - np.min(vertices_array[1::3])
    size_z = np.max(vertices_array[2::3]) - np.min(vertices_array[2::3])
    model_size = max(size_x, size_y, size_z)

    print("Vertex count:", v_count)
    print("Triangle count:", f_count)
    print("Texture coordinate count:", vt_count)
    print("Material group count:", len(material_groups))
    print("Model center:", (center_x, center_y, center_z))
    print("Model size:", model_size)
    for group in material_groups:
        print("  Material:", group['name'], "Triangle range:", group['start'], "-", group['end'])

    data = {
        'vertices': vertices_array,
        'colors': colors_array,
        'indices': indices_array,
        'texcoords': texcoord_array,
        'materials': materials,
        'material_groups': material_groups,
        'model_dir': model_dir,
        'center': (center_x, center_y, center_z),  # model center
        'size': model_size  # model size
    }

    end_timer('2a. OBJ parse')
    return data


def load_mtl(mtl_path):
    """load MTL material file"""

    start_timer('2b. MTL parse')

    materials = {}
    current_material = None

    try:
        f = open(mtl_path, 'r', encoding='utf-8')
    except FileNotFoundError:
        print("Warning: Material file not found", mtl_path)
        end_timer('2b. MTL parse')
        return materials

    for line in f:
        line = line.strip()
        if not line or line[0] == '#':
            continue

        parts = line.split()
        cmd = parts[0]

        if cmd == 'newmtl':
            current_material = parts[1]
            materials[current_material] = {}

        elif cmd == 'map_Kd' and current_material:
            texture_path = ' '.join(parts[1:])
            materials[current_material]['map_Kd'] = texture_path

        elif cmd == 'Kd' and current_material:
            try:
                r = float(parts[1])
                g = float(parts[2])
                b = float(parts[3])
                materials[current_material]['Kd'] = (r, g, b)
            except:
                print("Warning: skipping bad Kd value", line)

    f.close()

    end_timer('2b. MTL parse')
    return materials