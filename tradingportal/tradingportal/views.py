from django.shortcuts import render


def index(request):
    context = {'name': 'Tiger Woods'}
    return render(request, 'index.html', context)
