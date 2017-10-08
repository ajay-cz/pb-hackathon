(function($){
  $(function(){
    // Initialize Materialize Components
    $('.button-collapse').sideNav();
    $('.parallax').parallax();
    $('.datepicker').pickadate({
        onSet: function (val) {
            if (val && val.highlight) {
                return;
            }
            $('.picker__close').click();
        },
        closeOnSelect: true,
        format: "yyyy-mm-dd",
        selectMonths: true, // Creates a dropdown to control month
        selectYears: 50 // Creates a dropdown of 15 years to control year
    });
    $('select').material_select();
    // the "href" attribute of the modal trigger must specify the modal ID that wants to be triggered
    $('.modal').modal();
    $('form').submit(function() {
        $('#progress').toggleClass('hide');
    })
  }); // end of document ready
})(jQuery); // end of jQuery name space