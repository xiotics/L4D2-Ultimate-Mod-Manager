import os
import sys
import tkinter as tk
import shutil
import re
import requests
import concurrent.futures
from tkinter import messagebox, filedialog, simpledialog
from html.parser import HTMLParser
from PIL import Image, ImageTk
import threading

# Path to the game folder and gameinfo.txt
GAME_FOLDER = os.getcwd()
LEFT4DEAD2_EXE = os.path.join(GAME_FOLDER, 'left4dead2.exe')
USERMODS_PATH = os.path.join(GAME_FOLDER, 'usermods')
WORKSHOP_PATH = os.path.join(GAME_FOLDER, 'left4dead2', 'addons', 'workshop')
GAMEINFO_PATH = os.path.join(GAME_FOLDER, 'left4dead2', 'gameinfo.txt')

# Function to check game folder and create usermods folder if necessary
def check_setup():
    if not os.path.isfile(LEFT4DEAD2_EXE):
        messagebox.showerror("Setup Error", "left4dead2.exe not found, please move the Tool to the same directory.")
        sys.exit()

    if not os.path.exists(USERMODS_PATH):
        os.makedirs(USERMODS_PATH)

    if not os.path.exists(WORKSHOP_PATH):
        os.makedirs(WORKSHOP_PATH)  # Ensure workshop folder exists

check_setup()

def scan_for_mods():
    usermods_path = os.path.join(GAME_FOLDER, 'usermods')

    if not os.path.exists(usermods_path):
        messagebox.showerror("Error", f"usermods folder not found in {GAME_FOLDER}")
        return [], []

    enabled_mods = []
    disabled_mods = []

    all_mods = [
        folder_name for folder_name in os.listdir(usermods_path)
        if os.path.isdir(os.path.join(usermods_path, folder_name))
    ]

    if os.path.exists(GAMEINFO_PATH):
        with open(GAMEINFO_PATH, 'r') as file:
            gameinfo_content = file.readlines()

        enabled_mod_names = set()

        for line in gameinfo_content:
            line_stripped = line.strip()

            if line_stripped.startswith("Game") and "usermods\\" in line_stripped:
                enabled_mod_name = line_stripped.split("usermods\\")[-1]
                enabled_mod_names.add(enabled_mod_name)

        for mod in all_mods:
            mod_path = os.path.join(usermods_path, mod)
            if mod not in enabled_mod_names:
                if os.path.exists(os.path.join(mod_path, 'pak01_dir.vpk')):
                    disabled_mods.append(mod)

    else:
        disabled_mods = [
            mod for mod in all_mods 
            if os.path.exists(os.path.join(usermods_path, mod, 'pak01_dir.vpk'))
        ]

    return enabled_mods, disabled_mods

def update_mod_lists():
    enabled_mods, disabled_mods = scan_for_mods()
    enabled_listbox.delete(0, tk.END)
    disabled_listbox.delete(0, tk.END)

    for mod in enabled_mods:
        enabled_listbox.insert(tk.END, mod)

    for mod in disabled_mods:
        disabled_listbox.insert(tk.END, mod)

def disable_mods():
    selected_mods = enabled_listbox.curselection()
    if selected_mods:
        for index in selected_mods[::-1]:
            mod = enabled_listbox.get(index)
            enabled_listbox.delete(index)
            disabled_listbox.insert(tk.END, mod)

def enable_mods():
    selected_mods = disabled_listbox.curselection()
    if selected_mods:
        for index in selected_mods[::-1]:
            mod = disabled_listbox.get(index)
            disabled_listbox.delete(index)
            enabled_listbox.insert(tk.END, mod)

def apply_changes():
    usermods_path = os.path.join(GAME_FOLDER, 'usermods')

    if not os.path.exists(GAMEINFO_PATH):
        messagebox.showerror("Error", "gameinfo.txt not found in the left4dead2 folder.")
        return

    with open(GAMEINFO_PATH, 'r') as file:
        gameinfo_content = file.readlines()

    new_content = []
    
    for line in gameinfo_content:
        if not (line.strip().startswith("Game") and "usermods\\" in line):
            new_content.append(line)

    search_path_index = None
    for i, line in enumerate(new_content):
        if 'SearchPaths' in line:
            search_path_index = i + 2
            break

    if search_path_index is not None:
        enabled_mods = [enabled_listbox.get(i) for i in range(enabled_listbox.size())]
        temp_mod_entries = [f'\t\t\tGame\t\t\t\tusermods\\{mod}\n' for mod in enabled_mods]
        new_content[search_path_index:search_path_index] = temp_mod_entries

    with open(GAMEINFO_PATH, 'w') as file:
        file.writelines(new_content)

    messagebox.showinfo("Success", "Mod changes applied successfully!")
    update_mod_lists()

