from .models import Inventario

class EntregaService:
    def __init__(self, idbodega):
        self.idbodega = idbodega
        self.stock_disponible = self.cargar_stock()

    def cargar_stock(self):
        """
        Carga el stock inicial de la bodega en memoria para evitar múltiples consultas.
        """
        inventario = Inventario.objects.filter(idbodega=self.idbodega)
        return {item.idproducto.id: item.stock for item in inventario}

    def verificar_stock(self, idproducto, cantidad):
        """
        Verifica si hay stock suficiente en memoria antes de confirmar la entrega.
        """
        return self.stock_disponible.get(idproducto, 0) >= cantidad

    def actualizar_stock_temporal(self, idproducto, cantidad, operacion='reducir'):
        """
        Ajusta temporalmente el stock en memoria antes de confirmarlo en la base de datos.
        """
        if operacion == 'reducir':
            if self.verificar_stock(idproducto, cantidad):
                self.stock_disponible[idproducto] -= cantidad
                return True
            return False
        elif operacion == 'aumentar':
            self.stock_disponible[idproducto] += cantidad
            return True
        return False