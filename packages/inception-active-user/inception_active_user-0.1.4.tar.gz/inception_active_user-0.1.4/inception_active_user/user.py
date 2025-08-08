import aiohttp
from fastapi import Request
from fastapi.responses import JSONResponse
from inception_active_user.settings_usr import get_active_user_setting

# Get settings
user_setting = get_active_user_setting()


async def fetch_user_info(authorization_data: str, url: str):
    """
    Helper function to fetch current active user info from the API.
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers={
                    "Authorization": authorization_data,
                    "Content-Type": "application/json",
                },
            ) as response:
                if response.ok:
                    return await response.json()
                else:
                    error_detail = await response.json()
                    raise Exception(
                        f"Request failed with status {response.status}: {error_detail}"
                    )
    except Exception as e:
        print(f"[ERROR] Failed to fetch user info: {e}")
        return JSONResponse(
            status_code=401,
            content={"message": str(e)},
        )


async def get_current_active_user(request: Request):
    return await fetch_user_info(
        request.headers.get("Authorization"),
        f"{user_setting.url}/api/v1/users/me/minify",
    )


async def get_current_active_user_more_info(request: Request):
    return await fetch_user_info(
        request.headers.get("Authorization"), f"{user_setting.url}/api/v1/users/me"
    )
