//---------------------------------------------------------------------
// sa.objectdiscoveryrule application
//---------------------------------------------------------------------
// Copyright (C) 2007-2024 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.sa.objectdiscoveryrule.Application");

Ext.define("NOC.sa.objectdiscoveryrule.Application", {
    extend: "NOC.core.ModelApplication",
    requires: [
        "NOC.sa.objectdiscoveryrule.Model",
        "NOC.core.label.LabelField",
        "NOC.wf.workflow.LookupField",
        "NOC.main.pool.LookupField",
        "NOC.main.notificationgroup.LookupField",
        "NOC.main.handler.LookupField",
        "NOC.main.ref.check.LookupField",
        "Ext.ux.form.GridField",
        "NOC.core.JSONPreview"
    ],
    model: "NOC.sa.objectdiscoveryrule.Model",

    initComponent: function() {
        var me = this;
        Ext.apply(me, {
            columns: [
                {
                    text: __("Name"),
                    dataIndex: "name",
                    width: 100,
                    align: "left"
                },
                {
                    text: __("Builtin"),
                    dataIndex: "is_builtin",
                    width: 50,
                    renderer: NOC.render.Bool,
                    sortable: false
                },
                {
                    text: __("Active"),
                    dataIndex: "is_active",
                    renderer: NOC.render.Bool,
                    width: 100,
                    align: "left"
                },
                {
                    text: __("Pref."),
                    // tooltip: "Preference", - broken in ExtJS 5.1
                    dataIndex: "preference",
                    width: 40,
                    align: "right"
                }
            ],

            fields: [
                {
                    name: 'name',
                    xtype: 'textfield',
                    fieldLabel: __('Name'),
                    allowBlank: false,
                    uiStyle: 'large'
                },
                {
                    name: "uuid",
                    xtype: "displayfield",
                    fieldLabel: __("UUID")
                },
                {
                    name: "is_active",
                    xtype: "checkbox",
                    boxLabel: __("Active")
                },
                {
                    name: 'description',
                    xtype: 'textarea',
                    fieldLabel: __('Description'),
                    uiStyle: 'large'
                },
                {
                  name: "workflow",
                  xtype: "wf.workflow.LookupField",
                  fieldLabel: __("WorkFlow"),
                  allowBlank: true
                },
                {
                    name: "preference",
                    xtype: "numberfield",
                    fieldLabel: __("Preference"),
                    allowBlank: true,
                    uiStyle: "small",
                    defaultValue: 100,
                },
                {
                    name: "network_ranges",
                    xtype: "gridfield",
                    fieldLabel: __("Network Ranges"),
                    columns: [
                        {
                            text: __("Network"),
                            dataIndex: "network",
                            editor: "textfield",
                            width: 250
                        },
                        {
                            text: __("Pool"),
                            dataIndex: "pool",
                            width: 200,
                            editor: {
                                xtype: "main.pool.LookupField"
                            },
                            renderer: NOC.render.Lookup("pool")
                        },
                        {
                            text: __("Exclude"),
                            dataIndex: "exclude",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50
                        }
                    ]
                },
                {
                  name: "update_interval",
                  xtype: "numberfield",
                  fieldLabel: __("Check update interval (sec)"),
                  allowBlank: true,
                  uiStyle: "medium",
                  defaultValue: 0,
                  minValue: 0
                },
                {
                  name: "expired_ttl",
                  xtype: "numberfield",
                  fieldLabel: __("Expired TTL (sec)"),
                  allowBlank: true,
                  uiStyle: "medium",
                  defaultValue: 0,
                  minValue: 0
                },
                {
                    name: "stop_processed",
                    xtype: "checkbox",
                    boxLabel: __("Stop Processing")
                },
                {
                    name: "action",
                    xtype: "combobox",
                    fieldLabel: __("Action"),
                    store: [
                        ["new", __("As New")],
                        ["ignore", __("Send Ignore")],
                        ["skip", __("Skip Rule")],
                        ["approve", __("Send Approve")]
                    ],
                    value: "new",
                    uiStyle: "medium"
                },
                {
                    name: "sources",
                    xtype: "gridfield",
                    fieldLabel: __("Sources"),
                    columns: [
                        {
                            text: __("Source"),
                            dataIndex: "source",
                            width: 150,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["etl", _("ETL")],
                                    ["network-scan", _("Network Scan")],
                                    ["manual", _("Manual")]
                                ]
                            }
                        },
                        {
                            text: __("Required"),
                            dataIndex: "is_required",
                            editor: "checkbox",
                            renderer: NOC.render.Bool,
                            width: 50
                        }
                    ]
                },
                {
                    name: "check_policy",
                    xtype: "combobox",
                    fieldLabel: __("Check Policy"),
                    store: [
                        ["ALL", __("All success")],
                        ["ANY", __("Any success")],
                    ],
                    allowBlank: true,
                    value: "ALL",
                    uiStyle: "medium"
                },
                {
                    name: "checks",
                    fieldLabel: __("Checks"),
                    xtype: "gridfield",
                    allowBlank: true,
                    width: 350,
                    columns: [
                        {
                            text: __("Check"),
                            dataIndex: "check",
                            width: 200,
                            editor: "main.ref.check.LookupField",
                            allowBlank: false,
                            renderer: NOC.render.Lookup("check")
                        },
                        {
                            text: __("Argument"),
                            dataIndex: "arg0",
                            editor: "textfield",
                            width: 150
                        },
                        {
                            text: __("Port"),
                            dataIndex: "port",
                            editor: {
                                xtype: "numberfield",
                                defaultValue: 0
                            }
                        },
                        {
                            text: __("Match State"),
                            dataIndex: "match_state",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["ok", __("OK")],
                                    ["fail", __("Fail")],
                                    ["any", __("Any")]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "ok": __("OK"),
                                "fail": __("Fail"),
                                "any": __("Any")
                            })
                        },
                        {
                            text: __("Match"),
                            dataIndex: "match",
                            width: 100,
                            editor: {
                                xtype: "combobox",
                                store: [
                                    ["regex", __("Regex")],
                                    ["contains", __("Contains")],
                                    ["eq", __("Equal")],
                                    ["gte", __("Greater Equal")]
                                ]
                            },
                            renderer: NOC.render.Choices({
                                "regex": __("Regex"),
                                "contains": __("Contains"),
                                "eq": __("Equal"),
                                "gte": __("Greater Equal")
                            })
                        },
                        {
                            text: __("Value"),
                            dataIndex: "value",
                            editor: "textfield"
                        }
                    ]
                }
            ]
        });
        me.callParent();
    }
});
