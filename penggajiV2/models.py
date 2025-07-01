from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import json

# Pilihan untuk tipe operator dalam perhitungan
OPERATOR_CHOICES = [
    ('add', 'Tambah'),
    ('subtract', 'Kurang'),
    ('multiply', 'Kali'),
    ('divide', 'Bagi'),
    ('percentage', 'Persentase'),
    ('if_condition', 'Kondisi If'),
    ('greater_than', 'Lebih Besar Dari'),
    ('less_than', 'Lebih Kecil Dari'),
    ('equal', 'Sama Dengan'),
    ('not_equal', 'Tidak Sama Dengan'),
]

# Pilihan untuk tipe data input
INPUT_TYPE_CHOICES = [
    ('number', 'Angka'),
    ('text', 'Teks'),
    ('date', 'Tanggal'),
    ('time', 'Waktu'),
    ('boolean', 'Ya/Tidak'),
    ('select', 'Pilihan'),
]

class PayrollTemplate(models.Model):
    """Model untuk template perhitungan gaji kustom"""
    name = models.CharField(max_length=100, help_text="Nama template perhitungan gaji")
    description = models.TextField(blank=True, help_text="Deskripsi tentang template ini")
    is_active = models.BooleanField(default=True, help_text="Status aktif template")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name

class PayrollVariable(models.Model):
    """Model untuk variabel yang digunakan dalam perhitungan"""
    template = models.ForeignKey(PayrollTemplate, on_delete=models.CASCADE, related_name='variables')
    name = models.CharField(max_length=50, help_text="Nama variabel (tanpa spasi)")
    display_name = models.CharField(max_length=100, help_text="Nama yang ditampilkan")
    input_type = models.CharField(max_length=20, choices=INPUT_TYPE_CHOICES, help_text="Tipe data input")
    is_required = models.BooleanField(default=False, help_text="Apakah wajib diisi")
    default_value = models.CharField(max_length=255, blank=True, help_text="Nilai default")
    options = models.TextField(blank=True, help_text="Opsi untuk tipe select dalam format JSON: [{\"value\": \"1\", \"label\": \"Opsi 1\"}]")
    order = models.PositiveIntegerField(default=0, help_text="Urutan tampilan")
    
    def __str__(self):
        return f"{self.display_name} ({self.name})"
    
    def clean(self):
        # Validasi format nama variabel (tanpa spasi dan karakter khusus)
        if ' ' in self.name or not self.name.isalnum():
            raise ValidationError({'name': 'Nama variabel tidak boleh mengandung spasi atau karakter khusus'})
        
        # Validasi format options untuk tipe select
        if self.input_type == 'select' and self.options:
            try:
                options = json.loads(self.options)
                if not isinstance(options, list):
                    raise ValidationError({'options': 'Format opsi harus berupa array JSON'})
                for option in options:
                    if not isinstance(option, dict) or 'value' not in option or 'label' not in option:
                        raise ValidationError({'options': 'Setiap opsi harus memiliki value dan label'})
            except json.JSONDecodeError:
                raise ValidationError({'options': 'Format JSON tidak valid'})

class PayrollCalculationStep(models.Model):
    """Model untuk langkah-langkah perhitungan dalam logic flow"""
    template = models.ForeignKey(PayrollTemplate, on_delete=models.CASCADE, related_name='calculation_steps')
    step_id = models.CharField(max_length=50, help_text="ID unik untuk langkah ini")
    name = models.CharField(max_length=100, help_text="Nama langkah perhitungan")
    operator = models.CharField(max_length=20, choices=OPERATOR_CHOICES, help_text="Operator yang digunakan")
    input1_type = models.CharField(max_length=20, choices=[("variable", "Variabel"), ("value", "Nilai"), ("step", "Hasil Langkah")], help_text="Tipe input pertama")
    input1_value = models.CharField(max_length=255, help_text="Nilai atau referensi input pertama")
    input2_type = models.CharField(max_length=20, choices=[("variable", "Variabel"), ("value", "Nilai"), ("step", "Hasil Langkah")], blank=True, help_text="Tipe input kedua")
    input2_value = models.CharField(max_length=255, blank=True, help_text="Nilai atau referensi input kedua")
    result_variable = models.CharField(max_length=50, help_text="Nama variabel untuk menyimpan hasil")
    order = models.PositiveIntegerField(default=0, help_text="Urutan eksekusi")
    condition_true_step = models.CharField(max_length=50, blank=True, help_text="ID langkah jika kondisi benar (untuk operator kondisional)")
    condition_false_step = models.CharField(max_length=50, blank=True, help_text="ID langkah jika kondisi salah (untuk operator kondisional)")
    
    def __str__(self):
        return f"{self.name} ({self.step_id})"
    
    class Meta:
        ordering = ['order']

class PayrollAssignment(models.Model):
    """Model untuk penugasan template perhitungan gaji ke pengguna"""
    template = models.ForeignKey(PayrollTemplate, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.template.name}"
    
    class Meta:
        unique_together = ['template', 'user']

class PayrollCalculationResult(models.Model):
    """Model untuk menyimpan hasil perhitungan gaji"""
    assignment = models.ForeignKey(PayrollAssignment, on_delete=models.CASCADE)
    calculation_date = models.DateField()
    input_values = models.JSONField(help_text="Nilai input dalam format JSON")
    calculation_results = models.JSONField(help_text="Hasil perhitungan dalam format JSON")
    final_result = models.DecimalField(max_digits=12, decimal_places=2, help_text="Hasil akhir perhitungan gaji")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Hasil {self.assignment.user.username} - {self.calculation_date}"
