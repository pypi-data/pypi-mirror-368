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
import argparse
import wandb


if __name__ == '__main__':
        
    # set epoch as parameter
    parser = argparse.ArgumentParser() # nihao
    
    parser.add_argument('--epoch', type=int, default=500) # ?
    parser.add_argument('--use_orthogonal', type=int, default=0)
    parser.add_argument('--use_high_manifold_loss', type=int, default=0)
    parser.add_argument('--nu', default=0.1, type=float)
    parser.add_argument('--n_neighbors', default=5, type=int)
    parser.add_argument('--norm_loss', default=1, type=int)
    parser.add_argument('--batch_size', default=1000, type=int)
    parser.add_argument('--temp', default=10.0, type=float)
    
    args = parser.parse_args()

    # load
    torch.set_float32_matmul_precision('medium')

    data = np.load('/zangzelin/data/difftreedata/data/EpitheliaCell_new_data_n.npy')
    label = np.load('/zangzelin/data/difftreedata/data/EpitheliaCell_new_label.npy')
    num_cluster = 20
    num_gene = 3000

    # data = np.load(f'/zangzelin/data/difftreedata/data/EpitheliaCell_data_n_all_data.npy')
    # label = np.load(f'/zangzelin/data/difftreedata/data/EpitheliaCell_data_n_all_label.npy')
    # import pdb; pdb.set_trace()
    # # label = np.random.randint(0, num_cluster, data.shape[0])
    set_label_str = [str(i) for i in list(set(label))]

    # # 

    # if data.shape[0] > 100000:
    #     index_sample = np.random.choice(data.shape[0], 100000, replace=False)
    #     data = data[index_sample]
    #     label = label[index_sample]

    # adata = sc.read("/zangzelin/data/difftreedata/data/EpitheliaCell.h5ad")
    # # label_meta = np.load('/zangzelin/data/difftreedata/data/EpitheliaCell_label.npy')
    
    # data_all = adata.X.toarray().astype(np.float32)
    
    # var_gene = np.var(data_all, axis=0)
    # var_gene_index = np.argsort(var_gene)[::-1][:num_gene]
    
    # data_all = data_all[:, var_gene_index]
    # import pdb; pdb.set_trace()
    # cell_type_str = adata.obs['cell_type']
    # set_cell_type_str = sorted(list(set(cell_type_str)))
    # label = np.array([set_cell_type_str.index(i) for i in cell_type_str]).astype(np.int32)
    
    # np.save('/zangzelin/data/difftreedata/data/EpitheliaCell_new_data_n.npy', data_all)
    # np.save('/zangzelin/data/difftreedata/data/EpitheliaCell_new_label.npy', label)
    
    
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
        data, label, 
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
    run_save_umap(
        data, label, save_path=f'{path_f}umap/', plot=True, n_neighbors=args.n_neighbors, plot_s=4
    )
    wandb.log({'acc': acc, 'fig': wandb.Image(fig)})
    wandb.finish()
    # run_save_dmt(data, label, max_epochs=100, save_path='result_huada_aqc/', plot=True, num_devices=1)

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
    