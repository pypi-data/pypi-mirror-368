//===----------------------------------------------------------------------===//
//
//         STAIRLab -- STructural Artificial Intelligence Laboratory
//
//===----------------------------------------------------------------------===//
//
// class AnalysisNavigator {
//     constructor(baseUrl, analysisTypes) {
//         this.#url = baseUrl;
//         this.#analysisTypes = analysisTypes;
//     }
// }

class VeuxNavigator {
  #initializedTabs;
  #table;
  #url;
  #tabLinkContainer;
  #tabContentContainer;
  #propContainer;

  constructor(baseUrl, tabLinkContainer, tabContentContainer, propContainer) {
    this.#url = baseUrl;
    this.#initializedTabs = [];
    this.#tabLinkContainer = tabLinkContainer;
    this.#tabContentContainer = tabContentContainer;
    this.#propContainer = propContainer;
  }

  initTabs(tab1, tabselector) {
    this.#initializedTabs.push(tab1);

    const tabs = this.#tabLinkContainer.querySelectorAll(tabselector);

    tabs.forEach(tab => {
        tab.addEventListener('click', (e) => {
          e.preventDefault();
          this.clickTab(tab);
        });
    });
  }

  //
  //
  //
  select(elem) {
    const sname =  `${elem.id}`; //dataset.name;

    elem.parentElement.querySelectorAll('.table-active').forEach((el) => {
        el.classList.remove("table-active");
    });
    elem.classList.add("table-active");
    
    // elem.parentElement.querySelectorAll("tr").forEach((el) => {
    //     el.style.display = "none";
    // });
    // elem.style.display = "table-row";

    if (this.#initializedTabs.includes(sname)) {
        const tabLink = this.#tabLinkContainer.querySelector(`#${sname}-tab`);
        this.clickTab(tabLink);
        return;
    }

    this.addTab(elem);
  }

  addTab(elem) {
    const tab = `${elem.id}`;

    //
    //
    //
    const tabLink = document.createElement('a');
    tabLink.id = `${tab}-tab`;
    tabLink.classList.add("tab-link", "nav-link", "active");
    tabLink.href = "#";
    tabLink.setAttribute('data-tab', tab);
    tabLink.setAttribute('data-render', elem.dataset.render);
    tabLink.setAttribute('data-bs-toggle', 'tab');
    tabLink.setAttribute('role', 'tab');
    tabLink.innerHTML = `${elem.dataset.name} <button class="btn-close" type="button" aria-label="Close"></button>`;
    const closeButton = tabLink.querySelector('.btn-close');
    closeButton.addEventListener('click', (e) => {
        this.delTab(tabLink);
    });
    tabLink.addEventListener('click', (e) => {
        e.preventDefault(); 
        this.clickTab(tabLink);
    });

    const tabItem = document.createElement('li');
    tabItem.role = 'presentation';
    tabItem.classList.add('nav-item');
    tabItem.appendChild(tabLink);
    // Add to list of tabs
    this.#tabLinkContainer.appendChild(tabItem);

    //
    //
    //
    const tabContent = document.createElement('div');
    tabContent.classList.add('tab-content', 'mt-3', 'card-body', 'p-2');
    tabContent.id = `${tab}-content`;
    tabContent.style.display = 'block';
    this.#tabContentContainer.appendChild(tabContent);

    
    this.#initializedTabs.push(tab);
    this.clickTab(tabLink);
    this.fetchAndUpdateTab(tab, elem.dataset.render);
    return tabLink;
  }

