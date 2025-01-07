# -*- coding: utf-8 -*-
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import json
import shutil
from PIL import Image, ImageTk
import os
import pyotp
from pynput.keyboard import Key, Controller
import psutil
import subprocess
import datetime
from datetime import datetime, timedelta
import random

class File:
    def __init__(self, file: str, icon: str, name: str, monitor: str):
        self.file = file
        self.icon = icon
        self.name = name
        self.monitor = monitor

    def save_to_json(self, filename):
        file_dict = {"file": self.file, "icon": self.icon, "name": self.name, "monitor": self.monitor}
        with open(filename, "w") as f:
            f.write(json.dumps(file_dict, indent=2))


def on_enter(event):
    event.widget.config(bg="#E8E8E8")  # Change background color when mouse enters

def on_leave(event):
    event.widget.config(bg="#E0E0E0")   # Change background color when mouse leaves


def launchSelectedProgram():

    selected_item = tree.selection()
    details = tree.item(selected_item)
    # [:2] zato ker izberemo od druge črke naprej zato ker prva dva simbola smo  dali kot presledka (za dodaten prostor med sliko in imenom)
    item_name = details.get("text")[2:]

    file_path = f"profiles/{item_name}.json"
    with open(file_path, "r") as f:
        json_data = json.loads(f.read())
        file = json_data["file"]

        global launched
        launched = os.path.basename(json_data["file"])
        os.startfile(file)


def deleteItem(item_name):
    for item in tree.get_children():
        if tree.item(item, "text") == f"  {item_name}":
            tree.delete(item)
            break

    os.remove(f"profiles/{item_name}.json")
    os.remove(f"pics/{item_name}.png")


# Add button function
def okButton(name, path, icon, monitor):
    if name.strip() and path.strip():
        shutil.copyfile(icon, f"pics/{name}.png")
        programFile = File(path, f"pics/{name}.png", name, monitor)
        programFile.save_to_json(f"profiles/{name}.json")

        # Prikaz novega programa v tabeli
        file_path = f"profiles/{name}.json"
        with open(file_path, "r") as f:
            json_data = json.loads(f.read())
            icon = json_data["icon"]
            name = json_data["name"]
            monitor = json_data["monitor"]

        with Image.open(f"pics/{name}.png") as photo:
            photo_regular = ImageTk.PhotoImage(
                photo.resize(
                    (
                        int(40 * photo.width / photo.height),
                        40,
                    ),
                    Image.Resampling.LANCZOS,
                )
            )
        photo_regular_dict[name] = photo_regular
        tree.insert("", END, text=f"  {name}", image=photo_regular_dict[name])
        window.update()

def randomCapitalize(sentence):
    # Convert the sentence to a list of characters
     chars = list(sentence)

     for i, char in enumerate(chars):
        # Check if the character is a letter or a special character
        if char.isalpha() or char in ["š", "č", "ž"]:
            # Generate a random number between 0 and 1
            rand_num = random.random()
            # Randomly capitalize the character with a 50% probability
            if rand_num < 0.5:
                chars[i] = char.upper()

     # Join the characters back into a string
     return ''.join(chars)

def enterButton(sentence, text, text_window):
    if sentence == text:
        window.deiconify()
        text_window.destroy()
        with open("appminder.json", "r", encoding="utf-8") as f:
            json_data_om=json.loads(f.read())

        with open("appminder.json", "w", encoding="utf-8") as f:
          json_data_om["datetime"]=f"{datetime.now()}"
          json.dump(json_data_om, f, indent=4)
    else:
        window.destroy()
        window.quit


def set_path(entry_field, settings_window):
    entry_field.config(state="normal")
    path = filedialog.askopenfilename()
    entry_field.delete(0, END)
    entry_field.insert(0, path)
    entry_field.config(state="readonly")
    settings_window.focus_force()


def submitButton(code):
    key = "AppMinderSecretKey23452345234523452345324523454534254352523453425345435"
    totp = pyotp.TOTP(key)
    if code == totp.now():
        openText()
    else:
        window.destroy()
        window.quit

