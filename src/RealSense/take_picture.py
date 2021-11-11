import numpy as np                        # fundamental package for scientific computing
import matplotlib.pyplot as plt           # 2D plotting library producing publication quality figures
import pyrealsense2.pyrealsense2 as rs    # Intel RealSense cross-platform open-source API
import open3d as o3d
import imageio
import cv2
print("Environment Ready")



# Configure depth and color streams
# Change resolution here
pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth)
cfg.enable_stream(rs.stream.color)


#Start streaming
profile = pipe.start(cfg)

# Filter generates color images based on input depth frame
colorizer = rs.colorizer()

# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):pipe.wait_for_frames()

# Store frameset
frameset = pipe.wait_for_frames()
color_frame = frameset.get_color_frame()
depth_frame = frameset.get_depth_frame()

# Get intrinsic camera parameters
profile = pipe.get_active_profile()

# Change the type of stereo vision
device = profile.get_device()
depth_sensor = device.query_sensors()[0]
emitter = depth_sensor.get_option(rs.option.emitter_enabled)
print("emitter = ", emitter)
set_emitter = 0 #0 for active stereo vision, 1 for passive stereo vision
depth_sensor.set_option(rs.option.emitter_enabled, set_emitter)
emitter1 = depth_sensor.get_option(rs.option.emitter_enabled)
print("new emitter = ", emitter1)


print(profile)
depth_profile = rs.video_stream_profile(profile.get_stream(rs.stream.depth))
print(depth_profile)
depth_intrinsics = depth_profile.get_intrinsics()
print(depth_intrinsics)
w, h = depth_intrinsics.width, depth_intrinsics.height
print(w,h)


# Cleanup
pipe.stop()
print("Frames Captured")

# Convert images to numpy arrays
depth_image = np.asanyarray(depth_frame.get_data())
color_image = np.asanyarray(color_frame.get_data())
depth_image = cv2.resize(depth_image, (1280, 720))

imageio.imwrite("depth.png", depth_image)
imageio.imwrite("rgb.png", color_image)
print("Files saved")


print("Create pointcloud...")
color_raw = o3d.io.read_image("rgb.png")
depth_raw = o3d.io.read_image("depth.png")
rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
    color_raw, depth_raw, convert_rgb_to_intensity=False)
print(rgbd_image)

plt.subplot(1, 2, 1)
plt.title('RGB image')
plt.imshow(rgbd_image.color)
plt.subplot(1, 2, 2)
plt.title('Depth image')
plt.imshow(rgbd_image.depth)
plt.show()

p = o3d.camera.PinholeCameraIntrinsic()
p.intrinsic_matrix=[[421.139, 0.0, 426.176], [ 0.0, 421.139, 237.017], [ 0.0, 0.0, 1.0]]
pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
    rgbd_image,p)
# Flip it, otherwise the pointcloud will be upside down
pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
o3d.visualization.draw_geometries([pcd])

o3d.io.write_point_cloud("cloud.ply", pcd)

