from tkinter import *
import tkinter as tk
from tkinter import ttk
import requests
import json
import xml.etree.ElementTree as et

FONT = 'Vandana', 12
offerkey_optionlist = []
# open file
with open('config.json') as f:
    file = json.load(f)
txtfile = open('packagesinfo.txt', 'r')
for line in txtfile:
    offerkey_optionlist.append(line)

# usable class

# dictionary to refer to. Will consist all the data collected from API.
# will be updated within the application each time until the application is destroyed.
# tem_file is to store information needed to send over to the API.
dictionary = {}
temp_file = {}
param_names = {'Household ID' : 'householdId', 'Device ID': 'deviceId', 'Account ID': 'accountId', 'SmartCard ID': 'smartCardId',
                   'Subscriber ID': 'subscriberId', 'Offer Key': 'offerKey', 'Bouquet ID': 'bouquetId',
                   'bssFullType': 'bssFullType', 'Zip Code': 'zipCode', 'Community': 'community',
                   'Authorization Type': 'authorizationType', 'Population ID': 'populationId', 'Currency': 'currency'}


def storeDictionary(param_dict):
    # store data keyed in by the user into a general dictionary
    for k, v in param_dict.items():
        if k == 'offerKey':
            if isinstance(v, int):
                pass
            else:
                v = re.findall('\[([\d]+)\]', v.get_value())
                v = v[0]
            temp_file.update({k: v})
        if isinstance(v, str):
            temp_file.update({k: v})
        else:
            temp_file.update({k: v.get_value()})
            # delete the entry once the data is stored.
            if v.entry.__class__.__name__ == 'Entry':
                v.entry.delete(0, 'end')
    print(temp_file)


def getParam(apinfo):
    # complete the body and url with the right input
    # find the fields needed to replace
    fieldToReplace = re.findall('\{([\w]+)\}', apinfo)
    for item in fieldToReplace:
        if item in temp_file.keys():
            # fill in the parameter
            apinfo = apinfo.replace(''.join(['{', item, '}']), temp_file[item])
    print(apinfo)
    return apinfo


