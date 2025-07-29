// Integración con Mercado Pago
document.addEventListener('DOMContentLoaded', function() {
    console.log("Mercado Pago script loaded");
    
    // Obtenemos los elementos del DOM necesarios
    const checkoutBtn = document.getElementById('checkout-btn');
    const paymentSelect = document.getElementById('payment-method');
    
    if (!checkoutBtn || !paymentSelect) {
        console.error("No se encontraron los elementos necesarios para la integración con Mercado Pago");
        return;
    }
    
    console.log("Elementos encontrados", { checkoutBtn, paymentSelect });
    
    // Guardamos la referencia al manejador original
    const originalCheckoutClick = checkoutBtn.onclick;
    
    // Reemplazamos el comportamiento del botón
    checkoutBtn.onclick = function(event) {
        // Solo interceptamos si el método de pago es Mercado Pago
        if (paymentSelect.value === 'mercadopago') {
            event.preventDefault();
            event.stopPropagation();
            handleMercadoPagoCheckout();
            return false;
        }
        
        // Para otros métodos de pago, usamos el comportamiento normal
        return true;
    };
    
    // Función para manejar el checkout con Mercado Pago
    async function handleMercadoPagoCheckout() {
        console.log("Procesando pago con Mercado Pago");
        
        // Creamos el payload de la orden
        const payload = {
            items: cart.map(i => ({ producto_id: i.producto_id, cantidad: i.cantidad })),
            metodo_pago: 'mercadopago'
        };
        
        try {
            // Mostramos indicador de carga
            checkoutBtn.disabled = true;
            checkoutBtn.textContent = 'Procesando...';
            
            // Enviamos la orden al servidor
            const res = await fetch('/pos/order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            if (res.ok) {
                const orderData = await res.json();
                console.log("Orden creada:", orderData);
                
                // Procesamos el pago con Mercado Pago
                await processMercadoPagoPayment(orderData.id);
            } else {
                const err = await res.json();
                alert("❌ " + (err.detail || "Error al crear la orden"));
                // Reactivamos el botón
                checkoutBtn.disabled = false;
                checkoutBtn.textContent = 'Cobrar';
            }
        } catch (error) {
            console.error("Error en el checkout:", error);
            alert("❌ Error al procesar la orden: " + error.message);
            // Reactivamos el botón
            checkoutBtn.disabled = false;
            checkoutBtn.textContent = 'Cobrar';
        }
    }
    
    // Función para procesar pago con Mercado Pago
    async function processMercadoPagoPayment(ordenId) {
        console.log("Procesando pago con Mercado Pago para orden:", ordenId);
        
        try {
            const res = await fetch('/pos/process-payment-mp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ orden_id: ordenId })
            });
            
            if (res.ok) {
                const mpData = await res.json();
                console.log("Preferencia de pago creada:", mpData);
                
                // Verificar que mpData tenga los campos esperados
                if (!mpData.init_point) {
                    console.error("Error: La respuesta no contiene el campo init_point:", mpData);
                    alert("❌ Error: La URL de pago no está disponible. Contacte al administrador.");
                    checkoutBtn.disabled = false;
                    checkoutBtn.textContent = 'Cobrar';
                    return;
                }
                
                // Redirigir al checkout de Mercado Pago
                console.log("Redirigiendo a:", mpData.init_point);
                
                // Usamos window.open para abrir en una nueva pestaña
                // lo que suele funcionar mejor para evitar bloqueos de popups
                window.open(mpData.init_point, "_blank");
            } else {
                const err = await res.json();
                alert("❌ Error al procesar pago con Mercado Pago: " + (err.detail || "Error desconocido"));
                // Reactivamos el botón
                checkoutBtn.disabled = false;
                checkoutBtn.textContent = 'Cobrar';
            }
        } catch (error) {
            console.error("Error en la integración con Mercado Pago:", error);
            alert("❌ Error en la integración con Mercado Pago: " + error.message);
            // Reactivamos el botón
            checkoutBtn.disabled = false;
            checkoutBtn.textContent = 'Cobrar';
        }
    }
    
    console.log("Integración de Mercado Pago configurada correctamente");
});