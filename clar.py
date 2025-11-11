import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import fitz  # PyMuPDF
from difflib import Differ
from PIL import Image, ImageTk

# Zielabmessungen für Vorschaubilder in Pixeln
PREVIEW_WIDTH = 300
PREVIEW_HEIGHT = 400

# Extrahierungsfonktion


def extract_text_from_pdf(file_path):
    try:
        document = fitz.open(file_path)
        text = ""
        for page in document:
            text += page.get_text()
        document.close()
        return text
    except Exception as e:
        messagebox.showerror(
            "Fehler", f"unmöglich die File zu lesen! Error: {e}")
        return None

# Komparierungsfonktion


def compare_texts(text1, text2):
    d = Differ()
    # Splitlines, um Zeile für Zeile Vergleiche anzustellen.
    diff = list(d.compare(text1.splitlines(keepends=True),
                text2.splitlines(keepends=True)))

    # Nur hinzugefügte (+) oder gelöschte (-) Zeilen beibehalten
    formatted_diff = [line for line in diff if line.startswith(
        '- ') or line.startswith('+ ')]

    return "".join(formatted_diff)


def get_pdf_page_image(file_path, page_nummer=0):
    """Konvertiert die angegebene Seite der PDF-Datei in ein Tkinter-Bild mit angepasster Größe.
       page_num ist der Basisindex Null (0 für die erste Seite)."""
    try:
        document = fitz.open(file_path)
        # Überprüfen Sie, ob die Seitenzahl gültig ist
        if page_nummer < 0 or page_nummer >= document.page_count:
            document.close()
            return None

        page = document.load_page(page_nummer)
        zoom_factor = 3.0
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
        # Erstellen Sie ein PIL-Bild aus dem Pixmap
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        document.close()

        # Änderung der Größe des PIL-Bildes auf die feste Größe (PREVIEW_WIDTH x PREVIEW_HEIGHT)
        img = img.resize((PREVIEW_WIDTH, PREVIEW_HEIGHT),
                         Image.Resampling.LANCZOS)

        # Konvertierung das PIL-Bild in ein Tkinter-Bild
        tk_img = ImageTk.PhotoImage(img)

        return tk_img

    except Exception as e:
        print(f"Fehler bei der Konvertierung von PDF in Bild : {e}")
        return None

# --- CLASSE D'APPLICATION TKINTER ---


