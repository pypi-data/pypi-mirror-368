import os
# import sys
import torch
from torch.utils.cpp_extension import load
from pathlib import Path

_THIS_DIR = Path(__file__).resolve().parent
SRC_CPP = _THIS_DIR / "solve.cpp"
SRC_CU  = _THIS_DIR / "balinski-and-gomory-cuda" / "src" / "solver.cu"

os.environ["TORCH_CUDA_ARCH_LIST"] = "7.5;8.0;8.6;8.9;9.0+PTX"

# from torch.utils.cpp_extension import load
# import torch

# Load extension
cuda_solver = load(name="cuda_solver", sources=[str(SRC_CPP), str(SRC_CU)],
# sources=[
#     'solve.cpp',
#     'balinski-and-gomory-cuda/src/solver.cu',
#     # 'balinski_and_gomory/balinski-and-gomory-cuda/src/solver.h'
# ]
)