def openText():
    
    openTextWindow = Toplevel(window)
    openTextWindow.title("AppMinder")

    # definiramo širino in višino našega zaslona
    screen_width_Text = openTextWindow.winfo_screenwidth()
    screen_height_Text = openTextWindow.winfo_screenheight()

    # x and y are dimensions of our OTP window
    x_Text = int((screen_width_Text / 2) - (300 / 2))
    y_Text = int((screen_height_Text / 2) - (150 / 2))

    openTextWindow.geometry(f"300x150+{x_Text}+{y_Text}")
    openTextWindow.resizable(False, False)
    openTextWindow.configure(bg="white")
    openTextWindow.attributes("-topmost", 1)
    openTextWindow.iconbitmap("pics/window_logo.ico")
    
    frameText = Frame(openTextWindow, bg="#E0E0E0", width=410, height=185, highlightbackground="#888888", highlightthickness=1)
    frameText.pack(padx=20, pady=20)

    title_frameText = Frame(frameText, bg="#E0E0E0", width=410, highlightbackground="#888888", highlightthickness=1)
    title_frameText.place(rely=0.095, relx=-0.002, anchor="w")

    title_Text = Label(title_frameText, text="                          Text Verification                          ", bg="#E0E0E0", font=("Segoe UI", 9, "bold"))
    title_Text.pack(padx=0.5)
    
    with open("appminder.json","r", encoding="utf-8") as f:
       json_data= json.loads(f.read())
       sentence = json_data[f"sentence{random.randint(1,10)}"]
       rand_sentence = randomCapitalize(sentence)

    random_text = Label(openTextWindow, text=rand_sentence, bg="#E0E0E0", font=("Segoe UI", 9), wraplength=250)
    random_text.place(rely=0.32, relx=0.075)

    entry_Text = Entry(frameText, relief=FLAT, highlightbackground="#888888", highlightthickness=1, width=40)
    entry_Text.place(rely=0.73, relx=0.025)
 

    entry_Text.bind("<Return>", lambda event: enterButton(rand_sentence, entry_Text.get(), openTextWindow))

    #funkcija za spremembo jezika tipkovnice, ker sicer pride do glitcha da nemoreš v entry napisat "č" črke
    def change_keyboard_lang(event):
     keyboard = Controller()
     for i in range(2):
        keyboard.press(Key.alt)
        keyboard.press(Key.shift_l)
        keyboard.release(Key.shift_l)
        keyboard.release(Key.alt)

    entry_Text.bind("<FocusIn>", change_keyboard_lang)

    #terminate entire program when OTP window is closed  
    def on_closing():
        # Destroy the Toplevel window
        openTextWindow.destroy()
        # Terminate the entire program
        window.quit()
        window.destroy()

    # Intercept the close event
    openTextWindow.protocol("WM_DELETE_WINDOW", on_closing)
   

def openOTP():

    openOTP = Toplevel(window)
    openOTP.title("AppMinder")

    # definiramo širino in višino našega zaslona
    screen_width_OTP = openOTP.winfo_screenwidth()
    screen_height_OTP = openOTP.winfo_screenheight()

    # x and y are dimensions of our OTP window
    x_OTP = int((screen_width_OTP / 2) - (300 / 2))
    y_OTP = int((screen_height_OTP / 2) - (150 / 2))

    openOTP.geometry(f"300x150+{x_OTP}+{y_OTP}")
    openOTP.resizable(False, False)
    openOTP.configure(bg="white")
    openOTP.attributes("-topmost", 1)
    openOTP.iconbitmap("pics/window_logo.ico")
    
    frameOTP = Frame(openOTP, bg="#E0E0E0", width=410, height=180, highlightbackground="#888888", highlightthickness=1)
    frameOTP.pack(padx=20, pady=20)

    title_frameOTP = Frame(frameOTP, bg="#E0E0E0", width=410, highlightbackground="#888888", highlightthickness=1)
    title_frameOTP.place(rely=0.095, relx=-0.002, anchor="w")

    title_OTP = Label(title_frameOTP, text="                        2-Step Verification                        ", bg="#E0E0E0", font=("Segoe UI", 9, "bold"))
    title_OTP.pack(padx=0.5)
    
    entry_OTP = Entry(frameOTP, relief=FLAT, highlightbackground="#888888", highlightthickness=1, width=10)
    entry_OTP.place(rely=0.3, relx=0.368)
 
    frame_submit = Frame(frameOTP, highlightbackground="#888888", highlightthickness=1)
    frame_submit.place(rely=0.6, relx=0.39)
    button_submit = Button(frame_submit, bg="#E0E0E0", command=lambda:(
            submitButton(entry_OTP.get()),
            openOTP.destroy()
        ),text="Submit", relief=FLAT, borderwidth=0, pady=0, padx=5)
    button_submit.pack()
    
    
    button_submit.bind("<Enter>", on_enter)  # Bind on_enter function to mouse enter event
    button_submit.bind("<Leave>", on_leave)  # Bind on_leave function to mouse leave event 


    #terminate entire program when OTP window is closed  
    def on_closing():
        # Destroy the Toplevel window
        openOTP.destroy()
        # Terminate the entire program
        window.quit()
        window.destroy()

    # Intercept the close event
    openOTP.protocol("WM_DELETE_WINDOW", on_closing)

    
