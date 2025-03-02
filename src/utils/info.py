#!/usr/bin/env python3
import torch

def info():
    device = "cuda" if torch.cuda.is_available() else "cpu"