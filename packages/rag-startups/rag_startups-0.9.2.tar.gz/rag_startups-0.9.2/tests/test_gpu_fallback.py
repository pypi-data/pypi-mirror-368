import torch


def test_gpu_fallback():
    """Test that GPU code falls back to CPU correctly"""
    print("\nGPU Fallback Test Results:")
    print("-" * 50)
    print(f"CUDA Available: {torch.cuda.is_available()}")
    print(
        f"Device being used: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}"
    )
    print(f"PyTorch version: {torch.__version__}")
    print("-" * 50)

    # Create a simple tensor operation that would use GPU if available
    x = torch.randn(2, 3)
    print(f"Tensor device: {x.device}")  # Should show CPU

    return True


if __name__ == "__main__":
    test_gpu_fallback()
