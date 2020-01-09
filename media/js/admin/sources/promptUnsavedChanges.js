// Code to prevent losing unsaved data when navigating away
(function ($) {
  let formModified = false;
  let saveClicked = false;

  // Certain fields are updated using js and therefore change and input don't fire, so overriding the set method
  // so we can know when the field has been changed.
  function customInputSetter() {
    const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    const originalSet = descriptor.set;

    // define our own setter. This needs to be a regular function so that `this` is the input field rather than the window
    descriptor.set = function() {
      if ($(this).attr('name').includes('date_time')) {
        formModified = true;
      }
      originalSet.apply(this, arguments);
    };

    Object.defineProperty(HTMLInputElement.prototype, "value", descriptor);
  }

  customInputSetter();

  function setFormModifiedEvent() {
    $(':input:not(:button,:submit), textarea').on('input', () => {
      formModified = true;
    });
  }

  // The selector-chosen fields are inline and aren't available even if the document is ready, so need to wait until the load event
  $(window).on("load", () => {
    setFormModifiedEvent();

    $('.selector-chosen').bind("DOMSubtreeModified", function () {
      // This if is main to catch the scenario where the user just selects something with the 'from' list, but doesn't add the item.
      if ($(this).children('option').length) {
        formModified = true;
      }
    });

    $('.add-row a').click(() => {
      setFormModifiedEvent();
    });

    // Don't warn user they have unsaved changes if they click save
    $('input:submit').click((evt) => {
      if (evt.target.value.toLowerCase().includes('save')) {
        formModified = false;
        saveClicked = true;
      }
    });
  });

  // Checking if the user has modified the form upon closing window
  window.onbeforeunload = () => {
    let warnMessage = null;
    if (!saveClicked) {
      if (formModified) {
        warnMessage = 'You have unsaved changes on this page.';
      }
    }
    return warnMessage;
  };
})($);
