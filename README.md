# logisync-modules

## Adding Custom Modules to Odoo

- Open Odoo server folder, find ```DEFAULT_ODOO_PATH/server/odoo.conf``` file.
- Open the file using notepad as Administrator, add the path of this custom module parent folder. Make sure to remove ```/``` at the last character of the parent folder that contain this module folder.
- Open odoo on browser, open the menu on the top left corner and choose Apps menu.
- Choose Update App List and update to add the custom module to odoo. Optionally restart the odoo from service if the custom module is not listed on the apps list.
- Any updates to this custom module need to be upgraded in the odoo to apply the changes.