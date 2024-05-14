from django.shortcuts import render
from django.http import JsonResponse
import requests
from django.contrib import messages

def get_files():
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
    return parsed_files

def upload_file(request):
    if request.method == 'POST':
        file = request.FILES['file']  # 'file' es el nombre del campo de archivo en el formulario
        files = {'file': (file.name, file, file.content_type)}
        response = requests.post('https://alexa-docs.onrender.com/uploadfile', files=files)
        file_list = get_files()
        if response.status_code == 200:
            messages.success(request, 'Archivo subido correctamente')
            return render(request, 'upload.html', {'current': 'upload', 'files': file_list})
        if response.status_code == 400:
            messages.error(request, 'El nombre del archivo ya existe')
            return render(request, 'upload.html', {'current': 'upload', 'files': file_list})
    
def delete_file(request, file_id):
    if request.method == 'POST':
        response = requests.post(f'https://alexa-docs.onrender.com/delete_file_vectors/{file_id}')
        if response.status_code == 200:
            file_list = get_files()
            return render(request, 'upload.html', {'current': 'upload', 'delete_success': True, 'files': file_list})
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def index(request):
    context = {
        "title": "Panel de administración",
    }
    return render(request, 'index.html', context)

def upload(request):
    files = get_files()
    return render(request, 'upload.html', 
                  {'current': 'upload',
                    'files': files,
                    'title': 'Subir archivos'})

def dashboard(request):
    questions_list = requests.get('https://alexa-docs.onrender.com/questions/').json()

    parsed_questions = []
    for question in questions_list:
        parsed_questions.append({
            'Pregunta': question['Pregunta'],
            'Timestamp': question['Timestamp'],
        })

    ratings_list = requests.get('https://alexa-docs.onrender.com/ratings/').json()

    parsed_ratings = []
    for rating in ratings_list:
        stars = ['star'] * rating['Puntuacion']
        unfilled_stars = ['star_border'] * (5 - rating['Puntuacion'])
        parsed_ratings.append({
            'Estrellas': stars,
            'Fecha_Hora': rating['Timestamp'],
            'Estrellas_vacias': unfilled_stars,
        })

    return render(request, 'dashboard.html', {
        'current': 'dashboard',
        'questions': parsed_questions,
        'ratings': parsed_ratings,
        'title': 'Dashboard',
    })