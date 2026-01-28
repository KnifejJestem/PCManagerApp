import flet as ft
import websockets
import asyncio
import json

stat_box_width = 620

async def main(page: ft.Page):
    ft.Theme.use_material3 = True
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.title = "PC Manager Client"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    cpu_text = "Loading..."
    gpu_text = "Loading..."
    ram_text = "Loading..."
    disk_text = "Loading..."

    def create_stat_card(title, value, icon, color, width):
        return ft.Container(
            content=ft.Column( [
                ft.Icon(icon, size=30, color=color),
                ft.Text(title, size=16),
                ft.Text(value, size=20, weight="bold"),
            ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.WHITE10,
            border_radius=25,
            padding=ft.padding.all(20),
            alignment=ft.alignment.center,
            width=width,
            height=200,
        )

    stat_grid = ft.Row(
        controls=[
            create_stat_card("CPU", cpu_text, ft.Icons.MEMORY, ft.Colors.BLUE, stat_box_width),
            create_stat_card("GPU", gpu_text, ft.Icons.SIXTY_FPS_SELECT, ft.Colors.GREEN, stat_box_width),
            create_stat_card("RAM", ram_text, ft.Icons.MEMORY, ft.Colors.ORANGE, stat_box_width),
            create_stat_card("Disks", disk_text, ft.Icons.FOLDER, ft.Colors.PURPLE, stat_box_width),
        ],
        wrap=True,
        spacing=20,
        run_spacing=20,
        alignment=ft.MainAxisAlignment.CENTER,
    )

    dashboard_view = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            stat_grid,
        ],
    visible=False,)

    connection_view = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Enter Server IP to Connect", size=20),
            ip := ft.TextField(label="Server IP", width=300, on_submit=lambda e: setattr(ip, 'value', e.control.value)),
        ],
    visible=True,)

    benchmark_view = ft.Column(
        scroll=ft.ScrollMode.AUTO,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Text("Benchmark View Coming Soon!", size=20),
        ],
    visible=False,)

    views = [dashboard_view, connection_view, benchmark_view]

    on_nav_change = lambda e: [
        setattr(connection_view, 'visible', e.control.selected_index == 0),
        setattr(dashboard_view, 'visible', e.control.selected_index == 1),
        setattr(benchmark_view, 'visible', e.control.selected_index == 2),
        page.update(),
    ]

    page.navigation_bar = ft.NavigationBar(
        destinations=[  
            ft.NavigationBarDestination(icon=ft.Icons.WIFI, label="Connect"),     
            ft.NavigationBarDestination(icon=ft.Icons.DASHBOARD, label="Dashboard"),      
            ft.NavigationBarDestination(icon=ft.Icons.INSERT_CHART, label="Benchmark"), 
        ],
        on_change=on_nav_change
    )

    page.add(
        ft.Container(
            content=ft.Column(views, scroll=ft.ScrollMode.AUTO, expand=True),
            padding=20,
            expand=True,
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
                        cpu_text = f"{stats['cpu']['name']} \n Usage | {stats['cpu']['usage']}% \n Temperature | {stats['cpu']['temperature']}°C \n Clock Speed | {stats['cpu']['clock_speed']} Mhz \n Voltage | {stats['cpu']['voltage']}V"
                        gpu_text = f"{stats['gpu']['name']} \n Usage | {stats['gpu']['usage']}%"
                        ram_text = f"RAM Usage | {stats['ram']['used']} / {stats['ram']['total']} GB"
                        disk_text = "\n".join([
                            f"Disk {disk['device']} - Used | {disk['used']} / {disk['total']} GB"
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