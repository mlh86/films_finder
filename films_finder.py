"""
films_finder -- A search app for your categorized movie collection

This app aks you to select the folders holding your by-genre films and
your by-actor films. It then lists the genres and actors found in those
folders and allows you to multi-select the genres and actors to search
by. You can also add an additional folder to filter by (e.g. a particular
director). The search results are displayed in a separate pop-up window
and you can launch any film by clicking on it.

Copyright (C) 2022  Mohammad L. Hussain

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import tkinter as tk
import tkinter.ttk as ttk
import tkinter.filedialog as tkfd
import webbrowser
import ctypes
import os

from pathlib import Path

def update_genres_folder():
    dirpath = tkfd.askdirectory(title="Select Genres Folder", initialdir=".")
    if dirpath:
        genres_folder.set(dirpath)
        genres = sorted([f.name for f in os.scandir(dirpath) if f.is_dir()])
        genres_list.set(genres)

def update_actors_folder():
    dirpath = tkfd.askdirectory(title="Select Actors Folder", initialdir=".")
    if dirpath:
        actors_folder.set(dirpath)
        actors = sorted([f.name for f in os.scandir(dirpath) if f.is_dir()])
        actors_list.set(actors)

def update_filter_folder():
    dirpath = tkfd.askdirectory(title="Select Additional Folder to Filter By", initialdir=".")
    filter_folder.set(dirpath)

def launch(filepath):
    file_url = "file://" + filepath
    webbrowser.open_new(file_url)

def perform_film_search():
    # Open a new window to display matching films links
    selected_genres = [genres_listbox.get(i) for i in genres_listbox.curselection()]
    selected_actors = [actors_listbox.get(i) for i in actors_listbox.curselection()]
    if not (selected_genres or selected_actors):
        err_msg = "Please select one or more genres or actors to search by."
        tk.messagebox.showwarning("Invalid Selection", err_msg)
    else:
        filmsets = []
        filmpaths = {}
        basepath = genres_folder.get()
        extensions = {".avi",".mkv",".mp4",".m4v",".xvid",".divx", ".mpeg"}
        for genre in selected_genres:
            filmset = set()
            dirpath = os.path.join(basepath, genre)
            for p in Path(dirpath).rglob("*"):
                if p.suffix in extensions:
                    filmset.add(p.name)
                    filmpaths[p.name] = str(p.resolve())
            filmsets.append(filmset)
        basepath = actors_folder.get()
        for actor in selected_actors:
            filmset = set()
            dirpath = os.path.join(basepath, actor)
            for p in Path(dirpath).rglob("*"):
                if p.suffix in extensions:
                    filmset.add(p.name)
                    filmpaths[p.name] = str(p.resolve())
            filmsets.append(filmset)
        if filter_folder.get():
            filmset = set()
            for p in Path(filter_folder.get()).rglob("*"):
                if p.suffix in extensions:
                    filmset.add(p.name)
                    filmpaths[p.name] = str(p.resolve())
            filmsets.append(filmset)
        films = sorted(set.intersection(*filmsets))
        if not films:
            err_msg = "No films matching your search criteria were found!"
            tk.messagebox.showwarning("No Matches", err_msg)
        else:
            cwin = tk.Toplevel(root)
            cwin.geometry("480x600")
            cwin.title(str(len(films)) + " Films Found")
            R = ttk.Frame(cwin, padding=10)
            R.grid(row=0,column=0,sticky='nsew')

            header_text = "Genres: " + ", ".join(selected_genres)
            header_text += "\nActors: " + ", ".join(selected_actors) + "\n"
            header_label = ttk.Label(R, text=header_text)
            header_label.grid(row=0, column=0, pady=8, sticky=tk.W)

            for i, f in enumerate(films, start=1):
                f_label = tk.Label(R, text=f, fg="blue", cursor="hand2")
                f_label.grid(row=i, column=0, pady=8, sticky=tk.W)
                f_label.bind("<Button-1>", lambda e, fpath=filmpaths[f]: launch(fpath))

################################################################################################
# The main GUI-creation code can be found below.

if os.name == 'nt':
    ctypes.windll.shcore.SetProcessDpiAwareness(2)

root = tk.Tk()
root.geometry("600x800")
root.resizable(False, False)
root.title("Films FInder")

F = ttk.Frame(root, padding=10)
F.grid(row=0,column=0,sticky='nsew')

select_genres_folder_btn = ttk.Button(F, text="Select Genres Folder", command=update_genres_folder)
select_genres_folder_btn.bind("<Return>", update_genres_folder)
select_genres_folder_btn.grid(row=0, column=1, pady=10, sticky=tk.EW)

select_actors_folder_btn = ttk.Button(F, text="Select Actors Folder", command=update_actors_folder)
select_actors_folder_btn.bind("<Return>", update_actors_folder)
select_actors_folder_btn.grid(row=0, column=2, pady=10, sticky=tk.EW)

genres_folder = tk.StringVar()
actors_folder = tk.StringVar()
genres_list = tk.StringVar()
actors_list = tk.StringVar()
filter_folder = tk.StringVar()

label_genres_folder = ttk.Label(F, text="GF: ")
entry_genres_folder = tk.Entry(F, state='disabled', relief=tk.GROOVE,
    highlightthickness=2, highlightbackground='silver', textvariable=genres_folder)
label_actors_folder = ttk.Label(F, text="AF: ")
entry_actors_folder = tk.Entry(F, state='disabled', relief=tk.GROOVE,
    highlightthickness=2, highlightbackground='silver', textvariable=actors_folder)

label_genres_folder.grid(row=1, column=0, sticky=tk.W)
entry_genres_folder.grid(row=1, column=1, sticky=tk.EW, columnspan=2)
label_actors_folder.grid(row=2, column=0, sticky=tk.W)
entry_actors_folder.grid(row=2, column=1, sticky=tk.EW, columnspan=2)

F.columnconfigure(1, minsize=250)
F.columnconfigure(2, minsize=250)

label_genres_list = ttk.Label(F, text="GENRES")
GLBF = ttk.Frame(F)
genres_listbox = tk.Listbox(GLBF, selectmode=tk.MULTIPLE, listvariable=genres_list, height=6, exportselection=0)
genres_scrollbar = ttk.Scrollbar(GLBF, orient=tk.VERTICAL, command=genres_listbox.yview)
genres_listbox['yscrollcommand'] = genres_scrollbar.set

label_genres_list.grid(row=3, column=1, columnspan=2, pady=10)
GLBF.grid(row=4, column=1, columnspan=2, sticky=tk.EW)
GLBF.columnconfigure(0, minsize=480)
genres_listbox.grid(row=0, column=0, sticky=tk.EW)
genres_scrollbar.grid(row=0,column=1,sticky='ns')

label_actors_list = ttk.Label(F, text="ACTORS")
ALBF = ttk.Frame(F)
actors_listbox = tk.Listbox(ALBF, selectmode=tk.MULTIPLE, listvariable=actors_list, height=6, exportselection=0)
actors_scrollbar = ttk.Scrollbar(ALBF, orient=tk.VERTICAL, command=actors_listbox.yview)
actors_listbox['yscrollcommand'] = actors_scrollbar.set

label_actors_list.grid(row=5, column=1, columnspan=2, pady=10)
ALBF.grid(row=6, column=1, columnspan=2, sticky=tk.EW)
ALBF.columnconfigure(0, minsize=480)
actors_listbox.grid(row=0, column=0, sticky=tk.EW)
actors_scrollbar.grid(row=0,column=1,sticky='ns')

additional_filter_folder_btn = ttk.Button(F, text="Select Additional Folder To Filter By", command=update_filter_folder)
additional_filter_folder_btn.bind("<Return>", update_filter_folder)
additional_filter_folder_btn.grid(row=7, column=1, columnspan=2, pady=10)

entry_filter_folder = tk.Entry(F, state='disabled', relief=tk.GROOVE,
    highlightthickness=2, highlightbackground='silver', textvariable=filter_folder)
entry_filter_folder.grid(row=8, column=1, sticky=tk.EW, columnspan=2)

boldBtnStyle = ttk.Style()
boldBtnStyle.configure("Bold.TButton", font = ('Sans','14','bold'))
search_btn = ttk.Button(F, text="SEARCH", command=perform_film_search, style="Bold.TButton")
search_btn.bind("<Return>", perform_film_search)
search_btn.grid(row=9, column=1, columnspan=2, pady=30)

root.mainloop()