class PDFComparatorApp:
    def __init__(self, master):
        self.master = master
        master.title("Requirement Analysis with AI")

        # Konfiguration der Hintergrundfarbe des Hauptfensters
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=master['bg'])
        style.configure('TLabel', background=master['bg'])

        self.path1 = tk.StringVar()
        self.path2 = tk.StringVar()
        # Konfiguration der Hintergrundfarbe des Hauptfensters
        self.current_page1 = tk.IntVar(value=0)
        self.current_page2 = tk.IntVar(value=0)
        self.total_page1 = tk.IntVar(value=0)
        self.total_page2 = tk.IntVar(value=0)

        self.tk_img1 = None
        self.tk_img2 = None

        self.setup_ui()

    def setup_ui(self):
        # Konfiguration des globalen Rasters
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_columnconfigure(1, weight=0)
        self.master.grid_rowconfigure(5, weight=1)

        # AUSWAHL PDF-DATEI 1 (Zeile 0)
        frame1 = ttk.Frame(self.master, padding="10")
        frame1.grid(row=0, column=0, columnspan=2, sticky="ew")

        ttk.Label(frame1, text="PDF 1 :").pack(side=tk.LEFT)
        ttk.Entry(frame1, textvariable=self.path1, width=50).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame1, text="Anrufen", command=lambda: self.select_file(
            self.path1)).pack(side=tk.LEFT)

        # AUSWAHL PDF-DATEI 2 (Zeile 1)
        frame2 = ttk.Frame(self.master, padding="10")
        frame2.grid(row=1, column=0, columnspan=2, sticky="ew")

        ttk.Label(frame2, text="PDF 2 :").pack(side=tk.LEFT)
        ttk.Entry(frame2, textvariable=self.path2, width=50).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(frame2, text="Anrufen", command=lambda: self.select_file(
            self.path2)).pack(side=tk.LEFT)

        # ANZEIGERAHMEN (Zeile 2)
        view_frame = ttk.Frame(self.master, padding="10")
        view_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        view_frame.grid_columnconfigure(0, weight=1)
        view_frame.grid_columnconfigure(1, weight=1)

        # PDF 1-Anzeigebereich
        ttk.Label(view_frame, text="PDF-Vorschau 1:").grid(row=0,
                                                           column=0, sticky="s")
        self.pdf_label1 = tk.Label(view_frame,
                                   borderwidth=2, relief="groove",
                                   background="lightgray",
                                   width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT,
                                   text="hochladen PDF 1")
        self.pdf_label1.grid(row=1, column=0, padx=10, pady=5, sticky="n")
        # navigation pdf 1
        nav_frame1 = ttk.Frame(view_frame)
        nav_frame1.grid(row=2, column=0, padx=10, pady=5)

        ttk.Button(nav_frame1, text="< Seite", command=lambda: self.navigate_page(
            1, -1)).pack(side=tk.LEFT, padx=5)
        self.page_info_label1 = ttk.Label(nav_frame1, text="Seite -/-")
        self.page_info_label1.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame1, text="Seite >", command=lambda: self.navigate_page(
            1, 1)).pack(side=tk.LEFT, padx=5)

        # PDF 2-Anzeigebereich
        ttk.Label(view_frame, text="PDF-Vorschau 2:").grid(row=0,
                                                           column=1, sticky="s")
        self.pdf_label2 = tk.Label(view_frame,
                                   borderwidth=2, relief="groove",
                                   background="lightgray",
                                   width=PREVIEW_WIDTH, height=PREVIEW_HEIGHT,
                                   text="hochladen PDF 2")
        self.pdf_label2.grid(row=1, column=1, padx=10, pady=5, sticky="n")
        # navigation pdf 2
        nav_frame2 = ttk.Frame(view_frame)
        nav_frame2.grid(row=2, column=1, padx=10, pady=5)

        ttk.Button(nav_frame2, text="< Seite", command=lambda: self.navigate_page(
            2, -1)).pack(side=tk.LEFT, padx=5)
        self.page_info_label2 = ttk.Label(nav_frame2, text="Seite -/-")
        self.page_info_label2.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame2, text="Seite >", command=lambda: self.navigate_page(
            2, 1)).pack(side=tk.LEFT, padx=5)

        # Vergleichsknopf (row 3)
        ttk.Button(self.master, text="Vergleichung", command=self.run_comparison).grid(
            row=3, column=0, columnspan=2, pady=10)

        # Ergebnisse Rahmen
        ttk.Label(self.master, text="Ergebnisse des Vergleichs (Unterschiede)").grid(
            row=4, column=0, columnspan=2, sticky="w", padx=10)

        # Vorschauen Ergebnisse
        self.result_text = tk.Text(self.master, wrap=tk.WORD, height=15)
        self.result_text.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")

        # Konfiguration der Farbtags für den Ergebnistext
        self.result_text.tag_config('deleted', foreground='red')
        self.result_text.tag_config('added', foreground='green')
        self.result_text.tag_config('info', foreground="#c528d3", font=(
            'TkDefaultFont', 10, 'bold'))  # Info headers

        # Bildlaufleiste (Zeile 5, Spalte 1)
        scrollbar = ttk.Scrollbar(self.master, command=self.result_text.yview)
        scrollbar.grid(row=5, column=1, sticky='ns')
        self.result_text.config(yscrollcommand=scrollbar.set)

        # Überschreiben der Methode „close”, um Ressourcen freizugeben
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def select_file(self, path_var):
        """Öffnet ein Dialogfeld und aktualisiert die PDF-Vorschau."""
        filename = filedialog.askopenfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if filename:
            path_var.set(filename)

            if path_var == self.path1:
                self.current_page1.set(0)
            else:
                self.current_page2.set(0)

            self.update_pdf_preview(path_var)

    def update_pdf_preview(self, path_var):
        """Zeigt die erste Seite der PDF-Datei in der Benutzeroberfläche an."""
        file_path = path_var.get()
        if not file_path:
            return

        # Déterminer les variables d'état (page courante, total, label)
        if path_var == self.path1:
            current_page_var = self.current_page1
            total_pages_var = self.total_page1
            page_info_label = self.page_info_label1
            image_ref_var = 'tk_img1'
            label = self.pdf_label1
        else:
            current_page_var = self.current_page2
            total_pages_var = self.total_page2
            page_info_label = self.page_info_label2
            image_ref_var = 'tk_img2'
            label = self.pdf_label2

        page_nummer = current_page_var.get()

        # 1. Mise à jour du nombre total de pages
        try:
            doc = fitz.open(file_path)
            total_pages_var.set(doc.page_count)
            doc.close()
        except Exception:
            total_pages_var.set(0)

        # 2. Obtenir l'image de la page
        tk_img = get_pdf_page_image(file_path, page_nummer)

        # 3. Affichage
        total_pages = total_pages_var.get()

        if tk_img:
            setattr(self, image_ref_var, tk_img)  # Mémoriser la référence
            label.config(image=tk_img, text="")
            label.image = tk_img

            # Mise à jour de l'étiquette de navigation (Page N/Total)
            page_info_label.config(
                text=f"Seite {page_nummer + 1}/{total_pages}")

        else:
            # En cas d'erreur de chargement ou de page invalide
            label.config(
                image='', text=f"Erreur de chargement ou page {page_nummer+1} invalide. ({PREVIEW_WIDTH}x{PREVIEW_HEIGHT})")
            page_info_label.config(text=f"Seite -/{total_pages}")

       # tk_img = get_pdf_page_image(file_path)

        # if tk_img:
            # Identifizieren Sie, welches Label aktualisiert werden muss (PDF 1 oder PDF 2)
        #    if path_var == self.path1:
        #        label = self.pdf_label1
        #        self.tk_img1 = tk_img # Referenz speichern !
        #    else:
        #        label = self.pdf_label2
        #        self.tk_img2 = tk_img # Referenz speichern !

        #    label.config(image=tk_img, text="")
        #    label.image = tk_img
        # else:
            # Im Falle eines Ladefehlers
        #    if path_var == self.path1:
        #        self.pdf_label1.config(image='', text=f"Fehler beim Laden oder leere PDF-Datei. ({PREVIEW_WIDTH}x{PREVIEW_HEIGHT})")
        #    else:
        #        self.pdf_label2.config(image='', text=f"Fehler beim Laden oder leere PDF-Datei. ({PREVIEW_WIDTH}x{PREVIEW_HEIGHT})")

    def navigate_page(self, pdf_index, direction):
        """Änderung der aktuelle Seite der angegebenen PDF-Datei und aktualisiert die Vorschau"""
        if pdf_index == 1:
            current_page_var = self.current_page1
            total_pages_var = self.total_page1
            path_var = self.path1
        else:
            current_page_var = self.current_page2
            total_pages_var = self.total_page2
            path_var = self.path2

        current_page = current_page_var.get()
        total_pages = total_pages_var.get()

        if total_pages == 0 or not path_var.get():
            return

        new_page = current_page + direction

        # Grenzen überprüfen (Index 0 bis total_pages - 1)
        if 0 <= new_page < total_pages:
            current_page_var.set(new_page)
            self.update_pdf_preview(path_var)

    def run_comparison(self):
        file1 = self.path1.get()
        file2 = self.path2.get()

        if not file1 or not file2:
            messagebox.showwarning(
                "Fehlende Dateien", "Bitte wählen Sie die beiden zu vergleichenden PDF-Dateien aus.")
            return

        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(
            tk.END, "Extrahieren und Vergleichen in Bearbeitung...\n")

        text1 = extract_text_from_pdf(file1)
        text2 = extract_text_from_pdf(file2)

        if text1 is None or text2 is None:
            self.result_text.insert(
                tk.END, "Extrahieren fehlgeschlagen. Siehe Fehlermeldung..")
            return

        diff_output = compare_texts(text1, text2)

        self.result_text.delete(1.0, tk.END)

        if not diff_output.strip():
            self.result_text.insert(
                tk.END, " Die beide Dokumente sind (inhaltlich) identisch.")
        else:
            self.result_text.insert(tk.END, "---Unterschiede Erkannte---\n")
            # self.result_text.insert(tk.END, "Zeilen, die mit ‚-‘ beginnen, sind nur in PDF 1 enthalten.\n")
            # self.result_text.insert(tk.END, " Zeilen, die mit „+“ beginnen, sind nur im PDF 2 enthalten.\n\n")

            # Verarbeitung der Zeilen, um Farben anzuwenden
            for line in diff_output.splitlines(keepends=True):
                if line.startswith('- '):
                    self.result_text.insert(tk.END, line, 'deleted')
                elif line.startswith('+ '):
                    self.result_text.insert(tk.END, line, 'added')
                else:
                    self.result_text.insert(tk.END, line)

    def on_closing(self):
        """Beim Schließen aufgerufene Funktion zum Freigeben von Ressourcen (PyMuPDF)."""
        self.master.destroy()


# --- Ausführung der Anwendung ---
if __name__ == "__main__":
    root = tk.Tk()
    # Hintergrundfarbe des Hauptfensters
    root.configure(bg="#679A99")

    app = PDFComparatorApp(root)
    root.mainloop()


