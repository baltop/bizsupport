// Check the pagination HTML structure
console.log("=== PAGINATION ANALYSIS ===");
console.log("Current URL:", location.href);

// Find pagination container
const paginationContainer = document.querySelector('.pagination, .paging, [class*="page"]');
if (paginationContainer) {
  console.log("Pagination container found:", paginationContainer.className);
} else {
  console.log("No pagination container found, checking all links with #");
}

// Check all links with href="#"
const hashLinks = document.querySelectorAll('a[href="#"]');
console.log("Found", hashLinks.length, "links with href='#'");

hashLinks.forEach((link, index) => {
  console.log(`Link ${index}:`, link.textContent.trim(), link.getAttribute("onclick"));
});

// Check forms
const forms = document.querySelectorAll('form');
console.log("Found", forms.length, "forms");
forms.forEach((form, index) => {
  console.log(`Form ${index}:`, form.action, form.method);
  const formInputs = form.querySelectorAll('input');
  formInputs.forEach(input => {
    console.log(`  Input: ${input.name} = ${input.value} (type: ${input.type})`);
  });
});

// Try to navigate to page 3 by examining JavaScript functions
console.log("Checking for global functions:");
console.log("- goPage:", typeof goPage);
console.log("- pageMove:", typeof pageMove);
console.log("- movePage:", typeof movePage);
console.log("- fn_pageing:", typeof fn_pageing);
console.log("- fn_paging:", typeof fn_paging);

// Look for any form submission or AJAX calls
window.addEventListener('beforeunload', () => {
  console.log("Page unloading, new URL will be:", location.href);
});