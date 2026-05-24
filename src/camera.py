import math
import numpy as np


class Camera:
    def __init__(self, width, height):
        # window size
        self.width = width
        self.height = height

        # camera parameters camera rotates around object
        self.distance = 3.0  # distance
        self.rot_x = 30.0    # pitch angle
        self.rot_y = 45.0    # yaw angle

        # object center
        self.target_x = 0.0
        self.target_y = 0.0
        self.target_z = 0.0

        # avoid prevent lock
        self.max_pitch = 89.0
        self.min_pitch = -89.0

    def get_model_matrix(self):
        """calculate model matrix"""
        model = np.eye(4, dtype=np.float32)
        return model

    def get_view_matrix(self):
        """calculate view matrix"""
        # angle to radians
        pitch_rad = self.rot_x * math.pi / 180.0  # pitch angle
        yaw_rad = self.rot_y * math.pi / 180.0    # yaw angle

        cos_pitch = math.cos(pitch_rad)
        sin_pitch = math.sin(pitch_rad)
        cos_yaw = math.cos(yaw_rad)
        sin_yaw = math.sin(yaw_rad)

        # camera offset
        offset_x = self.distance * cos_pitch * cos_yaw
        offset_y = self.distance * sin_pitch
        offset_z = self.distance * cos_pitch * sin_yaw

        # camera position
        eye_x = self.target_x + offset_x
        eye_y = self.target_y + offset_y
        eye_z = self.target_z + offset_z

        # target point
        center_x = self.target_x
        center_y = self.target_y
        center_z = self.target_z

        # up direction
        up_x = 0.0
        up_y = 1.0
        up_z = 0.0

        # forward vector
        forward_x = center_x - eye_x
        forward_y = center_y - eye_y
        forward_z = center_z - eye_z

        length = math.sqrt(
            forward_x*forward_x +
            forward_y*forward_y +
            forward_z*forward_z
        )
        if length > 0.0001:
            forward_x = forward_x / length
            forward_y = forward_y / length
            forward_z = forward_z / length

        # right vector
        right_x = forward_y * up_z - forward_z * up_y
        right_y = forward_z * up_x - forward_x * up_z
        right_z = forward_x * up_y - forward_y * up_x

        length = math.sqrt(right_x*right_x + right_y*right_y + right_z*right_z)
        if length > 0.0001:
            right_x = right_x / length
            right_y = right_y / length
            right_z = right_z / length

        # real up vector
        real_up_x = right_y * forward_z - right_z * forward_y
        real_up_y = right_z * forward_x - right_x * forward_z
        real_up_z = right_x * forward_y - right_y * forward_x

        # view matrix
        view = np.array([
            [right_x, real_up_x, -forward_x, 0],
            [right_y, real_up_y, -forward_y, 0],
            [right_z, real_up_z, -forward_z, 0],
            [
                -(right_x*eye_x + right_y*eye_y + right_z*eye_z),
                -(real_up_x*eye_x + real_up_y*eye_y + real_up_z*eye_z),
                (forward_x*eye_x + forward_y*eye_y + forward_z*eye_z),
                1
            ]
        ], dtype=np.float32)

        return view

    def get_projection_matrix(self):
        """calculate projection matrix"""
        aspect = self.width / self.height
        fov = 60.0
        near = 0.1
        far = 100.0

        fov_rad = fov * math.pi / 180.0
        tan_half_fov = math.tan(fov_rad / 2.0)

        proj = np.array([
            [1.0 / (aspect * tan_half_fov), 0, 0, 0],
            [0, 1.0 / tan_half_fov, 0, 0],
            [0, 0, -(far + near) / (far - near), -1],
            [0, 0, -(2 * far * near) / (far - near), 0]
        ], dtype=np.float32)

        return proj

    def rotate(self, dx, dy):
        """rotate by mouse movement"""
        # yaw
        self.rot_y = self.rot_y + dx * 0.5

        # pitch
        self.rot_x = self.rot_x + dy * 0.5

        # limit pitch  to prevent lock
        if self.rot_x > self.max_pitch:
            self.rot_x = self.max_pitch
        if self.rot_x < self.min_pitch:
            self.rot_x = self.min_pitch

        if self.rot_y >= 360.0:
            self.rot_y = self.rot_y - 360.0
        if self.rot_y < 0.0:
            self.rot_y = self.rot_y + 360.0

    def zoom(self, delta):
        zoom_speed = 0.2
        self.distance = self.distance - delta * zoom_speed

        if self.distance < 0.5:
            self.distance = 0.5
        if self.distance > 20.0:
            self.distance = 20.0

    def reset(self):

        self.distance = 3.0
        self.rot_x = 30.0
        self.rot_y = 45.0
