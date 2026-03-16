import os
from instagrapi import Client

USERNAME = os.getenv("IG_USERNAME")
PASSWORD = os.getenv("IG_PASSWORD")

cl = Client()

print("กำลัง login Instagram...")

cl.login(USERNAME, PASSWORD)

cl.dump_settings("session.json")

print("สร้าง session สำเร็จ")