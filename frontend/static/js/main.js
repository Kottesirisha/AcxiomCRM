document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
            overlay.classList.toggle('show');
        });
    }
    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('show');
            overlay.classList.remove('show');
        });
    }

    // Auto-dismiss alerts
    document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
        setTimeout(function() { try { new bootstrap.Alert(alert).close(); } catch(e){} }, 5000);
    });

    // Delete confirmation modals
    document.querySelectorAll('[data-delete-url]').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.getAttribute('data-delete-url');
            const name = this.getAttribute('data-delete-name') || 'this item';
            const modal = document.getElementById('deleteModal');
            if (modal) {
                modal.querySelector('#deleteForm').action = url;
                modal.querySelector('#deleteItemName').textContent = name;
                new bootstrap.Modal(modal).show();
            }
        });
    });

    // Opportunity stage -> probability auto-set
    const stageSelect = document.getElementById('stage');
    const probInput = document.getElementById('probability');
    if (stageSelect && probInput) {
        const stageProb = {'Qualification':10,'Needs Analysis':25,'Proposal':50,'Negotiation':75,'Closed Won':100,'Closed Lost':0};
        stageSelect.addEventListener('change', function() {
            if (stageProb[this.value] !== undefined) probInput.value = stageProb[this.value];
        });
    }

    // Lead conversion toggle
    const createOpp = document.getElementById('create_opportunity');
    const oppFields = document.getElementById('opportunityFields');
    if (createOpp && oppFields) {
        createOpp.addEventListener('change', function() {
            oppFields.style.display = this.checked ? 'block' : 'none';
        });
    }

    // Format currency
    document.querySelectorAll('.currency').forEach(function(el) {
        const val = parseFloat(el.textContent);
        if (!isNaN(val)) el.textContent = '$' + val.toLocaleString('en-US', {minimumFractionDigits:2, maximumFractionDigits:2});
    });
});
