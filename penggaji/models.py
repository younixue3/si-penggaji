from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = [
        ('progress', 'Progress'),
        ('selesai', 'Selesai'),
        ('aktif', 'Aktif'),
    ]

MONTH_CHOICES = [
        ('january', 'January'),
        ('february', 'February'), 
        ('march', 'March'),
        ('april', 'April'),
        ('may', 'May'),
        ('june', 'June'),
        ('july', 'July'),
        ('august', 'August'),
        ('september', 'September'),
        ('october', 'October'),
        ('november', 'November'),
        ('december', 'December'),
    ]

class Penggajian(models.Model):

    month = models.CharField(
        max_length=20,
        choices=MONTH_CHOICES,
        help_text="The month for this payroll period"
    )
    days_in_month = models.IntegerField(
        help_text="Number of working days in the month"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='progress',
        help_text="Current status of the payroll processing"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when record was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when record was last updated"
    )

    class Meta:
        verbose_name = "Penggajian"
        verbose_name_plural = "Penggajian"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['month']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Penggajian - {self.month}"

    def clean(self):
        """Validate the model data."""
        if self.days_in_month < 1 or self.days_in_month > 31:
            raise ValidationError({
                'days_in_month': 'Days in month must be between 1 and 31'
            }) 

    def save(self, *args, **kwargs):
        # Get all active users
        active_users = User.objects.all()
        
        # Create SlipGaji records for each active user
        for user in active_users:
            slipgaji = SlipGaji.objects.create(
                penggajian=self.id,
                user=user.id
            )
            print(slipgaji)

class SlipGaji(models.Model):
    penggajian = models.ForeignKey(Penggajian, related_name='slip_gaji', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    gaji_pokok = models.DecimalField(max_digits=12, decimal_places=2, default=0)
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
