import requests
from app.config import Settings

headers = {'X-Api-Key': Settings.DAYS_YEAR_API_X_API_KEY}
response = requests.get("https://www.daysoftheyear.com/api/v1/today", headers=headers)
response_json = response.json()


year, month, day = 2022, 1, 1
url = f"https://www.daysoftheyear.com/api/v1/date/{year:04d}/{month:02d}/{day:02d}"
print(url)

response = requests.get(url, headers=headers)
response_json = response.json()

print(response_json)
