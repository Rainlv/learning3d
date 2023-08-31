from pathlib import Path

import h5py


class H5Data2Pcd:
    def __init__(self, h5_filepath: Path, pcd_dir: Path):
        self.h5_filepath = h5_filepath
        self.pcd_dir = pcd_dir
        self.h5_data = None
        self.h5_labels = None
        self.pcd_data = None

    def load_h5(self):
        f = h5py.File(str(self.h5_filepath), 'r')
        self.h5_data = f['data'][:]
        self.h5_labels = f['label'][:]
        f.close()

    def convert(self):
        self.load_h5()
        data_path = self.pcd_dir.joinpath("data")
        label_path = self.pcd_dir.joinpath("label")
        data_path.mkdir(parents=True, exist_ok=True)
        label_path.mkdir(parents=True, exist_ok=True)
        for i in range(self.h5_data.shape[0]):
            rel_path = data_path.joinpath(self.h5_filepath.stem + f'_{i}.pcd')
            self.write_single_pcd(self.h5_data[i], rel_path=rel_path)

        for i in range(self.h5_labels.shape[0]):
            rel_path = label_path.joinpath(self.h5_filepath.stem + f'_{i}.pcd')
            self.write_single_pcd(self.h5_data[i], rel_path=rel_path)

    def write_single_pcd(self, points, rel_path):
        # 写文件句柄
        handle = self.pcd_dir.joinpath(rel_path).open('w')
        # 得到点云点数
        point_num = points.shape[0]
        # pcd头部（重要）
        handle.write(
            '# .PCD v0.7 - Point Cloud Data file format\nVERSION 0.7\nFIELDS x y z\nSIZE 4 4 4\nTYPE F F F\nCOUNT 1 1 1')
        string = '\nWIDTH ' + str(point_num)
        handle.write(string)
        handle.write('\nHEIGHT 1\nVIEWPOINT 0 0 0 1 0 0 0')
        string = '\nPOINTS ' + str(point_num)
        handle.write(string)
        handle.write('\nDATA ascii')

        # 依次写入点
        for i in range(point_num):
            string = '\n' + str(points[i, 0]) + ' ' + str(points[i, 1]) + ' ' + str(points[i, 2])
            handle.write(string)
        handle.close()


if __name__ == '__main__':
    h5_filename = Path('/home/i/PycharmProjects/learning3d/data/modelnet40_ply_hdf5_2048/ply_data_test0.h5')
    pcd_dir = Path('/home/i/PycharmProjects/learning3d/data/pcd_data')
    h5_data2pcd = H5Data2Pcd(h5_filename, pcd_dir)
    h5_data2pcd.convert()
