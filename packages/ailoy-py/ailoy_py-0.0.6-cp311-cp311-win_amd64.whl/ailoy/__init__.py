"""""" # start delvewheel patch
def _delvewheel_patch_1_11_1():
    import os
    if os.path.isdir(libs_dir := os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, 'ailoy_py.libs'))):
        os.add_dll_directory(libs_dir)


_delvewheel_patch_1_11_1()
del _delvewheel_patch_1_11_1
# end delvewheel patch

if __doc__ is None:
    try:
        import importlib.metadata

        meta = importlib.metadata.metadata("ailoy-py")
        __doc__ = meta.get("Description")
    except importlib.metadata.PackageNotFoundError:
        pass

if __doc__ is None:
    from pathlib import Path

    readme = Path(__file__).parent.parent / "README.md"
    if readme.exists():
        __doc__ = readme.read_text()
    else:  # fallback docstring
        __doc__ = "# ailoy-py\n\nPython binding for Ailoy runtime APIs"

from .agent import Agent, AudioContent, BearerAuthenticator, ImageContent, TextContent, ToolAuthenticator  # noqa: F401
from .models import APIModel, LocalModel  # noqa: F401
from .runtime import AsyncRuntime, Runtime  # noqa: F401
from .vector_store import VectorStore  # noqa: F401
