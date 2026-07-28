"""
Pepper Clinical Infinity V6 — Cython compilation (code protection for sale)
© 2026 Lamya Fadlulmola Hamed Ali — All Rights Reserved

Compiles Python logic to native .so / .pyd binaries so buyers cannot read source.

USAGE (run from the project root ~/Desktop/pepper_commercial):
    pip install cython setuptools
    python cython_build/setup_cython.py build_ext --inplace
Then SHIP the .so/.pyd files and DELETE the matching .py sources you want hidden.
Keep pepper_app.py as a small launcher (it imports the compiled modules).
"""
import os, sys
from setuptools import setup
from Cython.Build import cythonize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Backend logic to protect
BACKEND = [
    "backend/app/core/security.py",
    "backend/app/core/licensing.py",
    "backend/app/core/billing.py",
    "backend/app/core/database.py",
    "backend/app/core/config.py",
    "backend/app/services/task_generator.py",
    "backend/app/services/clinical.py",
    "backend/app/services/videos.py",
]

# Frontend logic to protect (UI builders + engines)
FRONTEND = [
    "frontend/vision_engine.py",
    "frontend/motion_verifier.py",
    "frontend/motor_tasks.py",
    "frontend/clinical_local.py",
    "frontend/charts.py",
    "frontend/celebration.py",
    "frontend/session_left.py",
    "frontend/session_mid.py",
    "frontend/session_right.py",
    "frontend/session_screen.py",
    "frontend/pecs_bar.py",
    "frontend/dashboard.py",
    "frontend/api_client.py",
    "frontend/login_screen.py",
]

modules = [os.path.join(ROOT, f) for f in (BACKEND + FRONTEND)
           if os.path.exists(os.path.join(ROOT, f))]

setup(
    name="PepperClinicalV6",
    ext_modules=cythonize(
        modules,
        compiler_directives={"language_level": "3", "annotation_typing": False},
        quiet=True,
    ),
    zip_safe=False,
)
print("\n✓ Cython build complete — .so/.pyd binaries created next to each source.")
print("  Now delete the .py sources you want to hide. Keep pepper_app.py + theme.py.")
print("© 2026 Lamya F. H. Ali")
