import inspect
import json
import threading
from calendar import monthrange
from datetime import datetime
from sys import exc_info, argv
from time import sleep, time
from urllib.parse import unquote, parse_qs, urlparse
from uuid import getnode

from art import text2art
from colorama import Fore
from ntplib import NTPClient
from phonenumbers import region_code_for_number, parse, NumberParseException

from autowebx.files import add

__lock = threading.Lock()


class AccountError(Exception):
    """Raised when an account fails to create"""


def int_input(prompt: str, default: int = 1) -> int:
    try:
        return int(input(prompt))
    except ValueError:
        return default


def intro(name: str):
    user_id = getnode()
    sync_print('=' * 85)
    sync_print(f'{Fore.LIGHTYELLOW_EX}{text2art("Hazem3010", "banner3")}')
    indent = " " * int((85 - len(f'{name}    ::    Your ID: {user_id}')) / 2)
    sync_print(f'{indent}{Fore.GREEN}{name}{Fore.LIGHTMAGENTA_EX}    ::    {Fore.CYAN}Your ID: {user_id}{Fore.RESET}')
    sync_print('=' * 85)
    return str(user_id)


class PhoneNumber:
    def __init__(self, phone_number):
        self.number = phone_number
        try:
            parsed_number = parse(f'+{phone_number}')
            self.prefix = parsed_number.country_code
            self.country = region_code_for_number(parsed_number)
        except NumberParseException:
            self.prefix = None
            self.country = None



def sync_print(*content, end: str = '\n'):
    __lock.acquire()
    print(*content, end=end, flush=True)
    add(f"{' '.join(map(str, content))}{end}", 'output.txt')
    __lock.release()


class URL:
    def __init__(self, url: str):
        self.__parameters__ = parse_qs(urlparse(url).query)

    def get(self, parameter: str) -> str:
        return self.__parameters__.get(parameter)[0]


def __get_function__() -> None:
    http = argv[1]
    http_content = open(http, 'r').read()
    lines = http_content.split('\n')
    method, endpoint, _ = lines[0].split(' ')
    endpoint = unquote(endpoint).replace("\"", "\\\"")

    # Extract headers properly
    headers = {}
    host = ""
    for line in lines[1:]:
        if line == '':
            break
        line_data = line.split(':', 1)
        if len(line_data) == 2:
            key, value = line_data[0].strip(), unquote(line_data[1].strip())
            headers[key] = value
            if key.lower() == "host":
                host = value

    if not host:
        raise ValueError("Host header is missing in the request")

    result = f'def function(self):    # {http}\n    url = "https://{host}{endpoint}"\n\n'

    result += "    headers = {\n"
    for key, value in headers.items():
        result += f"        '{key}': '{value}',\n"
    result = result[:-2] + "\n    }\n\n"

    content = http_content.split('\n\n')
    with_payload = False
    json_payload = False
    if len(content) > 1 and content[1] != '':
        with_payload = True
        result += '    payload = '
        variables_content = content[1].strip()
        if variables_content.startswith('{'):
            payload = json.loads(variables_content)
            json_payload = True
        else:
            variables = content[1].strip().split('&')
            payload = {}
            for item in variables:
                try:
                    pair = item.split('=')
                    payload[pair[0]] = unquote(pair[1])
                except IndexError:
                    pass

        payload = json.dumps(payload, indent=4).replace('\n', '\n    ').replace(': true', ': True')
        payload = payload.replace(': false', ': False')
        result += unquote(payload)
        result = result + '\n\n'

    args = f'(url, headers=headers{", json=payload)" if json_payload else ", data=payload)" if with_payload else ")"}'
    result += f'    response = self.session.{method.lower()}{args}\n'
    result = result.replace('\t', '    ')

    open('function.py', 'w', encoding='UTF-8').write(result)


def ranges(numbers: list[str]) -> list[str]:
    return list({number[:-3] for number in numbers})


def days_in_month(year: int, month: int) -> int:
    return monthrange(year, month)[1]


