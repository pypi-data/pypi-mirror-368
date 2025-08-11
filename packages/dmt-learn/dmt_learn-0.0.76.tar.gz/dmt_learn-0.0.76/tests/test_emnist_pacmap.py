from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST, EMNIST
from torchvision import transforms
import matplotlib.pyplot as plt
from tool.compair import compair, run_save_dmt, run_save_pacmap
import torch
import os
import argparse
import wandb

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
    
    parser.add_argument('--epoch', type=int, default=100) # ?
    parser.add_argument('--use_orthogonal', type=int, default=0)
    parser.add_argument('--use_high_manifold_loss', type=int, default=0)
    parser.add_argument('--nu', default=0.2, type=float)
    parser.add_argument('--n_neighbors', default=5, type=int)
    parser.add_argument('--norm_loss', default=1, type=int)
    parser.add_argument('--batch_size', default=1000, type=int)
    parser.add_argument('--temp', default=10.0, type=float)
    
    args = parser.parse_args()
    wandb.init(project='dmt', entity='zangzelin', name='dmt_emnist', config=args)
    
    # load
    torch.set_float32_matmul_precision('medium')
    transform = transforms.Compose([
        transforms.ToTensor(),  # Converts PIL Image to Tensor
    ])

    # Load the EMNIST dataset with the transformation applied
    train_data = EMNIST(root='/zangzelin/data/', train=True, split="byclass", download=True, transform=transform)

    # Convert images to a NumPy array
    DATA = np.stack([train_data[i][0].numpy().squeeze() for i in range(len(train_data))]).reshape((-1, 784))

    # Convert labels to a NumPy array
    LABEL = np.array([train_data[i][1] for i in range(len(train_data))])
    set_label_str = sorted(list(set(LABEL)))
    
    np.save('emnist_data.npy', DATA)
    np.save('emnist_label.npy', LABEL)

    # import pdb; pdb.set_trace()

    path_f = f'result_normloss{bool(args.norm_loss)}_'
    set_label_str = [str(i) for i in set_label_str]

    down_sample_index = np.random.choice(DATA.shape[0], 100000, replace=False)
    DATA = DATA[down_sample_index]
    LABEL = LABEL[down_sample_index]

    # for epoch in [5, 10, 20, 30, 40, 60, 80, 100]:
    #     print('epoch', epoch)
    acc, fig = run_save_pacmap(
        DATA, LABEL, 
        save_path=f'{path_f}dmt/', 
        plot=True, 
        # max_epochs=args.epoch, 
        # num_devices=1,
        # use_orthogonal=bool(args.use_orthogonal),
        # use_high_manifold_loss=bool(args.use_high_manifold_loss),
        # plot_s=4,
        # cluster_name=set_label_str,
        # norm_loss=bool(args.norm_loss),
        # batch_size=args.batch_size,
        # temp=args.temp,
        )
    
    print('acc', acc)

    # wandb.log({'acc': acc, 'fig': wandb.Image(fig)})
    # wandb.finish()
    