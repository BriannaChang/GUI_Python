from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import font
import tkinter.messagebox as msgBox
import requests
import json
import xml.etree.ElementTree as et
from datetime import datetime
import os

# change directory file
os.chdir('C:\\Users\\Admin\\Desktop\\boa_ui')

FONT = 'Vandana', 20
authorizationId_optionlist = []
authorizationId_dict = {}
# open file
with open('config.json') as config:
    file = json.load(config)
txtfile = open('packagesinfo.txt')
for line in txtfile:
    offer_key = re.findall('\[([\d]+)\]', line)[0]
    textToShow = line.split(''.join(['[', offer_key, ']']))[1]
    authorizationId_optionlist.append(textToShow[:-1])
    authorizationId_dict.update({offer_key: textToShow[:-1]})
# dictionary to refer to. Will consist all the data collected from API.
# will be updated within the application each time until the application is destroyed.
# tem_file is to store information needed to send over to the API.
dictionary = {}
temp_file = {}
param_names = {'Household ID': 'householdId', 'Household Status': 'householdStatus', 'Device ID': 'deviceId', 'Account ID': 'accountId',
               'SmartCard ID': 'smartCardId', 'Subscriber ID': 'subscriberId', 'Bouquet ID': 'bouquetId',
               'bssFullType': 'bssFullType', 'Zip Code': 'zipCode', 'Community': 'community',
               'Population ID': 'populationId', 'Currency': 'currency', 'Authorization Type': 'authorizationType',
               'Authorization ID': 'authorizationId', }
device_list = {'Device ID': 'deviceId', 'bssFullType': 'bssFullType',
               'Create Date': 'createDate', 'Last Update Date': 'lastUpdateDate', 'Subscriber ID': 'subscriberId',
               'SmartCard ID': 'smartCardId'}


def storeDictionary(param_dict):
    # store data keyed in by the user into a general dictionary
    for k, v in param_dict.items():
        if isinstance(v, str):
            temp_file.update({k: v})
        else:
            value_check = v.get_value()
            if k == 'authorizationId':
                if isinstance(value_check, list) or isinstance(value_check, int):
                    temp_file.update({k: value_check})
                else:
                    # take Authorization ID number
                    for key in authorizationId_dict.keys():
                        if value_check == authorizationId_dict[key]:
                            temp_file.update({k: key})
            else:
                temp_file.update({k: value_check})

    # validation before send out
    details = []
    wrong_len = []
    validation_list = {'householdId': 8, 'accountId': 8, 'deviceId': 12, 'smartCardId': 12, 'subscriberId': 9,
                       'bouquetId': 4,
                       'zipCode': 8}
    for key, entry in temp_file.items():
        if entry == '' or entry is None:
            details.append(key)
        else:
            # check validation
            if key in validation_list.keys():
                if len(entry) != validation_list[key]:
                    wrong_len.append({key: validation_list[key]})
    if details:
        final_string = ''
        for item in details:
            info = ''.join([str(item), '\n'])
            final_string = final_string.join([info, ' '])
        msgBox.showinfo('INCOMPLETE', 'Please fill in the following details: \n '
                                      '{}'.format(final_string))
        raise ValueError
    if wrong_len:
        final_string = ''
        for item in wrong_len:
            info = ''.join([str(item)[2:-1], ' ', 'characters', '\n'])
            final_string = final_string.join([info, ' '])
        msgBox.showinfo('INCOMPLETE', 'Please fill in the details with the correct number of characters: \n'
                                      ' {}'.format(final_string))
        raise ValueError


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
    # create a set of xml to slot in for Authorization ID.
    finalXML = ''
    slot = '<subscription><authorizationId>{authorizationId}</authorizationId><authorizationType>SUBSCRIPTION</authorizationType>' \
           '</subscription>'
    authorizationIdlist = temp_file['authorizationId']
    for authorizationId in authorizationIdlist:
        xmltoadd = slot.replace(''.join(['{authorizationId}']), authorizationId)
        finalXML = ''.join([finalXML, xmltoadd])
    apinfo = apinfo.split('{subscriptions}')
    apinfo = finalXML.join(apinfo)
    return apinfo


def getReponse(widget_name):
    headers = {'Content-Type': 'text/xml'}
    apinfo = {}
    param = ''
    url = ''
    # send XML file to URL accordingly.
    for item in file.keys():
        if item == widget_name:
            apinfo = file[item]
    if apinfo['Body'] != '':
        if 'authorizationId' in temp_file.keys():
            xml = getSubscriptionsXML(apinfo['Body'])
        else:
            xml = apinfo['Body']
        param = getParam(xml)
    if apinfo['URL'] != '':
        url = getParam(apinfo['URL'])
    print('Sending requests to:', url, '\n', 'with XML FILE (if any):', param)
    try:
        if apinfo['Method'] == 'POST':
            if param == '':
                response = requests.post(url, headers=headers)
            else:
                response = requests.post(url, data=param, headers=headers)
        elif apinfo['Method'] == 'PUT':
            response = requests.put(url, data=param, headers=headers)
        elif apinfo['Method'] == 'GET':
            if param == '':
                response = requests.get(url, headers=headers)
            else:
                response = requests.get(url, data=param, headers=headers)
        else:
            response = requests.delete(url, headers=headers)
        # show toast message
        res_msg = response.text
        print('Request result', res_msg)
        toastMessage(res_msg, widget_name)
        return res_msg

    except requests.exceptions.ConnectionError:
        # show toast message
        msgBox.showinfo('CONNECTION ERROR', 'Please make sure you have internet connection.')


