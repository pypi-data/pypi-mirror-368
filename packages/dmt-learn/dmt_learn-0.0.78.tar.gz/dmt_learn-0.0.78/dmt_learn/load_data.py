import numpy as np
import scanpy as sc


num_cluster = 10
num_gene = 500

adata = sc.read("/zangzelin/data/difftreedata/data/EpitheliaCell.h5ad")
adata.obs['celltype']=adata.obs['cell_type']
label_celltype = adata.obs['celltype'].to_list()

# copy a new adata
adata_sub = adata.copy()
sc.pp.subsample(adata_sub, fraction=0.1)
data_all = adata_sub.X.toarray().astype(np.float32)
vars = np.var(data_all, axis=0)
mask_gene = np.argsort(vars)[-1*num_gene:]
adata = adata[:, mask_gene]

data = adata.X.toarray().astype(np.float32)

label_count = {}
for i in list(set(label_celltype)):
    label_count[i] = label_celltype.count(i)

label_count = sorted(label_count.items(), key=lambda x: x[1], reverse=True)
label_count = label_count[:num_cluster]

mask_top10 = np.zeros(len(label_celltype)).astype(np.bool_)
for str_label in label_count:
    mask_top10[str_label[0] == np.array(label_celltype)] = 1

data_n = np.array(data).astype(np.float32)[mask_top10]
label_train_str = np.array(list(np.squeeze(label_celltype)))[mask_top10]

# downsample the 10k data for every cell type
# mask = np.zeros(len(label_train_str)).astype(np.bool_)
# for i in range(num_cluster):
#     # random select 10k data for each cell type
#     random_index = np.random.choice(
#         np.where(label_train_str == label_count[i][0])[0],
#         10000, replace=False)
#     mask[random_index] = 1

# data_n = data_n[mask]
# label_train_str = label_train_str[mask]

mean = data_n.mean()
std = data_n.std()
data_n = (data_n - mean) / std  
label_train_str_set = sorted(list(set(label_train_str)))
label = np.array([label_train_str_set.index(i) for i in label_train_str]).astype(np.int32)

np.save('/zangzelin/data/difftreedata/data/EpitheliaCell_data_n.npy', data_n)
np.save('/zangzelin/data/difftreedata/data/EpitheliaCell_label.npy', label)
