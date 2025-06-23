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

# --- KLASA OBIEKTU (np. pracownik/klient/biblioteka) --- #
class Entity:
    def __init__(self, name, surname, city, extra_info, parent_library=""):
        self.name = name
        self.surname = surname
        self.city = city
        self.extra_info = extra_info
        self.parent_library = parent_library
        self.coordinates = get_coordinates(city)
        self.marker = None

# --- GUI GŁÓWNEGO PANELU ZARZĄDZANIA --- #
def main_gui(entity_type_name):
    global map_widget
    selected_index = [None]

    root = Tk()
    root.title(f"{entity_type_name} – {current_city}")
    root.geometry("1024x768")

    def go_back():
        root.destroy()
        main_menu()

    Button(root, text="⟵ ", command=go_back).grid(row=0, column=0, sticky="nw", padx=5, pady=5)

    def add_entity():
        name = entry_name.get()
        surname = entry_surname.get()
        city = entry_city.get()
        extra = entry_extra.get()
        parent_lib = entry_library.get()
        if not name or not city:
            return

        if selected_index[0] is not None:
            # Edycja
            obj = data[selected_index[0]]
            obj.name = name
            obj.surname = surname
            obj.city = city
            obj.extra_info = extra
            obj.parent_library = parent_lib
            obj.coordinates = get_coordinates(city)
            if obj.marker:
                obj.marker.delete()
            obj.marker = map_widget.set_marker(*obj.coordinates, text=name)
            selected_index[0] = None
            btn_add.config(text="Dodaj")
        else:
            # Nowy obiekt
            obj = Entity(name, surname, city, extra, parent_lib)
            obj.marker = map_widget.set_marker(*obj.coordinates, text=name)
            data.append(obj)
        show_list()
        clear_form()

    def edit_entity():
        idxs = listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        obj = data[idx]
        entry_name.delete(0, END)
        entry_name.insert(0, obj.name)
        entry_surname.delete(0, END)
        entry_surname.insert(0, obj.surname)
        entry_city.delete(0, END)
        entry_city.insert(0, obj.city)
        entry_extra.delete(0, END)
        entry_extra.insert(0, obj.extra_info)
        entry_library.delete(0, END)
        entry_library.insert(0, obj.parent_library)
        selected_index[0] = idx
        btn_add.config(text="Zapisz zmiany")

    def show_list():
        listbox.delete(0, END)
        for idx, obj in enumerate(data):
            if entity_type_name == "Biblioteki" and obj.parent_library is None:
                listbox.insert(idx, f"{obj.name} ({obj.city}) – {obj.surname} książek")
            else:
                listbox.insert(idx, f"{obj.name} {obj.surname} ({obj.city}) [{obj.parent_library}]")

    def clear_form():
        entry_name.delete(0, END)
        entry_surname.delete(0, END)
        entry_city.delete(0, END)
        entry_extra.delete(0, END)
        entry_library.delete(0, END)
        selected_index[0] = None
        btn_add.config(text="Dodaj")

    def show_details():
        idx = listbox.curselection()
        if not idx: return
        obj = data[idx[0]]
        label_val_name.config(text=obj.name)
        label_val_surname.config(text=obj.surname)
        label_val_city.config(text=obj.city)
        label_val_extra.config(text=obj.extra_info)
        label_val_library.config(text=obj.parent_library)
        map_widget.set_position(*obj.coordinates)
        map_widget.set_zoom(12)

    def delete_entity():
        idx = listbox.curselection()
        if not idx: return
        obj = data.pop(idx[0])
        if obj.marker: obj.marker.delete()
        show_list()
        clear_form()

    def show_library_map():
        target_library = entry_library.get().strip()
        if not target_library:
            messagebox.showwarning("Brak danych", "Wpisz nazwę biblioteki!")
            return



            # nowe okno
            map_window = Toplevel(root)
            map_window.title(f"Mapa - {entity_type_name} w '{target_library}'")
            map_window.geometry("1000x600")

            map_view = tkintermapview.TkinterMapView(map_window, width=1000, height=600)
            map_view.pack(fill=BOTH, expand=True)

            map_view.set_position(*get_coordinates(current_city))
            map_view.set_zoom(7)

            found = False
            for obj in data:
                if obj.parent_library == target_library:
                    map_view.set_marker(*obj.coordinates, text=f"{obj.name} {obj.surname}")
                    found = True

            if not found:
                messagebox.showinfo("Brak wyników", f"Brak {entity_type_name.lower()} w tej bibliotece!")

    # Layout

    ramka_lista = Frame(root)
    ramka_formularz = Frame(root)
    ramka_szczegoly = Frame(root)
    ramka_mapa = Frame(root)

    ramka_lista.grid(row=0, column=0, sticky="n")
    ramka_formularz.grid(row=0, column=1, sticky="ne", padx=10)
    ramka_szczegoly.grid(row=1, column=0, columnspan=2, sticky="w", padx=10, pady=5)
    ramka_mapa.grid(row=2, column=0, columnspan=2)

    Label(ramka_lista, text="Lista obiektów:").grid(row=0, column=0, columnspan=3)
    listbox = Listbox(ramka_lista, height=10, width=40)
    listbox.grid(row=1, column=0, columnspan=3)
    Button(ramka_lista, text="Pokaż szczegóły", command=show_details).grid(row=2, column=0)
    Button(ramka_lista, text="Edytuj obiekt", command=edit_entity).grid(row=2, column=1)
    Button(ramka_lista, text="Usuń obiekt", command=delete_entity).grid(row=2, column=2)

    if entity_type_name != "Biblioteki":
        Button(ramka_formularz, text="Pokaż mapę tej biblioteki", command=show_library_map).grid(row=7, column=0,
                                                                                                 columnspan=2, pady=5)
    Label(ramka_formularz, text="Formularz:").grid(row=0, column=0, columnspan=2)
    label_name = "Nazwa biblioteki:" if entity_type_name == "Biblioteki" else "Imię:"
    label_surname = "Liczba książek:" if entity_type_name == "Biblioteki" else "Nazwisko:"

    Label(ramka_formularz, text=label_name).grid(row=1, column=0, sticky=W)
    entry_name = Entry(ramka_formularz)
    entry_name.grid(row=1, column=1)

    Label(ramka_formularz, text=label_surname).grid(row=2, column=0, sticky=W)
    entry_surname = Entry(ramka_formularz)
    entry_surname.grid(row=2, column=1)
    Label(ramka_szczegoly, text="Nazwa:").grid(row=1, column=0)
    label_val_name = Label(ramka_szczegoly, text="....")
    Label(ramka_szczegoly, text=label_name).grid(row=1, column=1)
    Label(ramka_szczegoly, text="Info:").grid(row=1, column=2)
    label_val_surname = Label(ramka_szczegoly, text="....")
    label_val_surname.grid(row=1, column=3)
    #entry_name = Entry(ramka_formularz)
    #entry_name.grid(row=1, column=1)
    #Label(ramka_formularz, text="Nazwisko:").grid(row=2, column=0, sticky=W)
    #entry_surname = Entry(ramka_formularz)
    #entry_surname.grid(row=2, column=1)
    Label(ramka_formularz, text="Miasto:").grid(row=3, column=0, sticky=W)
    entry_city = Entry(ramka_formularz)
    entry_city.grid(row=3, column=1)
    entry_city.insert(0, current_city)
    Label(ramka_formularz, text="Dodatkowe info:").grid(row=4, column=0, sticky=W)
    entry_extra = Entry(ramka_formularz)
    entry_extra.grid(row=4, column=1)
    if entity_type_name != "Biblioteki":
        Label(ramka_formularz, text="Biblioteka:").grid(row=5, column=0, sticky=W)
        entry_library = Entry(ramka_formularz)
        entry_library.grid(row=5, column=1)
    else:
        entry_library = Entry(ramka_formularz)
        entry_library.grid_forget()
    btn_add = Button(ramka_formularz, text="Dodaj", command=add_entity)
    btn_add.grid(row=6, column=0, columnspan=2)

    Label(ramka_szczegoly, text="Szczegóły użytkownika:").grid(row=0, column=0, sticky=W)
    label_det_name = "Nazwa biblioteki:" if entity_type_name == "Biblioteki" else "Imię:"
    label_det_surname = "Liczba książek:" if entity_type_name == "Biblioteki" else "Nazwisko:"

    Label(ramka_szczegoly, text=label_det_name).grid(row=1, column=0)
    Label(ramka_szczegoly, text=label_det_surname).grid(row=1, column=2)
    #Label(ramka_szczegoly, text="Imię:").grid(row=1, column=0)
    #label_val_name = Label(ramka_szczegoly, text="....")
    #label_val_name.grid(row=1, column=1)
    #Label(ramka_szczegoly, text="Nazwisko:").grid(row=1, column=2)
    #label_val_surname = Label(ramka_szczegoly, text="....")
    #label_val_surname.grid(row=1, column=3)
    Label(ramka_szczegoly, text="Miasto:").grid(row=1, column=4)
    label_val_city = Label(ramka_szczegoly, text="....")
    label_val_city.grid(row=1, column=5)
    Label(ramka_szczegoly, text="Dodatkowe info:").grid(row=1, column=6)
    label_val_extra = Label(ramka_szczegoly, text="....")
    label_val_extra.grid(row=1, column=7)
    Label(ramka_szczegoly, text="Biblioteka:").grid(row=1, column=8)
    label_val_library = Label(ramka_szczegoly, text="....")
    label_val_library.grid(row=1, column=9)

    map_widget = tkintermapview.TkinterMapView(ramka_mapa, width=1000, height=400)
    map_widget.set_position(*get_coordinates(current_city))
    map_widget.set_zoom(6)
    map_widget.grid(row=0, column=0)

    root.mainloop()


# --- MENU WYBORU FUNKCJI --- #
def main_menu():
    root = Tk()
    root.title(f"Wybierz tryb – {current_city}")
    root.geometry("300x200")
    Label(root, text="Wybierz, czym chcesz zarządzać:").pack(pady=20)
    Button(root, text="Biblioteki", command=lambda: [root.destroy(), main_gui("Biblioteki")]).pack(fill=X, padx=40, pady=5)
    Button(root, text="Pracownicy", command=lambda: [root.destroy(), main_gui("Pracownicy")]).pack(fill=X, padx=40, pady=5)
    Button(root, text="Klienci", command=lambda: [root.destroy(), main_gui("Klienci")]).pack(fill=X, padx=40, pady=5)
    root.mainloop()




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