from tkinter import *
from tkinter import messagebox
from datetime import datetime
# timezone
import pytz
import os
import time
import subprocess

wificlick=0
netwclick=0
sharkclick=0
channelnumber=0;

def on_closing():
	if messagebox.askokcancel("Quit", "Do you want to quit?"):
		window.destroy()
		out=os.system("ifconfig | grep wlan0mon")
		if out==0:
			os.system("sudo killall -9 airodump-ng")
			time.sleep(200/1000)
			os.system("sudo airmon-ng stop wlan0mon")
			time.sleep(200/1000)
		os.system("sudo NetworkManager reset")
		#os.system("sudo nmcli networking off")
		time.sleep(500/1000)
		#os.system("sudo nmcli networking on")
	else:
		messagebox.showinfo("", "Idiot!!! Why click on Close if not sure! destroying window anyway.")
		window.destroy()
		

def readClock():
	# clear the field
	txtYy.delete(0,'end')
	txtMm.delete(0,'end')
	txtDd.delete(0,'end')
	txtHh.delete(0,'end')
	txtMi.delete(0,'end')
	txtSs.delete(0,'end')

	now = datetime.now(pytz.timezone('Asia/Kolkata'))
	if now:
		txtYy.insert(3,now.year)
		txtMm.insert(3,now.month)
		txtDd.insert(3,now.day)
		txtHh.insert(3,now.hour)
		txtMi.insert(3,now.minute)
		txtSs.insert(3,now.second)

def writeClock():
	if txtYy.get()=="":
		messagebox.showinfo("Clock", "yyyy fields is empty")
	elif txtMm.get()=="":
		messagebox.showinfo("Clock", "MM fields is empty")
	elif txtDd.get()=="":
		messagebox.showinfo("Clock", "DD fields is empty")
	elif txtHh.get()=="":
		messagebox.showinfo("Clock", "HH fields is empty")
	elif txtMi.get()=="":
		messagebox.showinfo("Clock", "mm fields is empty")
	elif txtSs.get()=="":
		messagebox.showinfo("Clock", "SS fields is empty")	
	elif not txtYy.get().isnumeric():
		messagebox.showinfo("Clock", "enter digits only in yyyy")	
	elif not txtMm.get().isnumeric():
		messagebox.showinfo("Clock", "enter digits only in MM")	
	elif not txtDd.get().isnumeric():
		messagebox.showinfo("Clock", "enter digits only in DD")	
	elif not txtHh.get().isnumeric():
		messagebox.showinfo("Clock", "enter digits only in HH")	
	elif not txtMi.get().isnumeric():
		messagebox.showinfo("Clock", "enter digits only in mm")	
	elif not txtSs.get().isnumeric():
		messagebox.showinfo("Clock", "enter digits only in SS")	
	else:
		clk = '"'+txtYy.get()+'-'+txtMm.get()+'-'+txtDd.get()+' '+txtHh.get()+':'+txtMi.get()+':'+txtSs.get()+'"'
		#print(clk)
		os.system("sudo timedatectl set-ntp false")
		time.sleep(100/1000)
		stime = "sudo timedatectl set-time "+clk
		print(stime)
		os.system(stime)
		time.sleep(200/1000)
		# if ntp is enabled, and internet then will overrite the clock
		os.system("sudo timedatectl set-ntp true")
		messagebox.showinfo("Clock", "Write Ok")

def validateCh(x):
	ch = int(x)
	match ch:
		# 2.4g channels
		case 1|2|3|4|5|6|7|8|9|10|11|12|13|14:
			return 1
		# 5g channels
		case 36|40|44|48|52|56|60|64|100|104|108|112|116|120|124|128|132|136|140|149|153|157|161|165:
			return 1
		case _:
			return 0

