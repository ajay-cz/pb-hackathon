(function($) {
    $(function() {
        $(document).ready(function() {

            var config = {
                "sDom": "<'row'<'col s6 pagination'><'col s6'>r>t<'row'<'col s12'f><'col s12'p>>",
                //"sDom": '<"top"i>rt<"bottom"flp><"clear">',
                "bProcessing": true,
                "bjQueryUI": false,
                "serverSide": true,
                "select": true,
                "pagingType": "full_numbers",
                "sAjaxSource": "/_server_data",
                "columnDefs": [{
                    "targets": -1,
                    "data": null,
                    "defaultContent": "<button>Click!</button>"
                }]
            };
            var table = $('#example').DataTable(config);

            $('#example tbody').on('click', 'tr', function(e) {
                var self = $(this);
                // Fetch Rates
                //$('#rates_btn').removeClass('disabled');
                $('#duties_btn').removeClass('disabled');
                // if($(this).find('#rates').val()){
                $('#shipping_btn').removeClass('disabled');
                //}
                //			var order_info = {"_id":"31e6853a-aad2-49de-8dc3-8b9fada2b89d","store_type":"Prestashop","fromAddress":{"company":"Pitney Bowes Inc.","name":"sender_fname","phone":"2032032033","email":"sender@email.com","residential":true,"addressLines":["27 Waterview Drive"],"cityTown":"Shelton","stateProvince":"CT","postalCode":"06484","countryCode":"US","status":"NOT_CHANGED"},"toAddress":{"company":"Glorias Co.","name":"Peter","phone":"2222222222","email":"receiver@email.com","residential":true,"addressLines":["1 Sullivan SQ"],"cityTown":"Berwick","postalCode":"03901","countryCode":"US","status":"NOT_CHANGED"},"parcel":{"weight":{"unitOfMeasurement":"OZ","weight":1},"dimension":{"unitOfMeasurement":"IN","length":6,"width":0.25,"height":4,"irregularParcelGirth":0.002}}};
                var order_info = $(this).find('#order_info').data('order');
                console.log("non-working:");
                console.log($(this).find('#order_info').data('order'));
                console.log("working:");
                console.log(order_info);

                if ($(this).hasClass('selected')) {
                    $(this).removeClass('selected');
                } else {
                    table.$('tr.selected').removeClass('selected');
                    $(this).addClass('selected');
                }
                // Create Shipment
                $('#shipping_btn').off('click').on('click', function() {
                    $('#progress').toggleClass('hide');
                    $.ajax({
                        url: "/create-shipment",
                        method: "POST",
                        data: JSON.stringify(order_info),
                        dataType: 'json',
                        contentType: "application/json",
                        success: function(result, status, jqXHR) {
                            $('#progress').toggleClass('hide');
                            //Do something
                            if(result && result.redirect_to) {
                                window.location.replace(result.redirect_to)
                            }
                        },
                        error(jqXHR, textStatus, errorThrown) {
                            $('#progress').toggleClass('hide');
                            if (jqXHR && jqXHR.status == 500) {
                                alert('Oops ! Some Details Appear not to be right');
                            } else {
                                alert('Oops ! Some Details Appear not to be right');
                            }
                            //Do something
                        }
                    });

                    // Make Ajax Call to invoke PB Api - create-shipment
                    // $.post(url, {})
                    // .done(function(pbResponse){
                    //	$(self).closest('#shipment').val('labels');
                    //})
                })
                // Calculate Duties
                $('#duties_btn').off('click').on('click', function() {
                    $('#progress').toggleClass('hide');
                    $.ajax({
                        url: "/duty",
                        method: "POST",
                        data: JSON.stringify(order_info),
                        dataType: 'json',
                        contentType: "application/json",
                        success: function(result, status, jqXHR) {
                            $('#progress').toggleClass('hide');
                            //Do something
                        },
                        error(jqXHR, textStatus, errorThrown) {
                            $('#progress').toggleClass('hide');
                            if (jqXHR && jqXHR.status == 500) {
                                alert('Oops ! Some Details Appear not to be right');
                            } else {
                                alert('Oops ! Some Details Appear not to be right');
                            }
                            //Do something
                        }
                    });

                    // Make Ajax Call to invoke PB Api - create-shipment
                    // $.post(url, {})
                    // .done(function(pbResponse){
                    //	$(self).closest('#shipment').val('labels');
                    //})
                })
                console.log(e);
            });

            //$('#button').click( function () {
            //	alert( table.rows('.selected').data().length +' row(s) selected' );
            //} );
        });
    }); // end of document ready
})(jQuery);