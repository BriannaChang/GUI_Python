from tkinter import *
import requests
import json

FONT = 'Vandana', 12

# open file
with open('config.json') as f:
    file = json.load(f)

# create main application
dictionary = {}


def passInfo(param_dict):
    store_dictionary(param_dict)


def store_dictionary(param_dict: object) -> object:
    for k, v in param_dict.items():
        dictionary.update({k: v.get_value()})
        if v.entry.__class__.__name__ == 'Entry':
            v.entry.delete(0, 'end')


def getReponse(widget_name):
    for item in file.keys():
        if item == widget_name:
            apinfo = file[item]
    param = getParam(apinfo)
    # if apinfo['Method'] == 'POST':
    #     response = requests.post(apinfo['URL'], param)
    # elif apinfo['Method'] == 'PUT':
    #     response = requests.put(apinfo['URL'], param)
    # elif apinfo['Method'] == 'GET':
    #     response = requests.get(apinfo['URL'], param)
    # else:
    #     response = requests.delete(apinfo['URL'])
    # return response.text


def getParam(apinfo):
    param = apinfo['Body']
    fieldToReplace = re.findall('\{([\w]+)\}', param)
    # fill in the parameter
    for item in fieldToReplace:
        if item in dictionary.keys():
            param = param.replace(''.join(['{', item, '}']), dictionary[item])
    return param


# def create_column(root, label_text, r, optionList=[], name="", widget_type=None):
#     label = Label(root, text=label_text, anchor="e")
#     label.grid(row=r, column=2, sticky='E')
#     self.entry = None
#     self.name = name
#     fixed_text = StringVar()
#     if label_text in dictionary.keys():
#         fixed_text.set(dictionary[label_text])
#         self.entry = Label(root, textvariable=fixed_text)
#         self.entry.grid(row=r, column=3, sticky='W')
#     else:
#         self.entry = Entry(root, textvariable=fixed_text)
#         self.entry.grid(row=r, column=3, sticky='W')
#
#     if widget_type == 'entry_list':
#         scrollbar = Scrollbar(root)
#         self.entry = Listbox(root, yscrollcommand=scrollbar.set)
#         scrollbar.grid(row=r, column=3)
#         for item in optionList:
#             self.entry.insert(END, item)
#         self.entry.grid(row=r, column=3)
#         self.entry.focus_set()
#         scrollbar.config(command=self.entry.yview)

def popUp(window_title):
    popup = Tk()
    popup.wm_title(window_title)
    dpSubs(popup)
    popup.mainloop()


def dpSubs(master):
    dpSub=Frame(master)
    title = Label(dpSub, text='Create New Subscriber')
    title.pack()

# Main frame
root = Tk()
root.geometry('300x200+250+250')
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1, weight=1)
root.wm_title('BOA Application')
menu = Menu(root)
root.config(menu=menu)
subMenu = Menu(menu)
menu.add_cascade(label='Option', menu=subMenu)
subMenu.add_command(label='Create New Subscriber', command=lambda: popUp('Create New Subscriber'))

root.mainloop()