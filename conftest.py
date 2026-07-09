"""Đảm bảo repo root nằm trên sys.path để test import được `webapp.*`, `tools.*`…
(pytest hoặc `python tests/xxx.py` đều chạy được).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
