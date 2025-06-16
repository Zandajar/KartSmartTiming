from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_race_results():
    number = input("Write session id: ")
    driver = webdriver.Chrome()
    driver.get(f"https://timing.batyrshin.name/tracks/narvskaya/heats/{number}")

    try:
        # change in future
        results = []
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        tables = driver.find_elements(By.TAG_NAME, "table")

        for i, table in enumerate(tables, 1):

            rows = table.find_elements(By.TAG_NAME, "tr")

            for row in rows:
                cells = row.find_elements(By.XPATH, ".//th|.//td")
                row_text = [cell.text.strip() for cell in cells]
                results.append(row_text)


    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()
    return results

raw_data = get_race_results()
print(raw_data)

def find_subarray_index():
    for index, subarray in enumerate(raw_data):
        if "Gap" in subarray:
            return index
    return -1

def get_driver_names():
    return raw_data[1]

def get_driver_place():
    return get_driver_names().index(input("Write driver name: "))

def get_kart_number():
    return raw_data[2]

def get_time_list():
    return raw_data[3:find_subarray_index()]

# test id - 82924
print(get_time_list())