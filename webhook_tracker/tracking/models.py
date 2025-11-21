from django.db import models
import uuid
from django.urls import reverse



class TrackingCampaign(models.Model):
    name = models.CharField(max_length=200)
    tracking_id = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    target_url = models.URLField(default='https://google.com')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.tracking_id})"
    
    def get_absolute_url(self):
        return reverse('tracking:track', kwargs={'tracking_id': self.tracking_id})
    
    def get_tracking_url(self):
        # Use Django sites framework or settings
        from django.conf import settings
        base_url = getattr(settings, 'TRACKING_BASE_URL', 'http://127.0.0.1:8000')
        return f"{base_url}/track/{self.tracking_id}/"
    
    def get_requests_count(self):
        return self.webhookrequest_set.count()
    
    def get_unique_visitors(self):
        return self.webhookrequest_set.values('ip_address').distinct().count()

# Update the WebhookRequest model to add foreign key
class WebhookRequest(models.Model):
    campaign = models.ForeignKey(TrackingCampaign, on_delete=models.CASCADE, null=True, blank=True)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tracking_id = models.CharField(max_length=100, db_index=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    referrer = models.URLField(blank=True, null=True)
    headers = models.JSONField(default=dict)
    method = models.CharField(max_length=10, default='GET')
    query_params = models.JSONField(default=dict)
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    isp = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['tracking_id', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.tracking_id} - {self.ip_address} - {self.timestamp}"
    
    def get_location_display(self):
        if self.city and self.country:
            return f"{self.city}, {self.country}"
        return self.country or "Unknown"