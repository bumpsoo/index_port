from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import pandas as pd
import time

def pull(fileName, chromeDriver):

    # Chrome 드라이버
    webdriver_path = chromeDriver
    service = Service(webdriver_path)
    wd = webdriver.Chrome(service=service)

    # 해외증시 url
    url = 'https://finance.naver.com/world/'
    wd.get(url)


    indices = []

    # 지수명 설정
    quot_section = wd.find_element(By.CLASS_NAME, 'section_quot')
    table_element = quot_section.find_element(By.TAG_NAME, 'table')
    tbody_element = table_element.find_element(By.TAG_NAME, 'thead')
    rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
    for row in rows[1:]:
        index_name_element = row.find_element(By.CLASS_NAME, 'tb_td2')
        index_name = index_name_element.text
        print(f'지수명 : {index_name}')
        indices.append(index_name)

    # 일일 가격데이터 
    with pd.ExcelWriter(fileName) as writer:
        for index in indices:
            wd.get(url)

            # 해당 페이지로 이동하기 위해 지수명 클릭
            quot_section = wd.find_element(By.CLASS_NAME, 'section_quot')
            table_element = quot_section.find_element(By.TAG_NAME, 'table')
            tbody_element = table_element.find_element(By.TAG_NAME, 'thead')
            rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                index_name_element = row.find_element(By.CLASS_NAME, 'tb_td2')
                if index_name_element.text == index:
                    index_element = index_name_element.find_element(By.TAG_NAME, 'a')
                    print(f'인덱스 요소 찾음: {index_element}')
                    index_element.click()
                    break

            # 열 이름을 위한 데이터
            table_element = wd.find_element(By.CLASS_NAME, 'section_quot')
            tbody_element = table_element.find_element(By.TAG_NAME, 'thead')
            table_rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
            data = []
            header = [item.text for item in table_rows[0].find_elements(By.TAG_NAME, 'span')]
            data.append(header)


            # 1~5페이지까지 추출 
            paging_div = wd.find_element(By.ID, 'dayPaging')
            paging_links = paging_div.find_elements(By.TAG_NAME, 'a')

            for i in range(1, 55):
                # 페이징된 번호들 클릭 
                if i % 10 == 1 and i > 1:
                    page_link = wd.find_element(By.CLASS_NAME, 'next')
                else:
                    page_link = wd.find_element(By.ID, f'dayLink{i}')
                
                page_link.click()
                wd.implicitly_wait(5)
                time.sleep(1)
                table_element = wd.find_element(By.CLASS_NAME, 'section_quot')
                tbody_element = table_element.find_element(By.TAG_NAME, 'thead')
                table_rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
                page_data = []
                header = [item.text for item in table_rows[0].find_elements(By.TAG_NAME, 'span')]

                # 일일 가격 데이터 추출
                tbody_element = table_element.find_element(By.TAG_NAME, 'tbody')
                table_rows = tbody_element.find_elements(By.TAG_NAME, 'tr')
                for row in table_rows:
                    row_data = [item.text.replace(',', '') for item in row.find_elements(By.TAG_NAME, 'td')]
                    status_element = row.find_element(By.CLASS_NAME, 'point_status')
                    status = status_element.text
                    if 'point_up' in row.get_attribute('class'):
                        row_data[2] = '+' + status
                    elif 'point_dn' in row.get_attribute('class'):
                        row_data[2] = '-' + status

                    # 날짜 형식을 "YYYY-MM-DD"로 변경
                    row_data[0] = row_data[0].replace('.', '-')

                    page_data.append(row_data)

                data.extend(page_data)


            df = pd.DataFrame(data[1:], columns=data[0])
            sheet_name = index

            # Excel 파일로 저장
            df.to_excel(writer, sheet_name=sheet_name, index=False, header=True)

    # Chrome 브라우저 종료
    wd.quit()