def handle_threads(threads: int, total: int, target) -> None:
    for i in range(1, total + 1):
        target(count=i).start()
        while True:
            active = 0
            for thread in threading.enumerate():
                if thread.name.startswith('Task_'):
                    active += 1
            if active < threads:
                break
            sleep(1)

    done = False
    while not done:
        done = True
        for thread in threading.enumerate():
            if thread.name.startswith('Task_'):
                done = False
                break



def var_name(var):
    for name, value in inspect.stack()[1].frame.f_locals.items():
        if value is var:
            return name
    return None


useragents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
    "Safari/537.36 Edg/123.0.2420.81",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
    "Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
    "Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.4; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 "
    "Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 "
    "Safari/537.36 OPR/109.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux i686; rv:124.0) Gecko/20100101 Firefox/124.0"
]

__locales_str = (
    "af_ZAam_ETar_AEar_BHar_DZar_EGar_IQar_JOar_KWar_LBar_LYar_MAar_OMar_QAar_SAar_SDar_SYar_TNar_YEaz_AZbe_BYbg_BGbn_B"
    "Dbn_INbs_BAca_EScs_CZcy_GBda_DKde_ATde_BEde_CHde_DEde_LIde_LUdv_MVel_CYel_GRen_AUen_BWen_CAen_GBen_HKen_IEen_INen_"
    "JMen_MHen_MTen_NAen_NZen_PHen_PKen_SGen_TTen_USen_ZAen_ZWes_ARes_BOes_CLes_COes_CRes_DOes_ECes_ESes_GTes_HNes_MXes"
    "_NIes_PAes_PEes_PRes_PYes_SVes_USes_UYes_VEet_EEeu_ESfa_IRfi_FIfo_FOfr_BEfr_BFfr_BIfr_BJfr_BLfr_CAfr_CDfr_CFfr_CGf"
    "r_CHfr_CIfr_CMfr_DJfr_FRfr_GAfr_GFfr_GNfr_GPfr_GQfr_HTfr_KMfr_LUfr_MAfr_MCfr_MFfr_MGfr_MLfr_MQfr_NEfr_PFfr_PMfr_RE"
    "fr_RWfr_SCfr_SNfr_SYfr_TDfr_TGfr_TNfr_VUfr_WFfr_YTga_IEgl_ESgu_INha_NGhe_ILhi_INhr_BAhr_HRhu_HUhy_AMid_IDig_NGis_I"
    "Sit_CHit_ITja_JPka_GEkk_KZkm_KHkn_INko_KRky_KGlo_LAlt_LTlv_LVmg_MGmk_MKml_INmn_MNmr_INms_BNms_MYmt_MTnb_NOne_NPnl_"
    "AWnl_BEnl_NLnn_NOom_ETor_INpa_INpl_PLps_AFpt_AOpt_BRpt_CHpt_CVpt_FRpt_GQpt_GWpt_LUpt_MOpt_MZpt_PTpt_STpt_TLro_MDro"
    "_ROru_BYru_KGru_KZru_MDru_RUru_UArw_RWsd_INsi_LKsk_SKsl_SIso_DJso_ETso_KEso_SOsq_ALsr_BAsr_MEsr_RSsv_AXsv_FIsv_SEs"
    "w_CDsw_KEsw_TZsw_UGta_INta_LKte_INth_THti_ERti_ETtl_PHtn_BWtn_ZAtr_CYtr_TRug_CNuk_UAur_INur_PKuz_AFuz_UZvi_VNyo_NG"
    "zh_CNzh_HKzh_MOzh_SGzh_TWzu_ZA"
)


def locales():
    return [__locales_str[i:i + 5] for i in range(0, len(__locales_str), 5)]


def exception_line():
    return exc_info()[-1].tb_lineno


def internet_time():
    return datetime.fromtimestamp(NTPClient().request('pool.ntp.org').tx_time)


class Timer:
    def __init__(self, timeout, message):
        self.timeout = timeout
        self.start = time()
        self.message = message

    def __call__(self):
        if time() - self.start > self.timeout:
            raise TimeoutError(self.message)
