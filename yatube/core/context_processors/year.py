
from datetime import date


def year(request):
    year_today = date.today().year
    return {
        'year': year_today,
    }
