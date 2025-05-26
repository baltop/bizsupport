console.log("Current URL:", location.href);

// Check pagination form
const paginationForm = document.querySelector("form");
if (paginationForm) {
  console.log("Form action:", paginationForm.action);
  console.log("Form method:", paginationForm.method);
  
  // Look for hidden inputs that might contain page info
  const inputs = paginationForm.querySelectorAll("input");
  inputs.forEach(input => {
    console.log("Input:", input.name, "=", input.value, "type:", input.type);
  });
}

// Check for any JavaScript functions related to pagination
if (typeof goPage === "function") {
  console.log("goPage function exists");
}

// Let's examine the current page input
const pageInput = document.querySelector('input[type="text"]');
if (pageInput) {
  console.log("Page input found:", pageInput.name, pageInput.value);
  
  // Set page to 3
  pageInput.value = "3";
  
  // Try to find and trigger form submission or page navigation
  const goLink = document.querySelector('a[href="#"]');
  if (goLink && goLink.textContent.includes("이동")) {
    console.log("Go link found, attempting to click");
    // Check if there's an onclick handler
    console.log("Go link onclick:", goLink.getAttribute("onclick"));
    
    // Try to trigger the click
    goLink.click();
    
    // Wait a moment and check new URL
    setTimeout(() => {
      console.log("New URL after click:", location.href);
    }, 1000);
  }
}