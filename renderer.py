import moderngl as mgl
import numpy as np
import pyglet
import shaders
import os
import glob
from test import start_timer, end_timer


class Renderer:
    def __init__(self, window, model_data):
        self.ctx = mgl.create_context()

        self.vertices = model_data['vertices']
        self.colors = model_data['colors']
        self.indices = model_data['indices']
        self.texcoords = model_data['texcoords']
        self.materials = model_data['materials']
        self.material_groups = model_data['material_groups']
        self.model_dir = model_data['model_dir']

        # compile shader
        start_timer('Shader compile')
        self.program = self.ctx.program(
            vertex_shader=shaders.VERTEX_SHADER,
            fragment_shader=shaders.FRAGMENT_SHADER
        )
        end_timer('Shader compile')

        # combine data: position(3) + color(3) + texture coord(2)
        vertex_count = len(self.vertices) // 3
        combined_data = []

        i = 0
        while i < vertex_count:
            vx = self.vertices[i * 3]
            vy = self.vertices[i * 3 + 1]
            vz = self.vertices[i * 3 + 2]
            cx = self.colors[i * 3]
            cy = self.colors[i * 3 + 1]
            cz = self.colors[i * 3 + 2]
            tx = self.texcoords[i * 2]
            ty = self.texcoords[i * 2 + 1]

            combined_data.append(vx)
            combined_data.append(vy)
            combined_data.append(vz)
            combined_data.append(cx)
            combined_data.append(cy)
            combined_data.append(cz)
            combined_data.append(tx)
            combined_data.append(ty)

            i = i + 1

        combined_array = np.array(combined_data, dtype=np.float32)

        # create VBO, EBO, VAO
        self.vbo = self.ctx.buffer(combined_array)
        self.ebo = self.ctx.buffer(self.indices)
        self.vao = self.ctx.vertex_array(
            self.program,
            [(self.vbo, '3f 3f 2f', 'aPos', 'aColor', 'aTexCoord')],
            self.ebo
        )

        # get uniform locations
        self.model_loc = self.program['model']
        self.view_loc = self.program['view']
        self.proj_loc = self.program['projection']

        self.material_textures = {}

        self.load_all_textures()

    def load_all_textures(self):
        """load texture for each material"""
        start_timer('Texture load')
        print("Model directory:", self.model_dir)
        print("Material list:", list(self.materials.keys()))
        for mat_name in self.materials:
            print("  Material:", mat_name, "->", self.materials[mat_name])


        # get all image files in directory
        image_files = {}
        image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']

        for ext in image_extensions:
            pattern = os.path.join(self.model_dir, ext)
            files = glob.glob(pattern)
            for f in files:
                base_name = os.path.basename(f).lower()
                name_without_ext = os.path.splitext(base_name)[0]
                image_files[name_without_ext] = f

        # find texture for each material
        for mat_name in self.materials:
            mat = self.materials[mat_name]
            texture_path = None

            # method 1: get map_Kd from mtl file
            if 'map_Kd' in mat:
                texture_path = mat['map_Kd']
                if not os.path.isabs(texture_path):
                    texture_path = os.path.join(self.model_dir, texture_path)
                if not os.path.exists(texture_path):
                    texture_path = None

            # method 2: find by material name
            if texture_path is None:
                mat_lower = mat_name.lower()
                if mat_lower.startswith('none_'):
                    mat_lower = mat_lower[5:]
                if mat_lower.endswith('_diffuse'):
                    mat_lower = mat_lower[:-8]

                if mat_lower in image_files:
                    texture_path = image_files[mat_lower]

            # method 3: fuzzy match by material name
            if texture_path is None:
                mat_lower = mat_name.lower()
                for img_name in image_files:
                    if mat_lower in img_name or img_name in mat_lower:
                        texture_path = image_files[img_name]
                        break

            # load texture
            if texture_path is not None and os.path.exists(texture_path):
                print("Material [", mat_name, "] loading texture:", texture_path)
                try:
                    img = pyglet.image.load(texture_path)
                    texture_data = img.get_image_data()

                    width = img.width
                    height = img.height
                    data = texture_data.get_data('RGB', width * 3)

                    tex = self.ctx.texture((width, height), 3, data)
                    tex.filter = (mgl.LINEAR, mgl.LINEAR)
                    self.material_textures[mat_name] = tex
                    print("  Texture loaded! Size:", width, "x", height)
                except:
                    print("  Texture load failed:", texture_path)
                    self.material_textures[mat_name] = None
            else:
                self.material_textures[mat_name] = None
                print("Material [", mat_name, "] no texture found, using color render")

        loaded_count = 0
        for mat_name in self.material_textures:
            if self.material_textures[mat_name] is not None:
                loaded_count = loaded_count + 1
        print("\nLoaded", loaded_count, "textures")

        end_timer('Texture load')

    def update_matrices(self, camera):
        model = camera.get_model_matrix()
        view = camera.get_view_matrix()
        proj = camera.get_projection_matrix()

        self.model_loc.write(model)
        self.view_loc.write(view)
        self.proj_loc.write(proj)

    def draw(self):
        """render by material groups"""
        if len(self.material_groups) == 0:
            # no material group, use first texture to render all
            if len(self.material_textures) > 0:
                for tex in self.material_textures.values():
                    if tex is not None:
                        tex.use(0)
                        break
            self.vao.render(mgl.TRIANGLES)
            return

        for group in self.material_groups:
            mat_name = group['name']
            start = group['start']
            end = group['end']

            # calculate triangle count to render
            triangle_count = end - start
            if triangle_count <= 0:
                continue

            tex = None
            if mat_name in self.material_textures:
                tex = self.material_textures[mat_name]

            if tex is not None:
                tex.use(0)

            # render from start triangle, count = triangle_count
            start_index = start * 3
            index_count = triangle_count * 3

            # prevent index out of range
            try:
                self.vao.render(mgl.TRIANGLES, vertices=start_index, first=index_count)
            except:
                print("Render error for material group:", mat_name)