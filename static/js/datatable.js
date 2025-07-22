// /static/js/datatable.js
// Versión actualizada sin importaciones

// Esperamos a que el DOM esté completamente cargado
document.addEventListener("DOMContentLoaded", () => {
  // Buscamos la tabla de productos
  const table = document.getElementById("products-table");
  
  // Si la tabla existe, inicializamos DataTable
  if (table) {
    try {
      // Creamos una nueva instancia de DataTable
      const dataTable = new simpleDatatables.DataTable(table, {
        searchable: true,
        fixedHeight: true,
        perPage: 10
      });

      console.log("DataTable inicializada correctamente");

      // Filtrar por stock si existen botones de filtro
      const filterButtons = document.querySelectorAll("button[data-filter]");
      if (filterButtons.length > 0) {
        filterButtons.forEach(btn => {
          btn.addEventListener("click", () => {
            const filter = btn.dataset.filter;
            dataTable.rows().forEach(row => {
              const stock = row.node().dataset.stock;
              row.show(filter === "all" || stock === filter);
            });
          });
        });
      }
    } catch (error) {
      console.error("Error al inicializar DataTable:", error);
    }
  } else {
    // No hacemos nada si la tabla no existe en esta página
  }
});
