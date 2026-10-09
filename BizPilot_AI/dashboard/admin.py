from django.contrib import admin
from .models import AnalysisResult

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'filename', 'upload_date', 'total_revenue', 'total_profit', 'health_score','profit_margin','health_status','total_products','total_records')
    list_filter = ('upload_date', 'health_status')
    search_fields = ('user__username', 'filename')
