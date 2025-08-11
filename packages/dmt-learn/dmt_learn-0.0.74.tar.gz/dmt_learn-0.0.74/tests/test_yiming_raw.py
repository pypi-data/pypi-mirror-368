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


if __name__ == '__main__':
        
    # set epoch as parameter
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', type=int, default=50)
    parser.add_argument('--use_orthogonal', type=bool, default=False)
    parser.add_argument('--use_high_manifold_loss', type=bool, default=False)
    parser.add_argument('--nu', default=0.2, type=float)
    parser.add_argument('--n_neighbors', default=300, type=int)
    
    
    
    args = parser.parse_args()

    # load
    torch.set_float32_matmul_precision('medium')

    # data_n = np.load('/zangzelin/data/difftreedata/data/EpitheliaCell3000Top20_data_n.npy')
    # label = np.load('/zangzelin/data/difftreedata/data/EpitheliaCell3000Top20_label.npy')

    # data_n = pd.read_csv('/zangzelin/data/celldata/yiming_data/raw/pca.csv')
    
    raw_counts = pd.read_csv('/zangzelin/data/celldata/yiming_data/raw/raw_counts.csv').T
    raw_counts.drop('Unnamed: 0', axis=0, inplace=True)
    
    total_counts = raw_counts.sum(axis=0)

    # 每个细胞检测到的基因数（非零值数量）
    detected_genes_per_cell = (raw_counts > 0).sum(axis=0)

    # 每个基因的总表达量（在所有细胞中的和）
    gene_counts = raw_counts.sum(axis=1)
    
    min_umi = 500          # 细胞总UMI计数下限
    min_genes = 200        # 细胞检测到的最少基因数
    max_mito_percent = 0.1  # 线粒体基因表达比例上限(可选)
    cell_filter = (total_counts > min_umi) & (detected_genes_per_cell > min_genes)
    filtered_counts = raw_counts.loc[:, cell_filter]

    gene_filter = (filtered_counts > 0).sum(axis=1) >= 3
    filtered_counts = filtered_counts.loc[gene_filter, :]


    normalized_counts = filtered_counts.div(filtered_counts.sum(axis=0), axis=1) * 1e4
    log_counts = normalized_counts.applymap(lambda x: np.log1p(x))

    # select top 3000 genes
    vars = np.var(log_counts, axis=1)
    mask_gene = np.argsort(vars)[-3000:]
    log_counts = log_counts.iloc[:, mask_gene]
    data = log_counts.to_numpy()
    
    # save data
    np.save('/zangzelin/data/celldata/yiming_data/raw/normalized_counts3000.npy', data)
    
    labelstr = pd.read_csv('/zangzelin/data/celldata/yiming_data/raw/metadata.csv')['celltype'].to_list()
    
    set_label_str = sorted(list(set(labelstr)))
    label = np.array([set_label_str.index(i) for i in labelstr]).astype(np.int32)

    data_mean = np.mean(data)
    data_std = np.std(data)
    data = (data - data_mean) / data_std
    path_f = 'result_yiming_raw_'
        
    acc_dmt = run_save_dmt(
        data, label, nu=args.nu, n_neighbors=args.n_neighbors,
        save_path=f'{path_f}dmt/', 
        plot=True, 
        max_epochs=args.epoch, 
        num_devices=1,
        use_orthogonal=args.use_orthogonal,
        use_high_manifold_loss=args.use_high_manifold_loss,
        plot_s=4,
        )

    wandb.init(project="dmtlearnyiming", entity="zangzelin", config=args)
    
    wandb.log({'acc_dmt': acc_dmt})
    
    wandb.finish()
    
    
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

