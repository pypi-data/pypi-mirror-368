from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST,KMNIST
from torchvision import transforms
import matplotlib.pyplot as plt
from tool.compair import compair, run_save_dmt
import torch
import os
import wandb
import argparse

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
        
    parser = argparse.ArgumentParser()
    parser.add_argument('--epoch', type=int, default=500) # ?
    parser.add_argument('--use_orthogonal', type=int, default=0)
    parser.add_argument('--use_high_manifold_loss', type=int, default=0)
    parser.add_argument('--nu', default=0.2, type=float)
    parser.add_argument('--n_neighbors', default=5, type=int)
    parser.add_argument('--norm_loss', default=1, type=int)
    parser.add_argument('--batch_size', default=1000, type=int)
    parser.add_argument('--temp', default=10.0, type=float)
    args = parser.parse_args()
    
    wandb.init(project='dmt_learn', entity='zangzelin', config=args)
    
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    train_data = KMNIST(root='data', train=True, download=True, transform=transform)
    DATA = np.stack([train_data[i][0].numpy().squeeze() for i in range(len(train_data))]).reshape((-1, 784))
    LABEL = np.array([train_data[i][1] for i in range(len(train_data))])

    set_label_str = [str(i) for i in list(set(LABEL))]


    path_f = 'result_kmnist_all'
    acc, fig = run_save_dmt(
        DATA, LABEL, 
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

    