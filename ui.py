from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as msgBox
import requests
import json
import xml.etree.ElementTree as et
from datetime import datetime

FONT = 'Vandana', 20
offerkey_optionlist = []
# open file
with open('config.json') as f:
    file = json.load(f)
txtfile = open('packagesinfo.txt', 'r')
for line in txtfile:
    offerkey_optionlist.append(line)


# dictionary to refer to. Will consist all the data collected from API.
# will be updated within the application each time until the application is destroyed.
# tem_file is to store information needed to send over to the API.
dictionary = {}
temp_file = {}
param_names = {'Household ID': 'householdId', 'Device ID': 'deviceId', 'Account ID': 'accountId',
               'SmartCard ID': 'smartCardId', 'Subscriber ID': 'subscriberId', 'Bouquet ID': 'bouquetId',
               'bssFullType': 'bssFullType', 'Zip Code': 'zipCode', 'Community': 'community',
               'Authorization Type': 'authorizationType', 'Population ID': 'populationId', 'Currency': 'currency',
               'Offer Key': 'offerKey', }
device_list = {'Device ID': 'deviceId', 'Device Type': 'deviceType', 'bssFullType': 'bssFullType',
               'Create Date': 'createDate', 'Last Update Date': 'lastUpdateDate', 'Subscriber ID': 'subscriberId',
               'SmartCard ID': 'smartCardId'}


def storeDictionary(param_dict):
    # store data keyed in by the user into a general dictionary
    for k, v in param_dict.items():
        if k == 'offerKey':
            temp_file.update({k: v})
        if isinstance(v, str):
            temp_file.update({k: v})
        else:
            temp_file.update({k: v.get_value()})
    print('temp file', temp_file)


def getParam(apinfo):
    # complete the body and url with the right input
    # find the fields needed to replace
    fieldToReplace = re.findall('\{([\w]+)\}', apinfo)
    for item in fieldToReplace:
        if item in temp_file.keys():
            # fill in the parameter
            apinfo = apinfo.replace(''.join(['{', item, '}']), temp_file[item])
    return apinfo


def getSubscriptionsXML(apinfo):
    # create a set of xml to slot in for offer key.
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
    try:
        if apinfo['Method'] == 'POST':
            response = requests.post(url, param)
        elif apinfo['Method'] == 'PUT':
            response = requests.put(url, param)
        elif apinfo['Method'] == 'GET':
            if param == '':
                response = requests.get(url)
            else:
                response = requests.get(url, param)
        else:
            response = requests.delete(url)
        # show toast message
        res_msg = response.text
        res_msg = res_msg.split('<body>')[0]
        if res_msg.split('<errorMessage>')[1] == '</errorMessage>':
            msgBox.showinfo('Request successful', 'Request successful.')
        else:
            msgBox.showinfo('Request unsuccessful', 'Please make sure the information is correctly filled in.')
    except requests.exceptions.ConnectionError:
        # show toast message
        msgBox.showinfo('CONNECTION ERROR', 'Please make sure you have internet connection.')


# when household API is called, parse the XML into dictionary
def parseHouseholdDetails():
    fileToParse = 'household.xml'
    # fileToParse = getReponse('Household')
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
    def __init__(self, root, label_text, r, c, optionList=[], name="", widget_type=None, fixed_text=None):
        Frame.__init__(self, root)
        label = Label(root, text=label_text, anchor="e")
        label.grid(row=r, column=c, sticky='W')
        self.entry = None
        self.name = name
        char_text = StringVar()
        if fixed_text is None:
            if widget_type == 'entry_combo':
                self.entry = ttk.Combobox(root)
                self.entry.grid(row=r, column=c+1)
                self.entry['values'] = optionList
            elif widget_type == 'entry_list':
                scrollbar_goright = Scrollbar(root, orient=HORIZONTAL)
                scrollbar_goright.grid(row=r+1, column=c+1, sticky='SEW')
                scrollbar_godown = Scrollbar(root, orient=VERTICAL)
                scrollbar_godown.grid(row=r, column=c+2, sticky='WNS')
                self.entry = Listbox(root, yscrollcommand=scrollbar_godown.set)
                self.entry.config(selectmode='multiple')
                self.entry.grid(row=r, column=c+1, sticky='W')

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
            self.entry = Label(root, text=fixed_text, width=20)
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
        self.root = root
        root.pack(side="top", fill="both", expand=True)
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
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

        # swtich frames
        self.frames = {}
        self.show_frame(AccountInfo)

    def arrange_page(self, frame_name):
            # arrange on showing the frame
            frame = frame_name(self.root, self)
            self.frames[frame_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, cont):
        self.arrange_page(cont)
        frame = self.frames[cont]
        frame.tkraise()

    def pop_up(self, frame, title):
        # show pop up windows
        self.newWindow = Toplevel()
        self.newWindow.wm_title(title)
        frame(self.newWindow)


