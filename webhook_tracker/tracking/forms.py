from django import forms
from .models import TrackingCampaign
import random
import string

class TrackingCampaignForm(forms.ModelForm):
    generate_id = forms.BooleanField(
        required=False, 
        initial=True,
        help_text="Automatically generate a tracking ID"
    )
    custom_tracking_id = forms.CharField(
        required=False,
        max_length=100,
        help_text="Leave empty to auto-generate, or specify your own ID"
    )
    
    class Meta:
        model = TrackingCampaign
        fields = ['name', 'description', 'target_url', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'target_url': forms.URLInput(attrs={'placeholder': 'https://example.com'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        generate_id = cleaned_data.get('generate_id')
        custom_tracking_id = cleaned_data.get('custom_tracking_id')
        
        if not generate_id and not custom_tracking_id:
            raise forms.ValidationError("Either generate ID automatically or provide a custom tracking ID.")
        
        if custom_tracking_id and TrackingCampaign.objects.filter(tracking_id=custom_tracking_id).exists():
            raise forms.ValidationError("This tracking ID is already in use.")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        if self.cleaned_data.get('generate_id') and not self.cleaned_data.get('custom_tracking_id'):
            # Generate unique tracking ID
            while True:
                tracking_id = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
                if not TrackingCampaign.objects.filter(tracking_id=tracking_id).exists():
                    instance.tracking_id = tracking_id
                    break
        else:
            instance.tracking_id = self.cleaned_data.get('custom_tracking_id')
        
        if commit:
            instance.save()
        
        return instance