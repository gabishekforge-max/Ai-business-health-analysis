from django.db import models
from django.contrib.auth.models import User

class AnalysisResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    total_revenue = models.FloatField()
    total_profit = models.FloatField()
    profit_margin = models.FloatField()
    health_score = models.IntegerField()
    health_status = models.CharField(max_length=50)
    total_products = models.IntegerField()
    total_records = models.IntegerField()

    def __str__(self):
        return f"{self.filename} - {self.upload_date.strftime('%Y-%m-%d %H:%M')}"