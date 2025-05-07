// Auto-update cart quantity when dropdown changes

document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('select[name="quantity"]').forEach(function(select) {
    select.addEventListener('change', function() {
      const itemId = this.getAttribute('data-item-id');
      const quantity = this.value;
      const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]')?.value;
      // Find the price per unit for this item
      const priceSpan = this.closest('li').querySelector('.text-body-secondary');
      const pricePerUnit = parseFloat(priceSpan.getAttribute('data-price-per-unit'));
      // Update item price
      priceSpan.textContent = `$${(pricePerUnit * quantity).toFixed(2)}`;
      // Update total
      let total = 0;
      document.querySelectorAll('select[name="quantity"]').forEach(function(qSelect) {
        const q = parseInt(qSelect.value);
        const pSpan = qSelect.closest('li').querySelector('.text-body-secondary');
        const pPerUnit = parseFloat(pSpan.getAttribute('data-price-per-unit'));
        total += q * pPerUnit;
      });
      const totalElem = document.querySelector('li.list-group-item.d-flex.justify-content-between strong');
      if (totalElem) {
        totalElem.textContent = `$${total.toFixed(2)}`;
      }
      fetch(`/update_cart_quantity/${itemId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken
        },
        body: `quantity=${quantity}`
      });
    });
  });
});