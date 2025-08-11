from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST
from torchvision import transforms
import matplotlib.pyplot as plt
from tool.compair import compair, run_save_dmt, run_save_umap, run_save_pacmap
import torch
import scanpy as sc
import os
import wandb
import argparse
import pandas as pd
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
    
    parser.add_argument('--epoch', type=int, default=200) # ?
    parser.add_argument('--use_orthogonal', type=int, default=0)
    parser.add_argument('--use_high_manifold_loss', type=int, default=0)
    parser.add_argument('--nu', default=0.1, type=float)
    parser.add_argument('--n_neighbors', default=20, type=int)
    parser.add_argument('--norm_loss', default=1, type=int)
    parser.add_argument('--batch_size', default=1000, type=int)
    parser.add_argument('--temp', default=10.0, type=float)
    
    args = parser.parse_args()
    # load
    torch.set_float32_matmul_precision('medium')

    # adata = sc.read("/zangzelin/data/huada/After_QC_Batch_leiden.h5ad")
    # label_meta = pd.read_csv('/zangzelin/data/huada/AQC_Occ_marker_anno_result.csv')

    # label_train_str = label_meta['marker_anno'].to_list()
    # label_train_str_set = sorted(list(set(label_train_str)))
    # label = np.array([label_train_str_set.index(i) for i in label_train_str]).astype(np.int32)

    # data_all = adata.X.astype(np.float32)

    # np.save('/zangzelin/data/huada/data_all.npy', data_all)
    # np.save('/zangzelin/data/huada/label.npy', label)

    data_all = np.load('/zangzelin/data/dmthi/aqc_all_data_3000.npy')
    label = np.load('/zangzelin/data/dmthi/aqc_all_label_62.npy')
    set_label_str = [str(i) for i in list(set(label))]
    # index_down_sample = np.random.choice(data_all.shape[0], 100000, replace=False)
    # data_all = data_all[index_down_sample]
    # label = label[index_down_sample]
    # import pdb; pdb.set_trace()

    wandb.init(project='dmt', entity='zangzelin', name='dmt_epi', config=args)
    path_f = f'result_aqc_normloss{bool(args.norm_loss)}_'
    acc, fig = run_save_dmt(
        data_all, label, 
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

    run_save_dmt(data_all, label, max_epochs=100, save_path='result_huada_aqc/', plot=True, num_devices=1)
    
    
    wandb.log({'acc': acc, 'fig': wandb.Image(fig)})
    wandb.finish()
    # run_save_pacmap(data_all, label, save_path='result_huada_aqc/', plot=True, num_devices=1)
    # run_save_umap(data_all, label, save_path='result_huada_aqc/', plot=True, num_devices=1)
    # acc, fig = run_save_pacmap(
    #     data_all, label, 
    #     save_path=f'pacmap/', 
    #     plot=True, 
    #     # max_epochs=args.epoch, 
    #     # num_devices=1,
    #     # use_orthogonal=bool(args.use_orthogonal),
    #     # use_high_manifold_loss=bool(args.use_high_manifold_loss),
    #     # plot_s=4,
    #     # cluster_name=set_label_str,
    #     # norm_loss=bool(args.norm_loss),
    #     # batch_size=args.batch_size,
    #     # temp=args.temp,
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
    