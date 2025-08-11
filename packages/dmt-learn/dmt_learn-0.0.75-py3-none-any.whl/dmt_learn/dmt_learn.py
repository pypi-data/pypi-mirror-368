from .data_model.datamodel_tri_test import MyDataModule

from .model.nnet_new_exp_mix_in_lat_exp_all import DMTEVT_model
from lightning.pytorch import Trainer, seed_everything
import torch
# import trainer
from pynndescent import NNDescent
import os
from sklearn.decomposition import PCA
import numpy as np
from tqdm import tqdm
import lightning as pl

def noise_map_exp(model, data, num_exp=10, noise_level=0.1):
    exp_feature_num = int(data.shape[1] // num_exp)
    emb = model.vis(data)
    distance_list = []
    for i in range(num_exp):
        start_index = i * exp_feature_num
        end_index = (i + 1) * exp_feature_num
        noise_data_delta = torch.rand_like(data) * noise_level * data.std(dim=0)
        noise_data = torch.clone(data)
        noise_data[:, start_index:end_index] += noise_data_delta[:, start_index:end_index]
        noise_emb = model.vis(noise_data)
        distance = torch.norm(noise_emb - emb, dim=1)
        distance_list.append(distance)
    distance_tensor = torch.stack(distance_list, dim=1)
    return distance_tensor

def cal_near_index(data, k=10, pca_dim=100):
    
    os.makedirs("save_near_index", exist_ok=True)
    
    X_rshaped = data.reshape((data.shape[0], -1))
    if pca_dim < X_rshaped.shape[1]:
        X_rshaped = PCA(n_components=pca_dim).fit_transform(X_rshaped)
    
    index = NNDescent(X_rshaped, n_jobs=-1)
    neighbors_index, neighbors_dist = index.query(X_rshaped, k=k + 1)
    neighbors_index = neighbors_index[:, 1:]
    
    return neighbors_index

def Preprocessing(data, k, pca_dim):

    neighbors_index = cal_near_index(
        data=data,
        k=k,
        pca_dim=pca_dim,
    )
    return neighbors_index


class DMTLearn:
    def __init__(self, 
                 n_neighbors=30,
                 n_components=2,
                 random_state=0,
                 max_epochs=200,
                 sample_rate_feature=0.999,
                 lr=0.005,
                 nu=0.5,
                 exaggeration=1.0,
                 T_hidden_size=512,
                 T_num_layers=4,
                 num_use_moe=1,
                 n_jobs=1,
                 num_devices=1,
                 use_orthogonal=False,
                 use_high_manifold_loss=False,
                 norm_loss=True,
                 batch_size=1000,
                 temp=10,
                 loss_type='L',
                 all_g_l_weight=0.5,
                 dim_high=500,  # Default value, can be adjusted as needed
                 save_ckpt_path=None
                 ):
        
        seed_everything(random_state)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        print('device:', self.device)
        
        self.sample_rate_feature = sample_rate_feature
        self.lr = lr
        self.nu = nu
        self.exaggeration = exaggeration
        self.T_hidden_size = T_hidden_size
        self.T_num_layers = T_num_layers
        self.num_use_moe = num_use_moe
        self.max_epochs = max_epochs
        self.n_neighbors = n_neighbors
        self.n_components = n_components
        self.norm_loss = norm_loss
        self.n_jobs = n_jobs
        self.batch_size = batch_size
        self.use_orthogonal = use_orthogonal
        self.use_high_manifold_loss = use_high_manifold_loss
        self.temp = temp
        self.loss_type = loss_type
        self.all_g_l_weight = all_g_l_weight
        self.dim_high = dim_high  # Default value, can be adjusted as needed
        self.save_ckpt_path = save_ckpt_path
        
        
        callbacks = []
        
        if self.save_ckpt_path is not None:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.save_ckpt_path), exist_ok=True)
            lightning_save_ckpt_callback = pl.callbacks.ModelCheckpoint(
                dirpath=os.path.dirname(self.save_ckpt_path),
                filename=os.path.basename(self.save_ckpt_path),
                save_top_k=1,
                monitor='epoch',
                mode='max',
                save_weights_only=True,
            )

            callbacks.append(lightning_save_ckpt_callback)

        if num_devices > 1:
            self.trainer = Trainer(
                max_epochs=max_epochs,
                devices=num_devices,
                accelerator='gpu',
                strategy='ddp',
                enable_checkpointing=False,
                logger=False,
                callbacks=callbacks,
            )
        else:
            self.trainer = Trainer(
                max_epochs=max_epochs,
                devices=num_devices,
                accelerator='gpu',
                enable_checkpointing=False,
                logger=False,
                callbacks=callbacks,
            )
        
    def transform(self, data, batch_size=1000):
        data_tensor = torch.tensor(data).float()
        # import pdb; pdb.set_trace()
        
        num_loop = data_tensor.size(0) // batch_size
        self.model.eval()
        
        list_lat_vis = []
        list_lat_high_dim = []
        with torch.no_grad():
            for i in range(num_loop+1):
                data_tensor_batch = data_tensor[i*batch_size:(i+1)*batch_size]
                if data_tensor_batch.size(0) != 0:
                    lat_masked, lat_high_dim_exp, lat_vis, lat_high_dim = self.model(data_tensor_batch)
                
                    list_lat_vis.append(lat_vis.detach().cpu())
                    list_lat_high_dim.append(lat_high_dim.detach().cpu())
        
        return torch.cat(list_lat_vis, 0).numpy(), torch.cat(list_lat_high_dim, 0).numpy()


    def transform_high(self, data, batch_size=1000):
        data_tensor = torch.tensor(data).float()
        # import pdb; pdb.set_trace()
        
        num_loop = data_tensor.size(0) // batch_size
        self.model.eval()
        
        list_lat_vis = []
        with torch.no_grad():
            for i in range(num_loop+1):
                data_tensor_batch = data_tensor[i*batch_size:(i+1)*batch_size]
                if data_tensor_batch.size(0) != 0:
                    lat_masked, lat_high_dim_exp, lat_vis, lat_high_dim = self.model(data_tensor_batch)
                
                    list_lat_vis.append(lat_high_dim.detach().cpu())
        
        return torch.cat(list_lat_vis, 0).numpy()


    def fit(self, dm):
        


        self.trainer.fit(self.model, dm)


    def extract_embeddings_from_loader(self):
        
        
        model = self.model
        data_loader = self.dm.train_dataloader()
        
        
        model.eval()
        all_embeddings = []
        all_labels = []
        all_datas = []
        all_exp_noist_test_result_dict = []
        # all_fea_noist_test_result_dict = []
        all_xmask = []

        print('start extract_embeddings_from_loader')
        with torch.no_grad():
            for batch in tqdm(data_loader, desc='inference: '):
                # import pdb; pdb.set_trace()
                data_input_item = batch['data_input_item'].to(model.device)
                label = batch['label'].to(model.device)
                x_masked, lat_high_dim_exp, lat_vis, lat_high_dim = model(data_input_item, tau=20)
                
                exp_noist_test_result_dict = []
                # fea_noist_test_result_dict = []
                for i in range(5):
                    exp_noist_test_result = noise_map_exp(model, lat_high_dim, noise_level=i * 0.1 + 0.1)
                    exp_noist_test_result_dict.append(exp_noist_test_result)
                                
                exp_noist_test_result_dict = torch.stack(exp_noist_test_result_dict).cpu()
                # # fea_noist_test_result_dict = torch.stack(fea_noist_test_result_dict).cpu()
                
                exp_noist_test_result_dict = exp_noist_test_result_dict.transpose(0, 1)
                # # fea_noist_test_result_dict = fea_noist_test_result_dict.transpose(0, 1)
                
                all_datas.append(data_input_item.cpu().numpy())
                all_embeddings.append(lat_vis.cpu().numpy())
                all_labels.append(label.cpu().numpy())
                all_exp_noist_test_result_dict.append(exp_noist_test_result_dict.cpu().numpy())
                # all_fea_noist_test_result_dict.append(fea_noist_test_result_dict.cpu().numpy())
                all_xmask.append(x_masked.cpu().numpy())
        
        
        all_datas = np.vstack(all_datas)
        all_embeddings = np.vstack(all_embeddings)
        all_exp_noist_test_result_dict = np.vstack(all_exp_noist_test_result_dict)
        all_xmask = np.vstack(all_xmask)
        all_labels = np.hstack(all_labels)

        return all_datas, all_embeddings, all_exp_noist_test_result_dict, all_xmask, all_labels


    def fit_transform(self, data, neighbors_index=None, return_high_dim=False):

        print('start init model')
        self.model = DMTEVT_model(
            num_input_dim=data.shape[1],
            lr=self.lr,
            nu_lat=self.nu,
            nu_emb=self.nu,
            exaggeration_lat=self.exaggeration,
            exaggeration_emb=self.exaggeration,
            sample_rate_feature=self.sample_rate_feature,
            T_hidden_size=self.T_hidden_size,
            num_use_moe=self.num_use_moe,
            T_num_layers=self.T_num_layers,
            max_epochs=self.max_epochs*5,
            weight_decay=0.000000001,
            use_orthogonal=self.use_orthogonal,
            use_high_manifold_loss=self.use_high_manifold_loss,
            norm_loss=self.norm_loss,
            temp=self.temp,
            loss_type=self.loss_type,
            all_g_l_weight=self.all_g_l_weight,
            vis_dim=self.n_components,
            dim_high=self.dim_high
        )

        self.model = self.model.to(self.device)

        if neighbors_index is None:
            neighbors_index = Preprocessing(data, self.n_neighbors, 64)
        
        print('start init MyDataModule')
        dm = MyDataModule(
            data_npy=data,
            data_name='DMTLEARN',
            pca_dim=64,
            batch_size=self.batch_size,
            num_workers=self.n_jobs,
            K=self.n_neighbors,
            n_f_per_cluster=3,
            l_token=10,
            data_path='./data_path',
            neighbors_index=neighbors_index,
        )
        self.dm = dm
        
        print('start fit')
        self.fit(dm)
        print('start transform')
        vis_results, high_dim_results = self.transform(data)

        if return_high_dim:
            return vis_results, high_dim_results
        else:
            return vis_results