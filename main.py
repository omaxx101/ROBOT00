# ----------------------------
# Raspberry Pi Pico 2 W — Wi-Fi Robot (Hold-to-Move, Arrow Keys + WASD)
# ----------------------------

import network, socket
from machine import Pin, PWM
from utime import sleep

ROBOT_NAME = "Robot00"   # Change per robot

# ----------------------------
# Wi-Fi setup
# ----------------------------
ssid = "Omax"
password = "12345678"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("Connecting to WiFi...")
while not wlan.isconnected():
    pass

ip = wlan.ifconfig()[0]
print("Connected:", ip)

# ----------------------------
# Motor pins (L298N)
# ----------------------------
IN1 = Pin(27, Pin.OUT)
IN2 = Pin(26, Pin.OUT)
IN3 = Pin(21, Pin.OUT)
IN4 = Pin(20, Pin.OUT)

ENA = PWM(Pin(19))
ENB = PWM(Pin(18))
ENA.freq(1000)
ENB.freq(1000)
speed = 40000
ENA.duty_u16(speed)
ENB.duty_u16(speed)

# ----------------------------
# Motor control
# ----------------------------
def stop_motors():
    IN1.low(); IN2.low()
    IN3.low(); IN4.low()

def forward():
    IN1.high(); IN2.low()
    IN3.high(); IN4.low()

def backward():
    IN1.low(); IN2.high()
    IN3.low(); IN4.high()

def left():
    IN1.low(); IN2.high()
    IN3.high(); IN4.low()

def right():
    IN1.high(); IN2.low()
    IN3.low(); IN4.high()

# ----------------------------
# HTML (Arrow Keys + WASD)
# ----------------------------
html = f"""
<!DOCTYPE html>
<html>
<head>
  <title>ROBOT00 Controller</title>
  <meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no">

  <style>
    body {
      margin:0;
      padding:0;
      height:100vh;
      width:100vw;
      background:#111;
      color:white;
      font-family:Arial, sans-serif;
      overflow:hidden;
      user-select:none;
      touch-action:none;
      display:flex;
      flex-direction:column;
      justify-content:center;
      align-items:center;
    }

    h2 {
      text-align:center;
      margin-bottom:20px;
      font-size:26px;
      color:white;
    }

    .control-grid {
      display:grid;
      grid-template-columns: 120px 120px 120px;
      grid-template-rows: 120px 120px 120px;
      gap:20px;
      justify-items:center;
      align-items:center;
    }

    .btn {
      width:120px;
      height:120px;
      background:rgba(255,255,255,0.15);
      border:3px solid white;
      border-radius:25px;
      font-size:40px;
      color:white;
      display:flex;
      justify-content:center;
      align-items:center;
      touch-action:none;
    }

    .ebtn {
      width:260px;
      height:120px;
      background:red;
      border:3px solid white;
      border-radius:25px;
      font-size:40px;
      color:white;
      display:flex;
      justify-content:center;
      align-items:center;
      touch-action:none;
      margin-top:30px;
    }

    .empty {
      width:120px;
      height:120px;
      background:transparent;
    }
  </style>
</head>

<body>

<h2>ROBOT00 Controls</h2>

<div class="control-grid">

  <div class="empty"></div>
  <div id="forwardBtn" class="btn">UP</div>
  <div class="empty"></div>

  <div id="leftBtn" class="btn">L</div>
  <div class="empty"></div>
  <div id="rightBtn" class="btn">R</div>

  <div class="empty"></div>
  <div id="backBtn" class="btn">DOWN</div>
  <div class="empty"></div>

</div>

<!-- ESTOP button OUTSIDE the grid -->
<div id="stopBtn" class="ebtn">ESTOP</div>

<script>
let activeCmd = null;
let intervalId = null;

function send(cmd) {
  fetch(cmd).catch(()=>{});
}

function start(cmd) {
  if (activeCmd === cmd) return;
  stop();
  activeCmd = cmd;
  send(cmd);
  intervalId = setInterval(() => send(cmd), 150);
}

function stop() {
  if (intervalId) clearInterval(intervalId);
  send('/s');
  activeCmd = null;
}

function bind(id, cmd) {
  let b = document.getElementById(id);

  b.addEventListener("touchstart", e => {
    e.preventDefault();
    start(cmd);
  });
  b.addEventListener("touchend", e => {
    e.preventDefault();
    stop();
  });

  b.addEventListener("mousedown", () => start(cmd));
  b.addEventListener("mouseup", () => stop());
  b.addEventListener("mouseleave", () => stop());
}

bind("forwardBtn", "/f");
bind("backBtn", "/b");
bind("leftBtn", "/l");
bind("rightBtn", "/r");
bind("stopBtn", "/s");

// Keyboard controls
document.addEventListener("keydown", e => {
  if (e.repeat) return;
  if (e.key === "ArrowUp" || e.key === "w") start('/f');
  if (e.key === "ArrowDown" || e.key === "s") start('/b');
  if (e.key === "ArrowLeft" || e.key === "a") start('/l');
  if (e.key === "ArrowRight"|| e.key === "d") start('/r');
});

document.addEventListener("keyup", stop);
</script>

</body>
</html>
"""

# ----------------------------
# Web Server
# ----------------------------
addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]

try:
    s.close()
except:
    pass

s = socket.socket()
s.bind(addr)
s.listen(1)

print("Web server running at http://" + ip)

while True:
    cl, addr = s.accept()
    req = cl.recv(1024).decode()

    if "/f" in req:
        forward()
    elif "/b" in req:
        backward()
    elif "/l" in req:
        left()
    elif "/r" in req:
        right()
    elif "/s" in req:
        stop_motors()

    cl.send("HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n")
    cl.send(html)
    cl.close()


