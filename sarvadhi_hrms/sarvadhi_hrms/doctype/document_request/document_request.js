// Copyright (c) 2025, admin and contributors
// For license information, please see license.txt

frappe.ui.form.on('Document Request', {
    onload: function(frm) {
        if (!frm.doc.requested_by) {
            frm.set_value('requested_by', frappe.session.user);
        }
    }
});
