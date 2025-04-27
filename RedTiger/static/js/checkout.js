// Auto-update cart quantity when dropdown changes

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('select[name="quantity"]').forEach(function(select) {
    select.addEventListener('change', function() {
      const itemId = this.getAttribute('data-item-id');
      const quantity = this.value;
      const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
      fetch(`/update_cart_quantity/${itemId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken
        },
        body: `quantity=${quantity}`
      }).then(function(response) {
        if (response.ok) {
          window.location.reload();
        }
      });
    });
  });
});