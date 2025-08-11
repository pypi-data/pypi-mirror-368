import flet as ft

import flet_easy as fs


class ConfigApp:
    def __init__(self, app: fs.FletEasy):
        self.app = app
        self.start()

    def start(self):
        @self.app.login
        async def login_required(data: ft.Page):
            # Using Jwt to authenticate user, which has been previously configured with the `data.login()` method.
            return await fs.decode_async(key_login="login", data=data)

        @self.app.view
        async def view_config(data: fs.Datasy):
            return fs.Viewsy(
                appbar=ft.AppBar(title=ft.Text("Flet-Easy")),
                
            )

        @self.app.config
        def page_config(page: ft.Page):
            theme = ft.Theme()
            platforms = ["android", "ios", "macos", "linux", "windows"]
            for platform in platforms:  # Removing animation on route change.
                setattr(theme.page_transitions, platform, ft.PageTransitionTheme.NONE)
            page.theme = theme

        @self.app.config_event_handler
        async def event_handler(data: fs.Datasy):
            page = data.page

            async def on_disconnect(e):
                print("Disconnect test application")

            page.on_disconnect = on_disconnect
