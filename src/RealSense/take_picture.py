import numpy as np                        # fundamental package for scientific computing
import matplotlib.pyplot as plt           # 2D plotting library producing publication quality figures
import pyrealsense2.pyrealsense2 as rs    # Intel RealSense cross-platform open-source API
import open3d as o3d
import imageio
import cv2
import pyransac3d as pyrsc
from datetime import datetime as date
print("Environment Ready")


# Configure depth and color streams
# Change resolution here
pipe = rs.pipeline()
cfg = rs.config()
cfg.enable_stream(rs.stream.depth,848, 480)
cfg.enable_stream(rs.stream.color, 848, 480)

#Start streaming
pipe.start(cfg)

# Filter generates color images based on input depth frame
colorizer = rs.colorizer()

# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):pipe.wait_for_frames()

# Get intrinsic camera parameters
profile = pipe.get_active_profile()

# Change the type of stereo vision
device = profile.get_device()
depth_sensor = device.query_sensors()[0]
emitter = depth_sensor.get_option(rs.option.emitter_enabled)
print("emitter = ", emitter)
set_emitter = 1.0
depth_sensor.set_option(rs.option.emitter_enabled, set_emitter)
emitter1 = depth_sensor.get_option(rs.option.emitter_enabled)
print("new emitter = ", emitter1)

# Store frameset
frameset = pipe.wait_for_frames()
color_frame = frameset.get_color_frame()
depth_frame = frameset.get_depth_frame()

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
depth_image = cv2.resize(depth_image, (848, 480))
color_image = cv2.resize(color_image, (848, 480))

timestamp = date.now().strftime("%Y-%m-%d-%H-%M")
imageio.imwrite("depth"+timestamp+".png", depth_image)
imageio.imwrite("rgb"+timestamp+".png", color_image)
print("Files saved")

#Start streaming
pipe.start(cfg)

# Skip 5 first frames to give the Auto-Exposure time to adjust
for x in range(5):pipe.wait_for_frames()

# Get intrinsic camera parameters
profile2 = pipe.get_active_profile()

# Change the type of stereo vision
device2 = profile2.get_device()
depth_sensor2 = device2.query_sensors()[0]
emitter = depth_sensor2.get_option(rs.option.emitter_enabled)
print("emitter = ", emitter)
set_emitter = 0.0
depth_sensor2.set_option(rs.option.emitter_enabled, set_emitter)
emitter1 = depth_sensor.get_option(rs.option.emitter_enabled)
print("new emitter = ", emitter1)

# Store frameset
frameset2 = pipe.wait_for_frames()
color_frame2 = frameset2.get_color_frame()
depth_frame2 = frameset2.get_depth_frame()

# Cleanup
pipe.stop()
print("Frames Captured")

# Convert images to numpy arrays
depth_image2 = np.asanyarray(depth_frame2.get_data())
color_image2 = np.asanyarray(color_frame2.get_data())
depth_image2 = cv2.resize(depth_image2, (848, 480))
color_image2 = cv2.resize(color_image2, (848, 480))

imageio.imwrite("depth2"+timestamp+".png", depth_image2)
imageio.imwrite("rgb2"+timestamp+".png", color_image2)
print("Files saved")


print("Create pointcloud...")

color_raw = o3d.io.read_image("rgb"+timestamp+".png")
depth_raw = o3d.io.read_image("depth"+timestamp+".png")
rgbd_image = o3d.geometry.RGBDImage.create_from_color_and_depth(
    color_raw, depth_raw, convert_rgb_to_intensity=False)
print(rgbd_image)


color_raw2 = o3d.io.read_image("rgb2"+timestamp+".png")
depth_raw2 = o3d.io.read_image("depth2"+timestamp+".png")
rgbd_image2 = o3d.geometry.RGBDImage.create_from_color_and_depth(
    color_raw2, depth_raw2, convert_rgb_to_intensity=False)

plt.subplot(1, 4, 1)
plt.title('RGB image')
plt.imshow(rgbd_image.color)
plt.subplot(1, 4, 2)
plt.title('Depth image')
plt.imshow(rgbd_image.depth)
plt.subplot(1, 4, 3)
plt.title('RGB image2')
plt.imshow(rgbd_image2.color)
plt.subplot(1, 4, 4)
plt.title('Depth image2')
plt.imshow(rgbd_image2.depth)
plt.show()

p = o3d.camera.PinholeCameraIntrinsic(o3d.camera.PinholeCameraIntrinsicParameters.PrimeSenseDefault)
p.intrinsic_matrix=[[421.139, 0.0, 426.176], [ 0.0, 421.139, 237.017], [ 0.0, 0.0, 1.0]] # 848*480 resolution
#p.intrinsic_matrix=[[635.682, 0.0, 643.285], [ 0.0, 635.682, 355.427], [ 0.0, 0.0, 1.0]] #1280*720 resolution
#p.intrinsic_matrix=[[381.409, 0.0, 321.971], [ 0.0, 381.409, 237.298], [ 0.0, 0.0, 1.0]] #640*480 resolution
pcd = o3d.geometry.PointCloud.create_from_rgbd_image(
    rgbd_image,p)
pcd2 = o3d.geometry.PointCloud.create_from_rgbd_image(
    rgbd_image2,p)

# Flip it, otherwise the pointcloud will be upside down
pcd.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
pcd2.transform([[1, 0, 0, 0], [0, -1, 0, 0], [0, 0, -1, 0], [0, 0, 0, 1]])
# Save the point cloud
o3d.io.write_point_cloud("cloud"+timestamp+".ply", pcd)
o3d.io.write_point_cloud("cloud2"+timestamp+".ply", pcd2)
# Get back the point cloud
pcd_load = o3d.io.read_point_cloud("cloud"+timestamp+".ply")
pcd_load2 = o3d.io.read_point_cloud("cloud2"+timestamp+".ply")
# Visualize the point cloud
o3d.visualization.draw_geometries([pcd])
o3d.visualization.draw_geometries([pcd2])

# open3d librairie to use RANSAC for a circular shape
circ = pyrsc.Circle()

# convert Open3D.o3d.geometry.PointCloud to numpy array (RANSAC needs a numpy array to work)
xyz_load = np.asarray(pcd_load2.points)
# RANSAC implementation for circular shape detection in point clouds
center, axis, radius, inliers = circ.fit(xyz_load, thresh=0.1, maxIteration=2)

# Select the inliers and the outliers points
inlier_cloud = pcd_load2.select_by_index(inliers)
outlier_cloud = pcd_load2.select_by_index(inliers, invert=True)

# Paint the inliers points in red and the rest in grey
inlier_cloud.paint_uniform_color([1, 0, 0])
outlier_cloud.paint_uniform_color([0.6, 0.6, 0.6])

# Visualize the inlier and outlier point clouds
o3d.visualization.draw_geometries([inlier_cloud, outlier_cloud])
