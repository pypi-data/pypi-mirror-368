

import threading
from .ui import  RotatingImageApp
app = None
gui_ready = threading.Event()
overlays = {}
rotating_images = {}
static_images = {}

def setup_gui_app():
    global app
    app = RotatingImageApp(background_path="static/back.png")
    # 安全启动层级维护
    app.root.after(500, app._safe_maintain_top_layers)

    return app

def run_gui():
    global app
    app = setup_gui_app()
    gui_ready.set()
    app.run()


def open_air_conditioning(app,room_name: str, temp: int):
    if room_name in rotating_images:
        app.remove_rotating_image(rotating_images[room_name])
    if room_name in static_images:
        app.remove_static_image(static_images[room_name])
    if room_name == "客厅":
        rotating_images[room_name] = app.add_rotating_image(f"static/fan.png", x=750, y=750, speed=temp)
        rotating_images[room_name].start()
    elif room_name == "主卧":
        rotating_images[room_name] = app.add_rotating_image(f"static/fan.png", x=1100, y=900, speed=temp)
        rotating_images[room_name].start()
    elif room_name == "次卧":
        rotating_images[room_name] = app.add_rotating_image(f"static/fan.png", x=1100, y=350, speed=temp)
        rotating_images[room_name].start()
    elif room_name == "儿童房":
        rotating_images[room_name] = app.add_rotating_image(f"static/fan.png", x=1210, y=600, speed=temp)
        rotating_images[room_name].start()



def close_air_conditioning(app,room_name: str):
    if room_name in rotating_images:
        app.remove_rotating_image(rotating_images[room_name])
    if room_name == "客厅":
        static_images[room_name] = app.add_static_image("static/fan_off.png", x=750, y=750)
    elif room_name == "主卧":
        static_images[room_name] = app.add_static_image("static/fan_off.png", x=1100, y=900)
    elif room_name == "次卧":
        static_images[room_name] = app.add_static_image("static/fan_off.png", x=1100, y=350)
    elif room_name == "儿童房":
        static_images[room_name] = app.add_static_image("static/fan_off.png", x=1210, y=600)


import asyncio
from typing import Any
import threading
import mcp.server.stdio
import mcp.types as types
from mcp.server.lowlevel import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("IOT_MCP")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools with structured output schemas."""
    return [
        types.Tool(
            name="open_lamp",
            description="打开灯光，比如用户说：打开阳台灯光",
            inputSchema={
                "type": "object",
                "properties": {
                    "room":
                   {
                        "type": "string",
                        "description": "房间名称，例如：“客厅”、“次卧”"
                   }
                },
                "required": ["room"],
            }
        ),
        types.Tool(
            name="close_lamp",
            description="关闭灯光，比如用户说：关闭阳台灯光",
            inputSchema={
                "type": "object",
                "properties":
                    {
                        "room":
                            {
                                "type": "string",
                                "description": "房间名称，例如：“客厅”、”阳台“"
                            }
                    },
                "required": ["room"],
            }
        ),
        types.Tool(
            name="control_mode",
            description="模式控制，比如用户说：回家模式",
            inputSchema={
                "type": "object",
                "properties":
                    {
                        "mode_name":
                            {
                                "type": "string",
                                "description": "模式名称，例如：“回家模式”、”离家模式“"
                            }
                    },
                "required": ["mode_name"],
            }
        ),
        types.Tool(
            name="open_air_conditioning",
            description="打开，比如用户说：打开客厅的空调",
            inputSchema={
                "type": "object",
                "properties":
                    {
                        "room":
                            {
                                "type": "string",
                                "description": "房间名称，例如：“客厅”、”阳台“"
                            }
                    },
                "required": ["room"],
            }
        ),
        types.Tool(
            name="close_air_conditioning",
            description="关闭空调，比如用户说：关闭客厅的空调",
            inputSchema={
                "type": "object",
                "properties":
                    {
                        "room":
                            {
                                "type": "string",
                                "description": "房间名称，例如：“客厅”、”阳台“"
                            }
                    },
                "required": ["room"],
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) ->  list[types.TextContent]:
    if name == "close_lamp":
        room = arguments["room"]
        if room in overlays:
            app.remove_overlay_image(overlays[room])
        return [types.TextContent(type="text", text=f"{room}灯光已关闭了")]
    elif name == "open_lamp":
        room = arguments["room"]
        overlays[room] = app.add_overlay_image(f"static/{room}.png")
        return [types.TextContent(type="text", text=f"{room}灯光已打开了")]
    elif name == "control_mode":
        mode_name=arguments["mode_name"]
        if mode_name == "回家模式":
            app.clear_all()
            overlays["客厅"] = app.add_overlay_image(f"static/客厅.png")
            overlays["次卧"] =app.add_overlay_image(f"static/次卧.png")
            overlays["主卧"] =app.add_overlay_image(f"static/主卧.png")
            overlays["儿童房"] =app.add_overlay_image(f"static/儿童房.png")
            open_air_conditioning(app, "客厅", 5)
            open_air_conditioning(app, "主卧", 5)
            open_air_conditioning(app, "次卧", 5)
            open_air_conditioning(app, "儿童房", 5)
        elif mode_name == "离家模式":
            app.clear_all()
            close_air_conditioning(app, "客厅")
            close_air_conditioning(app, "主卧")
            close_air_conditioning(app, "次卧")
            close_air_conditioning(app, "儿童房")
        return [types.TextContent(type="text", text=f"已设置为{mode_name}")]
    elif name == "open_air_conditioning":
        room = arguments["room"]
        open_air_conditioning(app, room, 10)
        return [types.TextContent(type="text", text=f"{room}空调已打开")]
    elif name == "close_air_conditioning":
        room = arguments["room"]
        close_air_conditioning(app,room)
        return [types.TextContent(type="text", text=f"{room}空调已关闭")]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def run():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="IOT_MCP",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )




def main() -> None:
    gui_thread = threading.Thread(target=run_gui, daemon=True)
    gui_thread.start()
    gui_ready.wait()
    app.add_static_image("static/logo.png", x=1000, y=430, size=(120,55))
    close_air_conditioning(app, "客厅")
    close_air_conditioning(app, "主卧")
    close_air_conditioning(app, "次卧")
    close_air_conditioning(app, "儿童房")

    asyncio.run(run())
