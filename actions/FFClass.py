# Import StreamController modules
from src.backend.PluginManager.ActionBase import ActionBase
from src.backend.DeckManagement.DeckController import DeckController
from src.backend.PageManagement.Page import Page
from src.backend.PluginManager.PluginBase import PluginBase

# Import gtk
import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw

class FFClass(ActionBase):
    ff_classes_dict = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugin_base.connect_to_event(event_id="com_swordmaiden_xivdeck::WebsocketEvent",
                                          callback=self.websocket_event)

    def on_key_down(self):
        settings = self.get_settings()
        class_id = settings["class_id"]
        if class_id is not None:
            try:
                self.plugin_base.backend.send_xivdeck("/classes/{}/execute".format(class_id))
                self.set_center_label(None)
            except Exception as e:
                self.set_center_label('Offline')


    def on_ready(self):
        self.update_button()

    def get_config_rows(self) -> list:
        available_classes = Gtk.StringList()
        available_classes.append("None")

        settings = self.get_settings()
        current_class = settings.get('class_id')

        i = 1
        stored_class_row = 0
        for class_dict in self.plugin_base.backend.get_classes():
            class_name = class_dict['name']
            class_id = class_dict['id']
            available_classes.append(class_name)
            if class_id == current_class:
                stored_class_row = i
            i += 1
        self.ff_class = Adw.ComboRow(title='Select Class', model=available_classes)

        self.ff_class.connect("notify::selected", self.on_ff_class_value_changed)

        self.ff_class.set_selected(stored_class_row)

        return [self.ff_class]

    async def websocket_event(self, event, message):
        if message is not None:
            if message == "disconnect":
                self.set_center_label('Offline')
            elif message == "connect":
                self.set_center_label(None)
                self.update_button()

    def update_button(self):
        image = None

        settings = self.get_settings()
        class_id = settings.get("class_id")
        class_name = None
        class_abbr = None

        if class_id is not None:
            class_name = settings["class_name"]
            class_abbr = settings['class_abbr']
            image = self.plugin_base.backend.get_icon(settings["class_icon_id"])

        self.set_media(media_path=image)
        self.set_top_label(class_abbr)
        self.set_bottom_label(class_name)

    def on_ff_class_value_changed(self, ff_class, status):
        class_name = ff_class.get_selected_item().get_string()
        if class_name != "None":
            class_dict = self.plugin_base.backend.get_classes(class_name)
            class_id = class_dict['id']
            class_icon_id = class_dict['iconId']
            class_abbr = class_dict['abbreviation']
        else:
            class_abbr = None
            class_icon_id = None
            class_id = None
        settings = self.get_settings()
        settings["class_name"] = class_name
        settings["class_id"] = class_id
        settings["class_icon_id"] = class_icon_id
        settings["class_abbr"] = class_abbr
        self.set_settings(settings)
        self.update_button()
