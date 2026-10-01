"""
ORBIT Data Generator Package Shim
Maps Python import 'data_gen' directly to the repository folder 'data-gen'.
"""
import sys
import os

_DATA_GEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data-gen")
if _DATA_GEN_DIR not in sys.path:
    sys.path.insert(0, _DATA_GEN_DIR)

import generator
import fault_injector
import scenarios
import storage_manager

# Re-export modules
sys.modules["data_gen.generator"] = generator
sys.modules["data_gen.fault_injector"] = fault_injector
sys.modules["data_gen.scenarios"] = scenarios
sys.modules["data_gen.storage_manager"] = storage_manager
