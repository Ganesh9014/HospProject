from django import forms
from hospApp.models import OpPatientRegistration

class OpPatientRegistrationForm(forms.ModelForm):
    gender = forms.ChoiceField(
        choices=[('Male', 'Male'), ('Female', 'Female')],
        widget=forms.Select(attrs={'class': 'form-select'},)
    )

    

    class Meta:
        model = OpPatientRegistration
        fields = '__all__'
        exclude = ['entrytime', 'createdtime', 'updatedtime', 'pro', 'refdoctor']

        widgets = {
            'entrydate': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 'class': 'form-control', 'readonly': True
            }),
            'uhid': forms.TextInput(attrs={
                'readonly': True, 'class': 'form-control', 'maxlength': '15'
            }),
            'title': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'patname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Patient Name',
                'required': True,
                'pattern': '^[A-Za-z .]+$',
                'title': 'Patient name must contain only letters and spaces.',
                'id':"patname",
            }),
            'fname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Father/Husband/Guardian Name',
                'required': True,
                'pattern': '^[A-Za-z .]+$',
                'title': 'Name must contain only letters and spaces.'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'min': '0',
                'max': '120',
                'required': True,
                
                'oninput': "if(this.value.length>3)this.value=this.value.slice(0,3);"

            }),
            'agetype': forms.Select(attrs={'class': 'form-select', 'required': True},
                                     choices=[('Years', 'Years'), ('Months', 'Months'), ('Days', 'Days'), ('Weeks', 'Weeks')]),
            'phone': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit Phone Number',
                'pattern': '^[0-9]{10}$',
                'title': 'Enter a valid 10-digit phone number',
                'required': True,
                'oninput': "if(this.value.length>10)this.value=this.value.slice(0,10);",
                'autocomplete': 'off'
                
            }),
            'alternatephone': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '10-digit Alternate Phone Number',    
                'pattern': '^[0-9]{10}$',
                'title': 'Enter a valid 10-digit phone number',
                'oninput': "if(this.value.length>10)this.value=this.value.slice(0,10);"
            }), 
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Enter full address',
                'required': True,
                'autocomplete': 'off'
            }),
            'state': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'district': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'city': forms.Select(attrs={'class': 'form-select', 'required': True}),
            'area': forms.TextInput(attrs={'class': 'form-control', 'required': True, 'maxlength': '50','placeholder': 'Enter Area Name'}),
            'pincode': forms.NumberInput(attrs={
                'class': 'form-control',
                'pattern': '^[0-9]{6}$',
                'title': 'Enter a valid 6-digit pincode',
                'oninput': "if(this.value.length>6)this.value=this.value.slice(0,6);",
                'placeholder': 'Enter Pincode',
            }),
           'userid': forms.PasswordInput(attrs={
            'class': 'usercode form-control',
            'placeholder': '****',
            'required': True,
            }),
            'refdoctor': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            
        }



    def clean_gender(self):
        title = self.cleaned_data.get("title", "").upper()
        if title in ["MR", "MASTER"]:
            return "Male"
        if title in ["MRS", "MISS", "MS", "BABY"]:
            return "Female"
        return "Male"   # fallback
    def clean_phone(self):
        phone = str(self.cleaned_data.get('phone', ''))
        
        # Must be exactly 10 digits
        if len(phone) != 10:
            raise forms.ValidationError("Phone number must be exactly 10 digits.")
        
        # Must start with 6, 7, 8, or 9 (Indian mobile numbers)
        if phone[0] not in ('6', '7', '8', '9'):
            raise forms.ValidationError("Enter a valid Indian mobile number (must start with 6, 7, 8, or 9).")
        
        # No all-same digits (0000000000, 1111111111, etc.)
        if len(set(phone)) == 1:
            raise forms.ValidationError("Enter a valid phone number.")
        
        # No sequential digits (1234567890 or 9876543210)
        ascending  = ''.join(str(i) for i in range(0, 10))   # 0123456789
        descending = ''.join(str(i) for i in range(9, -1, -1)) # 9876543210
        if phone in (ascending, descending, ascending[1:] + ascending[0], '1234567890', '0987654321'):
            raise forms.ValidationError("Enter a valid phone number.")
        
        return phone

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['gender'].widget.attrs['readonly'] = True
        self.fields['gender'].widget.attrs['style'] = "pointer-events: none; background:#e9ecef;"

        # 🩺 Bootstrap styling
        for name, field in self.fields.items():
            css = 'form-select' if isinstance(field.widget, forms.Select) else 'form-control'
            field.widget.attrs.setdefault('class', css)

        # 🔒 Read-only fields
        if 'uhid' in self.fields:
            self.fields['uhid'].widget.attrs['readonly'] = True

        if 'entrydate' in self.fields:
            self.fields['entrydate'].widget.attrs['readonly'] = True

        # 🔢 Maxlength limits
        maxlength = {
            'patname': 50,
            'fname': 50,
            'phone': 10,
            'address': 250,
            'area': 100,
            'pincode': 6,
            'userid': 10,
        }

        for field_name, max_len in maxlength.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['maxlength'] = str(max_len)

        # 🚫 Added fix: disable autocomplete for ALL fields
        for field in self.fields.values():
            field.widget.attrs['autocomplete'] = 'off'
