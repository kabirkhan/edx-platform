(function($) {
    'use strict';
    $.fn.extend({
        /*
         * leanModal prepares an element to be a modal dialog.  Call it once on the
         * element that launches the dialog, when the page is ready.  This function
         * will add a .click() handler that properly opens the dialog.
         *
         * The launching element must:
         *   - be an <a> element, not a button,
         *   - have an href= attribute identifying the id of the dialog element,
         *   - have rel='leanModal'.
         */
        leanModal: function(options) {
            var defaults = {
                    top: 100,
                    overlay: 0.5,
                    closeButton: null,
                    position: 'fixed'
                },
                $overlay;

            function closeModal(modalId, e) {
                $('#lean_overlay').fadeOut(200);
                $('iframe', modalId).attr('src', '');
                $(modalId).css({display: 'none'});
                if (modalId === '#modal_clone') {
                    $(modalId).remove();
                }
                e.preventDefault();
            }

            if ($('#lean_overlay').length === 0) {
                $overlay = $("<div id='lean_overlay'></div>");
                $('body').append($overlay);
            }

            $.extend(options, defaults);

            return this.each(function() {
                var o = options;

                $(this).click(function(ev) {
                    var notice,
                        modalId = $(this).attr('href'),
                        modalWidth = $(modalId).outerWidth(),
                        modalClone;
                    $('.modal').hide();

                    if ($(modalId).hasClass('video-modal')) {
                        // Video modals need to be cloned before being presented as a modal
                        // This is because actions on the video get recorded in the history.
                        // Deleting the video (clone) prevents the odd back button behavior.
                        modalClone = $(modalId).clone(true, true);
                        modalClone.attr('id', 'modal_clone');
                        $(modalId).after(modalClone);
                        modalId = '#modal_clone';
                    }

                    $('#lean_overlay').click(function(e) {
                        closeModal(modalId, e);
                    });

                    $(o.closeButton).click(function(e) {
                        closeModal(modalId, e);
                    });

                    // To enable closing of email modal when copy button hit
                    $(o.copyEmailButton).click(function(e) {
                        closeModal(modalId, e);
                    });

                    $('#lean_overlay').css({display: 'block', opacity: 0});
                    $('#lean_overlay').fadeTo(200, o.overlay);

                    $('iframe', modalId).attr('src', $('iframe', modalId).data('src'));
                    if ($(modalId).hasClass('email-modal')) {
                        $(modalId).css({
                            width: 80 + '%',
                            height: 80 + '%',
                            position: o.position,
                            opacity: 0,
                            'z-index': 11000,
                            left: 10 + '%',
                            top: 10 + '%'
                        });
                    } else {
                        $(modalId).css({
                            position: o.position,
                            opacity: 0,
                            'z-index': 11000,
                            left: 50 + '%',
                            'margin-left': -(modalWidth / 2) + 'px',
                            top: o.top + 'px'
                        });
                    }

                    $(modalId).show().fadeTo(200, 1);
                    $(modalId).find('.notice')
                              .hide()
                              .html('');
                    notice = $(this).data('notice');
                    if (notice !== undefined) {
                        notice = $(modalId).find('.notice');
                        notice.show().html(notice);
                        // This is for activating leanModal links that were in the notice.
                        // We should have a cleaner way of allowing all dynamically added
                        // leanmodal links to work.
                        notice.find('a[rel*=leanModal]').leanModal({
                            top: 120,
                            overlay: 1,
                            closeButton: '.close-modal',
                            position: 'absolute'
                        });
                    }
                    ev.preventDefault();
                });
            });
        }
    });

    $(document).ready(function() {
        $('a[rel*=leanModal]').each(function() {
            var embed = $($(this).attr('href')).find('iframe'),
                sep;
            $(this).leanModal({top: 120, overlay: 1, closeButton: '.close-modal', position: 'absolute'});
            if (embed.length > 0 && embed.attr('src')) {
                sep = (embed.attr('src').indexOf('?') > 0) ? '&' : '?';
                embed.data('src', embed.attr('src') + sep + 'autoplay=1&rel=0');
                embed.attr('src', '');
            }
        });
    });
}(jQuery));
