
Fetches the postcard, fetches email template from Wordpress, builds email with attachment to send via SES.


## Configuration

- `FROM_NAME` - The from name of the thank you email, "Campax Team",
- `FROM_EMAIL` - The from email of the thank you email, "info@campax.org",
- `LOG_LEVEL` - Log level ("INFO", "DEBUG", etc)

## Other infromation

The action JSON contains `thankYouTemplateRef` in action page data which
specifies the url of WP-JSON cli containing campaign infromation, and in it, the
tempalte for subject and body.

The action JSON also contains custom field `postcardUrl`, to which we add qrcode parameter (this is because when action is created, contact reference is not yet created, so postcardUrl does not contain the qrcode. The qrcode is composed of contact reference, colon, and action page id: `${contact_reference}:${action_page_id}`.

The `postcardUrl` with added qrcode parameter is used to a) download the postcard and attach it b) replace the `{postcardUrl}` placeholder in email template so the user can click and generate the postcard themselves.
