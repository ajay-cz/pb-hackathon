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
                var self = $(this), order_info = $(this).find('#order_info').data('order');
                // Fetch Rates
                //$('#rates_btn').removeClass('disabled');


                if ($(this).hasClass('selected')) {
                    $(this).removeClass('selected');
                } else {
                    table.$('tr.selected').removeClass('selected');
                    $(this).addClass('selected');
                }
                if (table.$('tr.selected').length > 0) {
                    $('#duties_btn').removeClass('disabled');
                    $('#shipping_btn').removeClass('disabled');
                }
                else {
                    $('#duties_btn').addClass('disabled');
                    $('#shipping_btn').addClass('disabled');
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
                            if(result && result.final_tax) {
                                $(self).find('#duties').html("Est. Duties " + result.final_tax);
                            }
                            else {
                                $(self).find('#duties').html("Est. Duties " + result.final_tax);
                            }
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
//                console.log(e);
            });

            //$('#button').click( function () {
            //	alert( table.rows('.selected').data().length +' row(s) selected' );
            //} );
        });
    }); // end of document ready
})(jQuery);