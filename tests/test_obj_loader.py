import pytest
import os
from src import obj_loader

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class TestSystem:
    # T01-T04,T11-T18 need GUI,skip in githubCI


    def test_T05_parse_vertices(self):
        obj_path = os.path.join(project_root, 'models', 'cube.obj')
        if not os.path.exists(obj_path):
            pytest.skip("cube.obj not found")
        data = obj_loader.load_obj(obj_path)
        vertex_count = len(data['vertices']) // 3
        assert vertex_count == 8
        print("✓ T05 passed / T05 пройден")

    def test_T06_parse_texture_coords(self):
        obj_path = os.path.join(project_root, 'models', 'paimon', 'paimon.obj')
        if not os.path.exists(obj_path):
            pytest.skip("paimon.obj not found")
        data = obj_loader.load_obj(obj_path)
        texcoord_count = len(data['texcoords']) // 2
        assert texcoord_count == 7269
        print("✓ T06 passed / T06 пройден")

    def test_T07_triangulation(self):
        obj_path = os.path.join(project_root, 'models', 'cube.obj')
        if not os.path.exists(obj_path):
            pytest.skip("cube.obj not found")
        data = obj_loader.load_obj(obj_path)
        assert len(data['indices']) > 0
        print("✓ T07 passed / T07 пройден")

    def test_T08_material_groups(self):
        obj_path = os.path.join(project_root, 'models', 'paimon', 'paimon.obj')
        if not os.path.exists(obj_path):
            pytest.skip("paimon.obj not found")
        data = obj_loader.load_obj(obj_path)
        group_count = len(data['material_groups'])
        assert group_count == 8
        print("✓ T08 passed / T08 пройден")

    def test_T09_parse_mtl(self):
        mtl_path = os.path.join(project_root, 'models', 'paimon', 'o5131fbilmlm.mtl')
        if not os.path.exists(mtl_path):
            pytest.skip("MTL file not found")
        materials = obj_loader.load_mtl(mtl_path)
        assert len(materials) > 0
        print("✓ T09 passed / T09 пройден")

    def test_T10_face_formats(self):
        obj_path = os.path.join(project_root, 'models', 'paimon', 'paimon.obj')
        if not os.path.exists(obj_path):
            pytest.skip("paimon.obj not found")
        data = obj_loader.load_obj(obj_path)
        assert len(data['indices']) > 0
        print("✓ T10 passed / T10 пройден")
