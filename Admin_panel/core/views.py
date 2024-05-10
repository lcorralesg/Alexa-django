from django.shortcuts import render
from django.http import JsonResponse
import requests

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']  # 'file' es el nombre del campo de archivo en el formulario
        response = requests.post('https://alexa-docs.onrender.com/uploadfile', files={'file': file})
        if response.status_code == 200:
            return render(request, 'upload.html', {'current_view': 'upload', 'success': True})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def index(request):
    context = {
        "title": "Panel de administración",
    }
    return render(request, 'index.html', context)

def upload(request):
    files_list = requests.get('https://alexa-docs.onrender.com/files').json()

    parsed_files = []
    for file in files_list:
        parsed_files.append({
            'id': file['id'],
            'name': file['Nombre'],
            'pages': file['Paginas'],
            'type': file['Tipo'],
            'timestamp': file['Timestamp'],
        })

    return render(request, 'upload.html', {'current_view': 'upload', 'files': parsed_files})

def dashboard(request):
    return render(request, 'dashboard.html', {'current_view': 'dashboard'})
