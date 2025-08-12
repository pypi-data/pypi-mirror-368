# 2023/10/16 빌드
# 2023/12/27 셀레니움 세이프브라우징 해제 옵션 추가
# 2024/08/22 Teams 채팅 메시지 함수 추가

from myinfo import *
from colorama import init, Back, Fore, Style
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoAlertPresentException, TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from datetime import datetime
from time import sleep
import pytesseract
import shutil
import os
import sys
import pyperclip
import requests
import json
from jira import JIRA
import pandas as pd

# colorama 초기화
init(autoreset=True)

# 날짜
now = datetime.now()
today = datetime.today().strftime('%Y-%m-%d')
date_mdhm = now.strftime('%m%d%H%M')
temp_folder = 'c:/rpa_temp/'

# temp_folder 초기화
if os.path.isdir(temp_folder) :
    for file in os.listdir(temp_folder):
        try:
            shutil.rmtree(temp_folder)
        except Exception as e:
            pass

if not os.path.exists(temp_folder):
    os.makedirs(temp_folder)

# 확인 팝업 처리
def handle_alert(driver):
    while True:
        try:
            alert = driver.switch_to.alert
            alert.accept()
            break
        except:
            sleep(1)

# 로딩 처리
def handle_loading(driver):
    while True:
        try:
            # 얼럿이 있는지 먼저 확인
            alert = driver.switch_to.alert
            # 얼럿이 존재할 경우 아무 작업도 하지 않음
            break  # 얼럿이 있어도 계속 대기
        except NoAlertPresentException:
            # 얼럿이 없을 경우 로딩 요소가 더 이상 존재하지 않을 때까지 대기
            try:
                WebDriverWait(driver, 1).until_not(EC.presence_of_element_located((By.ID, 'loading')))
                sleep(1)
                break
            except TimeoutException:
                # 로딩이 계속 진행 중일 경우 계속 대기
                continue

# 로그 타임 처리
def current_time():
    now = datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    time_list = time_str.split(" ")
    time_str = "[" +  time_list[0] + " " + time_list[1] + "]"
    return time_str

# 크롬 실행
def create_webbrowser():
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-features=InsecureDownloadWarnings")
    # options.add_argument("--headless")
    options.add_experimental_option('detach', True)  # 브라우저 바로 닫힘 방지
    options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 불필요한 메시지 제거
    options.add_experimental_option('prefs', {'download.default_directory':r'C:\rpa_temp' , 'safebrowsing.enabled': 'False'})
    driver = webdriver.Chrome(options=options)

    return driver

# sdp url 처리
def get_text_after_pattern(pattern):
    patterns = {
        "PRD": "",
        "QA": "qt-",
        "QA2": "qt2-",
    }
    if pattern in patterns:
        return patterns[pattern]
    return None

