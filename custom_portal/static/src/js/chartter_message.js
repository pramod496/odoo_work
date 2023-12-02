//import EventEmitter from 'events';
odoo.define('custom_portal.ks_qweb_load', function (require) {
'use strict';

    var core = require('web.core');
    var ajax = require('web.ajax');
    var ks_thread = require('mail.widget.Thread');
    var ks_abstract_message = require('mail.model.AbstractMessage');
    var ks_rpc = require('web.rpc');
    var ks_model_message = require('mail.model.Message');
    var ks_session = require('web.session');
    var ks_emojis = require('mail.emojis');
    var ks_mailUtils = require('mail.utils');
    var ks_ajax = require('web.ajax');
    var ks_config = require('web.config');
    var ks_qweb = core.qweb;
    var ks_thread_messages;
//    var AbstractThreadWindow = require('im_livechat.legacy.mail.AbstractThreadWindow');
//    const app = express()
//    const http = require('http');
//
//    const res = Object.create(http.ServerResponse.prototype)





    ks_thread.include({
         events: _.extend({}, ks_thread.prototype.events, {
		'click .o_thread_message_read': '_onMessageActionRead',
          }),

         _onMessageActionRead: function (ev){
		var self = this;
		var messageId = $(ev.currentTarget).data('message-id');
		var msg_read = $(ev.currentTarget).data('is-read');
		console.log("is read msg"+msg_read);
		if (msg_read){
			var readMsg = false;
		}else{
			var readMsg = true;
		}

		ks_rpc.query({
			model: "mail.message",
			method: "write",
			args: [[messageId],{'id': messageId, 'is_read': readMsg}],
		}).then(function(result){
			location.reload();
                        });
	},

    });

    ks_abstract_message.include({
	init: function (parent, data) {
            this._is_read = data.is_read;
	    this._super(parent, data);
        },
    isMsgRead: function(){
            return this._is_read;
        }
    });


});