def startMonitor():
	global channelnumber
	out = os.system("ifconfig | grep wlan0mon")
	if out==0:
		messagebox.showinfo("", "wlan0mon already present!")
	else:
		os.system("sudo airmon-ng check kill")
		time.sleep(1)
		if txtCh.get()=="":
			os.system("sudo airmon-ng start wlan0")
			channelnumber=0
			messagebox.showinfo("", "wlan0mon started, Ch# not specified")
		elif txtCh.get().isnumeric():
			ret = validateCh(txtCh.get())
			if ret==1:
				
				channelnumber=txtCh.get()
				cmd = "sudo airmon-ng start wlan0 " + txtCh.get()
				os.system(cmd)
				cmd = "wlan0mon started on ch#"+txtCh.get()
				messagebox.showinfo("", cmd)
			else:
				messagebox.showinfo("", "Invalid channel number, wlan0mon NOT started")
		else:
			messagebox.showinfo("", "Invalid channel number, wlan0mon NOT started")


def stopMonitor():
	out = os.system("ifconfig | grep wlan0mon")
	if out==0:
		os.system("sudo airmon-ng stop wlan0mon")
		messagebox.showinfo("", "wlan0mon stopped, You may want to Restart Network")		
	else:
		messagebox.showinfo("", "wlan0mon is already stopped!")


def launchWireshark():
	global sharkclick
	global channelnumber

	now = int(time.time()) - sharkclick
	if now < 10:
		messagebox.showinfo("", "Wait for 10s and try")
	else:
		out = os.system("ifconfig | grep wlan0mon")
		if out==0:
			os.system("sudo killall -9 wireshark")
			#os.system("sudo killall -s SIGTERM wireshark")
			time.sleep(1)
			## use wireless toolbar to select channel number
			if channelnumber==0:
				messagebox.showinfo("Wireshark", "View > Wireless-Toolbar to select Channel in wireshark")
			os.system("wireshark -i wlan0mon -k -S -l")
			sharkclick = int(time.time())
		else:
			messagebox.showinfo("", "wlan0mon NOT present!")

def networkRestart():
	global netwclick
	now = int(time.time()) - netwclick
	if now < 10:
		messagebox.showinfo("", "Wait for 10s and try")
	else:
		out = os.system("ifconfig | grep wlan0mon")
		if out==0:
			os.system("sudo killall -9 airodump-ng")
			#os.system("sudo killall -s SIGTERM airodump-ng")
			time.sleep(500/1000)
			os.system("sudo airmon-ng stop wlan0mon")
			time.sleep(500/1000)
		os.system("sudo NetworkManager reset")
		messagebox.showinfo("Network", "Reset done")
		netwclick = int(time.time())

def capturestart():
	global channelnumber
	err=0
	channel=""
	if txtCh2.get()=="" and channelnumber==0:
		messagebox.showinfo("", "Ch# num must be provided")
		return
	elif channelnumber!=0 and txtCh2.get()!="":
		messagebox.showinfo("", "Ch# is already set by wlan0mon")
		return
	if txtCh2.get().isnumeric():
		ret = validateCh(txtCh2.get())
		if ret==0:
			messagebox.showinfo("", "Ch# num is invalid")
			err=1
		else:
			channel = " --channel "+txtCh2.get()+" "
	
	if txtHt.get()=="":
		messagebox.showinfo("", "using default: ht20")
		txtHt.insert(3, "ht20")
		ht = " --ht20"
	elif txtHt.get().lower()=="ht20":
		ht = " --ht20"
	elif txtHt.get().lower()=="ht40-":
		ht = " --ht40-"
	elif txtHt.get().lower()=="ht40+":
		ht = " --ht40+"
	else:
		messagebox.showinfo("", "Invalid, using default: ht20")
		txtHt.insert(3, "ht20")
		ht = " --ht20"
	
	
	if txtBssid.get()=="":
		bssid=""
		#messagebox.showinfo("", "BSSID field is empty")
	else:
		bssid=" --bssid "+txtBssid.get()+" "
	
	if txtFile.get()=="":
		wprefix=" --write ~/logs/wlan0mon"
		#messagebox.showinfo("", "BSSID field is empty")
	else:
		wprefix=" --write ~/logs/"+txtFile.get()

	if err==1:
		return
	else:
		out = os.system("ifconfig | grep wlan0mon")
		if out==0:
			cmd = "sudo airodump-ng wlan0mon"+bssid+channel+ht+wprefix+" --beacons --output-format pcap &"
			print(cmd)
			os.system(cmd)
			messagebox.showinfo("", "Capturing started")		
		else:
			messagebox.showinfo("", "wlan0mon is not started yet!")


