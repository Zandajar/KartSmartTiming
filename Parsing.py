from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_race_results():
    driver = webdriver.Chrome()
    driver.get(f"https://timing.batyrshin.name/tracks/narvskaya/heats/82924")

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
        return results


    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        driver.quit()

print(get_race_results())