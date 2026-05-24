import pyglet
import sys
from src import camera, obj_loader, renderer
from src.timer import start_timer, end_timer, print_all_timings


class OBJViewer:
    def __init__(self, obj_filepath):

        start_timer('Total init')

        start_timer('Window create')
        try:
            self.window = pyglet.window.Window(800, 600, "OBJ Viewer")
            self.window.set_location(100, 100)
        except Exception as e:
            print("Unable to create window:", e)
            sys.exit(1)
        end_timer('Window create')

        from pyglet.gl import glEnable, GL_DEPTH_TEST
        glEnable(GL_DEPTH_TEST)

        start_timer('Model load')
        print("Loading model:", obj_filepath)
        try:
            self.model_data = obj_loader.load_obj(obj_filepath)
        except Exception as e:
            print("Failed to load model:", e)
            sys.exit(1)
        end_timer('Model load')

        print("Vertex count:", len(self.model_data['vertices']) // 3)
        print("Triangle count:", len(self.model_data['indices']) // 3)

        start_timer('Renderer init')
        self.renderer = renderer.Renderer(self.window, self.model_data)
        end_timer('Renderer init')

        # create camera, auto aim
        self.camera = camera.Camera(800, 600)

        # camera target is model center
        if 'center' in self.model_data:
            cx, cy, cz = self.model_data['center']
            self.camera.target_x = cx
            self.camera.target_y = cy
            self.camera.target_z = cz
            print("Camera aimed at model center:", (cx, cy, cz))

        # auto adjust camera distance
        if 'size' in self.model_data:
            model_size = self.model_data['size']
            # calculate suitable camera distance
            if model_size > 0:
                suggested_distance = model_size * 1.5
                # limit distance
                if suggested_distance < 1.0:
                    suggested_distance = 1.0
                if suggested_distance > 20.0:
                    suggested_distance = 20.0
                self.camera.distance = suggested_distance
                print("Auto adjusted camera distance:", suggested_distance)

        self.dragging = False
        self.last_x = 0
        self.last_y = 0

        self.window.push_handlers(self)

        end_timer('Total init')
        print_all_timings()

    def on_draw(self):
        self.window.clear()
        self.renderer.update_matrices(self.camera)
        self.renderer.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if button == 1:
            self.dragging = True
            self.last_x = x
            self.last_y = y

    def on_mouse_release(self, x, y, button, modifiers):
        if button == 1:
            self.dragging = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.dragging:
            self.camera.rotate(dx, -dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        self.camera.zoom(scroll_y)

    def on_resize(self, width, height):
        self.camera.width = width
        self.camera.height = height

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.R:
            self.camera.reset()
            # after reset
            if 'center' in self.model_data:
                cx, cy, cz = self.model_data['center']
                self.camera.target_x = cx
                self.camera.target_y = cy
                self.camera.target_z = cz
            print("Camera view reset")

    def run(self):
        pyglet.app.run()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py model_file.obj")
        print("Example: python main.py cube.obj")
        sys.exit(1)

    obj_file = sys.argv[1]
    viewer = OBJViewer(obj_file)
    viewer.run()
