import os
import json
import ast
from Orange.widgets import gui, widget
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.widget import Input, Output
from Orange.data import Table, StringVariable

class OWSaveFilepathEntry(widget.OWWidget):
    name = "Save with Filepath Entry"
    description = "Save data to a .pkl file, based on the provided path"
    icon = "icons/owsavefilepathentry.svg"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owsavefilepathentry.svg"
    priority = 1220
    want_main_area = False
    resizing_enabled = False

    # Persistent settings for fileId and CSV delimiter
    filename: str = Setting("embeddings.pkl") # type: ignore

    class Inputs:
        data = Input("Data", Table)
        save_path = Input("Path", str)
        path_table = Input("Path Table", Table)

    class Outputs:
        data = Output("Data", Table)

    @Inputs.data
    def dataset(self, data): 
        """Handle new data input."""
        self.data = data
        if self.data is not None:
            self.run()

    @Inputs.save_path
    def set_save_path(self, in_save_path):
        if in_save_path is not None:
            self.save_path = in_save_path.replace('"', '')
            self.run()

    @Inputs.path_table
    def set_path_table(self, in_path_table):
        if in_path_table is not None:
            if "path" in in_path_table.domain:
                self.save_path = in_path_table[0]["path"].value.replace('"', '')
                self.run()

            #pour enregistrement en json
            if "folder_path" in in_path_table.domain:
                self.save_path = in_path_table[0]["folder_path"].value.replace('"', '')
                self.json = True
                self.run()


    def __init__(self):
        super().__init__()
        self.info_label = gui.label(self.controlArea, self, "Initial info.")

        # Data Management
        self.save_path = None
        self.data = None
        self.json = False
        self.setup_ui()


    def setup_ui(self):
        """Set up the user interface."""
        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)

    def save_file(self):
        self.error("")
        self.warning("")
        if os.path.isdir(self.save_path):
            self.save_path = os.path.join(self.save_path, self.filename)

        import Orange.widgets.data.owsave as save_py
        saver = save_py.OWSave()
        filters = saver.valid_filters()
        extension = os.path.splitext(self.save_path)[1]
        selected_filter = ""
        for key in filters:
            if f"(*{extension})" in key:
                selected_filter = key
        if selected_filter == "":
            self.error(f"Invalid extension for savepath : {self.save_path}")
            return

        saver.data = self.data
        saver.filename = self.save_path
        saver.filter = selected_filter
        saver.do_save()

        self.data = None
        self.save_path = None

    def save_json(self):
        if "answer" not in self.data.domain:
            self.error("No answer column found.")
            return
        if "folder_path" not in self.data.domain:
            self.error("No folder_path column found.")
            return
        text_response = self.data.get_column("answer")[0]
        folder_path = self.data.get_column("folder_path")[0]
        try:
            data_raw = json.loads(text_response)
        except json.JSONDecodeError as e:
            print("JSON mal formé :", e)
            try:
                data_raw = ast.literal_eval(text_response)
            except Exception as e2:
                print("Faux JSON invalide aussi :", e2)
                self.error("Faux JSON invalide aussi :", e2)

        json_path = folder_path + "/rapport.json"
        # Étape 3 : enregistrer dans un fichier JSON propre
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data_raw, f, ensure_ascii=False, indent=4)
        self.information("JSON saved successfully")
        new_name_column = StringVariable("json_path")
        out_data = self.data.add_column(new_name_column, [json_path])
        self.json = False
        self.save_path = None
        self.Outputs.data.send(out_data)

    def run(self):
        self.error("")
        self.information("")
        """Save data to a file."""
        if self.data is None:
            return

        if self.save_path is None:
            return

        if self.json:
            self.save_json()
        else:
            self.save_file()




if __name__ == "__main__": 
    WidgetPreview(OWSaveFilepathEntry).run()
