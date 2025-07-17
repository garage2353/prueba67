import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

class InterfazVentana(ttk.Window):
    def __init__(self):
        super().__init__(themename="flatly", title="Lecciones", size=(1200, 900))
        self.state('zoomed')

        # Estilo personalizado
        self.style.configure(
            "Mi.TButton",
            font=("Helvetica", 12),
            foreground="white",
            background="#7a5331",
            borderwidth=1
        )
        self.style.map(
            "Mi.TButton",
            background=[("!disabled", "#7a5331"), ("pressed", "#3e2b17"), ("active", "#5c3e25")],
            foreground=[("disabled", "#ccc"), ("pressed", "white"), ("active", "white")]
        )

        # Fondo
        try:
            self.fondo_original = Image.open("fondo2.png")
            self.bg_img = ImageTk.PhotoImage(
                self.fondo_original.resize((self.winfo_width(), self.winfo_height()), Image.LANCZOS)
            )
            self.bg_label = ttk.Label(self, image=self.bg_img)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.bind("<Configure>", self.redimensionar_fondo)
        except Exception as e:
            print("No se pudo cargar fondo:", e)

    def redimensionar_fondo(self, event):
        if event.width < 10 or event.height < 10:
            return
        img = self.fondo_original.resize((event.width, event.height), Image.LANCZOS)
        self.bg_img = ImageTk.PhotoImage(img)
        self.bg_label.configure(image=self.bg_img)
        self.bg_label.image = self.bg_img
