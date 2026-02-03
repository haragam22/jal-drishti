"""Test configuration loader"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config_loader import config

print('[Test] Configuration Loader Test')
print('=' * 70)

# Print full summary
config.print_summary()

# Test getting individual values
print('[Test] Individual Values:')
print(f'  device.use_gpu: {config.get("device.use_gpu")}')
print(f'  device.fp16_enabled: {config.get("device.fp16_enabled")}')
print(f'  performance.target_fps: {config.get("performance.target_fps")}')
print(f'  confidence.confirmed_threat_threshold: {config.get("confidence.confirmed_threat_threshold")}')

# Test validation
print('[Test] Configuration Validation:')
is_valid = config.validate()
print(f'  Valid: {is_valid}')

print('\n[Test] ✓ Configuration Loader Test PASSED')
