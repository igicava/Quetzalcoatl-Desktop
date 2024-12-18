# -*- coding: utf-8 -*-
import sys
import requests
import json
import threading
import mdl
import log_reg

global_username=""
security_token=""

# Запуск приложения
if __name__ == "__main__":
    with open("server_config.json", "r") as file:
        cng = json.loads(file.read())
        mdl.ADDR=cng["addr"]
        mdl.PROTO=cng["proto"]
        mdl.SERVER=f"{mdl.PROTO}://{mdl.ADDR}"
        mdl.WS_SERVER=f"ws://{mdl.ADDR}"

    print("Client app is start")

    try: 
        with open("config.json", "r") as file:
            i = file.read()
            print(i)
        data = json.loads(i)

        r = requests.get(f"{mdl.SERVER}/login", json=data)

        R_tocken = r.json()
        security_token = R_tocken["token"]
        print(security_token)

        r = requests.get(f"{mdl.SERVER}/msgs", json=R_tocken)
        print(r.json())

        if r.status_code == 200:
            print("OK")
        else:
            print("Error get messages from server")

        global_username = data["username"]

        with open("token.txt", "w+") as file:
            file.write(R_tocken["token"])

        thread = threading.Thread(target=mdl.RunWS)
        thread.start()
        print("Websocket start")

        
        mdl.mp.Run(r.json(), data["username"])

    except FileNotFoundError:
        regForm = log_reg.LoginRegisterWindow()
        regForm.Run()

    sys.exit(mdl.application.exec())