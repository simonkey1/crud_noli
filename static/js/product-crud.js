// static/js/product-crud.js

// Inicializamos estas variables solo cuando sean necesarias para evitar errores
// si los elementos no existen en todas las páginas
let btn, spinner, btnText;

function resetButton() {
  if (btnText) btnText.textContent = "Crear";
  if (spinner) spinner.classList.add("hidden");
  if (btn) btn.disabled = false;
}

async function uploadAndSubmitProduct(form) {
  console.log("Iniciando uploadAndSubmitProduct con:", form);
  
  // Verificamos que form sea un elemento de formulario válido
  if (!(form instanceof HTMLFormElement)) {
    console.error("El objeto form no es una instancia de HTMLFormElement:", form);
    alert("Error: Formulario no válido");
    return;
  }
  
  // Inicializamos los elementos UI solo cuando vamos a usarlos
  btn = document.getElementById("submit-btn");
  spinner = document.getElementById("btn-spinner");
  btnText = document.getElementById("btn-text");
  
  if (!btn || !spinner || !btnText) {
    console.error("No se encontraron los elementos del botón de submit");
    return;
  }
  
  console.log("Elementos UI encontrados, cambiando estado del botón...");
  btn.disabled = true;
  spinner.classList.remove("hidden");
  btnText.textContent = "Cargando...";

  try {
    // Verificamos que el formulario tenga todos los campos necesarios
    const formData = new FormData(form);
    console.log("FormData creado, revisando campos requeridos...");
    
    // Verificamos que existan los campos obligatorios según el backend
    const nombreValue = formData.get('nombre');
    const precioValue = formData.get('precio');
    const cantidadValue = formData.get('cantidad');
    const codigoBarraValue = formData.get('codigo_barra');
    const categoriaIdValue = formData.get('categoria_id');
    
    console.log("Valores del formulario:", {
      nombre: nombreValue,
      precio: precioValue,
      cantidad: cantidadValue,
      codigo_barra: codigoBarraValue,
      categoria_id: categoriaIdValue,
      imagen: formData.get('imagen')?.name || 'No seleccionada'
    });
    
    if (!nombreValue || !precioValue) {
      throw new Error("Faltan campos obligatorios: nombre y precio son requeridos");
    }
    
    // No es necesario manipular FormData, el servidor FastAPI espera un formulario
    // multipart/form-data con los campos y la imagen tal como está
    const action = form.getAttribute("action");
    const method = form.getAttribute("method") || "POST";
    
    console.log("Enviando formulario a:", action, "con método:", method);
    
    // Aquí simplemente enviamos el formulario como es, ya que FastAPI
    // espera un FormData con los campos y la imagen
    form.submit();
    
    // No necesitamos manejar la redirección, el formulario lo hará automáticamente
    return;
  } catch (error) {
    console.error("Error en el proceso:", error);
    
    // Mostrar un mensaje de error más descriptivo
    let errorMsg = "Error al procesar el producto";
    if (error && error.message) {
      errorMsg = error.message;
    }
    
    alert(errorMsg);
    resetButton();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("product-form");
  if (form) {
    console.log("Formulario de producto encontrado, agregando listener...");
    
    // Verificar que todos los campos estén presentes
    const requiredFields = ['nombre', 'precio', 'cantidad', 'codigo_barra', 'categoria_id'];
    const missingFields = requiredFields.filter(field => !form.elements[field]);
    
    if (missingFields.length > 0) {
      console.warn("Campos faltantes en el formulario:", missingFields.join(", "));
    }
    
    form.addEventListener("submit", e => {
      e.preventDefault();
      console.log("Formulario enviado, iniciando proceso de subida...");
      console.log("Datos del formulario:", {
        nombre: form.nombre?.value || 'No disponible',
        precio: form.precio?.value || 'No disponible',
        cantidad: form.cantidad?.value || 'No disponible',
        codigo_barra: form.codigo_barra?.value || 'No disponible',
        categoria_id: form.categoria_id?.value || 'No disponible',
        imagen: form.imagen?.files[0]?.name || 'No seleccionada'
      });
      uploadAndSubmitProduct(form);
    });
  } else {
    console.log("Formulario de producto no encontrado en esta página");
  }
});

async function updateStock(productId, delta) {
  try {
    const response = await fetch(`/productos/${productId}/stock`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ delta })
    });

    if (response.ok) {
      const data = await response.json();
      const span = document.getElementById(`stock-${productId}`);
      const umbralElement = document.getElementById(`umbral-${productId}`);
      // Usamos el umbral_stock que viene de la respuesta del servidor, o el valor del elemento oculto como respaldo
      const umbral = data.umbral_stock !== undefined ? data.umbral_stock : 
                     umbralElement ? parseInt(umbralElement.value) : 5;
      
      if (data.cantidad <= 0) {
        // Sin stock
        span.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-800/30 dark:text-red-300";
        span.textContent = "Sin stock";
      } else if (data.cantidad <= umbral) {
        // Stock bajo (por debajo o igual al umbral)
        span.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800 dark:bg-amber-800/30 dark:text-amber-300";
        span.textContent = `${data.cantidad} unidades (bajo)`;
      } else {
        // Stock normal (por encima del umbral)
        span.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300";
        span.textContent = `${data.cantidad} unidades`;
      }
    } else {
      alert("Error al actualizar stock");
    }
  } catch (err) {
    console.error(err);
    alert("Error de red");
  }
}