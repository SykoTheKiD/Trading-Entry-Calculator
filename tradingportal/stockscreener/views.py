from django.shortcuts import render
from calculator.value_investing import main


def index(request):
    # context = main("aapl")
    return render(request, 'index.html', context=dict())


