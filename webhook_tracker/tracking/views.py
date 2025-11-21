from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from .models import WebhookRequest, TrackingCampaign
from .forms import TrackingCampaignForm



class CampaignCreateView(CreateView):
    model = TrackingCampaign
    form_class = TrackingCampaignForm
    template_name = 'tracking/campaign_form.html'
    success_url = reverse_lazy('tracking:campaign_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Tracking campaign '{form.instance.name}' created successfully!")
        return super().form_valid(form)

class CampaignUpdateView(UpdateView):
    model = TrackingCampaign
    form_class = TrackingCampaignForm
    template_name = 'tracking/campaign_form.html'
    success_url = reverse_lazy('tracking:campaign_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Tracking campaign '{form.instance.name}' updated successfully!")
        return super().form_valid(form)

class CampaignListView(ListView):
    model = TrackingCampaign
    template_name = 'tracking/campaign_list.html'
    context_object_name = 'campaigns'

class CampaignDeleteView(DeleteView):
    model = TrackingCampaign
    template_name = 'tracking/campaign_confirm_delete.html'
    success_url = reverse_lazy('tracking:campaign_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Tracking campaign deleted successfully!")
        return super().delete(request, *args, **kwargs)

class CampaignDetailView(DetailView):
    model = TrackingCampaign
    template_name = 'tracking/campaign_detail.html'
    context_object_name = 'campaign'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_requests'] = self.object.webhookrequest_set.all()[:10]
        return context


class TrackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, tracking_id):
        return self.process_request(request, tracking_id)
    
    def post(self, request, tracking_id):
        return self.process_request(request, tracking_id)
    
    def process_request(self, request, tracking_id):
        # Try to find campaign
        try:
            campaign = TrackingCampaign.objects.get(tracking_id=tracking_id, is_active=True)
            target_url = campaign.target_url
        except TrackingCampaign.DoesNotExist:
            campaign = None
            target_url = request.GET.get('redirect', 'https://google.com')
        
        # Get client IP
        ip_address = self.get_client_ip(request)
        
        # Get location information
        location_data = self.get_ip_location(ip_address)
        
        # Create WebhookRequest record
        webhook_request = WebhookRequest.objects.create(
            tracking_id=tracking_id,
            campaign=campaign,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', ''),
            headers=self.get_headers_dict(request),
            method=request.method,
            query_params=dict(request.GET),
            country=location_data.get('country'),
            city=location_data.get('city'),
            region=location_data.get('regionName'),
            isp=location_data.get('isp'),
            latitude=location_data.get('lat'),
            longitude=location_data.get('lon'),
        )
        
        print(f" Tracked: {tracking_id} from {ip_address}")
        print(f" Location: {webhook_request.get_location_display()}")
        
        return HttpResponseRedirect(target_url)
    

class TrackView(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def get(self, request, tracking_id):
        return self.process_request(request, tracking_id)
    
    def post(self, request, tracking_id):
        return self.process_request(request, tracking_id)
    
    def process_request(self, request, tracking_id):
        # Get client IP (handles proxies)
        ip_address = self.get_client_ip(request)
        
        # Get location information
        location_data = self.get_ip_location(ip_address)
        
        # Create WebhookRequest record
        webhook_request = WebhookRequest.objects.create(
            tracking_id=tracking_id,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', ''),
            headers=self.get_headers_dict(request),
            method=request.method,
            query_params=dict(request.GET),
            country=location_data.get('country'),
            city=location_data.get('city'),
            region=location_data.get('regionName'),
            isp=location_data.get('isp'),
            latitude=location_data.get('lat'),
            longitude=location_data.get('lon'),
        )
        
        print(f" Tracked: {tracking_id} from {ip_address}")
        print(f" Location: {webhook_request.get_location_display()}")
        
        # Redirect to target URL (you can make this configurable)
        target_url = request.GET.get('redirect', 'https://google.com')
        return HttpResponseRedirect(target_url)
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_headers_dict(self, request):
        headers = {}
        for key, value in request.META.items():
            if key.startswith('HTTP_'):
                header_name = key[5:].replace('_', '-').title()
                headers[header_name] = value
        return headers
    
    def get_ip_location(self, ip):
        try:
            # Using ip-api.com (free tier)
            response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query')
            data = response.json()
            return data if data.get('status') == 'success' else {}
        except Exception as e:
            print(f"Location lookup failed: {e}")
            return {}

class RequestListView(ListView):
    model = WebhookRequest
    template_name = 'tracking/view_requests.html'
    context_object_name = 'requests'
    paginate_by = 50
    
    def get_queryset(self):
        tracking_id = self.kwargs.get('tracking_id')
        return WebhookRequest.objects.filter(tracking_id=tracking_id)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking_id'] = self.kwargs.get('tracking_id')
        return context

class RequestDetailView(DetailView):
    model = WebhookRequest
    template_name = 'tracking/request_detail.html'
    context_object_name = 'webhook_request'


class DashboardView(View):
    def get(self, request):
        campaigns = TrackingCampaign.objects.all()[:5]
        recent_requests = WebhookRequest.objects.select_related('campaign').order_by('-timestamp')[:10]
        
        total_requests = WebhookRequest.objects.count()
        unique_ips = WebhookRequest.objects.values('ip_address').distinct().count()
        active_campaigns = TrackingCampaign.objects.filter(is_active=True).count()
        
        context = {
            'campaigns': campaigns,
            'recent_requests': recent_requests,
            'total_requests': total_requests,
            'unique_ips': unique_ips,
            'active_campaigns': active_campaigns,
        }
        return render(request, 'tracking/dashboard.html', context)
    

class RequestDataAPI(View):
    def get(self, request, tracking_id):
        requests = WebhookRequest.objects.filter(tracking_id=tracking_id).order_by('-timestamp')[:100]
        data = []
        for req in requests:
            data.append({
                'id': str(req.id),
                'ip_address': req.ip_address,
                'user_agent': req.user_agent,
                'location': req.get_location_display(),
                'timestamp': req.timestamp.isoformat(),
                'method': req.method,
            })
        return JsonResponse(data, safe=False)