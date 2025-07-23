from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_race_results(session_id):
    driver = webdriver.Chrome()
    driver.get(f"https://timing.batyrshin.name/tracks/narvskaya/heats/{session_id}")

    try:
        results = []
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        tables = driver.find_elements(By.TAG_NAME, "table")

        for table in tables:
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                cells = row.find_elements(By.XPATH, ".//th|.//td")
                results.append([cell.text.strip() for cell in cells])

    except Exception as e:
        print(f"Ошибка: {e}")
        results = []
    finally:
        driver.quit()
    return results

def find_subarray_index(data, word):
    for index, subarray in enumerate(data):
        if word in subarray:
            return index
    return -1

def get_driver_names(data):
    return data[1] if len(data) > 1 else []

def get_kart_numbers(data):
    return data[2] if len(data) > 2 else []

def get_time_list(data):
    gap_index = find_subarray_index(data, "Gap")
    return data[3:gap_index] if gap_index != -1 else []

def get_side_information(data):
    gap_index = find_subarray_index(data, "Gap")
    if gap_index == -1:
        return []
    return data[gap_index:gap_index + 4]

def get_stint_info(data):
    s1_index = find_subarray_index(data, "S1 kart")
    return data[s1_index:] if s1_index != -1 else []