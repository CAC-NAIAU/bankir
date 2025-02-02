from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
import os

# Create your models here.
class Figurant(models.Model):
    STATUS_CHOICES = [
                    ('-', '-'),
                    ('У роботі', 'У роботі'),
                    ('Відпрацьовано', 'Відпрацьовано'),
                    ('Кошик', 'Кошик')
                    ]
 
    fig_inn = models.CharField(primary_key=True, max_length=50)
    fig_name = models.TextField()
    activity_info = CKEditor5Field(null=True, blank=True, config_name="extends")
    add_info = CKEditor5Field(null=True, blank=True, config_name="extends")
    fig_logo = models.ImageField(default="fallback.png", blank=True, upload_to=f'logos/')
    status = models.CharField(choices=STATUS_CHOICES, default="-")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.fig_logo:
            if not os.path.exists(os.path.join(settings.MEDIA_ROOT, 'logos')):
                os.makedirs(os.path.join(settings.MEDIA_ROOT, 'logos'))
            file_name = os.path.basename(self.fig_logo.name)
            if "logo" not in file_name and file_name != 'fallback.png':
                file_base, file_extension = os.path.splitext(file_name)
                file_base = self.fig_inn
                
                #
                figurant_inn_dir = os.path.join(settings.MEDIA_ROOT, 'logos', self.fig_inn)
                
                if not os.path.exists(figurant_inn_dir):
                    os.makedirs(figurant_inn_dir)
                
                #
                logo_files_count = len([name for name in os.listdir(figurant_inn_dir) if os.path.isfile(os.path.join(figurant_inn_dir, name))])
                
                self.fig_logo.name = os.path.join(f'{file_base}', f"logo_{logo_files_count + 1}_" + file_base + file_extension)

        super(Figurant, self).save(*args, **kwargs)

    def __str__(self):
        return f"Назва: {self.fig_name} (ІНН {self.fig_inn})"

class FigAccount(models.Model):
    figurant = models.ForeignKey(
        Figurant, on_delete=models.CASCADE
        )
    account = models.TextField(null=True)
    currency = models.TextField(null=True)
    bank_code = models.TextField(null=True)
    bank_name = models.TextField(null=True)
    
    def __str__(self):
        return f"{self.figurant}, номер рахунку: {self.account}"
    
class Transaction(models.Model):    
    fig_acc = models.ForeignKey(
        FigAccount, on_delete=models.CASCADE
        )
    contr_acc=models.TextField(null=True)
    contr_name=models.TextField(null=True)
    contr_ipn=models.TextField(null=True)
    contr_bank_code=models.TextField(null=True)
    contr_bank_name=models.TextField(null=True)
    pay_purp=models.TextField(null=True)
    doc_num=models.TextField(null=True)
    doc_date=models.DateTimeField(null=True)
    direction=models.TextField(null=True)
    sum_ct=models.FloatField(null=True)
    sum_dt=models.FloatField(null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.fig}, транзакції рахунку: {self.fig_acc}"
