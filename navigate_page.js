// Navigate to page 3 and check URL
console.log("Current URL:", location.href);

// Check if the function exists
if (typeof fn_egov_link_page === 'function') {
  console.log("fn_egov_link_page function found");
  
  // Store original URL
  const originalUrl = location.href;
  console.log("Original URL:", originalUrl);
  
  // Navigate to page 3
  fn_egov_link_page(3);
  
  // Check new URL after navigation
  setTimeout(() => {
    console.log("URL after navigating to page 3:", location.href);
    
    // Navigate to page 4
    fn_egov_link_page(4);
    
    setTimeout(() => {
      console.log("URL after navigating to page 4:", location.href);
      
      // Extract the pattern
      const url4 = location.href;
      const baseUrl = url4.split('?')[0];
      const params = url4.split('?')[1];
      
      console.log("Base URL:", baseUrl);
      console.log("Parameters:", params);
      
      // Create the pattern
      const pattern = baseUrl + "?" + params.replace(/page=\d+/, 'page={{next_page}}');
      console.log("URL Pattern:", pattern);
      
    }, 500);
  }, 500);
} else {
  console.log("fn_egov_link_page function not found");
  console.log("Available functions:", Object.getOwnPropertyNames(window).filter(name => name.includes('page')));
}