# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:25:45 2022

@author: m88t448
"""

# Import the libraries
import tkinter as tk
import serial
import serial.tools.list_ports
from time import sleep
import threading as thr

# Create the window object
def connect_menu_init():
    global root, connect_btn, refresh_btn, msg
    root = tk.Tk()
    root.geometry("1250x300")
    root.configure(background='white')
    tk.Frame(root)
    
    # Port label
    port_lbl = tk.Label(root, text="Available Port(s): ", bg="white", borderwidth=1)
    port_lbl.grid(column=0, row=1, pady=10, padx=30)
    
    # Baudrate label
    bdr_lbl = tk.Label(root, text="Baudrate: ", bg="white", borderwidth=1)
    bdr_lbl.grid(column=0, row=2, pady=10, padx=30)
    
    # Refresh button to reset ports listed
    refresh_btn = tk.Button(root, text="Refresh", borderwidth=1, height=2,width=10,
                            command=update_coms)
    refresh_btn.grid(column=2,row=1,pady=10,padx=30)
    
    # Connect button
    connect_btn = tk.Button(root, text="Connect", borderwidth=1, height=2,width=10, 
                            state="disabled", command=connection)
    connect_btn.grid(column=2,row=2,pady=10,padx=30)
    
    # Displays messages from the Arduino
    msg_lbl = tk.Label(root, text="Arduino messages: ", bg="white", borderwidth=1)
    msg_lbl.grid(column=0, row=3, pady=10, padx=30)
    
    # Display message window
    msg = tk.Label(root, bg="white", borderwidth=1)
    msg.grid(columnspan=2, column=1, row=3, pady=10, padx=30)
    
    # These functions are further below
    baud_select()
    update_coms()

# Populates the pressure pump controller area
def pressure_pump_menu_init():
    global n
    # Preset number of pumps
    n = 4
    root.title("Pressure Pump Control")
    
    # Setup the headers
    sph_lbl = tk.Label(root, text = "Setpoint entry (psig)"  , width=20, height=2, borderwidth=1, relief="solid", bg="white")
    sph_lbl.grid(column = 4, row = 0)
    cph_lbl = tk.Label(root, text = "Current setpoint (psig)", width=20, height=2, borderwidth=1, relief="solid", bg="white")
    cph_lbl.grid(column = 6, row = 0)
    msh_lbl = tk.Label(root, text = "Measured value (psig)"  , width=20, height=2, borderwidth=1, relief="solid", bg="white")
    msh_lbl.grid(column = 7, row = 0)
    
    # Setup the valve labels
    vlv_lbl = [[0] for i in range(n)]
    for i in range (0,n):
        vlv_lbl[i] = tk.Label(root, text = "Valve #" + str(i), height=2, width = 10, borderwidth=1, relief="solid", bg="white")
        vlv_lbl[i].grid(column = 3, row = i+1, pady=10)
        
    # These functions are further below
    setpoint_display()
    measuredpoint_display()

# Populates setpoint entries, change buttons, and displays
def setpoint_display():
    # Set the setpoint entries
    global nsp_lbl, sps_var, sp_ind
    sps_var = [tk.StringVar(root, value = "0") for i in range(n)]
    
    sps_lbl = [[] for i in range(n)]
    sps_lbl[0] = tk.Entry(root, text = sps_var[0], width = 10, borderwidth=1, relief="solid")
    sps_lbl[1] = tk.Entry(root, text = sps_var[1], width = 10, borderwidth=1, relief="solid")
    sps_lbl[2] = tk.Entry(root, text = sps_var[2], width = 10, borderwidth=1, relief="solid")
    sps_lbl[3] = tk.Entry(root, text = sps_var[3], width = 10, borderwidth=1, relief="solid")
    
    # Set the new stpoint displays
    nsp_var = [tk.StringVar(root, value = "0") for i in range(n)]
    
    nsp_lbl = [[] for i in range(n)]
    nsp_lbl[0] = tk.Label(root, text = nsp_var[0].get(), width = 10, height=2, borderwidth=1, relief="solid")
    nsp_lbl[1] = tk.Label(root, text = nsp_var[1].get(), width = 10, height=2, borderwidth=1, relief="solid")
    nsp_lbl[2] = tk.Label(root, text = nsp_var[2].get(), width = 10, height=2, borderwidth=1, relief="solid")
    nsp_lbl[3] = tk.Label(root, text = nsp_var[3].get(), width = 10, height=2, borderwidth=1, relief="solid")
    
    # Change setpoint buttons
    csp_btn = [[0] for i in range(n)]
    csp_btn[0] = tk.Button(root, text="\N{RIGHTWARDS BLACK ARROW}", width = 10, height=2, command = lambda: setpoint_change(0))
    csp_btn[1] = tk.Button(root, text="\N{RIGHTWARDS BLACK ARROW}", width = 10, height=2, command = lambda: setpoint_change(1))
    csp_btn[2] = tk.Button(root, text="\N{RIGHTWARDS BLACK ARROW}", width = 10, height=2, command = lambda: setpoint_change(2))
    csp_btn[3] = tk.Button(root, text="\N{RIGHTWARDS BLACK ARROW}", width = 10, height=2, command = lambda: setpoint_change(3))
    
    # Setpoint acceptance indicators
    sp_ind = [[0] for i in range(n)]
    sp_ind[0] = tk.Label(root, width = 2, height=2)
    sp_ind[1] = tk.Label(root, width = 2, height=2)
    sp_ind[2] = tk.Label(root, width = 2, height=2)
    sp_ind[3] = tk.Label(root, width = 2, height=2)
    
    for i in range (0,n):
        sps_lbl[i].grid(column=4, row=i+1)
        nsp_lbl[i].grid(column=6, row=i+1)
        csp_btn[i].grid(column=5, row=i+1)
        sp_ind[i].grid(column=8, row=i+1)

# Populates the measured points display
def measuredpoint_display():
    global mps_var, mps_lbl
    mps_var = [tk.StringVar(root, value = "0") for i in range(n)]
    
    mps_lbl = [[] for i in range(n)]
    mps_lbl[0] = tk.Label(root, text = mps_var[0].get(), width = 10, height=2, borderwidth=1, relief="solid")
    mps_lbl[1] = tk.Label(root, text = mps_var[1].get(), width = 10, height=2, borderwidth=1, relief="solid")
    mps_lbl[2] = tk.Label(root, text = mps_var[2].get(), width = 10, height=2, borderwidth=1, relief="solid")
    mps_lbl[3] = tk.Label(root, text = mps_var[3].get(), width = 10, height=2, borderwidth=1, relief="solid")
    
    for i in range (0,n):
        mps_lbl[i].grid(column=7, row=i+1)

def setpoint_change(i):
    # Change setpoint function from the entry to the new setpoint display
    nsp_lbl[i]["text"] = sps_var[i].get()
    cmd = str(i) + "," + str(sps_var[i].get()) + "\n"
    ard.write(cmd.encode('ascii'))

# Checks if there is a connection with the Arduino
def connect_check(*args):
    if "-" in com_click.get() or "-" in bdr_click.get():
        connect_btn["state"] = "disable"
    else:
        connect_btn["state"] = "active"

# Creates the drop down menu to list the available Baudrates
def baud_select():
    global bdr_click, bdr_drop
    bdr_click = tk.StringVar()
    bdrs= ["-","110","300","600","1200","2400","4800","9600","14400","19200","38400","57600","115200","128000","256000"]
    bdr_click.set(bdrs[0])
    
    bdr_drop = tk.OptionMenu(root, bdr_click, *bdrs, command=connect_check)
    bdr_drop.config(width=20)
    bdr_drop.grid(column=1, row=2, padx=20)

# Connects to the Arduino
def update_coms():
    global com_click, com_drop
    ports = serial.tools.list_ports.comports()
    coms = [com[0] for com in ports]
    coms.insert(0,"-")
    
    try:
        com_drop.destroy()
    except:
        pass
    
    com_click = tk.StringVar()
    com_click.set(coms[0])
    
    com_drop = tk.OptionMenu(root, com_click, *coms, command=connect_check)
    com_drop.config(width = 20)
    com_drop.grid(column=1, row=1, padx=20)
    connect_check(0)

# Reads the Arduino output string
def read_arduino():
    output = []
    serbuff = ""
    i = 0
    while serdata:
        try:
            c = ard.read().decode('ascii')
            if len(c) == 0:
                break
            if c == '\n':
                serbuff += "\n"
                b = serbuff.strip()
                if b == 'Arduino is seady to start':
                    msg["text"] = b
                else:
                    output.append(b)
                    output1 = output[i].split(',')
                    i += 1
                    display_arduino(output1)
                serbuff = ""
            else:
                serbuff += c
        except:
            pass

# Updates the display areas with the Arduinos output
# Sets the connection indicator to green if the setpoints sent and stored are the same
# If the set points are not the same, then the connection indicator is set to red
def display_arduino(output1):
    try:
        vlv = int(output1[0])
        sp = output1[1]
        if sp == nsp_lbl[vlv]["text"]:
            mp = output1[2]
            mps_var[vlv].set(mp)
            mps_lbl[vlv]["text"] = mps_var[vlv].get()
            sp_ind[vlv]["bg"] = "green"
        else:
            sp_ind[vlv]["bg"] = "red"
    except:
        pass
    
# Updates changes to the connection
def connection():
    global ard, serdata
    # Closes the Arduino once the disconnect button is pressed
    if connect_btn["text"] in "Disconnect":
        connect_btn["text"]  = "Connect"
        refresh_btn["state"] = "active"
        bdr_drop["state"]    = "active"
        com_drop["state"]    = "active"
        serdata = False
        ard.close()
    # Or else it reads the data
    else:
        serdata = True
        connect_btn["text"]  = "Disconnect"
        refresh_btn["state"] = "disable"
        bdr_drop["state"]    = "disable"
        com_drop["state"]    = "disable"
        port = com_click.get()
        baud = bdr_click.get()
        try:
            ard = serial.Serial(port, int(baud))
        except:
            msg["text"] = "Having trouble connecting"
            pass
        # Uses threading to read the Arduino while the GUI loop is running
        t1 = thr.Thread(target = read_arduino)
        t1.daemon = True
        t1.start()

# Functions from above
connect_menu_init()
pressure_pump_menu_init()

# Starts the mainloop
root.mainloop()