# -*- coding: utf-8 -*-
import csv
import subprocess
import os
import sys
import time

def execute_bash_command(command):
    try:
        result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return None
    


print("Reading CSV file...")
file_path = os.path.join(os.path.dirname(__file__), 'server_site.csv')
with open(file_path, mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    data = [row for row in reader]
    for index, row in enumerate(data):
        if index < 5:
            continue
        if index > 12:
            break
        print(row[0], row[2])  # Replace 0 with the index of the desired field (e.g., site_code column index)

        com = f"claude --dangerously-skip-permissions -p '{row[0]}의 URL {row[2]}에 playwright를 이용해서 접근하여 pagination bar의 링크를 찾아 3 혹은 4 페이지에 이동한 후 location.href를 이용하여 page index의 키이름을 확인해서 다음과 형식으로 알려줘. 'https://www.anony.or.kr/elsl?dlsl=4&pageindex={{next_page}}' 같이 그 사이트의 전체  href url로  알려줘.' "

        result = execute_bash_command(com)  # Example command    
        if result:
            print(result)  # Print the output of the command

# execute bash command
