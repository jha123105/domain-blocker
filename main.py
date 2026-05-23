#!/usr/bin/env python3
import customtkinter as ctk
from core.bettercap_controller import BettercapController
from core.domain_manager import DomainManager
from utils.logger import log_info, log_error
import threading
from tkinter import messagebox
import os

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class DomainBlockerApp:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Domain Blocker (Bettercap)")
        self.window.geometry("900x700")
        self.window.minsize(800, 600)
        
        self.bettercap = BettercapController()
        self.domain_manager = DomainManager()
        self.blocked_domains = []
        self.is_running = False
        
        self.setup_ui()
        self.load_blocked_domains()
        
    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Top bar with title and about button
        top_bar_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        top_bar_frame.pack(fill="x", pady=(10,0))
        self.header = ctk.CTkLabel(top_bar_frame, text="Domain Blocker (Bettercap)", font=ctk.CTkFont(size=24, weight="bold"))
        self.header.pack(side="left", padx=10)
        self.about_btn = ctk.CTkButton(top_bar_frame, text="ℹ️ About", width=60, height=25, command=self.show_about)
        self.about_btn.pack(side="right", padx=10)
        
        self.subheader = ctk.CTkLabel(self.main_frame, text="Educational Purpose Only", font=ctk.CTkFont(size=12, slant="italic"))
        self.subheader.pack(pady=(0, 15))
        
        control_frame = ctk.CTkFrame(self.main_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.interface_label = ctk.CTkLabel(control_frame, text="Interface:")
        self.interface_label.pack(side="left", padx=5)
        self.interface_entry = ctk.CTkEntry(control_frame, width=150)
        self.interface_entry.pack(side="left", padx=5)
        self.interface_entry.insert(0, "eth0")
        
        self.gateway_label = ctk.CTkLabel(control_frame, text="Gateway IP:")
        self.gateway_label.pack(side="left", padx=5)
        self.gateway_entry = ctk.CTkEntry(control_frame, width=150)
        self.gateway_entry.pack(side="left", padx=5)
        self.gateway_entry.insert(0, "192.168.1.1")
        
        self.start_stop_btn = ctk.CTkButton(control_frame, text="Start Blocker", command=self.toggle_blocker, fg_color="green", width=120)
        self.start_stop_btn.pack(side="right", padx=10)
        
        domain_frame = ctk.CTkFrame(self.main_frame)
        domain_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(domain_frame, text="Blocked Domains", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=(10, 5))
        
        add_frame = ctk.CTkFrame(domain_frame)
        add_frame.pack(fill="x", padx=5, pady=5)
        self.domain_entry = ctk.CTkEntry(add_frame, placeholder_text="example.com", width=250)
        self.domain_entry.pack(side="left", padx=5)
        self.add_btn = ctk.CTkButton(add_frame, text="Add Domain", command=self.add_domain, width=100)
        self.add_btn.pack(side="left", padx=5)
        
        self.domain_listbox = ctk.CTkTextbox(domain_frame, height=150, font=ctk.CTkFont(size=12))
        self.domain_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.remove_btn = ctk.CTkButton(domain_frame, text="Remove Selected", command=self.remove_domain, fg_color="red", width=120)
        self.remove_btn.pack(pady=5)
        
        log_frame = ctk.CTkFrame(self.main_frame)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(log_frame, text="Log Output", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=5, pady=(10, 5))
        self.log_text = ctk.CTkTextbox(log_frame, height=200, font=ctk.CTkFont(size=11))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.status_label = ctk.CTkLabel(self.main_frame, text="Status: Stopped", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=5)
        
        # Footer credit
        self.credit_label = ctk.CTkLabel(self.main_frame, text="Developed by Yushie_Alya1", font=ctk.CTkFont(size=10, slant="italic"), text_color="gray")
        self.credit_label.pack(pady=(5, 0))
        
    def show_about(self):
        about_text = """Domain Blocker (Bettercap)
    
A modern GUI tool to block domains on your local network using Bettercap's ARP spoofing and HTTP/HTTPS proxy.

Developed by Yushie_Alya1
Version 1.0
License: MIT

⚠️ Educational Purpose Only
Use only on networks you own or have permission to test."""
        messagebox.showinfo("About Domain Blocker", about_text)
        
    def log(self, message):
        self.log_text.insert("end", f"{message}\n")
        self.log_text.see("end")
        self.window.update()
        
    def load_blocked_domains(self):
        self.blocked_domains = self.domain_manager.load_domains()
        self.update_domain_list()
        
    def update_domain_list(self):
        self.domain_listbox.delete("1.0", "end")
        for domain in self.blocked_domains:
            self.domain_listbox.insert("end", f"{domain}\n")
            
    def add_domain(self):
        domain = self.domain_entry.get().strip().lower()
        if not domain:
            messagebox.showwarning("No Domain", "Please enter a domain name.")
            return
        if domain in self.blocked_domains:
            messagebox.showinfo("Already Blocked", f"{domain} is already in the blocklist.")
            return
        self.blocked_domains.append(domain)
        self.domain_manager.save_domains(self.blocked_domains)
        self.update_domain_list()
        self.domain_entry.delete(0, "end")
        self.log(f"Added domain: {domain}")
        if self.is_running:
            self.bettercap.update_blocklist(self.blocked_domains)
            
    def remove_domain(self):
        try:
            index = int(self.domain_listbox.index("insert").split('.')[0]) - 1
            if 0 <= index < len(self.blocked_domains):
                domain = self.blocked_domains.pop(index)
                self.domain_manager.save_domains(self.blocked_domains)
                self.update_domain_list()
                self.log(f"Removed domain: {domain}")
                if self.is_running:
                    self.bettercap.update_blocklist(self.blocked_domains)
        except:
            messagebox.showwarning("No Selection", "Please select a domain to remove.")
            
    def toggle_blocker(self):
        if not self.is_running:
            interface = self.interface_entry.get().strip()
            gateway = self.gateway_entry.get().strip()
            if not interface or not gateway:
                messagebox.showerror("Missing Info", "Please fill in interface and gateway IP.")
                return
            self.start_blocker(interface, gateway)
        else:
            self.stop_blocker()
            
    def start_blocker(self, interface, gateway):
        self.start_stop_btn.configure(state="disabled", text="Starting...")
        self.status_label.configure(text="Status: Starting...")
        self.log("Starting Bettercap domain blocker...")
        
        def start_thread():
            success, message = self.bettercap.start(interface, gateway, self.blocked_domains, self.log)
            self.window.after(0, lambda: self.on_start_complete(success, message))
        
        threading.Thread(target=start_thread, daemon=True).start()
        
    def on_start_complete(self, success, message):
        self.start_stop_btn.configure(state="normal")
        if success:
            self.is_running = True
            self.start_stop_btn.configure(text="Stop Blocker", fg_color="red")
            self.status_label.configure(text="Status: Running")
            self.log(message)
        else:
            self.status_label.configure(text="Status: Failed")
            messagebox.showerror("Start Failed", message)
            
    def stop_blocker(self):
        self.start_stop_btn.configure(state="disabled", text="Stopping...")
        self.status_label.configure(text="Status: Stopping...")
        self.log("Stopping Bettercap...")
        
        def stop_thread():
            success, message = self.bettercap.stop()
            self.window.after(0, lambda: self.on_stop_complete(success, message))
            
        threading.Thread(target=stop_thread, daemon=True).start()
        
    def on_stop_complete(self, success, message):
        self.start_stop_btn.configure(state="normal")
        if success:
            self.is_running = False
            self.start_stop_btn.configure(text="Start Blocker", fg_color="green")
            self.status_label.configure(text="Status: Stopped")
            self.log(message)
        else:
            self.status_label.configure(text="Status: Stop Failed")
            messagebox.showerror("Stop Failed", message)
            
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = DomainBlockerApp()
    app.run()