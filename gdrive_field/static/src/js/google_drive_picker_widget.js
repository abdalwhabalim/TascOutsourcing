/**
Copyright (C) 2020 Artem Shurshilov <shurshilov.a@yandex.ru>
Odoo Proprietary License v1.0

This software and associated files (the "Software") may only be used (executed,
modified, executed after modifications) if you have purchased a valid license
from the authors, typically via Odoo Apps, or if you have received a written
agreement from the authors of the Software (see the COPYRIGHT file).

You may develop Odoo modules that use the Software as a library (typically
by depending on it, importing it and using its resources), but without copying
any source code or material from the Software. You may distribute those
modules under the license of your choice, provided that this license is
compatible with the terms of the Odoo Proprietary License (For example:
LGPL, MIT, or proprietary licenses similar to this one).

It is forbidden to publish, distribute, sublicense, or sell copies of the Software
or modified copies of the Software.

The above copyright notice and this permission notice must be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.**/
odoo.define('gdrive_field', function (require) {
    "use strict";
    var core = require('web.core');
    var _t = core._t;
    var QWeb = core.qweb;
    var utils = require('web.utils');
    var Dialog = require("web.Dialog");
    var registry = require("web.field_registry");
    var fields = require("web.basic_fields");

    var FieldPathGdrivePicker = fields.UrlWidget.extend({ 	
        template: 'FieldGdrive',
       // tagName: 'a',
        events: _.extend({}, fields.UrlWidget.prototype.events, {
            "click .gdrive_field": "_onGoogleDrivePicker",           
        }),

        _renderReadonly: function () {
            this.$el.html('<a target="_blank" href="'+this.value+'">'+this.value+'</a>')
        },

        init: function (parent, record, attachments) {
            var old_attachments = attachments;
            this._super.apply(this, arguments);
            attachments = old_attachments;
            var self = this;
            this.config_read = $.Deferred();
            this._rpc({
                route: '/gdrivef_picker',
                }).then( data => {
                    this._parseConfig(data);
                    this.config_read.resolve();
            });

            this.cookieName = "gdrive.oauthToken";
            // Scope to use to access user's Drive items.
            this.scope = ['https://www.googleapis.com/auth/drive'];
            this.gdrive = {
                pickerApiLoaded: false,
                oauthToken: false
            };
        },

        generate_access_token (){
            this.generate_access_token_done = $.Deferred();
            try {
                gapi.load('auth2', {
                    'callback': this.onAuthApiLoad.bind(this)
                });
            }
            catch(err) {
                console.log('Error load Google Drive API', err);
            }
            return this.generate_access_token_done;
        },

        _parseConfig: function (data) {
            //this.data = data;
            if (data.client_id)
                this.gdrive.clientId = data.client_id;
            if (data.scope)
                this.gdrive.scope = [data.scope];
            else
                this.gdrive.scope = this.scope;
            if (data.mimetypes)
                this.gdrive.mimetypes = data.mimetypes;
            if (data.navbar_hidden)
                this.gdrive.navbar_hidden = data.navbar_hidden;
            if (data.locale)
                this.gdrive.locale = data.locale;
            if (data.dir)
                this.gdrive.dir = data.dir;
            if (data.gdrive_storage)
                this.gdrive.storage = data.gdrive_storage;
        },

        /**
            Function for get Google oauth2 token
        **/
        onAuthApiLoad: function() {
            var self = this;
            this.gdrive.oauthToken = this.readGdriveTokenCookie();
            var expire_at = self.readGdriveExpiresAt() || 1595076236898 + (3599*1000);
            var now = new Date().getTime();
            this.config_read.then( data => {
                // get new access token
                if (!this.gdrive.oauthToken || now > expire_at) {
                    if (this.gdrive.clientId){
                        gapi.auth2.authorize({
                            client_id: this.gdrive.clientId,
                            scope: this.gdrive.scope,
                            immediate: false
                        }, function(authResult) {
                            if (authResult && !authResult.error) {
                            	self.generate_access_token_done.resolve(authResult.access_token);
                                self.saveGdriveTokenCookie(authResult.access_token, authResult.expires_at);
                                if (self.gdrive.pickerApiLoaded)
                                    self.createPicker();
                                /* access_token: "ya29.a0AfH6SMDWDkm2hOnKonyxccveLqKFpJ1HrDgEHNFtFfa1OS0U57WtI1s_cy_jdLRMgYNakfc4B6RpB5fl2R12geTNT9hiqbiDIVAHKJnDnBdEq3_yP8tR_XfiTXCq4WKQX33iS4vkgb5j57d2wu9_S6h5joCX9DZlHALg"
                                expires_at: 1595076236898
                                expires_in: 3599
                                first_issued_at: 1595072637898
                                scope: "https://www.googleapis.com/auth/drive openid"
                                session_state:
                                extraQueryParams: {authuser: "0"}
                                __proto__: Object
                                token_type: "Bearer"
                                __proto__: Object*/
                                //utils.set_cookie('odoo.gdrive.oauthToken',odoo.gdrive.oauthToken,24*60*60*365);
                            }
                            else {
                                alert("Cannot get authorization token for Google Drive: " + authResult.error_subtype + " - " + authResult.error + "-"+authResult);
                                console.error(authResult)
                            }
                        });
                    }
                    else {
                        console.log(_t("Cannot access parameter 'document.gdrive.client.id' check your configuration in General Settings"));
                        alert(_t("Cannot access parameter 'document.gdrive.client.id' check your configuration in General Settings"));
                    }
                }
                else{
                    self.generate_access_token_done.resolve(this.gdrive.oauthToken);
                }
            });

        },

        saveGdriveTokenCookie: function(oauthToken, expires_at) {
            utils.set_cookie(this.cookieName, oauthToken);
            utils.set_cookie('gdrive_auth2_expires_at', expires_at);
            return;
        },

        readGdriveTokenCookie: function() {
            return utils.get_cookie(this.cookieName);
        },

        readGdriveExpiresAt: function() {
            return utils.get_cookie('gdrive_auth2_expires_at');
        },

        // Create and render a Picker object for searching images.
        createPicker: function() {
            var self = this;

          if (this.gdrive.pickerApiLoaded && this.gdrive.oauthToken) {
            var origin = window.location.protocol + '//' + window.location.host;
            var view = new google.picker.View(google.picker.ViewId.DOCS);
            if (this.gdrive.mimetypes)
                    view.setMimeTypes(this.gdrive.mimetypes);
            var picker = new google.picker.PickerBuilder()
                .enableFeature(google.picker.Feature.MULTISELECT_ENABLED)
                .setOAuthToken(self.gdrive.oauthToken)
                .setCallback(self.pickerCallback.bind(self))
                .setOrigin(origin)

            if (this.gdrive.navbar_hidden)
                    picker.enableFeature(google.picker.Feature.NAV_HIDDEN)

            if (this.gdrive.locale)
                    picker.setLocale(this.gdrive.locale)

            picker.addView(view);
            picker.addView(new google.picker.DocsUploadView().setIncludeFolders(true));
            if (this.gdrive.dir) {
                    picker.addView(new google.picker.DocsView().setParent(this.gdrive.dir))
                    picker.addView(new google.picker.DocsUploadView().setParent(this.gdrive.dir).setIncludeFolders(true))
            }
/*            else {
                picker.addView(view);
                picker.addView(new google.picker.DocsUploadView().setIncludeFolders(true));
            }*/
            picker.addView(google.picker.ViewId.DOCUMENTS);

             picker.build().setVisible(true);
          }
        },

        _downloadFromGdrive: async function (document) {
            var def = $.Deferred();
            let url = 'https://www.googleapis.com/drive/v2/files/' + document.id+ '?alt=media&source=downloadUrl';
            let headers = {headers: {'Authorization': 'Bearer ' + this.gdrive.oauthToken}};
            fetch(url, headers).then( response =>{
                response.blob().then( blob =>{
                    this.blobsGdrive.push({
                        blob: blob,
                        name: document.name
                    });
                    def.resolve();
                })
            })
            return def;
        },

        _copyToOdooFromGdrive: function (document){
            var deferreds = [];
            this.filesGdrive = [];
            this.blobsGdrive = [];
            // DOWNLOADING
            deferreds.push(this._downloadFromGdrive(document));

            // UPLOADING
            Promise.all(deferreds).then( res => {
                for (var i = 0; i < this.blobsGdrive.length; i++)
                       this.filesGdrive.push( new File([this.blobsGdrive[i].blob], this.blobsGdrive[i].name) );
                this.ondropGdrive(this.filesGdrive);
            });
        },

        _copyURLFromGdrive: function (document){
            this.$input.val(document.url)
            this.$el.text(document.url)
            
            this.commitChanges()
            this._setValue(this._formatValue(document.url));
            // this._rpc({
            //     model: 'ir.attachment',
            //     method: 'create',
            //     args: [{'name': document.name,
            //             'type': 'url',
            //             //'type': 'gdrive',
            //             'url': document.url,
            //             'res_id': this.currentResID,
            //             'res_model': this.currentResModel,
            //             'mimetype': document.mimeType
            //         }],
            // }).then( res =>{
            //     this.trigger_up('reload_attachment_box');
            // })
        },

        pickerCallback: function(data) {
            var self = this;
            var url = 'nothing';
            if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
                // var def = $.Deferred();
                // if (this.gdrive.storage == 'any')
                //     this._dialogStorageGdrive(def);
                // else
                //         def.resolve();
                //def.then( res =>{
                        // SELECT DOCUMENTS
                        var docs = data[google.picker.Response.DOCUMENTS]
                        var documents = [];
                        for (var i = 0; i < docs.length; i++) {
                            var doc = docs[i];
                            documents.push({
                                id: doc[google.picker.Document.ID],
                                name: doc[google.picker.Document.NAME],
                                url: doc[google.picker.Document.EMBEDDABLE_URL] || doc[google.picker.Document.URL]
                            });

                            // if (this.gdrive.storage == 'copy')
                            //     this._copyToOdooFromGdrive(doc);

                            // if (this.gdrive.storage == 'url')
                                this._copyURLFromGdrive(doc);
                        }
                //});
            }
        },

        _setStorageGdrive: function(value, def){
            this.gdrive.storage = value;
            def.resolve();
        },

        _dialogStorageGdrive: function(def){
            var self = this;
            new Dialog(this, {
                title: _t('Google Drive select storage'),
                size: 'medium',
                $content: $('<div>').html(_t('<p>Please, select file (files) storage:<p/>')),
                buttons: [
                {text: _t('Google Drive url'), classes: 'btn-primary', close: true, click: function () {self._setStorageGdrive('url', def)}},
                {text: _t('Odoo copy'), classes: 'btn-primary', close: true, click: function () {self._setStorageGdrive('copy', def)}},
                {text: _t('Cancel'), close: true}]
            }).open()
        },

        async _onGoogleDrivePicker(e) {
            var self = this;
            try {
                // wait access token, then open picker
                let access_token = await self.generate_access_token()
                gapi.load('picker', {
                    'callback': function() {
                        self.gdrive.pickerApiLoaded = true;
                        self.createPicker();
                    }
                });
            }
            catch(err) {
                console.log('Error load Google Drive API', err);
            }
        },

        ondropGdrive: function (files){
             var self = this;
                 var form_upload = document.querySelector('form.o_form_binary_form');
                 if (form_upload.length == 0) {
                     return;
                 }

                 var form_data = new FormData(form_upload);
                 for (var iterator = 0, file; file = files[iterator]; iterator++) {
                     form_data.set('ufile', file);

                     $.ajax({
                         url: form_upload.getAttribute('action'),
                         method: form_upload.getAttribute('method'),
                         type: form_upload.getAttribute('method'),
                         processData: false,
                         contentType: false,
                         data: form_data,
                         success: function (data) {
                             self.trigger_up('reload_attachment_box');
                         },
                         error: function (jqXHR, textStatus, errorThrown) {
                             console.error(jqXHR, textStatus, errorThrown);
                         }
                     });
                 }
         },
    });

    registry.add("gdrive_picker_field", FieldPathGdrivePicker);

});
        