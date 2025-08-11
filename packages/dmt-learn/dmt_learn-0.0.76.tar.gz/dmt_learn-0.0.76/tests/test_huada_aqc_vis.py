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
import pandas as pd
import pickle
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
    
    # load
    torch.set_float32_matmul_precision('medium')

    adata = sc.read("/zangzelin/data/huada/After_QC_Batch_leiden.h5ad")
    label_meta = pd.read_csv('/zangzelin/data/huada/AQC_Occ_marker_anno_result.csv')

    label_train_str = label_meta['marker_anno'].to_list()
    label_train_str_set = sorted(list(set(label_train_str)))
    label = np.array([label_train_str_set.index(i) for i in label_train_str]).astype(np.int32)

    data_all = adata.X.astype(np.float32)
    import pdb; pdb.set_trace()

    # np.save('/zangzelin/data/huada/data_all.npy', data_all)
    # np.save('/zangzelin/data/huada/label.npy', label)

    # data_all = np.load('/zangzelin/data/dmthi/aqc_all_data_3000.npy')
    # label = np.load('/zangzelin/data/dmthi/aqc_all_label.npy')
    
    mask = label < 2 
    print(label_train_str[:3])
    
    data_all = data_all[mask]
    label = label[mask]
    
    if data_all.shape[0] > 10000:
        random_index = np.random.choice(data_all.shape[0], 10000, replace=False)
        data_all = data_all[random_index]
        label = label[random_index]
    

    # index_down_sample = np.random.choice(data_all.shape[0], 20000, replace=False)
    # data_all = data_all[index_down_sample]
    # label = label[index_down_sample]
    # import pdb; pdb.set_trace()

    # run_save_dmt(data_all, label, max_epochs=100, save_path='result_huada_aqc/', plot=True, num_devices=1)
    
    dmt = DMTLearn(
        n_components=2,
        max_epochs=100,
        n_jobs=1,
        lr=0.005,
        num_devices=1,
        use_orthogonal=False,
        use_high_manifold_loss=False,
        nu=0.1,
        sample_rate_feature=0.4,
        num_use_moe=2,
    )
    # neighbors_index = Preprocessing(data, n_neighbors, 64)
    vis_data_dmt = dmt.fit_transform(data_all)
    
    datas, embeddings, all_noist_test_result_dict, xmask, labels = dmt.extract_embeddings_from_loader()
    
    relation_exp_fea = np.mean(xmask, axis=0)
    relation_exp_ins = np.mean(xmask, axis=2)
    
    feature_names = adata.var['features'].to_list()
    data_ins_name = [f'cell_{i}' for i in range(datas.shape[0])]
    label_name = [f'label_{i}' for i in range(labels.shape[0])]
    
    cached_data = {
    'datas_input': datas, 
    'embeddings': embeddings, 
    # 'exp_emb_list': exp_emb_list,
    'relation_exp_fea': relation_exp_fea, 
    'relation_exp_ins': relation_exp_ins,
    'xmask': xmask, 
    'labels': labels,
    'feature_names': feature_names,
    'data_ins_name': data_ins_name,
    'label_name': label_name,
    }
    pickle.dump(cached_data, open('nhpcaTOP3_data.pkl', 'wb'))
    
    scatter = plt.scatter(
        vis_data_dmt[:, 0], 
        vis_data_dmt[:, 1], 
        marker='.', 
        c=label, 
        cmap='tab10', 
        s=3)
    plt.savefig('result.png', dpi=400)
    
    
    # run_save_umap(data_all, label, save_path='result_huada_aqc/', plot=True, num_devices=1)
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
    