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
