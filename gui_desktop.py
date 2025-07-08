import tkinter as tk
from tkinter import messagebox
import cv2
from pyzbar import pyzbar
import threading
from db import conectar
import os, sys

# --- FUNCIONES ---

def escanear_codigo():
    def run_lector():
        cap = cv2.VideoCapture(0)
        cv2.namedWindow("📷 Escaneando... pulsa 'q' para salir")
        codigo_encontrado = None

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            barcodes = pyzbar.decode(frame)
            for barcode in barcodes:
                codigo = barcode.data.decode("utf-8")
                codigo_encontrado = codigo
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f"Detectado: {codigo}", (x, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            cv2.imshow("📷 Escaneando... pulsa 'q' para salir", frame)

            if cv2.waitKey(1) & 0xFF == ord('q') or codigo_encontrado:
                break

        cap.release()
        cv2.destroyAllWindows()

        if codigo_encontrado:
            codigo_entry.delete(0, tk.END)
            codigo_entry.insert(0, codigo_encontrado)
            codigo_asig_entry.delete(0, tk.END)
            codigo_asig_entry.insert(0, codigo_encontrado)

    threading.Thread(target=run_lector).start()

def registrar_producto():
    codigo = codigo_entry.get()
    descripcion = descripcion_entry.get()
    modelo = modelo_entry.get()
    serial = serial_entry.get()

    if not codigo or not descripcion:
        messagebox.showwarning("Campos vacíos", "Por favor completa código y descripción.")
        return

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO activos (codigo, descripcion, modelo, serial)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (codigo) DO UPDATE SET
                descripcion = EXCLUDED.descripcion,
                modelo = EXCLUDED.modelo,
                serial = EXCLUDED.serial
        """, (codigo, descripcion, modelo, serial))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("✅ Registrado", "Producto guardado exitosamente.")
        descripcion_entry.delete(0, tk.END)
        modelo_entry.delete(0, tk.END)
        serial_entry.delete(0, tk.END)
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo registrar:\n{e}")

def asignar_producto():
    codigo = codigo_asig_entry.get()
    usuario = usuario_entry.get()
    equipo = equipo_entry.get()
    observaciones = observaciones_entry.get("1.0", tk.END).strip()
    modelo = modelo_entry.get()
    serial = serial_entry.get()

    if not codigo or not usuario or not equipo:
        messagebox.showwarning("Campos incompletos", "Código, usuario y equipo son obligatorios.")
        return

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            UPDATE activos
            SET asignado = TRUE,
                usuario = %s,
                equipo = %s,
                observaciones = %s,
                modelo = COALESCE(%s, modelo),
                serial = COALESCE(%s, serial)
            WHERE codigo = %s
        """, (usuario, equipo, observaciones, modelo, serial, codigo))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("✅ Asignado", "Activo asignado correctamente.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"No se pudo asignar:\n{e}")

def buscar_activos():
    criterio = criterio_busqueda.get().strip()
    if not criterio:
        messagebox.showwarning("Campo vacío", "Por favor ingresa nombre de usuario o código de equipo.")
        return

    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("""
            SELECT codigo, descripcion, modelo, serial, usuario, equipo, observaciones
            FROM activos
            WHERE usuario ILIKE %s OR equipo ILIKE %s
        """, (f"%{criterio}%", f"%{criterio}%"))
        resultados = cur.fetchall()
        cur.close()
        conn.close()

        if resultados:
            texto = "\n\n".join([
                f"Código: {r[0]}\nDescripción: {r[1]}\nModelo: {r[2]}\nSerial: {r[3]}\nUsuario: {r[4]}\nEquipo: {r[5]}\nObservaciones: {r[6]}"
                for r in resultados
            ])
            messagebox.showinfo("🔍 Resultados encontrados", texto)
        else:
            messagebox.showinfo("🔍 Sin resultados", "No se encontraron activos con ese criterio.")
    except Exception as e:
        messagebox.showerror("❌ Error", f"Error al buscar:\n{e}")

def limpiar_todo():
    codigo_entry.delete(0, tk.END)
    descripcion_entry.delete(0, tk.END)
    modelo_entry.delete(0, tk.END)
    serial_entry.delete(0, tk.END)
    codigo_asig_entry.delete(0, tk.END)
    usuario_entry.delete(0, tk.END)
    equipo_entry.delete(0, tk.END)
    observaciones_entry.delete("1.0", tk.END)
    criterio_busqueda.delete(0, tk.END)

def reiniciar():
    python = sys.executable
    os.execl(python, python, *sys.argv)

def salir():
    root.destroy()

# --- INTERFAZ ---
root = tk.Tk()
root.title("INTEINSA – Gestión de Activos")
root.geometry("600x900")
root.configure(bg="#1f1f1f")
root.resizable(False, False)

estilo_label = {"bg": "#1f1f1f", "fg": "#00c7c7", "font": ("Segoe UI", 12)}
estilo_entry = {"bg": "#2c2c2c", "fg": "#ffffff", "font": ("Segoe UI", 12)}

# --- REGISTRO ---
tk.Label(root, text="📦 Registro de Producto", fg="#00ffcc", bg="#1f1f1f", font=("Segoe UI", 14, "bold")).pack(pady=10)
tk.Label(root, text="Código del Activo (manual o escáner):", **estilo_label).pack()
codigo_entry = tk.Entry(root, **estilo_entry); codigo_entry.pack(pady=5, ipadx=50)
tk.Button(root, text="📷 Escanear con cámara", command=escanear_codigo, bg="#00c7c7", fg="black", font=("Segoe UI", 11)).pack(pady=8)
tk.Label(root, text="Descripción del Producto:", **estilo_label).pack()
descripcion_entry = tk.Entry(root, **estilo_entry); descripcion_entry.pack(pady=5, ipadx=50)
tk.Label(root, text="Modelo del Producto:", **estilo_label).pack()
modelo_entry = tk.Entry(root, **estilo_entry); modelo_entry.pack(pady=5, ipadx=50)
tk.Label(root, text="Serial del Producto:", **estilo_label).pack()
serial_entry = tk.Entry(root, **estilo_entry); serial_entry.pack(pady=5, ipadx=50)
tk.Button(root, text="💾 Registrar Producto", command=registrar_producto, bg="#00ffcc", fg="black", font=("Segoe UI", 11)).pack(pady=10)

# --- ASIGNACIÓN ---
tk.Label(root, text="👤 Asignar Producto", fg="#ffaa00", bg="#1f1f1f", font=("Segoe UI", 14, "bold")).pack(pady=15)
tk.Label(root, text="Código del Activo:", **estilo_label).pack()
codigo_asig_entry = tk.Entry(root, **estilo_entry); codigo_asig_entry.pack(pady=5, ipadx=50)
tk.Label(root, text="Nombre del Usuario:", **estilo_label).pack()
usuario_entry = tk.Entry(root, **estilo_entry); usuario_entry.pack(pady=5, ipadx=50)
tk.Label(root, text="Código del Equipo:", **estilo_label).pack()
equipo_entry = tk.Entry(root, **estilo_entry); equipo_entry.pack(pady=5, ipadx=50)
tk.Label(root, text="Observaciones:", **estilo_label).pack()
observaciones_entry = tk.Text(root, height=4, bg="#2c2c2c", fg="white", font=("Segoe UI", 12)); observaciones_entry.pack(pady=5, ipadx=10)
tk.Button(root, text="📌 Asignar Producto", command=asignar_producto, bg="#ffaa00", fg="black", font=("Segoe UI", 11)).pack(pady=10)

# --- BÚSQUEDA ---
tk.Label(root, text="🔍 Buscar por Usuario o Equipo", fg="#9f9fff", bg="#1f1f1f", font=("Segoe UI", 13, "bold")).pack(pady=15)
criterio_busqueda = tk.Entry(root, **estilo_entry); criterio_busqueda.pack(pady=5, ipadx=50)
tk.Button(root, text="🔎 Buscar Activo", command=buscar_activos, bg="#9f9fff", fg="black", font=("Segoe UI", 11)).pack(pady=8)

# --- FINAL ---
tk.Button(root, text="🧹 Limpiar Todo", command=limpiar_todo, bg="#444", fg="white").pack(pady=5)
tk.Button(root, text="🔄 Reiniciar", command=reiniciar, bg="#444", fg="white").pack(pady=5)
tk.Button(root, text="❌ Salir", command=salir, bg="#aa0000", fg="white").pack(pady=10)
tk.Label(root, text="Desarrollado por NeuroSentrix-TECH", bg="#1f1f1f", fg="#888").pack(side="bottom", pady=10)

root.mainloop()
