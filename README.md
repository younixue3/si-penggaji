# Si Penggaji

Sistem manajemen penggajian yang dibangun dengan Django dan Django-Tailwind.

## Fitur

- Manajemen karyawan
- Perhitungan gaji
- Pelacakan kehadiran
- Laporan penggajian
- Antarmuka pengguna yang menarik dengan Tailwind CSS
- Manajemen tunjangan dan potongan
- Dashboard analitik
- Ekspor laporan ke PDF/Excel

## Tech Stack

- Django 4.x
- Django-Tailwind
- Python 3.x
- SQLite/PostgreSQL
- HTML/CSS
- JavaScript
- Alpine.js (opsional untuk interaktivitas)

## Prasyarat

- Python 3.8 atau lebih tinggi
- pip
- Node.js dan npm (untuk Tailwind CSS)
- Git

## Instalasi

1. Clone repositori
   ```bash
   git clone https://github.com/username/si-penggaji.git
   cd si-penggaji
   ```
2. Buat virtual environment
   
   ```
   python -m venv venv
   ```
3. Aktifkan virtual environment
   
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```
     source venv/bin/activate
     ```
4. Instal dependensi Python
   
   ```
   pip install -r requirements.txt
   ```
5. Instal dependensi Tailwind CSS
   
   ```
   python manage.py tailwind install
   ```
6. Jalankan migrasi database
   
   ```
   python manage.py migrate
   ```
7. Buat superuser (admin)
   
   ```
   python manage.py createsuperuser
   ```
## Penggunaan
1. Jalankan server pengembangan
   
   ```
   python manage.py runserver
   ```
2. Jalankan proses build Tailwind CSS (dalam terminal terpisah)
   
   ```
   python manage.py tailwind start
   ```
3. Akses aplikasi di browser: http://127.0.0.1:8000/
4. Akses panel admin di: http://127.0.0.1:8000/admin/

## Deployment
### Persiapan untuk Produksi
1. Sesuaikan pengaturan produksi di settings.py :
   
   ```
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com', 
   'www.yourdomain.com']
   ```
2. Konfigurasi database produksi (PostgreSQL disarankan)
3. Kumpulkan file statis
   
   ```
   python manage.py collectstatic
   ```
### Opsi Deployment
- Heroku : Gunakan Procfile dan requirements.txt
- PythonAnywhere : Ikuti panduan deployment Django mereka
- DigitalOcean : Gunakan App Platform atau droplet dengan Gunicorn dan Nginx
- AWS : Gunakan Elastic Beanstalk atau EC2
## Kontribusi
1. Fork repositori
2. Buat branch fitur ( git checkout -b fitur-baru )
3. Commit perubahan Anda ( git commit -m 'Menambahkan fitur baru' )
4. Push ke branch ( git push origin fitur-baru )
5. Buat Pull Request
## Lisensi
Proyek ini dilisensikan di bawah MIT License .

## Kontak
Untuk pertanyaan atau dukungan, silakan hubungi email@example.com .