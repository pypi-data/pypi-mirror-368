from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST
from torchvision import transforms
import matplotlib.pyplot as plt
from tool.compair import compair, run_save_dmt
import torch
import argparse
import scanpy as sc
import wandb
import os
os.environ["OPENBLAS_NUM_THREADS"] = "4"


def cal_svc_acc(data, label):
    from sklearn.model_selection import train_test_split
    from sklearn.svm import SVC
    from sklearn.metrics import accuracy_score
    
    X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=0.2, random_state=0)
    
    clf = SVC(kernel='linear', C=1.0, gamma='auto', random_state=0)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    return acc


if __name__ == '__main__':

    parser = argparse.ArgumentParser() # nihao
    
    parser.add_argument('--epoch', type=int, default=500) # ?
    parser.add_argument('--use_orthogonal', type=int, default=0)
    parser.add_argument('--use_high_manifold_loss', type=int, default=0)
    parser.add_argument('--nu', default=0.01, type=float)
    parser.add_argument('--n_neighbors', default=5, type=int)
    parser.add_argument('--norm_loss', default=1, type=int)
    parser.add_argument('--batch_size', default=1000, type=int)
    parser.add_argument('--temp', default=10.0, type=float)
    
    args = parser.parse_args()
    
    # load
    torch.set_float32_matmul_precision('medium')

    adata = sc.read("/zangzelin/data/difftreedata/data/LimbFilter.h5ad")
    data_all = adata.X.toarray().astype(np.float32)
    label_celltype = adata.obs['celltype'].to_list()
    if filter:
        vars = np.var(data_all, axis=0)
        mask_gene = np.argsort(vars)[-3000:]
        data = data_all[:, mask_gene]

    label_count = {}
    for i in list(set(label_celltype)):
        label_count[i] = label_celltype.count(i)

    label_count = sorted(label_count.items(), key=lambda x: x[1], reverse=True)
    label_count = label_count[:10]

    mask_top10 = np.zeros(len(label_celltype)).astype(np.bool_)
    for str_label in label_count:
        mask_top10[str_label[0] == np.array(label_celltype)] = 1

    data_n = np.array(data).astype(np.float32)[mask_top10]
    label_train_str = np.array(list(np.squeeze(label_celltype)))[mask_top10]

    label_train_str_set = sorted(list(set(label_train_str)))
    label = np.array([label_train_str_set.index(i) for i in label_train_str]).astype(np.int32)
    set_label_str = [str(i) for i in list(set(label))]

    # import pdb; pdb.set_trace()

    wandb.init(project='dmt', entity='zangzelin', name='dmt_epi', config=args)
    # label_train_str = label_meta['marker_anno'].to_list()
    # label_train_str_set = sorted(list(set(label_train_str)))
    # label = np.array([label_train_str_set.index(·i) for i in label_train_str]).astype(np.int32)



    path_f = 'result_epi_all'
    if args.use_orthogonal:
        path_f += 'use_orthogonal_'
    if args.use_high_manifold_loss:
        path_f += 'use_high_manifold_loss_'
        
    acc, fig = run_save_dmt(
        data_n, label, 
        nu=args.nu, n_neighbors=args.n_neighbors,
        save_path=f'{path_f}dmt/', 
        plot=True, 
        max_epochs=args.epoch, 
        num_devices=1,
        use_orthogonal=bool(args.use_orthogonal),
        use_high_manifold_loss=bool(args.use_high_manifold_loss),
        plot_s=4,
        cluster_name=set_label_str,
        norm_loss=bool(args.norm_loss),
        batch_size=args.batch_size,
        temp=args.temp,
        )
    wandb.log({'acc': acc, 'fig': wandb.Image(fig)})
    wandb.finish()
    # run_save_dmt(data, label, max_epochs=100, save_path='result_huada_aqc/', plot=True, num_devices=1)

    