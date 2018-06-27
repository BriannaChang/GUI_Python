from tkinter import *
import tkinter as tk
import requests
import json

FONT = 'Vandana', 12

# open file
with open('config.json') as f:
    file = json.load(f)

# usable class

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
    param = getParam(apinfo['Body'])
    url = getParam(apinfo['URL'])
    if apinfo['Method'] == 'POST':
        response = requests.post(url, param)
    elif apinfo['Method'] == 'PUT':
        response = requests.put(url, param)
    elif apinfo['Method'] == 'GET':
        if widget_name == 'Household':
            response = requests.get(url)
        else:
            response = requests.get(url, param)
    else:
        response = requests.delete(url)
    return response.text


def getParam(apinfo):
    fieldToReplace = re.findall('\{([\w]+)\}', apinfo)
    # fill in the parameter
    for item in fieldToReplace:
        if item in dictionary.keys():
            param = apinfo.replace(''.join(['{', item, '}']), dictionary[item])
    return apinfo


# Create text box.


class CreateColumn(Frame):
    def __init__(self, root, label_text, r, optionList=[], name="", widget_type=None, fixed_text=None):
        Frame.__init__(self, root)
        label = Label(root, text=label_text, anchor="e")
        label.grid(row=r, column=2, sticky='E')
        self.entry = None
        self.name = name
        char_text = StringVar()
        if fixed_text is None:
            self.entry = Entry(root, textvariable=char_text)
            self.entry.grid(row=r, column=3, sticky='W')

        else:
            self.entry = Label(root, text=fixed_text)
            self.entry.grid(row=r, column=3, sticky='W')

        if widget_type == 'entry_list':
            scrollbar = Scrollbar(root)
            self.entry = Listbox(root, yscrollcommand=scrollbar.set)
            scrollbar.grid(row=r, column=3)
            for item in optionList:
                self.entry.insert(END, item)
            self.entry.grid(row=r, column=3)
            scrollbar.config(command=self.entry.yview)

    def set_title(self, title):
        title = Label(text=title, font=FONT)
        title.grid(row=2, column=2, columnspan=2)

    def get_value(self):
        if self.entry.__class__.__name__ == 'Listbox':
            return self.entry.get(self.entry.curselection())

        elif self.entry.__class__.__name__ == 'Entry':
            return self.entry.get()

        elif self.entry.__class__.__name__ == 'Label':
            return self.entry.cget('text')


class Boa(Tk):
    # the main frame to store things.
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.wm_title('BOA Application')
        root = Frame(self, width=1080, height=720)
        root.pack(side=RIGHT)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)
        menu = tk.Menu(root)
        tk.Tk.config(self, menu=menu)
        subMenu = tk.Menu(menu)
        menu.add_cascade(label='Option', menu=subMenu)
        subMenu.add_command(label='Create New Subscriber', command=lambda: self.pop_up(DpSubs))
        self.frames = {}
        btnSubs = Button(self, text='Subscriber', state=NORMAL, name='btnSubs')
        btnSubs.pack(side=TOP)
        btnDev = Button(self, text='Device',
                        state=NORMAL, name='btnDev')
        btnDev.pack(side=TOP)
        btnSett = Button(self, text='Settings',
                         state=NORMAL, name='btnSett')
        btnSett.pack(side=TOP)
        self.set_btn_status('btnSubs')
        self.show_frame(root, AccountInfo)

    def set_btn_status(self, btn: object) -> object:
        self.nametowidget(btn).config(state=DISABLED)

    def page_arrange(self, root, frame_name):
        frame = frame_name(root, self)
        self.frames[frame_name] = frame
        frame.pack(side=LEFT)

    def show_frame(self, root, cont, param_dict=None):
        if param_dict:
            self.store_dictionary(param_dict)
        self.page_arrange(root, cont)
        frame = self.frames[cont]
        frame.tkraise()

    def pop_up(self, frame):
        self.newWindow = Toplevel()
        self.newWindow.wm_title('Create New Subscriber')
        frame(self.newWindow)

# Subscriber page. Account info is empty before log in. Household ID will be needed to log in.