def getSubscriptionsXML(apinfo):
    # create a set of xml to slot in.
    finalXML = ''
    slot = '<subscription><offerKey>{offerKey}</offerKey><authorizationType>SUBSCRIPTION</authorizationType>' \
           '</subscription>'
    offerkeylist = temp_file['offerKey']
    for offerKey in offerkeylist:
        xmltoadd = slot.replace(''.join(['{offerKey}']), offerKey)
        finalXML = ''.join([finalXML, xmltoadd])
    apinfo = apinfo.split('{subscriptions}')
    apinfo = finalXML.join(apinfo)
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
        if 'offerKey' in temp_file.keys():
            xml = getSubscriptionsXML(apinfo['Body'])
        else:
            xml = apinfo['Body']
        param = getParam(xml)
    if apinfo['URL'] != '':
        url = getParam(apinfo['URL'])
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
    branch = tree.find('household')
    # make a dictionary with the first branch in household
    for first in branch:
        # branch with household id, household status etc
        list_of_dict = []
        list_of_dictionary =[]
        temporary_dict = {}
        tempo_dict = {}
        t_dict = {}
        subscription_list = []
        dictionary.update({first.tag: first.text})
        for second in first:
            if first.tag == 'enabledServices':
                list_of_dict.append({second.tag: second.text})
                dictionary.update({first.tag: list_of_dict})
            elif first.tag == 'authorizations':
                for third in range(0, len(second)):
                    t_dict[second[third].tag] = second[third].text
                    tm_dict = {}
                    if second[third].tag != second[third-1]:
                        subscription_list = []
                    for forth in second[third]:
                        tm_dict.update({forth.tag: forth.text})
                    subscription_list.append(tm_dict)
                    t_dict[second[third].tag] = subscription_list
                    if t_dict not in list_of_dictionary:
                        list_of_dictionary.append(t_dict)
                    dictionary.update({first.tag: list_of_dictionary})
            else:
                temporary_dict.update({second.tag: second.text})
                dictionary.update({first.tag: temporary_dict})
                for third in second:
                    tempo_dict.update({third.tag: third.text})
                    dictionary.update({first.tag: {second.tag: tempo_dict}})
    return dictionary

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
        label.grid(row=r, column=2, sticky='W')
        self.entry = None
        self.name = name
        char_text = StringVar()
        if fixed_text is None:
            if widget_type == 'entry_combo':
                self.entry = ttk.Combobox(root)
                self.entry.grid(row=r, column=3)
                self.entry['values'] = optionList
            elif widget_type == 'entry_list':
                scrollbar_goright = Scrollbar(root, orient=HORIZONTAL)
                scrollbar_goright.grid(row=r+1, column=3, sticky='SEW')
                scrollbar_godown = Scrollbar(root, orient=VERTICAL)
                scrollbar_godown.grid(row=r, column=4, sticky='WNS')
                self.entry = Listbox(root, yscrollcommand=scrollbar_godown.set)
                self.entry.config(selectmode='multiple')
                self.entry.grid(row=r, column=3, sticky='W')

                for i in optionList:
                    self.entry.insert(END, i)
                self.entry.grid_columnconfigure(1, weight=0)
                self.entry.grid_rowconfigure(1, weight=0)
                scrollbar_goright.config(command=self.entry.xview)
                scrollbar_godown.config(command=self.entry.yview)
            else:
                self.entry = Entry(root, textvariable=char_text)
                self.entry.grid(row=r, column=3, sticky='W')
        else:
            self.entry = Label(root, text=fixed_text)
            self.entry.grid(row=r, column=3, sticky='W')

    def get_value(self):
        # to get the value of the entry / label so that it can be passed into dictionary
        if self.entry.__class__.__name__ == 'Combobox':
            return self.entry.get()

        elif self.entry.__class__.__name__ == 'Entry':
            return self.entry.get()

        elif self.entry.__class__.__name__ == 'Label':
            return self.entry.cget('text')
        elif self.entry.__class__.__name__ == 'Listbox':
            selection_list = list()
            selection = self.entry.curselection()
            for i in selection:
                entry = self.entry.get(i)
                # take only offer key number
                entry = re.findall('\[([\d]+)\]', entry)
                entry = entry[0]
                selection_list.append(entry)
            return selection_list


