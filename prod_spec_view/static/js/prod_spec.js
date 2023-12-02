// TODO: add Condition to reload specs on state change
console.log("SPECS VIEW");
specview = ""
odoo.define("prod_spec_view.specView",function (require) {
    var Widget = require('web.Widget');
    var widgetRegistry = require('web.widget_registry');
    var renderer = require('web.FormRenderer');
    var base = require('web_editor.base');
    require('web.dom_ready');
    var SpecView = Widget.prototype.extend({
        template: 'prod_spec_view.specs_view',
        xmlDependencies: ['/prod_spec_view/static/xml/templates.xml'],
        init: function (parent) {
            this._super(parent);
        },
        start:function(){
            this._super();
        },
        loadSpecs: function(id,model){
            console.log("Specs View Is being Called")
            self = this;
            console.log("ID:"+id);
            console.log("Model:"+model);
            //TODO: Add model check here
            $.ajax({
                url: '/prod_spec_view/get_data/',
                type: "post",
                dataType: 'json',
                contentType: "application/json; charset=utf-8",
                data:JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params":{'id':id,'model':model}}),
                success:function(response) {
                    console.log(response);
                    if('error' in response){
                        $(".view_specs").html('Unable to get Product Specifications')
                    }
                    else{
                        if( "result" in response && response['result']['status']){
                            elbody = ``;
                            for (var i = 0; i < response['result']['res']['sale_order_lines'].length; i++) {
                                rowdata = ``;
                                for (var j = 0; j < response['result']['res']['sale_order_lines'][i]['specs'].length; j++) {
                                    cur_specs = response['result']['res']['sale_order_lines'][i]['specs'];
                                    if(cur_specs[j]['product_specification1'] ||cur_specs[j]['product_specification2'] ||cur_specs[j]['product_specification3'] ||cur_specs[j]['product_specification4'] ||cur_specs[j]['product_specification5'] ||cur_specs[j]['product_specification6']){
                                        rowdata+= `
                                            <tr>
                                                <td>${cur_specs[j]['product_specification1']?cur_specs[j]['product_specification1']:""}</td>
                                                <td>${cur_specs[j]['product_specification2']?cur_specs[j]['product_specification2']:""}</td>
                                                <td>${cur_specs[j]['product_specification3']?cur_specs[j]['product_specification3']:""}</td>
                                                <td>${cur_specs[j]['product_specification4']?cur_specs[j]['product_specification4']:""}</td>
                                                <td>${cur_specs[j]['product_specification5']?cur_specs[j]['product_specification5']:""}</td>
                                                <td>${cur_specs[j]['product_specification6']?cur_specs[j]['product_specification6']:""}</td>
                                            </tr>
                                        `
                                    }
                                }
                                elbody += `
                                    <h4>${response['result']['res']['sale_order_lines'][i]['product_name']}</h4>
                                    <table class = "o_list_view table table-sm table-hover table-striped o_list_view_ungrouped o_section_and_note_list_view">
                                    ${rowdata}
                                    </table>
                                `
                            }
                            $(".view_specs").html(elbody)
                        }
                        else{
                            if("result" in response){
                                $(".view_specs").html(response['result']['desc'])    
                            }
                            else{
                             $(".view_specs").html("Unknown error in retrieving the specs")   
                            }
                            
                        }                        
                    }

                }
            });

        }
    });
    widgetRegistry.add(
        'spec_view', SpecView
    );
    specview = new SpecView();
    specview.appendTo('.specView');
    return SpecView;
});
odoo.define("prod_spec_view.FormRendererSpecView", function (require) {
    var BasicRenderer = require('web.BasicRenderer');
    var config = require('web.config');
    var core = require('web.core');
    var dom = require('web.dom');
    var _t = core._t;
    var qweb = core.qweb;
    var FormRenderer = require('web.FormRenderer');
    
    FormRenderer.include({
        _updateView: function ($newContent) {
        var self = this;

        // Set the new content of the form view, and toggle classnames
        this.$el.html($newContent);
        this.$el.toggleClass('o_form_nosheet', !this.has_sheet);
        if (this.has_sheet) {
            this.$el.children().not('.oe_chatter')
                .wrapAll($('<div/>', {class: 'o_form_sheet_bg'}));
        }
        this.$el.toggleClass('o_form_editable', this.mode === 'edit');
        this.$el.toggleClass('o_form_readonly', this.mode === 'readonly');

        // Enable swipe for mobile when formview is in readonly mode and there are multiple records
        if (config.device.isMobile && this.mode === 'readonly' && this.state.count > 1) {
            this._enableSwipe();
        }

        // Attach the tooltips on the fields' label
        _.each(this.allFieldWidgets[this.state.id], function (widget) {
            var idForLabel = self.idsForLabels[widget.name];
            // We usually don't support multiple widgets for the same field on the
            // same view but it is the case with the new settings view on V11.0.
            // Therefore, we need to retrieve the correct label since it could be
            // displayed multiple times on the view, otherwise, for example the
            // enterprise label will be displayed as many times as the field
            // exists on settings.
            var $widgets = self.$('.o_field_widget[name=' + widget.name + ']');
            var $label = idForLabel ? self.$('.o_form_label[for=' + idForLabel + ']') : $();
            $label = $label.eq($widgets.index(widget.$el));
            if (config.debug || widget.attrs.help || widget.field.help) {
                self._addFieldTooltip(widget, $label);
            }
            if (widget.attrs.widget === 'upgrade_boolean') {
                // this widget needs a reference to its $label to be correctly
                // rendered
                widget.renderWithLabel($label);
            }
        });
//        specview.loadSpecs(self.state.res_id, self.state.model);
    },
    });
});
function getProjectId(){
  var urlcur = window.location.href;
  var a = urlcur.split("&");
  var b = a[0].split("#");
  var c = b[1].split("=");
  var projectid = c[1];
  return projectid;
}