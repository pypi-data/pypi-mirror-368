from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST
from torchvision import transforms
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    # load
    DATA = np.load('/zangzelin/data/rong/data_emb.npy')
    LABEL = np.load('/zangzelin/data/rong/y.npy')
    
    # DATA = DATA[:10000]
    # LABEL = LABEL[:10000]
    
    plt.figure(figsize=(50, 10))

    nu_list = [0.001, 0.002, 0.005, 0.01, 0.02]

    for i in range(5):
        dmt = DMTLearn(
            random_state=0,
            max_epochs=20,
            nu=nu_list[i],
        )
        
        vis_data = dmt.fit_transform(DATA)

        plt.subplot(1, 5, i+1)
        
        plt.scatter(vis_data[:, 0], vis_data[:, 1], marker='o', c=LABEL, cmap='tab10', s=0.5)
    
    plt.tight_layout()
    plt.savefig('result.png', dpi=400)
    