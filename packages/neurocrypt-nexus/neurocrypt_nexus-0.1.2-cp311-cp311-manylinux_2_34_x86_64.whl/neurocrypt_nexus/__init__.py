# This imports the Rust functions from the compiled _core module
# and makes them available at the top level of your package.
from ._core import get_message_from_rust_core, sum_as_string

# This lists what `from neurocrypt_nexus import *` will import
__all__ = ["sum_as_string", "get_message_from_rust_core"]
