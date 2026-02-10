import platform
import subprocess
import sys
import torch


def run(cmd):
    try:
        return subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
    except Exception:
        return ""


def detect_nvidia():
    return bool(run("nvidia-smi"))


def detect_amd():
    return bool(run("rocminfo"))


def detect_apple_silicon():
    return platform.system() == "Darwin" and platform.machine() == "arm64"


def detect_intel_gpu():
    return bool(run("lspci | grep -i intel"))


def print_header():
    print("\n[Jal-Drishti] Dependency Advisor")
    print("=" * 45)


def recommend_cuda():
    print("✔ Detected NVIDIA GPU")
    print("✔ Recommended Backend: CUDA (FP16 Enabled)")
    print("\nInstall Commands:")
    print(
        "pip install torch torchvision torchaudio "
        "--index-url https://download.pytorch.org/whl/cu121"
    )
    print("pip install ultralytics opencv-python fastapi uvicorn\n")


def recommend_rocm():
    print("✔ Detected AMD GPU")
    print("✔ Recommended Backend: ROCm (FP32 Preferred)")
    print("\n⚠ Linux Only")
    print("\nInstall Commands:")
    print(
        "pip install torch torchvision torchaudio "
        "--index-url https://download.pytorch.org/whl/rocm5.6"
    )
    print("pip install ultralytics opencv-python fastapi uvicorn\n")


def recommend_mps():
    print("✔ Detected Apple Silicon (M1/M2/M3)")
    print("✔ Recommended Backend: MPS (FP32 Only)")
    print("\n⚠ FP16 NOT recommended on MPS")
    print("\nInstall Commands:")
    print("pip install torch torchvision torchaudio")
    print("pip install ultralytics opencv-python fastapi uvicorn\n")


def recommend_xpu():
    print("✔ Detected Intel GPU")
    print("✔ Recommended Backend: Intel XPU (Experimental)")
    print("\n⚠ FP16 unstable")
    print("\nInstall Commands:")
    print("pip install torch torchvision torchaudio --extra-index-url https://pytorch-extension.intel.com/release-whl/stable")
    print("pip install ultralytics opencv-python fastapi uvicorn\n")


def recommend_cpu():
    print("✔ No compatible GPU detected")
    print("✔ Recommended Backend: CPU (Safe Fallback)")
    print("\nInstall Commands:")
    print("pip install torch torchvision torchaudio")
    print("pip install ultralytics opencv-python fastapi uvicorn\n")


def main():
    print_header()

    if detect_nvidia():
        recommend_cuda()
    elif detect_amd():
        recommend_rocm()
    elif detect_apple_silicon():
        recommend_mps()
    elif detect_intel_gpu():
        recommend_xpu()
    else:
        recommend_cpu()

    print("✔ Jal-Drishti is guaranteed to run on this configuration.")
    print("✔ No code changes required.\n")


if __name__ == "__main__":
    main()
