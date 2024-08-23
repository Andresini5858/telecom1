import requests
import customtkinter as ctk
import tkinter as tk
from tkcalendar import DateEntry
from datetime import datetime
newwindow = None
newwindow2 = None
contlabel = None
typelabel = None
timestamplabel = None
current_event = 0

def dibujar_diagrama(initialx1, initialx2, initialy1, initialy2, path, canvas):
    for i in range(len(path)):
        canvas.create_oval(initialx1, initialy1, initialx2, initialy2, outline="white", fill="#d4d4d4", width=0, activefill="#7f82b8")
        center_x = (initialx1 + initialx2) / 2
        center_y = (initialy1 + initialy2) / 2
        canvas.create_text(center_x, center_y, text=path[i], fill="black", font=("Source Code Pro", 12))
        if i < len(path) - 1:
            canvas.create_line(initialx2+2, center_y, initialx2+50, center_y, arrow=tk.LAST, fill="#d4d4d4", width=2)
        initialx1 += 125
        initialx2 += 125
    return

def getData(prefix, asn, date, hour, minute):
    url = f"https://stat.ripe.net/data/bgp-state/data.json?resource={prefix}&timestamp={date}T{hour}:{minute}" #Link
    response = requests.get(url) # Hacer un request a la URL
    data = response.json() # Convertir la respuesta a JSON
    for i in range(len(data["data"]["bgp_state"])): # Recorrer la lista de ASNs
        if data["data"]["bgp_state"][i]["path"][0] == int(asn): # Si el ASN es igual al que se busca
            return data["data"]["bgp_state"][i]["path"] # Retornar el path
        
    print("ASN no encontrado") # Si no se encuentra el ASN
    return # Retornar None

def getData2(prefix, asn, date1, date2, hour1, hour2, minute1, minute2, collector):
    eventos = {'Timestamp': [], 'Tipo': [], 'AS': []} # Crear un diccionario para guardar los eventos
    url = f"https://stat.ripe.net/data/bgplay/data.json?resource={prefix}&starttime={date1}T{hour1}:{minute1}&endtime={date2}T{hour2}:{minute2}" # Link
    response = requests.get(url) #
    data = response.json() # Convertir la respuesta a JSON
    
    for i in range(len(data["data"]["initial_state"])): # Recorrer la lista de estados iniciales
        if data["data"]["initial_state"][i]["path"][0] == int(asn): # Si el ASN es igual al que se busca
            path = data["data"]["initial_state"][i]["path"] # Guardar el path
            eventos['Timestamp'].append("Inicial") # Guardar el timestamp
            eventos['Tipo'].append("I") # Guardar el tipo de evento
            eventos['AS'].append(path) # Guardar el path
            source_id = data["data"]["initial_state"][i]["source_id"] # Guardar el source_id
            break # Salir del ciclo
        
    for i in range(len(data["data"]["events"])): # Recorrer la lista de eventos
        if data["data"]["events"][i]["type"] == "A": # Si el evento es un anuncio
            if data["data"]["events"][i]["attrs"]["path"][0] == int(asn) and data["data"]["events"][i]["attrs"]["source_id"] == source_id: # Si el ASN es igual al que se busca y el source_id es igual al source_id del estado inicial
                eventos['Timestamp'].append(data["data"]["events"][i]["timestamp"]) # Guardar el timestamp
                eventos['Tipo'].append(data["data"]["events"][i]["type"]) # Guardar el tipo de evento
                eventos['AS'].append(data["data"]["events"][i]["attrs"]["path"]) # Guardar el path
        elif data["data"]["events"][i]["type"] == "W": # Si el evento es un retiro
            if data["data"]["events"][i]["attrs"]["source_id"] == source_id: # Si el source_id es igual al source_id del estado inicial
                eventos['Timestamp'].append(data["data"]["events"][i]["timestamp"]) # Guardar el timestamp
                eventos['Tipo'].append(data["data"]["events"][i]["type"]) # Guardar el tipo de evento
                eventos['AS'].append(None) # Guardar porque se retiro el path
                
    return eventos, path # Retornar los eventos y el path
    
