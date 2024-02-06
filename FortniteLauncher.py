import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json

class ConfigEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("FortAlpha Launcher")
        self.master.geometry("400x150")  
        self.master.eval('tk::PlaceWindow . center')

        self.ini_path = tk.StringVar()
        self.game_exe_path = tk.StringVar()
        self.map_folder_path = tk.StringVar()
        self.selected_map = tk.StringVar()

        self.ini_selected = False
        self.game_exe_selected = False
        self.map_folder_selected = False

        self.map_list = []

        if not os.path.exists('.config'): 
            self.select_ini_file()
            self.select_game_exe()
            self.select_map_folder()

        self.load_config()
        self.create_widgets()

    def create_widgets(self):
        map_label = ttk.Label(self.master, text="Select the map:")
        map_label.grid(row=2, column=0, pady=10, padx=10, sticky="w")

        map_menu = ttk.Combobox(self.master, textvariable=self.selected_map, values=[map['name'] for map in self.map_list], width=30)
        map_menu.grid(row=2, column=1, pady=10, padx=10, sticky="w")

        apply_button = ttk.Button(self.master, text="Apply Changes", command=self.apply_changes)
        apply_button.grid(row=3, column=0, columnspan=2, pady=10, padx=10)

        launch_button = ttk.Button(self.master, text="Launch Game", command=self.launch_game)
        launch_button.grid(row=4, column=0, columnspan=2, pady=10, padx=10)

    def select_ini_file(self):
        ini_path = filedialog.askopenfilename(title="Select DefaultEngine.ini", filetypes=[("INI files", "*.ini")])
        if ini_path:
            self.ini_path.set(ini_path)
            self.ini_selected = True
            self.save_config()

    def select_game_exe(self):
        game_exe_path = filedialog.askopenfilename(title="Select game executable", filetypes=[("Executable files", "*.exe")])
        if game_exe_path:
            self.game_exe_path.set(game_exe_path)
            self.game_exe_selected = True
            self.save_config()

    def select_map_folder(self):
        map_folder_path = filedialog.askdirectory(title="Select 'Content'folder")
        if map_folder_path:
            self.map_folder_path.set(map_folder_path)
            self.map_folder_selected = True
            self.save_config()
            self.update_map_list()

    def apply_changes(self):
        if not self.ini_selected or not os.path.exists(self.ini_path.get()):
            messagebox.showerror("Error", "Select the DefaultEngine.ini file first.")
            return

        selected_map = self.selected_map.get()
        full_map_path = next((map['full_path'] for map in self.map_list if map['name'] == selected_map), "")

        if not full_map_path:
            messagebox.showerror("Error", f"Could not find the full path for the map {selected_map}.")
            return

        with open(self.ini_path.get(), "r") as file:
            lines = file.readlines()

        for i, line in enumerate(lines):
            if "GameDefaultMap=" in line:
                lines[i] = f"GameDefaultMap={full_map_path}\n"

        with open(self.ini_path.get(), "w") as file:
            file.writelines(lines)

        messagebox.showinfo("Information", "Changes applied successfully.")

    def update_map_list(self):
        if os.path.exists(self.map_folder_path.get()):
            self.map_list = []
            for root, dirs, files in os.walk(self.map_folder_path.get()):
                for file in files:
                    if file.endswith(".umap"):
                        relative_path = os.path.relpath(os.path.join(root, file), self.map_folder_path.get())
                        map_name = os.path.splitext(file)[0]
                        self.map_list.append({
                            'full_path': f"/Game/{relative_path.replace(os.path.sep, '/').replace('.umap', '')}",
                            'name': map_name
                        })

            self.selected_map.set(self.map_list[0]['name'] if self.map_list else "")
        else:
            self.map_list = []
            self.selected_map.set("")

    def launch_game(self):
        if not self.game_exe_selected or not os.path.exists(self.game_exe_path.get()):
            messagebox.showerror("Error", "Select the game FortniteClient-Win32-Shipping first.")
            return

        launch_command = f'start "" "{self.game_exe_path.get()}" -log -AUTH_LOGIN=unknown -AUTH_PASSWORD=5001 -AUTH_TYPE=exchangecode'
        os.system(launch_command)

    def save_config(self):
        config_data = {
            'ini_path': self.ini_path.get(),
            'game_exe_path': self.game_exe_path.get(),
            'map_folder_path': self.map_folder_path.get()
        }

        with open('.config', 'w') as config_file:
            json.dump(config_data, config_file)

    def load_config(self):
        if os.path.exists('.config'):
            with open('.config', 'r') as config_file:
                config_data = json.load(config_file)

            if 'ini_path' in config_data and 'game_exe_path' in config_data and 'map_folder_path' in config_data:
                self.ini_path.set(config_data['ini_path'])
                self.ini_selected = True

                self.game_exe_path.set(config_data['game_exe_path'])
                self.game_exe_selected = True

                self.map_folder_path.set(config_data['map_folder_path'])
                self.map_folder_selected = True

                self.update_map_list()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConfigEditor(root)
    root.mainloop()
