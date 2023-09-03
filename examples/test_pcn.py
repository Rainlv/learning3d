# author: Vinit Sarode (vinitsarode5@gmail.com) 03/23/2020

import argparse
import os

import numpy as np
import open3d as o3d
import torch
import torch.utils.data
from torch.utils.data import DataLoader
from tqdm import tqdm

# Only if the files are in example folder.
from examples.utils.import_utils import fix_import_path

fix_import_path()

from models import PCN
from data_utils import ModelNet40Data, ClassificationData
from losses import ChamferDistanceLoss


def display_open3d(input_pc, output):
    input_pc_ = o3d.geometry.PointCloud()
    output_ = o3d.geometry.PointCloud()
    input_pc_.points = o3d.utility.Vector3dVector(input_pc)
    output_.points = o3d.utility.Vector3dVector(output + np.array([1, 0, 0]))
    input_pc_.paint_uniform_color([1, 0, 0])
    output_.paint_uniform_color([0, 1, 0])
    o3d.visualization.draw_geometries([input_pc_, output_])


def test_one_epoch(device, model, test_loader):
    model.eval()
    test_loss = 0.0
    pred = 0.0
    count = 0
    for i, data in enumerate(tqdm(test_loader)):
        points, _ = data

        points = points.to(device)

        output = model(points)
        loss_val = ChamferDistanceLoss()(points, output['coarse_output'])
        print("Loss Val: ", loss_val)
        display_open3d(points[0].detach().cpu().numpy(), output['coarse_output'][0].detach().cpu().numpy())

        test_loss += loss_val.item()
        count += 1

    test_loss = float(test_loss) / count
    return test_loss


def test(args, model, test_loader):
    test_loss = test_one_epoch(args.device, model, test_loader)


def options():
    parser = argparse.ArgumentParser(description='Point Completion Network')
    parser.add_argument('--exp_name', type=str, default='exp_pcn', metavar='N',
                        help='Name of the experiment')
    parser.add_argument('--dataset_path', type=str, default='ModelNet40',
                        metavar='PATH', help='path to the input dataset')  # like '/path/to/ModelNet40'
    parser.add_argument('--eval', type=bool, default=False, help='Train or Evaluate the network.')

    # settings for input data
    parser.add_argument('--dataset_type', default='modelnet', choices=['modelnet', 'shapenet2'],
                        metavar='DATASET', help='dataset type (default: modelnet)')
    parser.add_argument('--num_points', default=1024, type=int,
                        metavar='N', help='points in point-cloud (default: 1024)')

    # settings for PCN
    parser.add_argument('--emb_dims', default=1024, type=int,
                        metavar='K', help='dim. of the feature vector (default: 1024)')
    parser.add_argument('--detailed_output', default=False, type=bool,
                        help='Coarse + Fine Output')

    # settings for on training
    parser.add_argument('--seed', type=int, default=1234)
    parser.add_argument('-j', '--workers', default=4, type=int,
                        metavar='N', help='number of data loading workers (default: 4)')
    parser.add_argument('-b', '--batch_size', default=32, type=int,
                        metavar='N', help='mini-batch size (default: 32)')
    parser.add_argument('--pretrained', default='learning3d/pretrained/exp_pcn/models/best_model.t7', type=str,
                        metavar='PATH', help='path to pretrained model file (default: null (no-use))')
    parser.add_argument('--device', default='cuda:0', type=str,
                        metavar='DEVICE', help='use CUDA if available')

    args = parser.parse_args()
    return args


def main():
    args = options()
    args.dataset_path = os.path.join(os.getcwd(), os.pardir, os.pardir, 'ModelNet40', 'ModelNet40')

    trainset = ClassificationData(ModelNet40Data(train=True))
    testset = ClassificationData(ModelNet40Data(train=False))
    train_loader = DataLoader(trainset, batch_size=args.batch_size, shuffle=True, drop_last=True,
                              num_workers=args.workers)
    test_loader = DataLoader(testset, batch_size=args.batch_size, shuffle=False, drop_last=False,
                             num_workers=args.workers)

    if not torch.cuda.is_available():
        args.device = 'cpu'
    args.device = torch.device(args.device)

    # Create PointNet Model.
    model = PCN(emb_dims=args.emb_dims, detailed_output=args.detailed_output)

    if args.pretrained:
        assert os.path.isfile(args.pretrained)
        model.load_state_dict(torch.load(args.pretrained, map_location='cpu'))
    model.to(args.device)

    test(args, model, test_loader)


if __name__ == '__main__':
    main()
