import time
from pathlib import Path
from pipeline import JalDrishtiPipeline

pipeline = JalDrishtiPipeline()
base_path = Path(__file__).parent.parent
image_path = str(base_path / "data" / "enhancement" / "raw" / "264286_00007889.jpg")

# Warm-up run
_ = pipeline.run(image_path=image_path)

# Timed run
start = time.time()
for i in range(10):
    result = pipeline.run(image_path=image_path)
elapsed = time.time() - start

avg_time = elapsed / 10
fps = 10 / elapsed

print(f"Average time per frame: {avg_time * 1000:.2f} ms")
print(f"Effective FPS: {fps:.2f}")