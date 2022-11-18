import flet
from flet import (
    Page,
    AppBar,
    Text,
    View,
    UserControl,
    Row,
    FloatingActionButton,
    icons,
    AlertDialog,
    ElevatedButton,
    TextField,
    Column,
    ListView,
    Divider,
    IconButton,
    Ref,
)
from db import add_record, remove_record, get_records
from listener import start_listener, mp_event


class HotkeyList(UserControl):
    def __init__(self):
        super().__init__()

        self.main_list = ListView(
            expand=1,
            spacing=10,
            padding=10,
            divider_thickness=0.5,
        )

    def build(self):
        current_items = get_records()
        for id, values in current_items.items():
            self.main_list.controls.append(
                HotkeyItem(
                    id=id,
                    hotkey=values["hotkey"],
                    replacement=values["replacement"],
                )
            )
        return self.main_list

    def fetch_tasks(self):
        self.main_list.controls.clear()
        current_items = get_records()
        for id, values in current_items.items():
            self.main_list.controls.append(
                HotkeyItem(
                    id=id,
                    hotkey=values["hotkey"],
                    replacement=values["replacement"],
                )
            )
        self.update()


list_view = HotkeyList()


class HotkeyItem(UserControl):
    def __init__(self, id, hotkey, replacement):
        super().__init__()
        self.id = id
        self.hotkey = hotkey
        self.replacement = replacement

    def build(self):
        o = Row(
            [
                Text(self.id, expand=1),
                Text(self.hotkey, expand=3),
                Text(self.replacement, expand=4),
                IconButton(
                    icon=icons.DELETE_FOREVER_ROUNDED,
                    icon_color="red400",
                    icon_size=20,
                    tooltip="Delete record",
                    on_click=self.delete_record,
                ),
            ]
        )
        return o

    def delete_record(self, e):
        remove_record(self.id)
        list_view.main_list.controls.remove(self)
        list_view.update()


def main(page: Page):
    page.window_height = 550
    page.window_width = 750
    main_appbar = AppBar(
        title=Text("Text Expander"),
        center_title=True,
    )
    page.title = "Text Expander"
    status_text = Text(value="Stopped", color="red200")
    page.update()

    def start_expanding(e):
        mp_event.clear()
        status_text.value = "Running..."
        status_text.color = "green200"
        page.update()
        list_view.update()
        d = get_records()
        start_listener(d)

    def stop_expanding(e):
        mp_event.set()
        status_text.value = "Stopped"
        status_text.color = "red200"
        list_view.update()
        page.update()

    def close_modal(e):
        item_modal.open = False
        page.update()

    def add_new_shortcut(hotkey, replacement):
        add_record(hotkey, replacement)
        item_modal.open = False
        item_modal.clean()
        page.update()
        list_view.fetch_tasks()

    modal_shortcut = TextField(label="Text Shortcut", expand=1)
    modal_replace = TextField(
        label="Replace With", expand=1, multiline=True, min_lines=5, max_lines=10
    )
    item_modal = AlertDialog(
        modal=True,
        title=Text("Add a new shortcut"),
        content=Column(
            [Row([modal_shortcut]), Row([modal_replace])],
            tight=True,
            alignment="center",
            horizontal_alignment="center",
            height=(int(page.height * 0.5)),
            width=(int(page.width * 0.75)),
            spacing=10,
        ),
        actions=[
            ElevatedButton(
                "Add",
                on_click=lambda _: add_new_shortcut(
                    hotkey=modal_shortcut.value, replacement=modal_replace.value
                ),
            ),
            ElevatedButton("Cancel", on_click=close_modal),
        ],
        actions_alignment="center",
    )

    def new_item_modal(e):
        page.dialog = item_modal
        item_modal.open = True
        page.update()

    def route_change(route):
        page.views.clear()
        page.views.append(
            View(
                route="/",
                controls=[
                    Row(
                        [
                            ElevatedButton(
                                text="Start",
                                width=(page.width * 0.1),
                                on_click=start_expanding,
                            ),
                            ElevatedButton(
                                text="Stop",
                                width=(page.width * 0.1),
                                on_click=stop_expanding,
                            ),
                        ],
                        alignment="center",
                    ),
                    Row([status_text], alignment="center"),
                    Divider(),
                    list_view,
                ],
                appbar=main_appbar,
                floating_action_button=FloatingActionButton(
                    text="Add Shortcut", icon=icons.ADD, on_click=new_item_modal
                ),
                scroll="auto",
            )
        )

        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)


if __name__ == "__main__":
    flet.app(target=main)
