# Reglas de negocio: Tienda web: precios, carrito, stock y permisos

- **RN-C01:** los precios se calculan con `Decimal` en euros, redondeando a centimos.
- **RN-C02:** el cupon `AHORRA10` descuenta un 10 % del subtotal; `SINENVIO` elimina gastos de envio. No se acumulan cupones.
- **RN-C03:** envio de 4,95 EUR si subtotal tras descuento es inferior a 50 EUR; gratuito en otro caso.
- **RN-C04:** cantidad solicitada positiva y nunca superior al stock disponible.
- **RN-C05:** solo el propietario puede consultar los detalles privados de un pedido, salvo administrador.
- **RN-C06:** ante un pedido rechazado, el stock y el historial no deben cambiar.

