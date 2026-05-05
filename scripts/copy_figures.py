"""Pre-render: ensure figures/ is available relative to lectures/ for Quarto."""
import shutil, pathlib

root = pathlib.Path(__file__).parent.parent
src = root / "figures"
dst = root / "lectures" / "figures"

if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)
print(f"Copied {len(list(dst.iterdir()))} figures to lectures/figures/")
