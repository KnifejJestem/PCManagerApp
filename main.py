import flet as ft
import websockets
import asyncio
import json

async def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.title = "PC Manager Client"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    cpu_text = "Loading..."
    gpu_text = "Loading..."
    ram_text = "Loading..."
    disk_text = "Loading..."

    def create_stat_card(title, value, icon, color):
        return ft.Container(
            content=ft.Column( [
                ft.Icon(icon, size=30, color=color),
                ft.Text(title, size=16),
                ft.Text(value, size=20, weight="bold"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.GREY,
            border_radius=25,
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
            col={"xs": 6, "sm": 6, "md": 4},
            width=200,
            height=200,
        )

    stat_grid = ft.ResponsiveRow(
        controls=[
            create_stat_card("CPU", cpu_text, ft.Icons.MEMORY, ft.Colors.BLUE),
            create_stat_card("GPU", gpu_text, ft.Icons.SIXTY_FPS_SELECT, ft.Colors.GREEN),
            create_stat_card("RAM", ram_text, ft.Icons.MEMORY, ft.Colors.ORANGE),
            create_stat_card("Disks", disk_text, ft.Icons.FOLDER, ft.Colors.PURPLE),
        ],
        spacing=20,
        run_spacing=20,
    )

    page.add(
        ft.Column( scroll=ft.ScrollMode.AUTO, alignment=ft.MainAxisAlignment.CENTER,
            controls=[ 
            stat_grid,
            ip := ft.TextField(label="Server IP", width=300, on_submit=lambda e: setattr(ip, 'value', e.control.value))
            ]
        )
    )


    while True:
        if ip:
            uri = f"ws://{ip.value}:8765"
            try:
                async with websockets.connect(uri, ping_interval=None) as websocket:
                    print(f"Connected to server at {uri}")
                    while True:
                        response = await websocket.recv()
                        stats = json.loads(response)
                        cpu_text = f"CPU: {stats['cpu']['name']} - Usage: {stats['cpu']['usage']}% \n Temperature: {stats['cpu']['temperature']}°C \n Clock Speed: {stats['cpu']['clock_speed']} Mhz \n Voltage: {stats['cpu']['voltage']} V"
                        gpu_text = f"GPU: {stats['gpu']['name']} - Usage: {stats['gpu']['usage']}%"
                        ram_text = f"RAM Used: {stats['ram']['used']} / {stats['ram']['total']} GB"
                        disk_text = "\n".join([
                            f"Disk {disk['device']} - Used: {disk['used']} / {disk['total']} GB ({disk['percent']}%)"
                            for disk in stats["disks"]
                        ])
                        stat_grid.controls[0].content.controls[2].value = cpu_text
                        stat_grid.controls[1].content.controls[2].value = gpu_text
                        stat_grid.controls[2].content.controls[2].value = ram_text
                        stat_grid.controls[3].content.controls[2].value = disk_text
                        page.update()
                        await asyncio.sleep(1)
            except Exception as e:
                print(f"Error connecting to server: {e} using {uri} - Retrying in 3 seconds...")
                await asyncio.sleep(3)

ft.app(main)