class AccountInfo(Frame):
    # Subscriber page. Account info is empty before log in. Household ID will be needed to log in.
    # create menu page with all the button.
    def __init__(self, root, controller):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Account Info'
        # create buttons for different sections
        # btnSubs = Button(self, text='Subscriber Details', state=NORMAL, name='btnSubs',
        #                  command=lambda: controller.show_frame('AccountInfo'))
        # btnSubs.grid(row=1, column=1, sticky='SNEW', rowspan=5)
        # btnDev = Button(self, text='Device(s) & Subscriptions', state=NORMAL, name='btnDev',
        #                 command=lambda: controller.show_frame('Device'))
        # btnDev.grid(row=6, column=1, sticky='SNEW', rowspan=6)
        # btnSett = Button(self, text='Info & Settings', state=NORMAL, name='btnSett')
        # btnSett.grid(row=12, column=1, sticky='SNEW', rowspan=6)

        # account info page
        self.dict = {}
        Label(self, text='Account info').grid(row=2, column=2, columnspan=3)
        if 'householdId' in dictionary.keys():
            logInCredentials = CreateColumn(self, 'Household ID', 1, 2, name='householdId',
                                            fixed_text=dictionary['householdId'])
            self.dict['householdId'] = logInCredentials
            self.dict.update({p: CreateColumn(self, p, i + 2, 2, name=param_names[p], fixed_text='') for i, p in
                               enumerate(param_names) if p != 'Household ID' and p != 'Authorization Type'
                               and p != 'Offer Key'})
            controller.refresh()
        else:
            logInCredentials = CreateColumn(self, 'Household ID', 1, 2, name='householdId', fixed_text='')
            self.dict['householdId'] = logInCredentials
            self.dict.update({p: CreateColumn(self, p, i + 2, 2, name=param_names[p], fixed_text='') for i, p in
                               enumerate(param_names) if p != 'Household ID' and p != 'Authorization Type'
                               and p != 'Offer Key'})
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser())
        logBtn.grid(row=1, column=4, sticky='W', columnspan=2)
        # refreshBtn= Button(self, text='Update', command=lambda: self.refresh())
        # refreshBtn.grid(row=17, column=3, sticky='W')

        # device page
        Label(self, text='Device & Subscription Information').grid(row=2, column=5, columnspan=3)
        Label(self, text='Device').grid(row=3, column=5, columnspan=3)
        # combobox to select device option
        
        # for i, p in enumerate(device_list.keys()):
        #     col = CreateColumn(self, p, i + 4, 5,  name=device_list[p], fixed_text='')
        #     self.dict[col.name] = col
        # Label(self, text='Device').grid(column=5, columnspan=3)
        # if 'authorizations' in dictionary.keys():
        #     for i, p in enumerate(device_list.keys()):
        #         col = CreateColumn(self, p, i + 12, 5, name=device_list[p], fixed_text=dictionary['devices']['device'][device_list[p]])
        #         self.dict[col.name] = col
        # else:
        #     for i, p in enumerate(device_list.keys()):
        #         col = CreateColumn(self, p, i + 12, 5,  name=device_list[p], fixed_text='')
        #         self.dict[col.name] = col

    def logInUser(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        parseHouseholdDetails()
        self.refresh()

    def refresh(self):
        objectList = self.root.winfo_children()[1].winfo_children()
        for item in range(0, len(objectList)):
            param = ''
            if objectList[item].widgetName == 'label':
                text = objectList[item].cget('text')
                if text in param_names.keys():
                    param = param_names[text]
                elif text in device_list.keys():
                    param = device_list[text]
                if param != '':
                    if param in dictionary.keys():
                        objectList[item + 1].config(text=dictionary[param])
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
        self.dict = {}
        param_names = {'Household ID': 'householdId', 'Device ID': 'deviceId', 'Account ID': 'accountId',
                       'SmartCard ID': 'smartCardId', 'Subscriber ID': 'subscriberId',
                       'Bouquet ID': 'bouquetId', 'Zip Code': 'zipCode'}
        self.dict['offerKey'] = CreateColumn(root, 'Offer Key(s)', 16, 2, optionList=offerkey_optionlist, name='offerKey',
                                              widget_type='entry_list')
        self.dict['bssFullType'] = CreateColumn(root, 'bssFullType', 11, 2, optionList=['IVP-DTH-STB', 'IVP-IP-STB'],
                                                 name='bssFullType', widget_type='entry_combo')
        self.dict['community'] = CreateColumn(root, 'Community', 12, 2, name='community', fixed_text='Malaysia Live')
        self.dict['populationId'] = CreateColumn(root, 'Population ID', 13, 2, name='populationId', fixed_text='1')
        self.dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 14, 2, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')
        self.dict['currency'] = CreateColumn(root, 'Currency', 15, 2, name='currency', fixed_text='0528')
        for i, p in enumerate(param_names.keys()):
            item = CreateColumn(root, p, i + 3, 2, name=param_names[p])
            self.dict.update({param_names[p]: item})
        saveButton = Button(root, text='Create', command=lambda: self.sendApi())
        saveButton.grid(row=18, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=18, column=3, sticky='E')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class SusReSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Suspend/Restore Subscriber'
        self.dict = {}
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 1, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 1, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Household Status To Be', 2, 2, optionList=['ACTIVATED', 'SUSPENDED'],
                           name='householdStatus', widget_type='entry_combo')
        self.dict[col.name] = col
        saveButton = Button(root, text='Go', command=lambda: self.sendApi())
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3, sticky='E')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class RefreshRepair(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Refresh card/Repair Box'
        self.dict = {}
        msgLabel = Label(root, text='Are you sure you want to refresh card/repair box for the following household ID?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Go', command=lambda: self.sendApi())
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID that you would like to refresh/repair.')
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class ResetPin(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Reset Pin'
        self.dict = {}
        msgLabel = Label(root, text='Are you sure you want to reset pin for the following household ID?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Yes', command=lambda: self.sendApi())
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID that you would like to reset pin for.')
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class DelSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Subscriber'
        self.dict = {}
        msgLabel = Label(root, text='Are you sure you want to delete the following subscriber?')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Yes', command=lambda: self.sendApi())
        saveButton.grid(row=3, column=3, sticky='W')
        cancelButton = Button(root, text='No', command=lambda: self.root.destroy())
        cancelButton.grid(row=3, column=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            msgLabel.config(text='Please enter the household ID for the subscriber that you would like to delete.')
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
            saveButton.config(text='Go')
            cancelButton.config(text='Cancel')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class ChangeBou(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Change Bouquet ID'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi())
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Bouquet ID (HEX)', 3, 2, name='bouquetId')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class ChangeRegKey(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Change Region Key'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi())
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Zip Code', 3, 2, name='zipCode')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class ReplaceCard(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Replace Card'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi())
        saveButton.grid(row=4, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'SmartCard ID', 3, 2, name='smartCardId')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        # get deviceId from dictionary or API
        if 'householdId' in dictionary.keys():
            self.dict['deviceId'] = dictionary['devices']['device']['deviceId']
        else:
            parseHouseholdDetails()
            self.dict['deviceId'] = dictionary['devices']['device']['deviceId']
        # store info again and call the API
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


class AddOppv(Frame):
    def __init__(self, root):
        time_set = []
        month_list = []
        day_list =[]
        current_year = datetime.now().year
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add OPPV'
        self.date = ''
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi())
        saveButton.grid(row=9, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=9, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Offer Key(s)', 3, 2, optionList=offerkey_optionlist, name='offerKey', widget_type='entry_combo')
        self.dict[col.name] = col
        # expiry date
        date_label = Label(root, text='Expiry Date(Year)')
        date_label.grid(row=4, column=2, sticky='W')
        self.year = ttk.Combobox(root)
        self.year.grid(row=4, column=3)
        self.year['values'] = [current_year + i for i in range(0, 20)]
        Label(root, text='Expiry Date(Month)').grid(row=5, column=2, sticky='W')
        self.month = ttk.Combobox(root)
        self.month.grid(row=5, column=3, sticky='W')
        for i in range(1, 13):
            if len(str(i)) == 1:
                str_i = ''.join([str(0), str(i)])
            else:
                str_i = str(i)
            month_list.append(str_i)
        self.month['values'] = month_list
        Label(root, text='Expiry Date(Day)').grid(row=6, column=2, sticky='W')
        self.day = ttk.Combobox(root)
        self.day.grid(row=6, column=3, sticky='W')
        for i in range(1, 32):
            if len(str(i)) == 1:
                str_i = ''.join([str(0), str(i)])
            else:
                str_i = str(i)
            day_list.append(str_i)
        self.day['values'] = day_list
        # expiry time
        Label(root, text='Expiry Time').grid(row=7, column=2, sticky='W')
        self.time = ttk.Combobox(root)
        self.time.grid(row=7, column=3, sticky='W')
        for i in range(0, 25):
            for j in range(0, 60):
                if len(str(i)) == 1:
                    str_i = ''.join([str(0), str(i)])
                else:
                    str_i = str(i)
                if len(str(j)) == 1:
                    str_j = ''.join([str(0), str(j)])
                else:
                    str_j = str(j)
                time = ''.join([str_i, ':', str_j, ':', '00'])
                time_set.append(time)
        self.time['values'] = time_set
        col = CreateColumn(root, 'Authorization Type', 8, 2, name='authorizationType', fixed_text='PPV')
        self.dict[col.name] = col

    def sendApi(self):
        self.date = ''.join([self.year.get(), '-', self.month.get(), '-', self.day.get()])
        self.time_toset = ''.join(['T', self.time.get(), 'Z'])
        self.dict['expirationDate'] = ''.join([self.date, self.time_toset])
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class DelOppv(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Remove OPPV'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Delete', command=lambda: self.sendApi())
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Purchase ID', 3, 2, name='purchaseId')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        getReponse('Remove OPPV - Get')
        response = getReponse('Remove OPPV - Delete')
        print(response)
        self.root.destroy()


class DelDev(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Device'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Delete', command=lambda: self.sendApi())
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        if 'devices' in dictionary.keys():
            col = CreateColumn(root, 'Device ID', 3, 2, name='deviceId', fixed_text=dictionary['devices']['device']['deviceId'])
        else:
            col = CreateColumn(root, 'Device ID', 3, 2, name='deviceId')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class AddDev(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add Device'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi())
        saveButton.grid(row=7, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=7, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Device ID', 3, 2, name='deviceId')
        self.dict[col.name] = col
        col = CreateColumn(root, 'SmartCard ID', 4, 2, name='smartCardId')
        self.dict[col.name] = col
        col = CreateColumn(root, 'Subscriber ID', 5, 2, name='subscriberId')
        self.dict[col.name] = col
        self.dict['bssFullType'] = CreateColumn(root, 'bssFullType', 6, 2, optionList=['IVP-DTH-STB', 'IVP-IP-STB'],
                                                 name='bssFullType', widget_type='entry_combo')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class DelSSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Single Service'
        self.dict = {}
        msgLabel = Label(root, text='Fill in the following details.')
        msgLabel.grid(column=2, columnspan=3)
        saveButton = Button(root, text='Go', command=lambda: self.sendApi())
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Offer Key', 4, 2, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_combo')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        response = getReponse('Delete Single Service')
        print(response)
        self.root.destroy()


class AddSSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.dict = {}
        self.name = 'Add Single Service'
        msgLabel = Label(root, text='Please fill in the below details.')
        msgLabel.grid(column=2, columnspan=3)
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId')
            self.dict[col.name] = col
        temp_file['authorizationType'] = 'SUBSCRIPTION'
        col = CreateColumn(root, 'Offer Key', 4, 2, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_combo')
        self.dict[col.name] = col
        saveButton = Button(root, text='Add', command=lambda: self.sendApi())
        saveButton.grid(row=5, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=5, column=3, sticky='E')

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        response = getReponse('Add Single Service')
        print(response)
        self.root.destroy()


class AddESer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add Enabler Service'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi())
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Enabler Services', 4, 2, optionList=['PPV_ENABLER', 'PVR_ENABLER', 'VOD_ENABLER'],
                           name='enablerServices',  widget_type='entry_combo')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        getReponse('Add Enabler Service')

        self.root.destroy()


class DelESer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Delete Enabler Service'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Delete', command=lambda: self.sendApi())
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Enabler Services', 4, 2, optionList=['PPV_ENABLER', 'PVR_ENABLER', 'VOD_ENABLER'],
                           name='enablerServices',  widget_type='entry_combo')
        self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        response = getReponse('Delete Enabler Service')
        print(response)
        self.root.destroy()


class ChangeOwnership(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Change Ownership'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi())
        saveButton.grid(row=13, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=13, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Account ID', 4, 2, name='accountId')
        self.dict[col.name] = col
        col = CreateColumn(root, 'Bouquet ID', 5, 2, name='bouquetId')
        self.dict[col.name] = col
        col = CreateColumn(root, 'Zip Code', 6, 2, name='zipCode')
        self.dict[col.name] = col
        col = CreateColumn(root, 'Offer Key(s)', 11, 2, optionList=offerkey_optionlist, name='offerKey',
                                              widget_type='entry_list')
        self.dict[col.name] = col
        self.dict['community'] = CreateColumn(root, 'Community', 8, 2, name='community', fixed_text='Malaysia Live')
        self.dict['populationId'] = CreateColumn(root, 'Population ID', 9, 2, name='populationId', fixed_text='1')
        self.dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 10, 2, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')
        self.dict['currency'] = CreateColumn(root, 'Currency', 7, 2, name='currency', fixed_text='0528')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class ModSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Modify Services'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Change', command=lambda: self.sendApi())
        saveButton.grid(row=7, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=7, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 3, 2, name='householdId')
            self.dict[col.name] = col
        col = CreateColumn(root, 'Offer Key(s)', 5, 2, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_list')
        self.dict[col.name] = col
        self.dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 4, 2, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')

    def sendApi(self):
        widget_name = self.name
        param_dict = self.dict
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()


class AddMulSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add Multiple Services'
        self.dict = {}
        msgLabel = Label(root, text='Key in the following details.')
        msgLabel.grid(column=2, columnspan=2)
        saveButton = Button(root, text='Add', command=lambda: self.sendApi())
        saveButton.grid(row=6, column=3, sticky='W')
        cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        cancelButton.grid(row=6, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
        else:
            col = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[col.name] = col
        self.dict['offerKey'] = CreateColumn(root, 'Offer Key(s)', 4, 2, optionList=offerkey_optionlist, name='offerKey',
                           widget_type='entry_list')
        self.dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 3, 2, name='authorizationType',
                                                       fixed_text='SUBSCRIPTION')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        response = getReponse(widget_name)
        print(response)
        self.root.destroy()

# make frame for device.


class Device(Frame):
    # create menu page with all the button.
    def __init__(self, root, controller):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Device & Subscriptions'
        # create buttons for different sections
        # btnSubs = Button(self, text='Subscriber Details', state=NORMAL, name='btnSubs',
        #                  command=lambda: controller.show_frame('AccountInfo'))
        # btnSubs.grid(row=1, column=1, sticky='SNEW', rowspan=5)
        # btnDev = Button(self, text='Device(s) & Subscriptions', state=NORMAL, name='btnDev',
        #                 command=lambda: controller.show_frame('Device'))
        # btnDev.grid(row=6, column=1, sticky='SNEW', rowspan=6)
        # btnSett = Button(self, text='Info & Settings', state=NORMAL, name='btnSett')
        # btnSett.grid(row=12, column=1, sticky='SNEW', rowspan=6)

        # device info page
        self.dict = {}

        refreshBtn= Button(self, text='Update', command=lambda: controller.refresh())
        refreshBtn.grid(row=17, column=3, sticky='W')

    def logInUser(self, controller):
        param_dict = self.dict
        storeDictionary(param_dict)
        parseHouseholdDetails()
        controller.refresh()





boa = Boa()
boa.mainloop()