def capturestop():
	out = os.system("ifconfig | grep wlan0mon")
	if out==0:
		out = os.system("sudo killall -9 airodump-ng")
		#out = os.system("sudo killall -s SIGTERM airodump-ng")
		if out==0:
			messagebox.showinfo("", "Capturing stopped, logs saved in path ~/logs folder")
		else:
			messagebox.showinfo("", "Capturing is already stopped!")		
	else:
		messagebox.showinfo("", "wlan0mon is NOT started yet!")

# not used, coz this will bring up the wlan0 interface (but keep wlan0mon)
# use network reset fn instead 
def wifirestart():
	global wificlick
	now = int(time.time()) - wificlick
	if now < 10:
		messagebox.showinfo("", "Wait for 10s and try")
	else:
		os.system("sudo nmcli radio wifi off")
		time.sleep(1)
		# this cmd will bring up the wlan0 interface
		os.system("sudo nmcli radio wifi on")
		messagebox.showinfo("Wlan", "Reset done")
		wificlick = int(time.time())
	
def getRegd():
	#os.system("iw reg get | grep country")
	out = subprocess.getoutput('iw reg get | grep country')
	#print(out)
	## we want only the 1st words in string, ignore the rest
	## a1 will contain "country US"
	a1,a2=out.split(":")
	## split into "countr" & "US"
	a2,a3=a1.split()
	#print(a2," ",a3)
	# a2 = "country", a3 = "US"
	#print(a3)
	txtregd.delete(0,'end')
	txtregd.insert(0,a3)

def setRegd():
	cmd = "sudo iw reg set "+txtregd.get().upper()
	nxt=txtregd.get().upper()
	ret = os.system(cmd)
	time.sleep(300/1000)
	getRegd()
	prev=txtregd.get().upper()
	if prev==nxt:
		messagebox.showinfo("","Regd set success")
	else:
		messagebox.showinfo("","Regd set fail, code invalid")



# declare the window
window = Tk()

window.title("wlan0mon Control Panel")
window.configure(width=800, height=400)
#window.configure("600x300+10+10")
window.configure(bg='lightgray')

# move window center
winWidth = window.winfo_reqwidth()
winwHeight = window.winfo_reqheight()
posRight = int(window.winfo_screenwidth() / 2 - winWidth / 2)
posDown = int(window.winfo_screenheight() / 2 - winwHeight / 2)
window.geometry("+{}+{}".format(posRight, posDown))

