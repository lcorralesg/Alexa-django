from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from datetime import datetime
from collections import defaultdict
import io
import decouple
import requests

external_api_host = decouple.config('EXTERNAL_API_HOST')
external_api_port = decouple.config('EXTERNAL_API_PORT')

api_url = f'http://{external_api_host}:{external_api_port}'

month_map = {
    'January': 'Enero',
    'February': 'Febrero',
    'March': 'Marzo',
    'April': 'Abril',
    'May': 'Mayo',
    'June': 'Junio',
    'July': 'Julio',
    'August': 'Agosto',
    'September': 'Septiembre',
    'October': 'Octubre',
    'November': 'Noviembre',
    'December': 'Diciembre'
    }

def get_files():
    files_list = requests.get(f'{api_url}/files').json()
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
        response = requests.post(f'{api_url}/uploadfile', files=files)
        # file_list = get_files()
        if response.status_code == 200:
            messages.success(request, 'Archivo subido correctamente')
            return redirect('upload')
        if response.status_code == 400:
            messages.error(request, 'El nombre del archivo ya existe')
            return redirect('upload')
  
def delete_file(request, file_id):
    if request.method == 'POST':
        response = requests.post(f'{api_url}/delete_file_vectors/{file_id}')
        if response.status_code == 200:
            messages.success(request, 'Archivo eliminado correctamente')
            return redirect('upload')
    else:
        return JsonResponse({'error': 'Método no permitido'}, status=405)

def downloadfile(request, filename):
    response = requests.get(f'{api_url}/downloadfile/{filename}')
    if response.status_code == 200:
        return FileResponse(io.BytesIO(response.content), as_attachment=True, filename=filename)
    else:
        return JsonResponse({'error': 'Archivo no encontrado'}, status=404)

def index(request):
    context = {
        "title": "Panel de administración",
    }
    return render(request, 'index.html', context)

@login_required
def upload(request):
    files = get_files()
    return render(request, 'upload.html', 
                  {'current': 'upload',
                    'files': files,
                    'title': 'Subir archivos'})

@login_required
def questions(request):
    questions_list = requests.get(f'{api_url}/questions').json()

    return render(request, 'questions.html', {
        'current': 'questions',
        'questions': questions_list,
        'title': 'Preguntas',
    })

@login_required
def ratings(request):
    ratings_list = requests.get(f'{api_url}/ratings').json()

    parsed_ratings = []
    for rating in ratings_list:
        stars = ['star'] * rating['Puntuacion']
        unfilled_stars = ['star_border'] * (5 - rating['Puntuacion'])
        parsed_ratings.append({
            'Estrellas': stars,
            'Fecha_Hora': rating['Timestamp'],
            'Estrellas_vacias': unfilled_stars,
        })

    return render(request, 'ratings.html', {
        'current': 'ratings',
        'ratings': parsed_ratings,
        'title': 'Calificaciones',
    })

@login_required
def dashboard(request):
    questions_list = requests.get(f'{api_url}/questions').json()

    rating_list = requests.get(f'{api_url}/ratings').json()

    questions_list.reverse()
    rating_list.reverse()

    que_x_axis = []
    que_y_axis = []

    for question in questions_list:
        question_date = datetime.strptime(question['Timestamp'], '%d-%m-%Y %H:%M')
        month = question_date.strftime('%B').capitalize()
        translation_q = month_map[month]
        if translation_q not in que_x_axis:
            que_x_axis.append(translation_q)
            que_y_axis.append(1)
        else:
            que_y_axis[que_x_axis.index(translation_q)] += 1

    ra_x_axis = []
    ra_y_axis = []

    ratings = defaultdict(lambda: {'sum': 0, 'count': 0})

    for rating in rating_list:
        rating_date = datetime.strptime(rating['Timestamp'], '%d-%m-%Y %H:%M')
        month = rating_date.strftime('%B').capitalize()
        ratings[month]['sum'] += rating['Puntuacion']
        ratings[month]['count'] += 1
    
    translated_ratings = {month_map[month]: ratings[month] for month in ratings}
    ra_x_axis = list(translated_ratings.keys())
    ra_y_axis = [round(translated_ratings[month]['sum'] / translated_ratings[month]['count'], 2) if translated_ratings[month]['count'] != 0 else 0 for month in ra_x_axis]
    ra_y_axis = [str(rating).replace(',', '.') for rating in ra_y_axis]

    return render(request, 'dashboard.html', {
        'current': 'dashboard',
        'que_x_axis': que_x_axis,
        'que_y_axis': que_y_axis,
        'ra_x_axis': ra_x_axis,
        'ra_y_axis': ra_y_axis,
        'title': 'Panel de control',
    })