def refresh_mods():
    update_mod_lists()

def move_mod_up():
    selected_indices = enabled_listbox.curselection()
    if selected_indices:
        sorted_indices = sorted(selected_indices)
        if sorted_indices[0] == 0:
            return

        items_to_move = [enabled_listbox.get(index) for index in sorted_indices]
        
        for index in sorted_indices:
            if index > 0:
                mod = enabled_listbox.get(index)
                enabled_listbox.delete(index)
                enabled_listbox.insert(index - 1, mod)

        for mod in items_to_move:
            new_index = enabled_listbox.get(0, tk.END).index(mod)
            enabled_listbox.select_set(new_index)

def move_mod_down():
    selected_indices = enabled_listbox.curselection()
    if selected_indices:
        sorted_indices = sorted(selected_indices, reverse=True)
        if sorted_indices[0] == enabled_listbox.size() - 1:
            return

        items_to_move = [enabled_listbox.get(index) for index in sorted_indices]

        for index in sorted_indices:
            if index < enabled_listbox.size() - 1:
                mod = enabled_listbox.get(index)
                enabled_listbox.delete(index)
                enabled_listbox.insert(index + 1, mod)

        for mod in items_to_move:
            new_index = enabled_listbox.get(0, tk.END).index(mod)
            enabled_listbox.select_set(new_index)

def delete_selected_mods():
    selected_enabled_mods = enabled_listbox.curselection()
    selected_disabled_mods = disabled_listbox.curselection()

    mods_to_delete = []
    if selected_enabled_mods:
        mods_to_delete += [enabled_listbox.get(i) for i in selected_enabled_mods]
    if selected_disabled_mods:
        mods_to_delete += [disabled_listbox.get(i) for i in selected_disabled_mods]

    if not mods_to_delete:
        messagebox.showwarning("Selection Error", "No mods selected for deletion.")
        return

    for mod in mods_to_delete:
        mod_path = os.path.join(USERMODS_PATH, mod)
        if os.path.exists(mod_path):
            try:
                shutil.rmtree(mod_path)
            except OSError as e:
                messagebox.showerror("Error", f"Failed to delete mod folder: {mod}. Error: {e}")
                continue

    with open(GAMEINFO_PATH, 'r') as file:
        gameinfo_content = file.readlines()

    new_content = []
    for line in gameinfo_content:
        if not any(mod in line for mod in mods_to_delete if line.strip().startswith("Game") and "usermods\\" in line):
            new_content.append(line)

    with open(GAMEINFO_PATH, 'w') as file:
        file.writelines(new_content)

    update_mod_lists()
    messagebox.showinfo("Success", "Selected mods deleted successfully!")

mod_mapping = {}

def add_mod():
    vpk_file_path = filedialog.askopenfilename(title="Select a VPK file", filetypes=[("VPK Files", "*.vpk")])
    if not vpk_file_path:
        return

    while True:
        folder_name = simpledialog.askstring("Input", "Enter a name for the mod folder:")
        if folder_name is None:
            return
        
        if re.match(r'^[\w-]+$', folder_name) and all(char not in folder_name for char in 'äöü'):
            break
        else:
            messagebox.showerror("Input Error", "Name contains invalid characters or spaces.")

    destination_folder = os.path.join(USERMODS_PATH, folder_name)
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    new_vpk_file_path = os.path.join(destination_folder, 'pak01_dir.vpk')

    try:
        shutil.copy(vpk_file_path, new_vpk_file_path)
        messagebox.showinfo("Success", f"Mod added successfully in {destination_folder} as pak01_dir.vpk")
        update_mod_lists()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to add mod: {e}")

class ModNameParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title_div = False
        self.mod_name = ""

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for attr in attrs:
                if attr == ('class', 'workshopItemTitle'):
                    self.in_title_div = True

    def handle_endtag(self, tag):
        if tag == 'div' and self.in_title_div:
            self.in_title_div = False

    def handle_data(self, data):
        if self.in_title_div:
            self.mod_name = data.strip()