# settings window
def openSettings():

    # Add item frame
    openSettings = Toplevel(window)
    openSettings.title("Settings")
    openSettings.geometry(f"415x350+{window.winfo_rootx() + 220}+{window.winfo_rooty() + 35}")
    openSettings.resizable(False, False)
    openSettings.configure(bg="white")
    openSettings.attributes("-topmost", 0)
    openSettings.iconbitmap("pics/settings_logo.ico")
    
    frame1 = Frame(openSettings, bg="#E0E0E0", width=410, height=180, highlightbackground="#888888", highlightthickness=1)
    frame1.pack(padx=20, pady=20)

    title_frame = Frame(frame1, bg="#E0E0E0", width=410, highlightbackground="#888888", highlightthickness=1)
    title_frame.place(rely=0.055, relx=-0.002, anchor="w")

    title_additem = Label(title_frame, text="  Add item                                                                                                      ", bg="#E0E0E0", font=("Segoe UI", 9, "bold"))
    title_additem.pack(padx=1.5)
    
    title_launchfile = Label(frame1, bg="#E0E0E0", text="  Launch file path")
    title_launchfile.place(rely=0.18, relx= 0.025)
    entry_launchfile = Entry(frame1, state="readonly", relief=FLAT, bg="#E6E6E6", highlightbackground="#888888", highlightthickness=1, width=19, cursor="arrow")
    entry_launchfile.place(rely=0.18, relx=0.37)
    frame_launchfile = Frame(frame1, highlightbackground="#888888", highlightthickness=1)
    frame_launchfile.place(rely=0.18, relx=0.71)
    browse_launchfile = Button(frame_launchfile, command=lambda:set_path(entry_launchfile, openSettings), bg="#E0E0E0", text="Browse", relief=FLAT, borderwidth=0, pady=0)
    browse_launchfile.pack()

    title_monitorfile = Label(frame1, bg="#E0E0E0", text="  Monitoring file path")
    title_monitorfile.place(rely=0.360, relx= 0.025)
    entry_monitorfile = Entry(frame1, relief=FLAT, state="readonly", bg="#E6E6E6",highlightbackground="#888888", highlightthickness=1, width=19, cursor="arrow")
    entry_monitorfile.place(rely=0.360, relx=0.37)
    frame_monitorfile = Frame(frame1, highlightbackground="#888888", highlightthickness=1)
    frame_monitorfile.place(rely=0.36, relx=0.71)
    browse_monitorfile = Button(frame_monitorfile, command=lambda:set_path(entry_monitorfile, openSettings), bg="#E0E0E0", text="Browse", relief=FLAT, borderwidth=0, pady=0)
    browse_monitorfile.pack()

    title_iconfile = Label(frame1, bg="#E0E0E0", text="  Icon file path")
    title_iconfile.place(rely=0.54, relx= 0.025)
    entry_iconfile = Entry(frame1,state="readonly", relief=FLAT, bg="#E6E6E6", highlightbackground="#888888", highlightthickness=1 , width=19, cursor="arrow")
    entry_iconfile.place(rely=0.54, relx=0.37)
    frame_iconfile = Frame(frame1, highlightbackground="#888888", highlightthickness=1)
    frame_iconfile.place(rely=0.54, relx=0.71)
    browse_iconfile = Button(frame_iconfile, command=lambda:set_path(entry_iconfile, openSettings), bg="#E0E0E0", text="Browse", relief=FLAT, borderwidth=0, pady=0)
    browse_iconfile.pack()

    title_itemname = Label(frame1, bg="#E0E0E0", text="  Item name")
    title_itemname.place(rely=0.72, relx= 0.025)
    entry_itemname = Entry(frame1, relief=FLAT, highlightbackground="#888888", highlightthickness=1, width=19)
    entry_itemname.place(rely=0.72, relx=0.37)

    frame_add = Frame(frame1, highlightbackground="#888888", highlightthickness=1)
    frame_add.place(rely=0.81, relx=0.86)
    button_add = Button(frame_add, bg="#E0E0E0", command=lambda:(
            okButton(entry_itemname.get(), entry_launchfile.get(), entry_iconfile.get(), entry_monitorfile.get()),
            openSettings.destroy(),
        ),text="Add", relief=FLAT, borderwidth=0, pady=0, padx=5)
    button_add.pack()
    
    # Remove Item frame
    frame2 = Frame(openSettings, bg="#E0E0E0", width=410, height=80, highlightbackground="#888888", highlightthickness=1)
    frame2.pack(padx=20, pady=0)

    title_frame2 = Frame(frame2, bg="#E0E0E0", width=410, highlightbackground="#888888", highlightthickness=1)
    title_frame2.place(rely=-0.01, relx=-0.002)

    title_removeitem = Label(title_frame2, text="  Remove item                                                                                               ", bg="#E0E0E0", font=("Segoe UI", 9, "bold"))
    title_removeitem.pack()

    title_removename = Label(frame2, bg="#E0E0E0", text="  Item name")
    title_removename.place(rely=0.41, relx= 0.025)
    entry_removename = Entry(frame2, relief=FLAT, highlightbackground="#888888", highlightthickness=1, width=19)
    entry_removename.place(rely=0.41, relx=0.27)

    frame_remove = Frame(frame2, highlightbackground="#888888", highlightthickness=1)
    frame_remove.place(rely=0.57, relx=0.804)
    button_remove = Button(frame_remove, bg="#E0E0E0", command=lambda:(deleteItem(entry_removename.get()), openSettings.destroy()), text="Remove", relief=FLAT, borderwidth=0, pady=0, padx=5)
    button_remove.pack()
    
    button_add.bind("<Enter>", on_enter)  # Bind on_enter function to mouse enter event
    button_add.bind("<Leave>", on_leave)  # Bind on_leave function to mouse leave event 
    browse_iconfile.bind("<Enter>", on_enter)  # Bind on_enter function to mouse enter event
    browse_iconfile.bind("<Leave>", on_leave)  # Bind on_leave function to mouse leave event 
    browse_launchfile.bind("<Enter>", on_enter)  # Bind on_enter function to mouse enter event
    browse_launchfile.bind("<Leave>", on_leave)  # Bind on_leave function to mouse leave event
    browse_monitorfile.bind("<Enter>", on_enter)  # Bind on_enter function to mouse enter event
    browse_monitorfile.bind("<Leave>", on_leave)  # Bind on_leave function to mouse leave event
    button_remove.bind("<Enter>", on_enter)  # Bind on_enter function to mouse enter event
    button_remove.bind("<Leave>", on_leave)  # Bind on_leave function to mouse leave event


