# classbasedPRTG API requester.
# G00001
#   python      3.7
#   requests    2.19.1
#   urllib3     1.23
#   pandas      0.23.4
#   pyOpenSSL   18.0.0
#   cryptography 2.3.1
#   certifi     2018.8.24
#

'''

    MultiProcesses:
        - UI / Search / 
        - Merge
        - Process notifications (Loading, cancelling, etc.)
        - garbagecollect
    
    Search:
        - Resize window/columns
        - XScrollbar
        - select / refilter
        - Check OR, results and multiple words in entrybox


    General:
        - hashes (pw/license keys)
        - SSL
        - merging
         

    automation
        - Time available to perform said task
            - check for ETA overlaps
            
        - Date intervals (everyday, every week etc.)
        - process to perform and id's to do it with
        - Create presets
        - Make last live request preset for automation


Interface

    - Program / create new automatic request 
    - Get data now
        - Use preset
        - manual request config

    - Manage existing requests
        - Do the do
        - test
        - summary of what it should return

    - Settings
        - Server settings
        - default filetype
        - Updates 
        - db settings


////////////////////////////
Windows

root.winfo_screenwidth()
root.winfo_screenheight()

root.geometry()
# calculate position x and y coordinates
    #   x / y are screen pos.
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))


Export presets in commandmenu

'''
#import pprint
import gc
from multicolumns import *
from tkinter import *
from customFunc import *
from tkinter import filedialog
import pandas as pd
import threading
import logging
# import ssl
#   cert = ssl.get_server_certificate(('127.0.0.1', 443))
# import multiprocessing