# SDP 자동 로그인
def sdp_login(target_server):
    server_url = get_text_after_pattern(target_server)
    url = f'http://{server_url}kic.smartdesk.lge.com/admin/main.lge'
    ep_url = 'http://newep.lge.com/portal/main/portalMain.do'
    if target_server == 'PRD':
        print(f'[RPA] 운영 서버에 {EPID} 계정으로 로그인 합니다.')
        options = Options()
        options.page_load_strategy = 'none'  # 'none'으로 설정하면 타임아웃 없이 계속 로드됨
        options.add_argument("--start-maximized")
        options.add_argument("--disable-features=InsecureDownloadWarnings")
        options.add_experimental_option('detach', True)  # 브라우저 바로 닫힘 방지
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 불필요한 메시지 제거
        options.add_experimental_option('prefs', {'download.default_directory':r'C:\rpa_temp' , 'safebrowsing.enabled': 'False'})
        driver = webdriver.Chrome(options=options)
        driver.get(ep_url)
        
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'USER')))
        sleep(1)
        driver.find_element(By.ID,'USER').send_keys(EPID)
        driver.find_element(By.ID,'LDAPPASSWORD').send_keys(EPPW)
        driver.implicitly_wait(2)
        driver.find_element(By.ID,'OTP').click()

        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])

        driver.find_element(By.ID,'pw').send_keys(EPPW)
        driver.find_element(By.ID,'myButton').click()

        sleep(1)
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
        driver.switch_to.window(driver.window_handles[1])
        driver.find_element(By.XPATH,'//*[@id="TA_01"]/div[4]/div[1]').click()
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(3))
        driver.switch_to.window(driver.window_handles[2])

        while True:
            try:
                driver.refresh()
                element1 = driver.find_element(By.ID,'photo_imageK')
                element_png = element1.screenshot_as_png 
                with open("otpimg.png", "wb") as file: file.write(element_png)
                pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
                otpimg = pytesseract.image_to_string(r'otpimg.png')
                driver.find_element(By.ID,'bizidK').send_keys(XID)
                driver.find_element(By.ID,'pcodeK').send_keys(BDAY)
                driver.find_element(By.ID,'answerK').send_keys(otpimg.replace(" ",""))
                driver.find_element(By.XPATH,'//*[@id="form1"]/div[1]/table/tbody/tr[8]/td/input[1]').click() 
                sleep(2) 
                try:
                    sleep(1)
                    result = Alert(driver)
                    print("[RPA] OTP 입력 오류, 재시도 합니다.")
                    result.accept()
                except:
                    print("[RPA] OTP 정상 입력.")
                    break
            except:
                pass

        sleep(1)
        WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(4))
        driver.switch_to.window(driver.window_handles[3])
        OTPD = driver.find_element(By.XPATH,'//*[@id="loadingK"]/b').text
        driver.close()
        driver.switch_to.window(driver.window_handles[2])
        driver.close()
        driver.switch_to.window(driver.window_handles[1])
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element(By.ID,'OTPPASSWORD').send_keys(OTPD)
        driver.find_element(By.ID,'loginSsobtn').click()
        sleep(1)
        
        while True:
            try:
                driver.get(ep_url)
                sleep(0.5)
                driver.find_element(By.ID,'USER').send_keys(EPID)
                driver.find_element(By.ID,'LDAPPASSWORD').send_keys(EPPW)
                driver.find_element(By.ID,'OTPPASSWORD').click()
                input(f'{Fore.RED}[ERROR] 로그인 오류, 수동 로그인 후 엔터키 입력..{Style.RESET_ALL}')
                continue
            except:
                driver.get(url)
                break  

        return driver

    elif target_server == 'QA':
        print(f'[RPA] QA 서버에 {QAID} 계정으로 로그인 합니다.')
        server_url = get_text_after_pattern(target_server)
        url = f'http://{server_url}kic.smartdesk.lge.com/admin/main.lge'
        options = Options()
        options.page_load_strategy = 'none'  # 'none'으로 설정하면 타임아웃 없이 계속 로드됨
        options.add_argument("--start-maximized")
        options.add_argument("--disable-features=InsecureDownloadWarnings")
        options.add_experimental_option('detach', True)  # 브라우저 바로 닫힘 방지
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 불필요한 메시지 제거
        options.add_experimental_option('prefs', {'download.default_directory':r'C:\rpa_temp' , 'safebrowsing.enabled': 'False'})
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        handle_alert(driver)
        driver.find_element(By.ID,'USER').send_keys(QAID)
        driver.find_element(By.ID,'LDAPPASSWORD').send_keys(QAPW)
        driver.find_element(By.ID,'loginSsobtn').click() 
        # 비밀번호 변경 메시지 처리
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.dismiss()
        except:
            pass

        pyperclip.copy(url)
        print('[RPA] QA서버 http 접근을 위해, 브라우저에서 url 을 직접 입력해 주세요 (url 이 복사 되었습니다.)')

        while True :
            if url in driver.current_url:
                break
            else:
                print(f'[RPA] url 입력 까지 대기 합니다.')
                print(f'[RPA] 현제 페이지 : {driver.current_url}')
                sleep(3)
        return driver

    else :
        print(f'[RPA] QA2 서버에 {QAID} 계정으로 로그인 합니다.')
        server_url = get_text_after_pattern(target_server)
        url = f'http://{server_url}kic.smartdesk.lge.com/admin/main.lge'
        options = Options()
        options.page_load_strategy = 'none'  # 'none'으로 설정하면 타임아웃 없이 계속 로드됨
        options.add_argument("--start-maximized")
        options.add_argument("--disable-features=InsecureDownloadWarnings")
        options.add_experimental_option('detach', True)  # 브라우저 바로 닫힘 방지
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # 불필요한 메시지 제거
        options.add_experimental_option('prefs', {'download.default_directory':r'C:\rpa_temp' , 'safebrowsing.enabled': 'False'})
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        handle_alert(driver)
        driver.find_element(By.ID,'USER').send_keys(QAID)
        driver.find_element(By.ID,'LDAPPASSWORD').send_keys(QAPW)
        driver.find_element(By.ID,'loginSsobtn').click() 
        # 비밀번호 변경 메시지 처리
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            alert.dismiss()
        except:
            pass
        driver.get(url)
        return driver

# 화면 보호기 방지
import ctypes
ES_CONTINUOUS = 0x80000000
ES_DISPLAY_REQUIRED = 0x00000002
SetThreadExecutionState = ctypes.windll.kernel32.SetThreadExecutionState
# 화면 보호기 방지 설정
def prevent_screensaver():
    return SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED)
