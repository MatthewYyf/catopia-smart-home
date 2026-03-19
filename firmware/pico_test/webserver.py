import network
import socket
import binascii
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
from lcd1602 import LCD1602

ssid = 'yuxuan_hotspot'
password = ''

i2c = machine.I2C(1, scl=machine.Pin(7), sda=machine.Pin(6), freq=400000)
display = LCD1602(i2c, 2, 16)
display.display()

def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    print(wlan.status())
    
    while wlan.isconnected() == False:
        print('Waiting for connection...', wlan.status())
        sleep(3)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temperature, state):
    #Template HTML
    html = f"""
            <!DOCTYPE html>
            <html>
            <form action="/sendtext">
            <input type="text" name="message"/>
            <input type="submit" value="Send"/>
            </form>
            <form action="/cleardisplay">
            <input type="submit" value="Clear"/>
            </form>
            </body>
            </html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    pico_led.off()
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        print(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request.startswith('/cleardisplay?'):
            display.clear()
        elif request.startswith('/sendtext?'):
            try:
                text = request.split('message=')[1]
                print("Textbox value:", text)
                display.clear()
                display.print(text)
            except:
                text = 'Invalid'
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()
        
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
