from loguru import logger

try:
    from nodes import NODE_CLASS_MAPPINGS, LoadImage
except ImportError:
    logger.error(
        "failed to import ComfyUI nodes modules, ensure PYTHONPATH is set correctly. (export PYTHONPATH=$PYTHONPATH:/path/to/ComfyUI)"
    )
    exit(1)


class BizyDraftLoadImage(LoadImage):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {"image": ([], {"image_upload": True})},
        }

    @classmethod
    def VALIDATE_INPUTS(s, image, *args, **kwargs):
        return True


def hijack_nodes():
    if "LoadImage" in NODE_CLASS_MAPPINGS:
        del NODE_CLASS_MAPPINGS["LoadImage"]
    NODE_CLASS_MAPPINGS["LoadImage"] = BizyDraftLoadImage

    logger.info("[BizyDraft] Hijacked LoadImage node to BizyDraftLoadImage.")