#   Logging Setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s:%(levelname)s:%(message)s:')
file_handler = logging.FileHandler('info.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# logging.basicConfig(filename='info.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s:')
# logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s:')

font = 'arial', 10, 'bold'
font2 = 'arial', 10
colFont = 'arial', 9, 'bold'
reqSel = ''


class Notification(Toplevel):

    def __init__(self, message, title='Notification', w=165, h=150, but_text='Ok'):
        Toplevel.__init__(self)
        self.title(title)
        self.title_name = title
        self.iconbitmap('imgs\prtg_active.ico')
        x = self.winfo_screenheight() / 2
        y = self.winfo_screenheight() / 2
        self.geometry('%dx%d+%d+%d' % (w, h, x - (w / 2), y - (h / 2)))
        self.label = Label(self, text=message, wraplength=w - (w * 0.1), justify='center')
        self.label.grid(row=0, columnspan=10, sticky=W + E + S + N)
        self.button = Button(self, text=but_text, command=self.destroy, width=7)
        self.button.grid(row=10, sticky=W + E, padx=5, pady=5)


class Window(Toplevel):

    def __init__(self, title, w, h):
        Toplevel.__init__(self)        
        self.title(title)
        self.title_name = title
        self.iconbitmap('imgs\prtg_active.ico')
        x = self.winfo_screenheight() / 2
        y = self.winfo_screenheight() / 2
        self.geometry('%dx%d+%d+%d' % (w, h, x - (w /2), y - (h / 2)))

class CheckAll(Frame, Checkbutton):
    def __init__(self, parent=None, params=[]):
        Frame.__init__(self, parent)
        self.f = parent
        self.vars = []
        self.params = params
        contX = 0
        contY = 0
        cont = 0
        for par in params:
            var = StringVar()  # assigning the checkbox text/name to var to read later
            chkb = Checkbutton(self, text=par,
                               variable=var, onvalue=par,
                               )
            if cont < len(params):  # psuedo for to populate the grid using a certain format
                chkb.grid(row=contY, column=contX, sticky=W, padx=2)
                if cont % 4 == 0 and cont != 0:

                    cont += 1
                    contY += 1
                    contX = 0
                else:

                    cont += 1
                    contX += 1

            chkb.select()
            self.vars.append(var)

    def state(self):  # returns a list with states of each checkbx.
        return map((lambda var: var.get()), self.vars)

    def updated(self, newParams):
        return Checkbar(self.f, params=newParams)

    def checked(self, newParams):
        return CheckAll(self.f, params=newParams)


class Checkbar(Frame, Checkbutton):
    def __init__(self, parent=None, params=[]):
        Frame.__init__(self, parent)
        self.f = parent
        self.vars = []
        self.params = params
        contX = 0
        contY = 0
        cont = 0
        for par in params:
            var = StringVar()  # assigning the checkbox text/name to var to read later
            chkb = Checkbutton(self, text=par,
                               variable=var, onvalue=par,
                               )
            if cont < len(params):  # psuedo for to populate the grid using a certain format
                chkb.grid(row=contY, column=contX, sticky=W, padx=2)
                if cont % 4 == 0 and cont != 0:

                    cont += 1
                    contY += 1
                    contX = 0
                else:

                    cont += 1
                    contX += 1

            chkb.deselect()
            self.vars.append(var)

    def state(self):  # returns a list with states of each checkbx.
        return map((lambda var: var.get()), self.vars)

    def updated(self, newParams):
        return Checkbar(self.f, params=newParams)

    def checked(self, newParams):
        return CheckAll(self.f, params=newParams)


class App:

    def __init__(self, master, screenx, screeny):
        self.root = master
        #   screen dimensions
        self.scy = screeny
        self.scx = screenx
        # posx = (self.scx/2) - (self.width/2)
        # posy = (self.scy/2) - (self.height/2)

        #   Multiprocessing

        #   queue vars
        self.iter = 1
        self.eta = ''
        self.start_time = datetime.datetime.now()

        #   iter == coutns iterations of multiple ID reqs

        #   Menu bar

        self.menubar = Menu(master)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.filemenu.add_command(label='Server settings', command=self.serverSettings)
        self.filemenu.add_command(label='Rebuild Search Index', command=self.rebuild)
        self.filemenu.add_separator()

        self.filemenu.add_command(label='Quit', command=master.destroy)
        self.menubar.add_cascade(label='File', menu=self.filemenu)

        #   requests vars
        # self.sleep_event = threading.Event()
        self.customFileName = StringVar()
        self.sleep_time = 11
        self.cancel_req = 0
        self.__gc = 1
        #   Internal data - credentials
        self.__usn = StringVar()
        self.__pw = StringVar()
        self.__ph = ''
        self.__ip = StringVar()
        self.__port = StringVar()
        self.__https = IntVar()

        self.error_count = 0
        #   count var to stop for after x connection failures
        #   Flags
        self.id_option = 'entry'
        #   possible values entry, import, search
        #   Id list objects
        self.idEntVar = StringVar()
        self.idEntVar.set('')
        self.valid_ids = []
        self.invalid_ids = []
        self.total_requests = 0

        #   internal_db
        self.sensors = pd.DataFrame()

        #   Search vars
        #   static ?
        self.search_query_var = StringVar()
        self.search_tags_var = StringVar()
        self.search_types_var = StringVar()
        self.search_name_var = StringVar()
        self.search_parent_var = StringVar()
        self.search_grp_var = StringVar()
        self.search_prb_var = StringVar()
        self.search_results = pd.DataFrame()
        #   Data frame read to display search results from parsed self.sensors
        self.temp_df_list = []
        self.temp_df = pd.DataFrame()
        #   Frames that will include other frames.

        self.main_page_tab = Frame(master, width=550, height=625)
        self.main_page_tab.pack()
        #   main tab, contains file opt, req opt, req sp opt.

        self.file_options_frame = Frame(self.main_page_tab, width=550, height=125)
        self.file_options_frame.grid(row=0)
        self.file_options_frame.grid_propagate(0)
        self.req_opt_frame = Frame(self.main_page_tab, width=550, height=225)
        self.req_opt_frame.grid(row=1)
        self.req_opt_frame.grid_propagate(0)
        self.req_sp_frame = Frame(self.main_page_tab, width=550, height=300)
        self.req_sp_frame.grid(row=2)
        self.req_sp_frame.grid_propagate(0)
        #   550 x 550px

        #   File options
        self.title_label_fo = Label(self.file_options_frame, text='File Options', anchor=W, font=font, relief=GROOVE)
        self.title_label_fo.grid(row=0, sticky=W + E, padx=3, pady=2, columnspan=30)
        self.title_label_fo.grid_propagate(0)
        self.outLab = Label(self.file_options_frame, text='File Type', font=font)
        self.outLab.grid(row=1, column=0, padx=3, pady=2, sticky=E)
        self.outpVar = StringVar()
        self.outpVar.set('CSV')
        self.outpDD = OptionMenu(self.file_options_frame, self.outpVar, 'XML', 'JSON', 'CSV',
                                 'HTML', 'HTML Table',
                                 command=self.checks)
        self.outpDD.config(width=9)
        self.outpDD.grid(row=1, column=2, padx=3, pady=2)
        self.filename_var = StringVar()
        self.filename_var.set('')
        self.filename_label = Label(self.file_options_frame, text="Merged file name")
        self.filename_label.grid(row=1, column=3, padx=3, pady=2, sticky=E)
        self.filename_entry = Entry(self.file_options_frame, width=25, textvariable=self.customFileName)
        self.filename_entry.grid(row=1, column=4, padx=3, pady=2, sticky=E)

        #   FO - ROW 2:
        self.pathButton = Button(self.file_options_frame, text="Save to", width=11, font=font2, command=self.setPath)
        self.pathButton.grid(row=2, column=2, columnspan=2, sticky=W, padx=3, pady=4)
        self.savePath = StringVar()
        self.savePath.set(userDesk)
        self.pathLabel = Label(self.file_options_frame, textvariable=self.savePath)
        self.pathLabel.grid(row=2, column=3, columnspan=20, sticky=W, padx=4, pady=4)
        self.preferences = 0

        self.rawVar = IntVar()
        self.rawVar.set(1)
        self.raw_cb = Checkbutton(self.file_options_frame, variable=self.rawVar,
                                  onvalue=0, offvalue=1, text='Include Raw data')
        self.raw_cb.grid(row=3, column=0, sticky=W, columnspan=3)
        #   Request options
        self.title_label_ro = Label(self.req_opt_frame, text='Request Options', anchor=W, font=font, relief=GROOVE)
        self.title_label_ro.grid(row=0, sticky=W + E, padx=1, pady=2, columnspan=30)

        self.reqLab = Label(self.req_opt_frame, text='Request', font=font, bd=2)
        self.reqLab.grid(row=1, column=2, padx=3, pady=3, sticky=W)
        self.reqVar = StringVar()
        self.reqVar.set('Historic')
        self.reqDD = OptionMenu(self.req_opt_frame, self.reqVar, 'Historic',
                           'Channels', 'Devices', 'Groups', 'Messages',
                           'Reports', 'Sensors', 'Sensortree', 'StoredReports',
                           'Ticketdata', 'Tickets', 'Values',
                           command=self.buildIt)
        self.reqDD.config(width=12)
        self.reqDD.grid(row=1, column=4, padx=3, pady=2)
        self.req_preset_label = Label(self.req_opt_frame, text='Saved Presets')
        self.req_preset_label.grid(row=1, column=5, padx=3, pady=2)
        self.preset_var = StringVar()
        self.preset_var.set('Preset 1')
        self.req_preset = OptionMenu(self.req_opt_frame, self.preset_var, 'Preset 1')
        self.req_preset.config(state='disabled')
        self.req_preset.grid(row=1, column=6, padx=3, pady=2)
        #   presets paid feature ?
        #   ID
        self.ent_x = 60
        self.id_label = Label(self.req_opt_frame, text='ID(s) (1, 2...)', font=font2)
        self.id_label.grid(row=2, column=2, columnspan=2, sticky=W, padx=3, pady=2)
        self.id_entry = Entry(self.req_opt_frame, width=self.ent_x, textvariable=self.idEntVar)
        self.id_entry.grid(row=2, column=4, columnspan=100, sticky=W, padx=3, pady=2)
        self.id_search_but = Button(self.req_opt_frame, text='Search & Select', width=12, command=self.search_window)
        self.id_search_but.grid(row=6, column=2, columnspan=2, sticky=W, padx=3, pady=2)
        self.csv_import_but = Button(self.req_opt_frame, text='Import CSV', width=10, command=self.import_csv)
        self.csv_import_but.grid(row=6, column=4, columnspan=3, sticky=W, padx=3, pady=2)
        self.clear_but = Button(self.req_opt_frame, text='Clear CSV / Search', width=14, command=self.clear_csv)
        self.clear_but.grid(row=6, column=5, columnspan=4, sticky=W, padx=3, pady=2)

        self.mergeVar = IntVar()
        self.mergeVar.set(1)
        self.merge_cb = Checkbutton(self.req_opt_frame, variable=self.mergeVar, onvalue=1, offvalue=0, text='Merge CSV', command=self.merging)
        self.merge_cb.grid(row=7, column=2, columnspan=2, sticky=W)

        self.remVar = IntVar()
        self.remVar.set(1)
        self.keep_cb = Checkbutton(self.req_opt_frame, variable=self.remVar, onvalue=1, offvalue=0, text='Only Keep Merged CSV')
        self.keep_cb.grid(row=7, column=4, columnspan=2, sticky=W)

        self.tag_label = Label(self.req_opt_frame, text='Tags (tag, tag...)')
        self.tag_label.grid(row=3, column=2, columnspan=2, sticky=W, padx=2, pady=2)
        self.filterTagsVar = StringVar()
        self.filterTagsEnt = Entry(self.req_opt_frame, width=self.ent_x, textvariable=self.filterTagsVar)
        self.filterTagsEnt.grid(row=3, column=4, columnspan=100, padx=2, pady=2)

        self.type_var = StringVar()
        self.type_var.set('')
        self.type_label = Label(self.req_opt_frame, text='Sensor Type')
        self.type_label.grid(row=4, column=2, columnspan=3, sticky=W, padx=2, pady=2)
        self.type_entry = Entry(self.req_opt_frame, width=15, textvariable=self.type_var)
        self.type_entry.grid(row=4, column=4, columnspan=100, padx=2, pady=2, sticky=W)

        self.count_label = Label(self.req_opt_frame, text='# of Results')
        self.count_label.grid(row=5, column=2, columnspan=2, sticky=W, padx=2, pady=2)
        self.countVar = StringVar()
        self.countVar.set('')
        self.count_entry = Entry(self.req_opt_frame, width=15, textvariable=self.countVar)
        self.count_entry.grid(row=5, column=4, columnspan=2, sticky=W, padx=2, pady=2)

        self.get_button = Button(self.req_opt_frame, text='Get', width=7, height=3, font=('arial', 11, 'bold'),
                                 command=self.start_get)
        self.get_button.grid(row=5, column=8, columnspan=4, rowspan=3, sticky=E)

        #   Request specific
        #   2 frames, 1 with checkboxes other with historic parameters
        self.title_label_ro = Label(self.req_sp_frame, text='Historic settings', anchor=W, font=font, relief=GROOVE)
        self.title_label_ro.grid(row=0, sticky=W + E, padx=1, pady=2, columnspan=30)

        #   historic frame
        self.historic_par = Frame(self.req_sp_frame, width=550)
        #   Dates

        self.format_label = Label(self.historic_par, text='YYYY-MM-DD-HH-MM-SS')
        self.format_label.grid(row=0, column=2, columnspan=4, sticky=W)
        self.idate_var = StringVar()
        self.idate = Label(self.historic_par, text='Start Date')
        self.idate.grid(row=1, column=1, sticky=W)
        self.idate_ent = Entry(self.historic_par, width=25, textvariable=self.idate_var)
        self.idate_ent.grid(row=1, column=2, sticky=W, columnspan=3)
        self.fdate_var = StringVar()
        self.fdate = Label(self.historic_par, text='End Date')
        self.fdate.grid(row=2, column=1, sticky=W)
        self.fdate_ent = Entry(self.historic_par, width=25, textvariable=self.fdate_var)
        self.fdate_ent.grid(row=2, column=2, sticky=W, columnspan=3)

        self.add_hours_start = Button(self.historic_par, text='+ 1 Hour', command=self.ah_start)
        self.add_hours_start.grid(row=1, column=8, sticky=W, padx=3, pady=3)
        self.sub_hours_start = Button(self.historic_par, text='- 1 Hour', command=self.sh_start)
        self.sub_hours_start.grid(row=1, column=6, sticky=W, padx=3, pady=3)

        self.add_hours_end = Button(self.historic_par, text='+ 1 Hour', command=self.ah_end)
        self.add_hours_end.grid(row=2, column=8, sticky=W, padx=3, pady=3)
        self.sub_hours_end = Button(self.historic_par, text='- 1 Hour', command=self.sh_end)
        self.sub_hours_end.grid(row=2, column=6, sticky=W, padx=3, pady=3)

        #   HT - date presets
        self.avg_lb = Label(self.historic_par, text='Avg. data by X seconds')
        self.avg_lb.grid(row=1, column=9, columnspan=2, padx=3, pady=2)
        self.avg = IntVar()
        self.avg.set(0)
        self.avg_ent = Entry(self.historic_par, width=8, textvariable=self.avg)
        #   e = Entry(root, textvariable=sv, validate="focusout", validatecommand=callback)
        self.avg_ent.grid(row=2, column=9, columnspan=2, padx=3, pady=2)
        #   if 0, max 40 days. else max 500 days but cannot verify with server.
        #

        self.max_label = Label(self.historic_par, text='Max Date range for Avg 0 is 40 Days, else 500 days is max.')
        self.max_label.grid(row=3, columnspan=20)

        self.date_b_w = 7
        self.lb = Label(self.historic_par, text='Quick Dates', font=font)
        self.lb.grid(row=4, columnspan=3)
        #   , command=self.calc_date('1 Day')
        self.one_day = Button(self.historic_par, text='1 Day', width=self.date_b_w, command=self.oneDay)
        self.one_day.grid(row=5, column=1, sticky=W, padx=2)

        self.five_day = Button(self.historic_par, text='5 Days', width=self.date_b_w, command=self.fiveDays)
        self.five_day.grid(row=5, column=2, sticky=W, padx=2, columnspan=2)

        self.one_week = Button(self.historic_par, text='1 Week', width=self.date_b_w, command=self.oneWeek)
        self.one_week.grid(row=5, column=4, sticky=W, padx=2, columnspan=2)

        self.ten_days = Button(self.historic_par, text='10 Days', width=self.date_b_w, command=self.tenDays)
        self.ten_days.grid(row=6, column=1, sticky=W, padx=2, columnspan=2)

        self.two_weeks = Button(self.historic_par, text='2 Weeks', width=self.date_b_w, command=self.twoWeeks)
        self.two_weeks.grid(row=5, column=5, sticky=W, padx=2, columnspan=2)

        self.four_weeks = Button(self.historic_par, text='4 Weeks', width=self.date_b_w, command=self.fourWeeks)
        self.four_weeks.grid(row=6, column=5, sticky=W, padx=2, columnspan=2)

        self.three_weeks = Button(self.historic_par, text='3 Weeks', width=self.date_b_w, command=self.threeWeeks)
        self.three_weeks.grid(row=6, column=4, sticky=W, padx=2, columnspan=2)

        self.thirty_days = Button(self.historic_par, text='30 Days', width=self.date_b_w, command=self.thirtyDays)
        self.thirty_days.grid(row=6, column=2, sticky=W, padx=2, pady=2, columnspan=2)

        self.todayBut = Button(self.historic_par, text='Today', width=self.date_b_w, command=self.date_manager, font=colFont)
        self.todayBut.grid(row=7, column=1, sticky=W, padx=2, columnspan=2)

        self.last_month = Button(self.historic_par, text='Last Month', width=self.date_b_w + 2, command=self.lastMonth)
        self.last_month.grid(row=7, column=2, sticky=W, padx=2, columnspan=2)

        self.last_24 = Button(self.historic_par, text='Last 24h', width=self.date_b_w + 2, command=self.lastDay)
        self.last_24.grid(row=7, column=4, sticky=W, padx=2, columnspan=2)

        #   live data frame
        self.checkbox_container = Frame(self.req_sp_frame, width=550)
        self.theBoxes = Checkbar(self.checkbox_container, params=chanReq)

        self.allSel = IntVar()
        self.selectAll = Checkbutton(self.checkbox_container, text='Select all', variable=self.allSel, command=self.buildIt)
        self.selectAll.grid(row=0, column=0, sticky=W, padx=1, pady=3)
        self.cred = 0
        #   self.init() - initial scripts
        init_thread = threading.Thread(target=self.init)
        init_thread.start()
        logger.info('init')
        self.valid = True
        # self.cd_thread()
        #self.killswitch()

    #   Internal vars

        self.results_list = []  #   contains tuples of parsed results
        self.results_dataframe = pd.DataFrame()
        self.results_index = []
        self.index_list = []
        self.tag_list = []
        self.types_list = []
        self.names_list = []
        self.parent_list = []
        self.ids_list = []
        self.match_var = IntVar()
        self.tags_and_var = IntVar()
        self.tags_and_var.set(1)
        self.tags_or_var = IntVar()
        self.tags_or_var.set(0)
        self.search_ids = []
        self.hurl = ''
        self.url = ''

    def killswitch(self, *args):
        #   expiration date.

        if self.valid:
            logger.info("Valid version - 0.12")

        else:
            try:
                logger.info('Disabling GET')
                self.get_button.config( state='disabled')
                w = Notification('Expired version.')
                # w.button.config(command=)

            except Exception as e:
                logger.exception('killswitch')
                logger.exception(e)

    def cd_thread(self, *args):
        # th = threading.Thread(target=self.check_date)
        # th.start()
        pass

    def check_date(self, *args):
        # Online Date Validator.
        expire_date = datetime.datetime(2018, 11, 5)
        #   ^ Y M D
        __apiuser = 'would go here'
        __apikey = 'would go here as well'
        __url = 'http://api.timezonedb.com/v2.1/get-time-zone'
        params = {'key': __apikey, 'format': 'json', 'by': 'zone', 'zone': 'America/Guatemala', 'country': 'GT'}
        try:
            r = requests.get(__url, params=params, stream=True)
            for line in r.iter_lines():

                # iter through request.content to parse data instead of creating file.
                if line:
                    decoded_line = line.decode('utf-8')
                    json_file = (json.loads(decoded_line))
                date = json_file['formatted'][:10]
                current = datetime.datetime(2018, int(date[5:7]), int(date[8:]))

            if current >= expire_date:
                #   no longer valid
                logger.info("invalid version since: " + str(expire_date))
                self.valid = False
                self.killswitch()
            else:
                #   void
                logger.info("Valid version")
                print('valid self.valid:', self.valid)
                self.valid = True

        except Exception as e:
            logger.exception(e)
            logger.info('Unable to get date')

    def quit(self, *args):
        self.root.destroy()

    def init(self, *args):
        #   method to contain all initial scripts in a thread.
        #   fix exception for invalid creds / bad request
        self.sso = 0
        self.merging()
        self.buildIt()
        self.date_manager()
        self.readIt()
        self.prtg_db()
        self.idParse()
        # self.killswitch()
        self.running = False

    def clear_csv(self, *args):
        if self.id_option == 'import' or 'search':
            self.id_option = 'entry'
            self.id_entry.config(state='normal')
            self.idParse()
            logger.info('Clear CSV, self.idParse()')
        else:
            pass

    def idParse(self, *args):
        #   checks selection to enable or disable ID entry
        op = self.reqVar.get()
        opt = ['Sensortree', 'Sensors', 'Devices', 'Tickets', 'Messages', 'Groups']
        required = ['Values', 'Historic', 'Channels', 'Storedreports', 'Ticketdata', 'Object Status', 'getsensorstatus']
        last = self.idEntVar.get()
        if op in opt:
            self.id_entry.config(state='normal')
            self.csv_import_but.config(state='normal')
            if last == '' or last == 'Optional' or last == 'Required':
                self.idEntVar.set('Optional')
            else:
                self.idEntVar.set(last)

        elif op in required:
            self.id_entry.config(state='normal')
            self.csv_import_but.config(state='normal')
            if last == '' or last == 'Optional' or last == 'Required':
                self.idEntVar.set('Required')
            else:
                self.idEntVar.set(last)

        else:
            self.idEntVar.set('')
            self.csv_import_but.config(state='disabled')
            self.id_entry.config(state='disabled')

    def getHash(self, usn, pw, ip, http, port=''):
        #   /api/getpasshash.htm
        if http == 1:
            url = 'https://'

        else:
            url = 'http://'

        url += ip + ':' + str(port) + '/api/getpasshash.htm'
        #   print(url)
        par = {'username': usn,
               'password': pw,
               }
        try:
            r = requests.get(url, par, verify=False)
            if r.status_code == 200:
                logger.info('getHash OK')
                #   assign passhash to var and save in config
                data = r.content    #   passhash in bytes
                self.__ph = data.decode()
            else:
                logger.info('getHash ConnectionError\n' + str(r.status_code))
                return 'Get hash Error'
        except Exception as e:
            logger.exception('getHash exception')
            self.mng_error(e)

    #   sets csv internal db pandas objects
    def prtg_db(self, *args):
        if self.cred == 0:
            logger.info('prtg_db() cred == 0')
            pass

        else:

            try:
                retry = (requests.exceptions.Timeout, requests.exceptions.ConnectionError, requests.exceptions.HTTPError)
                #   default retry exceptions
                ip = self.__ip.get()
                port = self.__port.get()
                ht = self.__https.get()
                if ht == 1:
                    url = 'https://'
                else:
                    url = 'http://'

                url += ip + ':' + port + '/api/table.xml'
                #   table.xml?content=groups&output=csvtable
                #   table.xml?content=sensors&output=csvtable
                #   table.xml?content=devices&output=csvtable
                #   &columns=
                par = { 'username': self.__usn.get(), 'passhash': self.__ph,
                        'output': 'csvtable', 'columns': 'objid,name,tags,type,parentid,device,group,probe',
                        'noraw': 1, 'count':50000,
                        }
                #   for, each req (sensors, devices, groups)
                #   Animals - Pink Floyd
                par_s = dict(par)
                par_s['content'] = 'sensors'
                r1 = requests.get(url, par_s, verify=False)
                logger.info('prtgdb request Successful')
                logger.info(url)
                #   print(r1.url)
                f1 = open('sensors.csv', 'wb')

                f1.write(r1.content)
                logger.info('Created sensorsdb file')
                f1.close()
                self.dbpath = join(abspath(f1.name))
                logger.info(self.dbpath)
                #   saving absolute path of sensorsdb.csv to read on search
                #   after downloading and writing files make into data frames
                self.csv_db_set()

            except retry:
                logger.exception('prtgdb Exception')
                self.mng_error('DB request exception, unable to connect to PRTG Server')

    def csv_db_set(self, *args):
        #   each param is a panda csv
        #   all have matching cols
        #   ID, OBJECT, TYPE, TAGS, PARENT ID
        #   Adding column -> PARENT

        #   maybe add new column 'Parent Tags'
        try:
            if exists(self.dbpath):
                self.sensors = pd.read_csv(self.dbpath, dtype={'ID': np.int32, 'Parent ID': np.int32})
                logger.info('read sensordb')
            else:
                #   if files exist read them, else rebuild
                self.prtg_db()

            self.sensors.to_csv(self.dbpath)

        except Exception as e:
            # "ValueError: can only convert an array of size 1 to a Python scalar"
            #   raises a ValueError exception but it still makes the changes.
            print('An Expected ValueError Exception:', e)

    def rebuild(self, *args):
        try:
            if not exists('sensors.csv'):
                self.prtg_db()
                logger.info('Rebuilt db')
            else:
                remove('sensors.csv')
                self.prtg_db()
                logger.info('Deleted and Rebuilt.')

        except Exception as e:
            logger.exception('rebuild')
            self.mng_error('Rebuilding index error,', e)

    #   IDS getter&Setter / check internal db
    def parse_requests_ids(self, ids):

        #   -   Checks if id's are in internal db, returns valid_list & invalids (rep)
        #   -   rep are repeated, invalid (i.e. letters) or not in internal db
        #   ADD
        #
        #       -   check from prebuilt csv dataframe if valid id's are in database.csv (in csv.ID)
        #       -   create a bypass for this setting as well.
        #
        #   func that will return a list of all id's to iter through
        #   type(ids) == String.
        #   this func might be joined with open from disk to import csv
        #   as to keep csv management under one roof.
        #   which I guess could then become a class as to be accessed as a csv object always.
        #   hmms
        valid_list = []
        theList = []
        reps = []
        logger.info('parse_requests_ids, before type check')
        logger.info(ids)

        if type(ids) == list:
            logger.info(str(len(ids)))
            #   came from import
            #   check if in db.csv or w/e to finally return valid and invalid list
            #   db == self.sensors
            #   return confirmed valid_id list
            for _id in ids:
                #   print(_id)
                if _id in self.sensors['ID'].values or _id in self.sensors['Parent ID'].values:
                    #   check if its on either, then 
                    if _id not in valid_list:
                        valid_list.append(_id)
                    else:
                        continue

                elif _id in self.sensors['Parent ID'].values:
                    #   i suspect this became obsolete with the OR lets see
                    #   add all sensors under given parent ID
                    logger.info("Adding parent id in parse_requests_ids")
                    temp_df = self.sensors[self.sensors['Parent ID'] == _id]
                    for child_id in temp_df['ID'].values:
                        if child_id not in valid_list:
                            valid_list.append(child_id)
                        else:
                            continue
                else:
                    if _id not in reps:
                        reps.append(_id)
                    else:
                        continue

            logger.info('Returning valid ids from Import List:')
            logger.info(str(len(valid_list)))
            logger.info(valid_list)
            return valid_list, reps

        else:
            #   else, its coming from the Entry textbox
            #   strip, parse, count commas and then check if list in db.csv
            ids = ids.strip()

            commas = ids.count(',')
            logger.info(commas)
            try:
                for each in range(0, commas + 1):
                    #   for each comma in id's plus one (assuming 1,2,3,4...)
                    if each == commas:
                        #   its the last loop so last number should be after the last comma.
                        temp = ids
                        temp = temp.strip()
                        if temp.isdigit() and int(temp) not in theList:
                            theList.append(int(temp))
                        else:
                            reps.append(temp)
                            continue

                    else:
                        temp = ids[:ids.find(',')]
                        temp = temp.strip()
                        if temp.isdigit() and int(temp) not in theList:
                            theList.append(int(temp))
                            ids = ids[ids.find(',') + 1:]
                        else:
                            reps.append(temp)
                            ids = ids[ids.find(',') + 1:]
                            continue
                #   returns list of valid ids and the repeated or invalid ids list.
                for _id in theList:
                    if (_id in self.sensors['ID'].values or _id in self.sensors['Parent ID'].values) and _id not in valid_list:
                        valid_list.append(_id)
                    else:
                        continue

                logger.info('Returning valid ids from Entry list:')
                logger.info(str(len(valid_list)))
                logger.info(valid_list)
                return valid_list, reps

            except Exception as e:
                logger.exception('Parse req')
                self.mng_error('parse_req, ' + e)

    def import_csv(self, *args):
        #   function to open filedialog and parse a csv file
        #
        #       Must infer if its one line csv or from "liveData" results.
        #   feed whatever it finds to request_id parser.
        #   (should be given regardless since it creates the lists)
        #
        feed_list = []
        #   Abspath:

        path = filedialog.askopenfilename(defaultextension='*.csv')
        print(path)
        if path == '':
            return
        if path[path.rfind('.'):] != '.csv':
            self.mng_error('Invalid File type')
            return
        else:
            logger.info('Selected path for IMPORT CSV')
            csv = pd.read_csv(path)
            #   after getting the filepath into pandas
            try:
                feed = csv.__getattr__('ID')
                logger.info('CSV FROM API')
                for each_id in feed:
                    print(each_id)
                    if each_id not in feed_list:
                        feed_list.append(each_id)
                    else:
                        continue

                self.id_option = 'import'
                self.idEntVar.set('Imported CSV')
                self.id_entry.config(state='disabled')
                self.valid_ids, self.invalid_ids = self.parse_requests_ids(feed_list)
                #   requests_ids checks if in internal db
                #   sets self.valid_ids = [1,2] to parse in GET

            except AttributeError:
                #   if its not a df, ergo just "id, id, id" and no additional cols
                csv = pd.read_csv(path)
                #if len(csv) == 0:
                    #   0 means its only a header so its a single row "id, id, id"
                    #   len > 0 means its row by row
                
                #   if len of csv == 0, single row
                if len(csv) == 0:
                    for each_id in csv:
                        each_id = each_id.strip()
                        if each_id.isdigit():
                            feed_list.append(int(each_id))
                        else:
                            continue
                elif len(csv) > 0:
                    csv = pd.read_csv(path, header=None)
                    for each_id in csv[0]:
                        feed_list.append(each_id)

                logger.info('Set request id option to import')
                self.id_option = 'import'
                self.idEntVar.set('Imported CSV')
                self.id_entry.config(state='disabled')
                self.valid_ids, self.invalid_ids = self.parse_requests_ids(feed_list)

#   Date managers
    def verify_date(self, *args):
        #   get both start and end date to verify end is later than start
        st = self.idate_var.get()
        end = self.fdate_var.get()
        st_dt = revDate(st)
        end_dt = revDate(end)
        if st_dt > end_dt:
            return False
        else:
            return True

    def date_manager(self, *args):
        #   gets date intervals ready
        now = datetime.datetime.now()
        self.idate_var.set(dates(now))
        self.fdate_var.set(dates(now))

    def ah_start(self, *args):
        end = self.idate_var.get()
        form = revDate(end)
        s = autodate(form, '+')
        self.idate_var.set(s)

    def sh_start(self, *args):
        end = self.idate_var.get()
        form = revDate(end)
        s = autodate(form, '-')
        self.idate_var.set(s)

    def ah_end(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '+')
        self.fdate_var.set(s)

    def sh_end(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '-')
        self.fdate_var.set(s)

    def oneDay(self, *args):
        #   receives date text from button and gets date from entry to calculate new dates
        #   end in yyyy-mm... format.
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '1 Day')
        self.idate_var.set(s)

    def fiveDays(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '5 Days')
        self.idate_var.set(s) 

    def tenDays(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '10 Days')
        self.idate_var.set(s)       

    def twoWeeks(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '2 Weeks')
        self.idate_var.set(s)

    def oneWeek(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '1 Week')
        self.idate_var.set(s)

    def threeWeeks(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '3 Weeks')
        self.idate_var.set(s)

    def fourWeeks(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '4 Weeks')
        self.idate_var.set(s)

    def thirtyDays(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, '30 Days')
        self.idate_var.set(s)

    def lastDay(self, *args):
        self.endDay()
        self.startDay()

    def endDay(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, 'last df')
        self.fdate_var.set(s)

    def startDay(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, 'last ds')
        self.idate_var.set(s)

    def lastMonth(self, *args):
        self.startMonth()
        self.endMonth()
        #   two funcs, second one updates fdate_var

    def startMonth(self, *args):
        end = self.fdate_var.get()
        form = revDate(end)
        s = autodate(form, 'last s')
        self.idate_var.set(s)

    def endMonth(self, *args):
        start = self.idate_var.get()
        form = revDate(start)
        s = autodate(form, 'last f')
        self.fdate_var.set(s)


