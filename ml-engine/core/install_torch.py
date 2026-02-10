import platform
import subprocess
import sys
import torch

def run(cmd):
    print(f"\n>>> {cmd}")
    subprocess.check_call(cmd, shell=True)

def detect_backend():
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        return "mps"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return "xpu"
    return "cpu"

def main():
    print("🔍 Jal-Drishti Torch Installer")
    print(f"OS: {platform.system()}")

    backend = detect_backend()
    print(f"Detected backend: {backend}")

    if backend == "cuda":
        cmd = (
            "pip install torch torchvision torchaudio "
            "--index-url https://download.pytorch.org/whl/cu118"
        )
    elif backend == "mps":
        cmd = "pip install torch torchvision torchaudio"
    elif backend == "xpu":
        cmd = (
            "pip install torch torchvision torchaudio "
            "--index-url https://download.pytorch.org/whl/xpu"
        )
    else:
        cmd = (
            "pip install torch torchvision torchaudio "
            "--index-url https://download.pytorch.org/whl/cpu"
        )

    print("\nRecommended install command:")
    print(cmd)

    if "--install" in sys.argv:
        run(cmd)

if __name__ == "__main__":
    main()
