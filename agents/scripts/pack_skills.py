"""
pack_skills.py — Package each skill directory as ZIP for MuleRun Agent Builder
Usage: python scripts/pack_skills.py
Output: agents/dist/macro-sentinel.zip, allocator.zip, etc.
"""
import os
import zipfile
from pathlib import Path

SKILLS_DIR = Path(__file__).parent.parent / "src" / "skills"
DIST_DIR   = Path(__file__).parent.parent / "dist"
DIST_DIR.mkdir(exist_ok=True)

SKILL_NAMES = [
    "macro-sentinel",
    "allocator",
    "execution-router",
    "risk-guardian",
    "reporting-scribe",
]

for skill_name in SKILL_NAMES:
    skill_path = SKILLS_DIR / skill_name
    zip_path   = DIST_DIR / f"{skill_name}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in skill_path.rglob("*"):
            if file_path.is_file() and "__pycache__" not in str(file_path):
                arcname = skill_name + "/" + str(file_path.relative_to(skill_path))
                zf.write(file_path, arcname)

    size_kb = zip_path.stat().st_size / 1024
    print(f"  {zip_path.name} ({size_kb:.1f} KB)")

print(f"\nAll skill ZIPs saved to: {DIST_DIR}")
print("Next: Upload each ZIP to MuleRun Agent Builder -> Select Skills")
