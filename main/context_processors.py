from .models import Category
 
def categories(request):
    """Add categories to context of all templates"""
    return {
        'categories': Category.objects.all()
    } 