# -*- coding: utf-8 -*-
import csv
import subprocess
import os
import sys
import time


# 이 스크립트는 사이트 코드와 URL이 포함된 CSV 파일을 읽고, 셸에서 실행할 명령어를 생성하여 실행합니다.
# 이 명령어는 Playwright를 사용해 웹 페이지의 페이지네이션 링크를 찾기 위해 설계되었습니다.

def execute_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # print("stdout", result.stdout.decode('utf-8'))
        print("stderr", result.stderr.decode('utf-8'))
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
    


print("Reading CSV file...")
file_path = os.path.join(os.path.dirname(__file__), '0424full.csv')
with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    data = [row for row in reader]
    for index, row in enumerate(data):
        if index <= 68:
            continue
        if index > 88:
            break
        print(row[0], row[2])  # Replace 0 with the index of the desired field (e.g., site_code column index)

        com = (f"claude --dangerously-skip-permissions -p '{row[0]}의 URL {row[2]}에 playwright를 이용해서 접근하여 " 
            " pagination bar의 링크를 찾아 3 혹은 4 페이지에 이동한 후 location.href를 이용하여 page index의 키이름을 확인해서 " 
            " 다음과 같이 json 형식으로 응답해줘. {{\"page_url\" : \"https://www.anony.or.kr/elsl?dlsl=4&pageindex={{next_page}}\"}} " 
            " key value에서 value는 {{next_page}}로 표시해줘. 사이트코드를 파일명으로 확장자는  .json으로 파일트 만들어서 ./page 아래에 저장해줘.' ")

        

        result = execute_bash_command(com)  # Example command    
        if result:
            print(result)  # Print the output of the command


