from pywinauto import application
import os, time, json

path = os.path.dirname(os.path.abspath(__file__))


with open(path+'/../env.json', 'r') as f:
    config = json.load(f)

creonid = config['private']["creonid"]
pwd = config['private']["creonpwd"]
pwdcert = config['private']["creonpwdcert"]


try:
    os.system('taskkill /IM coStarter* /F /T')
    os.system('taskkill /IM CpStart* /F /T')
    os.system('taskkill /IM DibServer* /F /T')
    os.system('wmic process where "name like \'%coStarter%\'" call terminate')
    os.system('wmic process where "name like \'%Cpstart%\'" call terminate')
    os.system('wmic process where "name like \'%DibServer%\'" call terminate')
except:
    pass

time.sleep(5)
app = application.Application()
app.start(f'C:\CREON\STARTER\coStarter.exe /prj:cp /id:{creonid} /pwd:{pwd} /pwdcert:{pwdcert} /autostart')
time.sleep(60)