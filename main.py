from pprint import pprint
import requests
import csv
from openpyxl import Workbook

from config import SECURITY_KEY


def access_token(func):
    def wrapper(*args, **kwargs):
        responce = func(*args, **kwargs)
        if responce == 401:
            pyrus.get_access_token()
            res = func(*args, **kwargs)
            return res
        return responce

    return wrapper


class PyrusClient:
    def __init__(self) -> None:
        self.access_token = ""

    def get_access_token(self):
        url = "https://api.pyrus.com/v4/auth"
        r = requests.post(
            url,
            json={"login": "pyrrusdocs@gmail.com", "security_key": SECURITY_KEY},
        )
        self.access_token = f"Bearer {r.json()['access_token']}"

    @access_token
    def get_id_from_form(self):
        headers = {"Authorization": self.access_token}
        url = "https://api.pyrus.com/v4/forms"
        r = requests.get(url, headers=headers)
        if r.status_code == 401:
            return r.status_code
        forms = r.json()
        return forms["forms"][0]["id"]

    @access_token
    def get_tasks(self, form_id):
        headers = {"Authorization": self.access_token}
        url = f"https://api.pyrus.com/v4/forms/{form_id}/register"
        r = requests.get(url, headers=headers)
        if r.status_code == 401:
            return r.status_code
        tasks = r.json()
        return tasks

    @access_token
    def download_file_from_form(self, file_id):
        headers = {"Authorization": self.access_token}
        url = f"https://api.pyrus.com/v4/files/download/{file_id}"
        r = requests.get(url, stream=True, headers=headers)
        if r.status_code == 401:
            return r.status_code
        with open(f"test.txt", "wb") as file:
            for chunk in r.iter_content(chunk_size=128):
                file.write(chunk)

    @access_token
    def upload_file(self, file_path):
        url = "https://api.pyrus.com/v4/files/upload"
        headers = {
            "Authorization": self.access_token,
        }
        files = {"file": ("test1.txt", open(file_path, "rb"))}

        r = requests.post(url, headers=headers, files=files)

        if r.status_code == 401:
            return r.status_code

        return r.json()

    @access_token
    def add_attachment(self, task_id, file_id):
        headers = {"Authorization": self.access_token}
        url = f"https://api.pyrus.com/v4/tasks/{task_id}/comments"
        r = requests.post(
            url,
            json={
                "attachments": [f"{file_id}"],
                "text": "Done",
            },
            headers=headers,
        )
        if r.status_code == 401:
            return r.status_code
        return r.json()

    @access_token
    def change_task_field(self, task_id, guid):
        headers = {"Authorization": self.access_token}
        url = f"https://api.pyrus.com/v4/tasks/{task_id}/comments"
        r = requests.post(
            url,
            json={
                "field_updates": [
                    {
                        "id": 26,
                        "value": [{"guid": guid}],
                    }
                ],
            },
            headers=headers,
        )
        if r.status_code == 401:
            return r.status_code
        return r.json()

    @access_token
    def download_tasks_from_form(self, form_id):
        headers = {"Authorization": self.access_token}
        url = f"https://api.pyrus.com/v4/forms/{form_id}/register?format=csv"
        r = requests.get(url, headers=headers, stream=True)
        if r.status_code == 401:
            return r.status_code

        decoded_content = r.content.decode("utf-8")
        reader = csv.reader(decoded_content.splitlines(), delimiter=",")

        wb = Workbook()
        ws = wb.active

        for row in reader:
            ws.append(row)
        wb.save(filename="test.xlsx")


pyrus = PyrusClient()

# pyrus.get_access_token()
form_id = pyrus.get_id_from_form()
tasks = pyrus.get_tasks(form_id)
# Выбран конкретный id для созданной мной таски
task_id = tasks["tasks"][0]["id"]
file_id = tasks["tasks"][0]["fields"][11]["value"]["fields"][5]["value"][0]["id"]
pyrus.download_file_from_form(file_id)
guid = pyrus.upload_file(file_path="test1.txt")["guid"]
file_id = pyrus.change_task_field(task_id, guid)["task"]["fields"][13]["value"][
    "fields"
][1]["value"][-1]["id"]
res = pyrus.add_attachment(task_id, file_id)
pyrus.download_tasks_from_form(form_id)