def fetch_workshop_mods():
    if not os.path.exists(WORKSHOP_PATH):
        messagebox.showerror("Error", "Workshop folder not found.")
        return

    def fetch_mod_info(vpk_file):
        workshop_id = os.path.splitext(vpk_file)[0]
        url = f"https://steamcommunity.com/sharedfiles/filedetails/?id={workshop_id}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                parser = ModNameParser()
                parser.feed(response.text)
                return parser.mod_name
            else:
                return None
        except Exception as e:
            print(f"Error fetching mod info for {vpk_file}: {e}")
            return None

    def fetch_mods():
        workshop_listbox.delete(0, tk.END)
        vpk_files = [f for f in os.listdir(WORKSHOP_PATH) if f.endswith('.vpk')]
        if not vpk_files:
            messagebox.showinfo("Info", "No mods found in the workshop folder.")
            return
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(fetch_mod_info, vpk_files))

        for vpk_file, mod_name in zip(vpk_files, results):
            if mod_name:
                mod_name_filtered = re.sub(r'[^a-zA-Z0-9-_]', '', mod_name.replace(' ', '_'))
                workshop_listbox.insert(tk.END, mod_name_filtered)
                mod_mapping[mod_name_filtered] = vpk_file
            else:
                messagebox.showwarning("Warning", f"Mod title not found for {vpk_file}.")

        messagebox.showinfo("Done", "Finished fetching workshop mods!")

    threading.Thread(target=fetch_mods).start()

def add_workshop_mod():
    selected_mods = workshop_listbox.curselection()
    added_count = 0

    for index in selected_mods:
        mod_name = workshop_listbox.get(index)
        vpk_file_name = mod_mapping.get(mod_name)

        if vpk_file_name:
            destination_folder = os.path.join(USERMODS_PATH, mod_name)
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)

            vpk_file_path = os.path.join(WORKSHOP_PATH, vpk_file_name)
            new_vpk_file_path = os.path.join(destination_folder, 'pak01_dir.vpk')

            try:
                shutil.copy(vpk_file_path, new_vpk_file_path)
                added_count += 1
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add workshop mod '{mod_name}': {e}")

    update_mod_lists()

def rename_mod():
    selected_enabled_mods = enabled_listbox.curselection()
    selected_disabled_mods = disabled_listbox.curselection()
    
    if len(selected_enabled_mods) + len(selected_disabled_mods) != 1:
        messagebox.showwarning("Selection Error", "Please select exactly one mod to rename.")
        return

    if selected_enabled_mods:
        current_listbox = enabled_listbox
    else:
        current_listbox = disabled_listbox

    current_mod_name = current_listbox.get(current_listbox.curselection())

    while True:
        new_mod_name = simpledialog.askstring("Rename Mod", "Enter a new name for the mod:")
        if new_mod_name is None:
            return
        
        if re.match(r'^[\w-]+$', new_mod_name) and all(char not in new_mod_name for char in 'äöü'):
            break
        else:
            messagebox.showerror("Input Error", "Name contains invalid characters or spaces.")

    old_mod_path = os.path.join(USERMODS_PATH, current_mod_name)
    new_mod_path = os.path.join(USERMODS_PATH, new_mod_name)

    try:
        os.rename(old_mod_path, new_mod_path)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to rename mod: {e}")
        return

    if current_mod_name in enabled_listbox.get(0, tk.END):
        with open(GAMEINFO_PATH, 'r') as file:
            gameinfo_content = file.readlines()

        new_content = []
        for line in gameinfo_content:
            if line.strip().startswith("Game") and f"usermods\\{current_mod_name}" in line:
                line = line.replace(current_mod_name, new_mod_name)
            new_content.append(line)

        with open(GAMEINFO_PATH, 'w') as file:
            file.writelines(new_content)

    messagebox.showinfo("Success", f"Mod renamed successfully to '{new_mod_name}'!")
    update_mod_lists()

