//opens new resource suggesiton form (suggest-resource.html)
function suggestNewResource() {
    window.location.href = "/resources/suggest";
}


//toogle book-specific and journal article-specific fields
//on the Suggest Resource form
function toggleFields(selectElement) {

    var selectedResourceType = selectElement.value;

    // Show fields based on the selected resource_type
    switch(selectedResourceType){
        case '7':
        case '8':
            $('#id_book, label[for="id_book"]').closest('.form-control').show();
            $('#id_isbn, label[for="id_isbn"]').closest('.form-control').show();
            $('#id_journal, label[for="id_journal"]').closest('.form-control').hide();
            $('#id_journal_issue, label[for="id_journal_issue"]').closest('.form-control').hide();
            break;
        case '1':
        case '2':
            $('#id_book, label[for="id_book"]').closest('.form-control').hide();
            $('#id_isbn, label[for="id_isbn"]').closest('.form-control').hide();
            $('#id_journal, label[for="id_journal"]').closest('.form-control').show();
            $('#id_journal_issue, label[for="id_journal_issue"]').closest('.form-control').show();
            break;
        default:
            $('#id_book, label[for="id_book"]').closest('.form-control').hide();
            $('#id_isbn, label[for="id_isbn"]').closest('.form-control').hide();
            $('#id_journal, label[for="id_journal"]').closest('.form-control').hide();
            $('#id_journal_issue, label[for="id_journal_issue"]').closest('.form-control').hide();
    }
} //(toggleFields)


function setValue(element, value) {

    if (element.tagName.toLowerCase() === 'select') {
        // For <select> elements, find the option with the corresponding value and select it
        const option = element.querySelector('option[value="' + value + '"]');

        if (option) {
            option.selected = true;
        } else {
            console.error('Option with value [' + value + '] not found for element ' + element.id);
        }
    } else {
        // For other input elements, set the value as before
        element.value = value;
    }
} //(setValue)


//Clears Review resource form and sets id to 0
function addNewResource() {

    clearFormFields();

    const idField = document.getElementById("id_id");
    idField.value = 0;

    document.getElementById('new_resource_heading').innerHTML = "NEW RESOURCE";
} //(addNewResource)


function clearFormFields() {
    // Clear all form fields
    const formFields = document.querySelectorAll("form input, form textarea, form select");
    formFields.forEach(field => {
        if (field.type === "text" || field.type === "textarea") {
            field.value = "";
        } else if (field.type === "select-multiple") {
            field.selectedIndex = -1;
        } else if (field.type === "select-one") {
            field.selectedIndex = 0;
        }
    });
} //(clearFormFields)


function prependAsteriskToRequiredFieldLabels() {

    $(function() {
        $("[required]").each(function() {
            // Find the corresponding label for the input field
            var label = $("label[for='" + $(this).attr('id') + "']");
            // Append an asterisk to the label
            label.prepend("<span style='color: red;'>* </span>");
        });
    });
}


function validateFormSubmission(event, formId) {
    const currForm = document.getElementById(formId);
    // Prevent form submission if form validation fails
    if (!currForm.checkValidity()) {
        event.preventDefault();
        alert("Please fill in all required fields.");
    }
}