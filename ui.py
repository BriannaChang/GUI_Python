from tkinter import *
import tkinter as tk
import requests
import json
import xml.etree.ElementTree as et

FONT = 'Vandana', 12

# open file
with open('config.json') as f:
    file = json.load(f)

# usable class

# dictionary to refer to. Will consist all the data collected from API.
# will be updated within the application each time until the application is destroyed.
# tem_file is to store information needed to send over to the API.
dictionary = {}
temp_file = {}


def storeDictionary(param_dict):
    # store data keyed in by the user into a general dictionary
    for k, v in param_dict.items():
        temp_file.update({k: v.get_value()})
        # delete the entry once the data is stored.
        if v.entry.__class__.__name__ == 'Entry':
            v.entry.delete(0, 'end')
    return temp_file


def getParam(apinfo):
    print(temp_file)
    # complete the body and url with the right input
    # find the fields needed to replace
    fieldToReplace = re.findall('\{([\w]+)\}', apinfo)
    for item in fieldToReplace:
        if item in temp_file.keys():
            # fill in the parameter
            apinfo = apinfo.replace(''.join(['{', item, '}']), temp_file[item])
    return apinfo


def getReponse(widget_name):
    apinfo = {}
    param = ''
    url = ''
    # send XML file to URL accordingly.
    for item in file.keys():
        if item == widget_name:
            apinfo = file[item]
    if apinfo['Body'] != '':
        param = getParam(apinfo['Body'])
    if apinfo['URL'] != '':
        url = getParam(apinfo['URL'])
    print('body', param, 'url', url)
    # if apinfo['Method'] == 'POST':
    #     response = requests.post(url, param)
    # elif apinfo['Method'] == 'PUT':
    #     response = requests.put(url, param)
    # elif apinfo['Method'] == 'GET':
    #     response = requests.get(url, param)
    # else:
    #     response = requests.delete(url)
    # return response.text

# when household API is called, parse the XML into dictionary


def parseHouseholdDetails(xml):
    fileToParse = xml
    tree = et.parse(fileToParse)
    # find the element to look into
    root = tree.find('household')
    for child in root:
        # get the name of the element and fill it into the dictionary.
        for key in dictionary.keys():
            if dictionary[key]['key'] == child.tag:
                dictionary[key]['value'] = child.text
            else:
                for grand in child:
                    if dictionary[key]['key'] == grand.tag:
                        dictionary[key]['value'] = grand.text
                    else:
                        for ggrand in grand:
                            if dictionary[key]['key'] == ggrand.tag:
                                dictionary[key]['value'] = ggrand.text
                # to cater for multi offer
                # if grand.tag == 'subscription':
    print(dictionary)

# Create text box to avoid repetitive codes.


class CreateColumn(Frame):
    # label text is for the name of the column
    # optionList is the list for scrolling options
    # name is for the widget naming
    # widget_type is to indicate when listing is needed.
    # fixed_text is to differentiate to use entry or label column.
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

    def get_value(self):
        # to get the value of the entry / label so that it can be passed into dictionary
        if self.entry.__class__.__name__ == 'Listbox':
            return self.entry.get(self.entry.curselection())

        elif self.entry.__class__.__name__ == 'Entry':
            return self.entry.get()

        elif self.entry.__class__.__name__ == 'Label':
            return self.entry.cget('text')


