document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('mortgageRatesTable');
    const tbody = table.querySelector('tbody');
    const headers = table.querySelectorAll('th.sortable');
    const bestRateHeader = document.getElementById('bestRateHeader');
    const overall30yearBestProgramHeader = document.getElementById('overall30yearBestProgramHeader');

    let sortDirection = {};
    let allRows = []; // Changed from originalRows as we're not filtering/rebuilding per filter

    // Set static header text (no more dynamic changes)
    bestRateHeader.textContent = "BEST RATE";
    overall30yearBestProgramHeader.textContent = "Overall 30Year Best Program";

    // Populate table body
    allCreditUnionsData.forEach((creditUnionData, index) => {
        let row = tbody.insertRow();
        row.dataset.rowIndex = index;

        let creditUnionCell = row.insertCell();
        creditUnionCell.textContent = creditUnionData['CreditUnion'];

        let linkCell = row.insertCell();
        let linkAnchor = document.createElement('a');
        linkAnchor.href = creditUnionData['Link'];
        linkAnchor.target = '_blank';
        linkAnchor.textContent = creditUnionData['Link'];
        linkCell.appendChild(linkAnchor);

        // Programs column (nested table)
        let programsCell = row.insertCell();
        let programsTableHtml = '<table class="program-table"><thead><tr><th>Program</th><th>Interest Rate</th></tr></thead><tbody>';
        creditUnionData.parsedRates.forEach(rate => {
            if (rate.loanTypeFull && rate.rateStr) {
                programsTableHtml += `<tr><td>${rate.loanTypeFull}</td><td>${rate.rateStr}</td></tr>`;
            }
        });
        programsTableHtml += '</tbody></table>';
        programsCell.innerHTML = programsTableHtml;

        // Overall 30Year Best Program column
        let bestProgramCell = row.insertCell();
        bestProgramCell.classList.add('dynamic-overall-30year-best-program');
        bestProgramCell.textContent = creditUnionData['OverallBestProgram'] !== 'N/A' ? creditUnionData['OverallBestProgram'] : 'None';

        // BEST RATE column
        let bestRateCell = row.insertCell();
        bestRateCell.classList.add('dynamic-best-rate');
        bestRateCell.textContent = creditUnionData['BestRate'] !== 'N/A' ? `${creditUnionData['BestRate']}%` : 'None';

        allRows.push(row);
    });

    // Initial table render (no filtering needed at start)
    // The sorting logic should still work on allRows
    headers.forEach(header => {
        const sortKey = header.dataset.sortKey;
        sortDirection[sortKey] = 'asc';
    });

    headers.forEach(header => {
        header.addEventListener('click', function () {
            const columnIndex = Array.from(header.parentNode.children).indexOf(header);
            const currentSortKey = header.dataset.sortKey;
            
            sortDirection[currentSortKey] = (sortDirection[currentSortKey] === 'asc') ? 'desc' : 'asc';

            headers.forEach(h => {
                h.classList.remove('asc', 'desc');
            });
            header.classList.add(sortDirection[currentSortKey]);

            sortTable(columnIndex, currentSortKey, sortDirection[currentSortKey]);
        });
    });

    function sortTable(columnIndex, sortKey, direction) {
        let rows = Array.from(tbody.children); // Sort all visible rows

        rows.sort((rowA, rowB) => {
            let cellA = rowA.children[columnIndex].textContent;
            let cellB = rowB.children[columnIndex].textContent;

            if (sortKey === 'bestrate') {
                let valA = parseFloat(cellA.replace(/[^\d.]/g, ''));
                let valB = parseFloat(cellB.replace(/[^\d.]/g, ''));

                valA = isNaN(valA) ? Infinity : valA;
                valB = isNaN(valB) ? Infinity : valB;

                if (direction === 'asc') {
                    return valA - valB;
                } else {
                    return valB - valA;
                }
            } else if (sortKey === 'overall30yearbestprogram') {
                return direction === 'asc' ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            } else {
                return direction === 'asc' ? cellA.localeCompare(cellB) : cellB.localeCompare(cellA);
            }
        });

        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    }

    // Call initial sort if needed, or simply populate (already done in forEach)
    // applyFilters(); // No longer needed as we removed filters
});