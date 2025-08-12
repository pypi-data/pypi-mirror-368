import os
import json
import zlib
import base64

def load_fun_data(filename):
    file_path = os.path.join(os.path.dirname(__file__), filename + ".json.enc")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"⚠️ فایل {filename}.json موجود نیست!")

    with open(file_path, "r", encoding="utf-8") as f:
        encoded_data = f.read()

    # رمزگشایی از Base64
    compressed_data = base64.b64decode(encoded_data)

    # باز کردن فشرده‌سازی zlib
    json_data = zlib.decompress(compressed_data).decode("utf-8")

    return json.loads(json_data)
