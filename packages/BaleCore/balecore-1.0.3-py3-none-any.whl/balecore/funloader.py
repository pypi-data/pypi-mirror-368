import pkgutil

def fun(filename: str) -> bytes:
    return pkgutil.get_data(__name__, f"fun/{filename}")

def list_fun() -> list[str]:
    return [
        "alaki.json.enc",
        "chandsaletbod.json.enc",
        "chanvaghte.json.enc",
        "dastan.json.enc",
        "deghatkardin.json.enc",
        "dialog.json.enc",
        "eteraf.json.enc",
        "fantezi.json.enc",
        "khaterat.json.enc",
        "mrghazi.json.enc",
        "panapa.json.enc",
        "ravanshenasi.json.enc",
    ]