def update_next(canvas, window, num_events, eventos, initial_path):
    global current_event, contlabel, typelabel, timestamplabel
    if current_event == num_events:
        return
    if typelabel is not None:
        typelabel.destroy()
    if timestamplabel is not None:
        timestamplabel.destroy()
    contlabel.destroy()
    contlabel = ctk.CTkLabel(window, text=f"No. de evento: {current_event+1:0{len(str(num_events))}}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
    contlabel.place(x=1000, y=400)
    canvas.delete("all")
    if current_event != 0:
        if eventos['Tipo'][current_event+1] == "A":
            if eventos['AS'][current_event] == eventos['AS'][current_event+1]:
                dibujar_diagrama(50, 125, 15, 65, eventos['AS'][current_event+1][::-1], canvas)
                timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event+1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
                timestamplabel.place(x=20, y=300)
                typelabel = ctk.CTkLabel(window, text="Anuncio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
                typelabel.place(x=20, y=250)
            else:
                dibujar_diagrama(50, 125, 15, 65, eventos['AS'][current_event+1][::-1], canvas)
                timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event+1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
                timestamplabel.place(x=20, y=300)
                typelabel = ctk.CTkLabel(window, text="Cambio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
                typelabel.place(x=20, y=250)
        elif eventos['Tipo'][current_event+1] == "W":
            timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event+1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
            timestamplabel.place(x=20, y=300)
            typelabel = ctk.CTkLabel(window, text="Retiro", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
            typelabel.place(x=20, y=250)
    else:
        if eventos['Tipo'][current_event+1] == "A":
            if eventos['AS'][current_event] == eventos['AS'][current_event+1]:
                dibujar_diagrama(50, 125, 15, 65, eventos['AS'][current_event+1][::-1], canvas)
                timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event+1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
                timestamplabel.place(x=20, y=300)
                typelabel = ctk.CTkLabel(window, text="Anuncio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
                typelabel.place(x=20, y=250)
            else:
                dibujar_diagrama(50, 125, 15, 65, eventos['AS'][current_event+1][::-1], canvas)
                timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event+1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
                timestamplabel.place(x=20, y=300)
                typelabel = ctk.CTkLabel(window, text="Cambio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
                typelabel.place(x=20, y=250)
        elif eventos['Tipo'][current_event+1] == "W":
            timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event+1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
            timestamplabel.place(x=20, y=300)
            typelabel = ctk.CTkLabel(window, text="Retiro", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
            typelabel.place(x=20, y=250)
    current_event += 1
    return
    
def update_prev(canvas, window, num_events, eventos, initial_path):
    global current_event, contlabel, typelabel, timestamplabel
    if current_event == 0:
        return
    if typelabel is not None:
        typelabel.destroy()
    if timestamplabel is not None:
        timestamplabel.destroy()
    contlabel.destroy()
    contlabel = ctk.CTkLabel(window, text=f"No. de evento: {current_event-1:0{len(str(num_events))}}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
    contlabel.place(x=1000, y=400)
    canvas.delete("all")
    if current_event != 1:
        if eventos['Tipo'][current_event-1] == "A":
            if eventos['AS'][current_event-2] == eventos['AS'][current_event-1]:
                dibujar_diagrama(50, 125, 15, 65, eventos['AS'][current_event-1][::-1], canvas)
                timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event-1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
                timestamplabel.place(x=20, y=300)
                typelabel = ctk.CTkLabel(window, text="Anuncio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
                typelabel.place(x=20, y=250)
            else:
                dibujar_diagrama(50, 125, 15, 65, eventos['AS'][current_event-1][::-1], canvas)
                timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event-1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
                timestamplabel.place(x=20, y=300)
                typelabel = ctk.CTkLabel(window, text="Cambio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
                typelabel.place(x=20, y=250)
        elif eventos['Tipo'][current_event-1] == "W":
            timestamplabel = ctk.CTkLabel(window, text=f"Timestamp: {eventos['Timestamp'][current_event-1]}", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
            timestamplabel.place(x=20, y=300)
            typelabel = ctk.CTkLabel(window, text="Retiro", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
            typelabel.place(x=20, y=250)
    else:
        contlabel.destroy()
        contlabel = ctk.CTkLabel(newwindow2, text="Inicial", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
        contlabel.place(x=1000, y=400)
        dibujar_diagrama(50, 125, 15, 65, initial_path[::-1], canvas)
    current_event -= 1
    return


def graphs():
    global newwindow
    if newwindow is not None:
        newwindow.destroy()
    datos = []
    prefix = getprefix.get()
    datos.append(prefix)
    asn = getasn.get()
    datos.append(asn)
    date = calendar.get_date()
    datos.append(date)
    hour = hourentry.get()
    datos.append(hour)
    minute = minuteentry.get()
    datos.append(minute)
    path = getData(prefix, asn, date, hour, minute)
    
    newwindow = ctk.CTkToplevel(fg_color="#1b1c1b")
    newwindow.geometry("1200x250")
    newwindow.title("Graficas")
    
    title = ctk.CTkLabel(newwindow, text="AS Path", font=("Source Code Pro", 48, "bold"), justify="center", fg_color="#1b1c1b")
    title.place(x=500, y=0)
    
    canvas = tk.Canvas(newwindow, width=1180, height=90, bg="#1b1c1b", bd=0, highlightthickness=0, relief='ridge')
    canvas.place(x=10, y=70)
    
    initialx1 = 50
    initialx2 = 125
    initialy1 = 15
    initialy2 = 65    
    for i in range(len(path)):
        canvas.create_oval(initialx1, initialy1, initialx2, initialy2, outline="white", fill="#d4d4d4", width=0, activefill="#7f82b8")
        center_x = (initialx1 + initialx2) / 2
        center_y = (initialy1 + initialy2) / 2
        canvas.create_text(center_x, center_y, text=path[len(path)-i-1], fill="black", font=("Source Code Pro", 12))
        if i < len(path) - 1:
            canvas.create_line(initialx2+2, center_y, initialx2+50, center_y, arrow=tk.LAST, fill="#d4d4d4", width=2)
        initialx1 += 125
        initialx2 += 125
        
    iniciolabel = ctk.CTkLabel(newwindow, text="Inicio", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
    iniciolabel.place(x=50, y=160)
    
    finlabel = ctk.CTkLabel(newwindow, text="Destino", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
    finlabel.place(x=initialx1-125, y=160)
    
    newwindow.mainloop()
    
def graphs2():
    global newwindow2, current_event, contlabel
    if newwindow2 is not None:
        newwindow2.destroy()
    datos = []
    current_event = 0
    prefix = getprefix2.get()
    datos.append(prefix)
    asn = getasn2.get()
    datos.append(asn)
    date1 = calendar2.get_date()
    datos.append(date1)
    date2 = calendar3.get_date()
    datos.append(date2)
    hour1 = hourentry2.get()
    datos.append(hour1)
    hour2 = hourentry3.get()
    datos.append(hour2)
    minute1 = minuteentry2.get()
    datos.append(minute1)
    minute2 = minuteentry3.get()
    datos.append(minute2)
    collectorvalor = collector.get()
    datos.append(collectorvalor)
    eventos, path = getData2(prefix, asn, date1, date2, hour1, hour2, minute1, minute2, collectorvalor)
    num_events = len(eventos['Timestamp'])-1
    
    newwindow2 = ctk.CTkToplevel(fg_color="#1b1c1b")
    newwindow2.geometry("1200x500")
    newwindow2.title("BGP Play")
    
    title = ctk.CTkLabel(newwindow2, text="BGP Play", font=("Source Code Pro", 48, "bold"), justify="center", fg_color="#1b1c1b")
    title.place(x=500, y=0)
    
    contlabel = ctk.CTkLabel(newwindow2, text="Inicial", font=("Source Code Pro", 16, "bold"), fg_color="#1b1c1b")
    contlabel.place(x=1000, y=400)
    
    canvas = tk.Canvas(newwindow2, width=1180, height=90, bg="#1b1c1b", bd=0, highlightthickness=0, relief='ridge')
    canvas.place(x=10, y=70)
    
    initialx1 = 50
    initialx2 = 125
    initialy1 = 15
    initialy2 = 65    
    for i in range(len(path)):
        canvas.create_oval(initialx1, initialy1, initialx2, initialy2, outline="white", fill="#d4d4d4", width=0, activefill="#7f82b8")
        center_x = (initialx1 + initialx2) / 2
        center_y = (initialy1 + initialy2) / 2
        canvas.create_text(center_x, center_y, text=path[len(path)-i-1], fill="black", font=("Source Code Pro", 12))
        if i < len(path) - 1:
            canvas.create_line(initialx2+2, center_y, initialx2+50, center_y, arrow=tk.LAST, fill="#d4d4d4", width=2)
        initialx1 += 125
        initialx2 += 125
        
    iniciolabel = ctk.CTkLabel(newwindow2, text="Origen", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
    iniciolabel.place(x=50, y=160)
    
    finlabel = ctk.CTkLabel(newwindow2, text="Destino", font=("Source Code Pro", 24, "bold"), fg_color="#1b1c1b")
    finlabel.place(x=initialx1-125, y=160)
    
    nextbutton = ctk.CTkButton(newwindow2, width=75, text="Next", font=("Source Code Pro", 16, "bold"), command=lambda: update_next(canvas, newwindow2, num_events, eventos, path))
    nextbutton.place(x=1100, y=450)
    
    prevbutton = ctk.CTkButton(newwindow2, width=75, text="Prev", font=("Source Code Pro", 16, "bold"), command=lambda: update_prev(canvas, newwindow2, num_events, eventos, path))
    prevbutton.place(x=1000, y=450)
    
    newwindow2.mainloop()
    
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")
    
root = ctk.CTk()
root.geometry("500x270")
root.title("Seleccionar Fecha y Hora")

tabview = ctk.CTkTabview(root, width=480, height=250)
tabview.place(x=10, y=10)

tabview.add("AS Path")
tabview.add("BGP Play")

mainttitle = ctk.CTkLabel(tabview.tab("AS Path"), text="Fecha", font=("Source Code Pro", 16, "bold"), justify="center")
mainttitle.place(x=240, y=10)

mainttitle2 = ctk.CTkLabel(tabview.tab("BGP Play"), text="Fecha Inicio", font=("Source Code Pro", 16, "bold"), justify="center")
mainttitle2.place(x=240, y=10)

mainttitle3 = ctk.CTkLabel(tabview.tab("BGP Play"), text="Fecha Final", font=("Source Code Pro", 16, "bold"), justify="center")
mainttitle3.place(x=240, y=90)

calendar = DateEntry(tabview.tab("AS Path"), width=16, background='black', foreground='white', borderwidth=2, maxdate=datetime.now(), fontstr=("Source Code Pro", 12, "bold"), date_pattern="yyyy-mm-dd", disabledbackground="black", disabledforeground="black")
calendar.place(x=240, y=40)

calendar2 = DateEntry(tabview.tab("BGP Play"), width=16, background='black', foreground='white', borderwidth=2, maxdate=datetime.now(), fontstr=("Source Code Pro", 12, "bold"), date_pattern="yyyy-mm-dd", disabledbackground="black", disabledforeground="black")
calendar2.place(x=240, y=40)

calendar3 = DateEntry(tabview.tab("BGP Play"), width=16, background='black', foreground='white', borderwidth=2, maxdate=datetime.now(), fontstr=("Source Code Pro", 12, "bold"), date_pattern="yyyy-mm-dd", disabledbackground="black", disabledforeground="black")
calendar3.place(x=240, y=120)

prefixlabel = ctk.CTkLabel(tabview.tab("AS Path"), text="Prefijo", font=("Source Code Pro", 16, "bold"))
prefixlabel.place(x=20, y=10)

getprefix = ctk.CTkEntry(tabview.tab("AS Path"), width=150, height=10, font=("Source Code Pro", 12, "bold"))
getprefix.place(x=20, y=40)

prefixlabel2 = ctk.CTkLabel(tabview.tab("BGP Play"), text="Prefijo", font=("Source Code Pro", 16, "bold"))
prefixlabel2.place(x=20, y=10)

getprefix2 = ctk.CTkEntry(tabview.tab("BGP Play"), width=150, height=10, font=("Source Code Pro", 12, "bold"))
getprefix2.place(x=20, y=40)

asnlabel = ctk.CTkLabel(tabview.tab("AS Path"), text="ASN", font=("Source Code Pro", 16, "bold"))
asnlabel.place(x=20, y=80)

getasn = ctk.CTkEntry(tabview.tab("AS Path"), width=150, height=10, font=("Source Code Pro", 12, "bold"))
getasn.place(x=20, y=110)

asnlabel2 = ctk.CTkLabel(tabview.tab("BGP Play"), text="ASN", font=("Source Code Pro", 16, "bold"))
asnlabel2.place(x=20, y=80)

getasn2 = ctk.CTkEntry(tabview.tab("BGP Play"), width=150, height=10, font=("Source Code Pro", 12, "bold"))
getasn2.place(x=20, y=110)

#collectorlabel = ctk.CTkLabel(tabview.tab("BGP Play"), text="Colector", font=("Source Code Pro", 16, "bold"))
#collectorlabel.place(x=20, y=150)

collector = ctk.CTkEntry(tabview.tab("BGP Play"), width=150, height=10, font=("Source Code Pro", 12, "bold"))
#collector.place(x=20, y=180)

hourlabel = ctk.CTkLabel(tabview.tab("AS Path"), text="Hora", font=("Source Code Pro", 16, "bold"))
hourlabel.place(x=240, y=80)

hourentry = ctk.CTkEntry(tabview.tab("AS Path"), width=50, height=10, font=("Source Code Pro", 12, "bold"))
hourentry.place(x=240, y=110)

hourlabel2 = ctk.CTkLabel(tabview.tab("BGP Play"), text="HH", font=("Source Code Pro", 16, "bold"))
hourlabel2.place(x=210, y=65)

hourentry2 = ctk.CTkEntry(tabview.tab("BGP Play"), width=50, height=10, font=("Source Code Pro", 12, "bold"))
hourentry2.place(x=240, y=70)

hourlabel3 = ctk.CTkLabel(tabview.tab("BGP Play"), text="HH", font=("Source Code Pro", 16, "bold"))
hourlabel3.place(x=210, y=145)

hourentry3 = ctk.CTkEntry(tabview.tab("BGP Play"), width=50, height=10, font=("Source Code Pro", 12, "bold"))
hourentry3.place(x=240, y=150)

minutelabel = ctk.CTkLabel(tabview.tab("AS Path"), text="Minuto", font=("Source Code Pro", 16, "bold"))
minutelabel.place(x=320, y=80)

minutelabel2 = ctk.CTkLabel(tabview.tab("BGP Play"), text="MM", font=("Source Code Pro", 16, "bold"))
minutelabel2.place(x=300, y=65)

minutelabel3 = ctk.CTkLabel(tabview.tab("BGP Play"), text="MM", font=("Source Code Pro", 16, "bold"))
minutelabel3.place(x=300, y=145)

minuteentry = ctk.CTkEntry(tabview.tab("AS Path"), width=50, height=10, font=("Source Code Pro", 12, "bold"))
minuteentry.place(x=320, y=110)

minuteentry2 = ctk.CTkEntry(tabview.tab("BGP Play"), width=50, height=10, font=("Source Code Pro", 12, "bold"))
minuteentry2.place(x=330, y=70)

minuteentry3 = ctk.CTkEntry(tabview.tab("BGP Play"), width=50, height=10, font=("Source Code Pro", 12, "bold"))
minuteentry3.place(x=330, y=150)

okbutton = ctk.CTkButton(tabview.tab("AS Path"), width=75, text="OK", font=("Source Code Pro", 16, "bold"), command=graphs)
okbutton.place(x=390, y=170)

okbutton2 = ctk.CTkButton(tabview.tab("BGP Play"), width=75, text="OK", font=("Source Code Pro", 16, "bold"), command=graphs2)
okbutton2.place(x=390, y=170)
    
root.mainloop()