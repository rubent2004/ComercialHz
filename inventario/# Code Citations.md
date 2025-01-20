# Code Citations

## License: desconocido
https://github.com/sneikerdiaz/Donde_El_Compay/tree/9ec881fd559fb1361d6435a42bf4455378b0cfb0/sistema/inventario/models.py

```
(max_length=80, unique=True)
    password = models.CharField(max_length=20)
    email = models.EmailField(max_length=100, unique=True)
    first_name = models.CharField(max_length=40)
    last_name = models.CharField(max_length=60)
    nivel =
```


## License: desconocido
https://github.com/jramos2020/proyectopython/tree/5980e28fd87c4fbe90d3be95231db7ba8c288508/appdiverxia/models.py

```
(objetos):
            arreglo.append([])
            if etiqueta:
                arreglo[indice].append(0)
                arreglo[indice].append("------")
                etiqueta = False
                arreglo.append([])

            arreglo[indice + extra].append(objeto.
```


## License: desconocido
https://github.com/estebancsi/cv_stock/tree/ebcaf7d139cddd1010d1e4dc6c361749c3f689c3/inventario/models.py

```
DetalleFactura(models.Model):
    id_factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    id_producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    sub_total = models.DecimalField(max_digits=20, decimal_places=2
```

