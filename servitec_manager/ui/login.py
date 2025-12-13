import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import os

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, logic, on_success_callback):
        super().__init__(master)
        self.logic = logic
        self.on_success_callback = on_success_callback
        self.var_user = ctk.StringVar() 
        self.var_user.trace("w", self.force_uppercase)
        self.var_pass = ctk.StringVar()
        
        self.setup_ui()

    def force_uppercase(self, *args):
        val = self.var_user.get()
        if val != val.upper():
            self.var_user.set(val.upper())

    def setup_ui(self):
        self.configure(fg_color="transparent")
        
        frame = ctk.CTkFrame(self, width=400, height=550, corner_radius=15)
        frame.pack(padx=20, pady=20)
        
        # LOGO GRANDE CENTRADO
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "servitec_logo.png")
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path)
                # Crear CTkImage para mejor compatibilidad con HighDPI
                ctk_logo = ctk.CTkImage(light_image=logo_img, dark_image=logo_img, size=(350, 130))
                logo_label = ctk.CTkLabel(frame, image=ctk_logo, text="")
                logo_label.pack(pady=(40, 20))
            except Exception as e:
                print(f"Error al cargar logo: {e}")
                ctk.CTkLabel(frame, text="SERVITEC\nMANAGER PRO", font=("Arial", 28, "bold"), justify="center").pack(pady=(40, 20))
        else:
            # Fallback si no existe el logo
            ctk.CTkLabel(frame, text="SERVITEC\nMANAGER PRO", font=("Arial", 28, "bold"), justify="center").pack(pady=(40, 20))

        # CAMPO USUARIO
        self.entry_user = ctk.CTkEntry(frame, textvariable=self.var_user, placeholder_text="USUARIO", width=220)
        self.entry_user.pack(pady=10)
        self.entry_user.bind("<Return>", lambda event: self.entry_pass.focus())

        # CAMPO CONTRASEÑA
        self.entry_pass = ctk.CTkEntry(frame, textvariable=self.var_pass, placeholder_text="CONTRASEÑA", show="•", width=220)
        self.entry_pass.pack(pady=10)
        self.entry_pass.bind("<Return>", lambda event: self.login_event())

        # BOTÓN INGRESAR
        self.btn_main = ctk.CTkButton(frame, text="INGRESAR", command=self.login_event, width=220)
        self.btn_main.pack(pady=20)
        
        self.lbl_error = ctk.CTkLabel(frame, text="", text_color="red")
        self.lbl_error.pack(pady=5)

        # FOCO INICIAL
        self.after(100, lambda: self.entry_user.focus())

    def login_event(self):
        user = self.var_user.get()
        password = self.var_pass.get()
        
        if not user or not password:
            self.lbl_error.configure(text="USUARIO Y CONTRASEÑA OBLIGATORIOS")
            return
        
        user_data = self.logic.login(user, password)
        if user_data:
            self.on_success_callback(user_data)
        else:
            self.lbl_error.configure(text="CREDENCIALES INVÁLIDAS")
            self.var_pass.set("")
            self.entry_pass.focus()
