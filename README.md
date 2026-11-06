# DPO_Odoo

## DPO Pay Odoo Addon v1.2.0 for Odoo v19.0

This is the DPO Pay addon for Odoo. Please feel free to contact
the [DPO Pay support team](https://dpogroup.com/contact-us/) should you require any assistance.

## How this works on Odoo 19

Odoo 19 ships its own DPO payment provider (`payment_dpo`, by Odoo S.A.). A second module with the same technical name
cannot be loaded next to it, so on Odoo 19 and later our features are delivered as an extension of Odoo's provider:

| Odoo version | Module | Notes |
|--------------|--------|-------|
| 16.0, 17.0, 18.0 | `payment_dpo` | The full DPO Pay module (see the `16.0`, `17.0` and `18.0` branches). |
| 19.0 and later | `payment_dpo_extras` | Installs on top of Odoo's built-in `payment_dpo`; no files of Odoo are replaced. |

`payment_dpo_extras` adds these options to the DPO payment provider:

- **Pay URL**: the DPO payment page the customer is redirected to (default `https://secure.3gdirectpay.com/payv3.php`).
  The API host is derived from it, so a sandbox URL works.
- **Service Description**: sent to DPO instead of the order reference.
- **Block Bank Transfer / Block PayPal**: hide these methods on the DPO payment page.
- **Payment Time Limit**: how long the DPO payment page stays valid (hours).
- The customer's street address and phone number in the `createToken` request.
- A clear error with DPO's explanation when DPO refuses to create a payment token.

## Installation (Odoo 19)

1. **Download the plugin**
    - Download **payment_dpo_extras** from the [Odoo Apps store](https://apps.odoo.com) or the releases page and unzip it.

2. **Install the plugin**
    - Upload the **payment_dpo_extras** folder to your Odoo addons directory. Do not touch Odoo's own `payment_dpo`.
    - Login to your Odoo admin area and navigate to **Settings** -> **Activate the developer mode**.
    - Navigate to **Apps** -> **Update Apps List**.
    - Search for **DPO Pay Extras** and click **Install**. Odoo's DPO provider is installed automatically as a
      dependency.
    - Restart your Odoo instance if you added the folder while it was running.

3. **Configure the provider**
    - Go to **Accounting** or **Website** -> **Configuration** -> **Payment Providers** -> **DPO**.
    - Enter your **Service ID** and **Company Token**, set the state to **Test Mode** or **Enabled**, and adjust the
      extra options (Pay URL, Service Description, blocked methods, time limit) if needed.
    - Save.

> **Odoo Online** does not allow third-party modules. Merchants there can only use Odoo's built-in DPO provider.
> **Odoo.sh** supports custom modules, so the installation above applies.

## Collaboration

Please submit pull requests with any tweaks, features or fixes you would like to share.