def toastMessage(res_msg, widget_name):
    res_msg = et.fromstring(res_msg)
    res_msg_error = res_msg.find('errorMessage')
    if res_msg_error.text:
        msgBox.showinfo('REQUEST UNSUCCESSFUL', res_msg_error.text)
        raise SystemError
    else:
        if widget_name != 'Household':
            msgBox.showinfo('Request successful', 'Request successful. Please click \"update page\" to '
                                                      'see the changes.')
        return True


# when household API is called, parse the XML into dictionary
def parseHouseholdDetails():
    # clear dictionary
    dictionary.clear()
    apinfo = file['Household']
    url = getParam(apinfo['URL'])
    print('Sending requests to:', url)
    res_msg = requests.get(url, headers={'Content-Type': 'text/xml'}).text
    print('result', res_msg)
    if toastMessage(res_msg, 'Household'):
        tree = et.fromstring(res_msg)
        branch = tree.find('household')
        # make a dictionary with the first branch in household
        for first in branch:
            # branch with household id, household status etc
            list_of_dict = []
            temporary_dict = {}
            tempo_dict = {}
            dictionary.update({first.tag: first.text})
            for second in first:
                if first.tag == 'enabledServices':
                    list_of_dict.append({second.tag: second.text})
                    dictionary.update({first.tag: list_of_dict})
                elif first.tag != 'authorizations' and first.tag != 'devices':
                    temporary_dict.update({second.tag: second.text})
                    dictionary.update({first.tag: temporary_dict})
                    for third in second:
                        tempo_dict.update({third.tag: third.text})
                        dictionary.update({first.tag: {second.tag: tempo_dict}})
        # for authorization
        author_branch = branch.find('authorizations')
        subscriptions_list = author_branch.find('subscriptions')
        list_subs = []
        for subs in subscriptions_list:
            dict_text = {}
            for det in subs:
                text = {det.tag: det.text}
                dict_text.update(text)
            list_subs.append(dict_text)
        # same goes to to titles
        title_list = author_branch.find('titles')
        list_title = []
        for til in title_list:
            dict_text = {}
            for det in til:
                text = {det.tag: det.text}
                dict_text.update(text)
            list_title.append(dict_text)
        # update dictionary
        author_dict = {}
        author_dict.update({'subscriptions': {'subscription': list_subs}, 'titles': list_title})
        dictionary.update({'authorizations': author_dict})
        # same goes to devices
        device_branch = branch.find('devices')
        list_dev = []
        for dev in device_branch:
            dict_text = {}
            for det in dev:
                text = {det.tag: det.text}
                dict_text.update(text)
            list_dev.append(dict_text)
        # update dictionary
        dictionary.update({'devices': list_dev})
        print('\n', 'data', dictionary)
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
        label = Label(root, text=label_text, justify='left', wraplength=100)
        label.grid(row=r, column=c, sticky='W')
        self.entry = None
        self.name = name
        char_text = StringVar()
        if fixed_text is None:
            if widget_type == 'entry_combo':
                self.entry = ttk.Combobox(root)
                self.entry.grid(row=r, column=c + 1)
                self.entry['values'] = optionList
            elif widget_type == 'entry_list':
                scrollbar_goright = Scrollbar(root, orient=HORIZONTAL)
                scrollbar_goright.grid(row=r + 1, column=c + 1, sticky='SEW')
                scrollbar_godown = Scrollbar(root, orient=VERTICAL)
                scrollbar_godown.grid(row=r, column=c + 2, sticky='WNS')
                self.entry = Listbox(root, yscrollcommand=scrollbar_godown.set)
                self.entry.config(selectmode='multiple')
                self.entry.grid(row=r, column=c + 1, sticky='W')

                for i in optionList:
                    self.entry.insert(END, i)
                self.entry.grid_columnconfigure(1, weight=0)
                self.entry.grid_rowconfigure(1, weight=0)
                scrollbar_goright.config(command=self.entry.xview)
                scrollbar_godown.config(command=self.entry.yview)
            else:
                self.entry = Entry(root, textvariable=char_text)
                self.entry.grid(row=r, column=c + 1, sticky='W')
        else:
            self.entry = Label(root, text=fixed_text, anchor='w', wraplength=180)
            self.entry.grid(row=r, column=c + 1, sticky='W')

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
                # take Authorization ID number
                for key in authorizationId_dict.keys():
                    if entry == authorizationId_dict[key]:
                        selection_list.append(key)
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
        subMenu.add_command(label='Create New Subscriber',
                            command=lambda: self.pop_up(CreateSubs, 'Create New Subscriber', root))
        subMenu.add_command(label='Suspend/Restore Subscriber',
                            command=lambda: self.pop_up(SusReSubs, 'Suspend/Restore Subscriber', root))
        subMenu.add_command(label='Refresh card/Repair Box',
                            command=lambda: self.pop_up(RefreshRepair, 'Refresh card/Repair Box', root))
        subMenu.add_command(label='Delete Subscriber', command=lambda: self.pop_up(DelSubs, 'Delete Subscriber', root))
        subMenu.add_command(label='Change Ownership',
                            command=lambda: self.pop_up(ChangeOwnership, 'Change Ownership', root))
        subSettMenu.add_command(label='Reset Pin', command=lambda: self.pop_up(ResetPin, 'Reset Pin', root))
        subSettMenu.add_command(label='Change Bouquet ID',
                                command=lambda: self.pop_up(ChangeBou, 'Change Bouquet ID', root))
        subSettMenu.add_command(label='Change Region Key',
                                command=lambda: self.pop_up(ChangeRegKey, 'Change Region Key', root))
        subDevMenu.add_command(label='Replace Card', command=lambda: self.pop_up(ReplaceCard, 'Replace Card', root))
        subDevMenu.add_command(label='Add/Delete Device',
                               command=lambda: self.pop_up(AddDelDev, 'Add/Delete Device', root))
        subSubMenu.add_command(label='Add/Delete OPPV',
                               command=lambda: self.pop_up(AddDelOppv, 'Add/Delete OPPV', root))
        subSubMenu.add_command(label='Add/Delete Enabler Service',
                               command=lambda: self.pop_up(AddDelESer, 'Add/Delete Enabler Service', root))
        subSubMenu.add_command(label='Add/Delete Single Service',
                               command=lambda: self.pop_up(AddDelSSer, 'Add/Delete Single Service', root))
        subSubMenu.add_command(label='Modify Service/Replace Offer',
                               command=lambda: self.pop_up(ModSer, 'Modify Service/Replace Offer', root))
        subSubMenu.add_command(label='Add Multiple Services',
                               command=lambda: self.pop_up(AddMulSer, 'Add Multiple Services', root))

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

    def pop_up(self, frame, title, root):
        # show pop up windows
        self.newWindow = Toplevel(padx=10, pady=10)
        self.newWindow.wm_title(title)
        self.newWindow.transient(master=root)
        self.newWindow.geometry('+400+250')
        frame(self.newWindow)


