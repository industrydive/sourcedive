// Code to prevent losing unsaved data when navigating away
(function ($) {
  let formModified = false;
  let saveClicked = false;

  // Certain fields are updated using js and therefore change and input don't fire, so overriding the set method
  // so we can know when the field has been changed.
  function customInputSetter() {
    const descriptor = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, "value");
    const originalSet = descriptor.set;

    // define our own setter
    descriptor.set = function (val) {
      // Ignore the hidden elements since those shouldn't be changed by the user
      if ($(this).attr('type') !== 'hidden') {
        formModified = true;
      }
      originalSet.apply(this, arguments);
    };

    Object.defineProperty(HTMLInputElement.prototype, "value", descriptor);
  }

  function setFormModifiedEvent() {
    $(':input:not(:button,:submit), textarea').on('input', function () {
      formModified = true;
    });
  }

  // Initial Setup
  customInputSetter();
  setFormModifiedEvent();

  // The selector-chosen fields are inline and aren't available even if the document is ready, so need to wait until the load event
  $(window).on("load", function () {
    $('.selector-chosen').bind("DOMSubtreeModified", function () {
      formModified = true;
    });

    $('.add-row a').click(() => {
      setFormModifiedEvent();
    });
  });


  // Don't warn user they have unsaved changes if they click save
  $('input:submit').click(() => {
    formModified = false;
    saveClicked = true;
  });

  // Checking if the user has modified the form upon closing window
  window.onbeforeunload = function () {
    let warnMessage = null;
    if (!saveClicked) {
      if (formModified) {
        warnMessage = 'You have unsaved changes on this page.';
      }
    }
    return warnMessage;
  };
})($);
