// Code to prevent losing unsaved data when navigating away
$(function() {
  var formModified = Boolean();
  var saveClicked = Boolean();

  formModified = false;
  saveClicked = false;

  // See if user changed any form inputs
  $(':input:not(:button,:submit), textarea').change(function() {
    formModified = true;
  });

  // Don't warn user they have unsaved changes if they click save
  $('input:submit').click(function() {
    formModified = false;
    saveClicked = true;
  });

  // Checking if the user has modified the form upon closing window
  window.onbeforeunload = function() {
    var warnMessage = null;
    if (!saveClicked) {
      if (formModified) {
        warnMessage = 'You have unsaved changes on this page.';
      }
    }
    return warnMessage;
  };
});
