import os, sys, csv, json, sqlite3, webbrowser, threading, tkinter as tk
import math, time
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from urllib.parse import quote
from datetime import datetime
from base64 import urlsafe_b64decode
from email.utils import parseaddr
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / 'internship_applications.db'
CONFIG_PATH = APP_DIR / 'settings.json'
PUTRAJAYA_LINE = [
    'Metro Prima', 'Kepong Baru', 'Jinjang', 'Sri Delima', 'Kampung Batu',
    'Kentonmen', 'Jalan Ipoh', 'Sentul Barat', 'Titiwangsa',
    'Hospital Kuala Lumpur', 'Raja Uda', 'Ampang Park', 'Persiaran KLCC',
    'Conlay', 'Tun Razak Exchange', 'Chan Sow Lin', 'Kuchai', 'Taman Naga Emas',
    'Sungai Besi', 'Serdang Raya Utara', 'Serdang Raya Selatan', 'Seri Kembangan',
    'UPM', 'Taman Equine', 'Putra Permai', '16 Sierra', 'Cyberjaya Utara',
    'Cyberjaya City Centre', 'Putrajaya Sentral'
]
KAJANG_LINE = ['Kwasa Damansara','Kota Damansara','Surian','Mutiara Damansara','Bandar Utama','TTDI','Phileo Damansara','Pusat Bandar Damansara','Semantan','Muzium Negara','Pasar Seni','Merdeka','Bukit Bintang','Tun Razak Exchange','Cochrane','Maluri','Taman Pertama','Taman Midah','Taman Mutiara','Taman Connaught','Taman Suntex','Sri Raya','Bandar Tun Hussein Onn','Batu 11 Cheras','Bukit Dukung','Sungai Jernih','Stadium Kajang','Kajang']
KELANA_JAYA_LINE = ['Putra Heights','Subang Alam','Alam Megah','USJ 21','Wawasan','USJ 7','Taipan','SS 18','SS 15','Subang Jaya','Glenmarie','Ara Damansara','Lembah Subang','Kelana Jaya','Taman Bahagia','Taman Paramount','Asia Jaya','Taman Jaya','Universiti','Kerinchi','Abdullah Hukum','Bangsar','KL Sentral','Pasar Seni','Masjid Jamek','Dang Wangi','Kampung Baru','KLCC','Ampang Park']
AMPANG_LINE = ['Sentul Timur','Sentul','PWTC','Sultan Ismail','Bandaraya','Masjid Jamek','Plaza Rakyat','Hang Tuah','Pudu','Chan Sow Lin','Miharja','Pandanmaran','Cempaka','Pandan Indah','Cahaya','Ampang']
SRI_PETALING_LINE = ['Sentul Timur','Sentul','PWTC','Sultan Ismail','Bandaraya','Masjid Jamek','Plaza Rakyat','Hang Tuah','Pudu','Chan Sow Lin','Cheras','Salak Selatan','Bandar Tasik Selatan','Sungai Besi','Bukit Jalil','Sri Petaling','Awan Besar','Muhibbah','Alam Sutera','Kinrara BK5','IOI Puchong Jaya','Pusat Bandar Puchong','Taman Perindustrian Puchong','Bandar Puteri','Puchong Perdana','Puchong Prima','Putra Heights']
MONORAIL_LINE = ['KL Sentral','Tun Sambanthan','Maharajalela','Imbi','Bukit Bintang','Raja Chulan','Bukit Nanas','Medan Tuanku','Chow Kit','Titiwangsa']
TRANSIT_LINES = {'MRT Putrajaya Line': PUTRAJAYA_LINE, 'MRT Kajang Line': KAJANG_LINE, 'LRT Kelana Jaya Line': KELANA_JAYA_LINE, 'LRT Ampang Line': AMPANG_LINE, 'LRT Sri Petaling Line': SRI_PETALING_LINE, 'KL Monorail': MONORAIL_LINE}
LINE_STATIONS = sorted({station for stations in TRANSIT_LINES.values() for station in stations})
LINE_CHOICES = ['All MRT / LRT / Monorail'] + list(TRANSIT_LINES)
DEFAULTS = {
    'student_name': '', 'course': '', 'internship_period': '', 'phone': '',
    'sender_email': '', 'resume_path': '', 'credentials_path': '',
    'email_subject': 'Application for IT Internship – {company}', 'geoapify_api_key': ''
}


def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('''CREATE TABLE IF NOT EXISTS companies (
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, website TEXT, address TEXT,
        postcode TEXT, city TEXT, state TEXT, country TEXT, industry TEXT, faculty TEXT,
        international_intern TEXT, hr_email TEXT DEFAULT '', station TEXT DEFAULT '',
        walk_minutes INTEGER, route_verified INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Not applied', notes TEXT DEFAULT '', last_sent TEXT DEFAULT ''
    )''')
    # Kept as migrations so existing users' application database is preserved.
    columns = {row['name'] for row in con.execute('PRAGMA table_info(companies)')}
    for name, definition in {
        'email_source': "TEXT DEFAULT ''", 'email_verified': 'INTEGER DEFAULT 0',
        'email_verified_at': "TEXT DEFAULT ''", 'last_contact': "TEXT DEFAULT ''",
        'station_line': "TEXT DEFAULT ''", 'walk_distance_meters': 'INTEGER',
        'latitude': 'REAL', 'longitude': 'REAL'
    }.items():
        if name not in columns:
            con.execute(f'ALTER TABLE companies ADD COLUMN {name} {definition}')
    con.execute('''CREATE TABLE IF NOT EXISTS system_threads (
        company_id INTEGER PRIMARY KEY, gmail_thread_id TEXT UNIQUE NOT NULL,
        recipient TEXT DEFAULT '', initial_message_id TEXT DEFAULT '', last_synced_at TEXT DEFAULT ''
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS system_messages (
        gmail_message_id TEXT PRIMARY KEY, company_id INTEGER NOT NULL, gmail_thread_id TEXT NOT NULL,
        direction TEXT NOT NULL, sender TEXT DEFAULT '', recipient TEXT DEFAULT '', subject TEXT DEFAULT '',
        body TEXT DEFAULT '', sent_at TEXT DEFAULT '', internal_date INTEGER DEFAULT 0
    )''')
    con.execute('''CREATE TABLE IF NOT EXISTS station_locations (
        line TEXT NOT NULL, station TEXT NOT NULL, latitude REAL NOT NULL, longitude REAL NOT NULL,
        updated_at TEXT DEFAULT '', PRIMARY KEY(line, station)
    )''')
    con.commit()
    return con


def load_settings():
    data = DEFAULTS.copy()
    if CONFIG_PATH.exists():
        try: data.update(json.loads(CONFIG_PATH.read_text(encoding='utf-8')))
        except Exception: pass
    return data


def save_settings(data):
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def _clean_company_name(value):
    return ''.join(ch.lower() for ch in str(value or '') if ch.isalnum())


def _first_email(value):
    """Return an address present in an Excel cell; never invent an address."""
    import re
    found = re.search(r'[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}', str(value or ''), re.I)
    return found.group(0).lower() if found else ''


def _email_columns(headers):
    terms = ('email', 'e-mail', 'email address', 'contact email', 'hr email', 'recruitment email')
    return [i for i, header in enumerate(headers) if any(term in str(header).lower() for term in terms)]