class AccountInfo(Frame):
    # create menu page with all the button.
    def __init__(self, root, controller):
        Frame.__init__(self, root)
        self.name = 'AccountInfo'
        self.root = root
        self.update()
        self.update_idletasks()
        logInCredentials = CreateColumn(self, 'HouseholdId', 2)
        param_dict = {'householdID': logInCredentials}
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser(param_dict))
        logBtn.grid(row=2, column=4, sticky='W')
        Label(self, text='Account info').grid(column=2, columnspan=3)
        param_names = ['deviceId', 'accountId', 'smartCardId', 'subscriberId', 'offerKey', 'bouquetId',
                       'zipCode', 'bssFullType', 'community', 'authorizationType', 'populationId', 'currency']

        param_dict.update({p: CreateColumn(self, p, i + 4, name=p, fixed_text='') for i, p in enumerate(param_names)})
        print(param_dict)
        refreshBtn= Button(self, text='Update', command=lambda: self.refresh())
        refreshBtn.grid(row=17, column=3, sticky='W')

    def logInUser(self, param):
        widget_name = 'Household'
        passInfo(param)
        rep = getReponse(widget_name)
        print(rep)

    def refresh(self):
        objectList = self.root.winfo_children()[0].winfo_children()
        for item in range(0, len(objectList)):
            print(objectList)
            print(dictionary)
            if objectList[item].widgetName == 'label':
                param = objectList[item].cget('text')
                print(param)
                if param in dictionary.keys():
                    self.root.winfo_children()[0].winfo_children()[item+1].config(text=dictionary[param])


class DpSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Create New Subscriber'
        param_dict = {}
        dictionary ={}
        param_names = ['householdId', 'deviceId', 'accountId', 'smartCardId',
                           'subscriberId', 'offerKey', 'bouquetId', 'zipCode', 'community'
            , 'authorizationType', 'populationId', 'currency']
        dictionary.update({'community': 'Malaysia Live', 'authorizationType': 'SUBSCRIPTION', 'populationId': '1'
            , 'currency': '0458'})
        for i,p in enumerate(param_names):
            if p in dictionary.keys():
                item = CreateColumn(root, p, i + 3, name=p, fixed_text=dictionary[p])
            else:
                item = CreateColumn(root, p, i + 3, name=p)
            param_dict.update({p: item})
        param_dict['bssFullType'] = CreateColumn(root, 'bssFullType', 16,
                                                     optionList=['IVP-DTH-STB', 'IVP-IP-STB'], name='bssFullType', widget_type='entry_list')
        saveButton = Button(root, text='Create', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=17, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=17, column=3, sticky='E')

    def refresh(self, param_dict):
        widget_name = self.name
        passInfo(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class Device(Frame):
    # create menu page with all the button.
    def __init__(self, root):
        Frame.__init__(self, root)
        self.name = 'Device'
        self.root = root
        self.update()
        self.update_idletasks()
        logInCredentials = CreateColumn(self, 'text', 'Household ID', 2)
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser(logInCredentials.entry.get()))
        logBtn.grid(row=2, column=4, sticky='W')
        Label(self, text='Account info').grid(column=2, columnspan=3)
        param_names = ['deviceId', 'accountId', 'smartCardId', 'subscriberId', 'bssFullType']
        for item in param_names:
            if dictionary[item]:
                param_dict = {p: CreateColumn(self, p, i + 4, name=p) for i, p in
                            enumerate(param_names)}

            else:
                param_dict = {p: CreateColumn(self, p, i + 4, name=p) for i, p in
                            enumerate(param_names)}
        createBtn = Button(self, text='Add More device', command=lambda: self.pop_up(DpSubs))
        createBtn.grid(row=17, column=3, sticky='W')

    def logInUser(self, param):
        widget_name = 'Log in'
        passInfo(param)
        getReponse(AccountInfo, widget_name)
        self.update()
        self.update_idletasks()

    def pop_up(self, frame):
        self.newWindow = Toplevel()
        self.newWindow.wm_title('Create New Subscriber')
        frame(self.newWindow)


boa = Boa()
boa.mainloop()