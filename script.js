function fetchData() {
    fetch('/get_estoque_data')
        .then(response => response.json())
        .then(data => {
            const dataTable = document.getElementById('data-table');
            const tbody = dataTable.getElementsByTagName('tbody')[0];
            tbody.innerHTML = '';

            data.forEach(row => {
                const tr = document.createElement('tr');

                const idCell = document.createElement('td');
                idCell.textContent = row['id'];
                tr.appendChild(idCell);

                const nomeCell = document.createElement('td');
                nomeCell.textContent = row['nome'];
                tr.appendChild(nomeCell);

                const descricaoCell = document.createElement('td');
                descricaoCell.textContent = row['descricao'];
                tr.appendChild(descricaoCell);

                const quantidadeCell = document.createElement('td');
                quantidadeCell.textContent = row['quantidade'];
                tr.appendChild(quantidadeCell);

                const actionsCell = document.createElement('td');

                const editButton = document.createElement('button');
                editButton.textContent = 'Editar';
                editButton.className = 'edit-button';
                editButton.onclick = () => editRow(row['id']);
                actionsCell.appendChild(editButton);

                const deleteButton = document.createElement('button');
                deleteButton.textContent = 'Excluir';
                deleteButton.className = 'delete-button';
                deleteButton.onclick = () => deleteRow(row['id']);
                actionsCell.appendChild(deleteButton);

                tr.appendChild(actionsCell);

                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Erro ao buscar dados do estoque:', error);
        });
}

function search() {
    const searchInput = document.getElementById('search-input');
    const searchText = searchInput.value.trim().toLowerCase();

    const dataTable = document.getElementById('data-table');
    const rows = dataTable.getElementsByTagName('tr');

    for (let i = 1; i < rows.length; i++) {
        const row = rows[i];
        const cells = row.getElementsByTagName('td');
        let match = false;

        for (let j = 0; j < cells.length - 1; j++) {
            const cell = cells[j];
            const text = cell.textContent.trim().toLowerCase();

            if (text.includes(searchText)) {
                match = true;
                break;
            }
        }

        row.style.display = match ? '' : 'none';
    }
}

function editRow(id) {
    window.location.href = '/editar_estoque/' + id;
}

function deleteRow(id) {
    if (confirm('Deseja excluir este registro?')) {
        fetch('/excluir_estoque', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ id: id })
        })
            .then(response => response.json())
            .then(result => {
                if (result.success) {
                    alert('Registro excluído com sucesso!');
                    fetchData();
                } else {
                    alert('Erro ao excluir registro.');
                }
            })
            .catch(error => {
                console.error('Erro ao excluir registro:', error);
            });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    fetchData();
});
