from rpa_config import *
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pathlib import Path
import requests
import os
from datetime import datetime

teams_header = '<b style="color: white; background-color: darkblue;">&nbsp;Q-Card Spec 다운로드 및 업로드&nbsp;</b> '

# 구글 마스터에서 설정 대상 정보 가져오기
print(f'구글 마스터에서 설정 정보를 수집 합니다.')

scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
json_file_name = 'My Settings/zeta-cortex-374507-ab6c3da63f82.json'
credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file_name, scope)
gc = gspread.authorize(credentials)

# 요청 리스트용 스프레드시트
request_spreadsheet_key = '1XJ043Oun3VTDjAyGEVSAZ6GUQiTH_-rJoT-8hTVw-gE'
request_doc = gc.open_by_key(request_spreadsheet_key)

# Q-Card 시트에서 기본 정보 가져오기
spec_df = get_dataframe(request_doc, 'Q-Card')
qcard_worksheet = request_doc.worksheet('Q-Card')

# 업로드 여부가 'Y'가 아닌 것만 필터링 (Spec Create 컬럼 기준)
if 'Spec Create' in spec_df.columns:
    rawdata_df = spec_df[spec_df['Spec Create'] != 'Y'].reset_index()
else:
    # Spec Create 컬럼이 없으면 전체 데이터
    rawdata_df = spec_df.reset_index()

if len(rawdata_df) == 0:
    print('대상 건이 없습니다.')
    exit()

# 지라 로그인하기
jira = JIRA(server="http://jira.lge.com/issue", auth=(JID,JPW))

print(f'\n{Back.BLUE}{Fore.WHITE} ▪ JIRA 첨부파일 다운로드 대상 리스트 {Style.RESET_ALL}')
idx_list = []
for idx, row in rawdata_df.iterrows():
    jira_key = row['JIRA']
    try:
        issue = jira.issue(jira_key)
        idx_list.append(idx + 1)
        upload_status = row.get('Spec Create', '')
        print(f'{Fore.BLUE} {idx + 1}. {row["Title"]} - [{jira_key}] {issue.fields.summary} - 파일: {row["스펙파일명"]} - 시트: {row["시트명"]}{Style.RESET_ALL}')
    except Exception as e:
        print(f'{Fore.RED} {idx + 1}. {row["Title"]} - [{jira_key}] JIRA 조회 실패: {e}{Style.RESET_ALL}')
        idx_list.append(idx + 1)

print("="*150)
s = input(f'>> 원하는 다운로드건의 순번을 입력해 주세요 ({idx_list[0]} ~ {idx_list[-1]}): ')

