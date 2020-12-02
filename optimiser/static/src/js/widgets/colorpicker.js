odoo.define('optimiser.op_colorpicker', function (require) {
    "use strict";

    var form_widgets = require('web.basic_fields');
    var field_registry = require('web.field_registry');
    var field_utils = require('web.field_utils');

    var OptimiserColorPicker = form_widgets.FieldChar.extend(
        {
            template: 'OptimiserColorPicker',
            widget_class: 'op_colorpicker',
            _getValue: function () {
                return field_utils.format.char(this.$('input').val());
            },
            _render: function () {

                var show_value = field_utils.format.char(this.value);

                if (this.mode === 'readonly') {
                    this.$el.html(show_value)
                        .css({
                            backgroundColor: show_value,
                            padding: '2px 0',
                        });
                } else {

                    new jscolor(this.$el.find('input')[0], {
                        hash: true,
                        width: 200,
                        height: 100,
                        borderColor: '#000',
                        insetColor: '#FFF',
                        backgroundColor: '#666',
                        zIndex: 9999999
                    });

                    this.$el.find('input')
                        .val(show_value)
                        .css("background-color", show_value);
                }
            }
        });

    field_registry.add('op_colorpicker', OptimiserColorPicker);

    return OptimiserColorPicker;
});