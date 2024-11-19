import os
import subprocess
import argparse

def run_command(command):
    """运行命令行命令"""
    process = subprocess.Popen(command, shell=True)
    process.wait()  # 确保命令执行完成

def get_parent_dir(directory):
    """获取父目录"""
    return os.path.dirname(directory)

def main(args):
    # 获取当前脚本所在目录的父目录
    base_dir = get_parent_dir(os.path.abspath(__file__))

    # 设置默认的工作输出文件夹和可执行文件目录
    work_dir = os.path.join(base_dir, args.work_dir)
    sensor_width_file = os.path.join(base_dir, args.sensor_width_file)
    openmvg_bin = os.path.join(base_dir, args.openmvg_bin)
    # 如果images_dir是绝对路径，直接使用；否则，与base_dir拼接
    images_dir = args.images_dir if os.path.isabs(args.images_dir) else os.path.join(base_dir, args.images_dir)

    # 创建工作目录
    os.makedirs(work_dir, exist_ok=True)
    os.chdir(work_dir)
    # 设置匹配目录
    matches_dir = os.path.join(work_dir, "matches")
    os.makedirs(matches_dir, exist_ok=True)
    # 根据sfm模式设置重建目录
    reconstruction_dir = os.path.join(work_dir, f"reconstruction_{args.sfm_mode}")
    os.makedirs(reconstruction_dir, exist_ok=True)
    # 设置导出目录
    export_dir = os.path.join(work_dir, args.export_dir)
    os.makedirs(export_dir, exist_ok=True)

    # 定义导出格式映射字典
    format_mapping = {
        'Agisoft': ('openMVG_main_openMVG2Agisoft', 'agisoft'),
        'CMPMVS': ('openMVG_main_openMVG2CMPMVS', 'cmpmvs'),
        'Colmap': ('openMVG_main_openMVG2Colmap', 'colmap'),
        'Meshlab': ('openMVG_main_openMVG2Meshlab', 'meshlab'),
        'MVE2': ('openMVG_main_openMVG2MVE2', 'mve2'),
        'MVSTEXTURING': ('openMVG_main_openMVG2MVSTEXTURING', 'mvstexturing'),
        'NVM': ('openMVG_main_openMVG2NVM', 'scene.nvm'),
        'openMVS': ('openMVG_main_openMVG2openMVS', 'scene.mvs'),
        'PMVS': ('openMVG_main_openMVG2PMVS', 'PMVS'),
        'WebGL': ('openMVG_main_openMVG2WebGL', 'webgl')
    }

    # 开始处理：
    # 初始化图像
    run_command(f'{os.path.join(openmvg_bin, "openMVG_main_SfMInit_ImageListing")} \
                -i {images_dir} \
                -d {sensor_width_file} \
                -o {matches_dir}')

    # 计算特征
    run_command(f'{os.path.join(openmvg_bin, "openMVG_main_ComputeFeatures")} \
                -i {matches_dir}/sfm_data.json \
                -o {matches_dir}')

    # 特征匹配
    if args.sfm_mode == 'incremental':
        run_command(f'{os.path.join(openmvg_bin, "openMVG_main_ComputeMatches")} \
                    -i {matches_dir}/sfm_data.json \
                    -o {matches_dir} \
                    -f 1 \
                    -n ANNL2')
    elif args.sfm_mode == 'global':
        # 使用全局SfM管道的特征匹配参数
        run_command(f'{os.path.join(openmvg_bin, "openMVG_main_ComputeMatches")} \
                    -i {matches_dir}/sfm_data.json \
                    -o {matches_dir} \
                    -r 0.8 \
                    -g e')

    if args.sfm_mode == 'incremental':
        # 增量sfm重建
        run_command(f'{os.path.join(openmvg_bin, "openMVG_main_IncrementalSfM")} \
                    -i {matches_dir}/sfm_data.json \
                    -m {matches_dir} \
                    -o {reconstruction_dir}')
    elif args.sfm_mode == 'global':
        # 全局sfm重建
        run_command(f'{os.path.join(openmvg_bin, "openMVG_main_GlobalSfM")} \
                    -i {matches_dir}/sfm_data.json \
                    -m {matches_dir} \
                    -o {reconstruction_dir}')

    # 生成颜色点云
    run_command(f'{os.path.join(openmvg_bin, "openMVG_main_ComputeSfM_DataColor")} \
                -i {reconstruction_dir}/sfm_data.bin \
                -o {os.path.join(reconstruction_dir, "colorized.ply")}')

    # 结构从已知姿态
    run_command(f'{os.path.join(openmvg_bin, "openMVG_main_ComputeStructureFromKnownPoses")} \
                -i {reconstruction_dir}/sfm_data.bin \
                -m {matches_dir} \
                -o {os.path.join(reconstruction_dir, "robust.ply")}')

    # 导出步骤
    if args.export_format:
        executable, export_filename = format_mapping[args.export_format]
        run_command(f'{os.path.join(openmvg_bin, executable)} \
                    -i {reconstruction_dir}/sfm_data.bin \
                    -o {os.path.join(export_dir, export_filename)}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='OpenMVG and OpenMVS pipeline script.')
    parser.add_argument('--sfm_mode', type=str, 
                        choices=['incremental', 'global'], 
                        default='incremental', 
                        help='选择SfM模式: incremental 或 global')
    parser.add_argument('--openmvg_bin', type=str, 
                        default='exe', 
                        help='OpenMVG可执行文件目录')
    parser.add_argument('--sensor_width_file', type=str, 
                        default='sensor_width_database/sensor_width_camera_database.txt', 
                        help='传感器宽度数据库文件路径')
    parser.add_argument('--work_dir', type=str, 
                        default='../../result/sfm',
                        help='工作目录')
    parser.add_argument('--images_dir', type=str, 
                        # default='E:/PIE-UAV/昆明BD联勤保障培训与展示会/模拟实时写入影像程序/small_tools_python/SfM/fountain-P11/images', 
                        # default='E:/PIE-UAV/昆明BD联勤保障培训与展示会/模拟实时写入影像程序/small_tools_python/SfM/ReleaseV1.6.Halibut.WindowsBinaries_VS2017/ImageDataset_SceauxCastle/images',
                        default='E:/PIE-UAV/昆明BD联勤保障培训与展示会/模拟实时写入影像程序/small_tools_python/SfM/example_building/images',
                        help='图像目录')
    parser.add_argument('--export_format', type=str, 
                        choices=['Agisoft', 'CMPMVS', 'Colmap', 'Meshlab', 'MVE2', 'MVSTEXTURING', 'NVM', 'openMVS', 'PMVS', 'WebGL'],
                        default='openMVS', 
                        help="Choose export format (default: None)")
    parser.add_argument('--export_dir', type=str, 
                        default="export", 
                        help="Set the export directory (default: 'export')")
    
    args = parser.parse_args()
    main(args)