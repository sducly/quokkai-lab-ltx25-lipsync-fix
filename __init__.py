"""ComfyUI entry point for the bundled, unchanged RC2 node."""

from .custom_nodes.quokkailab_audio import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
