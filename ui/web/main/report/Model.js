//---------------------------------------------------------------------
// main.remotesystem Model
//---------------------------------------------------------------------
// Copyright (C) 2007-2022 The NOC Project
// See LICENSE for details
//---------------------------------------------------------------------
console.debug("Defining NOC.main.report.Model");

Ext.define("NOC.main.report.Model", {
    extend: "Ext.data.Model",
    rest_url: "/main/report/",

    fields: [
        {
            name: "id",
            type: "string"
        },
        {
            name: "description",
            type: "string"
        },
        {
            name: "name",
            type: "string"
        },
        {
            name: "is_builtin",
            type: "boolean",
            persist: false
        },
        {
            name: "uuid",
            type: "string",
            persist: false
        },
        {
            name: "code",
            type: "string"
        },
        {
            name: "hide",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "is_system",
            type: "boolean",
            persist: false
        },
        {
            name: "allow_rest",
            type: "boolean",
            defaultValue: false
        },
        {
            name: "parameters",
            type: "auto"
        },
        {
            name: "templates",
            type: "auto"
        },
        {
            name: "bands",
            type: "auto"
        },
        {
            name: "bands_format",
            type: "auto"
        },
        {
            name: "root_orientation",
            type: "string"
        },
        {
            name: "root_queries",
            type: "auto"
        },
        {
            name: "permissions",
            type: "auto"
        },
        {
            name: "localization",
            type: "auto"
        }
    ]
});