window = Tk()
window.title("AppMinder")

# definiramo širino in višino našega zaslona
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# x in y predstavljata center zaslona našega ekrana
x = int((screen_width / 2) - (520 / 2))
y = int((screen_height / 2) - (610 / 2))

window.geometry(f"520x610+{x}+{y}")
window.resizable(False, False)
window.configure(bg="#3B3B3B")

with open("appminder.json", "r", encoding="utf-8") as f:
    json_data_re = json.loads(f.read())
    ura = json_data_re["datetime"]

    if (ura[:10] == f"{datetime.now()}"[:10]) :
        pass
    elif (ura[:10] != f"{datetime.now()}"[:10]):
        # Hide main launcher window
        window.withdraw()
        openOTP()

               
           
# Treeview custom style
style = ttk.Style()
style.theme_use("clam")
style.configure(
    "Custom.Treeview",
    font=("Segoe UI", 20),
    rowheight=60,
    background="#191919",
    fieldbackground="#191919",
    foreground="white",
    relief="flat",
)
# Removes border
style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

tree = ttk.Treeview(show="tree")
tree.configure(style="Custom.Treeview", height=2)
tree.pack(fill=BOTH, expand=True, padx=13, pady=(20, 3))

# Settings button
cogwheel = PhotoImage(file="pics/settings.png")
button7 = Button(
    image=cogwheel,
    command=openSettings,
    font=("Segoe UI", 14),
    background="#3B3B3B",
    activebackground="#3B3B3B",
    border=0,
    relief="flat",
    cursor="hand2"
)
button7.pack(padx=(0, 15), pady=(15, 20), side="right")

# Launch button
launchbutton = PhotoImage(file="pics/launch.png")
button9 = Button(
    image=launchbutton,
    command=lambda: launchSelectedProgram(),
    font=("Segoe UI", 16),
    background="#3B3B3B",
    activebackground="#3B3B3B",
    relief="flat",
    border=0,
    cursor="hand2",
)
button9.pack(padx=25, pady=(5, 5), side="left")


# Branje datotek json in nalaganje podatkov vsakega programa v tabelo
photo_regular_dict = {}
for profile in os.listdir("profiles"):
    if profile.endswith(".json"):
        file_path = os.path.join("profiles", profile)
        with open(file_path, "r") as f:
            json_data_ga = json.loads(f.read())
            file = json_data_ga["file"]
            icon = json_data_ga["icon"]
            name = json_data_ga["name"]

        with Image.open(f"pics/{name}.png") as photo:
            photo_regular = ImageTk.PhotoImage(
                photo.resize(
                    (
                        int(40 * photo.width / photo.height),
                        40,
                    ),
                    Image.Resampling.LANCZOS,
                )
            )
        photo_regular_dict[name] = photo_regular
        tree.insert("", END, text=f"  {name}", image=photo_regular_dict[name])


window.iconbitmap("pics/window_logo.ico")
window.mainloop()




