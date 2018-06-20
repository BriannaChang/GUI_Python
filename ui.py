from tkinter import *
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
    param = getParam(apinfo)
    print(dictionary)
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


# Create text box.


class CreateColumn(Frame):
    def __init__(self, root, widget_type, label_text, r, optionList=[], name="", fixed_text=None):
        Frame.__init__(self, root)
        label = Label(root, text=label_text, anchor="e")
        label.grid(row=r, column=2, sticky='E')
        self.entry = None
        self.name = name
        if widget_type == 'text':
            if fixed_text is None:
                character_value = StringVar()
                self.entry = Entry(root, textvariable=character_value)
                self.entry.grid(row=r, column=3, sticky='W')
            else:
                self.entry = Label(root, text=fixed_text)
                self.entry.grid(row=r, column=3, sticky='W')

        elif widget_type == 'list':
            scrollbar = Scrollbar(root)
            self.entry = Listbox(root, yscrollcommand=scrollbar.set)
            scrollbar.grid(row=r, column=3)
            for item in optionList:
                self.entry.insert(END, item)
            self.entry.grid(row=r, column=3)
            self.entry.focus_set()
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
        self.frames = {}
        self.update()
        btnSubs = Button(self, text='Subscriber', state=NORMAL, name='btnSubs')
        btnSubs.pack(side=TOP)
        btnDev = Button(self, text='Device',
                        state=NORMAL, name='btnDev')
        btnDev.pack(side=TOP)
        btnSett = Button(self, text='Settings',
                         state=NORMAL, name='btnSett')
        btnSett.pack(side=TOP)
        self.set_btn_status('btnSubs')
        
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
        frame.update()
        frame.tkraise()

    def refresh(self, widget):
        show = self.nametowidget(widget)
        self.frame = show

class RootPage(Frame):
    def __init__(self, root):
        Frame.__init__(self, root)
        # create buttons to show item
        btnSubs = Button(self, text='Subscriber', state=NORMAL, name='btnSubs')
        btnSubs.grid(row=1, column=1, sticky='W')
        btnDev = Button(self, text='Device',
                        state=NORMAL, name='btnDev')
        btnDev.grid(row=2, column=1, sticky='W')
        btnSett = Button(self, text='Settings',
                         state=NORMAL, name='btnSett')
        btnSett.grid(row=3, column=1, sticky='W')

    def set_btn_status(self, btn: object) -> object:
        self.nametowidget(btn).config(state=DISABLED)


# Subscriber page. Account info is empty before log in. Household ID will be needed to log in.


class AccountInfo(Frame):
    # create menu page with all the button.
    def __init__(self, root, controller):
        Frame.__init__(self, root)
        self.widgetName = 'AccountInfo'
        self.root = root
        logInCredentials = CreateColumn(self, 'text', 'Household ID', 2)
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser(logInCredentials.entry.get()))
        logBtn.grid(row=2, column=4, sticky='W')
        Label(self, text='Account info').grid(column=2, columnspan=3)
        param_names = ['deviceId', 'accountId', 'smartCardId', 'subscriberId', 'offerKey', 'bouquetId',
                       'zipCode', 'bssFullType', 'community', 'authorizationType', 'populationId', 'currency']
        if dictionary:
            param_dict = {p: CreateColumn(self, 'text', p, i + 4, name=p, fixed_text=dictionary[p]) for i, p in
                          enumerate(param_names)}

        else:
            param_dict = {p: CreateColumn(self, 'text', p, i + 4, name=p, fixed_text='') for i, p in
                          enumerate(param_names)}
        createBtn= Button(self, text='Create New Subscriber', command=lambda: self.pop_up(DpSubs))
        createBtn.grid(row=17, column=3, sticky='W')

    def pop_up(self, frame):
        self.newWindow = Toplevel()
        self.newWindow.wm_title('Create New Subscriber')
        frame(self.newWindow)


class DpSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Create New Subscriber'
        param_names = ['householdId', 'deviceId', 'accountId', 'smartCardId',
                           'subscriberId', 'offerKey', 'bouquetId', 'zipCode']
        param_dict = {p: CreateColumn(root, 'text', p, i + 3, name=p) for i, p in enumerate(param_names)}
        param_dict['bssFullType'] = CreateColumn(root, 'list', 'bssFullType', 11,
                                                     optionList=['IVP-DTH-STB', 'IVP-IP-STB'], name='bssFullType')
        param_dict['community'] = CreateColumn(root, 'text', 'community', 12, name='community'
                                                   , fixed_text='Malaysia Live')
        param_dict['authorizationType'] = CreateColumn(root, 'text', 'authorizationType', 13,
                                                           name='authorizationType'
                                                           , fixed_text='SUBSCRIPTION')
        param_dict['populationId'] = CreateColumn(root, 'text', 'populationId', 14, name='populationId',
                                                      fixed_text='1')
        param_dict['currency'] = CreateColumn(root, 'text', 'currency', 15, name='currency', fixed_text='0458')
        saveButton = Button(root, text='Create', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=17, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=17, column=3, sticky='E')

    def refresh(self, param_dict):
        widget_name = self.name
        passInfo(param_dict)
        getReponse(widget_name)
        self.root.destroy()


    # def logInUser(self, param):
    #     print(param)
    #     dict= {'householdid': param}
    #     resp = getResponse('http://10.7.0.74:9001/BillingAdaptor/api/v2/household/', param)
    #     print(resp)

# class CreateMenuBanner(Frame):
#     def __init__(self, root, controller):
#         Frame.__init__(self, root)
#         # create buttons to show item
#         btnSubs = Button(self, text='Subscriber', command=lambda: controller.show_frame(root, AccountInfo),
#                          state=NORMAL, name='btnSubs')
#         btnSubs.grid(row=1, column=1, sticky='W')
#         btnDev = Button(self, text='Device',
#                         state=NORMAL, name='btnDev')
#         btnDev.grid(row=2, column=1, sticky='W')
#         btnSett = Button(self, text='Settings',
#                          state=NORMAL, name='btnSett')
#         btnSett.grid(row=3, column=1, sticky='W')
#
#     def set_title(self, title):
#         title = Label(self, text=title, font=FONT)
#         title.grid(row=2, column=1, columnspan=2)
#
#     def set_btn_status(self, btn: object) -> object:
#         self.nametowidget(btn).configure(state=DISABLED)


# class SubscriberOption(Frame):
#     def __init__(self, root, controller):
#         Frame.__init__(self, root)
#         menu = CreateMenuBanner(self, controller)
#         menu.set_btn_status('btnSubs')
#         menu.grid(row=1, columnspan=3, sticky='W')
#         param_dict['bssFullType'] = CreateColumn(self, 'list', 'bssFullType', 11,
#                                                  optionList=['IVP-DTH-STB', 'IVP-IP-STB'], name='bssFullType')
#         param_dict['community'] = CreateColumn(self, 'text', 'community', 12, name='community'
#                                                , fixed_text='Malaysia Live')
#         param_dict['authorizationType'] = CreateColumn(self, 'text', 'authorizationType', 13, name='authorizationType'
#                                                , fixed_text='SUBSCRIPTION')
#         param_dict['populationId'] = CreateColumn(self, 'text', 'populationId', 14, name='populationId', fixed_text='1')
#         param_dict['currency'] = CreateColumn(self, 'text', 'currency', 15, name='currency', fixed_text='0458')
#         btnCreate = Button(self, text=' Create New Subscriber', command=lambda: controller.show_frame(root, DpSubs))
#         btnCreate.grid(row=2, column=2)
#         btnDelete = Button(self, text=' Delete Subscriber', command=lambda: controller.show_frame(root, DelSubs))
#         btnDelete.grid(row=3, column=2)

# class DelSubs(Frame):
#     def __init__(self, root, controller):
#         Frame.__init__(self, root)
#         menu = CreateMenuBanner(self, controller)
#         menu.set_btn_status('btnSubs')
#         menu.grid(row=1, columnspan=3, sticky='W')
#         menu.set_title('Delete Subscriber')
#         param_names = ['householdId']
#         param_dict = {p: CreateColumn(self, 'text', p, i+3, name=p) for i, p in enumerate(param_names)}
#         delButton = Button(self, text='Delete Account', command=lambda : controller.show_frame(root, SubscriberOption, param_dict))
#         delButton.grid(row=16, column=2, sticky='E')
#         cancelButton = Button(self, text='Cancel', command=lambda: controller.show_frame(root, SubscriberOption))
#         cancelButton.grid(row=17, column=2, sticky='E')
#
#
# class Device(Frame):
#     def __init__(self, root, controller):
#         Frame.__init__(self, root)
#         menu = CreateMenuBanner(self, controller)
#         menu.set_btn_status('btnDev')
#         menu.grid(row=1, columnspan=3, sticky='W')
#         btnCreate = Button(self, text=' Create New Subscriber', command=lambda: controller.show_frame(root, DpSubs))
#         btnCreate.grid(row=2, column=2)
#         btnDelete = Button(self, text=' Delete Subscriber', command=lambda: controller.show_frame(root, DelSubs))
#         btnDelete.grid(row=3, column=2)






boa = Boa()
boa.mainloop()