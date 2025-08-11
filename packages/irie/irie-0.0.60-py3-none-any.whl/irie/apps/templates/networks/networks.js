//===----------------------------------------------------------------------===//
//
//         STAIRLab -- STructural Artificial Intelligence Laboratory
//
//===----------------------------------------------------------------------===//
//
// IRiE
//
let initializedTabs = [];

function fetchAndUpdateTab(tab, formData) {

    const contentDiv = document.getElementById(`${tab}-content`);

    // Show loading message while content is being fetched
    contentDiv.innerHTML = `
    <div class="text-center">
        <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    </div>
    `;

    let apiUrl = `/api/networks/?tab=${tab}`
    if (formData != 'undefined') {
      // Fetch the content for the selected tab
      const queryParams = new URLSearchParams(formData);

      // Construct the API URL with query parameters
      apiUrl = apiUrl + "&" + queryParams.toString();
      console.log(apiUrl);
    }

    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            // Replace the loading message with the fetched content
            // when we get it
            if (data.error) {
                contentDiv.innerHTML = `<p>${data.error}</p>`;
            } else {
                contentDiv.innerHTML = data.map_html;
            }
            if (data.table_html) {
                document.getElementById('corridor-table').innerHTML = data.table_html;

                // Initialize the table pagination
                new TablePagination('myTable', 'pagination', 'searchInput');
            }
        })
        .catch(error => {
            console.error('Error fetching content:', error);
            document.getElementById('tab-content').innerHTML = '<p>Error loading content.</p>';
        });
}

function delCorridorTab(tabLink) {
    const tab = tabLink.getAttribute('data-tab');
    const corr = tabLink.getAttribute('data-corridor');
    const tabContent = document.getElementById(`${tab}-content`);
    tabContent.remove();

    const tabItem = tabLink.parentElement;
    tabItem.remove();

    const idx = initializedTabs.indexOf(tab);
    if (idx > -1) {
        initializedTabs.splice(idx, 1);
    }
    handleClickedTab(document.getElementById('tab1-tab'));
}

function addCorridorTab(corr) {
    const tab = `c${corr}`;

    //
    //
    //
    const tabLink = document.createElement('a');
    tabLink.id = `${tab}-tab`;
    tabLink.classList.add("tab-link", "nav-link", "active");
    tabLink.href = "#";
    tabLink.setAttribute('data-tab', tab);
    tabLink.setAttribute('data-corridor', corr);
    tabLink.setAttribute('data-bs-toggle', 'tab');
    tabLink.setAttribute('role', 'tab');
    tabLink.innerHTML = `Corridor ${corr} <button class="btn-close" type="button" aria-label="Close"></button>`;
    const closeButton = tabLink.querySelector('.btn-close');
    closeButton.addEventListener('click', (e) => {delCorridorTab(tabLink);});
    tabLink.addEventListener('click', function(e) {
        e.preventDefault(); handleClickedTab(tabLink);
    });

    const tabItem = document.createElement('li');
    tabItem.role = 'presentation';
    tabItem.classList.add('nav-item');
    tabItem.appendChild(tabLink);
    // Add to list of tabs
    const tabLinkContainter = document.getElementById('tab-link-container');
    tabLinkContainter.appendChild(tabItem);

    //
    //
    //
    const tabContent = document.createElement('div');
    tabContent.classList.add('tab-content', 'mt-3', 'card-body', 'p-2');
    tabContent.id = `${tab}-content`;
    tabContent.style.display = 'block';
    document.getElementById('tab-content-container').appendChild(tabContent);

    // Get the data-tab attribute to know which content to load
    const selectedTab = tabLink.getAttribute('data-tab');
    // const corr = tabLink.getAttribute('data-corridor');

    initializedTabs.push(tab);

    handleClickedTab(tabLink);

    // Create a URLSearchParams object from the form data
    const form = document.getElementById("tab1-form");
    let formData = new FormData(form);
    formData.append('corridor_input', corr);
    fetchAndUpdateTab(selectedTab, formData);
    return tabLink;
}

function handleCorridorSelection(elemid) {
    // Prevent the form from submitting in the traditional way
    // event.preventDefault();
    // Get the form element
    const corr = elemid.split("-")[1];
    console.log(corr);

    // TODO: Check initizliedTabs for existing tab
    if (initializedTabs.includes(`c${corr}`)) {
        const tabLink = document.getElementById(`c${corr}-tab`);
        handleClickedTab(tabLink);
        return;
    }

    addCorridorTab(corr);
}

function handleClickedTab(tabLink) {
    console.log(tabLink);

    const tabs = document.querySelectorAll('.tab-link');

    // Remove 'active' class from all tabs
    tabs.forEach(t => {
        t.classList.remove('active');
    });

    // Add 'active' class to the clicked tab
    tabLink.classList.add('active');

    const tab = tabLink.getAttribute('data-tab');
    const contentDiv = document.getElementById(`${tab}-content`);

    contentDiv.style.display = 'block';
    document.getElementsByClassName("tab-content").forEach((el) => {
        if (el.id != `${tab}-content`) {
            el.style.display = 'none';
        }
    });
}

function handleCorridorUpdate(event) {
    // Prevent the form from submitting in the traditional way
    event.preventDefault();
  
    // Get the form element
    const form = event.target;
    const tab = "tab1";
  
    // Normalize form fields with "weight" in their name to sum to 1.0
    const formData = new FormData(form);
    const weightFields = [];
    let totalWeight = 0;
  
    // Collect "weight" fields and calculate total weight
    formData.forEach((value, key) => {
      if (key.toLowerCase().includes("weight")) {
        // Ensure valid number, default to 0
        const numericValue = parseFloat(value) || 0;
        weightFields.push({ key, value: numericValue });
        totalWeight += numericValue;
      }
    });
  
    // Normalize weights if totalWeight > 0 to avoid division by zero
    if (totalWeight > 0) {
      weightFields.forEach(field => {
        const normalizedValue = field.value / totalWeight*100;
        formData.set(field.key, normalizedValue);
  
        // Update the input field in the form
        const inputElement = form.querySelector(`[name="${field.key}"]`);
        if (inputElement) {
          // Limit decimals for readability
          inputElement.value = normalizedValue.toFixed(0);
        }
      });
    }
  
    // Close all bridge tabs except the first one
    initializedTabs.slice(1, initializedTabs.length).forEach(tab => {
      if (tab.startsWith('c')) {
        console.log(tab);
        delCorridorTab(document.getElementById(`${tab}-tab`));
      }
    });
  
    // Create a URLSearchParams object from the form data
    // and fetch the data for the selected tab
    fetchAndUpdateTab(tab, formData);
}


// Event delegation: Listen for clicks on all nav links
document.addEventListener('DOMContentLoaded', function () {
    initializedTabs.push('tab1');
    
    fetchAndUpdateTab('tab1', new FormData(document.getElementById("tab1-form")));

    const tabs = document.querySelectorAll('.tab-link');

    tabs.forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault(); handleClickedTab(tab);
        });
    });
});
