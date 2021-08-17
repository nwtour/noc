//---------------------------------------------------------------------
// inv.resourcegroup application
//---------------------------------------------------------------------
// Copyright (C) 2007-2018 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.inv.resourcegroup.Application");

Ext.define("NOC.inv.resourcegroup.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.core.label.LabelField",
        "NOC.core.ListFormField",
        "NOC.inv.resourcegroup.Model",
        "NOC.core.combotree.ComboTree",
        "NOC.inv.technology.LookupField",
        "NOC.main.remotesystem.LookupField",

    ],
    model: "NOC.inv.resourcegroup.Model",
    search: true,
    helpId: "reference-resource-group",

    initComponent: function () {
        var me = this;

        me.cardButton = Ext.create("Ext.button.Button", {
            text: __("Card"),
            glyph: NOC.glyph.eye,
            scope: me,
            handler: me.onCard
        });

        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 300
                },
                {
                    text: __("Parent"),
                    dataIndex: "parent",
                    width: 300,
                    renderer: NOC.render.Lookup("parent")
                },
                {
                    text: __("Technology"),
                    dataIndex: "technology",
                    width: 300,
                    renderer: NOC.render.Lookup("technology")
                },
                {
                    text: __("Description"),
                    dataIndex: "description",
                    width: 300,
                    flex: 1
                }
            ],

            fields: [
                {
                    name: "name",
                    xtype: "textfield",
                    fieldLabel: __("Name"),
                    allowBlank: false,
                    uiStyle: "medium"
                },
                {
                    name: "parent",
                    xtype: "noc.core.combotree",
                    restUrl: "/inv/resourcegroup/",
                    fieldLabel: __("Resource Group"),
                    listWidth: 1,
                    listAlign: 'left',
                    labelAlign: "left",
                    width: 500,
                    allowBlank: true
                },
                {
                    name: "technology",
                    xtype: "inv.technology.LookupField",
                    fieldLabel: __("Technology"),
                    allowBlank: false
                },
                {
                    name: "description",
                    xtype: "textarea",
                    fieldLabel: __("Description"),
                    allowBlank: true
                },
                {
                name: "dynamic_service_labels",
                xtype: "listform",
                fieldLabel: __("Dynamic Service Labels"),
                items: [
                    {
                      name: "labels",
                      xtype: "labelfield",
                      fieldLabel: __("Match Labels"),
                      allowBlank: false,
                      isTree: true,
                      pickerPosition: "down",
                      uiStyle: "extra",
                      query: {
                        "allow_matched": true
                      }
                    },
                  ]
                },
                {
                name: "dynamic_client_labels",
                xtype: "listform",
                fieldLabel: __("Dynamic Client Labels"),
                items: [
                    {
                      name: "labels",
                      xtype: "labelfield",
                      fieldLabel: __("Match Labels"),
                      allowBlank: false,
                      isTree: true,
                      pickerPosition: "down",
                      uiStyle: "extra",
                      query: {
                        "allow_matched": true
                      }
                    },
                  ]
                },
                {
                    xtype: "fieldset",
                    layout: "hbox",
                    title: __("Integration"),
                    defaults: {
                        padding: 4,
                        labelAlign: "right"
                    },
                    items: [
                        {
                            name: "remote_system",
                            xtype: "main.remotesystem.LookupField",
                            fieldLabel: __("Remote System"),
                            allowBlank: true
                        },
                        {
                            name: "remote_id",
                            xtype: "textfield",
                            fieldLabel: __("Remote ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        },
                        {
                            name: "bi_id",
                            xtype: "displayfield",
                            fieldLabel: __("BI ID"),
                            allowBlank: true,
                            uiStyle: "medium"
                        }
                    ]
                },
                {
                    name: "labels",
                    xtype: "labelfield",
                    fieldLabel: __("Labels"),
                    allowBlank: true,
                    uiStyle: "extra",
                    query: {
                        "enable_resourcegroup": true
                    },
                }
            ],
            formToolbar: [
                me.cardButton
            ]
        });
        me.callParent();
    },
    filters: [
        {
            title: __("By Technology"),
            name: "technology",
            ftype: "lookup",
            lookup: "inv.technology"
        },
        {
            title: __("By ResourceGroup"),
            name: "parent",
            ftype: "tree",
            lookup: "inv.resourcegroup"
        },
    ],
    levelFilter: {
        icon: NOC.glyph.level_down,
        color: NOC.colors.level_down,
        filter: 'parent',
        tooltip: __('Parent filter')
    },
    //
    onCard: function() {
        var me = this;
        if(me.currentRecord) {
            window.open(
                "/api/card/view/resourcegroup/" + me.currentRecord.get("id") + "/"
            );
        }
    }
});
