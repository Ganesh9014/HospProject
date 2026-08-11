from django import forms
from hospApp.models import Employee, tblRoles, Tbluserpermission

class UserPermissionForm(forms.ModelForm):

    mainrole = forms.ModelChoiceField(
        queryset=tblRoles.objects.filter(mainrole='yes'),  # now includes custom roles too
        widget=forms.RadioSelect,
        label="Role",
        required=True
    )

    emp = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        label="Employee ID",
        empty_label="Please Select",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    department = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False
    )

    re_password = forms.CharField(
        label="Re-enter Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        max_length=50,
        required=False
    )

    class Meta:
        model = Tbluserpermission
        fields = ['emp', 'username', 'password', 'isactive', 'app_permission', 'mainrole', 'department']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter username',
            }),
            'isactive': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'app_permission': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_existing = False

    def validate_unique(self):
        is_existing = getattr(self, 'is_existing', False)
        if is_existing:
            exclude = self._get_validation_exclusions()
            exclude.add('username')
            try:
                self.instance.validate_unique(exclude=exclude)
            except forms.ValidationError:
                pass
        else:
            super().validate_unique()

    def clean(self):
        cleaned_data = super().clean()
        password     = cleaned_data.get("password")
        re_password  = cleaned_data.get("re_password")
        is_existing  = getattr(self, 'is_existing', False)

        if not is_existing:
            if not password:
                self.add_error('password', 'Password is required.')
            if not re_password:
                self.add_error('re_password', 'Please re-enter your password.')
            if password and re_password and password != re_password:
                raise forms.ValidationError("Passwords do not match!")

        return cleaned_data