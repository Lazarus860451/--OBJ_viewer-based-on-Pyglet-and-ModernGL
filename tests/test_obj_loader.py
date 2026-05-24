import pytest
import os
import sys
import subprocess
import time
from src import obj_loader

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class TestSystem:

    def test_T01_run_program_with_model(self):
        obj_path = os.path.join(project_root, 'models', 'cube.obj')
        if not os.path.exists(obj_path):
            pytest.skip("cube.obj not found")

        process = subprocess.Popen([sys.executable, os.path.join(project_root, 'main.py'), obj_path])
        time.sleep(2)
        assert process.poll() is None, "Program crashed"
        process.terminate()
        print("✓ T01 passed / T01 пройден")

    def test_T02_no_parameters_shows_help(self):
        result = subprocess.run([sys.executable, os.path.join(project_root, 'main.py')], capture_output=True, text=True)
        output = result.stdout + result.stderr
        assert "Usage" in output or "model_file" in output
        print("✓ T02 passed / T02 пройден")

    def test_T03_file_not_found_error(self):
        result = subprocess.run([sys.executable, os.path.join(project_root, 'main.py'), "notexist.obj"],
                                capture_output=True, text=True)
        output = result.stdout + result.stderr
        assert "Failed" in output or "Error" in output
        print("✓ T03 passed / T03 пройден")

    def test_T04_empty_file_error(self):
        empty_file = "temp_empty.obj"
        f = open(empty_file, 'w')
        f.write("")
        f.close()
        result = subprocess.run([sys.executable, os.path.join(project_root, 'main.py'), empty_file],
                                capture_output=True, text=True)
        os.remove(empty_file)
        output = result.stdout + result.stderr
        assert "Empty" in output or "empty" in output
        print("✓ T04 passed / T04 пройден")

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