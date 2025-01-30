from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def nivel_requerido(nivel_minimo):
    """
    Decorador compatible con vistas basadas en clases y funciones.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_or_request, *args, **kwargs):
            # Determinar si es una vista basada en clase
            request = getattr(view_or_request, 'request', view_or_request)
            
            if not request.user.is_authenticated:
                return redirect('inventario:login')
                
            if request.user.nivel < nivel_minimo:
                messages.error(request, 'Permisos insuficientes')
                return redirect('inventario:panel')
            
            return view_func(view_or_request, *args, **kwargs)
        return _wrapped_view
    return decorator