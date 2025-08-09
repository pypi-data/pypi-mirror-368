/*
 * Code mostly from https://github.com/gch1p/bootstrap-5-autocomplete (April 26 2022)
 * Applied fix from https://github.com/gch1p/bootstrap-5-autocomplete/pull/30/
*/

const DEFAULTS = {
  threshold: 2,
  maximumItems: 5,
  highlightTyped: true,
  highlightClass: 'text-primary',
  label: 'label',
  value: 'value',
  showValue: false,
  showValueBeforeLabel: false,
  debounceTimeout: 300,
};

class Autocomplete {
  constructor(field, options) {
    this.field = field;
    this.options = Object.assign({}, DEFAULTS, options);
    this.dropdown = null;

    field.parentNode.classList.add('dropdown');
    field.setAttribute('data-bs-toggle', 'dropdown');
    field.classList.add('dropdown-toggle');

    const dropdown = ce(`<div class="dropdown-menu"></div>`);
    if (this.options.dropdownClass)
      dropdown.classList.add(this.options.dropdownClass);

    insertAfter(dropdown, field);

    this.dropdownEl = dropdown;
    this.dropdown = new bootstrap.Dropdown(field, this.options.dropdownOptions);

    field.addEventListener('click', (e) => {
      if (this.createItems() === 0) {
        e.stopPropagation();
        this.dropdown.hide();
      }
    });

    field.addEventListener('input', debounce(() => {
      if (this.options.onInput)
        // cpa: added debounce and  first 'this' param
        this.options.onInput(this, this.field.value);
      this.renderIfNeeded();
    }, this.options.debounceTimeout));

    field.addEventListener('keydown', (e) => {
      if (e.keyCode === 27) {  // escape
        this.dropdown.hide();
        return;
      }
      if (e.keyCode === 40) {  // down arrow
        this.dropdown._menu.children[0]?.focus();
        return;
      }
    });
  }

  setData(data) {
    this.options.data = data;
    this.renderIfNeeded();
  }

  renderIfNeeded() {
    if (this.createItems() > 0)
      this.dropdown.show();
    else
      this.field.click();
  }

  createItem(lookup, item) {
    let label;
    const idx = removeDiacritics(item.label)
        .toLowerCase()
        .indexOf(removeDiacritics(lookup).toLowerCase());
    if (this.options.highlightTyped && idx >= 0) {
      const className = Array.isArray(this.options.highlightClass) ? this.options.highlightClass.join(' ')
        : (typeof this.options.highlightClass == 'string' ? this.options.highlightClass : '');
      label = item.label.substring(0, idx)
        + `<span class="${className}">${item.label.substring(idx, idx + lookup.length)}</span>`
        + item.label.substring(idx + lookup.length, item.label.length);
    } else {
      label = item.label;
    }

    if (this.options.showValue) {
      if (this.options.showValueBeforeLabel) {
        label = `${item.value} ${label}`;
      } else {
        label += ` ${item.value}`;
      }
    }

    const el = ce(
        `<button type="button" class="dropdown-item" data-label="${item.label}" data-value="${item.value}" ">${label}</button>`
    );
    el.dataset.details = JSON.stringify(item.details);
    return el
  }

  createItems() {
    const lookup = this.field.value;
    if (lookup.length < this.options.threshold || !this.options.data) {
      this.dropdown.hide();
      return 0;
    }

    const items = this.dropdownEl;
    items.innerHTML = '';

    const keys = Object.keys(this.options.data);

    let count = 0;
    for (let i = 0; i < keys.length; i++) {
      const key = keys[i];
      const entry = this.options.data[key];
      const item = {
          label: this.options.label ? entry[this.options.label] : key,
          value: this.options.value ? entry[this.options.value] : entry,
          details: entry.details
      };

      items.appendChild(this.createItem(lookup, item));
      if (this.options.maximumItems > 0 && ++count >= this.options.maximumItems)
        break;
    }

    this.dropdownEl.querySelectorAll('.dropdown-item').forEach((item) => {
      item.addEventListener('click', (e) => {
        let dataLabel = e.currentTarget.getAttribute('data-label');
        let dataValue = e.currentTarget.getAttribute('data-value');

        this.field.value = dataLabel;

        if (this.options.onSelectItem) {
          this.options.onSelectItem({
            value: dataValue,
            label: dataLabel,
            details: e.currentTarget.dataset.details
          });
        }

        this.dropdown.hide();
      })
    });

    return items.childNodes.length;
  }
}

/**
 * @param html
 * @returns {Node}
 */
function ce(html) {
  let div = document.createElement('div');
  div.innerHTML = html;
  return div.firstChild;
}

/**
 * @param elem
 * @param refElem
 * @returns {*}
 */
function insertAfter(elem, refElem) {
  return refElem.parentNode.insertBefore(elem, refElem.nextSibling);
}

/**
 * @param {String} str
 * @returns {String}
 */
function removeDiacritics(str) {
  return str
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '');
}

function debounce(func, timeout=300) {
  let timer;
  return (...args) => {
    if (timeout <= 0) func.apply(this, args);
    else {
      clearTimeout(timer);
      timer = setTimeout(() => { func.apply(this, args); }, timeout);
    }
  };
}

/* End of bootstrap-5-autocomplete code */

export function setupAutocomplete(section, widgetSelector) {
    section.querySelectorAll(widgetSelector).forEach(inp => {
        new Autocomplete(inp, {
            maximumItems: 10,
            onInput: async (ac, value) => {
                if (value) {
                    const resp = await fetch(`${inp.dataset.searchurl}?q=${value}`);
                    const data = await resp.json();
                    if (data.result && data.result == 'error') {
                        ac.setData([{label: `<i>Erreur: ${data.message}</i>`, value: ''}])
                    } else {
                        // data expected as list of {'label'/'value'} objects.
                        ac.setData(data);
                    }
                } else {
                    ac.setData({});
                    if (inp.dataset.pkfield) {
                        const pkInput = inp.form.querySelector(`input[name=${inp.dataset.pkfield}]`);
                        const pkInputHadValue = pkInput.value.length > 0;
                        pkInput.value = "";
                        if (pkInputHadValue) pkInput.dispatchEvent(new Event('change'));
                    }
                }
            },
            onSelectItem: (data) => {
                if (inp.dataset.pkfield) {
                    const pkInput = inp.form.querySelector(`input[name=${inp.dataset.pkfield}]`);
                    pkInput.value = data.value;
                    pkInput.dispatchEvent(new Event('change'));
                }
                inp.dispatchEvent(new CustomEvent('itemselected', {detail: data}));
            }
        });
    });
}

window.addEventListener('DOMContentLoaded', () => {
    setupAutocomplete(document, '.city_ch_autocomplete');
});
