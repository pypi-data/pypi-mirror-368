from loguru import logger


def prestartup_patch():
    def empty_download(*args, **kwargs):
        logger.warning(f"Blocked download {args}")
        return

    import torch.hub

    torch.hub.download_url_to_file = empty_download

    import huggingface_hub

    huggingface_hub.hf_hub_download = empty_download