# 화면 보호기 방지 해제 설정
def allow_screensaver():
    return SetThreadExecutionState(ES_CONTINUOUS)

# 오브 젝트 조작
def find_e(driver, locator, action, value=None, index=None, timeout=10, max_tries=3):
    for i in range(max_tries):
        try:
            elements = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located(locator))
            if index is not None:
                element = elements[index]
            else:
                element = elements[0]
            if action == 'click':
                element.click()
            elif action == 'send_keys':
                element.send_keys(value)
            elif action == 'clear':
                element.clear()
            else:
                raise ValueError(f"Unsupported action '{action}'")
            break
        except TimeoutException:
            print(current_time(),f"Timeout waiting for element located by {locator}, attempt {i+1} of {max_tries}")
    else:
        print(current_time(),f"Failed to locate element after {max_tries} tries")

def rpa_progress(status):
    # 현재 실행 중인 파이썬 파일명을 얻습니다.
    file_path = sys.argv[0]

    # 파일명만 추출합니다.
    file_name = os.path.basename(file_path)

    # 파일명 + '시작'을 출력합니다.
    print('\n[RPA] ' + current_time() + ' ' + file_name + ' ' +  status)

    return file_name


import ctypes
import os

ES_CONTINUOUS = 0x80000000
ES_DISPLAY_REQUIRED = 0x00000002
SetThreadExecutionState = ctypes.windll.kernel32.SetThreadExecutionState

# 화면 보호기 방지 설정
def prevent_screensaver():
    return SetThreadExecutionState(ES_CONTINUOUS | ES_DISPLAY_REQUIRED)

# 화면 보호기 방지 해제 설정
def allow_screensaver():
    return SetThreadExecutionState(ES_CONTINUOUS)

# 디스플레이 끄기 및 절전 모드 비활성화
def disable_power_settings():
    os.system("powercfg -change -monitor-timeout-ac 0")
    os.system("powercfg -change -standby-timeout-ac 0")
    os.system("powercfg -change -hibernate-timeout-ac 0")

# 전원 설정 복구
def enable_power_settings(monitor_timeout, standby_timeout, hibernate_timeout):
    os.system(f"powercfg -change -monitor-timeout-ac {monitor_timeout}")
    os.system(f"powercfg -change -standby-timeout-ac {standby_timeout}")
    os.system(f"powercfg -change -hibernate-timeout-ac {hibernate_timeout}")