class Boa(Tk):
    # the main frame
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.wm_title('BOA Application')
        root = Frame(self, width=250, height=300)
        root.pack(side=RIGHT)
        root.pack_propagate(0)
        root.grid_rowconfigure(0, weight=1)
        # create menu bar for actions
        menu = tk.Menu(root)
        tk.Tk.config(self, menu=menu)
        subMenu = tk.Menu(menu, tearoff=0)
        subDevMenu = tk.Menu(menu, tearoff=0)
        subSubMenu = tk.Menu(menu, tearoff=0)
        subSettMenu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label='Subscriber', menu=subMenu)
        menu.add_cascade(label='Device', menu=subDevMenu)
        menu.add_cascade(label='Settings', menu=subSettMenu)
        menu.add_cascade(label='Subscriptions', menu=subSubMenu)
        subMenu.add_command(label='Create New Subscriber', command=lambda: self.pop_up(CreateSubs, 'Create New Subscriber'))
        subMenu.add_command(label='Suspend/Restore Subscriber',
                            command=lambda: self.pop_up(SusReSubs, 'Suspend/Restore Subscriber'))
        subMenu.add_command(label='Refresh card/Repair Box',
                            command=lambda: self.pop_up(RefreshRepair, 'Refresh card/Repair Box'))
        subMenu.add_command(label='Delete Subscriber', command=lambda: self.pop_up(DelSubs, 'Delete Subscriber'))
        subMenu.add_command(label='Change Ownership', command=lambda: self.pop_up(ChangeOwnership, 'Change Ownership'))
        subSettMenu.add_command(label='Reset Pin', command=lambda: self.pop_up(ResetPin, 'Reset Pin'))
        subSettMenu.add_command(label='Change Bouquet ID', command=lambda: self.pop_up(ChangeBou, 'Change Bouquet ID'))
        subSettMenu.add_command(label='Change Region Key', command=lambda: self.pop_up(ChangeRegKey, 'Change Region Key'))
        subDevMenu.add_command(label='Replace Card', command=lambda: self.pop_up(ReplaceCard, 'Replace Card'))
        subDevMenu.add_command(label='Delete Device', command=lambda: self.pop_up(DelDev, 'Delete Device'))
        subDevMenu.add_command(label='Add Device', command=lambda: self.pop_up(AddDev, 'Add Device'))
        subSubMenu.add_command(label='Add OPPV', command=lambda: self.pop_up(AddOppv, 'Add OPPV'))
        subSubMenu.add_command(label='Delete OPPV', command=lambda: self.pop_up(DelOppv, 'Delete OPPV'))
        subSubMenu.add_command(label='Add Enabler Service',
                               command=lambda: self.pop_up(AddESer, 'Add Enabler Service'))
        subSubMenu.add_command(label='Delete Enabler Service',
                               command=lambda: self.pop_up(DelESer, 'Delete Enabler Service'))
        subSubMenu.add_command(label='Add Single Service',
                               command=lambda: self.pop_up(AddSSer, 'Add Single Service'))
        subSubMenu.add_command(label='Delete Single Service',
                               command=lambda: self.pop_up(DelSSer, 'Delete Single Service'))
        subSubMenu.add_command(label='Modify Service/Replace Offer',
                               command=lambda: self.pop_up(ModSer, 'Modify Service/Replace Offer'))
        subSubMenu.add_command(label='Add Multiple Services',
                               command=lambda: self.pop_up(AddMulSer, 'Add Multiple Services'))

        # create buttons for different sections
        btnSubs = Button(self, text='Subscriber Details', state=NORMAL, name='btnSubs')
        btnSubs.pack(side=TOP, fill=BOTH, expand=1)
        btnDev = Button(self, text='Device(s) & Subscriptions', state=NORMAL, name='btnDev')
        btnDev.pack(side=TOP, fill=BOTH, expand=1)
        btnSett = Button(self, text='Info & Settings', state=NORMAL, name='btnSett')
        btnSett.pack(side=TOP, fill=BOTH, expand=1)

        # swtich frames
        self.frames = {}
        self.show_frame(root, AccountInfo)


    # def enableMenu(self):
    #     if dictionary['householdId'] == '' or 'dictionary' not in dictionary.keys():
    #         count=1
    #         for menu in [self.subMenu, self.subDevMenu, self.subSettMenu]:
    #             menu.component

    def page_arrange(self, root, frame_name):
        # arrange on showing the frame
        frame = frame_name(root, self)
        self.frames[frame_name] = frame
        frame.pack_propagate(0)
        frame.pack(fill=BOTH, expand=1)

    def show_frame(self, root, cont):
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
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Account Info'
        self.update()
        self.update_idletasks()
        param_dict = {}
        logInCredentials = CreateColumn(self, 'Household ID', 2, name='householdId')
        param_dict['householdId'] = logInCredentials
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser())
        logBtn.grid(row=2, column=4, sticky='W')
        Label(self, text='Account info').grid(column=2, columnspan=3)
        param_dict.update({p: CreateColumn(self, p, i + 4, name=param_names[p], fixed_text='') for i, p in
                           enumerate(param_names) if p != 'Household ID' and p != 'Authorization Type'
                           and p != 'Offer Key'})
        refreshBtn= Button(self, text='Update', command=lambda: self.refresh())
        refreshBtn.grid(column=3, sticky='W')

    def logInUser(self):
        parseHouseholdDetails('household.xml')
        self.refresh()

    def refresh(self):
        objectList = self.root.winfo_children()[1].winfo_children()
        for item in range(0, len(objectList)):
            if objectList[item].widgetName == 'label':
                text = objectList[item].cget('text')
                if text in param_names.keys():
                    param = param_names[text]
                    if param in dictionary.keys():
                        objectList[item+1].config(text=dictionary[param])
                    else:
                        selected_branch = dictionary['devices']['device']
                        if param in selected_branch.keys():
                            objectList[item + 1].config(text=selected_branch[param])
                        else:
                            selected_branch = dictionary['locale']
                            if param in selected_branch.keys():
                                objectList[item + 1].config(text=selected_branch[param])
                            else:
                                selected_branch = dictionary['preferences']
                                if param in selected_branch.keys():
                                    objectList[item + 1].config(text=selected_branch[param])


class CreateSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Create New Subscriber'
        param_dict = {}
        param_names = {'Household ID': 'householdId', 'Device ID': 'deviceId', 'Account ID': 'accountId',
                       'SmartCard ID': 'smartCardId', 'Subscriber ID': 'subscriberId',
                       'Bouquet ID': 'bouquetId', 'Zip Code': 'zipCode'}
        param_dict['offerKey'] = CreateColumn(root, 'Offer Key(s)', 16, optionList=offerkey_optionlist, name='offerKey',
                                              widget_type='entry_list')
        param_dict['bssFullType'] = CreateColumn(root, 'bssFullType', 11, optionList=['IVP-DTH-STB', 'IVP-IP-STB'],
                                                 name='bssFullType', widget_type='entry_combo')
        param_dict['community'] = CreateColumn(root, 'Community', 12, name='community', fixed_text='Malaysia Live')
        param_dict['populationId'] = CreateColumn(root, 'Population ID', 13, name='populationId', fixed_text='1')
        param_dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 14, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')
        param_dict['currency'] = CreateColumn(root, 'Currency', 15, name='currency', fixed_text='0528')
        for i, p in enumerate(param_names.keys()):
            item = CreateColumn(root, p, i + 3, name=param_names[p])
            param_dict.update({param_names[p]: item})
        saveButton = Button(root, text='Create', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=18, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=18, column=3, sticky='E')

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
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 1, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 1, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Household Status To Be', 2, optionList=['ACTIVATED', 'SUSPENDED'],
                           name='householdStatus', widget_type='entry_combo')
        param_dict[col.name] = col
        saveButton = Button(root, text='Go', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3, sticky='E')

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class RefreshRepair(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Refresh card/Repair Box'
        param_dict = {}
        msgLabel = Label(root, text='Are you sure you want to refresh card/repair box for the following household ID?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Go', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID that you would like to refresh/repair.')
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col

    def sendApi(self, param_dict):
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
        saveButton = Button(root, text='Yes', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID that you would like to reset pin for.')
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def sendApi(self, param_dict):
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
        saveButton = Button(root, text='Yes', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID for the subscriber that you would like to delete.')
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def sendApi(self, param_dict):
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
        saveButton = Button(root, text='Change', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Bouquet ID (HEX)', 3, name='bouquetId')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
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
        saveButton = Button(root, text='Change', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Zip Code', 3, name='zipCode')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
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
        saveButton = Button(root, text='Change', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'SmartCard ID', 3, name='smartCardId')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        # get deviceId from dictionary or API
        if 'householdId' in dictionary.keys():
            param_dict['deviceId'] = dictionary['devices']['device']['deviceId']
        else:
            parseHouseholdDetails('household.xml')
            param_dict['deviceId'] = dictionary['devices']['device']['deviceId']
        # store info again and call the API
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
        saveButton = Button(root, text='Add', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Offer Key(s)', 3, name='offerKey')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Expiry Date', 4, name='expirationDate')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Authorization Type', 5, name='authorizationType', fixed_text='PPV')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
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
        saveButton = Button(root, text='Delete', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Purchase ID', 3, name='purchaseId')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
        storeDictionary(param_dict)
        getReponse('Remove OPPV - Get')
        getReponse('Remove OPPV - Delete')
        self.root.destroy()


class DelDev(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Device'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Delete', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        if 'devices' in dictionary.keys():
            col = CreateColumn(root, 'Device ID', 3, name='deviceId', fixed_text=dictionary['devices']['device']['deviceId'])
        else:
            col = CreateColumn(root, 'Device ID', 3, name='deviceId')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class AddDev(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add Device'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=7, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=7, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Device ID', 3, name='deviceId')
        param_dict[col.name] = col
        col = CreateColumn(root, 'SmartCard ID', 4, name='smartCardId')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Subscriber ID', 5, name='subscriberId')
        param_dict[col.name] = col
        param_dict['bssFullType'] = CreateColumn(root, 'bssFullType', 6, optionList=['IVP-DTH-STB', 'IVP-IP-STB'],
                                                 name='bssFullType', widget_type='entry_combo')

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class DelSSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Single Service'
        param_dict = {}
        msgLabel = Label(root, text='Fill in the following details.')
        msgLabel.grid(column=2, columnspan=3)
        saveButton = Button(root, text='Go', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Offer Key', 4, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_combo')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
        storeDictionary(param_dict)
        getReponse('Delete Single Service')
        self.root.destroy()


class AddSSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        param_dict = {}
        self.name = 'Add Single Service'
        msgLabel = Label(root, text='Please fill in the below details.')
        msgLabel.grid(column=2, columnspan=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, name='householdId')
            param_dict[col.name] = col
        temp_file['authorizationType'] = 'SUBSCRIPTION'
        col = CreateColumn(root, 'Offer Key', 4, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_combo')
        param_dict[col.name] = col
        saveButton = Button(root, text='Add', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=5, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=5, column=3, sticky='E')

    def sendApi(self, param_dict):
        storeDictionary(param_dict)
        getReponse('Add Single Service')
        self.root.destroy()


class AddESer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add Enabler Service'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Enabler Services', 4, optionList=['PPV_ENABLER', 'PVR_ENABLER', 'VOD_ENABLER'],
                           name='enablerServices',  widget_type='entry_combo')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
        storeDictionary(param_dict)
        getReponse('Add Enabler Service')

        self.root.destroy()


class DelESer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Enabler Service'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Delete', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Enabler Services', 4, optionList=['PPV_ENABLER', 'PVR_ENABLER', 'VOD_ENABLER'],
                           name='enablerServices',  widget_type='entry_combo')
        param_dict[col.name] = col

    def sendApi(self, param_dict):
        storeDictionary(param_dict)
        getReponse('Delete Enabler Service')
        self.root.destroy()

class ChangeOwnership(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Change Ownership'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=13, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=13, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Account ID', 4, name='accountId')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Bouquet ID', 5, name='bouquetId')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Zip Code', 6, name='zipCode')
        param_dict[col.name] = col
        col = CreateColumn(root, 'Offer Key(s)', 11, optionList=offerkey_optionlist, name='offerKey',
                                              widget_type='entry_list')
        param_dict[col.name] = col
        param_dict['community'] = CreateColumn(root, 'Community', 8, name='community', fixed_text='Malaysia Live')
        param_dict['populationId'] = CreateColumn(root, 'Population ID', 9, name='populationId', fixed_text='1')
        param_dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 10, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')
        param_dict['currency'] = CreateColumn(root, 'Currency', 7, name='currency', fixed_text='0528')

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class ModSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Modify Services'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=7, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=7, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, name='householdId')
            param_dict[col.name] = col
        col = CreateColumn(root, 'Offer Key(s)', 5, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_list')
        param_dict[col.name] = col
        param_dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 4, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class AddMulSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add Multiple Services'
        param_dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi(param_dict))
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, name='householdId', fixed_text=dictionary['householdId'])
            param_dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, name='householdId')
            param_dict[col.name] = col
        param_dict['offerKey'] = CreateColumn(root, 'Offer Key(s)', 4, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_list')
        param_dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 3, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')

    def sendApi(self, param_dict):
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()

# make frame for device.


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