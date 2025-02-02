from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest
from functools import wraps

def nivel_requerido(nivel_minimo):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_or_request, *args, **kwargs):
            if isinstance(view_or_request, HttpRequest):
                request = view_or_request  # FBV
            elif hasattr(view_or_request, 'request'):
                request = view_or_request.request  # CBV
            else:
                raise ValueError("No se pudo determinar el objeto request")

            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder a esta página.')
                return redirect('inventario:login')

            if not hasattr(request.user, 'nivel') or request.user.nivel is None:
                messages.error(request, 'Tu cuenta no tiene un nivel asignado.')
                return redirect('inventario:panel')

            if request.user.nivel < nivel_minimo:
                messages.error(request, 'No tienes permisos suficientes para acceder a esta página.')
                return redirect('inventario:panel')

            return view_func(view_or_request, *args, **kwargs)

        return _wrapped_view
    return decorator
