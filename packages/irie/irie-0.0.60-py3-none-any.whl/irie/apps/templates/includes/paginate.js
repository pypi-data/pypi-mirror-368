//===----------------------------------------------------------------------===#
//
//         STAIRLab -- STructural Artificial Intelligence Laboratory
//
//===----------------------------------------------------------------------===#
//
class TablePagination {

    constructor(tableId, paginationId, searchInputId, rowsPerPage = 9) {
        this.table = document.getElementById(tableId);
        this.pagination = document.getElementById(paginationId);
        this.searchInput = document.getElementById(searchInputId);
        this.rowsPerPage = rowsPerPage;
        this.tbody = this.table.getElementsByTagName('tbody')[0];
        this.rows = this.tbody.getElementsByTagName('tr');
        this.rowsCount = this.rows.length;
        this.pageCount = Math.ceil(this.rowsCount / this.rowsPerPage);
        this.currentPage = 1;
        this.init();
    }

    displayRows(page) {
        const start = (page - 1) * this.rowsPerPage;
        const end = start + this.rowsPerPage;
        for (let i = 0; i < this.rowsCount; i++) {
            this.rows[i].style.display = (i >= start && i < end) ? '' : 'none';
        }
    }

    setupPagination() {
        this.pagination.innerHTML = '';
        const prevLi = document.createElement('li');
        prevLi.className = 'page-item';
        prevLi.innerHTML = `<a class="page-link" href="#">Previous</a>`;
        prevLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.currentPage > 1) {
                this.currentPage--;
                this.displayRows(this.currentPage);
                this.setupPagination();
            }
        });
        this.pagination.appendChild(prevLi);

        const startPage = Math.max(1, this.currentPage - 1);
        const endPage = Math.min(this.pageCount, startPage + 2);

        for (let i = startPage; i <= endPage; i++) {
            const li = document.createElement('li');
            li.className = 'page-item';
            li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
            li.addEventListener('click', (e) => {
                e.preventDefault();
                this.currentPage = i;
                this.displayRows(this.currentPage);
                this.setupPagination();
            });
            if (i === this.currentPage) {
                li.classList.add('active');
            }
            this.pagination.appendChild(li);
        }

        const nextLi = document.createElement('li');
        nextLi.className = 'page-item';
        nextLi.innerHTML = `<a class="page-link" href="#">Next</a>`;
        nextLi.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.currentPage < this.pageCount) {
                this.currentPage++;
                this.displayRows(this.currentPage);
                this.setupPagination();
            }
        });
        this.pagination.appendChild(nextLi);
    }

    sortTable(columnIndex) {
        const rowsArray = Array.from(this.rows);
        const isAscending = this.table.querySelectorAll('th')[columnIndex].classList.toggle('asc');
        rowsArray.sort((a, b) => {
            const cellA = a.getElementsByTagName('td')[columnIndex].innerText;
            const cellB = b.getElementsByTagName('td')[columnIndex].innerText;
            return isAscending ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
        });
        rowsArray.forEach(row => this.tbody.appendChild(row));
        this.displayRows(this.currentPage);
    }

    filterRows() {
        const filter = this.searchInput.value.toLowerCase();
        Array.from(this.rows).forEach(row => {
            const cells = row.getElementsByTagName('td');
            const match = Array.from(cells).some(cell => cell.innerText.toLowerCase().includes(filter));
            row.style.display = match ? '' : 'none';
        });
    }

    init() {
        this.displayRows(this.currentPage);
        this.setupPagination();
        const headers = this.table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.addEventListener('click', () => this.sortTable(index));
        });
        this.searchInput.addEventListener('input', () => this.filterRows());
    }
}