def force_enable_selected_mod():
    selected_enabled = enabled_listbox.curselection()
    selected_disabled = disabled_listbox.curselection()

    if len(selected_enabled) + len(selected_disabled) != 1:
        messagebox.showwarning("Selection Error", "Please select exactly one mod.")
        return

    if selected_enabled:
        mod_name = enabled_listbox.get(selected_enabled[0])
    else:
        mod_name = disabled_listbox.get(selected_disabled[0])

    src_vpk = os.path.join(USERMODS_PATH, mod_name, "pak01_dir.vpk")

    if not os.path.exists(src_vpk):
        messagebox.showerror("Error", "pak01_dir.vpk not found in selected mod.")
        return

    while True:
        folder_name = simpledialog.askstring("Folder Name", f"Enter folder name for '{mod_name}':")
        if folder_name is None:
            return

        if folder_name.strip() and not any(c in folder_name for c in r'\/:*?"<>|'):
            break
        else:
            messagebox.showerror("Error", "Invalid folder name.")

    dst_folder = os.path.join(GAME_FOLDER, folder_name)
    os.makedirs(dst_folder, exist_ok=True)

    dst_vpk = os.path.join(dst_folder, "pak01_dir.vpk")

    try:
        shutil.copy(src_vpk, dst_vpk)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy VPK: {e}")
        return

    if not os.path.exists(GAMEINFO_PATH):
        messagebox.showerror("Error", "gameinfo.txt not found.")
        return

    with open(GAMEINFO_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    entry_line = f"\t\t\tGame\t\t\t\t{folder_name}\n"

    if entry_line in lines:
        messagebox.showinfo("Info", "Mod already force-enabled.")
        return

    insert_index = None
    for i, line in enumerate(lines):
        if "SearchPaths" in line:
            insert_index = i + 2
            break

    if insert_index is None:
        messagebox.showerror("Error", "SearchPaths not found.")
        return

    lines.insert(insert_index, entry_line)

    try:
        with open(GAMEINFO_PATH, "w", encoding="utf-8") as f:
            f.writelines(lines)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write gameinfo.txt: {e}")
        return

    messagebox.showinfo("Success", f"'{mod_name}' force-enabled as '{folder_name}'!")
    update_mod_lists()


dir_path = os.path.dirname(os.path.realpath(__file__))
icon_path = os.path.join(dir_path, 'icon.png')

root = tk.Tk()
root.title("L4D2 Mod Manager")

try:
    ico = Image.open(icon_path)
    photo = ImageTk.PhotoImage(ico)
    root.wm_iconphoto(False, photo)
except Exception:
    pass

root.geometry("730x350")
root.resizable(False, False)

tk.Label(root, text="v0.0.1").place(x=690, y=330)
tk.Label(root, text="Enabled Mods").place(x=20, y=10)
enabled_listbox = tk.Listbox(root, height=15, width=30, selectmode=tk.MULTIPLE, highlightthickness=0, bd=2, relief=tk.RIDGE)
enabled_listbox.place(x=20, y=40)
tk.Label(root, text="Disabled Mods").place(x=300, y=10)
disabled_listbox = tk.Listbox(root, height=15, width=30, selectmode=tk.MULTIPLE, highlightthickness=0, bd=2, relief=tk.RIDGE)
disabled_listbox.place(x=300, y=40)
tk.Label(root, text="Workshop Mods").place(x=520, y=10)
workshop_listbox = tk.Listbox(root, height=15, width=30, selectmode=tk.MULTIPLE, highlightthickness=0, bd=2, relief=tk.RIDGE)
workshop_listbox.place(x=520, y=40)

fetch_button = tk.Button(root, text="Fetch Mods", command=fetch_workshop_mods)
fetch_button.place(x=631, y=300)
add_workshop_button = tk.Button(root, text="←", command=add_workshop_mod)
add_workshop_button.place(x=492, y=140)
disable_button = tk.Button(root, text="→", command=disable_mods)
disable_button.place(x=240, y=100)
enable_button = tk.Button(root, text="←", command=enable_mods)
enable_button.place(x=240, y=180)
apply_button = tk.Button(root, text="Apply", command=apply_changes)
apply_button.place(x=221, y=300)
refresh_button = tk.Button(root, text="Refresh", command=refresh_mods)
refresh_button.place(x=20, y=300)
up_button = tk.Button(root, text="↑", command=move_mod_up)
up_button.place(x=205, y=40)
down_button = tk.Button(root, text="↓", command=move_mod_down)
down_button.place(x=205, y=258)
delete_button = tk.Button(root, text="Delete", command=delete_selected_mods)
delete_button.place(x=75, y=300)
add_mod_button = tk.Button(root, text="Add", command=add_mod)
add_mod_button.place(x=124, y=300)
rename_button = tk.Button(root, text="Rename", command=rename_mod)
rename_button.place(x=162, y=300)
force_button = tk.Button(root, text="Force Enable", command=force_enable_selected_mod)
force_button.place(x=300, y=260)

update_mod_lists()
root.mainloop()