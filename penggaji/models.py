from django.db import models

class Penggajian(models.Model):
    # Status choices for Penggajian
    STATUS_CHOICES = [
        ('progress', 'Progress'),
        ('selesai', 'Selesai'), 
        ('aktif', 'Aktif'),
    ]

    days_in_month = models.IntegerField()
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='progress'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Penggajian - {self.created_at.strftime('%B %Y')}"

class SlipGaji(models.Model):
    penggajian = models.ForeignKey(Penggajian, related_name='slip_gaji', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    gaji_pokok = models.DecimalField(max_digits=12, decimal_places=2)
    total_potongan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gaji_bersih = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Slip Gaji - {self.user.username} ({self.created_at.strftime('%B %Y')})"

    def calculate_total_potongan(self):
        # Calculate total deductions from IzinKeluarMasuk
        izin_potongan = self.izin_list.aggregate(
            total=models.Sum('nilai_izin')
        )['total'] or 0
        self.total_potongan = izin_potongan
        return self.total_potongan

    def calculate_gaji_bersih(self):
        # Calculate net salary
        self.gaji_bersih = self.gaji_pokok - self.calculate_total_potongan()
        return self.gaji_bersih

    def save(self, *args, **kwargs):
        self.calculate_total_potongan()
        self.calculate_gaji_bersih()
        super().save(*args, **kwargs)

class IzinKeluarMasuk(models.Model):
    slip_gaji = models.ForeignKey(SlipGaji, related_name='izin_list', on_delete=models.CASCADE)
    date = models.DateField()
    time_out = models.TimeField()  
    time_in = models.TimeField()
    nilai_izin = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Izin - {self.date} ({self.time_out} - {self.time_in})"
