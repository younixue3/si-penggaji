from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import transaction
import logging
from decimal import Decimal
from datetime import datetime, time, timedelta
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from mysite.utils.helpers import dd
logger = logging.getLogger(__name__)

STATUS_CHOICES = [
    ('progress', 'Progress'),
    ('selesai', 'Selesai'),
    ('aktif', 'Aktif'),
]

MONTH_CHOICES = [
    ('January', 'January'),
    ('February', 'February'), 
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]

class TableGaji(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    gaji_pokok = models.IntegerField(
        default=0,
        help_text="Base salary amount"
    )

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

    def create_slip_gaji(self):
        """
        Create SlipGaji records for all active users after a new Penggajian is created.
        This method should be called after creating a new Penggajian instance.
        """
        users = User.objects.filter(is_active=True)
        
        for user in users:
            slip_gaji = SlipGaji(
                penggajian=self,
                user=user
            )
            slip_gaji.save()  # This will trigger the save() method

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        try:
            with transaction.atomic():
                super().save(*args, **kwargs)
                
                if is_new:
                    self.create_slip_gaji()
                    
        except Exception as e:
            logger.error(f"Error creating Penggajian and SlipGaji: {str(e)}")
            raise

class SlipGaji(models.Model):
    penggajian = models.ForeignKey(Penggajian, related_name='slip_gaji', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upah_per_menit = models.IntegerField(default=0)
    gaji_bersih = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Slip Gaji - {self.user.username} ({self.created_at.strftime('%B %Y')})"

    def calculate_upah_per_menit(self):
        days_in_month = self.penggajian.days_in_month
        gaji_pokok = self.user.tablegaji.gaji_pokok
        
        WORK_HOURS_PER_DAY = 11
        minutes_per_day = WORK_HOURS_PER_DAY * 60  # 660 minutes
        
        total_minutes_worked = days_in_month * minutes_per_day
        
        try:
            if total_minutes_worked > 0:
                cut_per_minute = gaji_pokok / total_minutes_worked
            else:
                cut_per_minute = 0
        except ZeroDivisionError:
            logger.error(f"Division by zero when calculating cut_per_minute for SlipGaji ID: {self.id}")
            cut_per_minute = 0
            
        self.upah_per_menit = round(cut_per_minute, 0)
        return self.upah_per_menit

    def calculate_gaji_bersih(self):
        self.gaji_bersih = self.izin_list.aggregate(total=models.Sum('upah_harian'))['total'] or 0
        return self.gaji_bersih

    def create_izin_masuk(self):
        """
        Create IzinKeluarMasuk records for a slip gaji.
        Creates records from the 5th day of the month until days_in_month.
        """
        if not self.pk:
            raise ValueError("SlipGaji instance must be saved before creating IzinKeluarMasuk records")

        # Get month name and convert to datetime
        month_name = self.penggajian.month
        current_year = datetime.now().year
        month_num = datetime.strptime(month_name, '%B').month
        
        # Create date range from 5th to days_in_month
        start_date = datetime(current_year, month_num, 5)
        end_date = start_date + timedelta(days=self.penggajian.days_in_month)  # Subtract 5 to account for starting from 5th
        
        # Generate list of dates
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date.date())
            current_date += timedelta(days=1)

        # Create IzinKeluarMasuk objects for each date
        izin_masuk_objects = [
            IzinKeluarMasuk(
                slip_gaji=self,
                date=date,
                time_out=time(0, 0),
                time_in=time(0, 0),
                nilai_izin=0,
                time_work=time(0, 0),
                upah_harian=0
            ) for date in date_list
        ]
        
        IzinKeluarMasuk.objects.bulk_create(izin_masuk_objects)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        self.calculate_upah_per_menit()
        
        with transaction.atomic():
            super().save(*args, **kwargs)
            
            if is_new:
                self.create_izin_masuk()
            
            self.calculate_gaji_bersih()
            if not is_new:
                super().save(update_fields=['gaji_bersih'])

class IzinKeluarMasuk(models.Model):
    slip_gaji = models.ForeignKey(SlipGaji, related_name='izin_list', on_delete=models.CASCADE)
    date = models.DateField(null=True, blank=True)
    time_out = models.TimeField(blank=True, default=time(0, 0))
    time_in = models.TimeField(blank=True, default=time(0, 0))
    nilai_izin = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    time_work = models.TimeField(blank=True, default=time(0, 0))
    upah_harian = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    potongan = models.BooleanField(default=False)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f"Absensi {self.slip_gaji.user.username} - {self.date}"

    def calculate_upah_harian(self):
        upah_per_menit = self.slip_gaji.upah_per_menit

        # Convert time_work to datetime for comparison
        base_date = datetime.now().date()
        time_work_datetime = datetime.combine(base_date, self.time_work)
        end_time = datetime.combine(base_date, time(22, 0))  # 22:00
        
        if time_work_datetime < end_time:
            time_diff = end_time - time_work_datetime
            minutes = time_diff.total_seconds() / 60
        else:
            minutes = 0
        
        nilai_izin = self.nilai_izin - 60
        if nilai_izin > 0:
            minutes -= nilai_izin

        upah_harian = Decimal(str(minutes)) * Decimal(str(upah_per_menit))

        if self.potongan:
            upah_harian = upah_harian * Decimal('0.95')  # Apply 5% discount

        self.upah_harian = upah_harian

        return self.upah_harian
    
    def calculate_nilai_izin(self):
        # Convert time fields to datetime for calculation
        base_date = datetime.now().date()
        time_out_datetime = datetime.combine(base_date, self.time_out)
        time_in_datetime = datetime.combine(base_date, self.time_in)
        
        time_diff = time_in_datetime - time_out_datetime
        nilai_izin = time_diff.total_seconds() / 60  # Convert to minutes

        self.nilai_izin = nilai_izin
        return self.nilai_izin

    def save(self, *args, **kwargs):
        self.calculate_nilai_izin()
        self.calculate_upah_harian()
        super().save(*args, **kwargs)

        self.slip_gaji.calculate_gaji_bersih()
        self.slip_gaji.save(update_fields=['gaji_bersih'])

# # Signal handlers for automatic gaji bersih calculation
# @receiver(post_save, sender=IzinKeluarMasuk)
# def update_gaji_bersih_on_izin_save(sender, instance, **kwargs):
#     """
#     Automatically recalculate gaji_bersih when IzinKeluarMasuk is saved.
#     """
#     slip_gaji = instance.slip_gaji
#     slip_gaji.calculate_gaji_bersih()
#     slip_gaji.save(update_fields=['gaji_bersih'])

# @receiver(post_delete, sender=IzinKeluarMasuk)
# def update_gaji_bersih_on_izin_delete(sender, instance, **kwargs):
#     """
#     Automatically recalculate gaji_bersih when IzinKeluarMasuk is deleted.
#     """
#     slip_gaji = instance.slip_gaji
#     slip_gaji.calculate_gaji_bersih()
#     slip_gaji.save(update_fields=['gaji_bersih'])

# @receiver(post_save, sender=Penggajian)
# def create_izin_keluar_masuk_on_penggajian_save(sender, instance, created, **kwargs):
#     if created:  # Only run for newly created instances
#         for slip_gaji in instance.slip_gaji.all():
#             slip_gaji.create_izin_masuk()
#             slip_gaji.calculate_gaji_bersih()
#             slip_gaji.save(update_fields=['gaji_bersih'])
