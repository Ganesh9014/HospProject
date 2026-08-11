



from django.shortcuts import render 
from django.contrib.auth.decorators import login_required   

@login_required(login_url='login')
def PayeeMasterView(request):
    return render(request, 'hospApp/Admin/PayeeMaster.html')