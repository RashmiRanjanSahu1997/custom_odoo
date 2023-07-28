odoo.define('helpdesk.tickets', function (require) {
"use strict";

var fieldRegistry = require('web.field_registry');
var AbstractField = require('web.AbstractField');
var Timer = require('helpdesk.tickets');

var TimerFieldWidget = AbstractField.extend({


    isSet: function () {
        return true;
    },

    _render: function () {
        this._super.apply(this, arguments);
        this._startTimeCounter();
    },

    destroy: function () {
        this._super.apply(this, arguments);
        clearInterval(this.timer);
    },

    _startTimeCounter: async function () {
        if (this.record.data.timer_start) {
            const serverTime = this.record.data.timer_pause || await this._getServerTime();
            this.time = Timer.createTimer(0, this.record.data.timer_start, serverTime);
            this.$el.text(this.time.toString());
            this.timer = setInterval(() => {
                if (this.record.data.timer_pause) {
                    clearInterval(this.timer);
                } else {
                    this.time.addSecond();
                    this.$el.text(this.time.toString());
                }
            }, 1000);
        } else if (!this.record.data.timer_pause){
            clearInterval(this.timer);
        }
    },
    _getServerTime: function () {
        return this._rpc({
            model: 'helpdesk.tickets',
            method: 'get_server_time',
            args: []
        });
    }
});

fieldRegistry.add('timer', TimerFieldWidget);

});