class AccountInfo(Frame):
    # Subscriber page. Account info is empty before log in. Household ID will be needed to log in.
    # create menu page with all the button.
    def __init__(self, root, controller):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Account Info'
        # account info page
        self.dict = {}
        label = Label(self, text='Account info', font='bold')
        label.grid(row=2, column=2, columnspan=3)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        self.logInCredentials = CreateColumn(self, 'Household ID', 1, 2, name='householdId')
        [CreateColumn(self, p, i + 2, 2, name=param_names[p], fixed_text='') for i, p in
         enumerate(param_names) if p != 'Household ID' and p != 'Authorization Type'
         and p != 'Authorization ID']
        logBtn = Button(self, text='Log in', command=lambda: self.logInUser())
        logBtn.grid(row=1, column=4, sticky='W')
        refreshBtn = Button(self, text='Update the page', command=lambda: self.update_page())
        refreshBtn.grid(row=1, column=5, sticky='W')

        # device page
        # device
        label = Label(self, text='Device', font='bold')
        label.grid(row=2, column=5, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Total').grid(row=3, column=5)
        # find devices number
        Label(self, text='', width=10).grid(row=3, column=6)
        Label(self, text='Device 1').grid(row=4, column=5, columnspan=2)
        for i, p in enumerate(device_list.keys()):
            CreateColumn(self, p, i + 5, 5, name=device_list[p], fixed_text='')

        # subscription page
        label = Label(self, text='Subscriptions', font='bold')
        label.grid(row=2, column=7, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Total').grid(row=3, column=7)
        # find subsc number
        Label(self, text='', width=15).grid(row=3, column=8)
        Label(self, text='Authorizations Type').grid(row=4, column=7)
        Label(self, text='SUBSCRIPTIONS', width=20, anchor='w').grid(row=4, column=8)
        Label(self, text='Authorization ID(s)').grid(row=5, column=7, columnspan=2)

        # title page
        label = Label(self, text='PPV Titles', font='bold')
        label.grid(row=2, column=9, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Total').grid(row=3, column=9)
        # find subs number
        Label(self, text='').grid(row=3, column=10)
        Label(self, text='Authorizations Type', width=20).grid(row=4, column=9)
        Label(self, text='PPV', anchor='w', width=20).grid(row=4, column=10, sticky='W')
        title = {'PPV Title': 'ppvTitle', 'Expiration Date': 'expirationDate',
                 'Purchase ID': 'purchaseId'}
        Label(self, text='Title 1').grid(row=5, column=9, columnspan=2)
        for i, p in enumerate(title.keys()):
            CreateColumn(self, p, i + 6, 9, name=title[p], fixed_text='')

        # settings page
        label = Label(self, text='Settings', font='bold')
        label.grid(row=14, column=2, columnspan=3)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Port Connected').grid(row=15, column=2)
        base_url = file['Add Device']['URL'].split('/BillingAdaptor')[0]
        self.url = Label(self, text=base_url, wraplength=200, justify='left')
        self.url.grid(row=15, column=3, rowspan=2)
        # find base url
        self.dict['URL'] = base_url
        changeBtn = Button(self, text='Change', command=lambda: self.changeURL())
        changeBtn.grid(row=17, column=3, sticky='E')

    def changeURL(self):
        self.tempLabel = Label(self, text='Key in URL details')
        self.tempLabel.grid(row=19, column=2, columnspan=2)
        self.tempEntry = Entry(self, width=30)
        self.tempEntry.grid(row=20, column=2, columnspan=2)
        self.changeBtn = Button(self, text='Change', command=lambda: self.insertURL())
        self.changeBtn.grid(row=20, column=3, sticky='E')
        self.cancelBtn = Button(self, text='Cancel', command=lambda: self.delete())
        self.cancelBtn.grid(row=21, column=3, sticky='E')

    def delete(self):
        self.tempLabel.destroy()
        self.tempEntry.destroy()
        self.changeBtn.destroy()
        self.cancelBtn.destroy()

    def insertURL(self):
        # change URL in dictionary
        self.dict['new url'] = self.tempEntry.get()
        # change text in page
        self.url.config(text=self.tempEntry.get())
        # destroy current box
        self.delete()
        # change the one the config file
        with open('config.json', 'r+') as test:
            data = json.load(test)
            for apinfo in data.values():
                apinfo['URL'] = apinfo['URL'].replace(self.dict['URL'], self.dict['new url'])
            test.seek(0)
            json.dump(data, test, indent=4)
            test.truncate()

    def logInUser(self):
        # get household details
        if 'householdId' not in dictionary:
            h_id = self.logInCredentials.entry.get()
            if len(h_id) == 8:
                temp_file['householdId'] = h_id
            else:
                msgBox.showinfo('INCOMPLETE', 'Please make sure your household ID is valid.')
                raise ValueError
        parseHouseholdDetails()
        self.refresh()

    def update_page(self):
        try:
            parseHouseholdDetails()
        finally:
            self.refresh()

    def logOutUser(self):
        dictionary.clear()
        print(dictionary)
        self.refresh()

    def refresh(self):
        # destroy everything
        objectList = self.root.winfo_children()[1].winfo_children()
        for item in range(0, len(objectList)):
            objectList[item].destroy()
        # rebuild page
        label = Label(self, text='Account Info', font='bold')
        label.grid(row=2, column=2, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        if dictionary != {}:
            CreateColumn(self, 'Household ID', 1, 2, name='householdId', fixed_text=dictionary['householdId'])
            for i, p in enumerate(param_names):
                if p != 'Household ID' and p != 'Authorization Type' and p != 'Authorization ID':
                    if param_names[p] in dictionary.keys():
                        CreateColumn(self, p, i + 2, 2, name=param_names[p], fixed_text=dictionary[param_names[p]])
                    elif param_names[p] in dictionary['locale'].keys():
                        CreateColumn(self, p, i + 2, 2, name=param_names[p],
                                     fixed_text=dictionary['locale'][param_names[p]])
                    elif param_names[p] in dictionary['preferences'].keys():
                        CreateColumn(self, p, i + 2, 2, name=param_names[p],
                                     fixed_text=dictionary['preferences'][param_names[p]])
                    elif param_names[p] in dictionary['devices'][0].keys():
                        CreateColumn(self, p, i + 2, 2, name=param_names[p],
                                     fixed_text=dictionary['devices'][0][param_names[p]])
            logBtn = Button(self, text='Log out', command=lambda: self.logOutUser())
            logBtn.grid(row=1, column=4, sticky='W')
            refreshBtn = Button(self, text='Update the page', command=lambda: self.update_page())
            refreshBtn.grid(row=1, column=5, sticky='W')
        else:
            self.logInCredentials = CreateColumn(self, 'Household ID', 1, 2, name='householdId')
            [CreateColumn(self, p, i + 2, 2, name=param_names[p], fixed_text='') for i, p in
             enumerate(param_names) if p != 'Household ID' and p != 'Authorization Type'
             and p != 'Authorization ID']
            logBtn = Button(self, text='Log in', command=lambda: self.logInUser())
            logBtn.grid(row=1, column=4, sticky='W')
            refreshBtn = Button(self, text='Update the page', command=lambda: self.update_page())
            refreshBtn.grid(row=1, column=5, sticky='W')

        # device page
        # device
        label = Label(self, text='Device', font='bold')
        label.grid(row=2, column=5, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Total').grid(row=3, column=5)
        if dictionary != {}:
            # find devices number
            devices = dictionary['devices']
            Label(self, text='{}'.format(len(devices))).grid(row=3, column=6, sticky='W')
            k = 4
            l = 5
            for j, dev in enumerate(devices):
                Label(self, text='Device {}'.format(j+1)).grid(row=j+k, column=5, columnspan=2)
                for i, p in enumerate(device_list.keys()):
                    CreateColumn(self, p, i+l, 5, name=device_list[p], fixed_text=dev[device_list[p]])
                    k = l + i
                l = k + 2
        else:
            Label(self, text='', width=10).grid(row=3, column=6)
            Label(self, text='Device 1').grid(row=4, column=5, columnspan=2)
            for i, p in enumerate(device_list.keys()):
                CreateColumn(self, p, i + 5, 5, name=device_list[p], fixed_text='')

        # subscription page
        label = Label(self, text='Subscriptions', font='bold')
        label.grid(row=2, column=7, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Total').grid(row=3, column=7)
        # find subsc number
        Label(self, text='Authorizations Type').grid(row=4, column=7)
        Label(self, text='SUBSCRIPTIONS', width=20, anchor='w').grid(row=4, column=8)
        Label(self, text='Authorization ID(s)').grid(row=5, column=7, columnspan=2)
        if dictionary != {}:
            subscript = dictionary['authorizations']['subscriptions']['subscription']
            Label(self, text='{}'.format(len(subscript))).grid(row=3, column=8, sticky='W')
            for r, item in enumerate(subscript):
                Label(self, text=authorizationId_dict[item['authorizationId']]).grid(row=r + 6, column=7, sticky='W', padx=80, columnspan=2)

        # title page
        label = Label(self, text='PPV Titles', font='bold')
        label.grid(row=2, column=9, columnspan=2)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Total').grid(row=3, column=9)
        # find titles number
        Label(self, text='Authorizations Type', width=20).grid(row=4, column=9)
        Label(self, text='PPV', anchor='w', width=20).grid(row=4, column=10, sticky='W')
        if dictionary != {}:
            titles = dictionary['authorizations']['titles']
            Label(self, text='{}'.format(len(titles))).grid(row=3, column=10, sticky='W')
            k = 5
            l = 6
            for j, dev in enumerate(titles):
                Label(self, text='Title {}'.format(j+1)).grid(row=j + k, column=9, columnspan=2)
                CreateColumn(self, 'PPV Title', l, 9, name='title', fixed_text=authorizationId_dict[dev['authorizationId']])
                CreateColumn(self, 'Expiration Date', l+1, 9, name='expirationDate', fixed_text=dev['expirationDate'])
                Label(self, text='Purchase ID').grid(row=l + 2, column=9, rowspan=2, sticky='W')
                Label(self, text=dev['purchaseId'], wraplength=180, justify='left').grid(row=l + 2, column=10, rowspan=2)
                k = l + 4
                l = k + 2

        # settings page
        label = Label(self, text='Settings', font='bold')
        label.grid(row=14, column=2, columnspan=3)
        f = font.Font(label, label.cget("font"))
        f.configure(underline=True)
        label.configure(font=f)
        Label(self, text='Port Connected').grid(row=15, column=2)
        base_url = file['Add Device']['URL'].split('/BillingAdaptor')[0]
        self.url = Label(self, text=base_url, wraplength=200, justify='left')
        self.url.grid(row=15, column=3, rowspan=2)
        # find base url
        self.dict['URL'] = base_url
        changeBtn = Button(self, text='Change', command=lambda: self.changeURL())
        changeBtn.grid(row=17, column=3, sticky='E')


class CreateSubs(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Create New Subscriber'
        self.dict = {}
        param_names = {'Household ID': 'householdId', 'Device ID': 'deviceId', 'Account ID': 'accountId',
                       'SmartCard ID': 'smartCardId', 'Subscriber ID': 'subscriberId',
                       'Bouquet ID': 'bouquetId', 'Zip Code': 'zipCode'}
        self.dict['authorizationId'] = CreateColumn(root, 'Authorization ID(s)', 16, 2, optionList=authorizationId_optionlist,
                                             name='authorizationId', widget_type='entry_list')
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
        getReponse(widget_name)
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
        getReponse(widget_name)
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
        getReponse(widget_name)
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
        getReponse(widget_name)
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
        getReponse(widget_name)
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
        getReponse(widget_name)
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
        getReponse(widget_name)
        self.root.destroy()


class ReplaceCard(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Replace Card'
        self.dict = {}
        self.msgLabel = Label(root, text='Key in the following details.')
        self.msgLabel.grid(column=2, columnspan=2)
        self.saveButton = Button(root, text='Change', command=lambda: self.sendApi())
        self.saveButton.grid(row=4, column=3, sticky='W')
        self.cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        self.cancelButton.grid(row=4, column=3, sticky='E')
        if 'householdId' in dictionary.keys():
            self.household = CreateColumn(root, 'Household ID', 2, 2, name='householdId', fixed_text=dictionary['householdId'])
            self.dict[self.household.name] = self.household
        else:
            self.household = CreateColumn(root, 'Household ID', 2, 2, name='householdId')
            self.dict[self.household.name] = self.household
        self.smc = Label(root, text='SmartCard ID')
        self.smc.grid(row=3, column=2, sticky='W')
        self.smc.txt = Entry(root)
        self.smc.txt.grid(row=3, column=3)
        self.dict['smartCardId'] = self.smc.txt

    def sendApi(self):
        param_dict = self.dict
        param_dict['smartCardId'] = self.smc.txt.get()
        storeDictionary(param_dict)
        # get deviceId from dictionary or API
        if 'householdId' in dictionary.keys():
            pass
        else:
            parseHouseholdDetails()
        # find device
        dev = dictionary['devices']
        if len(dev) > 1:
            # destroy everything
            self.smc.destroy()
            self.msgLabel.destroy()
            self.saveButton.destroy()
            self.cancelButton.destroy()
            self.household.destroy()
            self.smc.txt.destroy()
            # choose dev
            Label(self.root, text='You have more than 1 device. Please select the device that you want this '
                                  'changes to be applied.', wraplength=200).grid(row=2, column=2, columnspan=2)
            Button(self.root, text='Change', command=lambda: self.storeDevId()).grid(row=6, column=3, sticky='W')
            Button(self.root, text='Cancel', command=lambda: self.root.destroy()).grid(row=6, column=3, sticky='E')
            # get device ID list
            deviceId_list = []
            for device in dev:
                deviceId_list.append(device['deviceId'])
            self.dict['deviceId'] = CreateColumn(self.root, 'Device ID', 3, 2, name='deviceId', widget_type='entry_combo',
                               optionList=deviceId_list)

        else:
            self.dict['deviceId'] = dictionary['devices'][0]['deviceId']
            # store info again and call the API
            self.storeDevId()

    def storeDevId(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        getReponse('Replace Card')
        self.root.destroy()

class AddDelOppv(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add/Delete OPPV'
        self.date = ''
        self.dict = {}
        if 'householdId' not in dictionary.keys():
            self.msgLabel = Label(root, text='Key in the household Id and the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Entry(self.root, width=23)
            self.household.grid(row=3, column=2)
        else:
            self.msgLabel = Label(root, text='Choose the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Label(self.root, text=dictionary['householdId'])
            self.household.grid(row=3, column=2)
        self.actionLa = Label(self.root, text='Action')
        self.actionLa.grid(row=4, column=1, sticky='W')
        self.entry = ttk.Combobox(root)
        self.entry.grid(row=4, column=2, columnspan=2)
        self.entry['values'] = ['Add', 'Delete']
        self.saveButton = Button(root, text='Go', command=lambda: self.goToRightPage())
        self.saveButton.grid(row=5, column=2)
        self.cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        self.cancelButton.grid(row=5, column=2, sticky='E', padx=10)

    def goToRightPage(self):
        action = self.entry.get()
        # get household details
        if 'householdId' not in dictionary:
            h_id = self.household.get()
            if len(h_id) == 8:
                temp_file['householdId'] = h_id
            else:
                msgBox.showinfo('INCOMPLETE', 'Please make sure your household ID is valid.')
                raise ValueError
            parseHouseholdDetails()
        else:
            pass
        # destory
        self.msgLabel.destroy()
        self.entry.destroy()
        self.saveButton.destroy()
        self.cancelButton.destroy()
        self.household.destroy()
        self.actionLa.destroy()
        self.householdLa.destroy()
        # new column
        if action == 'Add':
            self.dict['action'] = 'Add'
            time_set = []
            month_list = []
            day_list = []
            current_year = datetime.now().year
            saveButton = Button(self.root, text='Add', command=lambda: self.sendApi())
            saveButton.grid(row=9, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=9, column=3, sticky='E')
            col = CreateColumn(self.root, 'Household ID', 2, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            col = CreateColumn(self.root, 'Authorization ID(s)', 3, 2, optionList=authorizationId_optionlist, name='authorizationId',
                               widget_type='entry_combo')
            self.dict[col.name] = col
            # expiry date
            date_label = Label(self.root, text='Expiry Date(Year)')
            date_label.grid(row=4, column=2, sticky='W')
            self.year = ttk.Combobox(self.root)
            self.year.grid(row=4, column=3)
            self.year['values'] = [current_year + i for i in range(0, 20)]
            Label(self.root, text='Expiry Date(Month)').grid(row=5, column=2, sticky='W')
            self.month = ttk.Combobox(self.root)
            self.month.grid(row=5, column=3, sticky='W')
            for i in range(1, 13):
                if len(str(i)) == 1:
                    str_i = ''.join([str(0), str(i)])
                else:
                    str_i = str(i)
                month_list.append(str_i)
            self.month['values'] = month_list
            Label(self.root, text='Expiry Date(Day)').grid(row=6, column=2, sticky='W')
            self.day = ttk.Combobox(self.root)
            self.day.grid(row=6, column=3, sticky='W')
            for i in range(1, 32):
                if len(str(i)) == 1:
                    str_i = ''.join([str(0), str(i)])
                else:
                    str_i = str(i)
                day_list.append(str_i)
            self.day['values'] = day_list
            # expiry time
            Label(self.root, text='Expiry Time').grid(row=7, column=2, sticky='W')
            self.time = ttk.Combobox(self.root)
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
            col = CreateColumn(self.root, 'Authorization Type', 8, 2, name='authorizationType', fixed_text='PPV')
            self.dict[col.name] = col
        else:
            self.dict['action'] = 'Delete'
            msgLabel = Label(self.root, text='Key in the following details.')
            msgLabel.grid(column=2, columnspan=2)
            saveButton = Button(self.root, text='Delete', command=lambda: self.sendApi())
            saveButton.grid(row=6, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=6, column=3, sticky='E')
            col = CreateColumn(self.root, 'Household ID', 2, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            # retrieve purchase id
            titles = dictionary['authorizations']['titles']
            option = []
            for til in titles:
                option.append(til['purchaseId'])
            col = CreateColumn(self.root, 'Purchase ID', 3, 2, name='purchaseId', widget_type='entry_combo',
                               optionList=option)
            self.dict[col.name] = col

    def sendApi(self):
        if self.dict['action'] == 'Add':
            # combine date
            self.date = ''.join([self.year.get(), '-', self.month.get(), '-', self.day.get()])
            self.time_toset = ''.join(['T', self.time.get(), 'Z'])
            self.dict['expirationDate'] = ''.join([self.date, self.time_toset])
            param_dict = self.dict
            storeDictionary(param_dict)
            getReponse('Add OPPV')
            self.root.destroy()
        else:
            param_dict = self.dict
            storeDictionary(param_dict)
            #getReponse('Remove OPPV - Get')
            getReponse('Remove OPPV - Delete')
            self.root.destroy()


class AddDelDev(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add/Delete Device'
        self.dict = {}
        if 'householdId' not in dictionary.keys():
            self.msgLabel = Label(root, text='Key in the household Id and the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Entry(self.root, width=23)
            self.household.grid(row=3, column=2)
        else:
            self.msgLabel = Label(root, text='Choose the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Label(self.root, text=dictionary['householdId'])
            self.household.grid(row=3, column=2)
        self.actionLa = Label(self.root, text='Action')
        self.actionLa.grid(row=4, column=1, sticky='W')
        self.entry = ttk.Combobox(self.root)
        self.entry.grid(row=4, column=2)
        self.entry['values'] = ['Add', 'Delete']
        self.saveButton = Button(root, text='Go', command=lambda: self.goToRightPage())
        self.saveButton.grid(row=5, column=2)
        self.cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        self.cancelButton.grid(row=5, column=2, sticky='E', padx=10)
        self.dict['action'] = self.entry
        self.dict['householdId'] = self.household

    def goToRightPage(self):
        action = self.entry.get()
        # get household details
        if 'householdId' not in dictionary:
            h_id = self.household.get()
            if len(h_id) == 8:
                temp_file['householdId'] = h_id
            else:
                msgBox.showinfo('INCOMPLETE', 'Please make sure your household ID is valid.')
                raise ValueError
            parseHouseholdDetails()
        else:
            pass
        # destory
        self.msgLabel.destroy()
        self.entry.destroy()
        self.saveButton.destroy()
        self.cancelButton.destroy()
        self.household.destroy()
        self.actionLa.destroy()
        self.householdLa.destroy()
        # new column
        if action == 'Add':
            self.dict['action'] = 'Add'
            saveButton = Button(self.root, text='Add', command=lambda: self.sendApi())
            saveButton.grid(row=7, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=7, column=3, sticky='E')
            col = CreateColumn(self.root, 'Household ID', 2, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            col = CreateColumn(self.root, 'Device ID', 3, 2, name='deviceId')
            self.dict[col.name] = col
            col = CreateColumn(self.root, 'SmartCard ID', 4, 2, name='smartCardId')
            self.dict[col.name] = col
            col = CreateColumn(self.root, 'Subscriber ID', 5, 2, name='subscriberId')
            self.dict[col.name] = col
            self.dict['bssFullType'] = CreateColumn(self.root, 'bssFullType', 6, 2,
                                                    optionList=['IVP-DTH-STB', 'IVP-IP-STB'],
                                                    name='bssFullType', widget_type='entry_combo')
        else:
            self.dict['action'] = 'Delete'
            saveButton = Button(self.root, text='Delete', command=lambda: self.sendApi())
            saveButton.grid(row=6, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=6, column=3, sticky='E')
            col = CreateColumn(self.root, 'Household ID', 2, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            # get device ID list
            devices = dictionary['devices']
            deviceId_list = []
            for dev in devices:
                deviceId_list.append(dev['deviceId'])
            col = CreateColumn(self.root, 'Device ID', 3, 2, name='deviceId', widget_type='entry_combo',
                               optionList=deviceId_list)
            self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        if self.dict['action'] == 'Add':
            getReponse('Add Device')
        else:
            getReponse('Delete Device')
        self.root.destroy()


class AddDelSSer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.dict = {}
        self.name = 'Add/Delete Single Service'
        if 'householdId' not in dictionary.keys():
            self.msgLabel = Label(root, text='Key in the household Id and the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Entry(self.root, width=23)
            self.household.grid(row=3, column=2)
        else:
            self.msgLabel = Label(root, text='Choose the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Label(self.root, text=dictionary['householdId'])
            self.household.grid(row=3, column=2)
        self.actionLa = Label(self.root, text='Action')
        self.actionLa.grid(row=4, column=1, sticky='W')
        self.entry = ttk.Combobox(root)
        self.entry.grid(row=4, column=2, columnspan=2)
        self.entry['values'] = ['Add', 'Delete']
        self.saveButton = Button(root, text='Go', command=lambda: self.goToRightPage())
        self.saveButton.grid(row=5, column=2)
        self.cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        self.cancelButton.grid(row=5, column=2, sticky='E', padx=10)

    def goToRightPage(self):
        action = self.entry.get()
        # get household details
        if 'householdId' not in dictionary:
            h_id = self.household.get()
            if len(h_id) == 8:
                temp_file['householdId'] = h_id
            else:
                msgBox.showinfo('INCOMPLETE', 'Please make sure your household ID is valid.')
                raise ValueError
            parseHouseholdDetails()
        else:
            pass
        # destory
        self.msgLabel.destroy()
        self.entry.destroy()
        self.saveButton.destroy()
        self.cancelButton.destroy()
        self.household.destroy()
        self.actionLa.destroy()
        self.householdLa.destroy()
        # new column
        if action == 'Add':
            self.dict['action'] = 'Add'
            col = CreateColumn(self.root, 'Household ID', 3, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            temp_file['authorizationType'] = 'SUBSCRIPTION'
            col = CreateColumn(self.root, 'Authorization ID', 4, 2, optionList=authorizationId_optionlist, name='authorizationId',
                               widget_type='entry_combo')
            self.dict[col.name] = col
            saveButton = Button(self.root, text='Add', command=lambda: self.sendApi())
            saveButton.grid(row=5, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=5, column=3, sticky='E')
        else:
            self.dict['action'] = 'Delete'
            saveButton = Button(self.root, text='Delete', command=lambda: self.sendApi())
            saveButton.grid(row=6, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=6, column=3, sticky='E')
            col = CreateColumn(self.root, 'Household ID', 3, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            # retrieve authorizationId
            subscript = dictionary['authorizations']['subscriptions']['subscription']
            subscription_ls = []
            for item in subscript:
                subscription_ls.append(''.join(['[', item['authorizationId'], ']', ' ', item['authorizationId']]))
            col = CreateColumn(self.root, 'Authorization ID', 4, 2, optionList=subscription_ls, name='authorizationId',
                               widget_type='entry_combo')
            self.dict[col.name] = col

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        if self.dict['action'] == 'Add':
            getReponse('Add Single Service')
        else:
            getReponse('Delete Single Service')
        self.root.destroy()


class AddDelESer(Frame):
    def __init__(self, root):
        self.root = root
        Frame.__init__(self, self.root)
        self.name = 'Add/Delete Enabler Service'
        self.dict = {}
        if 'householdId' not in dictionary.keys():
            self.msgLabel = Label(root, text='Key in the household Id and the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Entry(self.root, width=23)
            self.household.grid(row=3, column=2)
        else:
            self.msgLabel = Label(root, text='Choose the action you would like to take.')
            self.msgLabel.grid(column=1, columnspan=2)
            self.householdLa = Label(self.root, text='Household ID')
            self.householdLa.grid(row=3, column=1, sticky='W')
            self.household = Label(self.root, text=dictionary['householdId'])
            self.household.grid(row=3, column=2)
        self.actionLa = Label(self.root, text='Action')
        self.actionLa.grid(row=4, column=1, sticky='W')
        self.entry = ttk.Combobox(root)
        self.entry.grid(row=4, column=2, columnspan=2)
        self.entry['values'] = ['Add', 'Delete']
        self.saveButton = Button(root, text='Go', command=lambda: self.goToRightPage())
        self.saveButton.grid(row=5, column=2)
        self.cancelButton = Button(root, text='Cancel', command=lambda: self.root.destroy())
        self.cancelButton.grid(row=5, column=2, sticky='E', padx=10)

    def goToRightPage(self):
        action = self.entry.get()
        # get household details
        if 'householdId' not in dictionary:
            h_id = self.household.get()
            if len(h_id) == 8:
                temp_file['householdId'] = h_id
            else:
                msgBox.showinfo('INCOMPLETE', 'Please make sure your household ID is valid.')
                raise ValueError
            parseHouseholdDetails()
        else:
            pass
        # destory
        self.msgLabel.destroy()
        self.entry.destroy()
        self.saveButton.destroy()
        self.cancelButton.destroy()
        self.household.destroy()
        self.actionLa.destroy()
        self.householdLa.destroy()
        # new column
        if action == 'Add':
            self.dict['action'] = 'Add'
            col = CreateColumn(self.root, 'Household ID', 3, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            col = CreateColumn(self.root, 'Enabler Services', 4, 2,
                               optionList=['PPV_ENABLER', 'PVR_ENABLER', 'VOD_ENABLER'],
                               name='enablerServices', widget_type='entry_combo')
            self.dict[col.name] = col
            saveButton = Button(self.root, text='Add', command=lambda: self.sendApi())
            saveButton.grid(row=6, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=6, column=3, sticky='E')
        else:
            self.dict['action'] = 'Delete'
            col = CreateColumn(self.root, 'Household ID', 3, 2, name='householdId',
                               fixed_text=dictionary['householdId'])
            self.dict[col.name] = col
            col = CreateColumn(self.root, 'Enabler Services', 4, 2,
                               optionList=['PPV_ENABLER', 'PVR_ENABLER', 'VOD_ENABLER'],
                               name='enablerServices', widget_type='entry_combo')
            self.dict[col.name] = col
            saveButton = Button(self.root, text='Delete', command=lambda: self.sendApi())
            saveButton.grid(row=6, column=3, sticky='W')
            cancelButton = Button(self.root, text='Cancel', command=lambda: self.root.destroy())
            cancelButton.grid(row=6, column=3, sticky='E')

    def sendApi(self):
        param_dict = self.dict
        storeDictionary(param_dict)
        if self.dict['action'] == 'Add':
            getReponse('Add Enabler Service')
        else:
            getReponse('Delete Enabler Service')
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
        col = CreateColumn(root, 'Authorization ID(s)', 11, 2, optionList=authorizationId_optionlist, name='authorizationId',
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
        getReponse(widget_name)
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
        col = CreateColumn(root, 'Authorization ID(s)', 5, 2, optionList=authorizationId_optionlist, name='authorizationId',
                           widget_type='entry_list')
        self.dict[col.name] = col
        self.dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 4, 2, name='authorizationType',
                                                      fixed_text='SUBSCRIPTION')

    def sendApi(self):
        widget_name = self.name
        param_dict = self.dict
        storeDictionary(param_dict)
        getReponse(widget_name)
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
        self.dict['authorizationId'] = CreateColumn(root, 'Authorization ID(s)', 4, 2, optionList=authorizationId_optionlist,
                                             name='authorizationId', widget_type='entry_list')
        self.dict['authorizationType'] = CreateColumn(root, 'Authorization Type', 3, 2, name='authorizationType',
                                                      fixed_text='SUBSCRIPTION')

    def sendApi(self):
        param_dict = self.dict
        widget_name = self.name
        storeDictionary(param_dict)
        getReponse(widget_name)
        self.root.destroy()


# make frame for device.


# class Device(Frame):
#     # create menu page with all the button.
#     def __init__(self, root, controller):
#         self.root = root
#         Frame.__init__(self, self.root)
#         self.name = 'Device & Subscriptions'
#         # create buttons for different sections
#         # btnSubs = Button(self, text='Subscriber Details', state=NORMAL, name='btnSubs',
#         #                  command=lambda: controller.show_frame('AccountInfo'))
#         # btnSubs.grid(row=1, column=1, sticky='SNEW', rowspan=5)
#         # btnDev = Button(self, text='Device(s) & Subscriptions', state=NORMAL, name='btnDev',
#         #                 command=lambda: controller.show_frame('Device'))
#         # btnDev.grid(row=6, column=1, sticky='SNEW', rowspan=6)
#         # btnSett = Button(self, text='Info & Settings', state=NORMAL, name='btnSett')
#         # btnSett.grid(row=12, column=1, sticky='SNEW', rowspan=6)
#
#         # device info page
#         self.dict = {}
#
#         refreshBtn= Button(self, text='Update', command=lambda: controller.refresh())
#         refreshBtn.grid(row=17, column=3, sticky='W')
#
#     def logInUser(self, controller):
#         param_dict = self.dict
#         storeDictionary(param_dict)
#         parseHouseholdDetails()

# create buttons
# create buttons for different sections
# btnSubs = Button(self, text='Subscriber Details', state=NORMAL, name='btnSubs',
#                  command=lambda: controller.show_frame('AccountInfo'))
# btnSubs.grid(row=1, column=1, sticky='SNEW', rowspan=5)
# btnDev = Button(self, text='Device(s) & Subscriptions', state=NORMAL, name='btnDev',
#                 command=lambda: controller.show_frame('Device'))
# btnDev.grid(row=6, column=1, sticky='SNEW', rowspan=6)
# btnSett = Button(self, text='Info & Settings', state=NORMAL, name='btnSett')
# btnSett.grid(row=12, column=1, sticky='SNEW', rowspan=6)

# refresh page
# if objectList[item].widgetName == 'button' and objectList[item]['text'] == 'Log in':
#     objectList[item].destroy()
#
# if objectList[item].widgetName == 'label':
#     param = ''
#     text = objectList[item].cget('text')
#     if text in param_names.keys():
#         param = param_names[text]
#     elif text in device_list.keys():
#         param = device_list[text]
#     if param != '':
#         if param in dictionary.keys():
#             if param == 'householdId':
#                 objectList[item + 1].destroy()
#                 Label(self, text=dictionary[param]).grid(row=1, column=3, sticky='W')
#             else:
#                 objectList[item + 1].config(text=dictionary[param], anchor='w')
#         else:
#             selected_branch = dictionary['locale']
#             if param in selected_branch.keys():
#                 objectList[item + 1].config(text=selected_branch[param], anchor='w')
#             else:
#                 selected_branch = dictionary['preferences']
#                 if param in selected_branch.keys():
#                     objectList[item + 1].config(text=selected_branch[param], anchor='w')

boa = Boa()
boa.mainloop()
