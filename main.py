from tkinter import *
from tkinter import ttk, messagebox
import tkintermapview
import requests
from bs4 import BeautifulSoup

# --- GLOBALNE ZMIENNE --- #
cities = ["Warszawa", "Kraków", "Gdańsk", "Wrocław", "Poznań"]
current_city = None
data = []
map_widget = None  # globalna mapa

# --- FUNKCJA DO POBIERANIA KOORDYNATÓW Z WIKIPEDII --- #
def get_coordinates(city):
    try:
        url = f"https://pl.wikipedia.org/wiki/{city}"
        response = requests.get(url).text
        soup = BeautifulSoup(response, "html.parser")
        lat = float(soup.select(".latitude")[1].text.replace(",", "."))
        lon = float(soup.select(".longitude")[1].text.replace(",", "."))
        return [lat, lon]
    except Exception as e:
        print(f"Błąd pobierania współrzędnych: {e}")
        return [52.23, 21.01]  # Warszawa domyślnie

# --- GUI GŁÓWNEGO PANELU --- #
def main_gui(entity_type_name):
    global map_widget

    root = Tk()
    root.title(f"{entity_type_name} – {current_city}")
    root.geometry("1024x768")

    selected_index = [None]

    def go_back():
        root.destroy()
        main_menu()

# --- START APLIKACJI (WYBÓR MIASTA) --- #
def start_app():
    global current_city
    if not combo.get():
        messagebox.showwarning("", "Wybierz miasto")
        return
    current_city = combo.get()
    welcome.destroy()
    main_menu()

welcome = Tk()
welcome.title("Wybór miasta")
welcome.geometry("350x200")

Label(welcome, text="Wybierz miasto:", font=("Arial", 14)).pack(pady=20)
combo = ttk.Combobox(welcome, values=cities, state="readonly")
combo.pack()
combo.set(cities[0])

ttk.Button(welcome, text="Dalej", command=start_app).pack(pady=10)
ttk.Button(welcome, text="Zamknij", command=welcome.destroy).pack()

welcome.mainloop()