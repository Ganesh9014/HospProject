from django import forms
from hospApp.models import Employee, tblRoles

class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Password'})
    )


class EmployeeForm(forms.ModelForm):
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
    designation = forms.ModelChoiceField(
        queryset=tblRoles.objects.filter(mainrole='yes'),
        empty_label="Select Designation",
        label="Designation",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Employee
        fields = [
            'emp_id', 'emp_name', 'designation', 'age', 'doj',
            'address', 'phone'
        ]

        widgets = {
            'emp_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employee ID',
                'readonly': True        
            }),
            'emp_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Employee Name',
                'maxlength': '30',
                'oninput': 'if(this.value.length>30)this.value=this.value.slice(0,30);'
            }),
            'age': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Age',
                'oninput': 'if(this.value.length>3)this.value=this.value.slice(0,3);'
            }),
            'doj': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control textarea',
                'rows': 2,
                'placeholder': 'Address',
                'maxlength': '100', 
                'oninput': 'if(this.value.length>100)this.value=this.value.slice(0,100);'
                
            }),
            'phone': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number',
                'oninput': 'if(this.value.length>10)this.value=this.value.slice(0,10);'
            }),
        }
