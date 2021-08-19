/**
Copyright (C) 2021 Artem Shurshilov <shurshilov.a@yandex.ru>
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

odoo.define('google_drive_picker/static/src/components/google_drive_picker/google_drive_picker.js', function (require) {
'use strict';

    const AttachmentBox = require('mail/static/src/components/attachment_box/attachment_box.js')
    const { patch } = require('web.utils');
    const { Component, useState } = owl;
    var core = require('web.core');
    var _t = core._t;
    var Dialog = require("web.Dialog");
    var utils = require('web.utils');

    patch(AttachmentBox, 'google_drive_picker/static/src/components/google_drive_picker/google_drive_picker.js', {
        async willStart(...args) {
            this._super(...args);

            this.config_read = $.Deferred();
            this.cookieName = "gdrive.oauthToken";
            // Scope to use to access user's Drive items.
            this.scope = ['https://www.googleapis.com/auth/drive'];
            this.gdrive = {
                pickerApiLoaded: false,
                oauthToken: false
            };
            this._parseConfig(this.env.session);
            this.config_read.resolve();

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

        _parseConfig(data) {
            data = data.gdrive;
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
        onAuthApiLoad() {
            var self = this;
            this.gdrive.oauthToken = this.readGdriveTokenCookie();
            var expire_at = self.readGdriveExpiresAt() || 0;
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
                                self.gdrive.oauthToken = authResult.access_token;
                                self.saveGdriveTokenCookie(authResult.access_token, authResult.expires_at);
                                // if (self.gdrive.pickerApiLoaded)
                                //     self.createPicker();
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

        saveGdriveTokenCookie(oauthToken, expires_at) {
            utils.set_cookie(this.cookieName, oauthToken);
            utils.set_cookie('gdrive_auth2_expires_at', expires_at);
            return;
        },

        readGdriveTokenCookie() {
            return utils.get_cookie(this.cookieName);
        },

        readGdriveExpiresAt() {
            return utils.get_cookie('gdrive_auth2_expires_at');
        },

        // Create and render a Picker object for searching images.
        createPicker() {
            //debugger
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
                this.env.services.rpc({
                //this._rpc({
                    route: '/gdrive_picker_path',
                    params: {
                        'res_id': this.thread.id,
                        'res_model': this.thread.model,
                        // 'res_id': this.currentResID,
                        // 'res_model': this.currentResModel,
                        'gdrive': this.gdrive
                    }
                }).then(function(data) {
                    var drive_path = null
                    if(data.dir_id){
                        drive_path=data.dir_id
                    }
                    else{
                        drive_path=self.gdrive.dir
                    }
                    if (drive_path) {
                        picker.addView(new google.picker.DocsView().setParent(drive_path).setLabel("Current Odoo record"))
                        picker.addView(new google.picker.DocsUploadView().setParent(drive_path).setIncludeFolders(true).setLabel("Upload to current Odoo record"))
                    }
                    else{
                        picker.addView(new google.picker.DocsUploadView().setIncludeFolders(true));
                    }
                    picker.addView(google.picker.ViewId.DOCUMENTS);
                    picker.build().setVisible(true);
                });
            }
        },

        async _downloadFromGdrive(document) {
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

        _copyToOdooFromGdrive(document){
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

        _copyURLFromGdrive(document){
            this.env.services.rpc({
                model: 'ir.attachment',
                method: 'create',
                args: [{'name': document.name,
                        'type': 'url',
                        //'type': 'gdrive',
                        'url': document.url,
                        'res_id': this.thread.id,
                        'res_model': this.thread.model,
                        'mimetype': document.mimeType
                        //'icon_url': document.iconUrl
                    }],
            }).then( res =>{
                this.thread.fetchAttachments.bind(this.thread)();
                this.thread.refresh();
            })
        },

        pickerCallback(data) {
            var self = this;
            var url = 'nothing';
            if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
                var def = $.Deferred();
                if (this.gdrive.storage == 'any')
                    this._dialogStorageGdrive(def);
                else
                        def.resolve();
                def.then( res =>{
                        // SELECT DOCUMENTS
                        console.log(data)
                        var docs = data[google.picker.Response.DOCUMENTS]
                        var documents = [];
                        for (var i = 0; i < docs.length; i++) {
                            var doc = docs[i];
                            documents.push({
                                id: doc[google.picker.Document.ID],
                                name: doc[google.picker.Document.NAME],
                                url: doc[google.picker.Document.EMBEDDABLE_URL] || doc[google.picker.Document.URL]
                            });

                            if (this.gdrive.storage == 'copy')
                                this._copyToOdooFromGdrive(doc);

                            if (this.gdrive.storage == 'url')
                                this._copyURLFromGdrive(doc);
                        }
                });
            }
        },

        _setStorageGdrive(value, def){
            this.gdrive.storage = value;
            def.resolve();
        },

        _dialogStorageGdrive(def){
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
                        // var expire_at = self.readGdriveExpiresAt() || 0;
                        // var now = new Date().getTime();
                        // if (self.gdrive.oauthToken && now <= expire_at)
                            self.createPicker();
                        // auto open picker
                        // else
                        //     alert(_t("Your Access Token expired, please refresh page and authorize again"));
                    }
                });
            }
            catch(err) {
                console.log('Error load Google Drive API', err);
            }
        },

        async ondropGdrive(files){
            await this._fileUploaderRef.comp.uploadFiles(files);
            this.thread.refresh();
        }
    });

});
        