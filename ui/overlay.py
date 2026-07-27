import customtkinter as ctk

class UIManager:
    def __init__(self, root, cancel_callback):
        self.root = root
        self.cancel_callback = cancel_callback
        self.overlay = None

    def show_overlay(self, mode):
        # Safely tells the main thread to build the UI
        self.root.after(0, self._build_overlay, mode)

    def _build_overlay(self, mode):
        if self.overlay and self.overlay.winfo_exists(): 
            self.overlay.destroy()
            
        self.overlay = ctk.CTkToplevel(self.root)
        self.overlay.overrideredirect(True)
        self.overlay.attributes("-topmost", True)
        self.overlay.geometry("200x80+20+20")
        
        icon = "🎙️ Listening..." if mode == "Mic" else "🔊 Reading..."
        lbl = ctk.CTkLabel(self.overlay, text=icon, font=("Arial", 16, "bold"))
        lbl.pack(pady=(10, 5))
        
        btn = ctk.CTkButton(self.overlay, text="Cancel (Esc)", width=100, height=25, command=self.cancel_callback)
        btn.pack()
        
        self.overlay.bind("<Escape>", lambda e: self.cancel_callback())

    def hide_overlay(self):
        def _hide():
            if self.overlay and self.overlay.winfo_exists():
                self.overlay.destroy()
                self.overlay = None
        self.root.after(0, _hide)