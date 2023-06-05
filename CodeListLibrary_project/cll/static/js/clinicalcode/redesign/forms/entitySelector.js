/**
 * Default description string if none provided
 */
const DEFAULT_DESCRIPTOR = 'Create a ${name}'

/**
 * getDescriptor
 * @desc gets the descriptor if valid, otherwise uses default format
 * @param {string} description 
 * @param {string} name 
 * @returns {string} the descriptor
 */
const getDescriptor = (description, name) => {
  if (!isNullOrUndefined(description) && !isStringEmpty(description)) {
    return description;
  }

  return new Function('name', `return \`${DEFAULT_DESCRIPTOR}\`;`)(name);
}

/**
 * createGroup
 * @desc method to interpolate a card using a template
 * @param {node} container the container element
 * @param {string} template the template fragment
 * @param {*} id any data value
 * @param {*} title any data value
 * @param {*} description any data value
 * @returns {node} the interpolated element after appending to the container node
 */
const createGroup = (container, template, id, title, description) => {
  description = getDescriptor(description, title);

  const html = interpolateHTML(template, {
    'id': id,
    'title': title.toLocaleUpperCase(),
    'description': description,
  });
  
  const doc = parseHTMLFromString(html);
  return container.appendChild(doc.body.children[0]);
}

/**
 * createCard
 * @desc method to interpolate a card using a template
 * @param {node} container the container element
 * @param {string} template the template fragment
 * @param {*} id any data value
 * @param {*} type any data value
 * @param {*} hint any data value
 * @param {*} title any data value
 * @param {*} description any data value
 * @returns {node} the interpolated element after appending to the container node
 */
const createCard = (container, template, id, type, hint, title, description) => {
  const html = interpolateHTML(template, {
    'type': type,
    'id': id,
    'hint': hint,
    'title': title,
    'description': description,
  });
  
  const doc = parseHTMLFromString(html);
  return container.appendChild(doc.body.children[0]);
}

/**
 * collectEntityData
 * @desc Method that retrieves all relevant <data/> and <template/> elements with
 *       its data-owner attribute pointing to the entity selector
 * @return {object} An object describing the data collected
 */
const collectEntityData = () => {
  const output = {
    templates: { },
    datasets: { },
  };

  const templates = document.querySelectorAll('template[data-owner="entity-selector"]');
  for (let i = 0; i < templates.length; ++i) {
    let template = templates[i];
    output.templates[template.getAttribute('name')] = Array.prototype.reduce.call(
      template.content.childNodes,
      (result, node) => result + (node.outerHTML || node.nodeValue),
      ''
    );
  }

  const datasets = document.querySelectorAll('data[data-owner="entity-selector"]');
  for (let i = 0; i < datasets.length; ++i) {
    let datapoint = datasets[i];
    let parsed;
    try {
      parsed = JSON.parse(datapoint.innerText.trim());
    }
    catch (e) {
      parsed = [];
    }

    output.datasets[datapoint.getAttribute('name')] = parsed;
  }

  return output;
}

/**
 * initialiseSelector
 * @desc initialises the selector form, creates the initial entity cards and handles user interaction
 * @param {*} formData 
 */
const initialiseSelector = (formData) => {
  const { templates, datasets } = formData;
  const groupContainer = document.querySelector('#group-container');

  const entities = datasets?.data?.entities;
  if (!isNullOrUndefined(entities)) {
    for (let i = 0; i < entities.length; ++i) {
      let entity = entities[i];
      const available = datasets?.data?.templates.filter(item => item.entity_class__id == entity.id);
      if (available.length < 1) {
        continue;
      }
      
      let group = createGroup(
        groupContainer,
        templates?.group,
        entity.id,
        entity.name,
        entity.description
      );

      let childContainer = group.querySelector('#entity-options');
      for (let i = 0; i < available.length; ++i) {
        let item = available[i];
        let card = createCard(
          childContainer,
          templates?.card,
          item.id,
          'Template',
          `Version ${item.template_version}`,
          item.name,
          item.description
        );
    
        let btn = card.querySelector('#select-btn');
        btn.addEventListener('click', (e) => {
          window.location.href = `${getCurrentURL()}${entity.id}`;
        });
      }
    }
  }
}

// Main
domReady.finally(() => {
  const formData = collectEntityData();
  initialiseSelector(formData);
});