# 입력 값 확인 후 진행
if int(s) in idx_list:
    try:
        selected_row = rawdata_df.iloc[int(s)-1]
        iss = selected_row['JIRA']
        iss_url = f'http://jira.lge.com/issue/browse/{iss}'
        issue = jira.issue(iss)
        
        print(f'\n{Fore.YELLOW}{s}. {selected_row["Title"]} - [{iss}] {issue.fields.summary} 다운로드 및 업로드를 시작 합니다.{Style.RESET_ALL}')
        
        # 스펙 파일명과 시트명 가져오기
        spec_filename = selected_row['스펙파일명']
        sheet_names = [name.strip() for name in selected_row['시트명'].split(',')]
        
        # 파일 경로 설정
        file_folder = pyfolder + 'qcard/'
        if not os.path.exists(file_folder):
            os.makedirs(file_folder)
        
        spec_file_path = file_folder + spec_filename + '.xlsx'
        
        print(f'스펙 파일: {spec_file_path}')
        print(f'처리할 시트: {sheet_names}')
        
        # JIRA에서 첨부파일 다운로드
        print(f"JIRA 이슈 {iss}에서 첨부파일을 조회합니다.")
        attachments = [(att.filename, att.content) for att in issue.fields.attachment]
        
        # 엑셀 파일만 필터링
        excel_attachments = [(fn, url) for fn, url in attachments if fn.endswith(('.xlsx', '.xls'))]
        
        if not excel_attachments:
            print(f'JIRA에 엑셀 첨부파일이 없습니다.')
            teams_text = f'<b style="color: red;"> [ERROR] JIRA에 엑셀 첨부파일이 없습니다</b><br>JIRA: {iss}'
            print_webhook(HOMERPA, teams_header + teams_text, n_print=True)
            exit()
        
        # 첫 번째 엑셀 파일 자동 선택 또는 사용자 선택
        if len(excel_attachments) == 1:
            selection = 0
            print(f"엑셀 파일을 자동으로 선택했습니다: {excel_attachments[0][0]}")
        else:
            print("\n다운로드 가능한 엑셀 파일 목록:")
            for idx, (filename, _) in enumerate(excel_attachments, start=1):
                print(f"{idx}. {filename}")
            try:
                selection = int(input("다운로드할 파일 번호를 입력하세요: ")) - 1
                if selection not in range(len(excel_attachments)):
                    print("잘못된 번호입니다. 첫 번째 파일을 선택합니다.")
                    selection = 0
            except ValueError:
                print("올바른 숫자를 입력하세요. 첫 번째 파일을 선택합니다.")
                selection = 0
        
        selected_filename, attachment_url = excel_attachments[selection]
        print(f'JIRA 첨부파일 다운로드 중: {selected_filename}')
        
        try:
            # JIRA 세션을 사용하여 첨부파일 다운로드
            response = jira._session.get(attachment_url, stream=True)
            
            if response.status_code == 200:
                with open(spec_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print(f'JIRA 첨부파일 다운로드 완료: {spec_file_path}')
            else:
                print(f'JIRA 첨부파일 다운로드 실패: HTTP {response.status_code}')
                teams_text = f'<b style="color: red;"> [ERROR] JIRA 첨부파일 다운로드 실패</b><br>HTTP {response.status_code}'
                print_webhook(HOMERPA, teams_header + teams_text, n_print=True)
                exit()
                
        except Exception as e:
            print(f'JIRA 첨부파일 다운로드 중 오류 발생: {e}')
            teams_text = f'<b style="color: red;"> [ERROR] JIRA 첨부파일 다운로드 중 오류</b><br>{str(e)}'
            print_webhook(HOMERPA, teams_header + teams_text, n_print=True)
            exit()
        
    except Exception as e:
        print(f'{Back.RED}{Fore.WHITE}🚨 순번 입력이 잘못 되었습니다: {e}. 프로그램을 종료 합니다.{Style.RESET_ALL}')
        quit()
else:
    print(f'{Back.RED}{Fore.WHITE}🚨 순번 입력이 잘못 되었습니다. 프로그램을 종료 합니다.{Style.RESET_ALL}')
    quit()

# Title 자동 생성 함수
def generate_titles(df, file_name, sheet_name):
    """Title이 비어있는 경우 자동으로 Title 생성"""
    try:
        df = df.fillna('')
        s_title = f'{date_mdhm[:4]}_{file_name.split("_")[1]}_'
        
        # Title이 비어있는 행 확인
        empty_title = df[df['Title'] == '']
        
        if len(empty_title) > 0:
            print(f'Title 값이 비어 있습니다. 자동 생성 합니다.')
            
            # 시트 유형에 따라 그룹핑 기준 결정
            if 'Display' in sheet_name and 'Shelf' not in sheet_name:
                # Q-Card Display: Country, Version, Platform, Senior Flag 기준
                # Version과 Senior Flag는 Product-Platform에서 분리해야 할 수도 있음
                group_columns = ['Country', 'Product-Platform']
                
            elif 'Shelf Display' in sheet_name:
                # Q-Card Shelf Display: Q-Card Type, Q-Card Title, Product-Platform, Country 기준
                group_columns = ['Q-Card Type', 'Q-Card Title', 'Product-Platform', 'Country']
                
            elif 'App' in sheet_name or 'BookMark' in sheet_name or 'Curation' in sheet_name:
                # App/BookMark Curation: Q-Card Type, Q-Card Title, Product-Platform, Country 기준
                group_columns = ['Q-Card Type', 'Q-Card Title', 'Product-Platform', 'Country']
                
            else:
                # 기본: Country, Product-Platform 기준
                group_columns = ['Country', 'Product-Platform']
            
            # 존재하는 컬럼만 사용
            available_group_columns = [col for col in group_columns if col in df.columns and not df[col].isna().all()]
            
            if available_group_columns:
                # 그룹핑
                df['group_id'] = df.groupby(available_group_columns).ngroup()
                
                # 첫 번째 등장 순서대로 Case 번호 할당
                group_mapping = {}
                case_counter = 1
                
                for idx, row in df.iterrows():
                    group_values = tuple(row[col] for col in available_group_columns)
                    
                    if group_values not in group_mapping:
                        if 'Shelf Display' in sheet_name:
                            # Shelf Display의 경우 Q-Card Type 포함
                            group_type = row.get('Q-Card Type', 'DEFAULT')
                            group_mapping[group_values] = f"{s_title}{group_type}_{case_counter:03d}"
                        elif 'App' in sheet_name or 'BookMark' in sheet_name or 'Curation' in sheet_name:
                            # App/BookMark Curation의 경우 Q-Card Title을 숫자로 포맷팅
                            qcard_title = str(row.get('Q-Card Title', '0'))
                            qcard_title_formatted = "{:0>5}".format(qcard_title)
                            group_mapping[group_values] = f"{s_title}{qcard_title_formatted}_{case_counter:03d}"
                        else:
                            # Display의 경우 단순 카운터
                            group_mapping[group_values] = f"{s_title}{case_counter:03d}"
                        
                        case_counter += 1
                
                # Title 컬럼 생성
                df['Title'] = df.apply(
                    lambda row: group_mapping[tuple(row[col] for col in available_group_columns)], 
                    axis=1
                )
                
                # 임시 컬럼 제거
                df = df.drop('group_id', axis=1)
                
                print(f'Title 자동 생성 완료: {len(df["Title"].drop_duplicates())}개 그룹')
            else:
                print('그룹핑 가능한 컬럼이 없어 Title 생성을 건너뜁니다.')
        else:
            print('모든 행에 Title이 있습니다.')
            
    except Exception as e:
        print(f'Title 생성 중 오류 발생: {e}')
    
    return df

# Q-Card_Spec 시트에 데이터 업로드 함수
def upload_to_qcard_spec(df, file_name, sheet_name):
    """엑셀 데이터를 Q-Card_Spec 시트에 업로드"""
    try:
        # Q-Card_Spec 워크시트 가져오기 또는 생성
        try:
            spec_worksheet = request_doc.worksheet('Q-Card_Spec')
            print(f'기존 Q-Card_Spec 시트 사용')
        except:
            # 시트가 없으면 생성
            spec_worksheet = request_doc.add_worksheet(title='Q-Card_Spec', rows=1000, cols=17)
            print(f'Q-Card_Spec 시트 생성')
            
        # 헤더 확인 및 설정
        try:
            existing_headers = spec_worksheet.row_values(1)
        except:
            existing_headers = []
            
        headers = ['File', 'Sheet', 'Q-Card Type', 'Q-Card Title', 'Q-Card Mgmt', 'Product-Platform', 'Country', 'Ordering', 'Service Type', 'App ID', 'App Title', 'Book Mark Title', 'Book Mark Icon Image', 'web URL', 'Recomm', 'Title', '완료 여부']
        if not existing_headers or existing_headers != headers:
            spec_worksheet.update('A1:Q1', [headers])
            print(f'헤더 설정 완료')
        
        # File과 Sheet 컬럼 추가
        df_upload = df.copy()
        df_upload.insert(0, 'File', file_name)
        df_upload.insert(1, 'Sheet', sheet_name)
        
        # 기존 데이터 가져오기
        try:
            existing_data = spec_worksheet.get_all_records()
            existing_df = pd.DataFrame(existing_data)
        except:
            existing_df = pd.DataFrame()
        
        if not existing_df.empty:
            # 동일한 File, Sheet 조합 제거
            mask = (existing_df['File'] == file_name) & (existing_df['Sheet'] == sheet_name)
            remaining_df = existing_df[~mask]
            
            print(f'기존 동일 데이터 {mask.sum()}건 제거')
            
            # 전체 시트 클리어 후 헤더와 남은 데이터 다시 입력
            spec_worksheet.clear()
            spec_worksheet.update('A1:Q1', [headers])
            
            if not remaining_df.empty:
                # 기존 데이터 업로드
                remaining_values = remaining_df.fillna('').values.tolist()
                if remaining_values:
                    spec_worksheet.update(f'A2:Q{len(remaining_values)+1}', remaining_values)
                start_row = len(remaining_values) + 2
            else:
                start_row = 2
        else:
            start_row = 2
        
        # 새 데이터 업로드
        upload_values = df_upload.fillna('').values.tolist()
        if upload_values:
            end_row = start_row + len(upload_values) - 1
            spec_worksheet.update(f'A{start_row}:Q{end_row}', upload_values)
        
        print(f'Q-Card_Spec 시트에 {len(df_upload)}건 업로드 완료')
        return True
        
    except Exception as e:
        print(f'Q-Card_Spec 업로드 실패: {e}')
        return False

# 시트별 데이터 업로드
print(f'\n{"="*50}')
print(f"엑셀 데이터를 Q-Card_Spec 시트에 업로드")
print(f"{"="*50}")

uploaded_sheets = []
failed_sheets = []

for sheet_name in sheet_names:
    try:
        print(f"\n시트 '{sheet_name}' 데이터 업로드 중...")
        
        # 엑셀 파일에서 해당 시트 읽기
        df = pd.read_excel(spec_file_path, sheet_name=sheet_name)
        print(f"시트 '{sheet_name}' 데이터 로드 완료: {len(df)}행")
        
        # 원본 컬럼명 출력
        print(f"원본 컬럼: {list(df.columns)}")
        
        # 필요한 컬럼만 선택 (존재하는 컬럼만)
        required_columns = ['Q-Card Type', 'Q-Card Title', 'Q-Card Mgmt', 'Product-Platform', 'Country', 'Ordering', 'Service Type', 'App ID', 'App Title', 'Book Mark Title', 'Book Mark Icon Image', 'web URL', 'Recomm', 'Title', '완료 여부']
        
        # 엑셀에 존재하는 컬럼만 사용
        upload_df = pd.DataFrame()
        for req_col in required_columns:
            if req_col in df.columns:
                upload_df[req_col] = df[req_col]
                print(f"컬럼 '{req_col}' 매핑 완료")
            else:
                upload_df[req_col] = ''  # 없는 컬럼은 빈값으로
                print(f"컬럼 '{req_col}' 없음 - 빈값으로 설정")
        
        # Title 자동 생성 (Title이 비어있는 경우)
        upload_df = generate_titles(upload_df, spec_filename, sheet_name)
        
        # 완료 여부 컬럼 기본값 설정
        if '완료 여부' in upload_df.columns:
            if upload_df['완료 여부'].isna().all() or (upload_df['완료 여부'] == '').all():
                upload_df['완료 여부'] = ''
        
        print(f"업로드할 데이터: {len(upload_df)}행 x {len(upload_df.columns)}열")
        
        # Q-Card_Spec 시트에 업로드
        if upload_to_qcard_spec(upload_df, spec_filename, sheet_name):
            uploaded_sheets.append(sheet_name)
            print(f"✅ 시트 '{sheet_name}' 업로드 완료")
        else:
            failed_sheets.append(sheet_name)
            print(f"❌ 시트 '{sheet_name}' 업로드 실패")
        
    except Exception as e:
        failed_sheets.append(sheet_name)
        print(f"❌ 시트 '{sheet_name}' 처리 중 오류 발생: {e}")
        continue

# 구글 시트 업로드 여부 업데이트
if len(uploaded_sheets) > 0:
    print(f'\n구글 시트 업로드 여부 업데이트')
    try:
        header_row = qcard_worksheet.row_values(1)
        if 'Spec Create' in header_row:
            target_column = 'Spec Create'
            column_index = header_row.index(target_column) + 1
            column_letter = chr(ord('A') + column_index - 1)
            
            actual_row = selected_row.name + 2  # 인덱스 + 헤더행
            today_date = datetime.now().strftime('%Y-%m-%d')
            
            qcard_worksheet.update(f'{column_letter}{actual_row}', today_date)
            print(f'구글 시트 Spec Create 업데이트 완료: {today_date}')
        else:
            print('Spec Create 컬럼이 없어 업데이트를 건너뜁니다.')
        
    except Exception as e:
        print(f'구글 시트 업데이트 실패: {e}')

# 최종 결과 출력
print(f'\n{"="*50}')
print(f"업로드 결과")
print(f"{"="*50}")
print(f"✅ 성공: {len(uploaded_sheets)}개 시트")
if uploaded_sheets:
    for sheet in uploaded_sheets:
        print(f"   - {sheet}")

if failed_sheets:
    print(f"❌ 실패: {len(failed_sheets)}개 시트")
    for sheet in failed_sheets:
        print(f"   - {sheet}")

# Teams 메시지 전송
if failed_sheets:
    teams_text = f'<b style="color: orange;"> Q-Card Spec 업로드가 일부 완료되었습니다! ⚠️</b><br>'
    teams_text += f'&nbsp;▪ JIRA: <a href="{iss_url}">{iss}</a><br>'
    teams_text += f'&nbsp;▪ 파일: {spec_filename}<br>'
    teams_text += f'&nbsp;▪ 성공: {len(uploaded_sheets)}개 시트 ({", ".join(uploaded_sheets)})<br>'
    teams_text += f'&nbsp;▪ 실패: {len(failed_sheets)}개 시트 ({", ".join(failed_sheets)})<br>'
else:
    teams_text = f'<b style="color: darkgreen;"> Q-Card Spec 업로드가 완료되었습니다! 🙂</b><br>'
    teams_text += f'&nbsp;▪ JIRA: <a href="{iss_url}">{iss}</a><br>'
    teams_text += f'&nbsp;▪ 파일: {spec_filename}<br>'
    teams_text += f'&nbsp;▪ 업로드: {len(uploaded_sheets)}개 시트 ({", ".join(uploaded_sheets)})<br>'

print_webhook(HOMERPA, teams_header + teams_text, n_print=True)

print('\n다운로드 및 업로드 완료🙂')