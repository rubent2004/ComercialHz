from django.utils import timezone
import zoneinfo

# Activa manualmente la zona horaria de El Salvador
timezone.activate(zoneinfo.ZoneInfo("America/El_Salvador"))

# Ahora debería reflejar correctamente la zona horaria
print("Fecha UTC:", timezone.now())  # Fecha en UTC
print("Fecha local:", timezone.localtime(timezone.now()))  # Fecha en hora local
print("Zona horaria actual:", timezone.get_current_timezone())  # Debe mostrar America/El_Salvador
