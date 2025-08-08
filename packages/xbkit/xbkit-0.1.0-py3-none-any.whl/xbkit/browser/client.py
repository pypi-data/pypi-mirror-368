from typing import Awaitable, Callable
from pathlib import Path

import asyncio

from playwright_stealth import Stealth
from playwright.async_api import async_playwright, Response


DEFAULT_STORAGE_STATE_PATH = Path("config/stroage_state.json")


# 浏览器客户端
class BrowserClient:

    def __init__(
        self,
        storage_state: str | Path = DEFAULT_STORAGE_STATE_PATH,
        use_stealth: bool = True,
        headless: bool = False,
    ):
        if isinstance(storage_state, str):
            storage_state = Path(storage_state)
        # 保存参数
        self.storage_state = storage_state
        self.use_stealth = use_stealth
        self.headless = headless
        # 初始化响应路由表
        self.resp_routes: dict[str, Callable[[Response], Awaitable[None]]] = {}

        if self.use_stealth:
            self.ctx_ = Stealth().use_async(async_playwright())
        else:
            self.ctx_ = async_playwright()

    async def __aenter__(self):
        loop = asyncio.get_event_loop()
        self.playwright = await self.ctx_.__aenter__()
        # 启动浏览器
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        # 浏览器创建一个上下文,加载storage_state
        self.context = await self.browser.new_context(
            storage_state=self.storage_state if self.storage_state.exists() else None
        )
        # 新建一个标签页
        self.page = await self.context.new_page()
        # 设置回调函数on_response监听网络响应
        self.page.on("response", self.__on_response)
        return self

    async def __aexit__(self, *args):
        loop = asyncio.get_event_loop()
        self.storage_state.parent.mkdir(parents=True, exist_ok=True)
        await self.context.storage_state(path=self.storage_state, indexed_db=True)
        await self.browser.close()
        await self.ctx_.__aexit__(*args)

    # 监听网络响应
    async def __on_response(self, resp: Response):
        # 遍历路由表，执行对应回调函数
        for route, handler in self.resp_routes.items():
            if route in resp.url:
                await handler(resp)
                break

    # 注册网络响应回调
    def reg_response_cb(self, url: str, cb: Callable[[Response], Awaitable[None]]):
        self.resp_routes[url] = cb
