from caravan import Caravan
from model import Model

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

if __name__ == '__main__':

    caravan = Caravan()
    caravan.email('sourish.saswade@gmail.com').group("adsflj").key("1234").gpu_count(4).build()
    
    a = torch.tensor([1,2,3,4,5])
    b = torch.tensor([2,3,4,5,6])
    c = a + b
  
    device = 0
    
    dataset = np.loadtxt('pima-indians.csv', delimiter=',')
    X = dataset[:,0:8]
    y = dataset[:,8]
    
    X = torch.tensor(X, dtype=torch.float32, device=device)
    y = torch.tensor(y, dtype=torch.float32, device=device).reshape(-1,1)

    model = Model().to(device=device)
    
    loss_fn = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.005)

    n_epochs = 5000
    batch_size = 8

    for epoch in range(n_epochs):
        for i in range(0, len(X), batch_size):
            Xbatch = X[i:i+batch_size]
            y_pred = model(Xbatch)
            ybatch = y[i:i+batch_size]
            loss = loss_fn(y_pred, ybatch)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
        print(f'Finished epoch {epoch}, latest loss {loss}')

    y_pred = model(X)

    accuracy = (y_pred.round() == y).float().mean()
    print(f"Accuracy {accuracy}")
