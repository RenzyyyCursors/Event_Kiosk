import csv
import datetime
import os
import sys
import customtkinter as ctk

# Configuration
CSV_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "event_attendees.csv"
)
ADMIN_PASSWORD = "admin"  

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class AdminExitModal(ctk.CTkToplevel):

  def __init__(self, parent, password_check_callback):
    super().__init__(parent)
    self.parent = parent
    self.password_check_callback = password_check_callback

    self.title("Admin Access")
    self.geometry("360x220")
    self.resizable(False, False)

    # center the modal over screen
    screen_w = self.winfo_screenwidth()
    screen_h = self.winfo_screenheight()
    x = (screen_w // 2) - 180
    y = (screen_h // 2) - 110
    self.geometry(f"360x220+{x}+{y}")

    # UI stuff here
    self.label = ctk.CTkLabel(
        self, text="Enter Admin Password", font=("Helvetica", 16, "bold")
    )
    self.label.pack(pady=(20, 10))

    self.pwd_entry = ctk.CTkEntry(
        self, show="*", width=260, height=40, font=("Helvetica", 14)
    )
    self.pwd_entry.pack(pady=10)
    self.pwd_entry.focus_set()
    self.pwd_entry.bind("<Return>", lambda event: self.verify())

    self.error_label = ctk.CTkLabel(
        self, text="", text_color="#FF5555", font=("Helvetica", 12)
    )
    self.error_label.pack(pady=(0, 5))

    self.confirm_btn = ctk.CTkButton(
        self,
        text="Unlock & Exit",
        width=260,
        height=38,
        font=("Helvetica", 14, "bold"),
        command=self.verify,
    )
    self.confirm_btn.pack(pady=5)

    # layering management fixed
    self.transient(parent)
    self.grab_set()

  def verify(self):
    entered = self.pwd_entry.get()
    if entered == ADMIN_PASSWORD:
      self.grab_release()
      self.destroy()
      self.password_check_callback(True)
    else:
      self.error_label.configure(text="Incorrect Password!")
      self.pwd_entry.delete(0, "end")


class EventKiosk(ctk.CTk):

  def __init__(self):
    super().__init__()

    # Enforce Windows Borderless Screen Takeover
    self.overrideredirect(True)
    screen_width = self.winfo_screenwidth()
    screen_height = self.winfo_screenheight()
    self.geometry(f"{screen_width}x{screen_height}+0+0")
    self.attributes("-topmost", True)

    # disable system close shortcuts : fixed
    self.protocol("WM_DELETE_WINDOW", self.prevent_close)
    self.bind("<Alt-F4>", self.prevent_close)
    self.bind("<Control-q>", self.prevent_close)
    self.bind("<Control-w>", self.prevent_close)
    self.bind("<Escape>", self.open_admin_modal)

    self.init_csv()

    # layout Configs
    self.grid_columnconfigure(0, weight=1)
    self.grid_rowconfigure(0, weight=1)

    # main Center card ui here
    self.card = ctk.CTkFrame(self, corner_radius=16, width=460, height=520)
    self.card.grid(row=0, column=0)
    self.card.grid_propagate(False)
    self.card.grid_columnconfigure(0, weight=1)

    # header
    self.title_label = ctk.CTkLabel(
        self.card, text="Event Check-In", font=("Helvetica", 26, "bold")
    )
    self.title_label.grid(row=0, column=0, pady=(35, 5))

    self.subtitle_label = ctk.CTkLabel(
        self.card,
        text="Please enter your details to proceed",
        font=("Helvetica", 13),
        text_color="gray70",
    )
    self.subtitle_label.grid(row=1, column=0, pady=(0, 25))

    # inputs
    self.name_entry = ctk.CTkEntry(
        self.card,
        placeholder_text="Full Name",
        width=360,
        height=45,
        font=("Helvetica", 14),
    )
    self.name_entry.grid(row=2, column=0, pady=10)

    self.reg_entry = ctk.CTkEntry(
        self.card,
        placeholder_text="Registration Number",
        width=360,
        height=45,
        font=("Helvetica", 14),
    )
    self.reg_entry.grid(row=3, column=0, pady=10)

    # Submit Button
    self.submit_btn = ctk.CTkButton(
        self.card,
        text="Check In",
        width=360,
        height=48,
        font=("Helvetica", 15, "bold"),
        corner_radius=8,
        command=self.process_checkin,
    )
    self.submit_btn.grid(row=4, column=0, pady=(20, 10))

    # Notification Label
    self.status_label = ctk.CTkLabel(
        self.card, text="", font=("Helvetica", 13)
    )
    self.status_label.grid(row=5, column=0, pady=5)

    # Pinned Admin Exit Button (Bottom Right)
    self.exit_btn = ctk.CTkButton(
        self,
        text="Admin Exit",
        width=90,
        height=30,
        fg_color="transparent",
        hover_color="#2B2B2B",
        text_color="gray50",
        command=self.open_admin_modal,
    )
    self.exit_btn.place(relx=0.99, rely=0.98, anchor="se")

  def init_csv(self):
    if not os.path.exists(CSV_FILE):
      with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Serial No", "Full Name", "Reg No", "Timestamp (Date & Time)"]
        )

  def get_next_serial(self):
    if not os.path.exists(CSV_FILE):
      return 1
    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
      reader = csv.reader(f)
      rows = list(reader)
      return len(rows)

  def process_checkin(self):
    name = self.name_entry.get().strip()
    reg_no = self.reg_entry.get().strip()

    if not name or not reg_no:
      self.show_status("Please complete both fields.", color="#FF5555")
      return

    serial_no = self.get_next_serial()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
      writer = csv.writer(f)
      writer.writerow([serial_no, name, reg_no, timestamp])

    self.name_entry.delete(0, "end")
    self.reg_entry.delete(0, "end")
    self.show_status(
        f"Check-in #{serial_no} recorded successfully!", color="#50FA7B"
    )

  def show_status(self, message, color):
    self.status_label.configure(text=message, text_color=color)
    self.after(3500, lambda: self.status_label.configure(text=""))

  def prevent_close(self, event=None):
    return "break"

  def open_admin_modal(self, event=None):
    self.attributes("-topmost", False)
    AdminExitModal(self, self.handle_exit_decision)

  def handle_exit_decision(self, success):
    if success:
      self.destroy()
      sys.exit()
    else:
      self.attributes("-topmost", True)


if __name__ == "__main__":
  app = EventKiosk()
  app.mainloop()