odoo.define('optimiser.script', function (require) {
    jQuery(document).ready(function ($) {
        new LazyLoad({
            elements_selector: '.optimiser_lazy'
        });

        setTimeout(function () {
            new LazyLoad({
                elements_selector: '.optimiser_lazy'
            });
        }, 1000);

        $(document).ajaxComplete(function () {
            new LazyLoad({
                elements_selector: '.optimiser_lazy'
            });
        });

        (function () {
            orig = $.fn.css;
            $.fn.css = function () {
                var result = orig.apply(this, arguments);

                if (arguments[0] === "background-image") {
                    $(this).trigger('stylechange');
                }

                return result;
            }
        })();

        $('.optimiser_lazy').on('stylechange', function (ev) {
            if ($('body').hasClass('editor_enable') && ev.target.style.length && ev.target.style.backgroundImage) {
                $(ev.target).attr('data-src', ev.target.style.backgroundImage.replace(/url\(['"]*|['"]*\)/g, ""));
            }
        });
    });

    var sAnimation = require('website.content.snippets.animation');

    sAnimation.registry.autohideMenu.include({
        /**
         * @override
         */
        start: function () {
            var self = this;
            self.$el.addClass('invisible');
            var res = [this._super.apply(this, arguments)];

            self.$el.addClass('o_menu_loading');

            return $.when.apply($, res).then(function () {
                $(window).resize();
            }).then(function () {
                setTimeout(function () {
                    self.$el.removeClass('invisible');
                    self.$el.removeClass('o_menu_loading');
                }, 500);
            });
        },
    });

});