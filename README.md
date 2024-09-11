# PointCloudsFastTinning
This project implements a fast point cloud thinning algorithm based on sample point spatial neighborhood and provides a graphical user interface (GUI) to load, display, and manipulate point cloud data.

## Features

- Load PLY format point cloud data
- Display and rotate point cloud
- Adjust parameters of the point cloud thinning algorithm
- Save the thinned point cloud data

## Dependencies

- Python 3.x
- Open3D
- NumPy
- ImGui
- GLFW
- PyOpenGL
- Tkinter
- Pandas

## Installation

1. Clone this repository to your local machine:

   ```sh
   git clone https://github.com/yourusername/point-cloud-thinning.git
   cd point-cloud-thinning
   ```

2. Install the required Python libraries:

   ```sh
   pip install open3d numpy imgui glfw PyOpenGL pandas
   ```

## Usage

1. Run the main program:

   ```sh
   python compress_point/main.py
   ```

2. In the GUI, you can:

   - Click the "Load PLY File" button to load point cloud data.
   - Check the "Enable Thinning" checkbox to enable the point cloud thinning algorithm.
   - Use the sliders to adjust the distance threshold (ds), height threshold (dh), and LOD level.
   - Click the "Save Simplified Point Cloud" button to save the thinned point cloud data.

## File Descriptions

- `compress_point/main.py`: The main program, containing the GUI and point cloud rendering logic.
- `compress_point/mouse_controller.py`: The MouseController class, used to handle mouse input.
- `compress_point/point_cloud_thinning.py`: The implementation of the point cloud thinning algorithm.

## Example

- A Point Clouds Fast Thinning Algorithm Based on Sample Point Spatial Neighborhood
  ![Point_Cloud_Tinning](./assets/Point_Cloud_Tinning-1726049378012-1.gif)

## Reference **Algorithm** 

- Wei J, Xu M, Xiu H. A point clouds fast thinning algorithm based on sample point spatial neighborhood[J]. Journal of Information Processing Systems, 2020, 16(3): 688-698.

## License

This project is licensed under the MIT License. For more information, see the `LICENSE` file.