class Boa(Tk):
    # the main frame
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.wm_title('BOA Application')
        root = Frame(self, width=1080, height=720)
        root.pack(side=RIGHT)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(1, weight=1)
        # create options for actions
        menu = tk.Menu(root)
        tk.Tk.config(self, menu=menu)
        subMenu = tk.Menu(menu)
        menu.add_cascade(label='Option', menu=subMenu)
        subMenu.add_command(label='Create New Subscriber', command=lambda: self.pop_up(CreateSubs, 'Create New Subscriber'))
        subMenu.add_command(label='Suspend/Restore Subscriber', command=lambda: self.pop_up(SusReSubs, 'Suspend/Restore Subscriber' ))
        subMenu.add_command(label='Refresh card/Repair Box', command=lambda: self.pop_up(RefreshRepair, 'Refresh card/Repair Box'))
        subMenu.add_command(label='Reset Pin', command=lambda: self.pop_up(ResetPin, 'Reset Pin'))
        subMenu.add_command(label='Delete Subscriber', command=lambda: self.pop_up(DelSubs, 'Delete Subscriber'))
        subMenu.add_command(label='Change Bouquet ID', command=lambda: self.pop_up(ChangeBou, 'Change Bouquet ID'))
        subMenu.add_command(label='Change Region Key', command=lambda: self.pop_up(ChangeRegKey, 'Change Region Key'))
        subMenu.add_command(label='Replace Card', command=lambda: self.pop_up(ReplaceCard, 'Replace Card'))
        subMenu.add_command(label='Add OPPV', command=lambda: self.pop_up(AddOppv, 'Add OPPV'))
        subMenu.add_command(label='Delete OPPV', command=lambda: self.pop_up(DelOppv, 'Delete OPPV'))
        self.frames = {}
        # create buttons for different section
        btnSubs = Button(self, text='Subscriber', state=NORMAL, name='btnSubs')
        btnSubs.pack(side=TOP)
        btnDev = Button(self, text='Device', state=NORMAL, name='btnDev')
        btnDev.pack(side=TOP)
        btnSett = Button(self, text='Settings', state=NORMAL, name='btnSett')
        btnSett.pack(side=TOP)
        self.set_btn_status('btnSubs')
        self.show_frame(root, AccountInfo)

    def set_btn_status(self, btn: object) -> object:
        # disabled that button when user clicks on that frame
        self.nametowidget(btn).config(state=DISABLED)

    def page_arrange(self, root, frame_name):
        # arrange on showing the frame
        frame = frame_name(root, self)
        self.frames[frame_name] = frame
        frame.pack(side=LEFT)

    def show_frame(self, root, cont):
        # show the frame. If there is a dictionary, key in the values first.
        self.page_arrange(root, cont)
        frame = self.frames[cont]
        frame.tkraise()

    def pop_up(self, frame, title):
        # show pop up windows
        self.newWindow = Toplevel()
        self.newWindow.wm_title(title)
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
        param_dict = {}
        logInCredentials = CreateColumn(self, 'Household ID', 2, name='householdId')
        param_dict['householdId'] = logInCredentials
        # dictionary.update({'Household ID': {'key': 'householdId', 'value': ""}})
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser())
        logBtn.grid(row=2, column=4, sticky='W')
        Label(self, text='Account info').grid(column=2, columnspan=3)
        param_names ={'Device ID': 'deviceId', 'Account ID': 'accountId', 'SmartCard ID': 'smartCardId',
                      'Subscriber ID': 'subscriberId', 'Offer Key': 'offerKey', 'Bouquet ID': 'bouquetId',
                      'bssFullType': 'bssFullType', 'Zip Code': 'zipCode', 'Community': 'community',
                      'Authorization Type': 'authorizationType', 'Population ID': 'populationId', 'Currency': 'currency'}
        # temp_file.update({k: {'key': v, 'value': ""} for k, v in param_names.items()})
        param_dict.update({p: CreateColumn(self, p, i + 4, name=param_names[p], fixed_text='') for i, p in enumerate(param_names)})
        refreshBtn= Button(self, text='Update', command=lambda: self.refresh())
        refreshBtn.grid(column=3, sticky='W')

    def logInUser(self):
        parseHouseholdDetails('household.xml')
        self.refresh()

    def refresh(self):
        objectList = self.root.winfo_children()[1].winfo_children()
        for item in range(0, len(objectList)):
            if objectList[item].widgetName == 'label':
                param = objectList[item].cget('text')
                if param in dictionary.keys():
                    objectList[item+1].config(text=dictionary['value'])


class CreateSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Create New Subscriber'
        param_dict = {}
        param_names = {'Household ID': 'householdId', 'Device ID': 'deviceId', 'Account ID': 'accountId',
                       'SmartCard ID': 'smartCardId', 'Subscriber ID': 'subscriberId', 'Offer Key': 'offerKey',
                       'Bouquet ID': 'bouquetId', 'Zip Code': 'zipCode'}
        # temp_file['Community']['value'] = 'Malaysia Live'
        # temp_file['Population ID'] = {'key': 'populationId', 'value': 1}
        # temp_file['Currency'] = {'key': 'currency', 'value': '0458'}
        param_dict['community'] = CreateColumn(root, 'Community', 12, name='community', fixed_text='Malaysia Live')
        param_dict['populationId'] = CreateColumn(root, 'Population ID', 13, name='populationId', fixed_text='1')
        param_dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 14, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')
        param_dict['currency'] = CreateColumn(root, 'Currency', 15, name='currency', fixed_text='0528')
        for i, p in enumerate(param_names.keys()):
            item = CreateColumn(root, p, i + 3, name=param_names[p])
            param_dict.update({param_names[p]: item})
        param_dict['bssFullType'] = CreateColumn(root, 'bssFullType', 16, optionList=['IVP-DTH-STB', 'IVP-IP-STB'],
                                                 name='bssFullType', widget_type='entry_list')
        saveButton = Button(root, text='Create', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=17, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=17, column=3, sticky='E')

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class SusReSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Suspend/Restore Subscriber'
        param_dict = {}
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 1, name='householdId', fixed_text=dictionary['householdId']['value'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 1, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Household Status To Be', 2, optionList=['ACTIVATED', 'SUSPENDED'],
                           name='householdStatus', widget_type='entry_list')
        param_dict[col.name] = col
        saveButton = Button(root, text='Go', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3, sticky='E')

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class RefreshRepair(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Suspend/Restore Subscriber'
        param_dict = {}
        msgLabel = Label(root, text='Are you sure you want to refresh card/repair box for the following household ID?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Yes', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID that you would like to refresh/repair.')
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class ResetPin(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Reset Pin'
        param_dict = {}
        msgLabel = Label(root, text='Are you sure you want to reset pin for the following household ID?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Yes', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID that you would like to reset pin for.')
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class DelSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Subscriber'
        param_dict = {}
        msgLabel = Label(root, text='Are you sure you want to delete the following subscriber?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Yes', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID for the subscriber that you would like to delete.')
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class ChangeBou(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Change Bouquet ID'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Bouquet ID (HEX)', 3, name='bouquetId')
        param_dict[col.name] = col

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class ChangeRegKey(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Change Region Key'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Zip Code', 3, name='zipCode')
        param_dict[col.name] = col

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class ReplaceCard(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Replace Card'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'SmartCard ID', 3, name='smartCardId')
        param_dict[col.name] = col

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class AddOppv(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add OPPV'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Offer Key', 3, name='offerKey')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Expiry Date', 4, name='expirationDate')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Authorization Type', 5, name='authorizationType', fixed_text='PPV')
        param_dict[col.name] = col

    def refresh(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class DelOppv(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Remove OPPV'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Delete', command=lambda: self.refresh(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'Household ID' in dictionary.keys() and dictionary['Household ID']['value'] != '':
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['Household ID']['value'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Purchase ID', 3, name='purchaseId')
        param_dict[col.name] = col

    def refresh(self, param_dict):
        storeDictionary(param_dict)
        getReponse('Remove OPPV - Get')
        getReponse('Remove OPPV - Delete')
        self.root.destroy()

class Device(Frame):
    # create menu page with all the button.
    def __init__(self, root):
        Frame.__init__(self, root)
        self.name = 'Device'
        self.root = root
        self.update()
        self.update_idletasks()
        logInCredentials = CreateColumn(self, 'Household ID', 2)
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
        createBtn = Button(self, text='Add More device', command=lambda: self.pop_up(CreateSubs))
        createBtn.grid(row=17, column=3, sticky='W')

    def logInUser(self, param):
        widget_name = 'Log in'
        storeDictionary(param)
        getReponse(AccountInfo, widget_name)
        self.update()
        self.update_idletasks()

    def pop_up(self, frame):
        self.newWindow = Toplevel()
        self.newWindow.wm_title('Create New Subscriber')
        frame(self.newWindow)


boa = Boa()
boa.mainloop()