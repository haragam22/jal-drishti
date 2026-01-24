from pipeline import JalDrishtiPipeline
import numpy as np

pipeline = JalDrishtiPipeline()

# Test 1: None input
result = pipeline.run(image_array=None)
assert result['state'] == 'SAFE_MODE'
assert 'error' in result
print("✅ None input handled correctly")

# Test 2: Empty array
result = pipeline.run(image_array=np.array([]))
assert result['state'] == 'SAFE_MODE'
assert 'error' in result
print("✅ Empty array handled correctly")

# Test 3: Wrong dimensions
result = pipeline.run(image_array=np.zeros((100, 100)))
assert result['state'] == 'SAFE_MODE'
assert 'error' in result
print("✅ Wrong dimensions handled correctly")

print("\n🎉 All frame validity tests passed!")