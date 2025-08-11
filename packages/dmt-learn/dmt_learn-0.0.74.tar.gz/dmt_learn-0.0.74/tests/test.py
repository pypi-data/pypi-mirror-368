from dmt_learn import DMTLearn
from sklearn import datasets
import numpy as np
from torchvision.datasets import MNIST
from torchvision import transforms
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    # load
    transform = transforms.Compose([
        transforms.ToTensor(),
    ])
    train_data = MNIST(root='data', train=True, download=True, transform=transform)
    DATA = np.stack([train_data[i][0].numpy().squeeze() for i in range(len(train_data))]).reshape((-1, 784))
    LABEL = np.array([train_data[i][1] for i in range(len(train_data))])
    
    
    dmt = DMTLearn(
        random_state=0,
        max_epochs=20,
    )
    
    vis_data = dmt.fit_transform(DATA)
    print('vis_data.shape', vis_data.shape)
    
    
    plt.figure(figsize=(8, 6))
    plt.scatter(vis_data[:, 0], vis_data[:, 1], marker='.', c=LABEL, cmap='tab10', s=0.05)
    plt.colorbar()
    plt.savefig('result.png', dpi=400)
    