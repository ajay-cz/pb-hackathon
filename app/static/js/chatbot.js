(function($) {
    $(document).ready(function() {
        $('.modal').modal();
        var $chatbox = $('.chatbox'),
            $chatboxTitle = $('.chatbox__title'),
            $chatboxTitleClose = $('.chatbox__title__close'),
            $chatboxCredentials = $('.chatbox__credentials'),
            $chatform = $("#chatform");
        $chatboxTitle.on('click', function() {
            $chatbox.toggleClass('chatbox--tray');
        });
        $chatboxTitleClose.on('click', function(e) {
            e.stopPropagation();
            $chatbox.addClass('chatbox--closed');
        });
        $chatbox.on('transitionend', function() {
            if ($chatbox.hasClass('chatbox--closed')) $chatbox.remove();
        });
        $chatboxCredentials.on('submit', function(e) {
            e.preventDefault();
            $chatbox.removeClass('chatbox--empty');
        });

        function renderTables(obj) {
            var tabl = '';
            if (obj && obj.success) {
                obj.tracking_details.forEach(function(track_element) {
                    // console.log(track_element);
                    var checkpoints = '<table><thead><tr><td>Last Location</td><td>Status</td></tr></thead><tbody>';
                    track_element.checkpoints.forEach(function(checkpoint) {
                        // console.log(checkpoint);
                        checkpoints += '<tr>' +
                            '<td>' + checkpoint.checkpoint_time + '<br>' + checkpoint.city + '</td>' +
                            '<td>' + checkpoint.tag + '<br>' + checkpoint.message + '</td>' +
                            '</tr>'
                    });
                    checkpoints += '</tbody></table>';
                    tabl = '<table class="table">' +
                        '<thead>' +
                        '<tr>' +
                        '<td>' + track_element.order_id + '</td>' +
                        '<td>' + track_element.tracking_number + '</td>' +
                        '<td>' + track_element.tag + '</td>' +
                        '</tr>' +
                        '</thead>' +
                        '<tbody>' + checkpoints + '</tbody>' +
                        '</table>';
                    console.log(tabl);
                });
                return tabl;
            }
        };
        var chatInit = function(e) {
            e.preventDefault();
            var CustomerMsgTemplate = '<div class="chatbox__body__message chatbox__body__message--right">' +
                '<img src="https://s3.amazonaws.com/uifaces/faces/twitter/arashmil/128.jpg" alt="Picture">' +
                '<p>' + $chatform.find('textarea').val() + '</p>' +
                '</div>'
                $('.chatbox__body').append(CustomerMsgTemplate);

            $.post(
                    $chatform.attr('action'), {
                        'message': $chatform.find('textarea').val()
                    }
                )
                .done(function(sResp) {
                    console.log(sResp);
                    var d = JSON.parse(sResp);
                    $('#t_body').html(renderTables(d));
                    var message = 'Sorry ! We couldnt recognize the Order ID';
                    if(d && d.tracking_details && d.tracking_details[0] && d.tracking_details[0].order_id && d.tracking_details[0].order_id !== '[]') {

                        message = 'Check Tracking Of' + d.tracking_details[0].order_id;
                        message = '<a class="waves-effect waves-light btn modal-trigger" href="#track_modal">' + message +'</a>';
                        $('.modal').modal();
                        $('#track_modal').modal('open');
                    }
                    var systemMessageTemplate =
                        '<div class="chatbox__body__message chatbox__body__message--left">' +
                        '<img src="https://s3.amazonaws.com/uifaces/faces/twitter/brad_frost/128.jpg" alt="Picture">' +
                        '<p>' + message + '</p></div>'
                    $('.chatbox__body').append(systemMessageTemplate);
                })
                .fail(function(e) {
                    console.log(e)
                    $('.chatbox__body').append('<div class="chatbox__body__message chatbox__body__message--left">' +
                    '<img src="https://s3.amazonaws.com/uifaces/faces/twitter/brad_frost/128.jpg" alt="Picture">' +
                    '<p>' + 'Sorry ! We couldnt recognize the Order ID'  + '</p>' +
                    '</div>');
                })
                .always(function(){
                    $chatform.find('textarea').val('');
                    $('#progress').toggleClass('hide');
                })
        }
        $chatform.off('submit').on('submit', chatInit);
    });
})(jQuery);