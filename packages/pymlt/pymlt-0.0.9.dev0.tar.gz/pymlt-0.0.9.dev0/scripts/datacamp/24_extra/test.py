#!/usr/local/bin/python3

import torch

x = torch.rand(5, 3)
print(x)
print(torch.arange(1, 90, 2))


print(torch.is_tensor(x))
