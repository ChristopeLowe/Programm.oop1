import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import fitz # PyMuPDF
from difflib import Differ
from PIL import Image, ImageTk 


PREVIEW_WIDTH = 300
PREVIEW_HEIGHT =400

#Extrahierungsfonktion
def extract_text_from_pdf(file_path):
    try:
        document = fitz.open(file_path)
        text = ""
        for page in document:
            text += page.get_text()
        document.close()
        return text
    except Exception as e:
        messagebox.showerror("Fehler", f"unmöglich die File zu lesen! Erreur: {e}")
        return None
    
#Komparierungsfonktion

def compare_texts(text1, text2):
    d = Differ()
    diff = list(d.compare(text1.splitlines(keepends=True), text2.splitlines(keepends=True)))

    formatted_diff = [line for line in diff if line.startswith('- ') or line.startswith('+ ')]

    return "".join(formatted_diff)

def get_pdf_page_image(file_path):
    """Convertit la première page du PDF en une image Tkinter."""
    try:
        document = fitz.open(file_path)
        page = document.load_page(0) # On charge la première page (index 0)
        
        # Convertir la page en Pixmap (représentation des pixels)
        zoom_factor = 3.0
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor)) # Zoom 1.5 pour une meilleure qualité
        
        # Créer une image PIL à partir du Pixmap
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        document.close()

        img = img.resize((PREVIEW_WIDTH, PREVIEW_HEIGHT), Image.Resampling.LANCZOS)
        
        # Convertir l'image PIL en image Tkinter (nécessaire pour l'affichage)
        tk_img = ImageTk.PhotoImage(img)
        
        return tk_img # Retourne l'objet image Tkinter
        
    except Exception as e:
        print(f"Erreur lors de la conversion PDF en image : {e}")
        messagebox.showerror("Fehler", f"Erreur:{e}")
        return None

# --- CLASSE D'APPLICATION TKINTER (MODIFIÉE) ---