#
lbl_clk = Label(window, text="System Clock", fg='red', font=("Helvetica",16))
lbl_clk.place(x=10, y=15)
txtYy = Entry(window, text="yyyy", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtYy.place(x=10, y=50, height=42, width=100)
txtMm = Entry(window, text="mm", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtMm.place(x=130, y=50, height=42, width=60)
txtDd = Entry(window, text="dd", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtDd.place(x=210, y=50, height=42, width=60)
txtHh = Entry(window, text="hh", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtHh.place(x=290, y=50, height=42, width=60)
txtMi = Entry(window, text="mi", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtMi.place(x=370, y=50, height=42, width=60)
txtSs = Entry(window, text="ss", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtSs.place(x=450, y=50, height=42, width=60)
lbl_Yy = Label(window, text="YYYY", fg='red', font=("Helvetica",16))
lbl_Yy.place(x=35, y=100)
lbl_Mm = Label(window, text="MM", fg='red', font=("Helvetica",16))
lbl_Mm.place(x=145, y=100)
lbl_Dd = Label(window, text="DD", fg='red', font=("Helvetica",16))
lbl_Dd.place(x=225, y=100)
lbl_Hh = Label(window, text="hh", fg='red', font=("Helvetica",16))
lbl_Hh.place(x=310, y=100)
lbl_Mi = Label(window, text="mm", fg='red', font=("Helvetica",16))
lbl_Mi.place(x=383, y=100)
lbl_Ss = Label(window, text="ss", fg='red', font=("Helvetica",16))
lbl_Ss.place(x=470, y=100)

btn_rdclk = Button(window, text="Read Clock", fg='blue', font=("Helvetica",16), command=readClock)
btn_rdclk.place(x=10, y=140)
btn_wrclk = Button(window, text="Write Clock", fg='blue', font=("Helvetica",16), command=writeClock)
btn_wrclk.place(x=180, y=140)
readClock()

#
lbl_mon = Label(window, text="wlan0mon: ", fg='red', font=("Helvetica",16))
lbl_mon.place(x=10, y=200)
btn_stpcap = Button(window, text="Start", fg='blue', font=("Helvetica",16), command=startMonitor)
btn_stpcap.place(x=127, y=195)
btn_sppcap = Button(window, text="Stop", fg='blue', font=("Helvetica",16), command=stopMonitor)
btn_sppcap.place(x=214, y=195)
lbl_Ch = Label(window, text="Ch#", fg='blue', font=("Helvetica",16))
lbl_Ch.place(x=301, y=202)
txtCh = Entry(window, text="Ch", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtCh.place(x=347, y=190, height=42, width=60)

lbl_wsrk = Label(window, text="Wireshark: ", fg='red', font=("Helvetica",16))
lbl_wsrk.place(x=10, y=250)
btn_wsrk = Button(window, text="Launch", fg='blue', font=("Helvetica",16), command=launchWireshark)
btn_wsrk.place(x=125, y=245)
lbl_netw = Label(window, text="Network: ", fg='red', font=("Helvetica",16))
lbl_netw.place(x=242, y=250)
btn_netw = Button(window, text="Reset", fg='blue', font=("Helvetica",16), command=networkRestart)
btn_netw.place(x=332, y=245)

lbl_regd = Label(window, text="Regd: ", fg='red', font=("Helvetica",16))
lbl_regd.place(x=435, y=250)
txtregd = Entry(window, text="regd", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtregd.place(x=508, y=240, height=42, width=60)
btn_regdr = Button(window, text="Get", fg='blue', font=("Helvetica",16), command=getRegd)
btn_regdr.place(x=435, y=195)
btn_regdw = Button(window, text="Set", fg='blue', font=("Helvetica",16), command=setRegd)
btn_regdw.place(x=510, y=195)
getRegd()

lbl_cap = Label(window, text="Capture: ", fg='red', font=("Helvetica",16))
lbl_cap.place(x=10, y=298)
lbl_bssid = Label(window, text="Bssid# ", fg='blue', font=("Helvetica",16))
lbl_bssid.place(x=110, y=298)
txtBssid = Entry(window, text="BSSID", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtBssid.place(x=180, y=285, height=42, width=200)
lbl_ch2 = Label(window, text="Ch# ", fg='blue', font=("Helvetica",16))
lbl_ch2.place(x=390, y=298)
txtCh2 = Entry(window, text="ch2#", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtCh2.place(x=440, y=285, height=42, width=60)
btn_cstart = Button(window, text="Start", fg='blue', font=("Helvetica",16), command=capturestart)
btn_cstart.place(x=510, y=290)

lbl_file = Label(window, text="logfile ", fg='blue', font=("Helvetica",16))
lbl_file.place(x=110, y=342)
#txtFile = Entry(window, text="filename", bg='white', fg='black', bd=5, font=("Helvetica",16), state='disabled')
txtFile = Entry(window, text="filename", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtFile.place(x=180, y=332, height=42, width=200)
btn_cstop = Button(window, text="Stop", fg='blue', font=("Helvetica",16), command=capturestop)
btn_cstop.place(x=510, y=332)
txtHt = Entry(window, text="ht20", bg='white', fg='black', bd=5, font=("Helvetica",16))
txtHt.place(x=430, y=332, height=42, width=70)
txtHt.insert(5,"ht20")

#
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()


