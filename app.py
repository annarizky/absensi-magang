from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app) # Mengizinkan frontend HTML mengakses API ini

# IP Wi-Fi Kantor (Ganti dengan Public IP kantor yang sebenarnya)
IP_KANTOR_SAH = "127.0.0.1" 
# Catatan: 127.0.0.1 dipakai untuk tes di laptop yang sama. Nanti ganti dengan IP publik kantor.

# Fungsi untuk inisialisasi database SQLite
def init_db():
    conn = sqlite3.connect('data_presensi.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS presensi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            waktu TEXT,
            nama TEXT,
            instansi TEXT,
            ip_address TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Jalankan inisialisasi saat script dimulai
init_db()

@app.route('/api/absen', methods=['POST'])
def proses_absen():
    data = request.json
    nama = data.get('nama')
    instansi = data.get('instansi')
    
    # Membaca IP Address dari perangkat yang menekan tombol
    ip_pengunjung = request.remote_addr

    # Pengecekan IP
    if ip_pengunjung == IP_KANTOR_SAH:
        status_absen = "Berhasil"
        pesan = "Absen sukses dicatat."
        is_sukses = True
    else:
        status_absen = "Ditolak (Bukan Wi-Fi Kantor)"
        pesan = f"Akses ditolak. IP kamu: {ip_pengunjung}"
        is_sukses = False

    # Simpan ke Database SQLite
    waktu_sekarang = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect('data_presensi.db')
    c = conn.cursor()
    c.execute("INSERT INTO presensi (waktu, nama, instansi, ip_address, status) VALUES (?, ?, ?, ?, ?)",
              (waktu_sekarang, nama, instansi, ip_pengunjung, status_absen))
    conn.commit()
    conn.close()

    # Kirim balasan ke Frontend
    return jsonify({
        "sukses": is_sukses,
        "pesan": pesan
    })

if __name__ == '__main__':
    # Jalankan server di port 5000
    app.run(debug=True, port=5000)