class PDFComparatorApp:
    def __init__(self, master):
        # ... (initialisation des variables inchangée) ...
        self.master = master
        master.title("Requirement with AI")
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('TFrame', background=master['bg'])
        style.configure('TLabel', background=master['bg'])
        self.path1 = tk.StringVar()
        self.path2 = tk.StringVar()
        self.tk_img1 = None # image PDF 1 
        self.tk_img2 = None # image PDF 2
       
        
        self.setup_ui()

    def setup_ui(self):
        #Configuration de la grille globale
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0)
        self.master.grid_columnconfigure(2, weight=1)
        self.master.grid_columnconfigure(3, weight=1)
        self.master.grid_rowconfigure(5, weight=1)
        # ... (les frames et boutons de sélection de fichiers restent les mêmes) ...
        frame1 = ttk.Frame(self.master, padding="10")
        frame1.grid(row=0, column=0, columnspan=2, sticky="ew")


        ttk.Label(frame1, text="PDF 1 :").pack(side=tk.LEFT)
        ttk.Entry(frame1, textvariable=self.path1, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame1, text="Anrufen", command=lambda: self.select_file(self.path1)).pack(side=tk.LEFT)


        frame2 = ttk.Frame(self.master, padding="10")
        frame2.grid(row=1, column=0, columnspan=2, sticky="ew")


        ttk.Label(frame2, text="PDF 2 :").pack(side=tk.LEFT)
        ttk.Entry(frame2, textvariable=self.path2, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame2, text="Anrufen", command=lambda: self.select_file(self.path2)).pack(side=tk.LEFT)

        
        # 3.0. Cadre principal pour les visualisations (Affichage côte à côte)
        view_frame = ttk.Frame(self.master, padding="10")
        view_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        view_frame.grid_columnconfigure(0, weight=1)
        view_frame.grid_columnconfigure(1, weight=1)

        # 3.1. Zone d'affichage PDF 1
        ttk.Label(view_frame, text="Aperçu PDF 1:").grid(row=0,column=0, sticky="s")
        self.pdf_label1 = tk.Label(view_frame, borderwidth=2, relief="groove",
                                    background="lightgray", width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT,
                                    text="hinführen PDF 1")
        self.pdf_label1.grid(row=1, column=0, padx=10, pady=5, sticky="n")
        
        # 3.2. Zone d'affichage PDF 2
        ttk.Label(view_frame, text="Aperçu PDF 2:").grid(row=0, column=1, sticky="s")
        self.pdf_label2 = tk.Label(view_frame, borderwidth=2, relief="groove", 
                                   background="lightgray", width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT,
                                   text=" hinführen PDF 2")
        self.pdf_label2.grid(row=1, column=1, padx=10, pady=5, sticky="n")
        
        # 3.3. Bouton de comparaison et Zone de résultat (décalés)
        ttk.Button(self.master, text="Vergleichung", command=self.run_comparison).grid(row=2, column=0, columnspan=2, sticky="w",padx=10, pady=10) # row=3 
        ttk.Label(self.master, text="Résultats de la Comparaison (Différences)").grid(row=4, column=0, columnspan=2, sticky="w", padx=10) # row=4
        #self.result_text = tk.Text(self.master, wrap=tk.WORD, height=10, width=80)
        #self.result_text.grid(row=5, column=0, padx=10, pady=5) # row=5
        
        self.result_text = tk.Text(self.master, wrap=tk.WORD, height=15)#, width=80
        self.result_text.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(self.master, command=self.result_text.yview)
        scrollbar.grid(row=5, column=1, sticky='ns')
        self.result_text.config(yscrollcommand=scrollbar.set)

        self.master.protocol("WM_DELECTE_WINSDOW", self.on_closing)

    def select_file(self, path_var):
        """Ouvre une boîte de dialogue et met à jour l'aperçu PDF."""
        filename = filedialog.askopenfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            path_var.set(filename)
            self.update_pdf_preview(path_var)

    def update_pdf_preview(self, path_var):
        """Affiche la première page du PDF dans l'interface."""
        file_path = path_var.get()
        if not file_path:
            return

        tk_img = get_pdf_page_image(file_path)
        
        if tk_img:
            # Identifier quel label mettre à jour (PDF 1 ou PDF 2)
            if path_var == self.path1:
                label = self.pdf_label1
                self.tk_img1 = tk_img # Mémoriser la référence !
            else:
                label = self.pdf_label2
                self.tk_img2 = tk_img # Mémoriser la référence !

            # Afficher l'image dans le Label
            label.config(image=tk_img, text="", compound="image")
            label.image = tk_img # Important : empêche la garbage collection
            #label.config(text="")
        else:
            # En cas d'erreur
            if path_var == self.path1:
                self.pdf_label1.config(image='', text=f"Aperçu indisponible. ({PREVIEW_WIDTH}*{PREVIEW_HEIGHT})")
            else:
                self.pdf_label2.config(image='', text=f"Aperçu indisponible. ({PREVIEW_WIDTH}*{PREVIEW_HEIGHT})")

    def run_comparison(self):
        file1 = self.path1.get()
        file2 = self.path2.get()

        if not file1 or not file2:
            messagebox.showwarning("Fehlende Dateien", "Bitte wählen Sie die beiden zu vergleichenden PDF-Dateien aus.")
            return
        
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "Extraction et Comparaison en cours...\n")

        text1 = extract_text_from_pdf(file1)
        text2 = extract_text_from_pdf(file2)

        if text1 is None or text2 is None:
            self.result_text.insert(tk.END, "Echec de extraction. Voir le message erreur.")
            return
        
        diff_output = compare_texts(text1, text2)

        self.result_text.delete(1.0, tk.END)

        if not diff_output.strip():
            self.result_text.insert(tk.END, " Les documents sont identique (au niveau textuel).")
        else:
            #self.result_text.insert(tk.END, "---Differences Detectees---\n")
            self.result_text.insert(tk.END, "Lignes commencant par '-' sont dans le PDF 1 seulement.\n")
            self.result_text.insert(tk.END, " Lignes commencant par '+' sont dans le PDF 2 seulemnt.\n\n")
            self.result_text.insert(tk.END, diff_output)

    def on_closing(self):
        self.master.destory()

# --- Exécution de l'Application ---

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg="#860DAC")
    #root.title("Page avec Arrière-Plan Personnalisé")
    app = PDFComparatorApp(root)
    root.mainloop()