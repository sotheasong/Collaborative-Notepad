import json
import os
import socket
from tkinter import *
from tkinter import filedialog
import pymongo

client = pymongo.MongoClient("mongodb+srv://sothea:2005@cluster0.bkxfvwj.mongodb.net/?retryWrites=true&w=majority")  # Connect to MongoDB
database = input("Enter the database: ")
db = client[database]  # Choose or create a database
col = input("Enter the collection: ")
collection = db[col]  # Choose or create a collection

def new_file():
    #Create a new file
    window.title("Untitled")
    text_area.delete(1.0, END)


def open_file():
    # Opening file
    options = list(collection.find({}))  # Lists all the files in the collection

    if len(options) == 0:
        print("There are no files in the database.")

    else:
        try:
            print("Choose the file to open")
            for option in options:
                name = json.dumps(option["file_name"])
                print(name.strip('"'))
            choice = input("Enter file name: ")
            # Asks for user input on which file
            if choice:
                document = collection.find_one({"file_name": choice})
                if document:
                    file_content = document.get('content')  # Gets the content of the file
                    window.title(os.path.basename(choice))
                    text_area.delete(1.0, END)  # Deletes the content of the current file
                    text_area.insert(1.0, file_content)  # Writes the content of the chosen file into the current file

        except Exception:
            print("couldn't read file")


def save_file(event=None):
    # Saving file
    # Initially asks user to save the file in user's system and creates a copy which is saved into mongodb
    file = filedialog.asksaveasfilename(initialfile='unititled.txt',
                                        defaultextension=".txt",
                                        filetypes=[("All Files", "*.*"),
                                                   ("Text Documents", "*.txt")])

    if file is None:
        return

    else:
        try:
            def get_unique_filename(file_path, collection):
                if collection.find_one({'file_name': file_path}) is None:
                    return file_path

                else:
                    userChoice = input("File already exists. Do you want to: " + "\n" + "(1) Override" + "\n" + "(2) Make a duplicate?" + "\n" + "--> ") # Asks the user if they want to overide the file or make a copy
                    if userChoice == "1":
                        print("File will be overriden")
                        collection.delete_one(collection.find_one({'file_name': file_path})) # Deletes the file in mongodb and saves the file with the same name
                    else:
                        file_name, file_extension = os.path.splitext(file_path) # Splits the file name into the "file name" and its extension
                        index = 1
                        new_file_path = f"{file_name}_{index}{file_extension}"

                        while True:
                            if collection.find_one({'file_name': new_file_path}) is None:
                                return new_file_path
                            index += 1
                            new_file_path = f"{file_name}_{index}{file_extension}" # Makes a copy of the file with the name in the format
                                                                                    # "filename_index.extension eg. example_2.txt
                        print("File created: " + new_file_path)

            
            window.title(os.path.basename(file)) # Changes the file name to the saved file name
            file_name = os.path.basename(file) # Copies the name of the file

            # Writes the file into the system
            with open(file, "w") as f1:
                f1.write(text_area.get(1.0, END))

            # Writes a copy of the file into mongodb database
            with open(file, "r") as f2:
                content = f2.read()
                new_file_name = get_unique_filename(file_name, collection) # Checks if theres any other files under the same name
                                                                            # and asks the user if they want to overried or make a copy
                json_content = {'file_name': new_file_name, 'content': content}


            collection.insert_one(json_content)

        except Exception:
            print("couldn't save file")

        finally:
            f1.close()
            f2.close()


def cut():
    # Creates a command in the menu bar that allows the user to cut text
    text_area.event_generate("<<Cut>>")

def copy():
    # Creates a command in the menu bar that allows the user to copy text
    text_area.event_generate("<<Copy>>")

def paste():
    # Creates a command in the menu bar that allows the user to paste text
    text_area.event_generate("<<Paste>>")

def getLineNumber():
    # Counts the amount of lines there are in the text file similar to an IDE
    row, _ = text_area.index('end').split('.')
    return '\n'.join(str(i) for i in range(1, int(row)))

def updateLineNumber(event=None):
    # Adds the line number to the UI as the user types
    LineNumber_bar = getLineNumber()
    LineNumber.config(state="normal")
    LineNumber.delete(1.0, END)
    LineNumber.insert(1.0, LineNumber_bar)
    LineNumber.config(state="disabled")

def on_text_scroll(*args):
    LineNumber.yview_moveto(args[0])    


# Graphic interface
window = Tk()
window.title("--text editor--")
file = None

# Line number bar to the left
LineNumber = Text(
    window,
    width=3,
    padx=1,
    state="disabled",
    takefocus=0,
    background="white",
    wrap="none"
)
LineNumber.pack(side=LEFT, fill=Y)

window_width = 500
window_height = 500
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

x = int((screen_width / 2) - (window_width / 2))
y = int((screen_height / 2) - (window_height / 2))

window.geometry("{}x{}+{}+{}".format(window_width, window_height, x, y))

font_name = StringVar(window)
font_name.set("Lucida Console")

font_size = StringVar(window)
font_size.set("12")

text_area = Text(window, font=(font_name.get(), font_size.get()), undo=True)
text_area.bind('<KeyRelease>', updateLineNumber)

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

# Creates a scrollbar
scroll_bar_vertical = Scrollbar(text_area, orient=VERTICAL, command=text_area.yview)
text_area.pack(expand="yes", fill="both", side=TOP)
scroll_bar_vertical.pack(side=RIGHT, fill=Y)
text_area.config(yscrollcommand=scroll_bar_vertical.set)
text_area['yscrollcommand'] = on_text_scroll

frame = Frame(window)
frame.pack()

menu_bar = Menu(window)
window.config(menu=menu_bar)

# Menu bar for editing and file manipulation
file_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="New", command=new_file)
file_menu.add_command(label="Open", command=open_file)
file_menu.add_command(label="Save", command=save_file)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=quit)

edit_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Edit", menu=edit_menu)
edit_menu.add_command(label="Cut", command=cut)
edit_menu.add_command(label="Copy", command=copy)
edit_menu.add_command(label="Paste", command=paste)
edit_menu.add_command(label="Undo", command=text_area.edit_undo)
edit_menu.add_command(label="Redo", command=text_area.edit_redo)

# Connects  to the server so the server can see who is connected 
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9999))

window.mainloop()