#   End of date managers

    def merging(self, *args):
        if self.mergeVar.get() == 0:
            self.filename_entry.config(state='disabled')
            self.keep_cb.config(state='disabled')
            self.remVar.set(0)
        else:
            self.keep_cb.config(state='normal')
            #self.filename_entry.config(state='normal')

#   Search engine
    def ttl(self, var):
        #   text to list
        #   recieves a string with 'item, item, item' returns item_list[item, item, item]
        try:
            queries = []
            var = var.strip()
            commas = var.count(',')
            for each in range(0, commas + 1):
                if each == commas:
                    temp = var.strip()
                    if temp not in queries:
                        queries.append(temp)
                    else:
                        continue

                else:
                    temp = var[:var.find(',')]
                    temp = temp.strip()
                    if temp not in queries:
                        queries.append(temp)
                        var = var[var.find(',') + 1:]
                    else:
                        var = var[var.find(',') + 1:]

        except Exception as e:
            self.mng_error('Parsing queries error,', e)

    def search_window(self, *args):
        #   search db
        self.prtg_db()
        logger.info('Created search window')
        self.search_top = Toplevel()
        self.search_top.title('Search')
        self.search_top.minsize(600, 400)
        self.search_top.iconbitmap('imgs\prtg_active.ico')
        sew = 50
        #   search entry width lol
        cbc = 9

        #   checbox column
        entcols = 3
        entcolsp = 10
        self.query_frame = Frame(self.search_top, width=600, height=200)
        self.query_frame.grid(row=0)
        self.search_cat = Label(self.query_frame, text='Categories', font=font)
        self.search_cat.grid(row=0, column=0, columnspan=10, sticky=W)

        self.stags_label = Label(self.query_frame, text='Tags')
        self.stags_label.grid(row=2, column=0, columnspan=2, sticky=W)
        self.s_tags_ent = Entry(self.query_frame, width=sew, textvariable=self.search_tags_var)
        self.s_tags_ent.grid(row=2, column=entcols, columnspan=entcolsp, sticky=W)
        #   uses OR/And

        self.total_results = Label(self.query_frame, text="Total Sensors:", font=colFont)
        self.total_results.grid(row=1, column=14, sticky=W)
        self.total_results_n = Label(self.query_frame)
        self.total_results_n.grid(row=1, column=15, sticky=W)

        self.hist_eta = Label(self.query_frame, text="Historic ETA:", font=colFont)
        self.hist_eta.grid(row=2, column=14, sticky=W)
        self.hist_eta_n = Label(self.query_frame)
        self.hist_eta_n.grid(row=2, column=15, sticky=W)

        Label(self.query_frame, text="Logic operator:").grid(row=1, column=7)
        self.tags_and = Checkbutton(self.query_frame, text='AND', variable=self.tags_and_var, onvalue=1, offvalue=0, command=self.andor)
        self.tags_and.grid(row=1, column=cbc, sticky=W, columnspan=1, padx=2)

        self.tags_or = Checkbutton(self.query_frame, text='OR', variable=self.tags_or_var, onvalue=1, offvalue=0, command=self.orand, state='disabled')
        self.tags_or.grid(row=1, column=cbc + 1, sticky=W, columnspan=2, padx=4)

        self.stypes_label = Label(self.query_frame, text='Types')
        self.stypes_label.grid(row=3, column=0, columnspan=2, sticky=W)
        self.s_type_ent = Entry(self.query_frame, width=sew, textvariable=self.search_types_var)
        self.s_type_ent.grid(row=3, column=entcols, columnspan=entcolsp, sticky=W)
        #   uses OR always

        self.stypes_label = Label(self.query_frame, text='Sensor Name')
        self.stypes_label.grid(row=4, column=0, columnspan=2, sticky=W)
        self.s_name_ent = Entry(self.query_frame, width=sew, textvariable=self.search_name_var)
        self.s_name_ent.grid(row=4, column=entcols, columnspan=entcolsp, sticky=W)

        self.sparents_label = Label(self.query_frame, text='Device')
        self.sparents_label.grid(row=5, column=0, columnspan=3, sticky=W)
        self.s_parent_ent = Entry(self.query_frame, width=sew, textvariable=self.search_parent_var)
        self.s_parent_ent.grid(row=5, column=entcols, columnspan=entcolsp, sticky=W)


        self.sgrp_label = Label(self.query_frame, text='Group')
        self.sgrp_label.grid(row=6, column=0, columnspan=3, sticky=W)
        self.s_grp_ent = Entry(self.query_frame, width=sew, textvariable=self.search_grp_var)
        self.s_grp_ent.grid(row=6, column=entcols, columnspan=entcolsp, sticky=W)

        self.sprb_label = Label(self.query_frame, text='Probe')
        self.sprb_label.grid(row=7, column=0, columnspan=3, sticky=W)
        self.s_prb_ent = Entry(self.query_frame, width=sew, textvariable=self.search_prb_var)
        self.s_prb_ent.grid(row=7, column=entcols, columnspan=entcolsp, sticky=W)

        #   Search buttons
        #   Search, previous results, refilter, USE, Reset 
        #   case sens
        #   checkbox with booleanvar or someshit and use 
        #   case=False, case=booleanvar.get()
        bw = 8
        self.searchBut = Button(self.query_frame, text='Search', width=bw, command=self.search_all)
        self.searchBut.grid(row=8, column=3, columnspan=2, sticky=E, pady=3)

        self.rebBut = Button(self.query_frame, text='Rebuild Index', width=bw + 2, command=self.rebuild)
        self.rebBut.grid(row=8, column=0, columnspan=2, sticky=E, pady=3, padx=3)

        self.useBut = Button(self.query_frame, text='Use Results', width=bw + 2, font=colFont,
                             command=self.add_notification)
        self.useBut.grid(row=8, column=12, columnspan=2, sticky=E, pady=3)

        self.useSel = Button(self.query_frame, text='Use Selected', width=bw + 3, font=colFont,
                             command=self.add_sel_notification)
        self.useSel.grid(row=8, column=14, columnspan=2, sticky=E, pady=3)

        self.clearBut = Button(self.query_frame, text='Reset', width=bw, command=self.clear_search)
        self.clearBut.grid(row=8, column=7, columnspan=3, sticky=E, pady=3)

        self.clearBut = Button(self.query_frame, text='Refilter', width=bw, state='disabled')
        self.clearBut.grid(row=8, column=5, columnspan=3, sticky=E, pady=3)

        #   sensors[sensors['string column'].str.contains(query, case=False)]
        #   Thread for ID's since its a list ? is it the same speed really ?
        #   for each in requests_id_returned list if sensors[sensors['ID'] == _id] add to results_dataframe
        self.results_frame = Frame(self.search_top)
        #   width=600, height=300
        self.results_frame.grid(row=1, columnspan=400, sticky=NSEW)
        self.results_frame.grid_propagate(1)
        self.results_lb = MultiTwo(self.results_frame, self.index_list, self.results_dataframe)
        self.results_lb.grid(sticky=NSEW)
        #self.results_lb.tree.grid(in_=self.results_lb.parent, row=0, column=0, sticky=NSEW)

    def indexes(self, dataframe):
        for each in dataframe:
            if each not in self.index_list:
                self.index_list.append(each)
            else:
                continue

    def search_all(self, *args):
        #   | == or
        #   & == and
        n = self.search_name_var.get()
        ty = self.search_types_var.get()
        ta = self.search_tags_var.get()
        pa = self.search_parent_var.get()   #   Device (direct parent)
        gr = self.search_grp_var.get()
        prb = self.search_prb_var.get()
        logger.info('Prompted search')

        if self.tags_and_var.get() == 1:
            self.results_dataframe = self.sensors[self.sensors['Object'].str.contains(n, case=False) &  self.sensors['Type'].str.contains(ty, case=False) &  self.sensors['Tags'].str.contains(ta, case=False) &  self.sensors['Device'].str.contains(pa, case=False)
             &  self.sensors['Group'].str.contains(gr, case=False) &  self.sensors['Probe'].str.contains(prb, case=False)].drop_duplicates()
        else:
            self.results_dataframe = self.sensors[self.sensors['Object'].str.contains(n, case=False) |  self.sensors['Type'].str.contains(ty, case=False) |  self.sensors['Tags'].str.contains(ta, case=False) |  self.sensors['Device'].str.contains(pa, case=False)
            |  self.sensors['Group'].str.contains(gr, case=False) |  self.sensors['Probe'].str.contains(prb, case=False)].drop_duplicates()

        self.index_list = self.results_dataframe.index.tolist()
        logger.info('Parsed all indexes')
        self.total_results_n.config(text=str(len(self.index_list)))
        heta_seconds = 12 * len(self.index_list)
        text = str(datetime.timedelta(seconds=heta_seconds))
        self.hist_eta_n.config(text=text)
        self.results_lb.grid_forget()
        self.results_lb = self.results_lb.update(self.index_list, self.results_dataframe)
        self.results_lb.grid(sticky=NSEW)
        self.search_get()
        #   results.values.view(), returns np.array where each index contains all columns independently.
        #   len(self.results_index)

    def clear_search(self, *args):
        self.search_name_var.set('')
        self.search_types_var.set('')
        self.search_tags_var.set('')
        self.search_parent_var.set('')
        self.search_grp_var.set('')
        self.search_prb_var.set('')
        self.results_lb.clear()

    def search_get(self, *args):
        self.id_option = 'search'
        self.search_ids = []
        for each_index in self.index_list:
            self.search_ids.append(self.results_dataframe['ID'][each_index])

    def add_notification(self, *args):
        #   receive an exception message and display it.
        self.idEntVar.set('From Search Results')
        self.notWindow = Toplevel()
        self.notWindow.minsize(150, 125)
        x = (self.scx / 2) - (150 / 2)
        y = (self.scy / 2) - (125 / 2)
        self.notWindow.geometry('%dx%d+%d+%d' % (150, 125, x, y))
        self.notWindow.iconbitmap('imgs\prtg_active.ico')
        self.notWindow.title('Adding ID\'s')
        Message(self.notWindow, text='Added search results!', justify=CENTER, width=95).grid(padx=5, pady=5, row=1, column=0, columnspan=15, sticky=W + E)
        self.is_k = Button(self.notWindow, text='Ok', width=10, command=self.is_kill)
        self.is_k.grid(row=10, column=0, sticky=W + E, padx=5, pady=5)
        self.cancel_req = 0
        logger.info('Added search results for Get')

    def add_sel_notification(self, *args):

        self.selected_index = get_id_index(list(self.results_lb.getsel()), list(self.results_lb.getsel2()))
        #   get currently selected + get all result indexes
        #   receives indexes to parse results id list, self.search_ids.
        #   next remove not selected ids from list by matching indexes
        self.search_ids = set_id_index(self.selected_index, self.search_ids)

        self.idEntVar.set('From Search Results')
        self.notWindow = Toplevel()
        self.notWindow.minsize(150, 125)
        x = (self.scx / 2) - (150 / 2)
        y = (self.scy / 2) - (125 / 2)
        self.notWindow.geometry('%dx%d+%d+%d' % (150, 125, x, y))
        self.notWindow.iconbitmap('imgs\prtg_active.ico')
        self.notWindow.title('Adding ID\'s')
        Message(self.notWindow, text='Added selected results!\n' + str(len(self.search_ids)) + ' sensors.',
                justify=CENTER, width=95).grid(padx=5, pady=5, row=1, column=0, columnspan=15, sticky=W + E)
        self.is_k = Button(self.notWindow, text='Ok', width=10, command=self.is_kill)
        self.is_k.grid(row=10, column=0, sticky=W + E, padx=5, pady=5)
        self.cancel_req = 0
        logger.info('Added search results for Get')

    def is_kill(self, *args):
        self.notWindow.destroy()
        self.search_top.destroy()

    def orand(self, *args):
        self.tags_and_var.set(0)
        self.tags_or_var.set(1)

    def andor(self, *args):
        self.tags_and_var.set(1)
        self.tags_or_var.set(0)


