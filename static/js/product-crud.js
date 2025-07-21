// static/js/product-crud.js

const btn = document.getElementById("submit-btn");
const spinner = document.getElementById("btn-spinner");
const btnText = document.getElementById("btn-text");

async function uploadAndSubmitProduct(form) {
  btn.disabled = true;
  spinner.classList.remove("hidden");
  btnText.textContent = "Cargando...";

  try {
    const nombre = form.nombre.value.trim();
    const descripcion = form.descripcion.value.trim();
    const precio = parseFloat(form.precio.value);
    const file = document.getElementById("image-input")?.files[0];
    let imageKey;

    if (file) {
      const filename = `${nombre.replace(/\s+/g, "_")}.webp`;
      const presigned = await fetch(`/upload/presigned-url?filename=${filename}`);
      if (!presigned.ok) throw new Error("Error al obtener URL de imagen");
      const { url, key } = await presigned.json();

      const uploadRes = await fetch(url, {
        method: "PUT",
        headers: { "Content-Type": "image/webp" },
        body: file
      });
      if (!uploadRes.ok) throw new Error("Error al subir imagen");
      imageKey = key;
    }

    const action = form.getAttribute("action");
    const method = form.getAttribute("method") || "POST";
    const payload = { nombre, descripcion, precio, ...(imageKey && { image_key: imageKey }) };

    const res = await fetch(action, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Error procesando producto");
    }

    window.location = "/web/productos";
  } catch (error) {
    alert(error.message);
  } finally {
    btnText.textContent = "Crear";
    spinner.classList.add("hidden");
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("product-form");
  if (form) {
    form.addEventListener("submit", e => {
      e.preventDefault();
      uploadAndSubmitProduct(form);
    });
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
      if (data.cantidad > 0) {
        span.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800";
        span.textContent = `${data.cantidad} unidades`;
      } else {
        span.className = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800";
        span.textContent = "Sin stock";
      }
    } else {
      alert("Error al actualizar stock");
    }
  } catch (err) {
    console.error(err);
    alert("Error de red");
  }
} 