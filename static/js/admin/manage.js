// manage.js - Handles delete confirmation for admin content

document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.btn-delete').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const id = btn.getAttribute('data-id');
            if (confirm('Are you sure you want to delete this item?')) {
                fetch(`/admin/delete/${id}`, {
                    method: 'POST',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' }
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } else {
                        alert(data.error || 'Delete failed');
                    }
                });
            }
        });
    });
});
