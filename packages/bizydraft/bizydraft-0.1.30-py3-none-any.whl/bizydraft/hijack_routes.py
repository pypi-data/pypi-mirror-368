import asyncio
import math
import mimetypes
import os
import uuid

from aiohttp import ClientSession, ClientTimeout, web
from loguru import logger

try:
    import execution
    from server import PromptServer

    comfy_server = PromptServer.instance
except ImportError:
    logger.error(
        "failed to import ComfyUI modules, ensure PYTHONPATH is set correctly. (export PYTHONPATH=$PYTHONPATH:/path/to/ComfyUI)"
    )
    exit(1)


BIZYDRAFT_MAX_FILE_SIZE = int(
    os.getenv("BIZYDRAFT_MAX_FILE_SIZE", 100 * 1024 * 1024)
)  # 100MB
BIZYDRAFT_REQUEST_TIMEOUT = int(
    os.getenv("BIZYDRAFT_REQUEST_TIMEOUT", 20 * 60)
)  # 20分钟
BIZYDRAFT_CHUNK_SIZE = int(os.getenv("BIZYDRAFT_CHUNK_SIZE", 1024 * 16))  # 16KB


async def view_image(request, old_handler):
    logger.debug(f"Received request for /view with query: {request.rel_url.query}")
    if "filename" not in request.rel_url.query:
        logger.warning("'filename' not provided in query string, returning 404")
        return web.Response(status=404, text="'filename' not provided in query string")

    filename = request.rel_url.query["filename"]
    subfolder = request.rel_url.query.get("subfolder", "")

    if not filename.startswith(("http://", "https://")) and not subfolder.startswith(
        ("http://", "https://")
    ):
        logger.warning(f"Invalid filename format: {filename}, only URLs are supported")
        return web.Response(
            status=400, text="Invalid filename format(only url supported)"
        )

    try:
        filename = (
            f"{subfolder}/{filename}"
            if not filename.startswith(("http://", "https://"))
            else filename
        )  # preview 3d request: https://host:port/api/view?filename=filename.glb&type=output&subfolder=https://bizyair-dev.oss-cn-shanghai.aliyuncs.com/outputs&rand=0.5763957215362988

        content_type, _ = mimetypes.guess_type(filename)
        if content_type and any(x in content_type for x in ("image", "video")):
            return web.HTTPFound(filename)

        timeout = ClientTimeout(total=BIZYDRAFT_REQUEST_TIMEOUT)
        async with ClientSession(timeout=timeout) as session:
            async with session.get(filename) as resp:
                resp.raise_for_status()
                content_length = int(resp.headers.get("Content-Length", 0))
                if content_length > BIZYDRAFT_MAX_FILE_SIZE:
                    logger.warning(
                        f"File size {human_readable_size(content_length)} exceeds limit {human_readable_size(BIZYDRAFT_MAX_FILE_SIZE)}"
                    )
                    return web.Response(
                        status=413,
                        text=f"File size exceeds limit ({human_readable_size(BIZYDRAFT_MAX_FILE_SIZE)})",
                    )

                headers = {
                    "Content-Disposition": f'attachment; filename="{uuid.uuid4()}"',
                    "Content-Type": "application/octet-stream",
                }

                proxy_response = web.StreamResponse(headers=headers)
                await proxy_response.prepare(request)

                total_bytes = 0
                async for chunk in resp.content.iter_chunked(BIZYDRAFT_CHUNK_SIZE):
                    total_bytes += len(chunk)
                    if total_bytes > BIZYDRAFT_MAX_FILE_SIZE:
                        await proxy_response.write(b"")
                        return web.Response(
                            status=413,
                            text=f"File size exceeds limit during streaming ({human_readable_size(BIZYDRAFT_MAX_FILE_SIZE)})",
                        )
                    await proxy_response.write(chunk)

                return proxy_response

    except asyncio.TimeoutError:
        return web.Response(
            status=504,
            text=f"Request timed out (max {BIZYDRAFT_REQUEST_TIMEOUT//60} minutes)",
        )
    except Exception as e:
        return web.Response(
            status=502, text=f"Failed to fetch remote resource: {str(e)}"
        )


def human_readable_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


async def post_prompt(request):
    json_data = await request.json()
    logger.debug(f"Received POST request to /prompt with data")
    json_data = comfy_server.trigger_on_prompt(json_data)

    if "prompt" in json_data:
        prompt = json_data["prompt"]
        valid = execution.validate_prompt(prompt)
        if valid[0]:
            response = {
                "prompt_id": None,
                "number": None,
                "node_errors": valid[3],
            }
            return web.json_response(response)
        else:
            return web.json_response(
                {"error": valid[1], "node_errors": valid[3]}, status=400
            )
    else:
        error = {
            "type": "no_prompt",
            "message": "No prompt provided",
            "details": "No prompt provided",
            "extra_info": {},
        }
        return web.json_response({"error": error, "node_errors": {}}, status=400)


def hijack_routes():
    routes = comfy_server.routes
    for idx, route in enumerate(routes._items):
        if route.path == "/view" and route.method == "GET":
            old_handler = route.handler

            async def new_handler(request):
                return await view_image(request, old_handler)

            routes._items[idx] = web.get("/view", new_handler)
            routes._items[idx].kwargs.clear()
            logger.info("Hijacked /view route to handle image, video and 3D streaming")
            break
    for idx, route in enumerate(routes._items):
        if route.path == "/prompt" and route.method == "POST":
            routes._items[idx] = web.post("/prompt", post_prompt)
            logger.info(
                "Hijacked /prompt route to handle prompt validation but not execution"
            )
            break

    routes = comfy_server.routes
    white_list = [
        # 劫持改造过的
        "/prompt",
        "/view",
        # 原生的
        "/",
        "/ws",
        "/extensions",
        "/object_info",
        "/object_info/{node_class}",
    ]

    async def null_handler(request):
        return web.Response(
            status=403,
            text="Access Forbidden: You do not have permission to access this resource.",
        )

    for idx, route in enumerate(routes._items):
        if (route.path not in white_list) and ("/bizyair" not in route.path):
            if route.method == "GET":
                logger.info(f"hijiack to null: {route.path}, {route.method}")
                routes._items[idx] = web.get(route.path, null_handler)
                routes._items[idx].kwargs.clear()
            elif route.method == "POST":
                logger.info(f"hijiack to null: {route.path}, {route.method}")
                routes._items[idx] = web.post(route.path, null_handler)
                routes._items[idx].kwargs.clear()
            else:
                logger.warning(
                    f"neither GET or POST, passed: {route.path}, {route.method}"
                )
        else:
            logger.warning(f"passed directly: {route.path}, {route.method}")