def print_webhook(webhook_url, webhook_data, n_print=None):
    # webhook_data에 HTML 테이블 스타일링 적용
    styled_data = (webhook_data
                   .replace('<table border="1" class="dataframe">', '<table border="1" style="border-collapse: collapse;">')
                   .replace('<tr style="text-align: right;">', '<tr style="text-align: center;">')
                   .replace('<th>', '<th style="padding: 4px;color:white;background-color:#000000;text-align:center;font-size:13px;max-width:300px;">')
                   .replace('<td>', '<td style="padding: 4px;font-size:12px;max-width:300px;word-break:break-all;">')
                   .replace('&lt;', '<')
                   .replace('&gt;', '>'))
    
    # 전송할 데이터 구성
    data = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.0",
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": '🕹 ' + styled_data,
                            "wrap": True
                        }
                    ]
                }
            }
        ]
    }
    
    # HTTP POST 요청 보내기
    response = requests.post(webhook_url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    
    # n_print가 없을 때만 print 호출
    if not n_print:
        print(styled_data)  # 스타일링된 데이터를 출력
    
    return response

def select_jira_issue(jira, jql_query):
    """
    JIRA에서 특정 JQL 조건의 이슈를 조회하고 사용자에게 선택하도록 함.
    
    :param jira: JIRA 객체
    :param jql_query: JQL 쿼리 문자열
    :return: 선택된 이슈 키 (예: 'ABC-123') 또는 None
    """
    jira_issues = [issue.key for issue in jira.search_issues(jql_query, maxResults=100)]
    
    if not jira_issues:
        print(f"{Back.RED}{Fore.WHITE}🚨 검색된 JIRA 이슈가 없습니다.{Style.RESET_ALL}")
        return None
    
    idx_list = list(range(1, len(jira_issues) + 1))
    print(f'\n{Back.BLUE}{Fore.WHITE}▪ JIRA 요청 리스트 {Style.RESET_ALL}')
    for idx, issue_key in enumerate(jira_issues, 1):
        issue = jira.issue(issue_key)
        print(f'{Fore.BLUE} {idx}. {issue_key} {issue.fields.summary} {Style.RESET_ALL}')
    print('-' * 90)
    
    if len(jira_issues) == 1:
        s = "1"
        print(f' >> 단일 항목이므로 자동 선택: {s}')
    else:
        s = input(f' >> 원하는 설정건의 순번을 입력해 주세요 ({idx_list[0]} ~ {idx_list[-1]}) : ')
    
    if not s.isdigit() or int(s) not in idx_list:
        print(f'{Back.RED}{Fore.WHITE}🚨 순번 입력이 잘못 되었습니다. RPA를 종료합니다.{Style.RESET_ALL}')
        return None
    
    selected_issue_key = jira_issues[int(s) - 1]
    print(f'\n{Fore.YELLOW}{s}. {selected_issue_key} 설정을 시작합니다.\n{Style.RESET_ALL}')
    
    return selected_issue_key  # 🔥 이슈 키만 반환

# ✅ 글로벌 변수 선언 (최초 실행 전 None 상태)
load_df = None
load_filename = None
load_sheetname = None

def download_jira_attachment(jira, issue_key, temp_folder, extensions=None):

    global load_df, load_filename, load_sheetname  # ✅ 글로벌 변수 선언

    print(f"조회할 이슈 키: {issue_key}")
    try:
        jira_issue = jira.issue(issue_key)
        print(f"이슈 객체 로드 완료: {jira_issue}")
    except Exception as e:
        print(f"🚨 JIRA 이슈를 가져오는 중 오류 발생: {e}")
        return None, None, None  # 오류 발생 시 None 반환

    attachments = [(att.filename, att.content) for att in jira_issue.fields.attachment]

    if extensions:
        attachments = [(fn, url) for fn, url in attachments if any(fn.endswith(ext) for ext in extensions)]

    if not attachments:
        print("\n다운로드할 파일이 없습니다.")
        return None, None, None  # 첨부 파일 없으면 None 반환

    if len(attachments) == 1:
        selection = 0
        print(f"\n{attachments[0][0]} 파일을 자동으로 다운로드합니다.")
    else:
        print("\n다운로드 가능한 파일 목록:")
        for idx, (filename, _) in enumerate(attachments, start=1):
            print(f"{idx}. {filename}")

        try:
            selection = int(input("다운로드할 파일 번호를 입력하세요: ")) - 1
            if selection not in range(len(attachments)):
                print("잘못된 번호입니다. 다시 확인해 주세요.")
                return None, None, None  # 잘못된 번호 입력 시 None 반환
        except ValueError:
            print("올바른 숫자를 입력하세요.")
            return None, None, None  # 숫자 오류 시 None 반환

    load_filename, url = attachments[selection]  # ✅ 자동 글로벌 변수 저장
    attachment_path = os.path.join(temp_folder, load_filename)

    r = jira._session.get(url, stream=True)
    with open(attachment_path, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)

    print(f"다운로드 완료: {attachment_path}")

    if load_filename.endswith('.xlsx'):
        xls = pd.ExcelFile(attachment_path)
        print("\n엑셀 파일의 시트 목록:")
        for idx, sheet in enumerate(xls.sheet_names, start=1):
            print(f"{idx}. {sheet}")

        try:
            sheet_selection = int(input("불러올 시트 번호를 입력하세요: ")) - 1
            if sheet_selection not in range(len(xls.sheet_names)):
                print("잘못된 번호입니다. 기본 첫 번째 시트를 불러옵니다.")
                sheet_selection = 0
        except ValueError:
            print("올바른 숫자를 입력하세요. 기본 첫 번째 시트를 불러옵니다.")
            sheet_selection = 0

        load_sheetname = xls.sheet_names[sheet_selection]  # ✅ 자동 글로벌 변수 저장
        load_df = pd.read_excel(xls, sheet_name=load_sheetname)  # ✅ 자동 글로벌 변수 저장

        return load_df, load_filename, load_sheetname  # 여러 값을 반환

    return None, None, None  # 엑셀 파일이 아니면 None 반환

# 구글 데이터 프레임 가져오기
def get_dataframe(doc, sheet_name):
    worksheet = doc.worksheet(sheet_name)
    values = worksheet.get_all_values()
    return pd.DataFrame(values[1:], columns=values[0]) if values else pd.DataFrame()

# 얼럿 메세지 처리 하기 
def check_alert(driver, expected_message):
    try:
        WebDriverWait(driver, 60).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"[ALERT] 얼럿 발견: {alert_text}")
        alert.accept()
        return alert_text
    except TimeoutException:
        print(f"[ALERT] 60초 동안 '{expected_message}' 얼럿이 나타나지 않았습니다.")
        return ""
    except Exception as e:
        print(f"[ALERT] 얼럿 처리 중 오류 발생: {e}")
        return ""