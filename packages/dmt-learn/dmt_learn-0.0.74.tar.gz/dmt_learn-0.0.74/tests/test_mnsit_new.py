from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST
from torchvision import transforms
import matplotlib.pyplot as plt
from tool.compair import compair, run_save_dmt, run_save_umap
import torch
import scanpy as sc
import os
os.environ["OPENBLAS_NUM_THREADS"] = "4"
import numpy as np
import scanpy as sc
import pandas as pd
import wandb
import argparse
import uuid


if __name__ == '__main__':
        
    # set epoch as parameter
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', type=int, default=200)
    parser.add_argument('--use_orthogonal', type=bool, default=False)
    parser.add_argument('--use_high_manifold_loss', type=bool, default=False)
    parser.add_argument('--nu', default=0.2, type=float)
    parser.add_argument('--n_neighbors', default=10, type=int)

    args = parser.parse_args()
    # load
    torch.set_float32_matmul_precision('medium')

    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    train_data = MNIST(root='data', train=True, download=True, transform=transform)
    DATA = np.stack([train_data[i][0].numpy().squeeze() for i in range(len(train_data))]).reshape((-1, 784))
    LABEL = np.array([train_data[i][1] for i in range(len(train_data))])

    path_f = 'result_mnist_'
    # if args.use_orthogonal:
    #     path_f += 'use_orthogonal_'
    # if args.use_high_manifold_loss:
    #     path_f += 'use_high_manifold_loss_'
    uuid_str = str(uuid.uuid4())[:5]
        
    acc_dmt = run_save_dmt(
        DATA, LABEL, nu=args.nu, n_neighbors=args.n_neighbors,
        save_path=f'{path_f}dmt{uuid_str}{args.nu}/', 
        plot=True, 
        max_epochs=args.epoch, 
        num_devices=1,
        use_orthogonal=args.use_orthogonal,
        use_high_manifold_loss=args.use_high_manifold_loss,
        plot_s=4,
        cluster_name=[str(i) for i in range(10)],
        )

    # run_save_umap(
    #     data, label, 
    #     save_path=f'{path_f}umap/', 
    #     plot=True, 
    #     num_devices=1,
    #     plot_s=4,
    #     )
    # dmt = DMTLearn(
    #     random_state=0,
    #     max_epochs=20,
    # )
    
    # vis_data = dmt.fit_transform(DATA)
    # print('vis_data.shape', vis_data.shape)

    # acc = cal_svc_acc(vis_data, LABEL)
    # print('acc', acc)
    
    # plt.figure(figsize=(8, 6))
    # plt.scatter(vis_data[:, 0], vis_data[:, 1], marker='.', c=LABEL, cmap='tab10', s=0.05)
    # plt.colorbar()
    # plt.savefig('result.png', dpi=400)
    
# 读取 1w_Frac_spRNA.rds

