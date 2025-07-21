// /static/js/datatable.js
import { DataTable } from "https://cdn.jsdelivr.net/npm/simple-datatables@latest";

const table = document.getElementById("products-table");
const dataTable = new DataTable(table, {
  searchable: true,
  fixedHeight: true
});

// Filtrar por stock
document.querySelectorAll("button[data-filter]").forEach(btn => {
  btn.addEventListener("click", () => {
    const filter = btn.dataset.filter;
    dataTable.rows().forEach(row => {
      const stock = row.node().dataset.stock;
      row.show(filter === "all" || stock === filter);
    });
  });
});
