 document.addEventListener('DOMContentLoaded', function() {
  const searchInput = document.getElementById('search-input');
  const searchForm = document.getElementById('search-form');
  let searchTimeout;

  function submitForm() {
    searchForm.submit();
  }

  searchInput.addEventListener('input', function() {
    clearTimeout(searchTimeout);

    searchTimeout = setTimeout(submitForm, 500);
  });

  searchForm.addEventListener('submit', function(e) {
    e.preventDefault();
    submitForm();
  });
});