  clickTab(tabLink) {
    const tabs = this.#tabLinkContainer.querySelectorAll('.tab-link');

    // Remove 'active' class from all tabs
    tabs.forEach(t => {
        t.classList.remove('active');
    });

    // Add 'active' class to the clicked tab
    tabLink.classList.add('active');

    const tab = tabLink.getAttribute('data-tab');
    const contentDiv = this.#tabContentContainer.querySelector(`#${tab}-content`);

    contentDiv.style.display = 'block';
    this.#tabContentContainer.querySelectorAll(".tab-content").forEach((el) => {
        if (el.id != `${tab}-content`) {
            el.style.display = 'none';
        }
    });
  }

  delTab(tabLink) {
    const tab = tabLink.getAttribute('data-tab');
    const corr = tabLink.getAttribute('data-corridor');
    const tabContent = this.#tabContentContainer.querySelector(`#${tab}-content`);
    tabContent.remove();

    const tabItem = tabLink.parentElement;
    tabItem.remove();

    const idx = this.#initializedTabs.indexOf(tab);
    if (idx > -1) {
        this.#initializedTabs.splice(idx, 1);
    }
    this.clickTab(document.getElementById('tab1-tab'));
  }

  fetchAndUpdateTab(tab, query) {
    const contentDiv = this.#tabContentContainer.querySelector(`#${tab}-content`);

    // Show loading message while content is being fetched
    contentDiv.innerHTML = `
    <div class="text-center">
        <div class="spinner-border" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
    </div>
    `;

    let apiUrl = `${this.#url}/render/?${query}`;
    console.log(`Fetching content from: ${apiUrl}`);

    if (true) {
      contentDiv.innerHTML = "";
      const mv = document.createElement('model-viewer');

      mv.setAttribute('camera-controls', '');
      mv.setAttribute('autoplay', '');
      mv.setAttribute('interaction-prompt', 'none');
      mv.style.width  = '100%';
      mv.style.height = '400px';

      mv.src = `${this.#url}/render/?${query}`;
      contentDiv.appendChild(mv);
    }

      //
      //
    if (this.#propContainer) {
      fetch(`${this.#url}/properties/?${query}`)
        .then(response => response.json())
        .then(data => {
            let accordion = document.createElement('div');
            accordion.classList.add('accordion');
            accordion.classList.add('accordion-flush');

            for (const prop_table of data) {
              const table = document.createElement('table');
              table.classList.add('table', 'table-striped', 'table-bordered');
              const thead = document.createElement('thead');
              const tbody = document.createElement('tbody');
              thead.innerHTML = `
                    <tr>
                        <th>Property</th>
                        <th>Value</th>
                    </tr>
              `;
              prop_table.data.forEach(prop => {
                const row = document.createElement('tr');
                row.innerHTML = `
                        <td>${prop.name}</td>
                        <td>${prop.value.toFixed(2)}</td>
                    `;
                tbody.appendChild(row);
              });
              table.appendChild(thead);
              table.appendChild(tbody);
              
              const item = document.createElement('div');
              item.classList.add('accordion-item');
              {
                  // Accordion item header
                  const header = document.createElement('span');
                  header.classList.add('accordion-header');
                  header.id = `heading-${prop_table.name}`;
                  const button = document.createElement('button');
                  button.classList.add('accordion-button');
                  button.setAttribute('type', 'button');
                  button.setAttribute('data-bs-toggle', 'collapse');
                  button.setAttribute('data-bs-target', `#collapse-${prop_table.name}`);
                  button.setAttribute('aria-expanded', 'true');
                  button.setAttribute('aria-controls', `collapse-${prop_table.name}`);
                  button.innerText = prop_table.name;
                  header.appendChild(button);
                  item.appendChild(header);
              }
              const collapse = document.createElement('div');
              collapse.classList.add('accordion-collapse', 'collapse');
              collapse.id = `collapse-${prop_table.name}`;
              collapse.setAttribute('aria-labelledby', `heading-${prop_table.name}`);
              collapse.setAttribute('data-bs-parent', `#accordion-${prop_table.name}`);
              {
                  // Body
                  const body = document.createElement('div');
                  body.classList.add('accordion-body');
                  body.appendChild(table);
                  collapse.appendChild(body);
              }
              item.appendChild(collapse);
              accordion.appendChild(item);
              }
              this.#propContainer.innerHTML = ''; // Clear previous content
              this.#propContainer.appendChild(accordion);
          })
          .catch(error => {
            console.error('Error analysis:', error);
            this.#propContainer.innerHTML = '<p>Error loading content.</p>';
          });
    }
  }
}
