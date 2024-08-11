from .models import ThemeConfiguration

def theme(request):
    if request.user.is_authenticated:
        theme_config = ThemeConfiguration.objects.filter(user=request.user).first()
        theme = theme_config.theme if theme_config else 'light'
    else:
        theme = 'light'
    return {'theme': theme}