#   End of Search engine
    def mng_error(self, exception):
        #   receive an exception message and display it.
        logger.info('Error prompted: ' + str(exception))
        errorWindow = Toplevel()
        x = (self.scx / 2) - (250 / 2)
        y = (self.scy / 2) - (175 / 2)
        errorWindow.minsize(250, 175)
        errorWindow.geometry('%dx%d+%d+%d' % (250, 175, x, y))
        errorWindow.iconbitmap('imgs\prtg_active.ico')
        errorWindow.title('Error!')
        Message(errorWindow, text=exception, justify=CENTER, width=100).grid(row=1, columnspan=5, sticky=W + E)
        Button(errorWindow, text='Ok', command=errorWindow.destroy, width=8).grid(row=10, sticky=S)

    def queue_status(self, *args):
        logger.info('Created queue window')
        self.queue_top = Toplevel()
        self.queue_top.title('Requests')
        self.queue_top.minsize(185, 165)
        self.queue_top.iconbitmap('imgs\prtg_active.ico')
        x = (self.scx / 2) - (175 / 2)
        y = (self.scy / 2) - (150 / 2)
        self.queue_top.geometry('%dx%d+%d+%d' % (175, 150, x, y))

        self.processing = Label(self.queue_top, text='Processing...', font=font,  relief=GROOVE)
        self.processing.grid(row=0, column=0, columnspan=10, sticky=W + E, padx=3)

        self.req_label = Label(self.queue_top, text='Requesting: ' + self.reqVar.get() + ' data')
        self.req_label.grid(row=2, column=0, columnspan=5, padx=3)
        self.am = Label(self.queue_top, text='Requests:')
        self.am.grid(row=3, column=0, sticky=W, padx=3)
        self.amount = Label(self.queue_top, font=font2)
        self.amount.grid(row=3, column=2, sticky=W, columnspan=8, padx=3)

        #   queue ETA
        self.eta_text = Label(self.queue_top)
        self.eta_text.grid(row=4, column=2, sticky=W, columnspan=8, padx=3)
        self.estimate = Label(self.queue_top, text='Estimated Time:')
        self.estimate.grid(row=4, column=0, sticky=W, padx=3)

        #   queue Time elapsed
        self.qta_text = Label(self.queue_top)
        self.qta_text.grid(row=5, column=2, sticky=W, columnspan=8, padx=3)
        self.elapsed = Label(self.queue_top, text='Elapsed Time:')
        self.elapsed.grid(row=5, column=0, sticky=W, padx=3)

        self.merge_status = Label(self.queue_top, text='Merge files:')
        self.merge_status.grid(row=6, column=0, sticky=W, padx=3)
        self.merge_text = Label(self.queue_top)
        self.merge_text.grid(row=6, column=2, sticky=W, padx=3)

        self.cancel_queue_but = Button(self.queue_top, text='Cancel', command=self.stop_thread, width=8)
        self.cancel_queue_but.grid(row=9, columnspan=6, sticky=W + E, padx=3)

        #   cancel
        #   set errors == 9 and to raise Manual Cancel
        #       this way it finishes the current file download/manage

    def dest(self, *args):
        try:
            self.queue_top.destroy()
        except AttributeError:
            print('No currently open window to close')

    def buildIt(self, *args):  #
        self.checks()
        self.idParse()
        self.check_gc()
        op = self.reqVar.get()
        tout = self.allSel.get()
        # self.idParse()
        # dictOfChecks -> dictionary with key:value == 'reqSelection': listOfParams
        # takes the selected request type from dropdown (self.reqVar.get())
        # creates a new object of itself and assigns it to itself but with new list value. :)
        checks = ['Sensortree', 'Groups', 'Sensors', 'Devices', 'Tickets', 'Messages',
                  'Values', 'Channels', 'StoredReports', 'Ticketdata', 'Reports',
                  'Object Status', 'getsensorstatus']
        if op in checks:
            self.historic_par.grid_forget()
            self.checkbox_container.grid(row=1)
            self.selectAll.grid(row=1, column=0, sticky=W, padx=1, pady=3)
            self.title_label_ro.config(text='Column Select')
            if tout == 0:
                self.theBoxes.grid_forget()  # first removes existing widget (original object)
                self.theBoxes = self.theBoxes.updated(
                    dictOfChecks[op])  # uses module that returns a new object of same class but with new list
                self.theBoxes.grid()  # inserts it to frame.
            else:
                self.theBoxes.grid_forget()
                self.theBoxes = self.theBoxes.checked(dictOfChecks[op])
                self.theBoxes.grid()

        elif op == 'Historic':
            self.checkbox_container.grid_forget()
            self.theBoxes.grid_forget()
            self.selectAll.grid_forget()
            self.title_label_ro.config(text='Historic Data')
            self.historic_par.grid(row=1)
            self.date_manager()

    def checks(self, *args):
        #   check format and request type to disable/enable settings
        a = self.outpVar.get()
        b = self.reqVar.get()
        c = self.remVar.get()

        if a == 'CSV':
            self.merge_cb.config(state='active')
            self.keep_cb.config(state='active')
            self.mergeVar.set(1)
        else:
            self.filename_var.set('')
            self.mergeVar.set(1)
            self.filename_entry.config(state='disabled')
            self.merge_cb.config(state='disabled')
            self.keep_cb.config(state='disabled')

        #if b == 'Messages' or b == 'Tickets':
        #    self.datefilterdd.config(state="active")
        #    self.datefilterVar.set('None')
        #else:
        #    self.datefilterdd.config(state="disabled")
        #    self.datefilterVar.set('None')

        if b == 'Sensortree':
            self.outpVar.set('XML')
            self.outpDD.config(state='disabled')
            self.rawVar.set(1)
            self.raw_cb.config(state='disabled')

        else:
            self.rawVar.set(1)
            self.outpDD.config(state='active')
            self.raw_cb.config(state='active')

        if b != 'Historic':
            self.filterTagsEnt.config(state='normal')
            self.count_entry.config(state='normal')
            self.type_entry.config(state='normal')
        else:
            #   self.outpVar.set('CSV')
            self.filterTagsEnt.config(state='disabled')
            self.count_entry.config(state='disabled')
            self.type_entry.config(state='disabled')

        if self.mergeVar.get() == 0:
            self.remVar.set(0)
            self.keep_cb.config(state='disabled')
        self.merging()

    def setPath(self, *args):
        try:
            path = filedialog.askdirectory()
            if path == '': 
                pass
            else:
                logger.info('Selected new path')
                self.savePath.set(path)
                logger.info(path)
            self.preferences = 1
        except Exception as e:
            logger.exception('Save to exception')
            self.errors(e)

    def make_request(self, http, ip, port, request, output, username, passhash, raw, merge, count='', ID='', columns=None, path='', tags='', types=''):

        useContent = [
            'Channels', 'Devices', 'Groups', 'Messages',
            'Reports', 'Sensors', 'Sensortree', 'StoredReports',
            'Ticketdata', 'Tickets', 'Toplists', 'Values',

        ]
        dontUseContent = {
            #   these requests don't use the content=* type req. (checkboxes)
            'Sensor Details': 'getsensordetails',
            'Sensor Types in Use': 'sensortypesinuse.json',  # only json
            'Tree node stats': 'gettreenodestats.xml',  # only xml
            'System Status': 'getstatus',  # + .htm?id=0 / .xml?id=0
            'Ticket Status': 'getticketstatus.htm',  # ?id=ticketid
            'Ticket Subject': 'getticketmessage.htm',
            'Object Property': 'getobjectproperty.htm',  # ?id=ticketid + name=property
            'Object Status': 'getobjectstatus.htm',  # ?id=ticketid + name=column

        }

        retry = (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
        )
        max_retries = 3
        timeout = 5
        for i in range(max_retries):
            logger.info('Try number:', i, 'for:', request)
            #   Console 'logs'
            try:
                par = {
                    'username': username,
                    'passhash': passhash,
                }

                #   depending request type we add more parameters.

                if http == 1:
                    #   https
                    self.url = 'https://'
                elif http == 0:
                    self.url = 'http://'

                self.url += str(ip) + ':' + port + '/api/'
                # then depending of request type we finish the URL

                if request in useContent:
                    # uses /api/table.* & output=*
                    self.url += 'table.'
                    if output == 'JSON':
                        self.url += 'json'
                    else:
                        self.url += 'xml'

                    '''
                    if dates != 'None':
                        dates = dates.lower()
                        if ' ' in dates:
                            dates = dates[:dates.find(' ')] + dates[dates.find(' ') + 1:]
                            par['filter_drel'] = dates
                        else:
                            par['filter_drel'] = dates
                    '''
                    output = output.lower()
                    output2 = output
                    if output == 'csv':
                        output += 'table'
                        #   csv request is csvtable

                    if count.isdigit():
                        par['count'] = count

                    if tags != '':
                        par['filter_tags'] = '@tag(' + tags + ')'
                        #   must be exact match to work in Request
                        #   will make internal search instead to make it valid.

                    if types != '':
                        par['filter_type'] = types

                    request = request.lower()
                    par['content'] = request
                    par['output'] = output
                    par['columns'] = columns
                    par['noraw'] = raw
                    output = output2
                    sleep(0.5)
                    #   makes output .csv again
                    if ID != '':
                        par['id'] = ID
                        r = requests.get(self.url, params=par, verify=False)
                        fileFolder(request, output, path, r.content, merge, ID)
                        logger.info('ID: '+ str(ID))
                        logger.info('HTTP Code:' +  str(r.status_code))
                        print('URL:', r.url)
                        self.url = ''
                        return

                    else:
                        r = requests.get(self.url, params=par, verify=False)
                        r.url
                        logger.info(merge)
                        fileFolder(request, output, path, r.content, merge, ID='')
                        logger.info('HTTP Code:' +  str(r.status_code))
                        print('URL:', r.url)
                        self.url = ''
                        return

            #except retry:
            except retry:
                logger.exception('Retry ' + str(self.error_count))
                #self.mng_error(e)
                #   if any of the above exceptions occurs retry.
                self.error_count += 1
                sleep(timeout)
                continue
            else:
                return 'Error of sorts'
        else:
            pass

    def hist_req(self, http, ip, port, output, username, passhash, start_date, end_date, avg, ID, path, merge):
        retry = (
            requests.exceptions.Timeout,
            requests.exceptions.ConnectionError,
            requests.exceptions.HTTPError,
                )
        max_retries = 2
        timeout = 6

        #   historic_url
        for i in range(max_retries):
            try:
                logger.info('Try number: ' + str(i) + ' for Historic')
                if http == 1:
                    #   https
                    self.hurl = 'https://'
                    logger.info('SSL')
                elif http == 0:
                    self.hurl = 'http://'
                    logger.info('No SSL.')
                self.hurl += str(ip) + ':' + port + '/api/historicdata.'

                if output == 'JSON':
                    self.hurl += 'json'

                elif output == 'XML':
                    self.hurl += 'xml'

                elif output == 'CSV':
                    self.hurl += 'csv'
                    output = output.lower()

                par = {'username': username, 'passhash': passhash, 'id': ID, 'avg': avg,
                       'sdate': start_date, 'edate': end_date}
                r = requests.get(self.hurl, par, verify=False)
                print(r.url)
                fileFolder('Historic', output, path, r.content, merge, ID)
                self.hurl = ''
                return
            except retry:
                logger.exception('Retry ' + str(self.error_count))
                #   if any of the above exceptions occurs retry.
                self.error_count += 1
                sleep(timeout)
                continue
        else:
            pass

    def elapsedTime(self, *args):
        time = 0
        while self.running:
            time += 1
            stopwatch = str(datetime.timedelta(seconds=time))
            self.qta_text.config(text=stopwatch)
            sleep(1)

    def elapsedThread(self, *args):
        self.time_thread = threading.Thread(target=self.elapsedTime)
        self.time_thread.start()

    def update_queue(self, *args):
        try:
            total = str(self.iter) + ' / ' + str(len(self.valid_ids))
            self.amount.config(text=total)
        except Exception as e:
            logger.exception(e)
            self.stop_thread()

    def getStates(self, *args):
        #   gets checkbox / entry states
        #   makes

        if self.cred == 0:
            logger.info('GET without Creds')
            t = Toplevel()
            t.pack_propagate(0)
            t.minsize(125, 125)
            t.iconbitmap('imgs\prtg_active.ico')
            t.title('Get')
            x = (self.scx / 2) - (125 / 2)
            y = (self.scy / 2) - (125 / 2)
            self.t.geometry('%dx%d+%d+%d' % (125, 125, x, y))
            Message(t, text='No server settings.').pack(padx=5, pady=4)
            Button(t, text='OK', width=8, command=t.destroy).pack(padx=5, pady=4)
        else:
            #   Give to make_requeest
            #       -   self.savePath , output
            #       -   creds
            #       -   op
            #       -   count, tags, types, ids
            #       -   merge / keep option
            while self.running:
                logger.info('GET with Cred')
                self.dest()
                mt = 'No'
                self.get_button.config(state='disabled')
                self.queue_status()
                self.elapsedThread()
                if not self.verify_date():
                    self.mng_error('Invalid Dates')
                    self.stop_thread()
                    return

                try:
                    remove = self.remVar.get()
                    merge = self.mergeVar.get()
                    if merge == 1:
                                mt = 'Yes'
                    self.merge_text.config(text=mt)
                    self.error_count = 0
                    op = self.reqVar.get()
                    print('Current id parse option:', self.id_option)
                    if self.id_option == 'entry':
                        self.valid_ids, self.invalid_ids = self.parse_requests_ids(self.idEntVar.get())

                    if self.id_option == 'search':
                        self.valid_ids, self.invalid_ids = self.parse_requests_ids(self.search_ids)

                    if op == 'Historic':
                        if len(self.valid_ids) == 0:
                            logger.info('No valid id\'s')
                            self.mng_error('No valid id\'s')
                            self.stop_thread()
                            self.get_button.config(state='active')
                            self.dest()
                            return

                        if len(self.valid_ids) < 7:
                            self.sleep_time = 9
                        elif len(self.valid_ids) < 7:
                            self.sleep_time = 11

                        in_date = self.idate_var.get()
                        fin_date = self.fdate_var.get()
                        if not revDate(in_date):
                            logger.info('Invalid Start Date')
                            self.mng_error('Invalid Start Date')
                            self.stop_thread()
                            self.get_button.config(state='active')
                            self.dest()
                            return

                        elif not revDate(fin_date):
                            logger.info('Invalid End Date')
                            self.mng_error('Invalid End Date')
                            self.stop_thread()
                            self.get_button.config(state='active')
                            self.dest()
                            return

                        else:
                            #   its format valid so use dates
                            #   though not necessarily valid req date.

                            avg = self.avg.get()
                            self.start_time = datetime.datetime.now()
                            #   Set 'ETA:' self.eta // seconds * amount of id's
                            eta_seconds = 12 * len(self.valid_ids)
                            self.eta = str(datetime.timedelta(seconds=eta_seconds))
                            self.eta_text.config(text=self.eta)
                            self.merge_text.config(text=mt)
                            for each_id in self.valid_ids:
                                #   set current Iter at every for
                                self.update_queue()

                                if self.error_count < 9 and self.cancel_req == 0:
                                    self.hist_req(self.__https.get(), self.__ip.get(), self.__port.get(),
                                                  self.outpVar.get(), self.__usn.get(),
                                                  self.__ph, in_date, fin_date, avg,
                                                  ID=each_id, path=self.savePath.get(), merge=merge)
                                    self.iter += 1
                                    if self.cancel_req == 1:
                                        self.cancel_req = 0
                                        logger.info('Manual cancel')
                                        self.mng_error('Manual Cancel')
                                        break
                                    else:
                                        sleep(self.sleep_time)
                                        #self.sleep_event.wait(self.sleep_time)

                                else:
                                    if self.error_count >= 9:
                                        logger.info('Too many failed connections')
                                        self.mng_error('Too many failed connections')
                                        break
                                    elif self.cancel_req == 1:
                                        self.cancel_req = 0
                                        logger.info('Manual cancel')
                                        self.mng_error('Manual Cancel')
                                        break

                            if merge == 1:
                                #   path, ids
                                #   do the do
                                self.processing.config(text="Merging files...")
                                logger.info('Start Merge')
                                csvmerger(self.savePath.get(), self.valid_ids, remove=remove, name=self.customFileName.get())

                            self.error_count = 0
                            self.cancel_req = 0
                            self.iter = 1
                            self.running = False
                            self.get_button.config(state='active')
                            self.processing.config(text='Done!')
                            logger.info('RequestQueue Finished')
                            self.cancel_queue_but.config(text='Done', command=self.queue_top.destroy)

                    else:
                        #   get checkbox states
                        if self.id_option == 'search':
                            self.valid_ids, self.invalid_ids = self.parse_requests_ids(self.search_ids)
                        current = list(self.theBoxes.state())
                        columns = findNJoin(current)
                        if len(self.valid_ids) > 0:

                            for each_id in self.valid_ids:
                                self.update_queue()
                                if self.error_count < 9 and self.cancel_req == 0:
                                    self.make_request(self.__https.get(), self.__ip.get(), self.__port.get(), op,
                                                      self.outpVar.get(), self.__usn.get(),
                                                      self.__ph, self.rawVar.get(), self.mergeVar.get(),
                                                      ID=each_id, columns=columns, path=self.savePath.get(),
                                                      tags=self.filterTagsVar.get(), types=self.type_var.get())
                                    sleep(0.1)
                                    self.iter += 1
                                else:
                                    if self.error_count >= 9:
                                        logger.info('Too many failed connections')
                                        self.mng_error('Too many failed connections')
                                        break
                                    elif self.cancel_req == 1:
                                        self.cancel_req = 0
                                        logger.info('Manual cancel')
                                        self.mng_error('Manual Cancel')
                                        break

                            if merge == 1:
                                #   path, ids
                                #   do the do
                                self.processing.config(text="Merging files...")
                                logger.info('Start Merge')
                                csvmerger(self.savePath.get(), self.valid_ids, remove=remove, name=self.customFileName.get())
                            self.error_count = 0
                            self.cancel_req = 0
                            self.iter = 1
                            self.running = False
                            self.get_button.config(state='active')
                            self.processing.config(text='Done!')
                            logger.info('RequestQueue Finished')
                            self.cancel_queue_but.config(text='Done', command=self.queue_top.destroy)

                        else:
                            #   the ones that don't require ID's L O L
                            if self.error_count < 9 and self.cancel_req == 0:
                                total = str(self.iter) + ' / ' + str(1)
                                self.amount.config(text=total)
                                self.make_request(self.__https.get(), self.__ip.get(), self.__port.get(), op,
                                                  self.outpVar.get(), self.__usn.get(),
                                                  self.__ph, self.rawVar.get(), self.mergeVar.get(),
                                                  ID='', columns=columns, path=self.savePath.get(),
                                                  tags=self.filterTagsVar.get(), types=self.type_var.get())
                                sleep(0.1)

                            self.error_count = 0
                            self.cancel_req = 0                            
                            self.iter = 1
                            self.running = False
                            self.get_button.config(state='active')
                            self.processing.config(text='Done!')
                            logger.info('RequestQueue Finished')
                            self.cancel_queue_but.config(text='Done', command=self.queue_top.destroy)
                            return

                except Exception as e:
                    logger.exception('Request Exception')
                    self.mng_error('GET' + str(e))
                    self.stop_thread()

    def savethread(self, *args):
        self.svthread = threading.Thread(target=self.save)
        self.svthread.start()

    def serverSettings(self, *args):
        #   server settings/credential input window
        #   if no credentials file is found should be prompted.
        try:
            if self.sso == 1:
                self.tp.destroy()
                self.sso = 0
            else:
                self.tp = Toplevel()
                self.sso = 1
                self.tp.title('Settings')
                self.tp.iconbitmap('imgs\prtg_active.ico')
                self.tp.minsize(270, 275)
                x = (self.scx / 2) - (245 / 2)
                y = (self.scy / 2) - (275 / 2)
                self.tp.geometry('%dx%d+%d+%d' % (245, 275, x, y))
                Button(self.tp, text='Connect', width=8, command=self.savethread).grid(row=10, column=1, columnspan=3, sticky=W, padx=3, pady=3)
                Button(self.tp, text='Cancel', width=7, command=self.tp.destroy).grid(row=10, column=3, columnspan=4, sticky=W, padx=3, pady=3)

                self.title_serv = Label(self.tp, text='PRTG User and Server Settings', anchor=W, relief=GROOVE)
                self.title_serv.grid(row=0, sticky=W + E, padx=3, pady=2, columnspan=30)
                Label(self.tp, text='Username').grid(row=1, column=0, padx=3, pady=3, sticky=W)
                Label(self.tp, text='Password').grid(row=2, column=0, padx=3, pady=3, sticky=W)
                Label(self.tp, text='Server IP').grid(row=3, column=0, padx=3, pady=3, sticky=W)
                Label(self.tp, text='Port').grid(row=4, column=0, padx=3, pady=3, sticky=W)

                us = Entry(self.tp, width=16, textvariable=self.__usn)
                us.grid(row=1, column=2, padx=3, pady=3)

                pw = Entry(self.tp, width=16, textvariable=self.__pw, show='*')
                pw.grid(row=2, column=2, padx=3, pady=3)

                ip = Entry(self.tp, width=16, textvariable=self.__ip)
                ip.grid(row=3, column=2, padx=3, pady=3)

                port = Entry(self.tp, width=12, textvariable=self.__port)
                port.grid(row=4, column=2, padx=3, pady=3, sticky=W)
                settErr = Message(self.tp)

                self.httpCh = Checkbutton(self.tp, text='SSL / HTTPS', variable=self.__https, onvalue=1, offvalue=0)
                self.httpCh.grid(row=4, column=3, columnspan=3, padx=3, pady=3)

        except Exception as e:
            logger.exception('serverSettings')

    def save(self, *args):  # save server settings into txt file
        # missing:
        # encrypt / decrypt file
        try:
            settErr = Message(self.tp, text='Connecting to PRTG...', width=90)
            settErr.grid(row=11, column=0, columnspan=15, sticky=W + E)
            logger.info('Testing Connection')
            t = testConn(self.__usn.get(), self.__pw.get(), self.__ip.get(), self.__https.get(), self.__port.get())  # validates inputs and tries to connect
            #   t will be tuple with (boolean,status code)
            #   print(t)

            if t[0]:
                logger.info('Test successful, getting hash.')
                self.getHash(self.__usn.get(), self.__pw.get(), self.__ip.get(), self.__https.get(), self.__port.get())
                self.tp.destroy()
                t2 = Toplevel()
                t2.title('Successful')
                t2.iconbitmap('imgs\prtg_active.ico')
                t2.minsize(125, 125)
                x = (self.scx / 2) - (125 / 2)
                y = (self.scy / 2) - (125 / 2)
                t2.geometry('%dx%d+%d+%d' % (125, 125, x, y))
                credSave(self.__usn.get(), self.__ph, self.__ip.get(), self.__https.get(), self.__port.get())
                Message(t2, text='Successfully connected and saved credentials').pack(fill=BOTH, padx=3, pady=4)
                Button(t2, text='OK', width=7, command=t2.destroy).pack(padx=3, pady=4)
                logger.info('Got Hash and Saved Creds')
                #   Once it successfully connects create the internal db.
                self.prtg_db()
                self.readIt()
                #   since it worked just auto read creds and set having creds True

            else:
                logger.info('Unable to test connection')
                logger.info(t[1])
                self.txt = "Unable to connect, check settings or verify PRTG services are running"
                settErr = Message(self.tp, text=self.txt)
                settErr.grid(row=11, column=0, columnspan=15, sticky=W + E)
                # print('test')

        except Exception as e:
            logger.exception('TestConn')
            self.mng_error(e)

    def readIt(self, *args):
        #   func to find and setup any preferences or credentials
        if self.cred == 0:
            if exists('qd.rst'):
                try:
                    f = open('qd.rst', 'r')
                    usname = f.readline()
                    self.__usn.set(usname[:len(usname) - 1])
                    phash = f.readline()
                    self.__ph = (phash[:len(phash) - 1])
                    ipad = f.readline()
                    self.__ip.set(ipad[:len(ipad) - 1])
                    port = f.readline()
                    self.__port.set(port[:len(port) - 1])
                    http = f.readline()
                    http = int(http)
                    self.__https.set(http)
                    f.close()
                    self.cred = 1
                    logger.info('Successfully read credentials')
                except Exception as e:
                    logger.exception('Reading Creds error')
                    print('readIt error', e)
                    errMsg = Toplevel()
                    errMsg.title('Error')
                    Message(errMsg, text=e).pack()
                    Button(errMsg, text='OK', command=errMsg.destroy).pack()

            else:
                #   no creds so prompt server settings
                self.serverSettings()
        else:
            pass

    def sort_db(self, *args):
        #   not sure if worth, I'd assume it is for speed.
        self.sensors.sort_values(['Parent ID', 'Tags', 'Type',])

    def start_search(self, *args):
        #   probably not necessary.
        self.searching = True
        self.search_thread = threading.Thread(target=self.search_all)
        self.search_thread.start()

    def start_get(self, *args):
        self.running = True
        self.newthread = threading.Thread(target=self.getStates)
        self.newthread.start()

    def stop_thread(self, *args):
        try:
            logger.info("Stop Thread / Cancel")
            self.running = False
            self.cancel_req = 1
            #   self.sleep_time = 0.1
            #   self.get_button.config(state='active')
            self.processing.config(text='Cancelling... Don\'t close')
            remove_files(merge_list)
            logger.info("Removed old request/merge files")
            #   delete future merge files post cancelling
            #   self.sleep_event.set()
            try:
                #   in case queue window is closed.
                self.cancel_queue_but.config(text='Ok', command=self.queue_top.destroy)
            except Exception as e:
                logger.exception('Closed queue window before clean up is finished.')
            finally:
                self.check_gc()
                self.iter = 1
                self.cancel_req = 0
        except Exception as e:
            #   lazy fix
            self.iter = 1
            self.cancel_req = 0
            logger.exception('Stop Thread exception')
            self.get_button.config(state='active')

    def check_gc(self, *args):
        if self.__gc == 10:
            gc.enable()
            #   gc.collect()
            self.__gc = 1
        else:
            self.__gc += 1
            #   print(self.__gc)


if __name__ == '__main__':
    root = Tk()

    root.title('PRTG API')
    root.minsize(485, 590)  # for now.
    root.iconbitmap('imgs\prtg_active.ico')
    x = (root.winfo_screenwidth() / 2) - (430 / 2)
    y = (root.winfo_screenheight()/ 2) - (555 / 2)
    # root.geometry('%dx%d+%d+%d' % (450, 575, x, y))
    app = App(root, root.winfo_screenwidth(), root.winfo_screenheight())
    # app.killswitch()
    root.config(menu=app.menubar)
    mainloop()

'''
Remodel Nation:
    Framing:
        A) File options
            -   Type
            -   Filename
            -   Save to + Path
            -   Keep duplicates / Keep only merged / Merge 
        B) request options
            -   Type
            -   Preset
            -   GET preset
        C) request specific options
            -   ID + Entry 
            -   Search / Import CSV
                - Build and manage a Queue/
                - eta + # of files
                - undo
                - 
                
            -   Merge CSV / Only keep merged / Include Raw data
            -   Tags
            -   GET
        D) GET ? (pero que nunca se mueva)
    Independent Frames:
        A) Server settings.
        B) Errors
        C) Status
        D) Preset editing and creating.
        E) Schedule tasks
        F)

'''
