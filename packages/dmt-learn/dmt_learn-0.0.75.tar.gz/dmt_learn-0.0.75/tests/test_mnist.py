from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST
from torchvision import transforms
import matplotlib.pyplot as plt
from tool.compair import compair, run_save_dmt
import torch
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
    
    # load
    torch.set_float32_matmul_precision('medium')
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    train_data = MNIST(root='data', train=True, download=True, transform=transform)
    DATA = np.stack([train_data[i][0].numpy().squeeze() for i in range(len(train_data))]).reshape((-1, 784))
    LABEL = np.array([train_data[i][1] for i in range(len(train_data))])

    # for epoch in [5, 10, 20, 30, 40, 60, 80, 100]:
    #     print('epoch', epoch)
    run_save_dmt(
        DATA, LABEL, 
        save_path='result_mnist/', 
        plot=True, 
        max_epochs=100, 
        num_devices=1,
        use_orthogonal=False,
        )
        # run_save_dmt(
        #     DATA, LABEL, 
        #     save_path='result_mnist_use_orthogonal/', 
        #     plot=True, 
        #     max_epochs=epoch, 
        #     num_devices=1,
        #     use_orthogonal=True,
        #     )
    