def _company_column(headers):
    for i, header in enumerate(headers):
        text = str(header).strip().lower()
        if text in ('company', 'company name', 'employer', 'organization', 'organisation', 'name'):
            return i
    return 0


def _excel_email_lookup(wb):
    """Index company → email from every sheet that actually contains both fields."""
    lookup = {}
    for sheet in wb.worksheets:
        headers = [str(c.value or '').strip() for c in sheet[1]]
        company_col, email_cols = _company_column(headers), _email_columns(headers)
        if not email_cols:
            continue
        for row in sheet.iter_rows(min_row=2, values_only=True):
            key = _clean_company_name(row[company_col] if company_col < len(row) else '')
            if not key:
                continue
            email = next((_first_email(row[i]) for i in email_cols if i < len(row) and _first_email(row[i])), '')
            if email and key not in lookup:
                source = next((headers[i] for i in email_cols if i < len(row) and _first_email(row[i])), 'Email')
                lookup[key] = (email, f'Excel: {sheet.title} / {source}')
    return lookup


def import_excel(path):
    try:
        import openpyxl
    except ImportError:
        raise RuntimeError('Missing openpyxl. Please run install.bat first.')
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    ws = wb[wb.sheetnames[0]]
    headers = [str(c.value or '').strip() for c in ws[1]]
    required = ['Website', 'Address 1', 'City', 'Industry', 'Target Faculty']
    missing = [x for x in required if x not in headers]
    if missing: raise ValueError('Excel missing expected columns: ' + ', '.join(missing))
    idx = {h: headers.index(h) for h in headers if h}
    email_lookup = _excel_email_lookup(wb)
    def val(row, key):
        i = idx.get(key)
        return '' if i is None or i >= len(row) or row[i] is None else str(row[i]).strip()
    con = db(); added = 0; skipped = 0; email_candidates = 0
    for row in ws.iter_rows(min_row=2, values_only=True):
        name = str(row[0] or '').strip() if row else ''
        faculty = val(row, 'Target Faculty')
        # Match the actual FOCS token, not incidental text.
        tokens = faculty.strip().strip('[]').replace(' ', '').split(',') if faculty else []
        if not name or 'FOCS' not in tokens: continue
        address = ', '.join(x for x in [val(row, 'Address 1'), val(row, 'Address 2'), val(row, 'Address 3')] if x)
        values = (name, val(row,'Website'), address, val(row,'Postcode'), val(row,'City'),
                  val(row,'State'), val(row,'Country'), val(row,'Industry'), faculty,
                  val(row,'Accept International Students Interns?'))
        candidate_email, email_source = email_lookup.get(_clean_company_name(name), ('', ''))
        if candidate_email: email_candidates += 1
        exists = con.execute('SELECT id FROM companies WHERE name=? AND address=?', (name,address)).fetchone()
        if exists:
            con.execute('''UPDATE companies SET website=?, postcode=?, city=?, state=?, country=?, industry=?, faculty=?, international_intern=? WHERE id=?''',
                        (values[1],values[3],values[4],values[5],values[6],values[7],values[8],values[9],exists['id']))
            # A re-import must never replace an address the user already verified.
            if candidate_email:
                con.execute('''UPDATE companies SET hr_email=?, email_source=?, email_verified=0, email_verified_at=''
                               WHERE id=? AND (COALESCE(email_verified,0)=0 OR COALESCE(hr_email,'')='')''',
                            (candidate_email, email_source, exists['id']))
            skipped += 1
        else:
            con.execute('''INSERT INTO companies(name,website,address,postcode,city,state,country,industry,faculty,international_intern) VALUES(?,?,?,?,?,?,?,?,?,?)''', values)
            if candidate_email:
                con.execute('UPDATE companies SET hr_email=?,email_source=?,email_verified=0 WHERE name=? AND address=?',
                            (candidate_email, email_source, name, address))
            added += 1
    con.commit(); con.close(); wb.close()
    return added, skipped, email_candidates


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('IT Internship Auto Apply | Gmail')
        self.geometry('1400x820'); self.minsize(1100,650)
        self.settings = load_settings(); self.selected_id = None; self._conversation_syncing = False; self._bulk_calculating = False
        self._style(); self._build(); self.refresh()
        self.after(60000, self._auto_refresh_conversation)

    def _style(self):
        s=ttk.Style(self); s.theme_use('clam')
        s.configure('Treeview', rowheight=27, font=('Segoe UI',9))
        s.configure('Treeview.Heading', font=('Segoe UI',9,'bold'))
        s.configure('Title.TLabel', font=('Segoe UI',17,'bold'))
        s.configure('Hint.TLabel', foreground='#555')
        s.configure('Verified.TLabel', foreground='#167d36')
        s.configure('Warning.TLabel', foreground='#a35b00')

    def _build(self):
        top=ttk.Frame(self,padding=12); top.pack(fill='x')
        ttk.Label(top,text='IT Internship Auto Apply',style='Title.TLabel').pack(side='left')
        ttk.Label(top,text='Gmail • verified contacts • KL MRT/LRT/Monorail distance',style='Hint.TLabel').pack(side='left',padx=18)
        bar=ttk.Frame(self,padding=(12,0,12,8)); bar.pack(fill='x')
        ttk.Button(bar,text='Import Excel',command=self.import_file).pack(side='left',padx=3)
        ttk.Button(bar,text='Profile & Gmail Setup',command=self.profile_dialog).pack(side='left',padx=3)
        ttk.Button(bar,text='Select Resume PDF',command=self.choose_resume).pack(side='left',padx=3)
        ttk.Button(bar,text='Refresh list',command=self.refresh).pack(side='left',padx=3)
        self.bulk_station_button=ttk.Button(bar,text='Auto-calculate all nearest stations',command=self.calculate_all_nearest_stations)
        self.bulk_station_button.pack(side='left',padx=3)
        ttk.Label(bar,text='Search:').pack(side='left',padx=(20,4))
        self.search=tk.StringVar(); ent=ttk.Entry(bar,textvariable=self.search,width=30); ent.pack(side='left'); ent.bind('<KeyRelease>',lambda e:self.refresh())
        filters=ttk.Frame(self,padding=(12,0,12,8)); filters.pack(fill='x')
        self.industry_filter=tk.StringVar(value='All industries')
        self.region_filter=tk.StringVar(value='All regions')
        self.distance_filter=tk.StringVar(value='All distances')
        self.status_filter=tk.StringVar(value='All applications')
        self.industry_combo=self._filter(filters,'Industry',self.industry_filter,0,28)
        self.region_combo=self._filter(filters,'Region',self.region_filter,1,26)
        self.industry_combo.bind('<<ComboboxSelected>>',self._scope_changed)
        self.region_combo.bind('<<ComboboxSelected>>',self._scope_changed)
        self.distance_combo=self._filter(filters,'Distance',self.distance_filter,2,20,
                                         ['All distances','≤ 1 km straight-line','≤ 3 km straight-line','≤ 5 min walk','≤ 10 min walk','Route verified','Distance unknown'])
        self.status_combo=self._filter(filters,'Application',self.status_filter,3,20,
                                       ['All applications','Ready to apply','Not applied','Draft ready','Applied','Replied','Interview','Rejected','No response'])
        self.line_filter=tk.StringVar(value='All transit lines')
        ttk.Label(filters,text='Transit line:').grid(row=1,column=0,sticky='w',pady=(6,0))
        self.line_combo=ttk.Combobox(filters,textvariable=self.line_filter,state='readonly',width=28,values=['All transit lines']+list(TRANSIT_LINES))
        self.line_combo.grid(row=1,column=1,sticky='w',padx=(0,14),pady=(6,0)); self.line_combo.bind('<<ComboboxSelected>>',lambda e:self.refresh())

        stats=ttk.Frame(self,padding=(12,0,12,8)); stats.pack(fill='x')
        self.stats_label=ttk.Label(stats,text=''); self.stats_label.pack(anchor='w')
        main=ttk.Panedwindow(self,orient='horizontal'); main.pack(fill='both',expand=True,padx=12,pady=4)
        left=ttk.Frame(main); right=ttk.Frame(main,padding=10); main.add(left,weight=4); main.add(right,weight=3)
        cols=('name','industry','city','state','station','walk','contact','status')
        self.tree=ttk.Treeview(left,columns=cols,show='headings',selectmode='browse')
        widths={'name':230,'industry':145,'city':105,'state':120,'station':145,'walk':70,'contact':112,'status':100}
        heads={'name':'Company','industry':'Industry','city':'City','state':'State','station':'MRT Station','walk':'Walk','contact':'Contact email','status':'Application'}
        for c in cols: self.tree.heading(c,text=heads[c]); self.tree.column(c,width=widths[c],anchor='w')
        vs=ttk.Scrollbar(left,orient='vertical',command=self.tree.yview); hs=ttk.Scrollbar(left,orient='horizontal',command=self.tree.xview)
        self.tree.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
        self.tree.grid(row=0,column=0,sticky='nsew'); vs.grid(row=0,column=1,sticky='ns'); hs.grid(row=1,column=0,sticky='ew')
        left.rowconfigure(0,weight=1); left.columnconfigure(0,weight=1); self.tree.bind('<<TreeviewSelect>>',self.on_select)

        notebook=ttk.Notebook(right); notebook.pack(fill='both',expand=True)
        review=ttk.Frame(notebook,padding=10); conversation=ttk.Frame(notebook,padding=10)
        notebook.add(review,text='Company review & apply'); notebook.add(conversation,text='System email conversation')
        ttk.Label(review,text='Company & route review',font=('Segoe UI',12,'bold')).pack(anchor='w',pady=(0,8))
        self.detail=tk.Text(review,height=7,wrap='word',font=('Segoe UI',9)); self.detail.pack(fill='x')
        form=ttk.Frame(review); form.pack(fill='x',pady=8)
        self.hr_var=tk.StringVar(); self.station_line_var=tk.StringVar(value='MRT Putrajaya Line'); self.station_var=tk.StringVar(value='Metro Prima'); self.walk_var=tk.StringVar(); self.walk_distance_var=tk.StringVar(); self.status_var=tk.StringVar(value='Not applied'); self.email_verified_var=tk.BooleanVar(value=False)
        self._field(form,'Contact email (candidate)',self.hr_var,0)
        self.email_source_label=ttk.Label(form,text='Source: —',style='Hint.TLabel',wraplength=350)
        self.email_source_label.grid(row=1,column=1,sticky='w',pady=(0,3))
        ttk.Checkbutton(form,text='I personally verified this email is the correct recruitment contact',variable=self.email_verified_var).grid(row=2,column=1,sticky='w',pady=(1,5))
        ttk.Label(form,text='Transit line').grid(row=3,column=0,sticky='w',pady=3)
        ttk.Combobox(form,textvariable=self.station_line_var,state='readonly',values=LINE_CHOICES,width=35).grid(row=3,column=1,sticky='ew',pady=3)
        ttk.Label(form,text='Nearest MRT / LRT station').grid(row=4,column=0,sticky='w',pady=3)
        ttk.Combobox(form,textvariable=self.station_var,state='readonly',values=LINE_STATIONS,width=35).grid(row=4,column=1,sticky='ew',pady=3)
        ttk.Label(form,text='Nearest-station distance').grid(row=5,column=0,sticky='w',pady=3)
        ttk.Label(form,textvariable=self.walk_distance_var,style='Hint.TLabel').grid(row=5,column=1,sticky='w',pady=3)
        ttk.Label(form,text='Final walk minutes').grid(row=6,column=0,sticky='w',pady=3)
        ttk.Entry(form,textvariable=self.walk_var,width=38).grid(row=6,column=1,sticky='ew',pady=3)
        ttk.Label(form,text='Application status').grid(row=7,column=0,sticky='w',pady=3)
        ttk.Combobox(form,textvariable=self.status_var,state='readonly',values=['Not applied','Draft ready','Applied','Replied','Interview','Rejected','No response'],width=35).grid(row=7,column=1,sticky='ew',pady=3)
        form.columnconfigure(1,weight=1)
        ttk.Button(review,text='Save company / route details',command=self.save_company).pack(fill='x',pady=3)
        ttk.Button(review,text='Calculate selected company station',command=self.calculate_nearest_station).pack(fill='x',pady=3)
        ttk.Label(review,text='Free geocoding by Geoapify / OpenStreetMap data',style='Hint.TLabel').pack(anchor='w',pady=(0,3))
        ttk.Button(review,text='Open Google Maps route',command=self.open_map).pack(fill='x',pady=3)
        ttk.Separator(review).pack(fill='x',pady=9)
        ttk.Label(review,text='Email preview',font=('Segoe UI',12,'bold')).pack(anchor='w')
        self.preview=tk.Text(review,height=10,wrap='word',font=('Segoe UI',9)); self.preview.pack(fill='both',expand=True,pady=5)
        actions=ttk.Frame(review); actions.pack(fill='x')
        ttk.Button(actions,text='Generate preview',command=self.generate_preview).pack(side='left',expand=True,fill='x',padx=2)
        ttk.Button(actions,text='Create Gmail Draft',command=lambda:self.gmail_action(send=False)).pack(side='left',expand=True,fill='x',padx=2)
        ttk.Button(actions,text='Review & Send',command=lambda:self.gmail_action(send=True)).pack(side='left',expand=True,fill='x',padx=2)
        ttk.Label(review,text='Safety: no email is sent until you review the recipient, message and attachment, then confirm.',style='Hint.TLabel',wraplength=420).pack(anchor='w',pady=(7,0))

        ttk.Label(conversation,text='Emails sent from this app only',font=('Segoe UI',12,'bold')).pack(anchor='w')
        ttk.Label(conversation,text='The selected system thread checks for new replies every minute; Refresh updates it now. Other inbox email is never shown here.',style='Hint.TLabel',wraplength=420).pack(anchor='w',pady=(2,8))
        self.conversation_status=ttk.Label(conversation,text='Select a company that was emailed through this app.',style='Hint.TLabel')
        self.conversation_status.pack(anchor='w',pady=(0,6))
        self.conversation_text=tk.Text(conversation,height=17,wrap='word',font=('Segoe UI',9),state='disabled')
        self.conversation_text.pack(fill='both',expand=True)
        conv_actions=ttk.Frame(conversation); conv_actions.pack(fill='x',pady=(8,3))
        ttk.Button(conv_actions,text='Refresh conversation',command=self.refresh_conversation).pack(side='left')
        ttk.Button(conv_actions,text='Send reply below',command=self.send_reply).pack(side='right')
        ttk.Label(conversation,text='Reply message',font=('Segoe UI',10,'bold')).pack(anchor='w',pady=(6,2))
        self.reply_text=tk.Text(conversation,height=5,wrap='word',font=('Segoe UI',9))
        self.reply_text.pack(fill='x')

    def _filter(self,parent,label,var,column,width,values=None):
        ttk.Label(parent,text=label+':').grid(row=0,column=column*2,sticky='w',padx=(0,4))
        combo=ttk.Combobox(parent,textvariable=var,state='readonly',width=width,values=values or [var.get()])
        combo.grid(row=0,column=column*2+1,sticky='w',padx=(0,14))
        combo.bind('<<ComboboxSelected>>',lambda e:self.refresh())
        return combo

    def _scope_changed(self,event=None):
        self.refresh(); self._update_bulk_station_button()

    def _update_bulk_station_button(self):
        industry=self.industry_filter.get()
        if industry == 'All industries':
            label='Auto-calculate all nearest stations'
        else:
            label='Auto-calculate selected industry stations'
        self.bulk_station_button.config(text=label)

    def _field(self,parent,label,var,row):
        ttk.Label(parent,text=label).grid(row=row,column=0,sticky='w',pady=3)
        ttk.Entry(parent,textvariable=var,width=38).grid(row=row,column=1,sticky='ew',pady=3)

    def import_file(self):
        p=filedialog.askopenfilename(title='Select CareeReX Excel',filetypes=[('Excel files','*.xlsx *.xlsm')])
        if not p:return
        try:
            a,b,c=import_excel(p); self.refresh(); messagebox.showinfo('Import complete',f'FOCS companies added: {a}\nExisting records updated: {b}\nEmail candidates matched by company: {c}\n\nAny Excel email was imported as an unverified candidate. Check the company and tick the verification box before sending.')
        except Exception as e: messagebox.showerror('Import failed',str(e))

    def refresh(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        con=db(); rows=con.execute('SELECT * FROM companies ORDER BY name').fetchall(); con.close()
        industries=sorted({str(r['industry']).strip() for r in rows if str(r['industry']).strip()})
        regions=sorted({self._region_label(r) for r in rows if self._region_label(r)})
        self.industry_combo['values']=['All industries']+industries
        self.region_combo['values']=['All regions','Kuala Lumpur / Selangor']+regions
        q=self.search.get().strip().lower()
        shown=[]
        for r in rows:
            hay=' '.join(str(r[k] or '') for k in ['name','industry','address','city','state']).lower()
            if q and q not in hay: continue
            local=(str(r['state']).lower() in ['selangor','wilayah persekutuan kuala lumpur'] or str(r['city']).lower() in ['kuala lumpur','petaling jaya'])
            route_checked=bool(r['route_verified']) and r['station'] in LINE_STATIONS and r['walk_minutes'] is not None
            verified=route_checked and int(r['walk_minutes'])<=10
            ready=verified and bool(r['hr_email']) and '@' in r['hr_email'] and bool(r['email_verified']) and r['status']!='Applied'
            distance=self.distance_filter.get(); status=self.status_filter.get(); region=self.region_filter.get()
            if self.industry_filter.get() != 'All industries' and r['industry'] != self.industry_filter.get(): continue
            # A company without a saved nearest-station result must remain visible.
            # Otherwise selecting a line hides every new import and prevents the
            # user from selecting a company to calculate in the first place.
            if self.line_filter.get() != 'All transit lines' and r['station_line'] and r['station_line'] != self.line_filter.get(): continue
            if region == 'Kuala Lumpur / Selangor' and not local: continue
            if region not in ('All regions','Kuala Lumpur / Selangor') and self._region_label(r) != region: continue
            if distance == '≤ 1 km straight-line' and not (r['walk_distance_meters'] is not None and int(r['walk_distance_meters']) <= 1000): continue
            if distance == '≤ 3 km straight-line' and not (r['walk_distance_meters'] is not None and int(r['walk_distance_meters']) <= 3000): continue
            if distance == '≤ 5 min walk' and not (verified and int(r['walk_minutes']) <= 5): continue
            if distance == '≤ 10 min walk' and not verified: continue
            if distance == 'Route verified' and not route_checked: continue
            if distance == 'Distance unknown' and (r['walk_distance_meters'] is not None or r['walk_minutes'] is not None): continue
            if status == 'Ready to apply' and not ready: continue
            if status not in ('All applications','Ready to apply') and r['status'] != status: continue
            shown.append(r)
        selected_line=self.line_filter.get()
        if selected_line != 'All transit lines':
            # Put known matches first; uncalculated companies stay accessible below.
            shown.sort(key=lambda r: (0 if r['station_line'] == selected_line else 1, str(r['name'] or '').lower()))
        for r in shown:
            ok=bool(r['route_verified']) and r['station'] in LINE_STATIONS and r['walk_minutes'] is not None and int(r['walk_minutes'])<=10
            walk=f"{r['walk_minutes']} min" if r['walk_minutes'] is not None else '—'
            contact='Verified' if r['email_verified'] else ('Check needed' if r['hr_email'] else 'Missing')
            station=r['station'] or ('Needs calculation' if selected_line != 'All transit lines' else '—')
            self.tree.insert('', 'end', iid=str(r['id']), values=(r['name'],r['industry'],r['city'],r['state'],station,walk,contact,r['status']))
        base=f'Total FOCS companies: {len(rows):,}   |   Showing: {len(shown):,}   |   Route verified ≤10 min: {sum(1 for r in rows if r["route_verified"] and r["walk_minutes"] is not None and int(r["walk_minutes"])<=10):,}'
        if selected_line != 'All transit lines':
            matched=sum(1 for r in shown if r['station_line'] == selected_line)
            waiting=sum(1 for r in shown if not r['station_line'])
            base += f'   |   {selected_line}: {matched:,} calculated match(es), {waiting:,} waiting to calculate'
        self.stats_label.config(text=base)

    @staticmethod
    def _region_label(r):
        return ' — '.join(x for x in [str(r['city'] or '').strip(), str(r['state'] or '').strip()] if x)

    def on_select(self,event=None):
        sel=self.tree.selection()
        if not sel:return
        self.selected_id=int(sel[0]); con=db(); r=con.execute('SELECT * FROM companies WHERE id=?',(self.selected_id,)).fetchone(); con.close()
        self.hr_var.set(r['hr_email'] or ''); self.email_verified_var.set(bool(r['email_verified'])); self.station_line_var.set(r['station_line'] or self._station_line_for(r['station']) or 'MRT Putrajaya Line'); self.station_var.set(r['station'] or 'Metro Prima'); self.walk_var.set('' if r['walk_minutes'] is None else str(r['walk_minutes'])); self.walk_distance_var.set((f"{r['walk_distance_meters']:,} m • " if r['walk_distance_meters'] is not None else '') + (f"{r['walk_minutes']} min walk" if r['walk_minutes'] is not None else 'Not calculated')); self.status_var.set(r['status'] or 'Not applied')
        source=r['email_source'] or ('Verified manually' if r['email_verified'] else 'No imported source')
        self.email_source_label.config(text='Source: '+source,style='Verified.TLabel' if r['email_verified'] else 'Warning.TLabel')
        self.detail.delete('1.0','end')
        self.detail.insert('1.0',f"{r['name']}\nIndustry: {r['industry']}\nAddress: {r['address']}, {r['postcode']} {r['city']}, {r['state']}, {r['country']}\nWebsite: {r['website']}\nTarget Faculty: {r['faculty']}\nInternational interns: {r['international_intern']}\n\nThe email is not usable until you personally verify it. Calculate nearest station is a free straight-line estimate. Check the final walking route in Maps before entering walk minutes and saving.")
        self.preview.delete('1.0','end')
        self.reply_text.delete('1.0','end'); self.load_conversation()

    def save_company(self):
        if not self.selected_id: messagebox.showwarning('Select company','Please select a company first.'); return
        current=self.current_company()
        email=self.hr_var.get().strip(); station=self.station_var.get().strip(); station_line=self.station_line_var.get().strip(); raw=self.walk_var.get().strip(); email_verified=bool(self.email_verified_var.get())
        if email and ('@' not in email or '.' not in email.split('@')[-1]): messagebox.showerror('Invalid email','Enter a verified HR email address.'); return
        if email_verified and not email: messagebox.showerror('Email missing','Add a contact email before marking it verified.'); return
        if station_line == 'All MRT / LRT / Monorail': messagebox.showerror('Choose a station line','Calculate a station first or select its actual line before saving.'); return
        mins=None
        if raw:
            try: mins=int(raw)
            except ValueError: messagebox.showerror('Invalid walk time','Enter a whole number from 0 to 240 minutes.'); return
            if not 0<=mins<=240: messagebox.showerror('Invalid walk time','Enter a whole number from 0 to 240 minutes.'); return
        # Explicit checkbox-like confirmation via dialog before route_verified=1.
        verified=False
        if mins is not None:
            verified=messagebox.askyesno('Confirm route check',f'Have you personally verified the final walking route from {station} ({station_line}) to the actual office entrance is {mins} minutes or less?\n\nOnly click Yes if the Google Maps result and office entrance are correct.')
        source=current['email_source'] if current and email == (current['hr_email'] or '') and current['email_source'] else ('Manually entered' if email else '')
        con=db(); con.execute('UPDATE companies SET hr_email=?,email_source=?,email_verified=?,email_verified_at=?,station=?,station_line=?,walk_minutes=?,route_verified=?,status=? WHERE id=?',
                              (email, source, 1 if email_verified else 0, datetime.now().isoformat(timespec='minutes') if email_verified else '', station,station_line,mins,1 if verified else 0,self.status_var.get(),self.selected_id)); con.commit(); con.close(); self.refresh()
        messagebox.showinfo('Saved','Company details saved. Contact email: '+('Verified' if email_verified else 'Needs verification')+'\nRoute eligibility: '+('Verified' if verified else 'Not verified'))

    def current_company(self):
        if not self.selected_id: return None
        con=db(); r=con.execute('SELECT * FROM companies WHERE id=?',(self.selected_id,)).fetchone(); con.close(); return r

    @staticmethod
    def _station_line_for(station):
        return next((line for line, stations in TRANSIT_LINES.items() if station in stations), '')

    def calculate_nearest_station(self):
        company=self.current_company()
        if not company: messagebox.showwarning('Select company','Select a company first.'); return
        selected_line=self.station_line_var.get()
        lines=TRANSIT_LINES if selected_line == 'All MRT / LRT / Monorail' else {selected_line: TRANSIT_LINES.get(selected_line, [])}
        candidates=[(line,station) for line, stations in lines.items() for station in stations]
        if not candidates: messagebox.showerror('No stations','Choose a valid MRT/LRT line first.'); return
        address=', '.join(x for x in [company['name'],company['address'],company['postcode'],company['city'],company['state'],'Malaysia'] if x)
        self.walk_distance_var.set('Looking up free map coordinates…')
        threading.Thread(target=self._nearest_station_worker,args=(company['id'],address,candidates),daemon=True).start()

    @staticmethod
    def _straight_distance_meters(a_lat,a_lon,b_lat,b_lon):
        radius=6371000
        p1,p2=math.radians(a_lat),math.radians(b_lat)
        dp,dl=math.radians(b_lat-a_lat),math.radians(b_lon-a_lon)
        h=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
        return int(2*radius*math.asin(math.sqrt(h)))

    @staticmethod
    def _geoapify_location(query, api_key):
        """One free-plan geocoding request. Results are cached in SQLite by caller."""
        url='https://api.geoapify.com/v1/geocode/search?text='+quote(query)+'&filter=countrycode:my&limit=1&apiKey='+quote(api_key)
        request=Request(url,headers={'User-Agent':'ITInternshipAutoApply/1.0'})
        with urlopen(request,timeout=30) as response:
            features=json.loads(response.read().decode('utf-8')).get('features',[])
        if not features: return None
        lon,lat=features[0]['geometry']['coordinates'][:2]
        return float(lat),float(lon)

    def _station_points(self,con,api_key,progress=None):
        points=[]; all_stations=[(line,station) for line,stations in TRANSIT_LINES.items() for station in stations]
        for index,(line,station) in enumerate(all_stations,1):
            cached=con.execute('SELECT latitude,longitude FROM station_locations WHERE line=? AND station=?',(line,station)).fetchone()
            if cached:
                points.append((line,station,cached['latitude'],cached['longitude'])); continue
            if progress: progress(f'Loading station {index}/{len(all_stations)}…')
            mode='MRT' if line.startswith('MRT') else ('LRT' if line.startswith('LRT') else 'Monorail')
            location=self._geoapify_location(f'{station} {mode} station, Malaysia',api_key)
            time.sleep(.22)  # Geoapify Free permits up to 5 requests/second.
            if not location: continue
            con.execute('INSERT OR REPLACE INTO station_locations(line,station,latitude,longitude,updated_at) VALUES(?,?,?,?,?)',(line,station,location[0],location[1],datetime.now().isoformat(timespec='minutes')))
            points.append((line,station,*location))
        con.commit()
        return points

    def _save_nearest_station(self,con,company,points):
        if company['latitude'] is None or company['longitude'] is None or not points: return False
        distance,line,station=min(((self._straight_distance_meters(company['latitude'],company['longitude'],lat,lon),line,station) for line,station,lat,lon in points),key=lambda row:row[0])
        con.execute('''UPDATE companies SET station=?,station_line=?,walk_distance_meters=?,walk_minutes=NULL,route_verified=0 WHERE id=?''',(station,line,distance,company['id']))
        return True

    def calculate_all_nearest_stations(self):
        if self._bulk_calculating: return
        api_key=self.settings.get('geoapify_api_key','').strip()
        if not api_key:
            messagebox.showerror('Free Geoapify key required','Create a free key at https://myprojects.geoapify.com, paste it in Profile & Gmail Setup, save, then run automatic calculation.')
            return
        industry=self.industry_filter.get(); region=self.region_filter.get()
        scope_parts=[]
        if industry != 'All industries': scope_parts.append(f'Industry: {industry}')
        if region != 'All regions': scope_parts.append(f'Region: {region}')
        scope=' • '.join(scope_parts) if scope_parts else 'All companies'
        if not messagebox.askyesno('Calculate nearest stations',f'This will automatically geocode companies in this scope:\n{scope}\n\nIt only calculates companies that do not yet have a nearest station. It uses Geoapify’s free daily quota, caches every result locally, and may take several minutes the first time. Continue?'): return
        self._bulk_calculating=True; self.bulk_station_button.state(['disabled']); self.stats_label.config(text='Preparing automatic nearest-station calculation…')
        threading.Thread(target=self._bulk_station_worker,args=(api_key,industry,region,scope),daemon=True).start()

    def _bulk_station_worker(self,api_key,industry,region,scope):
        try:
            con=db()
            def progress(text): self.after(0,lambda value=text:self.stats_label.config(text=value))
            points=self._station_points(con,api_key,progress)
            if not points: raise RuntimeError('No KL station coordinates were found. Check the API key and internet connection.')
            clauses=["COALESCE(route_verified,0)=0","(latitude IS NULL OR longitude IS NULL OR COALESCE(station_line,'')='')"]
            params=[]
            if industry != 'All industries':
                clauses.append("COALESCE(industry,'')=?"); params.append(industry)
            if region == 'Kuala Lumpur / Selangor':
                clauses.append("(LOWER(COALESCE(state,'')) IN (?,?) OR LOWER(COALESCE(city,'')) IN (?,?))")
                params += ['selangor','wilayah persekutuan kuala lumpur','kuala lumpur','petaling jaya']
            elif region != 'All regions':
                city,state=(region.split(' — ',1)+[''])[:2] if ' — ' in region else ('',region)
                if city: clauses.append("COALESCE(city,'')=?"); params.append(city)
                if state: clauses.append("COALESCE(state,'')=?"); params.append(state)
            companies=con.execute('SELECT * FROM companies WHERE '+' AND '.join(clauses)+' ORDER BY id',params).fetchall()
            total=len(companies); completed=located=failed=0
            for company in companies:
                point=(company['latitude'],company['longitude']) if company['latitude'] is not None and company['longitude'] is not None else None
                if not point:
                    address=', '.join(x for x in [company['address'],company['postcode'],company['city'],company['state'],'Malaysia'] if x)
                    point=self._geoapify_location(address,api_key); time.sleep(.22)
                    if point:
                        con.execute('UPDATE companies SET latitude=?,longitude=? WHERE id=?',(point[0],point[1],company['id']))
                        company=con.execute('SELECT * FROM companies WHERE id=?',(company['id'],)).fetchone()
                    else: failed+=1; completed+=1; continue
                if self._save_nearest_station(con,company,points): located+=1
                completed+=1
                if completed % 5 == 0 or completed == total:
                    con.commit(); progress(f'Auto-calculating {scope}: {completed:,}/{total:,} companies • {located:,} completed • {failed:,} address not found')
            con.commit(); con.close()
            self.after(0,lambda:self._bulk_station_done(located,failed,None,scope))
        except HTTPError as e:
            detail=e.read().decode('utf-8','replace')
            self.after(0,lambda err=f'Geoapify error {e.code}: {detail}':self._bulk_station_done(0,0,err,scope))
        except Exception as e:
            self.after(0,lambda err=str(e):self._bulk_station_done(0,0,err,scope))

    def _bulk_station_done(self,located,failed,error,scope):
        self._bulk_calculating=False; self.bulk_station_button.state(['!disabled'])
        if error: messagebox.showerror('Automatic calculation stopped',error)
        else:
            self.refresh(); self._update_bulk_station_button(); messagebox.showinfo('Automatic calculation complete',f'Scope: {scope}\nNearest MRT/LRT/Monorail station calculated: {located:,}\nAddress not located: {failed:,}\n\nUse Transit line plus distance filters to view nearby companies. Distance is straight-line; confirm final walking time in Google Maps before applying.')

    def calculate_nearest_station(self):
        company=self.current_company()
        if not company: messagebox.showwarning('Select company','Select a company first.'); return
        api_key=self.settings.get('geoapify_api_key','').strip()
        if not api_key: messagebox.showerror('Free Geoapify key required','Add the free Geoapify key in Profile & Gmail Setup first.'); return
        self.walk_distance_var.set('Calculating nearest station…')
        threading.Thread(target=self._single_station_worker,args=(company['id'],api_key),daemon=True).start()

    def _single_station_worker(self,company_id,api_key):
        try:
            con=db(); company=con.execute('SELECT * FROM companies WHERE id=?',(company_id,)).fetchone(); points=self._station_points(con,api_key)
            if company['latitude'] is None or company['longitude'] is None:
                address=', '.join(x for x in [company['address'],company['postcode'],company['city'],company['state'],'Malaysia'] if x)
                point=self._geoapify_location(address,api_key)
                if not point: raise RuntimeError('Company address could not be located. Edit the company address and try again.')
                con.execute('UPDATE companies SET latitude=?,longitude=? WHERE id=?',(point[0],point[1],company_id)); con.commit(); company=con.execute('SELECT * FROM companies WHERE id=?',(company_id,)).fetchone()
            if not self._save_nearest_station(con,company,points): raise RuntimeError('No KL station could be located.')
            con.commit(); result=con.execute('SELECT * FROM companies WHERE id=?',(company_id,)).fetchone(); con.close()
            self.after(0,lambda:self._nearest_station_done(result,None))
        except Exception as e: self.after(0,lambda err=str(e):self._nearest_station_done(None,err))

    def _nearest_station_done(self,result,error):
        if error: self.walk_distance_var.set('Not calculated'); messagebox.showerror('Station calculation failed',error); return
        if result['id'] != self.selected_id: return
        self.station_line_var.set(result['station_line']); self.station_var.set(result['station']); self.walk_var.set(''); self.walk_distance_var.set(f"{result['walk_distance_meters']:,} m straight-line")
        self.refresh(); messagebox.showinfo('Nearest station calculated',f"Nearest station: {result['station']}\nLine: {result['station_line']}\nStraight-line distance: {result['walk_distance_meters']:,} m\n\nConfirm actual walking time in Google Maps before applying.")

    def open_map(self):
        r=self.current_company()
        if not r: messagebox.showwarning('Select company','Select a company first.'); return
        dest=', '.join(x for x in [r['name'],r['address'],r['city'],r['state'],r['country']] if x)
        origin=', '.join(x for x in [r['station'],r['station_line'],'Malaysia'] if x) or 'Kuala Lumpur, Malaysia'
        url='https://www.google.com/maps/dir/?api=1&origin='+quote(origin)+'&destination='+quote(dest)+'&travelmode=walking'
        webbrowser.open(url)

    def make_email(self,r):
        s=self.settings
        subject=s.get('email_subject','Application for IT Internship – {company}').format(company=r['name'])
        name=s.get('student_name') or '[Your Name]'; course=s.get('course') or '[Your Course]'; period=s.get('internship_period') or '[Internship Period]'; phone=s.get('phone') or '[Phone Number]'
        body=(f'Dear Hiring Manager,\n\nI hope you are doing well. My name is {name}, and I am currently studying {course}. '
              f'I am writing to express my interest in an IT internship opportunity at {r["name"]}. '
              f'I would appreciate the opportunity to apply my knowledge, learn from your team, and gain practical industry experience.\n\n'
              f'My available internship period is {period}. I have attached my resume for your consideration. '
              f'Please let me know if there are any suitable internship opportunities or further documents required.\n\n'
              f'Thank you for your time and consideration. I look forward to hearing from you.\n\n'
              f'Best regards,\n{name}\n{course}\n{phone}\n{s.get("sender_email","")}')
        return subject,body

    def generate_preview(self):
        r=self.current_company()
        if not r: messagebox.showwarning('Select company','Select a company first.'); return
        subject,body=self.make_email(r)
        self.preview.delete('1.0','end'); self.preview.insert('1.0',f'To: {r["hr_email"] or "[Add verified HR email]"}\nSubject: {subject}\n\n{body}')

    def profile_dialog(self):
        win=tk.Toplevel(self); win.title('Profile & Gmail Setup'); win.geometry('680x630'); win.transient(self); win.grab_set()
        vars={k:tk.StringVar(value=str(self.settings.get(k,''))) for k in ['student_name','course','internship_period','phone','sender_email','resume_path','credentials_path','geoapify_api_key']}
        frm=ttk.Frame(win,padding=14); frm.pack(fill='both',expand=True)
        labels={'student_name':'Your full name','course':'Course / programme','internship_period':'Internship period (e.g. Jan–Apr 2027)','phone':'Phone number','sender_email':'Your Gmail address','resume_path':'Resume PDF path','credentials_path':'Google OAuth credentials.json path','geoapify_api_key':'Geoapify free geocoding API key'}
        for i,(k,label) in enumerate(labels.items()):
            ttk.Label(frm,text=label).grid(row=i,column=0,sticky='w',pady=6)
            ttk.Entry(frm,textvariable=vars[k],width=58,show='•' if k=='geoapify_api_key' else '').grid(row=i,column=1,sticky='ew',pady=6)
            if k in ['resume_path','credentials_path']:
                cmd=lambda key=k: self._browse_into(vars[key], 'PDF files' if key=='resume_path' else 'JSON files', '*.pdf' if key=='resume_path' else '*.json')
                ttk.Button(frm,text='Browse',command=cmd).grid(row=i,column=2,padx=4)
        ttk.Label(frm,text='Automatic nearest-station calculation uses Geoapify’s free plan (3,000 requests/day, no credit card) and caches coordinates locally. Create a free key at myprojects.geoapify.com, then paste it above. No Google Maps key is required.',wraplength=620,style='Hint.TLabel').grid(row=len(labels),column=0,columnspan=3,sticky='w',pady=10)
        def save():
            for k,v in vars.items(): self.settings[k]=v.get().strip()
            save_settings(self.settings); win.destroy(); messagebox.showinfo('Saved','Profile settings saved on this computer.')
        ttk.Button(frm,text='Save settings',command=save).grid(row=len(labels)+1,column=1,sticky='e',pady=12)
        frm.columnconfigure(1,weight=1)

    def _browse_into(self,var,label,pattern):
        p=filedialog.askopenfilename(filetypes=[(label,pattern)])
        if p: var.set(p)

    def choose_resume(self):
        p=filedialog.askopenfilename(title='Choose resume PDF',filetypes=[('PDF files','*.pdf')])
        if p: self.settings['resume_path']=p; save_settings(self.settings); messagebox.showinfo('Resume selected',p)

    def gmail_action(self,send=False):
        r=self.current_company()
        if not r: messagebox.showwarning('Select company','Select a company first.'); return
        if not r['hr_email'] or '@' not in r['hr_email'] or not r['email_verified']:
            messagebox.showerror('Verified contact required','Check the candidate email and tick the verification box before sending. The app never guesses an address.'); return
        if not r['route_verified'] or r['station'] not in LINE_STATIONS or r['walk_minutes'] is None or int(r['walk_minutes'])>10:
            messagebox.showerror('Route not verified','Verify the Putrajaya Line-only journey from Metro Prima and final walk (≤10 min) before applying.'); return
        resume=self.settings.get('resume_path','')
        if not resume or not Path(resume).is_file() or not resume.lower().endswith('.pdf'):
            messagebox.showerror('Resume missing','Select an existing Resume PDF first.'); return
        subject,body=self.make_email(r)
        confirm_text=f'To: {r["hr_email"]}\nCompany: {r["name"]}\nSubject: {subject}\nAttachment: {resume}\n\n{body}\n\n'
        if not messagebox.askyesno('Review before Gmail action',confirm_text+'\nProceed to '+('SEND this email' if send else 'create a Gmail Draft')+'?'):
            return
        if not self.settings.get('credentials_path') or not Path(self.settings['credentials_path']).is_file():
            messagebox.showerror('Gmail not configured','Select your Google OAuth credentials.json in Profile & Gmail Setup.'); return
        threading.Thread(target=self._gmail_worker,args=(r['id'],r['hr_email'],subject,body,resume,send),daemon=True).start()

    def _gmail_worker(self,cid,to,subject,body,resume,send):
        try:
            from email.message import EmailMessage
            import base64
            service=self._gmail_service()
            msg=EmailMessage(); msg['To']=to; msg['Subject']=subject
            msg.set_content(body)
            with open(resume,'rb') as f: data=f.read()
            msg.add_attachment(data,maintype='application',subtype='pdf',filename=Path(resume).name)
            raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
            if send:
                result=service.users().messages().send(userId='me',body={'raw':raw}).execute()
                status='Applied'; sent=datetime.now().isoformat(timespec='minutes')
                self._sync_gmail_thread(service,cid,result['threadId'])
            else:
                service.users().drafts().create(userId='me',body={'message':{'raw':raw}}).execute()
                status='Draft ready'; sent=''
            con=db(); con.execute('UPDATE companies SET status=?,last_sent=? WHERE id=?',(status,sent,cid)); con.commit(); con.close()
            self.after(0,lambda:self._gmail_done(send,None))
        except Exception as e:
            self.after(0,lambda err=str(e):self._gmail_done(send,err))

    def _gmail_done(self,send,error):
        if error: messagebox.showerror('Gmail error',error)
        else:
            self.refresh(); self.load_conversation(); messagebox.showinfo('Gmail complete','Email sent successfully. The new conversation is now tracked here.' if send else 'Gmail Draft created successfully.')

    def _gmail_service(self):
        """Authenticate with read/write access needed for app-originated conversation threads."""
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
        # A separate token forces one clear re-consent when upgrading from the
        # earlier compose-only version of the application.
        token_path=APP_DIR/'token_messages.json'; scopes=['https://www.googleapis.com/auth/gmail.modify']
        creds=None
        if token_path.exists():
            creds=Credentials.from_authorized_user_file(str(token_path),scopes)
        # An older compose-only token cannot read a conversation; request the
        # expanded scope again instead of silently failing on refresh.
        granted=set(getattr(creds,'granted_scopes',None) or []) if creds else set()
        if not creds or not creds.valid or (granted and not set(scopes).issubset(granted)):
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow=InstalledAppFlow.from_client_secrets_file(self.settings['credentials_path'],scopes)
                creds=flow.run_local_server(port=0)
            token_path.write_text(creds.to_json(),encoding='utf-8')
        return build('gmail','v1',credentials=creds)

    @staticmethod
    def _message_headers(message):
        return {h['name'].lower(): h.get('value','') for h in message.get('payload',{}).get('headers',[])}

    @staticmethod
    def _message_body(payload):
        if payload.get('body',{}).get('data') and payload.get('mimeType','').startswith('text/plain'):
            return urlsafe_b64decode(payload['body']['data']+'===').decode('utf-8','replace')
        for part in payload.get('parts',[]) or []:
            text=App._message_body(part)
            if text:
                return text
        return ''

    def _sync_gmail_thread(self,service,company_id,thread_id):
        """Persist one app-created Gmail thread; no inbox-wide query is ever performed."""
        thread=service.users().threads().get(userId='me',id=thread_id,format='full').execute()
        con=db()
        for msg in thread.get('messages',[]):
            headers=self._message_headers(msg); sender=headers.get('from',''); recipient=headers.get('to','')
            # Inbox replies are recognized only inside this thread, which originated from the app.
            direction='outbound' if 'SENT' in msg.get('labelIds',[]) else 'inbound'
            con.execute('''INSERT OR REPLACE INTO system_messages(gmail_message_id,company_id,gmail_thread_id,direction,sender,recipient,subject,body,sent_at,internal_date)
                           VALUES(?,?,?,?,?,?,?,?,?,?)''',
                        (msg['id'],company_id,thread_id,direction,sender,recipient,headers.get('subject',''),self._message_body(msg.get('payload',{})),headers.get('date',''),int(msg.get('internalDate','0') or 0)))
        first=(thread.get('messages') or [{}])[0].get('id','')
        con.execute('''INSERT INTO system_threads(company_id,gmail_thread_id,recipient,initial_message_id,last_synced_at)
                       VALUES(?,?,?,?,?) ON CONFLICT(company_id) DO UPDATE SET gmail_thread_id=excluded.gmail_thread_id,recipient=excluded.recipient,initial_message_id=excluded.initial_message_id,last_synced_at=excluded.last_synced_at''',
                    (company_id,thread_id,'',first,datetime.now().isoformat(timespec='minutes')))
        inbound=con.execute("SELECT COUNT(*) FROM system_messages WHERE company_id=? AND direction='inbound'",(company_id,)).fetchone()[0]
        con.execute('UPDATE companies SET last_contact=?,status=CASE WHEN ? > 0 AND status IN (\'Applied\',\'No response\') THEN \'Replied\' ELSE status END WHERE id=?',
                    (datetime.now().isoformat(timespec='minutes'),inbound,company_id))
        con.commit(); con.close()

    def load_conversation(self):
        self.conversation_text.config(state='normal'); self.conversation_text.delete('1.0','end')
        if not self.selected_id:
            self.conversation_status.config(text='Select a company that was emailed through this app.')
        else:
            con=db(); thread=con.execute('SELECT * FROM system_threads WHERE company_id=?',(self.selected_id,)).fetchone()
            messages=con.execute('SELECT * FROM system_messages WHERE company_id=? ORDER BY internal_date',(self.selected_id,)).fetchall(); con.close()
            if not thread:
                self.conversation_status.config(text='No system-sent email for this company yet.')
            else:
                self.conversation_status.config(text='Tracked Gmail thread • last synced: '+(thread['last_synced_at'] or 'Never'))
                for message in messages:
                    label='YOU SENT' if message['direction']=='outbound' else 'THEY REPLIED'
                    self.conversation_text.insert('end',f"{label}  •  {message['sent_at']}\n{message['sender']} → {message['recipient']}\nSubject: {message['subject']}\n\n{message['body'].strip()}\n\n{'─'*56}\n\n")
        self.conversation_text.config(state='disabled')

    def refresh_conversation(self):
        if not self.selected_id: messagebox.showwarning('Select company','Select a company first.'); return
        con=db(); thread=con.execute('SELECT gmail_thread_id FROM system_threads WHERE company_id=?',(self.selected_id,)).fetchone(); con.close()
        if not thread: messagebox.showinfo('No tracked conversation','Send the first email through this app. Only threads created here are available.'); return
        if not self.settings.get('credentials_path') or not Path(self.settings['credentials_path']).is_file():
            messagebox.showerror('Gmail not configured','Select your Google OAuth credentials.json in Profile & Gmail Setup.'); return
        if self._conversation_syncing: return
        self._conversation_syncing=True; self.conversation_status.config(text='Refreshing this system email thread…')
        threading.Thread(target=self._conversation_refresh_worker,args=(self.selected_id,thread['gmail_thread_id'],False),daemon=True).start()

    def _conversation_refresh_worker(self,company_id,thread_id,silent=False):
        try:
            self._sync_gmail_thread(self._gmail_service(),company_id,thread_id)
            self.after(0,lambda:self._conversation_refresh_done(None,silent))
        except Exception as e:
            self.after(0,lambda err=str(e):self._conversation_refresh_done(err,silent))

    def _conversation_refresh_done(self,error,silent=False):
        self._conversation_syncing=False
        if error:
            if not silent: messagebox.showerror('Conversation refresh failed',error)
        else:
            self.refresh(); self.load_conversation()

    def _auto_refresh_conversation(self):
        """Poll only the selected app-created thread, never the whole mailbox."""
        try:
            if self.selected_id and not self._conversation_syncing and self.settings.get('credentials_path') and Path(self.settings['credentials_path']).is_file():
                con=db(); thread=con.execute('SELECT gmail_thread_id FROM system_threads WHERE company_id=?',(self.selected_id,)).fetchone(); con.close()
                if thread:
                    self._conversation_syncing=True
                    threading.Thread(target=self._conversation_refresh_worker,args=(self.selected_id,thread['gmail_thread_id'],True),daemon=True).start()
        finally:
            self.after(60000, self._auto_refresh_conversation)

    def send_reply(self):
        if not self.selected_id: messagebox.showwarning('Select company','Select a company first.'); return
        body=self.reply_text.get('1.0','end').strip()
        if not body: messagebox.showwarning('Reply message','Write a reply before sending.'); return
        con=db(); thread=con.execute('SELECT gmail_thread_id FROM system_threads WHERE company_id=?',(self.selected_id,)).fetchone(); company=con.execute('SELECT * FROM companies WHERE id=?',(self.selected_id,)).fetchone(); con.close()
        if not thread: messagebox.showerror('No system conversation','The first email must be sent through this app before you can reply here.'); return
        if not messagebox.askyesno('Review reply',f'To: {company["hr_email"]}\n\n{body}\n\nSend this reply in the tracked system conversation?'): return
        threading.Thread(target=self._reply_worker,args=(company,thread['gmail_thread_id'],body),daemon=True).start()

    def _reply_worker(self,company,thread_id,body):
        try:
            from email.message import EmailMessage
            import base64
            service=self._gmail_service(); thread=service.users().threads().get(userId='me',id=thread_id,format='full').execute()
            latest=(thread.get('messages') or [])[-1]; headers=self._message_headers(latest)
            subject=headers.get('subject','Application follow-up')
            if not subject.lower().startswith('re:'): subject='Re: '+subject
            msg=EmailMessage(); msg['To']=company['hr_email']; msg['Subject']=subject
            if headers.get('message-id'): msg['In-Reply-To']=headers['message-id']; msg['References']=headers['message-id']
            msg.set_content(body); raw=base64.urlsafe_b64encode(msg.as_bytes()).decode()
            service.users().messages().send(userId='me',body={'raw':raw,'threadId':thread_id}).execute()
            self._sync_gmail_thread(service,company['id'],thread_id)
            self.after(0,lambda:self._reply_done(None))
        except Exception as e:
            self.after(0,lambda err=str(e):self._reply_done(err))

    def _reply_done(self,error):
        if error: messagebox.showerror('Reply failed',error)
        else:
            self.reply_text.delete('1.0','end'); self.refresh(); self.load_conversation(); messagebox.showinfo('Reply sent','Your reply was sent and saved to this system conversation.')

if __name__=='__main__':
    app=App()
    if not db().execute('SELECT COUNT(*) FROM companies').fetchone()[0]:
        # Offer the original workbook if it sits beside the app.
        default=APP_DIR/'CareeReX_IT_highlight.xlsx'
        if default.exists():
            try: import_excel(default)
            except Exception: pass
    app.refresh(); app.mainloop()
